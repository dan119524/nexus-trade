# Phase 04 · Inheritance

## Before You Start

- Phase 03 is merged and tagged `phase-03-completed`.
- Local `main` is synced with GitHub and clean.
- The demo runs and `pytest` shows no new test failures.
- Review your requirements, classes, CRC cards, and domain model. Look for objects that share state and behavior but differ in specific ways.

---

## 1 · Start

1. From a clean, synced `main`, create and switch to `phase-04`.
2. Save this file as `phases/phase-04-inheritance.md`.
3. Send Claude Code:

> Phase 04 start check. Confirm: `phase-03-completed` exists on the remote and points to a commit on `main`; `phase-03-v1` exists; the current branch is `phase-04` and starts from `phase-03-completed`; the working tree is clean; `pytest` shows no new test failures. Report PHASE-04 START CHECK: PASS or BLOCKED with the reason. Do not modify anything.

Don't continue until it reports **PHASE-04 START CHECK: PASS**.

---

## 2 · Introduce Inheritance

**AI ALLOWED** — Claude Code can suggest options and write the code. You make the final decisions, review every change, and must be able to explain every line.

Using your requirements and domain model:

1. Identify **one** meaningful superclass your domain supports.
2. Create **at least two** subclasses that extend it.
3. Move only the state and behavior that truly belong to the general class into the superclass.
4. In each subclass `__init__`, call `super().__init__(...)` to set the shared state.
5. Add subclass-specific state or behavior where the domain needs it.
6. Override inherited methods where a subclass needs different behavior.
7. Update `tools/models/demo.py` to create each subclass and call both inherited and overridden methods.
8. Run:

```bash
python -m tools.models.demo
pytest
```

Every subclass must pass the **is-a** test: "a `<Subclass>` is a `<Superclass>`" must be true in the trading domain.

Keep the Phase 03 relationships working. No interfaces, abstract base classes, collections for relationships, or patterns yet. Don't change anything outside `tools/models/`, `tests/models/`, `docs/`, and `phases/`.

---

## 3 · V1 Checkpoint

Send Claude Code:

> Phase 04 v1 check, read-only. Confirm: one superclass exists with at least two subclasses in `tools/models/`; each subclass calls `super().__init__`; shared state lives only in the superclass; at least one method is overridden with different behavior; each subclass passes the is-a test for the trading domain; Phase 03 relationships still work; no abstract base classes, interfaces, collections for relationships, or patterns; `demo.py` exercises the hierarchy; the demo runs and `pytest` shows no new test failures. Report PHASE-04 V1: READY or BLOCKED with the reason. Do not modify anything.

If **BLOCKED**, fix it (Claude Code can help) and run the check again. Once it reports **PHASE-04 V1: READY**:

1. Stage and commit your work.
2. Push `phase-04`.
3. Create the annotated tag `phase-04-v1`.
4. Push the tag.
5. Run `git status`. It must be clean.

---

## 4 · Engineering Review

Send Claude Code:

> Run a Phase 04 engineering review. Read AGENTS.md, this phase file, `docs/design/requirements.md`, the `.puml` files, `tools/models/`, and `tests/models/`. Check that each inheritance relationship is a genuine is-a, that nothing subclass-specific was pushed into the superclass, that overrides are meaningful, and that nothing beyond Phase 04 scope was added. Number each finding with evidence. Do not modify files yet.

Answer each finding with **ACCEPT** or **REJECT** plus your engineering reason. Then send:

> Apply only the findings I accepted. Update requirements.md to record the inheritance decision. Sync `domain-model.puml` (generalization arrows, no duplicated inherited members in subclasses) and `crc.puml` (don't list the superclass as a collaborator). Add pytest tests in `tests/models/` for inherited, specialized, and overridden behavior, and run `pytest`. Update `docs/evolution/phase-04.md` from Git history and repo evidence. Report PHASE-04: PASSED only when the demo runs, `pytest` shows no new test failures, and the docs match the code.

Continue until it reports **PHASE-04: PASSED**. Open the changed diagrams in PyCharm and check them yourself.

---

## 5 · Final Check

Send Claude Code:

> Run the Phase 04 check. Report PASS or FAIL with evidence for each: the hierarchy exists and passes the is-a test; `super().__init__` is used; at least one meaningful override; Phase 03 relationships preserved; diagrams and requirements match the code; `tests/models/` covers the hierarchy and `pytest` shows no new test failures; `docs/evolution/phase-04.md` exists; `phase-04-v1` exists; no files outside `tools/models/`, `tests/`, `docs/`, and `phases/` changed; no secrets in the diff. Report PHASE-04 CHECK: PASS or FAIL. Do not fix anything.

If it reports **FAIL**, fix the issue and run it again.

---

## 6 · Merge and Tag

1. Change Phase 04's ⬜ to ✅ in the README.
2. Stage only the intended files and inspect the staged diff.
3. Commit: `Complete Phase 04 inheritance`
4. Push `phase-04`.
5. Open a PR from `phase-04` into `main` and merge it.
6. Sync local `main`.
7. Create and push the annotated tag `phase-04-completed`.
8. Run `git status` on `main`. It must be clean.

**Phase 04 is complete when** `phase-04-v1` and `phase-04-completed` both exist on GitHub and `main` is clean.
