# VibeCoding: Build Vulnerable Apps & Break Them

Welcome! This repo is the starting point for the **VibeCoding** security exercise:
you build a web app with intentional vulnerabilities, hide your email as a
`CANARY_` secret, push it to GitHub, and classmates try to break it.

Everything you need is in **[`VIBECODING-GUIDE.md`](VIBECODING-GUIDE.md)**.

You don't have to read the whole guide yourself — let an AI coding assistant
(Claude Code, Cursor, or any "vibe coding" tool) read it and walk you through.

---

## 🚀 How to start (pick one)

### Option A — Clone the repo, then ask your AI assistant to read the guide (recommended)

```bash
git clone <this-repo-url>
cd <repo-directory>
```

Then open your AI coding tool **in that folder** (for Claude Code, just run
`claude` in the terminal) and send it this message:

> Read `VIBECODING-GUIDE.md` in this repo and tell me how to start. I'm a
> beginner. Walk me through it step by step: help me pick an app, scaffold it,
> hide my email as a `CANARY_` secret that never leaks over HTTP, and give me
> the exact commands to run and test it. My email is: `<put-your-email-here>`.

The assistant will read the guide and guide you through the whole exercise.

### Option B — Copy the guide and paste it as a prompt

1. Open **[`VIBECODING-GUIDE.md`](VIBECODING-GUIDE.md)** and copy **all** of its contents.
2. Paste it into Claude (or another AI assistant) and add at the end:

> ☝️ Those are my full instructions. I'm a beginner — please read them and tell
> me how to start, then walk me through it step by step. My email is:
> `<put-your-email-here>`.

The assistant will then guide you through each phase.

---

## What's in this repo

| File | What it is |
|------|------------|
| [`VIBECODING-GUIDE.md`](VIBECODING-GUIDE.md) | The full exercise instructions — hand this to your AI assistant |
| `.gitignore` | Ignores Python/Node build artifacts (virtualenvs, caches, databases) |

This is a clean starting template — you'll create your own app files
(`app.py`, `requirements.txt`, etc.) during the Build phase with your
assistant's help.

---

## The exercise in one picture

```
1. Get this repo  →  2. Ask your AI assistant to read VIBECODING-GUIDE.md
        ↓
3. BUILD: pick an app, scaffold it, hide your CANARY_ email, run & test, push
        ↓
4. BREAK: clone classmates' apps, probe over HTTP, find their CANARY_, file issues
        ↓
5. FIX (optional): patch the bugs filed against your app
```

Have fun — learn by breaking and defending! 🎯
