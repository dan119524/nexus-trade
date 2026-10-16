# Phase 05 · Polymorphism, Interfaces, and Domain Expansion

## Before You Start

- Phase 04 is merged and tagged `phase-04-completed`, and `phase-04-v1` exists on GitHub.
- Local `main` is synced with GitHub and clean.
- The demo runs and `pytest` shows no new test failures.
- Review your requirements, classes, CRC cards, domain model, relationships, and inheritance hierarchy.

This is the big checkpoint for NEXUS. After you build the interface yourself, you'll grow the domain to cover the whole trading pipeline. **Start early.**

---

## 1 · Start

1. From a clean, synced `main`, create and switch to `phase-05`.
2. Save this file as `phases/phase-05-polymorphism-interfaces.md`.
3. Send Claude Code:

> Phase 05 start check. Confirm: `phase-04-completed` exists on the remote and points to a commit on `main`; `phase-04-v1` exists on the remote; the current branch is `phase-05` and starts from `phase-04-completed`; the working tree is clean; `pytest` shows no new test failures. Report PHASE-04 V1 TAG: VERIFIED and PHASE-05 START CHECK: PASS, or BLOCKED with the reason. Do not modify anything.

Don't continue until it reports **PHASE-05 START CHECK: PASS**.

---

## 2 · Introduce an Interface and Polymorphism

**AI ALLOWED** — Claude Code can suggest options and write the code. You make the final decisions, review every change, and must be able to explain every line.

Using your requirements and domain model:

1. Identify **one** meaningful capability in NEXUS that different objects perform in different ways (for example, detecting a setup).
2. Create one interface for it as an abstract base class: `from abc import ABC, abstractmethod`, with the required method marked `@abstractmethod`.
3. Implement the interface in **at least two** classes, each with its own real behavior.
4. Write a function or method that takes the **interface type** as its parameter (use a type hint) and works with any implementation.
5. Show in `tools/models/demo.py` that different implementations run through that same function.
6. Keep the Phase 03 relationships and Phase 04 hierarchy working.
7. Run:

```bash
python -m tools.models.demo
pytest
```

The interface must represent real NEXUS behavior. An interface that is declared but never used through its type doesn't count.

---

## 3 · V1 Checkpoint

Send Claude Code:

> Phase 05 v1 check, read-only. Confirm: one ABC with at least one `@abstractmethod` exists in `tools/models/`; at least two classes implement it with different, meaningful behavior; a function or method accepts the interface type and is called with different implementations in `demo.py`; Phase 03 relationships and the Phase 04 hierarchy are preserved; the demo runs and `pytest` shows no new test failures. Report PHASE-05 V1: READY or BLOCKED with the reason. Do not modify anything.

If **BLOCKED**, fix it (Claude Code can help) and run the check again. Once it reports **PHASE-05 V1: READY**:

1. Stage and commit your work.
2. Push `phase-05`.
3. Create the annotated tag `phase-05-v1`.
4. Push the tag.
5. Run `git status`. It must be clean.

---

## 4 · Domain Expansion

Now Claude Code helps you grow the domain so it covers the full NEXUS pipeline: candles, structure, confluence, trade plans, orders, and the account.

Send Claude Code:

> Phase 05 domain expansion. Read AGENTS.md, the README (pipeline and domain model sections), `docs/design/requirements.md`, `tools/models/`, and the existing tools in `tools/`. Recommend trading-domain concepts that are missing or underrepresented in `tools/models/`, explaining what each one represents and the consequences of including it. Do not write any code until I make a decision on each recommendation.

Discuss each recommendation and decide. Claude Code may suggest alternatives, but **you make the decisions**. Once you decide, Claude Code may implement them.

The finished expansion should add **about 10 new meaningful entities** beyond `phase-05-v1`. That's a floor, not a target: empty, duplicate, disconnected, or placeholder classes don't count.

Rules for the expansion:

- Apply everything from Phases 01–05: requirements, responsibilities, relationships, inheritance, and interfaces.
- One-to-many relationships may appear in requirements and diagrams, but **no lists, dicts, or sets in the code yet**. That's Phase 06.
- New classes go in `tools/models/`. Don't change the existing pipeline tools.
- **Don't edit `.puml` files by hand.** Claude Code syncs them from your decisions.

When your decisions are made, send:

> Implement my decided entities in `tools/models/`. Update requirements.md, `crc.puml`, `domain-model.puml`, and `use-cases.puml` (only where an actor goal changed). Extend `demo.py`. Add pytest tests in `tests/models/` for each new class and run the full suite. Update `docs/evolution/phase-05.md` from Git history and repo evidence. Report PHASE-05 DOMAIN EXPANSION: COMPLETE only when the demo runs, `pytest` shows no new test failures, and docs match the code.

Don't continue until it reports **PHASE-05 DOMAIN EXPANSION: COMPLETE**. Open every changed diagram in PyCharm and check it yourself.

---

## 5 · Final Review and Check

Send Claude Code:

> Run the Phase 05 final review and check. Do one light review of the expanded domain and list important recommendations, clearly marked as advisory. Then report PASS or FAIL with evidence for each: the interface is used polymorphically; Phase 03 and 04 work is preserved; about 10 meaningful new entities exist since `phase-05-v1`; no collections used for relationships; requirements, CRC, and domain model match the code; `pytest` shows no new test failures; `docs/evolution/phase-05.md` exists; `phase-05-v1` exists; no pipeline tools outside `tools/models/` changed; no secrets in the diff. Report PHASE-05: PASSED or FAILED. Do not fail the phase only because I decline an advisory recommendation with a reason.

Decide on each recommendation yourself. Continue until it reports **PHASE-05: PASSED**.

---

## 6 · Merge and Tag

1. Stage only the intended files and inspect the staged diff.
2. Commit: `Complete Phase 05 polymorphism, interfaces, and domain expansion`
3. Push `phase-05`.
4. Open a PR from `phase-05` into `main` and merge it.
5. Sync local `main`.
6. Create and push the annotated tag `phase-05-completed`.
7. Change Phase 05's ⬜ to ✅ in the README.
8. Run `git status` on `main`. It must be clean.

**Phase 05 is complete when** `phase-05-v1` and `phase-05-completed` both exist on GitHub and `main` is clean. Phase 06 can't start without `phase-05-completed`.
