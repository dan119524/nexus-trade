# Phase 09 · Adapter and Facade

## Before You Start

- Phase 08 is merged and tagged `phase-08-completed`.
- Local `main` is synced with GitHub and clean.
- `python -m tools.models.demo` runs and `pytest` shows no new test failures.
- Read Module 10.
- Review where Nexus meets formats that are not its own (OANDA responses, the pipeline's dicts) and where callers coordinate several objects to do one thing.
- Reread `docs/evolution/phase-08.md`, "Notes for Later Phases". Switching `build_trade_plan` to `TradePlanBuilder` was planned for this phase, and it needs the pipeline dicts turned into domain objects.

Phase 09 uses only concepts through Module 10. No persistence, databases, dependency injection, MVC, layers, or broad restructuring. No real OANDA calls in tests.

---

## 1 · Start

1. From a clean, synced `main`, create and switch to `workshop-09`.
2. Save this file as `phases/phase-09-adapter-and-facade.md`.
3. Copy `workshops/workshop-09-adapter-and-facade.md` from `course-content` into this repository's `workshops/` folder, and add the contents of `workshops/prompts/workshop-09-prompts.md` to the end of `agents/PROMPTS.md`. Don't change earlier prompts.
4. Send Claude:

> Phase 09 start check, read-only. Confirm: `AGENTS.md` is unchanged from `origin/main`; `phase-08-completed` exists on the remote and points to a commit on `main`; the current branch is `workshop-09` and contains `phase-08-completed`; the Phase 09 guide, the copied workshop file, and the `agents/PROMPTS.md` additions are present (these are expected additions); the working tree has no other changes; `pytest` shows no new test failures. If GitHub can't be reached, report NOT VERIFIED, not BLOCKED. Report WORKSHOP-08 COMPLETION: VERIFIED and WORKSHOP-09 START CHECK: PASS, or BLOCKED with the first failed requirement. Do not modify anything.

Don't continue until it reports **WORKSHOP-09 START CHECK: PASS**.

---

## 2 · Apply Adapter or Facade

**AI ALLOWED.** Nexus is a personal project. It is not submitted or graded, and only borrows the workshop's steps. Claude can write the code. You make the decisions (the problem, the pattern, and the boundary), review every change, and must be able to explain every line.

The workshop's "STUDENT OWNED, no AI" rule for this section applies to the graded CSC 413 semester application, Tirgum, not to Nexus.

1. Describe one structural problem in your own words, based on the current code.
2. Choose Adapter or Facade, and say why the other one fits less well.
3. Implement it.
4. Update `tools/models/demo.py` (Nexus's `Main.java`) to show it, with a comment right above the demonstration: why this pattern, how it solves the problem, and why not the other one.
5. Run it:

```bash
python -m tools.models.demo
pytest
```

Rules:

- Apply only one pattern for V1.
- Preserve existing behavior. No new features, no real OANDA calls.
- Don't change trading rules: R:R ≥ 2, the 2% risk cap, and practice-only stay as they are (`AGENTS.md` section 3).

---

## 3 · V1 Checkpoint

Send Claude:

> Phase 09 V1 check, read-only. Compare against `phase-08-completed`, including staged and unstaged changes. Confirm: one meaningful structural problem was identified; one Adapter or Facade reasonably addresses it (a Facade must simplify, not just rename); `demo.py` shows it, with the comment above the demonstration; the demo runs; `pytest` shows no new test failures. Don't require both patterns, docs, diagrams, or extra tests. Report WORKSHOP-09-V1: READY FOR INSTRUCTOR REVIEW or BLOCKED with the first clear blocker. Do not modify anything, commit, push, or tag.

Once it reports **READY**:

1. Stage and commit your V1 work.
2. Push `workshop-09`.
3. Create the annotated tag `workshop-09-v1-completed`.
4. Push the tag.
5. Run `git status`. It must be clean.

---

## 4 · Structural Design Collaboration

**AI ALLOWED.** Claude acts as a senior engineer: it recommends, explains alternatives, and implements your decisions. You're the engineer with final say.

Send Claude:

> Phase 09 structural design collaboration. Confirm `workshop-09-v1-completed` exists on the remote, then don't re-review V1. Read AGENTS.md, this phase file, requirements.md, `docs/evolution/phase-08.md`, the `.puml` files, `tools/`, and `tests/`. Review the whole application: where Nexus uses formats, terminology, or data shapes that differ from its own model, and where callers coordinate the same subsystem in the same way. For each recommendation, give the problem, the affected classes, the pattern or alternative, the improvement, and the tradeoffs. Don't invent problems to justify a pattern. Do not write code until I decide.

Decide on each recommendation with a reason. Then send:

> Implement my decisions. Preserve behavior and earlier phases' design. Update requirements.md (no new FRs just because structure moved), the CRC analysis, `crc.puml`, `domain-model.puml`, and `docs/evolution/phase-09.md`. Add or update tests only for the approved changes, following AGENTS.md section 9. Run all tests. Report WORKSHOP-09 DESIGN COLLABORATION: COMPLETE only when the demo runs, `pytest` shows no new test failures, and docs match the code.

Rules:

- Changes must be justified. Don't force both patterns.
- **Don't edit `.puml` files by hand.** Check every changed diagram in IntelliJ yourself.
- No other patterns, persistence, dependency injection, MVC, layers, or broad restructuring.

---

## 5 · Final Review and Check

Send Claude:

> Run the Phase 09 final review and check. Do one light review and list at most four important recommendations, marked advisory. Then report PASS or FAIL with evidence for each: the V1 pattern is still present and addresses a real structural problem; Adapter and Facade were both evaluated and my decisions have reasons; behavior and earlier phases' work are preserved; requirements, CRC, and domain model match the code; `pytest` shows no new test failures; `docs/evolution/phase-09.md` exists; `workshop-09-v1-completed` exists; no concepts beyond Module 10; no secrets in the diff. Report WORKSHOP-09: PASSED or BLOCKED. Only block on required objectives, test failures, or AGENTS.md rules, not on advisory recommendations I decline with a reason.

---

## 6 · Merge and Tag

1. Change Phase 09's ⬜ to ✅ in the README.
2. Stage only the intended files and inspect the staged diff.
3. Commit: `Complete Phase 09 adapter and facade`
4. Push `workshop-09`.
5. Open a PR from `workshop-09` into `main` and merge it.
6. Sync local `main`.
7. Create and push the annotated tag `workshop-09-completed`.
8. Run `git status` on `main`. It must be clean.

**Phase 09 is complete when** `workshop-09-v1-completed` and `workshop-09-completed` both exist on GitHub and `main` is clean. Phase 10 can't start without `workshop-09-completed`.
