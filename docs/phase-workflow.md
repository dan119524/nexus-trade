# Phase Workflow

How every NEXUS phase (00–12) gets built, following the same cycle as a CSC 413 workshop.

The 7 pipeline workflows in `workflows/` describe how NEXUS **runs**. This file describes how NEXUS gets **built**.

---

## The Cycle

| Step | What happens | Who |
|---|---|---|
| 1 | Start the branch | Daniel |
| 2 | Update requirements | Daniel |
| 3 | Design | Daniel (agent can suggest) |
| 4 | Build | Daniel + agent |
| 5 | Test | Daniel + agent |
| 6 | v1 checkpoint | Daniel |
| 7 | Engineering review | Agent |
| 8 | Decide on review findings | Daniel |
| 9 | Sync design docs | Agent |
| 10 | Evolution record | Agent |
| 11 | Phase check | Agent |
| 12 | Merge and final tag | Daniel |

---

## Step 1: Start the branch

```bash
git switch main
git pull
git switch -c phase-NN
git branch --show-current
```

## Step 2: Update requirements

Add or change user stories and constraints in `docs/requirements/` for what this phase adds. This is your decision, not the agent's.

## Step 3: Design

Update the domain model and CRC cards in `docs/design/` with the new classes, responsibilities, and relationships for this phase.

## Step 4: Build

Write the code in `tools/`. Use only concepts from this phase and earlier ones.

## Step 5: Test

Add pytest tests in `tests/` for the new or changed behavior. Run the full suite:

```bash
pytest
```

Every earlier test must still pass.

## Step 6: v1 checkpoint

This saves your own work **before** the review.

```bash
git status
git add <exact files>
git commit -m "Phase NN: initial implementation"
git tag -a phase-NN-v1 -m "Phase NN before review"
git push origin phase-NN
git push origin phase-NN-v1
```

## Step 7: Engineering review

Paste this prompt to the agent:

> Run an engineering review for phase NN. Read AGENTS.md, the README roadmap, `docs/requirements/`, `docs/design/`, the code, and the tests. Check the work against this phase's topic only. List concrete problems with file evidence, and separate real problems from optional ideas. Do not modify any files.

## Step 8: Decide on findings

For each finding, choose **accept**, **modify**, **reject**, or **defer**. Make the accepted changes, then run `pytest` again.

## Step 9: Sync design docs

> Sync the design docs for phase NN. Compare `docs/design/` with `docs/requirements/` and the current code. Update diagrams to match what is actually implemented. Do not invent anything. If requirements, code, and docs disagree, report it instead of fixing it.

## Step 10: Evolution record

> Write `docs/evolution/phase-NN.md`. Using Git history since `phase-(NN-1)-completed`, describe what changed in this phase and why, based only on repo evidence. No recommendations, no future plans.

## Step 11: Phase check

> Check phase NN. Using the README roadmap row for this phase, list each deliverable as PASS or FAIL with file evidence. Confirm `pytest` passes and no secrets are in the diff. Do not fix anything.

If anything fails, fix it and run the check again.

## Step 12: Merge and final tag

```bash
git add <exact files>
git commit -m "Phase NN: complete"
git push origin phase-NN
```

Open a pull request from `phase-NN` into `main` on GitHub and merge it. Then:

```bash
git switch main
git pull
git tag -a phase-NN-completed -m "Phase NN completed"
git push origin phase-NN-completed
```

Finally, change the phase's ⬜ to ✅ in the README roadmap.
