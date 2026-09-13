#!/usr/bin/env python3
"""
AI News Digest — bundle v1.0 (email + multi-recipient + Blogspot auto-publish)

A zero-cost, self-hosted daily AI news service:
  • Fetches top AI stories from Hacker News (Algolia API) + curated RSS feeds
  • De-duplicates, ranks, and caps the list
  • Emails one clean digest (optionally to friends via hidden BCC)
  • Optionally publishes the same digest to a free Blogspot blog (Blogger API v3)
  • Optionally adds an AI-written brief (Google Gemini, free tier)

Runs as a scheduled GitHub Actions job. Required secrets/env:
    SMTP_USER, SMTP_PASS, EMAIL_TO
Optional:
    EMAIL_BCC, GEMINI_API_KEY,
    BLOG_ID, BLOGGER_CLIENT_ID, BLOGGER_CLIENT_SECRET, BLOGGER_REFRESH_TOKEN,
    SMTP_HOST, SMTP_PORT, SMTP_FROM, HOURS_LOOKBACK, MAX_ITEMS,
    MAX_PER_SOURCE, HN_MIN_POINTS, GEMINI_MODEL, SUMMARY_LANG,
    BLOG_LABELS, BLOG_DRAFT

Anything unset is skipped automatically. See SOP.md for setup.
"""
from __future__ import annotations

import calendar
import html
import os
import re
import smtplib
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import feedparser
import requests

# ---------------------------------------------------------------------------
# Configuration (env-overridable)
# ---------------------------------------------------------------------------

HOURS_LOOKBACK = int(os.getenv("HOURS_LOOKBACK", "26"))
MAX_ITEMS      = int(os.getenv("MAX_ITEMS", "15"))
MAX_PER_SOURCE = int(os.getenv("MAX_PER_SOURCE", "5"))
HN_MIN_POINTS  = int(os.getenv("HN_MIN_POINTS", "80"))
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
SUMMARY_LANG   = os.getenv("SUMMARY_LANG", "English")
TIMEOUT        = 20

UA_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

# Free, keyless sources. Failed sources are skipped automatically (non-fatal).
RSS_SOURCES = [
    {"name": "VentureBeat AI",  "url": "https://venturebeat.com/category/ai/feed/",                           "weight": 0.8},
    {"name": "The Verge AI",    "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",   "weight": 0.8},
    {"name": "Ars Technica AI", "url": "https://arstechnica.com/ai/feed/",                                     "weight": 0.8},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/", "weight": 0.8},
    {"name": "TechCrunch AI",   "url": "https://techcrunch.com/category/artificial-intelligence/feed/",        "weight": 0.7},
    {"name": "AI News",         "url": "https://www.artificialintelligence-news.com/feed/",                    "weight": 0.6},
]

# Only used to filter Hacker News (a firehose of all topics).
# RSS sources above are already AI-only feeds, so they are not keyword-filtered.
AI_KEYWORDS = re.compile(
    r"\b("
    r"ai|agi|a\.i\b|artificial intelligence|artificial general intelligence|"
    r"machine learning|deep learning|neural|llms?|language models?|"
    r"openai|anthropic|deepmind|mistral|claude|gemini|chatgpt|gpt|llamas?|"
    r"deepseek|qwen|grok|sora|midjourney|stable diffusion|dall|"
    r"foundation models?|generative|diffusion models?|transformers?|chatbots?|"
    r"computer vision|natural language|nlp|fine-?tun\w*|multimodal|"
    r"superintelligence|nvidia|gpus?|tpus?|training data|synthetic data"
    r")\b",
    re.IGNORECASE,
)

TAG_RE    = re.compile(r"<[^>]+>")
WS_RE     = re.compile(r"\s+")
BOILER_RE = re.compile(r"The post .+ appeared first on .+\s*$", re.IGNORECASE)
TITLE_STRIP = re.compile(r"[^a-z0-9]+")
TRACKING_PREFIXES = ("utm_", "fbclid", "gclid", "mc_", "ref_", "spm")

# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def _mk(source, title, url, published, points=0, comments=0,
        snippet="", weight=1.0, hn_id=None):
    return {
        "source": source, "title": title.strip(), "url": url.strip(),
        "published": published, "points": points or 0, "comments": comments or 0,
        "snippet": snippet, "weight": weight, "hn_id": hn_id,
    }


def fetch_hn():
    """High-scoring HN stories from the look-back window, filtered by AI keywords."""
    cutoff = int(time.time()) - HOURS_LOOKBACK * 3600
    url = (
        "https://hn.algolia.com/api/v1/search_by_date"
        "?tags=story&hitsPerPage=500"
        f"&numericFilters=points>={HN_MIN_POINTS},created_at_i>={cutoff}"
    )
    r = requests.get(url, timeout=TIMEOUT, headers=UA_HEADERS)
    r.raise_for_status()
    items = []
    for h in r.json().get("hits", []):
        title = (h.get("title") or "").strip()
        if not title or not AI_KEYWORDS.search(title):
            continue
        link = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
        published = datetime.fromtimestamp(h.get("created_at_i", 0), tz=timezone.utc)
        items.append(_mk("Hacker News", title, link, published,
                         points=h.get("points") or 0,
                         comments=h.get("num_comments") or 0,
                         hn_id=h.get("objectID")))
    return items


def clean_snippet(raw, limit=240):
    text = html.unescape(TAG_RE.sub(" ", raw or ""))
    text = BOILER_RE.sub("", text)
    text = WS_RE.sub(" ", text).strip()
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0].rstrip(",;:-") + "…"
    return text


def fetch_rss(src):
    r = requests.get(src["url"], timeout=TIMEOUT, headers=UA_HEADERS)
    r.raise_for_status()
    parsed = feedparser.parse(r.content)
    if parsed.get("bozo") and not parsed.entries:
        raise RuntimeError(f"feed parse error: {parsed.get('bozo_exception')}")

    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_LOOKBACK)
    items = []
    for e in parsed.entries:
        title = html.unescape(e.get("title") or "").strip()
        link = (e.get("link") or "").strip()
        if not title or not link:
            continue
        published = None
        for key in ("published_parsed", "updated_parsed", "created_parsed"):
            st = e.get(key)
            if st:
                # feedparser normalizes timestamps to UTC struct_time
                published = datetime.fromtimestamp(calendar.timegm(st), tz=timezone.utc)
                break
        if published is None or published < cutoff:
            continue  # undated or stale — skip so old items never repeat
        items.append(_mk(src["name"], title, link, published,
                         snippet=clean_snippet(e.get("summary") or ""),
                         weight=src["weight"]))
    return items


def collect_all():
    items = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch_hn): "Hacker News"}
        for src in RSS_SOURCES:
            futures[pool.submit(fetch_rss, src)] = src["name"]
        for fut in as_completed(futures):
            label = futures[fut]
            try:
                got = fut.result()
                items.extend(got)
                print(f"[INFO] {label}: {len(got)} relevant items")
            except Exception as exc:
                print(f"[WARN] {label}: failed ({exc}) — skipped (non-fatal)")
    return items

# ---------------------------------------------------------------------------
# Ranking / de-duplication
# ---------------------------------------------------------------------------

def canon_url(url):
    try:
        p = urlsplit(url.strip())
    except ValueError:
        return url.strip().lower()
    q = urlencode([(k, v) for k, v in parse_qsl(p.query)
                   if not k.startswith(TRACKING_PREFIXES)])
    host = p.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return urlunsplit((p.scheme.lower(), host, p.path.rstrip("/") or "/", q, ""))


def title_key(t):
    return WS_RE.sub(" ", TITLE_STRIP.sub(" ", t.lower())).strip()


def score(it):
    s = it["weight"] * 30.0
    if it["points"]:
        s += min(it["points"], 500) * 0.25          # 200 points -> +50
    if it["published"]:
        age_h = (datetime.now(timezone.utc) - it["published"]).total_seconds() / 3600
        s += max(0.0, HOURS_LOOKBACK - age_h) * 0.5  # freshness bonus
    return s


def dedupe(items):
    """Same URL or near-identical title (across sources) -> keep the best one."""
    kept, seen_urls, seen_titles = [], set(), []
    for it in sorted(items, key=score, reverse=True):
        cu = canon_url(it["url"])
        if cu in seen_urls:
            continue
        tk = title_key(it["title"])
        duplicate = False
        if len(tk) >= 15:
            for st in seen_titles:
                if (abs(len(st) - len(tk)) < 25
                        and SequenceMatcher(None, st, tk).ratio() >= 0.7):
                    duplicate = True
                    break
        if duplicate:
            continue
        seen_urls.add(cu)
        seen_titles.append(tk)
        kept.append(it)
    return kept  # sorted best-first


def select(items):
    """Cap items per source (diversity), then take the top MAX_ITEMS."""
    chosen, per_source = [], {}
    for it in items:
        n = per_source.get(it["source"], 0)
        if n >= MAX_PER_SOURCE:
            continue
        per_source[it["source"]] = n + 1
        chosen.append(it)
        if len(chosen) == MAX_ITEMS:
            break
    return chosen

# ---------------------------------------------------------------------------
# Optional Gemini summary (free tier)
# ---------------------------------------------------------------------------

def _strip_md(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    return text.strip()


def gemini_brief(items):
    key = (os.environ.get("GEMINI_API_KEY") or "").strip()
    if not key or not items:
        return None
    headlines = "\n".join(f"- {it['title']} [{it['source']}]" for it in items)
    prompt = (
        "You are the editor of a concise daily AI news digest. Below are today's "
        f"headlines. Write your answer in {SUMMARY_LANG}:\n"
        "1) A 2-3 sentence 'editor's brief' of the overall picture.\n"
        "2) Then exactly 3 one-line bullets for the most significant stories.\n"
        "Be factual, specific and neutral. Plain text only.\n\n"
        f"Headlines:\n{headlines}"
    )
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 600},
            },
            timeout=60,
        )
        r.raise_for_status()
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return _strip_md(text)
    except Exception as exc:
        print(f"[WARN] Gemini summary failed ({exc}) — sending digest without it.")
        return None

# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def esc(s):
    return html.escape(s or "", quote=True)


def format_time(dt):
    return dt.astimezone(timezone.utc).strftime("%d %b, %H:%M UTC")


def _head(date_s, sub):
    return (
        '<div style="font-family:-apple-system,\'Segoe UI\',Roboto,Helvetica,Arial,'
        'sans-serif;max-width:640px;margin:0 auto;padding:28px 20px;color:#20222e;">'
        '<div style="border-bottom:3px solid #6C5CE7;padding-bottom:14px;margin-bottom:22px;">'
        '<h1 style="font-size:24px;margin:0;">🤖 AI News Digest</h1>'
        f'<p style="color:#8a8a99;font-size:13px;margin:6px 0 0;">{esc(date_s)} · {esc(sub)}</p></div>'
    )


_FOOT = (
    '<div style="margin-top:30px;padding-top:14px;border-top:1px solid #ECECEF;'
    'color:#9a9aa8;font-size:12px;line-height:1.6;">'
    'Sent by your <b>ai-news-digest</b> repo running on GitHub Actions (free). '
    'To stop these emails: disable the workflow or delete the repo. '
    'To change sources/schedule: see README.</div></div>'
)


def render_html(items, brief):
    date_s = datetime.now(timezone.utc).strftime("%A, %d %B %Y")
    parts = [_head(date_s, f"{len(items)} stories · Hacker News + RSS")]
    if brief:
        parts.append(
            '<div style="background:#F5F3FF;border:1px solid #DDD6FE;border-radius:10px;'
            'padding:16px 18px;margin:0 0 24px;">'
            '<div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#6C5CE7;'
            'margin-bottom:8px;">✨ EDITOR&#39;S BRIEF · GEMINI</div>'
            f'<div style="font-size:14px;line-height:1.6;color:#333340;white-space:pre-wrap;">{esc(brief)}</div></div>'
        )
    for i, it in enumerate(items, 1):
        meta = [esc(it["source"])]
        if it["points"]:
            meta.append(f"▲ {it['points']}")
        if it["comments"]:
            meta.append(f"💬 {it['comments']}")
        if it["published"]:
            meta.append(esc(format_time(it["published"])))
        disc = ""
        if it["hn_id"]:
            disc = (' · <a href="https://news.ycombinator.com/item?id=' + esc(str(it["hn_id"])) +
                    '" style="color:#6C5CE7;text-decoration:none;">discussion</a>')
        snippet_html = ""
        if it["snippet"]:
            snippet_html = ('<div style="font-size:13.5px;color:#55555f;line-height:1.55;'
                            f'margin-top:5px;">{esc(it["snippet"])}</div>')
        parts.append(
            '<div style="margin-bottom:22px;">'
            '<div style="font-size:16.5px;font-weight:600;line-height:1.4;margin-bottom:3px;">'
            f'<a href="{esc(it["url"])}" style="color:#20222e;text-decoration:none;">'
            f'{i}. {esc(it["title"])}</a></div>'
            f'<div style="font-size:12px;color:#8a8a99;">{" · ".join(meta)}{disc}</div>'
            f"{snippet_html}</div>"
        )
    parts.append(_FOOT)
    return "".join(parts)


def render_text(items, brief):
    lines = [f"AI NEWS DIGEST — {datetime.now(timezone.utc).strftime('%A, %d %B %Y')}", ""]
    if brief:
        lines += ["✨ EDITOR'S BRIEF", brief, ""]
    for i, it in enumerate(items, 1):
        lines.append(f"{i}. {it['title']}")
        meta = [it["source"]]
        if it["points"]:
            meta.append(f"{it['points']} points, {it['comments']} comments")
        lines.append("   " + " · ".join(meta))
        lines.append(f"   {it['url']}")
        if it["snippet"]:
            lines.append(f"   {it['snippet']}")
        lines.append("")
    lines.append("Sent by your ai-news-digest on GitHub Actions. Disable the workflow to stop.")
    return "\n".join(lines)


def render_quiet():
    date_s = datetime.now(timezone.utc).strftime("%A, %d %B %Y")
    note = (f"No AI stories passed the filters in the last {HOURS_LOOKBACK} hours. "
            "Either a genuinely slow news day, or your filters are strict "
            "(see HN_MIN_POINTS and HOURS_LOOKBACK in the README).")
    html_body = _head(date_s, "quiet day") + f'<p style="color:#333340;">{esc(note)}</p>' + _FOOT
    return html_body, f"AI NEWS DIGEST — {date_s}\n\n{note}"

# ---------------------------------------------------------------------------
# Sending (email, with optional private BCC list)
# ---------------------------------------------------------------------------

def send_mail(subject, html_body, text_body):
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.environ["SMTP_USER"]
    pw   = os.environ["SMTP_PASS"]
    to   = os.environ["EMAIL_TO"]
    bcc  = os.getenv("EMAIL_BCC", "").strip()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = os.getenv("SMTP_FROM", user)
    msg["To"] = to
    if bcc:
        msg["Bcc"] = bcc   # send_message strips the Bcc header before sending
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(host, port, timeout=60) as s:
            s.starttls()
            s.login(user, pw)
            s.send_message(msg)
    except smtplib.SMTPAuthenticationError:
        sys.exit("[ERROR] SMTP login rejected. For Gmail you must use a 16-character "
                 "App Password (not your normal password). See SOP Phase 3.")
    extra = f" (+ {len([a for a in bcc.split(',') if a.strip()])} BCC)" if bcc else ""
    print(f"[INFO] Email sent to {to}{extra}")

# ---------------------------------------------------------------------------
# Optional: publish the digest to your Blogspot blog (Blogger API v3)
# ---------------------------------------------------------------------------

def publish_blogger(subject, html_body):
    """Optional: also publish the digest as a Blogspot post (Blogger API v3).
    Skips silently if not configured. Email is always sent first."""
    blog_id       = (os.getenv("BLOG_ID") or "").strip()
    client_id     = (os.getenv("BLOGGER_CLIENT_ID") or "").strip()
    client_secret = (os.getenv("BLOGGER_CLIENT_SECRET") or "").strip()
    refresh_token = (os.getenv("BLOGGER_REFRESH_TOKEN") or "").strip()
    if not (blog_id and client_id and client_secret and refresh_token):
        print("[INFO] Blogger publishing not configured — skipping.")
        return
    try:
        # 1. Exchange the long-lived refresh token for a short-lived access token
        tok = requests.post(
            "https://oauth2.googleapis.com/token",
            data={"client_id": client_id, "client_secret": client_secret,
                  "refresh_token": refresh_token, "grant_type": "refresh_token"},
            timeout=30)
        tok.raise_for_status()
        access_token = tok.json()["access_token"]

        # 2. Create the post (reuse the email's HTML, swap the footer)
        blog_footer = (
            '<div style="margin-top:30px;padding-top:14px;border-top:1px solid #ECECEF;'
            'color:#9a9aa8;font-size:12px;line-height:1.6;">'
            'Daily digest auto-published by <b>ai-news-digest</b> on GitHub Actions. '
            'Browse older issues on this blog.</div></div>'
        )
        content = html_body.replace(_FOOT, blog_footer)
        labels = [x.strip() for x in os.getenv("BLOG_LABELS", "AI, daily-digest").split(",") if x.strip()]
        post = requests.post(
            f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"isDraft": os.getenv("BLOG_DRAFT", "false").lower()},
            json={"kind": "blogger#post", "title": subject, "content": content, "labels": labels},
            timeout=60)
        post.raise_for_status()
        print(f"[INFO] Published to Blogger: {post.json().get('url', '(url unknown)')}")
    except requests.HTTPError as exc:
        detail = exc.response.text[:300] if exc.response is not None else ""
        print(f"[WARN] Blogger publishing failed: {exc} | {detail}")
    except Exception as exc:
        print(f"[WARN] Blogger publishing failed ({exc}) — the email was already sent.")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    for var in ("SMTP_USER", "SMTP_PASS", "EMAIL_TO"):
        if not os.environ.get(var):
            sys.exit(f"[ERROR] Missing required secret: {var}. Add it under "
                     "Settings → Secrets and variables → Actions (see SOP Phase 4).")

    print(f"[INFO] Collecting AI news from the last {HOURS_LOOKBACK}h ...")
    raw = collect_all()
    if not raw:
        sys.exit("[ERROR] Every source failed — check the Actions log or your sources.")

    items = select(dedupe(raw))
    print(f"[INFO] {len(raw)} raw items → {len(items)} in digest "
          f"(caps: {MAX_ITEMS} max, {MAX_PER_SOURCE}/source)")

    brief = gemini_brief(items)
    if items:
        subject = f"🤖 AI News Digest — {len(items)} stories — {datetime.now(timezone.utc):%d %b}"
        html_body, text_body = render_html(items, brief), render_text(items, brief)
    else:
        subject = "🤖 AI News Digest — quiet day"
        html_body, text_body = render_quiet()
    send_mail(subject, html_body, text_body)
    publish_blogger(subject, html_body)


if __name__ == "__main__":
    main()
