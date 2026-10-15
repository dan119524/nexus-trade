# Phase 02 · From Design to Objects

## Before You Start

- Phase 01 must be merged and tagged `phase-01-completed`.
- `.venv` is active and `pytest` runs.
- Keep `docs/design/requirements.md` and `domain-model.puml` open as your reference.

---

## 1 · Start

1. Sync `main` with GitHub, then create and switch to `phase-02`.
2. Save this file as `phases/phase-02-design-to-objects.md`.

---

## 2 · Implement the Object Model

**AI ALLOWED** — Claude Code can suggest options and write the code. You make the final decisions, review every change, and must be able to explain every line.

Using the design from Phase 01:

- Create one Python class per domain entity in `tools/models/` (one file per class, plus an `__init__.py`).
- Give each class only the state its requirements call for.
- **Valid construction:** `__init__` checks its inputs and raises `ValueError` on bad data (for example, a candle whose `high` is below its `low`).
- **Encapsulation:** store attributes with a leading underscore (`self._high`) and expose them with `@property`. Only add a setter when a requirement says the value can change.
- Add only behavior an object can do **with its own data** (for example, `candle.is_bullish()`). **No collaboration between objects yet.** That's Phase 03.
- Create `tools/models/demo.py` that creates your objects and calls their methods, including one invalid object inside a `try/except` to show validation works.

Run it:

```bash
python -m tools.models.demo
pytest
```

The demo must run and every existing test must still pass.

Use only concepts from Phase 02 and earlier: no inheritance, interfaces, patterns, or changes to existing tools.

---

## 3 · V1 Checkpoint

**AI ALLOWED** — Claude Code can run these steps. Review `git diff --staged` before it commits.

- Commit and push your work to `phase-02`.
- Create and push the annotated tag `phase-02-v1`.

Stay on `phase-02`. Don't continue until the v1 tag is pushed.

---

## 4 · Engineering Review

Send Claude Code:

> Run a Phase 02 engineering review. Read AGENTS.md, this phase file, `docs/design/requirements.md`, `docs/design/uml/domain-model.puml`, and every file in `tools/models/`. Check: each Phase 01 entity has one class; state matches the requirements; `__init__` rejects invalid data; attributes are encapsulated with `_name` and `@property`; setters exist only where a requirement allows change; methods only use the object's own data; there's no collaboration between objects; no inheritance, interfaces, or patterns; `demo.py` exercises every class including one invalid case; nothing in other `tools/` folders changed. Number each finding with evidence, and separate real problems from optional ideas. Do not modify any files.

Answer each finding in the chat:

- **ACCEPT** — adopt it, with your reason
- **MODIFY** — fix it differently, with your reason
- **REJECT** — keep your decision, with your reason
- **DEFER** — postpone it within this phase's scope, with your reason

When every finding has a decision, send:

> Apply only the findings I marked ACCEPT or MODIFY, exactly as I decided. Change nothing else. Then list each finding with its final decision and report: Engineering Review: RESOLVED.

Continue until it reports **Engineering Review: RESOLVED**.

---

## 5 · Save the Reviewed State

**AI ALLOWED** — Claude Code can run these steps. Review `git diff --staged` before it commits.

```bash
python -m tools.models.demo
pytest
```

Both must succeed. Then commit and push the reviewed state to `phase-02`.

---

## 6 · Sync the Project

Send Claude Code:

> Sync the project for Phase 02. Compare `tools/models/` with `docs/design/requirements.md` and the three `.puml` files. Update `domain-model.puml` to show the attributes and public methods actually implemented, using + and - visibility. Update `crc.puml` only if responsibilities changed. Leave `use-cases.puml` alone unless an actor goal changed. If requirements and code disagree, report it instead of choosing. List every change you make.

Inspect every change. Reject anything incorrect and ask for a revision. Open each changed diagram in PyCharm and check it yourself.

---

## 7 · Test the Phase

Send Claude Code:

> Write pytest tests for Phase 02 in `tests/models/`. For each class in `tools/models/`, test: valid construction stores the right values; each invalid input raises `ValueError`; each behavior method returns the correct result. Test observable behavior only. Don't touch existing tests. Don't call the OANDA API. Then run `pytest` and report the results. If a test fails, do not change the code; explain the likely cause using requirement → test → code.

Run the full suite yourself:

```bash
pytest
```

Don't continue until every test passes. If a fix changes a design decision, update the requirements and diagrams too, then test again.

---

## 8 · Record the Evolution

Send Claude Code:

> Write `docs/evolution/phase-02.md` describing how the Phase 01 design became Python classes, what the engineering review found and what I decided, what changed during sync, and what tests were added. Use only Git history and repo evidence.

Read it and confirm it's accurate. After you've personally checked the diagrams, add:

```markdown
## Verification Confirmation
I personally inspected all affected PlantUML diagrams in PyCharm and confirmed they match my approved Phase 02 decisions.
```

---

## 9 · Final Check

Run one last time:

```bash
python -m tools.models.demo
pytest
```

Send Claude Code:

> Run the Phase 02 check. Report PASS or FAIL with evidence for each: one class per Phase 01 entity exists in `tools/models/`; constructors validate input; attributes are encapsulated; no collaboration, inheritance, interfaces, or patterns; `demo.py` runs; `tests/models/` exists and all of `pytest` passes; `domain-model.puml` matches the code; `docs/evolution/phase-02.md` exists with a Verification Confirmation; `phase-02-v1` tag exists; no other `tools/` files changed; no secrets in the diff. Do not fix anything.

Don't continue until every item is **PASS**.

---

## 10 · Merge and Tag

You decide whether Phase 02 is ready.

1. Stage only the intended files and inspect the staged diff.
2. Commit: `Complete Phase 02 design to objects`
3. Push `phase-02`.
4. Open a PR from `phase-02` into `main` and merge it.
5. Sync local `main`.
6. Create and push the annotated tag `phase-02-completed`.
7. Change Phase 02's ⬜ to ✅ in the README.

**Phase 02 is complete when** the work is merged on `main`, local `main` matches, and `phase-02-completed` points to the merged commit.
