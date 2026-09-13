SOP — Free Daily AI News Email + Automatic Blogspot Archive
SOP version	1.0
Repo version	1.0 (complete bundle: email + multiple recipients + Blogger auto-publish)
Cost	$0 — everything on free tiers. No credit card anywhere.
Audience	Anyone with a web browser. No coding experience needed.
Time needed	~30 minutes, once. Zero daily effort after that.
Maintenance	~2 minutes per month (automatic keepalive included)
What you get when finished:

One clean AI-news email in your inbox every morning.
(Optional) The same email to friends — privately, via BCC.
The same digest auto-published every day as a post on your freeyourname.blogspot.com blog — a permanent, searchable archive.
Advanced extras (AI-written summary, extra news feeds) exist in the projectbut are not required — anything you don't configure is skipped automatically.

What you are building
GitHub Actions (free daily scheduler)        │        ▼   digest.py  ──►  Hacker News API + 6 tech RSS feeds   (free, no keys)        │             stories de-duplicated & ranked        ├──►  ① Email to your inbox (+ friends, optional)        └──►  ② Blog post on your Blogspot blog         (automatic archive)
Everything you use is free
Service	Free-tier allowance	This project consumes
GitHub Actions	Unlimited (public repo) · 2,000 min/month (private)	~1 min/day
Gmail SMTP	~500 emails/day	1/day
Hacker News API, RSS feeds	Free, keyless	1 fetch/day each
Blogger + Blogspot	Free hosting + free yourname.blogspot.com address	1 post/day
Blogger API v3 + Google Cloud OAuth	Free (no billing account needed)	1 request/day
Versions this SOP was tested with
Component	Version	Where it lives
actions/checkout	v4	.github/workflows/digest.yml
actions/setup-python	v5	.github/workflows/digest.yml
Python	3.12	.github/workflows/digest.yml
requests	2.32.3 (allowed: ≥2.31, <3)	requirements.txt
feedparser	6.0.11 (allowed: ≥6.0, <7)	requirements.txt
Blogger API	v3	digest.py
OAuth	2.0 (refresh-token flow)	Phase 9
Gmail SMTP	smtp.gmail.com, port 587	digest.py
If any screen or menu doesn't match, Google or GitHub changed their UI.The buttons still exist — search the settings page for the same wording.

Files your repo must contain (v1.0)
File	Purpose
digest.py	The engine: fetch → rank → email → publish to blog (contains publish_blogger)
requirements.txt	Two small libraries
.github/workflows/digest.yml	Daily schedule + credential wiring
.github/workflows/keepalive.yml	Stops GitHub disabling the schedule after 60 idle days
README.md, SOP.md	Documentation (this file)
Quick check that your repo is v1.0 (needed for Phase 9 to work):

digest.py contains the text def publish_blogger — search for it.
.github/workflows/digest.yml contains these lines in the env: block:
          BLOG_ID:                ${{ secrets.BLOG_ID }}          BLOGGER_CLIENT_ID:      ${{ secrets.BLOGGER_CLIENT_ID }}          BLOGGER_CLIENT_SECRET:  ${{ secrets.BLOGGER_CLIENT_SECRET }}          BLOGGER_REFRESH_TOKEN:  ${{ secrets.BLOGGER_REFRESH_TOKEN }}
Phase 1 — Prerequisites ✅ (2 min)
☐ A GitHub account — free at github.com/signup☐ A Gmail account — free at gmail.com☐ A web browser and ~30 uninterrupted minutes

Tip: use the same Google account for Gmail, the blog (Phase 8), andthe Google Cloud setup (Phase 9). It makes everything work first try.

Phase 2 — Create the repository ✅ (3 min)
Log in to GitHub.
If you received this as a template repo: click the greenUse this template → Create a new repository button.Otherwise: click + (top-right) → New repository → name itai-news-digest → Create repository.
Upload the 5 files from the table above, keeping the exact folder structure(both .yml files go inside .github/workflows/).
✅ Checkpoint: the repo's main page lists digest.py, requirements.txt,and the .github folder.

Phase 3 — Get your Gmail App Password ✅ (3 min)
(This is your email credential. It is not your normal Gmail password.)

Go to myaccount.google.com/security.
Turn on 2-Step Verification (Google requires this before app passwords).
On the same Security page, type "app passwords" in the search box → open it.
Create one, name it ai-news-digest, and copy the 16-character passwordshown (format like abcd efgh ijkl mnop — spaces don't matter).
✅ Checkpoint: your Gmail address + a 16-character app password, written down.

Phase 4 — Enter your email credentials ✅ (3 min)
Path: Repo → Settings → Secrets and variables → Actions →New repository secret — add each one. Names must match exactly(capital letters matter):

Secret name	Value	Required?
SMTP_USER	your Gmail address, e.g. you@gmail.com	✅
SMTP_PASS	the 16-character App Password from Phase 3	✅
EMAIL_TO	your email address (more addresses in Phase 7)	✅
The workflow also mentions other optional secrets (GEMINI_API_KEY,EMAIL_BCC, …). Leave them unset for now — Blogger secrets come inPhase 9. Anything unset is skipped automatically.

Secrets are stored encrypted by GitHub — they never appear in code or logs.

✅ Checkpoint: 3 green entries under "Repository secrets".

Phase 5 — First test run (email only) ✅ (2 min) — do not skip
Open the Actions tab → click Daily AI Digest in the left list.If prompted, click "I understand my workflows, go ahead and enable them".
Right side: Run workflow → Run workflow (leave defaults).
Click the running job and watch the log. Expected lines:[INFO] Hacker News: 12 relevant items … [INFO] Email sent to …and [INFO] Blogger publishing not configured — skipping.(That last line is correct — you haven't set up the blog yet.)
Check your inbox (~60 seconds after the job starts).
✅ Checkpoint: email arrived with subject"🤖 AI News Digest — N stories — [date]".If not → Phase 12 (Troubleshooting) before continuing.

Phase 6 — Confirm the schedule ✅ (1 min)
.github/workflows/digest.yml contains:

on:  schedule:    - cron: "30 7 * * *"   # 07:30 UTC, every day
That's UTC. Local equivalents: 03:30 New York (EDT) · 08:30 London (BST) ·09:30 Berlin (CEST) · 13:00 Mumbai (IST).

To change the time: edit the cron: line (helper: crontab.guru) and commit.
Runs may start up to ~1 hour late under load — normal; the script's26-hour news window is built to tolerate it.
Phase 7 — Optional: send to multiple email addresses ✅ (1 min)
Mode A — everyone sees everyone: comma-separated addresses in EMAIL_TO:

you@gmail.com, alice@gmail.com, bob@outlook.com
Mode B — private (recommended): keep EMAIL_TO as just yourself; add onemore secret EMAIL_BCC with the other addresses comma-separated. Everyonegets the email, but nobody sees each other's address.

Friends should click "Not spam" on their first digest.
Gmail free limit: ~500 recipients/day — even 50 friends uses only 50.
Edit the secret anytime; the change applies on the next run.
✅ Checkpoint (if used): re-run the workflow; every inbox receives the email.

Phase 8 — Create your free Blogger blog ✅ (3 min)
Go to blogger.com — signed in with your Google account.
Click "Create Your Blog" (or Create new blog):
Title: e.g. My AI News Tracker
Address: pick an available yourname.blogspot.com name →pick a theme → Create blog.
Want it just for yourself? Blog → Settings → Permissions →Reader access → choose "Private – only authors".The digest still auto-publishes daily; only you can read it (log in toview). Leave it public if you'd like friends/readers to browse the archive.
Find your Blog ID: from the Blogger dashboard, click your blog's nameand look at the browser address bar:blogger.com/blog/1234567890/settings — that number is yourBlog ID. Write it down.
✅ Checkpoint: blog exists at yourname.blogspot.com + Blog ID noted.

Phase 9 — Connect automatic publishing ✅ (15 min, one-time only)
This is the longest phase. Every click is spelled out. You never write code,never pay anything, and never see a credit-card screen.

9.1 Create a Google Cloud project (2 min)
Open console.cloud.google.com → sign in with the same Googleaccount that owns the blog.
Top bar → project dropdown (says "Select a project") → New project →name it ai-news-digest → Create. Wait ~30 seconds, then make surethe project dropdown shows ai-news-digest.
You will not be asked for billing. Blogger API and OAuth credentialsare free. Do not link a billing account.

9.2 Enable the Blogger API (1 min)
☰ menu (top-left "Navigation menu") → APIs & Services → Library.
Search box: "Blogger API v3" → click the result → click Enable.(If asked to pick a project, choose ai-news-digest.)
9.3 OAuth consent screen (3 min) — ⚠️ one critical setting
☰ → APIs & Services → OAuth consent screen → Get started(or "Configure").
User type:External → Create.
App name: ai-news-digest · your email for both email fields →Save and continue through the remaining pages (scopes and test userscan be left as-is → Continue → Back to dashboard).
⚠️ CRITICAL STEP: on the OAuth consent screen overview, click"Publish app" so the Publishing status becomes "In production".If it stays "Testing", Google silently deletes your login token after7 days and your blog stops updating. The "unverified app" warning isfine — only you use this app, and the Blogger permission is not sensitive.
9.4 Create your OAuth client (2 min)
☰ → APIs & Services → Credentials → + Create credentials →OAuth client ID.
Application type: Desktop app (leave the name as-is) → Create.
Copy two values and keep them handy:
Client ID — a long string ending in apps.googleusercontent.com
Client secret — a shorter string starting with GOCSPX-
9.5 Get your permanent "refresh token" (5 min) — browser only
Open developers.google.com/oauthplayground.
Click the ⚙ gear icon (top-right) → tick "Use your own OAuthcredentials" → paste your Client ID and Client secret → close the panel.
Left panel, "Step 1": in the input box (above the scope list, where itsays "Input your own scopes"), paste exactly:
https://www.googleapis.com/auth/blogger
Then click the blue "Authorize APIs" button next to that box(not the big list below).
Sign in with the Google account that owns the blog. If you see an"unverified app" screen: Advanced → "Go to ai-news-digest (unsafe)"(normal for your own app) → Allow/Continue.
You land on "Step 2": click "Exchange authorization code for tokens".
"Step 3" now shows your tokens. Copy the refresh_token value(a long string, usually starting with 1//) — not the access token.
If the refresh_token field is empty, the gear-icon step (2) failed —you used Google's built-in credentials instead of your own. Redo from step 2.

✅ Checkpoint: you now hold four values —Blog ID (Phase 8), Client ID, Client secret, refresh_token.

9.6 Add the Blogger secrets to GitHub (1 min)
Repo → Settings → Secrets and variables → Actions →New repository secret:

Secret name	Value
BLOG_ID	the number from Phase 8, e.g. 1234567890
BLOGGER_CLIENT_ID	…apps.googleusercontent.com
BLOGGER_CLIENT_SECRET	GOCSPX-…
BLOGGER_REFRESH_TOKEN	1//…
✅ Checkpoint: 7 green secrets total (3 email + 4 Blogger).

9.7 Verify the wiring (30 sec)
Confirm your repo passes the "quick check" from the top of this SOP(digest.py contains publish_blogger; digest.yml has the 4 BLOG_* envlines). If the 4 lines are missing, paste them into the env: block and commit.

Phase 10 — Full test: email + blog ✅ (2 min)
Actions tab → Daily AI Digest → Run workflow → Run workflow.
Watch the log. Expected final lines:[INFO] Email sent to …[INFO] Published to Blogger: https://yourname.blogspot.com/2025/…
Open that link.
✅ Checkpoint — setup complete:

☑ Email in your inbox
☑ Post live on your blog (with a title like"🤖 AI News Digest — 14 stories — 05 May" and the labels AI, daily-digest)
Phase 11 — Daily operation (what "done" looks like)
Every day at 07:30 UTC (± up to 1 hour):

The job runs for ~1 minute (visible under the Actions tab).
Your email arrives.
A new post appears on your blog — the blog grows into your permanent,searchable AI-news archive; the email is your daily ping.
Phase 12 — Troubleshooting
Symptom	Cause	Fix
Log: 535 Authentication failed	Normal Gmail password used	Redo Phase 3; update SMTP_PASS
Red job: Missing required secret	Secret missing or misnamed	Redo Phase 4 / 9.6 — names are case-sensitive
Email arrives, log: Blogger publishing not configured — skipping	A Blogger secret is missing/typo'd	Check the 4 names in Phase 9.6
Blog stops updating after ~1 week	Consent screen left in "Testing"	Phase 9.3 step 4 → set In production, redo 9.5, update BLOGGER_REFRESH_TOKEN
Log: 401 … invalid_grant / invalid_client	Dead/typo'd refresh token or client credentials	Redo 9.4–9.5; update the secrets
Log: 404 … Blog not found	Wrong BLOG_ID	Re-read the number from the address bar (Phase 8, step 4)
Playground: invalid_client error	Gear-icon credentials missing/typo'd, or wrong app type	Redo 9.4–9.5 with Desktop app type
Post exists but page won't load for others	Blog set to Private	Intended if you chose Private (Phase 8, step 3) — log in to blogger.com to read
Email in spam	First delivery to that inbox	Mark "Not spam" once
Digest late	GitHub cron jitter	Wait 60 minutes before worrying
Digests stopped after ~2 months	GitHub's 60-day-idle rule	keepalive.yml prevents it — confirm Actions are enabled
"Quiet day" email	Slow news day / strict filters	Lower HN_MIN_POINTS or raise HOURS_LOOKBACK in digest.yml
[WARN] … failed — skipped in log	One news source down	Non-fatal — email and post still go out
Phase 13 — Monthly check ✅ (2 min)
Repo → Actions → ~30 successful runs.
One commit named chore: keepalive … exists.
Blog shows ~30 new posts for the month.
Skim one digest; tune MAX_ITEMS / HN_MIN_POINTS if needed.
Teardown (undo everything)
Repo → Settings → General → Delete repository — stops emails and posts.
myaccount.google.com/security → App passwords → delete ai-news-digest.
console.cloud.google.com → IAM & Admin → Settings → Delete project(removes the OAuth credentials).
Blogger → delete the blog — or keep it as your reading archive.
You are done. Ongoing effort: zero.

How to get this into GitHub (pick one)
Path A — fully in the browser, no downloads (recommended):

Create the repo (+ → New repository → ai-news-digest).
On the empty repo page: Add file → Create new file.
In the name box, type the full path with slashes — e.g. .github/workflows/digest.yml — GitHub creates the folders automatically.
Paste that file's content from above → Commit changes.
Repeat for all 6 files (~5 minutes total).
Path B — save locally, drag-and-drop in one shot:

On your computer, create a folder ai-news-digest containing a subfolder .github/workflows.
Save each block above as its file (Notepad/TextEdit → Save As, plain text, exact names).
Repo page → Add file → Upload files → drag the whole ai-news-digest folder contents in → Commit changes. (Dragging the folder preserves the structure.)
Either way, the files are final — no edits needed anywhere. Credentials never touch the files; they go in via Settings → Secrets and variables → Actions (SOP Phases 4 and 9.6).

Final verification checklist
☑ 6 files present, exact names/paths (SOP's "quick check" confirms v1.0 wiring)
☑ Secrets added: 3 email (Ph. 4) + 4 Blogger (Ph. 9.6) + optional EMAIL_BCC
☑ Actions → Run workflow once
☑ Log ends with [INFO] Email sent to … and [INFO] Published to Blogger: …
☑ Email in inbox + post live on yourname.blogspot.com
