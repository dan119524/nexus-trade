# Phase 06 · Growing the Object Model

## Before You Start

- Phase 05 is merged and tagged `phase-05-completed`.
- Local `main` is synced with GitHub and clean.
- The demo runs and `pytest` shows no new test failures.
- Review your entities, relationships, multiplicities, hierarchies, and interfaces. Note any design limitations and any one-to-many relationships that are still single references.

---

## 1 · Start

1. From a clean, synced `main`, create and switch to `phase-06`.
2. Save this file as `phases/phase-06-growing-the-object-model.md`.
3. Send Claude Code:

> Phase 06 start check. Confirm: `phase-05-completed` exists on the remote and points to a commit on `main`; the current branch is `phase-06` and starts from `phase-05-completed`; the working tree is clean; `pytest` shows no new test failures. Report PHASE-05 COMPLETION: VERIFIED and PHASE-06 START CHECK: PASS, or BLOCKED with the reason. Do not modify anything.

Don't continue until it reports **PHASE-06 START CHECK: PASS**.

---

## 2 · Grow the Object Model

**AI ALLOWED** — Claude Code can suggest options and write the code. You make the final decisions, review every change, and must be able to explain every line.

### Task 1: Composition vs. Inheritance

Find **one** place in `tools/models/` where a changing requirement would make the current design hard to maintain (for example, a subclass that exists only to change one behavior).

Refactor it using **composition**, **delegation**, or **interface-based polymorphism**, whichever fits best. Existing behavior must still work.

Write two or three sentences in `docs/design/requirements.md` explaining the limitation and why your change improves it.

### Task 2: Collections

Pick **one** real one-to-many relationship (for example, a chart and its candles) and implement it with a typed collection: `list[T]`, `set[T]`, or `dict[K, V]`.

- Store it privately (`self._candles: list[Candle] = []`).
- Add meaningful methods to **add** and to **get or remove** items. Validate what gets added.
- Don't expose the internal list directly. Return a copy or a tuple.

If you already used a typed collection correctly in an earlier phase, you don't need another one here.

### Demo

Update `tools/models/demo.py` to show both changes. The collection must hold at least two objects.

```bash
python -m tools.models.demo
pytest
```

---

## 3 · V1 Checkpoint

Send Claude Code:

> Phase 06 v1 check, read-only. Confirm: one design limitation was refactored using composition, delegation, or interface-based polymorphism, and requirements.md explains it; existing behavior is preserved; one one-to-many relationship uses a typed `list`, `set`, or `dict`, stored privately with validated add and get/remove methods, and not exposed directly; `demo.py` shows both, with at least two objects in the collection; the demo runs and `pytest` shows no new test failures. Report PHASE-06 V1: READY or BLOCKED with the reason. Do not modify anything.

If **BLOCKED**, fix it (Claude Code can help) and run the check again. Once it reports **PHASE-06 V1: READY**:

1. Stage and commit your work.
2. Push `phase-06`.
3. Create the annotated tag `phase-06-v1`.
4. Push the tag.
5. Run `git status`. It must be clean.

---

## 4 · Domain-Wide Object Model Review

Now review the **entire** domain with Claude Code. Claude Code acts as a senior engineer: it recommends, explains alternatives, and implements your decisions. You're the engineer with final say.

Send Claude Code:

> Phase 06 object model collaboration. Read AGENTS.md, this phase file, requirements.md, the `.puml` files, `tools/models/`, and `tests/models/`. Review the entire domain and recommend changes for: one-to-many relationships still stored as single references; inheritance that would work better as composition, delegation, or an interface; placeholder or demo-only methods that should have real behavior based on existing requirements. Explain each recommendation and its consequences. You may challenge my reasoning, but don't block a decision I justify. Do not write code until I decide.

Decide on each recommendation with a reason. Then send:

> Implement my decisions. Preserve valid inheritance, interfaces, polymorphism, and existing behavior. Keep existing exception behavior. Update requirements.md, `crc.puml`, `domain-model.puml`, and `docs/evolution/phase-06.md`. Extend `demo.py` and the pytest suite, and run all tests. Report PHASE-06 OBJECT MODEL: COMPLETE only when the demo runs, `pytest` shows no new test failures, and docs match the code.

Rules:

- Changes must be justified. No extra classes, interfaces, or collections just to add work.
- **Don't edit `.puml` files by hand.**
- No design patterns, databases, persistence, service layers, or restructuring. Those come later.
- Don't change pipeline tools outside `tools/models/`.

Don't continue until it reports **PHASE-06 OBJECT MODEL: COMPLETE**. Check every changed diagram in PyCharm yourself.

---

## 5 · Final Review and Check

Send Claude Code:

> Run the Phase 06 final review and check. Do one light review and list important recommendations, marked advisory. Then report PASS or FAIL with evidence for each: remaining one-to-many relationships use typed collections with proper add/get/remove methods; inheritance decisions were evaluated and improved where justified; placeholder behavior was replaced where requirements support it; Phase 03–05 work is preserved; requirements, CRC, and domain model match the code; `pytest` shows no new test failures; `docs/evolution/phase-06.md` exists; `phase-06-v1` exists; no patterns, persistence, or service layers were added; no files outside `tools/models/`, `tests/`, `docs/`, and `phases/` changed; no secrets in the diff. Report PHASE-06: PASSED or FAILED. Only block on required objectives, build or test failures, or AGENTS.md rules, not on advisory recommendations I decline with a reason.

Decide on each recommendation yourself. Continue until it reports **PHASE-06: PASSED**.

---

## 6 · Merge and Tag

1. Change Phase 06's ⬜ to ✅ in the README.
2. Stage only the intended files and inspect the staged diff.
3. Commit: `Complete Phase 06 growing the object model`
4. Push `phase-06`.
5. Open a PR from `phase-06` into `main` and merge it.
6. Sync local `main`.
7. Create and push the annotated tag `phase-06-completed`.
8. Run `git status` on `main`. It must be clean.

**Phase 06 is complete when** `phase-06-v1` and `phase-06-completed` both exist on GitHub and `main` is clean. Phase 07 can't start without `phase-06-completed`.
