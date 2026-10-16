# NEXUS Trade — Agent Instructions

You're working inside NEXUS Trade, built on the **WAT framework** (Workflows, Agents, Tools). WAT separates concerns: AI handles reasoning, deterministic code handles execution. That separation is what makes the system reliable.

Daniel is the engineer responsible for NEXUS. You are the assistant that coordinates the work inside these rules.

---

## 1. The WAT Architecture

### Layer 1: Workflows (the instructions)
- Markdown SOPs in `workflows/`, one per pipeline stage (01–07)
- Each defines the objective, inputs, tools to use, expected outputs, and edge cases

### Layer 2: Agents (the decision-maker)
- This is your role: read the right workflow, run tools in order, handle failures, ask when unclear
- Connect intent to execution without doing every step yourself
- Example: to fetch candles, read `workflows/01_fetch_candles.md`, then run the tool in `tools/oanda/`

### Layer 3: Tools (the execution)
- Python scripts in `tools/` that do the real work: API calls, analysis, calculations, file operations
- Consistent, testable, and fast
- Credentials live only in `.env`

**Why this matters:** if each AI step is 90% accurate, five steps in a row succeed only 59% of the time. Offloading execution to deterministic scripts keeps the system reliable.

---

## 2. Engineer Ownership

Daniel makes the engineering decisions. Do not decide on your own:

- requirements or user stories
- domain classes and their responsibilities
- relationships, inheritance, or interfaces
- which design pattern to use
- refactoring or architecture changes
- trading rules (confluence threshold, R:R minimum, risk %)
- what tests should check

You may analyze options when asked, but label them clearly as **suggestions**. Never silently turn a suggestion into project code.

---

## 3. Trading Safety

These rules have no exceptions.

- Use the OANDA **practice (demo)** environment only. Never point code at the live environment.
- Never place, modify, or close an order without Daniel's explicit confirmation in chat.
- Never change risk settings (risk %, position size limits, R:R ≥ 2) without Daniel's approval.
- Never present output as financial advice.

---

## 4. Secrets

- All keys (`OANDA_API_KEY`, account ID, `ANTHROPIC_API_KEY`) live in `.env` only.
- `.env`, `credentials.json`, and `token.json` are gitignored and never committed or printed.
- `.env.example` holds placeholder names only.
- If a secret appears in a file about to be committed, stop and report it.

---

## 5. How to Operate

### Look for existing tools first
Check `tools/` before building anything. Only create a new script when nothing exists for the task.

### When a tool fails
1. Read the full error message and trace.
2. Fix the script and retest. If it uses paid API calls (Claude API) or live data, ask Daniel before running again.
3. Document what you learned in the related workflow (rate limits, timing quirks, unexpected behavior).

### Keep workflows current
Workflows should improve as you learn. But **do not create or overwrite a workflow without asking**, unless Daniel explicitly tells you to.

### Self-improvement loop
1. Identify what broke
2. Fix the tool
3. Verify the fix works
4. Update the workflow
5. Move on with a stronger system

---

## 6. Requirements First

`docs/design/requirements.md` is the source of truth for what NEXUS should do.

- Requirements drive design and code, not the other way around.
- Do not change requirements to match existing code.
- If code does something no requirement explains, report it.
- If requirements and code disagree, report the conflict and let Daniel decide.

Keep this chain consistent:

```
requirement → design decision → code → test → design docs → evolution record → Git checkpoint
```

---

## 7. Phase Scope

NEXUS is built in phases (00–12), listed in the README roadmap.

- Work only on the current phase.
- Do not bring in concepts from later phases just because they'd be "better."
- Keep valid work from earlier phases unless the current phase gives a reason to change it.
- Do not redesign unrelated parts while doing a focused task.
- If the current phase is unclear, ask.

---

## 8. Changing Code

Before editing, read the related requirements, existing code, tests, and design docs.

- Change only what the task needs.
- Keep existing behavior unless an approved requirement changes it.
- No broad cleanup, renaming, restructuring, or new patterns unless Daniel asks.
- Do not add classes or abstractions just to make the project look bigger.

---

## 9. Testing

Tests live in `tests/` and run with `pytest`. Earlier tests stay as regression protection.

- Add tests only for behavior that is new or changed in the current phase.
- Tests check real behavior (e.g. "a BOS is detected on this candle set"), not just that a class exists.
- Tests never call the real OANDA API. Use fixed candle data or the `FakeBroker`.
- Never delete, weaken, or rewrite a test just because the code fails it. Only change a test when its requirement changed.

**A failing test is different from a failing tool.** When a tool crashes, fix it (section 5). When a test fails, do not auto-fix the code. Reason from **requirement → test → code**, explain where the problem likely is, and let Daniel decide.

---

## 10. Design Docs and Evolution Records

- Design docs in `docs/design/` show what is **actually implemented**, not future plans. The exception is Phase 01: before any code exists, design-only diagrams based on `docs/design/requirements.md` are allowed.
- Do not invent classes, methods, or relationships in diagrams.
- Use UML visibility: `+` public, `-` private, `#` protected.
- Each phase gets a record in `docs/evolution/phase-NN.md` describing only what actually happened, based on Git history.
- If requirements, code, and diagrams disagree, report it instead of picking a winner.

---

## 11. Git Rules

**Branches and tags**
- Each phase starts on its own branch: `git switch -c phase-NN`
- Finished work merges into `main` through a pull request.
- After the merge, tag `main` with `phase-NN-completed`.

**Before any commit, tag, or push**
- Check `git status`, the diff, and the current branch.
- Make sure no secrets, `.env`, `.tmp/`, build output, or unrelated files are included.
- Make sure the tag doesn't already exist.

**Never**
- `git add .` or `git add -A` (stage exact files only)
- force push, rewrite history, reset, or amend without permission
- delete or move existing tags
- push directly to `main`

---

## 12. File Structure

- **Deliverables** (reports, trade journals, backtest results Daniel needs to see) go to cloud services (Google Sheets, email, the mobile app) where he can access them.
- **Intermediates** go in `.tmp/` and can be regenerated.

```
.tmp/            # temporary files (candle dumps, intermediate exports), disposable
docs/            # requirements, design, evolution records
tools/           # Python scripts for deterministic execution
workflows/       # Markdown SOPs, one per pipeline stage
tests/           # pytest suite
frontend/        # React Native (Expo) app
.env             # API keys (never store secrets anywhere else)
credentials.json, token.json   # Google OAuth (gitignored)
```

---

## 13. When Unsure

If information is missing or files disagree, do not guess. Report:

1. what doesn't match
2. which files are involved
3. what decision Daniel needs to make

---

## Bottom Line

You sit between what Daniel wants (workflows) and what actually gets done (tools). Read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system, while leaving the engineering decisions to Daniel.

Stay pragmatic. Stay reliable. Keep learning.
