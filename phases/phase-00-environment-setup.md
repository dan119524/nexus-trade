# Phase 00 · Environment and Project Setup

## Purpose

Prepare and verify the NEXUS Trade development environment, and give the existing repository the structure every later phase builds on.

By the end of this phase you will have:

- Python, Git, Graphviz, PlantUML, and Claude Code working
- the NEXUS repo cloned and opening cleanly in PyCharm
- a virtual environment with all dependencies installed
- `.env` secrets safely git-ignored, with a `.env.example` template
- the `docs/` folders, `AGENTS.md`, and `phases/` in place
- one written artifact: `docs/executive-summary.md`
- the phase merged into `main` and tagged `phase-00-completed`

Phase 00 is setup and direction only. **Do not** create domain classes, requirements, use cases, UML models, interfaces, or design patterns, and do not change any existing tool logic.

---

## Part 1 · Understand the Toolchain

| Tool | Job |
|---|---|
| PyCharm | Main editor |
| Python 3.12 | Runs the backend |
| venv + pip | Isolated dependencies from `requirements.txt` |
| Git + GitHub | Version history and hosting |
| pytest | Runs the test suite |
| Graphviz | Layout engine PlantUML needs |
| PlantUML (plugin) | Diagrams stored as `.puml` text |
| Claude Code | AI assistant, governed by `AGENTS.md` |
| OANDA practice account | Demo market data and orders |

---

## Part 2 · Verify Python

```bash
python3 --version
```

The output must report Python 3.12 (or the version your project uses). Fix the install before continuing if it doesn't.

---

## Part 3 · Verify Git

```bash
git --version
git config --global user.name
git config --global user.email
```

If the name or email is missing or wrong:

```bash
git config --global user.name "Daniel Tewelde"
git config --global user.email "your-email@example.com"
```

---

## Part 4 · Open the Repo and Create the Phase Branch

Open the NEXUS repo in PyCharm, then in the PyCharm terminal:

```bash
git status
git remote -v
```

Confirm the remote points to **your Nexus repo**, not your CSC 413 repo.

Sync and branch:

```bash
git switch main
git pull
git switch -c phase-00
git branch --show-current
```

The last command must print `phase-00`. Do all Phase 00 work on this branch.

---

## Part 5 · Add the Phase Instructions

At the repo root, create `phases/` and save this file as:

```
phases/phase-00-environment-setup.md
```

Also add `docs/phase-workflow.md` and `AGENTS.md` to the repo root if they aren't there yet.

---

## Part 6 · Set Up the Virtual Environment

From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

In PyCharm, set the interpreter to `.venv`:
**Settings → Project → Python Interpreter → Add Interpreter → Existing → `.venv/bin/python`**

Verify:

```bash
which python
pytest
```

`which python` must point inside `.venv`. `pytest` must run. If existing tests fail, **do not fix them in this phase**; write down which ones fail in your executive summary's notes and move on.

---

## Part 7 · Secure Your Secrets

Open `.gitignore` and confirm it contains at least:

```
.env
.venv/
.tmp/
__pycache__/
.pytest_cache/
.idea/
credentials.json
token.json
```

Create `.env.example` with placeholder names only (no real values):

```
OANDA_API_KEY=your-practice-api-key
OANDA_ACCOUNT_ID=your-practice-account-id
OANDA_ENVIRONMENT=practice
ANTHROPIC_API_KEY=your-anthropic-key
```

Check that `.env` has never been committed:

```bash
git log --all --oneline -- .env
```

This must print nothing. If it prints commits, stop: your keys are in Git history. Regenerate the OANDA and Anthropic keys right away, and fix the history before continuing.

---

## Part 8 · Create the Docs Structure

Create these folders at the repo root:

```
docs/
├── requirements/
├── design/
│   └── uml/
└── evolution/
```

Git doesn't track empty folders, so put an empty `.gitkeep` file in each one.

---

## Part 9 · Install and Verify PlantUML

Install Graphviz:

```bash
brew install graphviz
dot -V
```

`dot -V` must print a version. Restart PyCharm if it was open during the install.

In PyCharm: **Settings → Plugins → Marketplace**, search **PlantUML Integration**, install it, and restart.

Test it by creating `docs/design/uml/plantuml-practice.puml`:

```
@startuml
class ExampleA
class ExampleB
ExampleA --> ExampleB
@enduml
```

The preview should show two connected classes. Change `ExampleB` to `ExampleC` and confirm the preview updates. Then **delete the practice file**.

---

## Part 10 · Claude Code Read-Only Inspection

Open Claude Code in the repo and send:

> Inspect this repository in read-only mode. Read AGENTS.md first. Then explain the purpose of `tools/`, `workflows/`, `tests/`, `frontend/`, `docs/`, and `phases/`, and confirm `.env` is git-ignored. If something doesn't exist, say so instead of assuming. Do not modify, create, delete, stage, commit, or push anything.

Compare the answer with what you actually see. You decide whether it's correct.

---

## Part 11 · Write the Executive Summary

Create `docs/executive-summary.md` with one clear sentence per section:

```markdown
# NEXUS Trade Executive Summary

## Problem

## Intended Users

## General Purpose

## Initial Scope
```

- **Problem:** the real trading problem NEXUS solves
- **Intended Users:** who it's for
- **General Purpose:** what it helps them do
- **Initial Scope:** a realistic boundary, including at least one thing NEXUS will **not** do (for example, "will not trade with real funds")

Plain language only. No classes, patterns, frameworks, or architecture.

---

## Part 12 · Commit and Push

```bash
git branch --show-current     # must be phase-00
git status
```

Stage only the intended files:

```bash
git add phases
git add docs
git add AGENTS.md
git add .gitignore
git add .env.example
```

Never `git add .` or `git add -A`. Inspect before committing:

```bash
git status
git diff --staged
```

Confirm no `.env`, `.venv/`, `.idea/`, `.tmp/`, or cache files are staged. Then:

```bash
git commit -m "Complete Phase 00 project setup"
git push -u origin phase-00
```

---

## Part 13 · Final Read-Only Review

Send Claude Code:

> Review my repository against Phase 00 in `phases/phase-00-environment-setup.md`. Check: the current branch is phase-00; `.gitignore` covers `.env`, `.venv/`, `.tmp/`, caches, and OAuth files; `.env.example` has placeholders only; `.env` is not in Git history; the `docs/` structure exists; `AGENTS.md` and `phases/` exist; `docs/executive-summary.md` has all four sections with no design decisions; the practice `.puml` file is deleted; no secrets or generated files are committed. Report each finding and why it matters. Do not modify anything.

Evaluate each finding yourself. Fix only what's justified, commit it on `phase-00`, and push again.

---

## Part 14 · Merge and Tag

On GitHub, open a pull request:

- base: `main`
- compare: `phase-00`

Review the files, then merge. After it merges:

```bash
git switch main
git pull origin main
git tag -a phase-00-completed -m "Phase 00 completed"
git push origin phase-00-completed
git status
```

Phase 00 does not use a `phase-00-v1` tag. Change Phase 00's ⬜ to ✅ in the README roadmap.

---

## Completion Checklist

- [ ] `python3 --version` reports the project's Python version
- [ ] Git name and email are configured
- [ ] `git remote -v` points to the Nexus repo
- [ ] All work was done on `phase-00`
- [ ] This file is saved at `phases/phase-00-environment-setup.md`
- [ ] `.venv` is set up and PyCharm uses it
- [ ] `pip install -r requirements.txt` succeeds and `pytest` runs
- [ ] `.gitignore` covers `.env`, `.venv/`, `.tmp/`, caches, `.idea/`, OAuth files
- [ ] `.env.example` exists with placeholders only
- [ ] `.env` has never been committed
- [ ] `docs/requirements/`, `docs/design/uml/`, and `docs/evolution/` exist
- [ ] `dot -V` works and the PlantUML preview rendered
- [ ] The practice `.puml` file is deleted
- [ ] Both read-only Claude Code inspections were done and evaluated
- [ ] `docs/executive-summary.md` has all four sections
- [ ] No existing tool logic was changed
- [ ] The PR merged into `main`
- [ ] `phase-00-completed` is tagged on the merged `main`
- [ ] `git status` is clean on `main`

When every box is checked, NEXUS is ready for Phase 01, where requirements and design begin.
