# Phase 08 · Factory and Builder

## Before You Start

- Phase 07 is merged and tagged `phase-07-completed`.
- Local `main` is synced with GitHub and clean.
- `python -m tools.models.demo` runs and `pytest` shows no new test failures.
- Read Module 09.
- Review how objects are created across Nexus, in `tools/models/` and in the pipeline tools that build plans. Note any Factory and Builder opportunities.
- Reread `docs/design/phase-07-review.md`. Row 1 (`build_trade_plan`) is planned for this phase as `TradePlanBuilder`.

Phase 08 uses only concepts through Module 09. No Adapter, Facade, persistence, dependency injection, MVC, or layers. Those come later.

---

## 1 · Start

1. From a clean, synced `main`, create and switch to `workshop-08`.
2. Save this file as `phases/phase-08-factory-and-builder.md`.
3. Copy `workshops/workshop-08-factory-and-builder.md` and `workshops/prompts/workshop-08-prompts.md` from `course-content` into this repository's `workshops/` folder.
4. Send Claude Code:

> Phase 08 start check, read-only. Confirm: `AGENTS.md` is unchanged from `origin/main`; `phase-07-completed` exists on the remote and points to a commit on `main`; the current branch is `workshop-08` and contains `phase-07-completed`; the Phase 08 guide and the copied workshop files are present (these are expected additions, not unauthorized changes); the working tree has no other changes; `pytest` shows no new test failures. If GitHub can't be reached, report NOT VERIFIED, not BLOCKED. Report PHASE-07 COMPLETION: VERIFIED and PHASE-08 START CHECK: PASS, or BLOCKED with the first failed requirement. Do not modify anything.

Don't continue until it reports **PHASE-08 START CHECK: PASS**.

---

## 2 · Apply the Builder

**AI ALLOWED** — Nexus is a personal project. It is not submitted or graded, and only borrows the workshop's steps. Claude Code can write the code. You make the decisions (the problem, the pattern, and the responsibility), review every change, and must be able to explain every line.

The workshop's "STUDENT OWNED, no AI" rule for this section applies to the graded CSC 413 semester application, Tirgum (`csc413-fall26-05-dan119524`), not to Nexus.

Your Builder target is `TradePlanBuilder`. Phase 07 review row 1 found that `tools/trade_plan/build_trade_plan.py` mixes orchestration, file I/O, an OANDA call, and the trade plan rules, and that it never builds the existing `TradePlan` class.

1. Describe the object-creation problem in your own words, based on the current code.
2. Decide what `TradePlanBuilder` is responsible for and where it belongs. Justify the choice.
3. Implement it yourself.
4. Update `tools/models/demo.py` to show the improvement.
5. Run it:

```bash
python -m tools.models.demo
pytest
```

Rules:

- Apply only one pattern for V1.
- Preserve existing behavior. No new features.
- Don't change trading rules: R:R ≥ 2, the 2% risk cap, and practice-only stay as they are (`AGENTS.md` section 3).
- Be ready to explain the original problem, your decisions, and the improvement.

---

## 3 · V1 Checkpoint

Send Claude Code:

> Phase 08 V1 check, read-only. Compare against `phase-07-completed`, including staged and unstaged changes. Confirm: one meaningful object-creation problem supported by the existing code was identified; one Builder (or Factory) was applied that actually demonstrates the pattern rather than renaming a class or method; it reasonably addresses the problem; `demo.py` shows the affected behavior still works; the demo runs; `pytest` shows no new test failures. Don't require a fluent interface, a specific class structure, both patterns, doc or diagram updates, or extra tests. Don't review unrelated areas. Report PHASE-08 V1: READY or BLOCKED with the first clear blocker. Do not modify anything, commit, push, or tag.

If **BLOCKED**, fix it (Claude Code can help) and run the check again. Once it reports **PHASE-08 V1: READY**:

1. Stage and commit your V1 work.
2. Push `workshop-08`.
3. Create the annotated tag `phase-08-v1`.
4. Push the tag.
5. Run `git status`. It must be clean.

If you complete V1 in class, show the instructor or TA the V1 message, explain your Builder, and show `phase-08-v1` on GitHub and a clean `git status`.

If you don't reach V1 in class, commit and push your current work, then create and push the annotated tag `phase-08-in-progress`. Don't create it if `phase-08-v1` already exists.

---

## 4 · Object Creation Collaboration

**AI ALLOWED.** Claude Code acts as a senior engineer: it recommends, explains alternatives, and implements your decisions. You're the engineer with final say.

Send Claude Code:

> Phase 08 object creation collaboration. Confirm `phase-08-v1` exists on the remote, then don't re-review V1. Read AGENTS.md, this phase file, requirements.md, `docs/design/phase-07-review.md`, the `.puml` files, `tools/models/`, `tools/trade_plan/`, and `tests/`. Review object creation across Nexus: callers that choose among concrete types, repeated construction decisions, creation conditionals spread across callers, constructors with hard combinations of values, construction sequences that are easy to get wrong, creation logic in the wrong place, and places where direct construction should stay. For each recommendation, give the problem, the affected classes, why it's a problem, the proposed change, and the tradeoffs. Don't invent problems or create artificial concrete types to justify a Factory. Do not write code until I decide.

Where a Factory might fit (suggestions to evaluate, not decisions):

- **Trade direction.** `Signal.trade_direction()` chooses `BuyDirection` or `SellDirection` from a vote. `calculate_sl_tp` still branches on `bullish`/`bearish` itself (Phase 07 review row 2). A small factory for `TradeDirection` could give both one place to make that choice.
- **`OrderFactory`.** It's named in the README roadmap. Today `Order` has only one type (market), so check whether a Factory solves a real creation problem before adding one.

Decide on each recommendation with a reason. Then send:

> Implement my decisions. Preserve valid relationships, inheritance, interfaces, polymorphism, collections, composition, exception behavior, and direct construction where it's clearer. Update requirements.md (no new FRs just because creation moved), the CRC analysis, `crc.puml`, `domain-model.puml`, and `docs/evolution/phase-08.md`. Add or update tests only for the approved changes, following AGENTS.md section 9 (no real OANDA calls). Run all tests. Report PHASE-08 OBJECT CREATION: COMPLETE only when the demo runs, `pytest` shows no new test failures, and docs match the code.

Rules:

- Changes must be justified. Not every constructor needs a pattern.
- **Don't edit `.puml` files by hand.**
- No Adapter or Facade (Phase 09), no broad restructuring (Phase 10).

Don't continue until it reports **PHASE-08 OBJECT CREATION: COMPLETE**. Check every changed diagram in PyCharm yourself.

---

## 5 · Final Review and Check

Send Claude Code:

> Run the Phase 08 final review and check. Do one light review and list at most four important recommendations, marked advisory. Then report PASS or FAIL with evidence for each: the V1 Builder is still present and addresses a real creation problem; object creation across Nexus was reviewed and my decisions have reasons; justified Factory or Builder changes were made and direct construction kept where appropriate; behavior and Phase 03–07 work are preserved; requirements, CRC, and domain model match the code; `pytest` shows no new test failures; `docs/evolution/phase-08.md` exists; `phase-08-v1` exists; no concepts beyond Module 09; no secrets in the diff. Report PHASE-08: PASSED or FAILED. Only block on required objectives, test failures, or AGENTS.md rules, not on advisory recommendations I decline with a reason.

Decide on each recommendation yourself. Continue until it reports **PHASE-08: PASSED**.

---

## 6 · Merge and Tag

1. Change Phase 08's ⬜ to ✅ in the README.
2. Stage only the intended files and inspect the staged diff.
3. Commit: `Complete Phase 08 factory and builder`
4. Push `workshop-08`.
5. Open a PR from `workshop-08` into `main` and merge it.
6. Sync local `main`.
7. Create and push the annotated tag `phase-08-completed`.
8. Run `git status` on `main`. It must be clean.

**Phase 08 is complete when** `phase-08-v1` and `phase-08-completed` both exist on GitHub and `main` is clean. Phase 09 can't start without `phase-08-completed`.
