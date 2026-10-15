# Phase 01 · Requirements and Initial Domain Modeling

## Goal

Starting from the Phase 00 executive summary, write the first requirements and domain model for NEXUS Trade.

By the end of Phase 01 you will have:

- exactly **3** core domain entities
- **3–4** use cases (actor + goal)
- **4–5** functional requirements
- CRC analysis for each entity
- relationships and multiplicities between the entities
- **3** design diagrams

Keep the design small and conceptual. **No Python domain classes yet.** Implementation starts in Phase 02. Existing tools in `tools/` stay untouched.

Use Phase 00 as your Git reference. Routine Git commands aren't repeated here.

---

## 1 · Start the Phase

| Activity | Who |
|---|---|
| Create the branch | Daniel or Claude Code |

1. Sync `main` with GitHub and confirm the working tree is clean.
2. Create and verify the `phase-01` branch.
3. Save this file as `phases/phase-01-requirements-domain-modeling.md`.
4. Re-read `docs/executive-summary.md`. It's your starting point.

**Done when:** you're on `phase-01`, this file is in `phases/`, and the executive summary is your baseline.

---

## 2 · Requirements and Domain Model

| Activity | Who |
|---|---|
| Engineering decisions | Daniel has the final say |
| Claude Code | Allowed to suggest entities, use cases, requirements, and CRC, and to draft the file |

Create `docs/design/requirements.md`:

```markdown
# NEXUS Trade Requirements and Initial Domain Model

## Domain Entities

## Use Cases

## Functional Requirements

## CRC Analysis

## Relationships and Multiplicities
```

Fill it in yourself, or ask Claude Code to draft it and then edit it until every decision is one you agree with:

- **Exactly 3 domain entities.** Pick the 3 most central concepts in NEXUS. More get added in later phases as requirements grow.
- **3–4 use cases**, each with an actor and a goal (for example: *Trader — review a confirmed setup*).
- **4–5 functional requirements**, each a clear "NEXUS shall…" statement that can be checked.
- **CRC** for each entity: its responsibilities, and the other entities it collaborates with.
- **Relationships and multiplicities** between the 3 entities (for example, `1` to `0..*`).

Stay within Phase 01 scope: no inheritance, interfaces, patterns, or architecture.

**Done when:** `requirements.md` contains your full initial design, and you've approved every decision in it.

---

## 3 · Create and Verify the Diagrams

| Activity | Who |
|---|---|
| Engineering decisions | Already made by Daniel in `requirements.md` |
| Writing the diagram files | Claude Code allowed |
| Visual check | Daniel only |

Required files:

```
docs/design/uml/use-cases.puml
docs/design/uml/crc.puml
docs/design/uml/domain-model.puml
```

The diagrams must show only what's in `requirements.md`. They add no new decisions.

Send Claude Code:

> Read AGENTS.md and `docs/design/requirements.md`. Create `use-cases.puml`, `crc.puml`, and `domain-model.puml` in `docs/design/uml/`, representing only what requirements.md already states. Use `skinparam classAttributeIconSize 0` and standard UML visibility (+, -, #). Do not use UML relationship arrows inside the CRC cards. Do not invent entities, attributes, methods, relationships, or multiplicities. If requirements.md is unclear, ask me instead of guessing.

Then **open all three files in PyCharm yourself** and confirm they render and match `requirements.md`.

**Done when:** all three diagrams render, match the requirements, and you've checked them yourself.

---

## 4 · Record the Evolution

| Activity | Who |
|---|---|
| New decisions | Not allowed |
| Writing the record | Claude Code allowed |
| Verification claims | Must match what Daniel actually did |

Send Claude Code:

> Create `docs/evolution/phase-01.md` describing how NEXUS went from the Phase 00 executive summary to the Phase 01 requirements and diagrams. Use these sections: Starting State, Requirements and Analysis, Domain Modeling, AI Assistance, Verification, End State. Use only repo evidence. Before writing Verification, ask me whether I personally checked the rendered diagrams.

Read it and make sure it's accurate.

**Done when:** the record accurately describes Phase 01 with no new decisions or false claims.

---

## 5 · V1 Checkpoint

| Activity | Who |
|---|---|
| Git operations | Daniel or Claude Code |
| Review | Daniel checks `git diff --staged` before committing |

This saves your design **before** review. Stage only:

```
docs/design/requirements.md
docs/design/uml/use-cases.puml
docs/design/uml/crc.puml
docs/design/uml/domain-model.puml
docs/evolution/phase-01.md
phases/phase-01-requirements-domain-modeling.md
```

Include `docs/executive-summary.md` only if you actually changed it.

- Commit message: `Complete Phase 01 initial design`
- Push `phase-01`
- Annotated tag: `phase-01-v1`, then push it

Never move, delete, or recreate the v1 tag. Fixes after review go in new commits.

**Done when:** `phase-01` and `phase-01-v1` are both pushed.

---

## 6 · Engineering Review

| Activity | Who |
|---|---|
| Final say | Daniel |
| Review | Claude Code |

Send Claude Code:

> Run a Phase 01 engineering review. Read AGENTS.md, this phase file, `docs/executive-summary.md`, `docs/design/requirements.md`, and the three diagrams. Check: exactly 3 entities; 3–4 use cases with actor and goal; 4–5 testable functional requirements; CRC responsibilities fit each entity and collaborators are real; relationships and multiplicities make sense; diagrams match requirements.md; nothing beyond Phase 01 scope. Number each finding, give evidence, and separate real problems from optional ideas. Do not modify any files.

Answer each finding:

- **ACCEPT** — adopt it, with your reason
- **MODIFY** — fix it differently, with your reason
- **REJECT** — keep your decision, with your reason
- **DEFER** — postpone it, with your reason

If a decision changes, update `requirements.md` **first**, then send:

> Sync the Phase 01 diagrams with `docs/design/requirements.md`. Change only what the updated requirements require. Report anything that doesn't match instead of guessing.

Check any changed diagram in PyCharm again.

**Done when:** every finding has a decision, and accepted changes are in requirements and diagrams.

---

## 7 · Final Check

Send Claude Code:

> Update `docs/evolution/phase-01.md` with the engineering review outcome and any changes it caused. Use only repo evidence.

Then:

> Run the Phase 01 check. For each item below, report PASS or FAIL with file evidence: `requirements.md` has all five sections; exactly 3 entities; 3–4 use cases; 4–5 functional requirements; CRC for every entity; relationships and multiplicities defined; all three `.puml` files exist and match requirements.md; evolution record exists and includes the review outcome; `phase-01-v1` tag exists; no Python domain classes were added; no files in `tools/` changed; no secrets in the diff. Do not fix anything.

If anything fails, fix it and run the check again.

**Done when:** every item reports PASS.

---

## 8 · Merge and Tag

You decide when Phase 01 is ready. Passing the check doesn't decide it for you.

1. Stage only the intended files and inspect the staged diff.
2. Commit: `Complete Phase 01 requirements and initial domain model`
3. Push `phase-01`.
4. Open a PR from `phase-01` into `main` and merge it.
5. Sync local `main`.
6. Create and push the annotated tag `phase-01-completed`.
7. Change Phase 01's ⬜ to ✅ in the README.

**Phase 01 is complete when** the work is merged on `main`, local `main` matches, and `phase-01-completed` points to the merged commit.

Don't implement the entities yet. Phase 02 turns the domain model into Python classes.
