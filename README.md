🤖 AI News Digest — free daily AI email + automatic Blogspot archive
Zero-maintenance, $0 forever (no credit card, no server, no paid API):one clean email per day with the top AI stories — to you, optionally tofriends via hidden BCC, and the same digest auto-posted to your freeBlogspot blog via Blogger's built-in email posting.
**Repo version: 1.1** — footer-free emails and blog posts.

👉 Start here: SOP.md
A click-by-click, ~20-minute setup guide for complete beginners (SOP v2.0).This README is the quick reference.

What it does (every day at 07:30 UTC)
GitHub Actions runs digest.py (~1 minute, free)
Pulls top AI stories from Hacker News (≥80 points) + 6 RSS feeds
De-duplicates, ranks, caps at 15 stories, max 5 per source
Sends one clean email → EMAIL_TO (+ EMAIL_BCC, hidden)
Your BCC list includes your secret Blogger posting address → the emailautomatically becomes a blog post (setup: SOP Phase 8)
Optional: AI "Editor's brief" via free Gemini key
Secrets (Settings → Secrets and variables → Actions)
Secret	Required	Purpose
SMTP_USER / SMTP_PASS / EMAIL_TO	✅	Gmail address, App Password, recipient
EMAIL_BCC	–	hidden recipients: friends + your Blogger posting address (yourname.secretword@blogger.com)
GEMINI_API_KEY	–	AI summary — free key: aistudio.google.com/apikey
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
Add/remove news sources: edit RSS_SOURCES in digest.py.

Blog archive: powered by Blogger's built-in "post via email" — no APIkeys, no OAuth, nothing to expire. Setup: SOP.md Phase 8.

Troubleshooting
See SOP.md → Phase 10.

Tested with: actions/checkout v4 · actions/setup-python v5 · Python 3.12 ·requests 2.32.3 · feedparser 6.0.11 · Gmail SMTP :587.

MIT — do whatever you want with it.
