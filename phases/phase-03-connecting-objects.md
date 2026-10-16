# Phase 03 · Connecting Objects

## Before You Start

- Phase 02 is merged and tagged `phase-02-completed`.
- Local `main` is synced with GitHub and clean.
- `python -m tools.models.demo` runs and `pytest` shows no new test failures.
- Review your Phase 02 classes and CRC cards. The CRC collaborators tell you which objects need to connect.

---

## 1 · Start

1. From a clean, synced `main`, create and switch to `phase-03`.
2. Save this file as `phases/phase-03-connecting-objects.md`.
3. Send Claude Code:

> Phase 03 start check. Confirm: `phase-02-completed` exists on the remote and points to a commit on `main`; the current branch is `phase-03` and it starts from that commit; the working tree is clean; `pytest` shows no new test failures. Report PHASE-03 START CHECK: PASS or BLOCKED with the reason. Do not modify anything.

Don't continue until it reports **PHASE-03 START CHECK: PASS**.

---

## 2 · Connect Your Objects

**AI ALLOWED** — Claude Code can suggest options and write the code. You make the final decisions, review every change, and must be able to explain every line.

Using your Phase 02 classes and CRC analysis:

1. Identify the relationships your objects need (for example, a trade needs to know its instrument).
2. Classify each one as **association**, **aggregation**, or **composition**, and write that classification in `docs/design/requirements.md` under Relationships and Multiplicities.
3. Implement each relationship with an object reference (for example, `self._instrument = instrument`). Validate that the object passed in is the right type.
4. Update `tools/models/demo.py` to build connected objects and show one object using another.
5. Run:

```bash
python -m tools.models.demo
pytest
```

**No lists, dicts, or sets for relationships yet.** If a relationship is one-to-many, connect a single object, or record the relationship as deferred in requirements.md. Collections come in Phase 06.

No inheritance, interfaces, or patterns. Don't change anything outside `tools/models/`, `tests/models/`, `docs/`, and `phases/`.

---

## 3 · V1 Checkpoint

Send Claude Code:

> Phase 03 v1 check, read-only. Confirm: requirements.md classifies each relationship as association, aggregation, or composition; each classified relationship is implemented as an object reference in `tools/models/`, or recorded in requirements.md as deferred to a later phase; no lists, dicts, or sets are used for relationships; no inheritance, interfaces, or patterns; `demo.py` shows connected objects; the demo runs and `pytest` shows no new test failures; nothing outside `tools/models/`, `tests/models/`, `docs/`, and `phases/` changed. Report PHASE-03 V1: READY or BLOCKED with the reason. Do not modify anything.

If **BLOCKED**, fix it (Claude Code can help) and run the check again. Once it reports **PHASE-03 V1: READY**:

1. Stage and commit your work.
2. Push `phase-03`.
3. Create the annotated tag `phase-03-v1`.
4. Push the tag.

---

## 4 · Engineering Review

Send Claude Code:

> Run a Phase 03 engineering review. Read AGENTS.md, this phase file, `docs/design/requirements.md`, the `.puml` files, `tools/models/`, and `tests/models/`. Check that each relationship is correctly classified, that composition is used only where the part can't exist without the whole, that references are validated, and that nothing beyond Phase 03 scope was added. Number each finding with evidence. Do not modify files yet.

Answer each finding with **ACCEPT** or **REJECT** plus your engineering reason. Then send:

> Apply only the findings I accepted. Then sync `domain-model.puml` and `crc.puml` with the code and requirements, add pytest tests in `tests/models/` for the new relationships, and run `pytest`. Update `docs/evolution/phase-03.md` from Git history and repo evidence. Report PHASE-03: PASSED only when the demo runs, `pytest` shows no new test failures, and the docs match the code.

Continue until it reports **PHASE-03: PASSED**. Open the changed diagrams in PyCharm and check them yourself.

---

## 5 · Merge and Tag

1. Change Phase 03's ⬜ to ✅ in the README.
2. Stage only the intended files and inspect the staged diff.
3. Commit: `Complete Phase 03 connecting objects`
4. Push `phase-03`.
5. Open a PR from `phase-03` into `main` and merge it.
6. Sync local `main`.
7. Create and push the annotated tag `phase-03-completed`.
8. Run `git status` on `main`. It must be clean.

**Phase 03 is complete when** `phase-03-v1` and `phase-03-completed` both exist on GitHub and `main` is clean.
