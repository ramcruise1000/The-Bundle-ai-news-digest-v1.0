🤖 AI News Digest — free daily AI email + automatic Blogspot archive
Zero-maintenance, $0 forever (no credit card, no server, no paid API):one clean email per day with the top AI stories — to you, optionally tofriends via hidden BCC, and optionally auto-published to your freeBlogspot blog as a permanent archive.

👉 Start here: SOP.md
A click-by-click, ~30-minute setup guide for complete beginners.This README is the quick reference.

What it does (every day at 07:30 UTC)
GitHub Actions runs digest.py (~1 minute, free)
Pulls top AI stories from Hacker News (≥80 points) + 6 RSS feeds
De-duplicates, ranks, caps at 15 stories, with max 5 per source
Sends one clean email → EMAIL_TO (+ EMAIL_BCC, hidden)
Publishes the same digest as a post on your Blogspot blog
Optional: AI-written "Editor's brief" via free Gemini key
Secrets (Settings → Secrets and variables → Actions)
Secret	Required	Purpose
SMTP_USER / SMTP_PASS / EMAIL_TO	✅	Gmail address, App Password, recipient
EMAIL_BCC	–	extra recipients, hidden from each other
GEMINI_API_KEY	–	AI summary — free key: aistudio.google.com/apikey
BLOG_ID	–	Blogspot auto-publish (SOP Phase 9)
BLOGGER_CLIENT_ID / BLOGGER_CLIENT_SECRET / BLOGGER_REFRESH_TOKEN	–	Blogspot auto-publish (SOP Phase 9)
Anything unset is skipped automatically.

Customization (env vars in .github/workflows/digest.yml)
Variable	Default	What it does
HOURS_LOOKBACK	26	story window (tolerates cron jitter)
MAX_ITEMS	15	stories per digest
MAX_PER_SOURCE	5	diversity cap per source
HN_MIN_POINTS	80	popularity bar for Hacker News
SUMMARY_LANG	English	language of the AI brief
GEMINI_MODEL	gemini-2.0-flash	any current Gemini model
SMTP_HOST / SMTP_PORT	smtp.gmail.com / 587	switch email provider
BLOG_LABELS	AI, daily-digest	labels on blog posts
BLOG_DRAFT	false	true = save posts as drafts
Add/remove news sources: edit RSS_SOURCES in digest.py (any RSS/Atom feed).

Troubleshooting
See SOP.md → Phase 12.

Tested with: actions/checkout v4 · actions/setup-python v5 · Python 3.12 ·requests 2.32.3 · feedparser 6.0.11 · Blogger API v3 · Gmail SMTP :587.

MIT — do whatever you want with it.
