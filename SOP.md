SOP — Free Daily AI News Email + Automatic Blogspot Archive
SOP version	2.1 (field-tested revision)
| **Repo version** | 1.1 (digest.py v1.1 — footer removed) |
Cost	$0 — everything on free tiers. No credit card anywhere.
Audience	Anyone with a web browser. No coding experience needed.
Time needed	~15 minutes (core) + 5 minutes (optional blog). Zero daily effort after.
Maintenance	~2 minutes per month (automatic keepalive included)
What you get when finished:

One clean AI-news email in your inbox every morning.
(Optional) The same email to friends — privately, via BCC.
(Optional) The same digest auto-published every day as a post on yourfree Blogspot blog — a permanent, searchable archive.
What changed in v2.0: **v2.1:** repo upgraded to digest.py v1.1 — the digest email (and the blog
posts created from it) now ends cleanly after the last story; the
"Sent by…" footer line was removed.blog publishing now uses Blogger's built-in"post via email" feature instead of the Google Cloud / OAuth API method.Field testing showed the email method is simpler, free, and — mostimportantly — nothing in it can expire. It needs zero extra accountsand zero API keys. (Coming from v1.0? See "Migrating from v1.0" near the end.)

What you are building
GitHub Actions (free daily scheduler)        │        ▼   digest.py  ──►  Hacker News API + 6 tech RSS feeds   (free, no keys)        │             stories de-duplicated & ranked        ├──►  ① Email → your inbox (+ friends, hidden BCC)        │        └──►  ② The same email → Blogger's secret posting address                            → auto-published on your Blogspot blog
Everything you use is free
Service	Free-tier allowance	This project consumes
GitHub Actions	Unlimited (public repo) · 2,000 min/month (private)	~1 min/day
Gmail SMTP	~500 emails/day	1/day
Hacker News API, RSS feeds	Free, keyless	1 fetch/day each
Blogger + Blogspot	Free hosting + free yourname.blogspot.com address	1 post/day
Blogger "post via email"	Free, built-in	1 email/day
Versions this SOP was tested with
Component	Version	Where it lives
actions/checkout	v4	.github/workflows/digest.yml
actions/setup-python	v5	.github/workflows/digest.yml
Python	3.12	.github/workflows/digest.yml
requests	2.32.3 (allowed: ≥2.31, <3)	requirements.txt
feedparser	6.0.11 (allowed: ≥6.0, <7)	requirements.txt
Gmail SMTP	smtp.gmail.com, port 587	digest.py
If any screen or menu doesn't match, Google or GitHub changed their UI.The buttons still exist — search the settings page for the same wording.

Files your repo must contain
File	Purpose
digest.py	The engine: fetch → rank → email (BCC) → optional blog publish
requirements.txt	Two small libraries
.github/workflows/digest.yml	Daily schedule + credential wiring
.github/workflows/keepalive.yml	Stops GitHub disabling the schedule after 60 idle days
README.md, SOP.md	Documentation (this file)
Phase 1 — Prerequisites ✅ (2 min)
☐ A GitHub account — free at github.com/signup☐ A Gmail account — free at gmail.com☐ A web browser and ~20 uninterrupted minutes

Tip: use the same Google account for Gmail and Blogger.It makes Phase 8 work first try.

Phase 2 — Create the repository ✅ (3 min)
Log in to GitHub.
If you received this as a template repo: click the greenUse this template → Create a new repository button.Otherwise: click + (top-right) → New repository → name itai-news-digest → Create repository.
Add the 5 files from the table above, keeping the exact folder structure(both .yml files go inside .github/workflows/).Easiest way, fully in the browser: Add file → Create new file → typethe full path with slashes (e.g. .github/workflows/digest.yml) →paste the file's content → Commit changes. Repeat per file.
✅ Checkpoint: the repo's main page lists digest.py, requirements.txt,and the .github folder.

Phase 3 — Get your Gmail App Password ✅ (3 min)
(This is your email credential. It is not your normal Gmail password.)

Go to myaccount.google.com/security.
Turn on 2-Step Verification (Google requires this before app passwords).
On the same Security page, type "app passwords" in the search box → open it.
Create one, name it ai-news-digest, and copy the 16-character passwordshown (format like abcd efgh ijkl mnop — spaces don't matter).
✅ Checkpoint: your Gmail address + a 16-character app password, written down.

Phase 4 — Enter your email credentials ✅ (3 min)
Path: Repo → Settings → Secrets and variables → Actions →New repository secret. Names must match exactly (capital letters matter):

Secret name	Value	Required?
SMTP_USER	your Gmail address, e.g. you@gmail.com	✅
SMTP_PASS	the 16-character App Password from Phase 3	✅
EMAIL_TO	your email address	✅
EMAIL_BCC	friends' addresses + (later) the Blogger posting address — comma-separated, see Phases 7–8	optional
Secrets are stored encrypted by GitHub and never appear in code or logs.(If a log ever shows ***, that's GitHub masking a secret — normal.)

✅ Checkpoint: 3 green entries under "Repository secrets".

Phase 5 — First test run (email only) ✅ (2 min) — do not skip
Open the Actions tab → click Daily AI Digest in the left list.If prompted, click "I understand my workflows, go ahead and enable them".
Right side: Run workflow → Run workflow (leave defaults).
Click the running job and watch the log. Expected lines:[INFO] Hacker News: 12 relevant items …[INFO] Email sent to ***[INFO] Blogger publishing not configured — skipping.(That last line is correct — the blog isn't configured yet.)
Check your inbox (~60 seconds after the job starts).
✅ Checkpoint: email arrived with subject"🤖 AI News Digest — N stories — [date]".If not → Phase 10 (Troubleshooting) before continuing.

Phase 6 — Confirm the schedule ✅ (1 min)
.github/workflows/digest.yml contains:

on:  schedule:    - cron: "30 7 * * *"   # 07:30 UTC, every day
That's UTC. Local equivalents: 03:30 New York (EDT) · 08:30 London (BST) ·09:30 Berlin (CEST) · 13:00 Mumbai (IST).

To change the time: edit the cron: line (helper: crontab.guru) and commit.
Runs may start up to ~1 hour late under load — normal; the script's26-hour news window is built to tolerate it.
Phase 7 — Optional: send to multiple email addresses ✅ (1 min)
Mode A — everyone sees everyone: comma-separated addresses in EMAIL_TO.

Mode B — private (recommended): keep EMAIL_TO as just yourself; put theother addresses in EMAIL_BCC, comma-separated. Everyone gets the email, butnobody sees each other's address.

Friends should click "Not spam" on their first digest.
Gmail free limit: ~500 recipients/day — even 50 friends uses only 50.
Edit the secret anytime; the change applies on the next run.
Phase 8 — Optional: auto-publish to your Blogspot blog ✅ (5 min)
Blogger has a built-in feature: emails sent to a secret address becomeblog posts. Since your workflow already emails the digest daily, you onlyneed to add one address — no code, no extra accounts, nothing to expire.

Go to blogger.com and sign in with your Google account.
⚠️ Decide which blog gets the posts. The digest will publish towhichever blog you configure below. If you have an existing blog andwant the digest there — fine. If you want a separate digest archive,click "Create new blog" first (title, an availableyourname.blogspot.com address, a theme).This is the #1 gotcha: people configure one blog and then check another.Remember your choice.
Open that blog → Settings (left menu) → Email section(called "Email posts to" / post via email).
Type a secret word — letters and numbers only, e.g. ai123news.Blogger displays the generated posting address, something likeyourname.ai123news@blogger.com — copy it exactly (don't retype).
Choose the delivery option:
"Publish emails immediately" — recommended: fully automatic
"Save emails as draft posts" — if you want to review before publishing
GitHub → Settings → Secrets and variables → Actions → edit theEMAIL_BCC secret and add the Blogger address (comma-separatedwith friends, if any):
friend1@gmail.com, yourname.ai123news@blogger.com
Actions → Run workflow (or wait for the daily run).
Where to look for the post — read carefully:
Open blogger.com → the blog you configured in step 2 → Posts.
Check Published and, if you chose draft mode, Drafts.
Allow up to 15–30 minutes after the email is sent — Blogger'semail ingestion is not instant.
The post title = the email subject("🤖 AI News Digest — N stories — [date]").
Formatting is good, not pixel-perfect (Blogger converts the email'sHTML; expect minor style differences).
✅ Checkpoint: today's digest visible in Posts on the blog you configured.

Security & housekeeping:

The secret address is the only key — anyone who knows it can post. Keep itprivate. To cut it off: change the secret word in Blogger settings(the old address stops working) and update EMAIL_BCC.
Test runs create posts too — delete extras in Blogger → Posts.
Over time the blog becomes your permanent, searchable digest archive.
Phase 9 — Daily operation (what "done" looks like)
Every day at 07:30 UTC (± up to 1 hour):

The job runs ~1 minute (visible under the Actions tab).
Your email arrives (and friends', if configured).
The post appears on your blog within ~30 minutes.
Phase 10 — Troubleshooting (field-tested)
Symptom	Cause	Fix
Log: 535 Authentication failed	Normal Gmail password used	Redo Phase 3; update SMTP_PASS
Red job: Missing required secret	Secret missing or misnamed	Redo Phase 4 — names are case-sensitive
Email in spam	First delivery to that inbox	Mark "Not spam" once; add sender to contacts
Blog post not appearing	Wrong blog, draft mode, or impatience	Check the blog whose Email settings you configured (Phase 8, step 2); check Drafts; wait 15–30 min
Blog posts stopped	Secret word changed, or EMAIL_BCC edited	Re-copy the address from Blogger → Settings → Email; update EMAIL_BCC
Anyone posting to my blog?	Secret address leaked	Change the secret word in Blogger settings; update EMAIL_BCC
Digest late	GitHub cron jitter	Wait 60 minutes before worrying
Digests stopped after ~2 months	GitHub's 60-day-idle rule	keepalive.yml prevents it — confirm Actions are enabled
"Quiet day" email	Slow news day / strict filters	Lower HN_MIN_POINTS or raise HOURS_LOOKBACK in digest.yml
[WARN] … 429/403 … skipped in log	One news feed rate-limited or blocking	Non-fatal — digest still sent; usually recovers next run
[WARN] Blogger publishing failed … invalid_grant	Old v1.0 OAuth secrets still present	Delete the 4 BLOG_* secrets — see "Migrating from v1.0" below
SyntaxError after editing digest.py	Hand-typed code fragment broke indentation	Replace the whole file with the original; never retype fragments — paste complete blocks only
*** appears in logs	GitHub masking secret values	Normal, ignore
Phase 11 — Monthly check ✅ (2 min)
Repo → Actions → ~30 successful runs.
One commit named chore: keepalive … exists.
Blog shows ~30 new posts for the month.
Skim one digest; tune MAX_ITEMS / HN_MIN_POINTS if needed.
Migrating from v1.0 (the old OAuth/API blog method)
If you previously followed SOP v1.0 and created the Google Cloud OAuth setup:

Repo → Settings → Secrets → delete BLOG_ID, BLOGGER_CLIENT_ID,BLOGGER_CLIENT_SECRET, BLOGGER_REFRESH_TOKEN.The log's [WARN] … invalid_grant line disappears; the clean[INFO] Blogger publishing not configured — skipping. is the correct state.
Optional: delete the Google Cloud project(console.cloud.google.com → IAM & Admin → Settings → Delete project).
Optional tidiness: delete the four BLOG_* lines from the env: blockof .github/workflows/digest.yml (harmless either way).
Keep EMAIL_BCC with the Blogger posting address — that's the working pipe.
Teardown (undo everything)
Repo → Settings → General → Delete repository — stops emails and posts.
myaccount.google.com/security → App passwords → delete ai-news-digest.
Blogger → Settings → Email → change/delete the secret word (cuts off posting).
Blogger → delete the blog — or keep it as your reading archive.
You are done. Ongoing effort: zero.
