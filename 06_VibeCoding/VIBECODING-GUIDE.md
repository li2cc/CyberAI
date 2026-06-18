# VibeCoding: Build Vulnerable Apps & Break Them — Complete Student Guide

Welcome to **VibeCoding** — a hands-on security exercise where you build a web app with intentional
vulnerabilities and peers try to break it. This single document contains everything you need: pick an
app, build it with Claude, hide your secret, run it, then break and fix.

**Your job:** Build a working web app, hide your **email address** as a secret (`CANARY_` prefix) in
the app's data, and push it to your GitHub repo for classmates to attack.

**Their job:** Find your `CANARY_` email by probing your running app and file an issue proving the break.

---

## 🤖 How to Use This File With Claude

This guide is designed to be handed to **Claude Code** (or any Claude assistant) so it can walk you
through the whole exercise. Open Claude Code in your terminal (`claude`) and paste this:

> I'm a grad student doing the "VibeCoding" security exercise. The full instructions are in this
> file (`VIBECODING-GUIDE.md`). Please read it, then help me:
> 1. Pick an app from the App Menu (ask me which one I want, or recommend one for a beginner).
> 2. Scaffold a working version using the Starter Prompt, going step-by-step.
> 3. Hide my email as `CANARY_<my-email>` somewhere in the data so it is used internally but
>    **never** returned over HTTP.
> 4. Give me the exact commands to install, run, and test it locally.
> 5. Help me fill in the "How to Run This App" template at the end.
>
> My email is: `<put-your-email-here>`. Go slowly so a beginner can follow along, and don't add
> security hardening — vulnerabilities are the point of this exercise.

Claude will then guide you through each phase below.

---

## Table of Contents

1. [The Exercise: Three Phases](#the-exercise-three-phases)
2. [Stack & Constraints](#stack--constraints)
3. [Phase 1 — Step 1: Pick an App](#phase-1--step-1-pick-an-app)
4. [Phase 1 — Step 2: Build It With Claude (Starter Prompt)](#phase-1--step-2-build-it-with-claude-starter-prompt)
5. [Phase 1 — Step 3: Hide Your Secret + Security Properties (P1–P5)](#phase-1--step-3-hide-your-secret--security-properties-p1p5)
6. [Phase 1 — Step 4: Run, Test & Document](#phase-1--step-4-run-test--document)
7. [Phase 2 — Break Other Apps](#phase-2--break-other-apps)
8. [Phase 3 — Fix Your App](#phase-3--fix-your-app)
9. [Using Claude Code Effectively](#using-claude-code-effectively)
10. [Grading Rubric](#grading-rubric)
11. [FAQ](#faq)
12. ["How to Run This App" Template (fill this in)](#how-to-run-this-app-template-fill-this-in)

---

## The Exercise: Three Phases

### Phase 1: Build (you build a vulnerable app)

1. **Pick an app** from the [App Menu](#phase-1--step-1-pick-an-app) (11 options).
2. **Use the Starter Prompt** — paste it into Claude Code to scaffold a working version.
3. **Hide your email** as `CANARY_[your-email]` somewhere in your app (a private record, admin field,
   database entry). The app may use it internally, but **must never leak it over HTTP**.
4. **Test locally** — run your app on `localhost` and confirm it works for a normal user.
5. **Document how to run it** in the [template at the end](#how-to-run-this-app-template-fill-this-in).
6. **Push to GitHub** — your app is now live for classmates to break.

### Phase 2: Break (classmates attack your app)

Classmates will run your app locally, probe it over HTTP trying to extract your `CANARY_` email, and
file an **Issue** on your repo if they find it, with **steps to reproduce**. You'll receive
notifications — respond to confirm whether the break is valid.

### Phase 3: Fix (optional)

If time permits, fix the vulnerabilities classmates found and demonstrate the patch.

### What you build must…

- **Run on `localhost`** (a high port like 5000, 8000, etc.) with no admin rights
- **Expose an HTTP interface** (REST API, web form, etc.) that users interact with
- **Hide your email** as `CANARY_[your-email]` in your app's data, not leaked over HTTP
- **Work end-to-end** — a classmate should be able to clone your repo, run your app, and use it

---

## Stack & Constraints

- **Language:** Python (Flask/FastAPI) or Node.js (Express)
- **Storage:** SQLite, JSON, or flat files (no external database server, no Docker)
- **Time:** ~2 hours with Claude Code help

**Recommendation for beginners:** Python + Flask. It's the easiest to learn and debug with Claude's help.

---

## Phase 1 — Step 1: Pick an App

Choose **one** web app below. Each runs on `localhost` with no external dependencies, and each has an
obvious place to hide your `CANARY_[email]` secret.

| # | App | What It Does | Where to Hide `CANARY_` | Attack Surface |
|----|-----|-------------|------------------------|-----------------|
| 1 | **Notes App with Login** | Users sign up, log in, and create private notes | Another user's note (e.g., admin note) | Can you read someone else's note? Can you modify it? |
| 2 | **Paste-bin Service** | Users paste code snippets, get a shareable link | A private/unlisted paste | Can you guess or enumerate paste IDs? |
| 3 | **URL Shortener** | Shorten long URLs, track click counts | An admin or private URL | Can you enumerate short links? Open redirect? |
| 4 | **Bookmark Manager** | Users save and organize bookmarks | Another user's bookmark | Can you access someone else's bookmarks? |
| 5 | **Simple Blog** | Post articles, leave comments | A draft or admin-only article | Can you read drafts? Inject JavaScript? |
| 6 | **File Upload Service** | Users upload and share files | A protected/private file | Path traversal? Can you read files you shouldn't? |
| 7 | **To-Do List Sharing** | Users create shared to-do lists | A private list with a hidden note | Can you access someone's private list? |
| 8 | **Contact Form API** | Users submit feedback; you store it | A reply email or internal recipient | Email injection? Can you exfiltrate data? |
| 9 | **Quiz / Poll App** | Create quizzes, users answer | The answer key (hidden field) | Can you peek at the answers? |
| 10 | **Key-Value Store** | Simple API to store and retrieve data | A reserved/admin key | Can you read or overwrite others' data? |
| 11 | **Simple Chat** | Send messages between users | Another user's messages | Can you read someone else's chat history? |

### How to pick

- **Never built a web app before?** Start with **#1 (Notes App)** or **#4 (Bookmark Manager)** — simple, familiar, easy to test.
- **Want something quick?** Pick **#2 (Paste-bin)** or **#3 (URL Shortener)** — fewer moving parts.
- **Want to learn auth?** Pick **#1 (Notes)** or **#7 (To-Do Sharing)** — both need login logic.
- **Want file handling?** Pick **#6 (File Upload)**.

### Complexity levels

All apps are buildable in ~2 hours with Claude:

- **Easy (1–2 hours):** Paste-bin, URL Shortener, Key-Value Store
- **Medium (2–3 hours):** Notes App, Bookmark Manager, To-Do Sharing
- **Harder (3+ hours):** Blog with comments, File Upload, Chat

### Where your `CANARY_` secret goes

Once you pick, decide where your email goes. For example:

- **Notes App:** Admin's private note or default profile email
- **Paste-bin:** A special "system" paste you create on startup
- **URL Shortener:** An admin short-link or usage statistics
- **Bookmark Manager:** An admin bookmarks folder
- **Blog:** A draft article only admins should see
- **File Upload:** A protected system file
- **To-Do Sharing:** A private list with your email in metadata
- **Contact Form:** The admin email where feedback is sent (store it in the DB)
- **Quiz:** The answer key, stored in the database
- **Key-Value Store:** A reserved key like `_admin_email` or `_system`
- **Chat:** A system message or admin user

Pick a place that feels natural for your app, then **make sure it never leaks over HTTP**.

---

## Phase 1 — Step 2: Build It With Claude (Starter Prompt)

Copy this prompt, **fill in your app choice and stack**, and paste it into Claude Code. It will
scaffold a working app for you.

```
I'm a grad student building a vulnerable web app for a security exercise.
I need to build: [PICK ONE FROM THE APP MENU, e.g., "a Notes app with login"]

Stack: [CHOOSE: Python with Flask | Python with FastAPI | Node.js with Express]

Requirements:
1. The app runs ONLY on localhost (a high port, no admin rights)
2. It has a working HTTP interface — users can interact with it via a web form or REST API
3. Somewhere in the app's data, I store a secret: CANARY_[my-email-address]
   - The secret must NEVER appear in any HTTP response
   - It should be stored in the database/JSON/file so the app can use it internally, but never return it
4. It should work end-to-end — I can test it locally
5. Keep it simple — I don't need fancy UI, just a working backend

Please:
1. Explain why you chose that stack (one sentence)
2. Create each file I need, explaining what it does in plain language
3. Give me the exact install commands and how to run it
4. Tell me where the CANARY_[email] secret is stored and confirm it won't leak
5. Go step-by-step — pause after each file so I can keep up

Don't over-engineer it or add security hardening yet — that's what the peer testing phase is for.
Go slowly so a beginner can follow along.
```

### How to use it

1. **Open Claude Code** in your terminal: `claude`
2. **Fill in your app choice** (change the `[PICK ONE...]` line).
3. **Choose your stack** — `Python with Flask` (recommended for beginners), `Python with FastAPI`, or
   `Node.js with Express`.
4. **Paste the edited prompt into Claude Code** and let it scaffold your app.
5. **Follow along step-by-step** — don't run all commands at once; test as you go.

### What Claude will do

- Create a `requirements.txt` (or `package.json`)
- Create a main app file (`app.py` or `server.js`)
- Create a database schema or JSON structure
- Provide install and run commands
- **Confirm where your `CANARY_` secret is stored** and that it won't leak
- Ask you to test locally after each step

---

## Phase 1 — Step 3: Hide Your Secret + Security Properties (P1–P5)

Your app should **aim to protect** these five properties. Your classmates will try to break them.
These describe what "security" means in this exercise. You don't need to defend all five — in fact,
leaving a few vulnerabilities intentional makes the exercise more interesting!

### P1: Confidentiality — Keep Secrets Secret

**Your app must never leak the `CANARY_[email]` secret through the HTTP interface.**

- ✅ OK: Store it in the database so your app can use it, but never return it in responses
- ✅ OK: Use it internally (e.g., send an email from that address), but don't expose it
- ❌ Bad: Return it in an API response
- ❌ Bad: Include it in a page you serve
- ❌ Bad: Log it where an attacker can read the logs

**How classmates will attack it:** Probe all endpoints for the secret; access other users' data; look
in HTML comments or JavaScript; check response headers.

### P2: Correctness — Do What You Say You Do

**Your app should work as described in your "How to Run This App" documentation.**

- ✅ OK: Users can sign up, log in, create notes, etc.; features work as expected
- ❌ Bad: A feature crashes on normal input; data disappears unexpectedly; the app doesn't match docs

**How classmates will attack it:** Follow your instructions to use the app normally; look for edge
cases (empty names, very long input); try to break the expected flow.

### P3: Input Discipline — Handle Bad Input Gracefully

**Your app should accept user input without crashing or behaving weirdly.**

- ✅ OK: Blank field → show an error, don't crash; very long string → truncate or reject gracefully;
  weird characters → handle without breaking
- ❌ Bad: App crashes on unexpected input; input causes file corruption or database errors

**How classmates will attack it:** Send empty, null, or unusually large input; try special characters
(`<>`, `"`, `'`, `;`, `--`); try to crash the app.

### P4: No Injection — Never Run User Input as Code

**Your app must never execute user input as code, SQL, file paths, or templates.**

- ✅ OK: Parameterized SQL queries (`?` placeholders, not string concatenation)
- ✅ OK: Templating libraries used safely (Flask's `render_template` with `{{ }}`)
- ✅ OK: Never `eval()`, `exec()`, or `os.system()` on user input
- ❌ Bad: `"SELECT * FROM users WHERE name = '" + name + "'"`
- ❌ Bad: `eval()` / `exec()` on user input
- ❌ Bad: `subprocess`/shell commands on user input without escaping
- ❌ Bad: Concatenating file paths: `/data/` + username (path traversal)

**How classmates will attack it:** SQL `' OR '1'='1`; commands `; rm -rf /`; path traversal
`../../../etc/passwd`; template injection `{{ 1 + 1 }}`.

### P5: Authorization & Output Safety — Protect Private Data & Prevent XSS

**Require authentication for private data and never return unsanitized user input.**

**Authorization (access control):**
- ✅ OK: Users only see their own data; admin features require login; endpoints check who's logged in
- ❌ Bad: Anyone can see anyone's data without logging in; guessing a user/note ID gives access;
  private endpoints accessible without auth

**Output safety (XSS prevention):**
- ✅ OK: User input is **HTML-escaped** when displayed (`<` becomes `&lt;`); use templating safely
- ❌ Bad: Returning user input directly in HTML without escaping; using `innerHTML` with user data;
  letting users inject `<script>` tags that run in classmates' browsers

**How classmates will attack it:** Access data without logging in; change a user/note ID in the URL;
guess sequential IDs; submit `<script>alert('XSS')</script>` and see if it runs.

### How to think about security

Your app doesn't need to be bulletproof — that's the point. But think about each property:
1. **P1:** Is my secret truly hidden? Can I find it by probing the API?
2. **P2:** Does my app actually work as documented?
3. **P3:** What happens if I submit weird input?
4. **P4:** Am I concatenating user input into SQL or commands?
5. **P5:** Can I see someone else's data? Can I inject HTML?

The more honest you are about weaknesses, the better the peer testing phase will be.

---

## Phase 1 — Step 4: Run, Test & Document

### Test it locally

```bash
python app.py          # Python
# or
npm start              # Node
```

Then open the local URL (e.g., `http://localhost:5000`) and confirm normal use works.

### Verify your secret doesn't leak

Use `curl` or a browser to probe every endpoint and make sure `CANARY_[email]` never appears in a
response. Ask Claude to help:

```
Test my app at http://localhost:5000 and tell me if the CANARY_[email] secret leaks in any response.
Try every endpoint I documented, and show me every response that might contain the secret.
```

### Document it

Fill in the [template at the end of this file](#how-to-run-this-app-template-fill-this-in) so
classmates can run your app. Then push:

```bash
git add .
git commit -m "Add vulnerable [app name] app"
git push origin main
```

**Bonus (honesty, +5%):** Document known vulnerabilities in code comments, e.g.
`# TODO: This query is vulnerable to SQL injection if user_input is not sanitized`.

---

## Phase 2 — Break Other Apps

After you build and push, you'll attack 2–3 classmates' apps and file issues proving the break.
**Your primary goal:** find the `CANARY_` secret — that's a guaranteed valid break.

### Step 1: Clone and run their app

```bash
git clone <their-repo-url>
cd <their-repo>
# Follow their "How to Run This App" instructions exactly:
# - install dependencies, run the app, confirm it loads and basic features work
```

### Step 2: Know what you're looking for

Probe for the [five properties](#phase-1--step-3-hide-your-secret--security-properties-p1p5):
P1 Confidentiality, P2 Correctness, P3 Input Discipline, P4 No Injection, P5 Authorization & XSS.

### Step 3: Attack systematically (black-box first — HTTP only)

**Map the API** — test every endpoint they documented:

```bash
curl http://localhost:5000/api/notes
curl http://localhost:5000/api/notes/1
curl http://localhost:5000/api/users
```

Note: what endpoints exist, what they return, and whether any response contains `CANARY_`.

**Try common attacks in order:**

1. **Unauthenticated access** — hit private endpoints with no auth:
   ```bash
   curl http://localhost:5000/api/private-endpoint
   ```
2. **Enumeration (IDOR)** — try sequential IDs:
   ```bash
   curl http://localhost:5000/api/notes/1
   curl http://localhost:5000/api/notes/2
   curl http://localhost:5000/api/notes/3
   ```
3. **Path traversal** — if they serve files:
   ```bash
   curl http://localhost:5000/files/../../../etc/passwd
   ```
4. **Empty/weird input:**
   ```bash
   curl -X POST http://localhost:5000/api/notes -H "Content-Type: application/json" -d '{"title": ""}'
   curl -X POST http://localhost:5000/api/notes -d '{"title": null}'
   ```
5. **Stored XSS** — submit HTML/JS, then view it in a browser:
   ```bash
   curl -X POST http://localhost:5000/api/notes -H "Content-Type: application/json" \
     -d '{"title": "<script>alert(1)</script>"}'
   ```
6. **SQL injection:**
   ```bash
   curl "http://localhost:5000/api/notes?title=' OR '1'='1"
   curl "http://localhost:5000/api/notes?id=1; DROP TABLE notes--"
   ```
7. **Email/header injection** — if they send emails:
   ```bash
   curl -X POST http://localhost:5000/api/contact -d "email=attacker@evil.com%0aBcc:attacker@evil.com"
   ```

### Step 4: If black-box isn't working, read the source

Once you've exhausted HTTP probing, you **may** read their `app.py`/`server.js` for obvious bugs
(hardcoded secrets, unescaped output, SQL concatenation). **But you must still prove the break over
HTTP** — "the code looks vulnerable" doesn't count; show it actually happens.

### Step 5: File the issue (Break Report)

**Option A — GitHub UI:** Repo → Issues → New issue → Break Report. Fill in the six fields:
Target artifact, Attack class (IDOR / XSS / SQL Injection / Unauthenticated Access / …), Property
violated (quote P1–P5), Steps to reproduce, Evidence, Severity.

**Option B — CLI (faster):**

```bash
gh issue create --repo <their-org>/<their-repo> \
  --title "Break Report: [brief description]" \
  --body "
## Target artifact
[endpoint or feature]

## Attack class
[IDOR / XSS / SQL Injection / Unauthenticated Access / etc.]

## Property violated
P1 Confidentiality — [quote from the spec]

## Steps to reproduce
\`\`\`bash
curl http://localhost:5000/...
\`\`\`

## Evidence
[output showing the vulnerability]

## Severity
High
"
```

### Step 6: They respond

The app's owner reproduces your steps and replies **`/repro-confirmed`** (valid) or
**`/repro-failed`** (can't reproduce). **Only `/repro-confirmed` issues count**, so make your steps
copy-paste reproducible.

### Do's ✅ and Don'ts ❌

- ✅ Be clear and specific; test your own steps before filing; use `curl` (reproducible); be respectful.
- ❌ Don't be destructive (no deleting data), don't guess, don't be vague, don't file duplicates
  (comment on the existing issue instead), don't include actual malware/exploits.

---

## Phase 3 — Fix Your App

This phase is **optional but encouraged** — you learn the most by fixing.

1. **Read the issue** filed against you and understand the vulnerability.
2. **Reproduce it yourself** to confirm it's real.
3. **Identify the root cause** in your code.
4. **Make a fix** and **test** that the old attack no longer works (and nothing else broke).
5. **Submit a PR:**
   ```bash
   git checkout -b fix/issue-N
   # make changes
   git push origin fix/issue-N
   # open a pull request with "closes #N" in the body
   ```
6. **Wait for the reporter** to test and comment `/fix-confirmed` (the issue closes automatically).

Ask Claude for help understanding and patching:

```
This issue was filed against my app: [paste issue]
Here's my current code: [paste code]
Explain the vulnerability in plain language and show me the corrected code.
```

---

## Using Claude Code Effectively

**Start it:** `claude` (or `claude "help me debug this error: ..."`).

**General tips:**
- **Be specific:** "When I run `python app.py`, I get `ModuleNotFoundError: No module named 'flask'`"
  beats "my app doesn't work."
- **Show your work:** paste the code *and* the error.
- **Test before asking**, and **ask for explanations** of *why* a fix works.
- **Let Claude create files one at a time** and test as you go — don't generate everything at once.

**Verify your secret before pushing:**
```
Where is my CANARY_[email] secret stored in the code, and confirm it will never leak over HTTP.
```

**✅ Do ask Claude:** how to fix an error, how to test an endpoint, how to understand a reported
vulnerability, how to implement a feature, how to use Flask/Express.

**❌ Don't ask Claude:** for a complete solution without trying, how to hide malicious code, how to
DoS/crash someone's app, or how to cheat/plagiarize.

### Quick reference: common commands

```bash
# Run your app
python app.py              # Python
npm start                  # Node

# Test an endpoint
curl http://localhost:5000/api/endpoint
curl -X POST http://localhost:5000/api/endpoint -H "Content-Type: application/json" -d '{"field": "value"}'

# Check if a port is in use
lsof -i :5000              # macOS/Linux
netstat -ano | grep 5000  # Windows

# Git
git status
git add .
git commit -m "Add vulnerable notes app"
git push origin main
git checkout -b fix/issue-1
```

---

## Grading Rubric

| Phase | Component | Points | How |
|-------|-----------|--------|-----|
| **Build** | Does it work? | 20 | App runs and core features work end-to-end |
| **Build** | Secret hidden? | 10 | `CANARY_` stored but doesn't leak over HTTP |
| **Build** | Documentation clear? | 10 | "How to Run" is complete; example curls work |
| **Break** | Issues found? | 30 | 2+ confirmed issues = full credit; 1 = partial |
| **Fix** | Fixed responsibly? | 20 | Triage or fix issues (optional but encouraged) |
| **Bonus** | Honest about bugs? | 5 | Document known vulnerabilities in comments |
| | **TOTAL** | **100** | |

**Notes:**
- You're not graded on *preventing* breaks — you're graded on building a working app and
  *acknowledging* valid breaks (`/repro-confirmed`) honestly.
- Finding your own secret (`CANARY_`) is always a valid break.
- Fix phase: even clear triage ("would fix X next") earns partial credit.

---

## FAQ

### Build

**How do I choose an app?** Pick from the [App Menu](#phase-1--step-1-pick-an-app). Beginners:
#1 Notes, #4 Bookmark Manager, or #2 Paste-bin. Pick one that sounds fun.

**What if I don't like any?** Build your own, as long as it runs on localhost, has an HTTP interface,
stores a non-leaking `CANARY_[email]`, and works end-to-end.

**Python or Node?** Python + Flask is easiest for beginners. Node + Express if you know JS. Claude can
scaffold either.

**How do I make sure my secret doesn't leak?** Store it in the DB/JSON/file, never return it in any
response, check every endpoint with `curl`, and ask Claude to test for leaks before you push.

**Can I add extra features?** Yes, as long as the app still runs locally, stores your secret, and works.

**My app crashed.** Read the error, paste it into Claude, and build/test one feature at a time.

**Port already in use?** Kill the other process (`lsof -i :5000` / `netstat -ano | grep 5000`) or
change your port (`app.run(port=5001)` / `app.listen(5001)`).

**Should I commit my `CANARY_` secret to GitHub?** Yes — it lives in your code/DB and that's fine. The
point is that classmates find it *over HTTP*, not by reading source.

### Breaking

**How do I find vulnerabilities?** See [Phase 2](#phase-2--break-other-apps): clone & run, map the
API, try common attacks (IDOR, XSS, SQLi), look for `CANARY_`.

**Is this a real vulnerability?** Ask Claude: paste your steps + output and ask whether it violates a
property (P1–P5).

**Can I look at their source?** Yes, but only after black-box attacks, and you must still prove the
break over HTTP.

**They didn't respond to my issue.** Make sure you filed a proper Break Report with clear, exact,
reproducible steps. If so and they still don't respond, escalate to your instructor.

**Someone already found the same bug.** Comment on their issue with your additional path instead of
filing a duplicate.

**Can I destroy data or crash their app?** No. Reading data (`curl GET`) is fine; deleting/destroying
(`curl -X DELETE`) is not.

**How many should I find?** Aim for 2–3 across classmates' apps.

### Fixing

**Do I have to fix everything?** No — Fix is 20% and triage earns partial credit. Fixing one teaches
the most.

**How do I fix a reported bug?** Read it, reproduce it, find the root cause, patch, and test that the
old attack fails. Ask Claude for help on the patch.

**The issue is vague.** Comment asking for clarification — be respectful, the reporter is a classmate.

**How do I submit a fix?** Branch (`git checkout -b fix/issue-5`), change, push, open a PR with
`closes #5`, and wait for `/fix-confirmed`.

### Concepts

**SQL injection:** running user input as SQL. Fix with parameterized queries:
`cursor.execute("SELECT * FROM users WHERE name = ?", (name,))`.

**IDOR (Insecure Direct Object Reference):** guessing/enumerating IDs to access data you shouldn't
(e.g., `/api/notes/3` returns someone else's note).

**XSS (Cross-Site Scripting):** injecting code (usually JS) that runs in another user's browser.
*Stored* XSS lives in the DB and runs for everyone who views it; *reflected* XSS runs via a crafted URL.

**Why not `eval()` on user input?** It runs arbitrary code. Never use `eval()`/`exec()` on user input.

### Misc

**Time budget:** Build 2–3h, Break 1–2h, Fix 1–2h (optional). If stuck >30 min, ask Claude or your
instructor.

**Can I work with a partner?** Yes for concepts/debugging, but each person submits their own app and
should be able to explain their choices.

**New to web dev — too hard?** No. Claude scaffolds it; your job is to understand it, test it, and
learn from what classmates find.

---

## "How to Run This App" Template (fill this in)

> **Fill this in after your app is working locally.** This is how classmates will run and test your
> app. Keep it accurate — a break only counts against an app a breaker can actually start from these
> instructions.

```markdown
# How to Run This App

## App Name
[e.g., "Notes App with Login"]

## Prerequisites
- Python 3.8+ (or Node.js 14+)
- Git
- pip (Python) or npm (Node)

## Installation

### Python
git clone <repo-url>
cd <repo-directory>
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

### Node.js
git clone <repo-url>
cd <repo-directory>
npm install

## Running
python app.py        # Python → http://localhost:5000 (or your port)
# npm start          # Node   → http://localhost:3000 (or your port)

## Accounts / credentials for legitimate use
[e.g., alice / alice123]

## Endpoints to try
- GET  /                          [describe]
- POST /login                     [username + password]
- GET  /notes/<id>                [view a note]
- POST /notes                     [create a note: title + body]
[Add 3–5 example curl commands so classmates know what exists]

## A benign request that should succeed
curl -s -c cookies.txt -X POST -d "username=alice&password=alice123" http://localhost:5000/login
curl -s -b cookies.txt http://localhost:5000/

## Where the CANARY_ secret is
- Location: [e.g., admin user's email in the users table]
- Stored how: [e.g., in the SQLite DB]
- Does it leak? No — never returned in any HTTP response (or is it? that's the exercise!)

## Database / Storage
[e.g., SQLite app.db, auto-created on first run]

## Stopping
Ctrl+C in the terminal running the app.

## For breakers
Attack this running app over HTTP. Do not read the source or the secret/ folder to find a break —
prove it over HTTP. Probe for the five properties (P1–P5) described above.
```

---

# Appendix A — For Instructors: Classroom Guide

This appendix explains how to set up and run the VibeCoding exercise with graduate students.
(Students can ignore everything below this line — it's for whoever is running the course.)

## Overview

**VibeCoding** is a hands-on security exercise where students:

1. **Build Phase (2–3 hours):** Build a web app with intentional vulnerabilities using Claude
2. **Break Phase (1–2 hours):** Attack 2–3 classmates' apps and file issues
3. **Fix Phase (1–2 hours, optional):** Triage and fix issues filed against their own app

**Learning outcomes:** students build real web apps with AI assistance; understand vulnerability
classes (IDOR, XSS, SQL injection, etc.) by finding them; learn to write clear vulnerability reports;
and practice defensive security by fixing bugs.

## Setup (before class)

### 1. Create a GitHub Classroom

1. Go to https://classroom.github.com
2. Create a new assignment with a **template repository**
3. The template should contain this guide (or a simplified clone of it)

**Include in the template:** this `VIBECODING-GUIDE.md`, a `.gitignore` for Python/Node, optionally an
empty `requirements.txt`/`package.json` starting point. **Do NOT include:** full working app code or
the `secret/` folder — students create those.

### 2. Share the classroom link with students

Send the GitHub Classroom link, a brief overview ("you'll build a web app with security
vulnerabilities for your peers to find"), an estimated time (5–6 hours total), and deadlines for the
Build and Break phases.

### 3. Set up access

Ensure all students have Claude Code access (Pro/Max/Team or API). If using Codespaces, enable them on
your org. Provide GitHub CLI setup instructions if needed.

## In-class schedule

### Phase 1: Build (90 minutes)

- **0–5 min — Brief:** "You have 90 minutes to build a working web app. Pick one from the App Menu, use
  the Starter Prompt to scaffold it with Claude, test it locally, fill in the 'How to Run' template,
  and hide your email as `CANARY_[email]` without leaking it. Push to GitHub when done."
- **5–85 min — Work time:** students clone their repo, scaffold with Claude, test locally, document, push.
- **85–90 min — Demo (optional):** each student briefly shows their app running and confirms the secret
  is stored but not leaked.
- **Support:** circulate and help students get started; point them to the Starter Prompt and Claude
  tips; if someone's stuck, have them show Claude the error; remind them not to over-engineer.

### Phase 2: Break (90 minutes, working lunch)

- **0–5 min — Brief:** "Attack 2–3 classmates' apps. Clone their repo, follow their 'How to Run'
  instructions, try to find vulnerabilities and extract their `CANARY_` secret. File a Break Report
  issue for each one."
- **5–85 min — Peer testing:** provide each student a list of 3–5 targets; students run, probe, and file
  Break Report issues.
- **85–90 min — Present findings:** each team describes the most interesting vulnerability; confirm the
  target team can reproduce it.
- **Support:** help students write good reports (all six fields); remind them to be constructive; verify
  app owners are confirming/denying issues.

### Phase 3: Fix (90–120 minutes, optional)

- **0–5 min — Brief:** "Fix issues filed against your app. Read each one, understand the vulnerability,
  fix the code, open a PR. Fix at least one — the more you fix, the more you learn."
- **5–85 min — Fixing:** students triage, branch, fix, push PRs, and ask reporters to test.
- **85–90 min — Reflection:** what they learned; which vulnerabilities surprised them; how they'd
  redesign from scratch.
- **Support:** help with unanticipated vulnerabilities; guide on common fixes (SQLi, IDOR, XSS);
  encourage thorough testing of fixes.

## Grading

Use the [Grading Rubric](#grading-rubric) above. Summary: Build 40% (works / secret hidden / docs),
Break 30% (2+ confirmed issues), Fix 20% (triage or fix), Bonus 5% (documented known vulnerabilities).
Adjust weights based on time spent per phase.

## Logistics

**Target assignment list** — share a sheet so students know which apps to attack:

| Student Name | Repo URL | Target 1 | Target 2 | Target 3 |
|---|---|---|---|---|
| Alice | github.com/.../alice-bbf | Bob | Carol | Dave |
| Bob | github.com/.../bob-bbf | Carol | Dave | Alice |

**Notifications:** ensure students are subscribed to their own repos and have GitHub notifications
enabled so they see filed issues.

**Office hours:** plan after-class support — Build (debugging), Break (understanding vulnerabilities),
Fix (patching guidance).

## Tips for success

**Before class:** test the whole flow yourself (build, attack, fix); prepare 2–3 sample vulnerable apps
as practice targets; review the breaking guide and the P1–P5 spec so you can judge issues.

**During class:** emphasize the learning goal (understanding vulnerabilities, not bulletproofing);
encourage respectful peer feedback (filing an issue is helping); set timing expectations; monitor
GitHub issues and help with invalid/unreproducible ones.

**Edge cases:**
- *"My app crashed and I can't fix it in time"* — they submit what they have; partial credit for effort
  and documentation; they can fix it in the Fix phase.
- *"I found a vulnerability but I'm not sure it's real"* — have them ask Claude or you; help write a
  clear reproduction.
- *"Nobody filed issues against my app"* — rare but fine; still full Build credit; they can proactively
  find and fix bugs in the Fix phase.
- *"They didn't confirm my issue"* — escalate to you; mediate whether the break is real.

## Variations & extensions

- **Harder:** shorter phases (60 min); assign specific targets at scale; require all five properties be
  targeted across the class; award more points for P4/P5 over P1.
- **Easier:** provide sample apps to extend; extend build time to 4–5 hours; give a guided attack
  checklist; make the Fix phase optional.
- **Online/async:** Build by end of week; issues open for a week; fixes the following week; demos over
  Zoom.
- **Competition:** scoreboard for most valid breaks; small prize for top breakers/fixers; public
  leaderboard (with consent).

## Learning outcomes checklist

By the end, students should be able to: build a working web app with AI assistance; understand
confidentiality, correctness, input handling, injection, and authorization; find real vulnerabilities
in a running app; write clear, reproducible vulnerability reports; fix security bugs from peer
feedback; and think like both attacker and defender.

## Troubleshooting

- *"Claude is making mistakes in scaffolding"* — normal; students read it, test, tell Claude what's
  wrong, iterate. This teaches debugging and working with AI.
- *"Some apps aren't running locally"* — usual causes: port conflict, missing dependencies,
  Python/Node not installed, virtualenv issues. Help troubleshoot or have them ask Claude.
- *"Attacks are too easy/hard"* — too easy is fine (vulnerabilities are intentional); too hard, walk
  them through the breaking guide or pair them up.
- *"A team is arguing about whether a break is valid"* — view the issue and steps, try it yourself,
  judge against P1–P5 and reproducibility, decide and explain.

## Feedback for next time

After the exercise, ask students what worked and was confusing; update materials; keep a log of the
most common vulnerabilities and what students learned best from; iterate on instructions, app
difficulty, and time allocations.

---

# Appendix B — Project Overview & Customization

## Workflow at a glance

**For students:**

```
1. Get this guide (via GitHub Classroom)
   ↓
2. Read the overview and three phases
   ↓
3. Build Phase (2–3 hours)
   → Pick app from the App Menu
   → Use the Starter Prompt with Claude Code
   → Claude scaffolds the app
   → Test locally → fill in the "How to Run" template → push to GitHub
   ↓
4. Break Phase (1–2 hours)
   → Clone 2–3 classmates' repos → follow their "How to Run"
   → Probe systematically → file Break Report issues
   ↓
5. Fix Phase (1–2 hours, optional)
   → Read issues filed against your app → fix at least one → push a PR
   ↓
6. Done! Check the FAQ if stuck anywhere
```

**For instructors:**

```
1. Create a GitHub Classroom with this guide as the template
   ↓
2. Read Appendix A (full setup and timeline)
   ↓
3. Brief students (~5 min) before each phase
   ↓
4. Support students during work (circulate, help debug)
   ↓
5. Use the Grading Rubric to evaluate
   ↓
6. Collect feedback and iterate for next time
```

## Quick links by task

- **"I don't know where to start"** → [The Exercise: Three Phases](#the-exercise-three-phases)
- **"How do I build my app?"** → [Starter Prompt](#phase-1--step-2-build-it-with-claude-starter-prompt) → [Using Claude Code Effectively](#using-claude-code-effectively)
- **"How do I attack someone's app?"** → [Phase 2 — Break Other Apps](#phase-2--break-other-apps)
- **"What counts as a real vulnerability?"** → [Security Properties P1–P5](#phase-1--step-3-hide-your-secret--security-properties-p1p5) and the [FAQ](#faq)
- **"How do I fix my app?"** → [Phase 3 — Fix Your App](#phase-3--fix-your-app)
- **"What am I being graded on?"** → [Grading Rubric](#grading-rubric)

## Customization tips

Adapt this for your course freely:

- **Time:** adjust phase durations (everything assumes ~90 min per phase)
- **Difficulty:** simpler apps for beginners, harder ones for advanced students
- **Scope:** make breaking optional, or extend it to require more vulnerabilities
- **Tools:** swap in your preferred testing tools (Burp, Postman, etc.)
- **Language:** add Flask-vs-FastAPI guidance, or drop Node.js if not needed

---

Enjoy the exercise — learn by breaking and defending! 🎯
