# Phase 01 Evolution Record: Requirements and Initial Domain Modeling

## Starting State

- Phase 00 was merged into `main` through pull request #2 (merge commit `f0b42f3`) and tagged `phase-00-completed`.
- The `phase-01` branch was created from that commit. At the time of this record it has no commits of its own; all Phase 01 work is uncommitted in the working tree.
- The baseline was `docs/executive-summary.md`. It describes the problem (traders struggle to read market structure, find strong setups, and know whether a strategy works), the intended users (anyone interested in forex trading), the general purpose (analyze the market, pick setups, backtest them, highlight top-performing pairs), and the initial scope (OANDA practice account only, no real money, never exceed the set risk limit).
- `docs/design/` contained only an empty `uml/` folder. No requirements, use cases, or diagrams existed.

## Requirements and Analysis

- `docs/design/requirements.md` was created with the five sections required by the Phase 01 guide.
- **Use cases:** four, all with the actor Trader: review market structure (UC1), review a suggested trade setup (UC2), backtest trade setups (UC3), and see the best-performing pairs (UC4). Each maps to a goal in the executive summary's General Purpose.
- **Functional requirements:** five "NEXUS shall" statements (FR1–FR5), each linked to a use case. FR3 ("shall not suggest any trade setup whose risk is greater than the set risk limit") comes from the executive summary's Initial Scope.
- No numeric trading rules (risk percent, reward-to-risk ratio, confluence threshold) were added. FR3 refers only to "the set risk limit."
- The source-of-truth location for requirements changed. `AGENTS.md` section 6, `docs/phase-workflow.md`, and the README project tree now point to `docs/design/requirements.md`, and the empty `docs/requirements/` folder was deleted. This resolved a conflict between `AGENTS.md`, which named `docs/requirements/`, and the Phase 01 guide, which places the file in `docs/design/`.

## Domain Modeling

- **Entities:** exactly three, `CurrencyPair`, `TradeSetup`, and `BacktestResult`. They match the three activities in the executive summary: analyzing pairs, picking setups, and backtesting them.
- Past price data and market structure were treated as things a `CurrencyPair` knows, not as separate entities.
- **CRC analysis:** each entity has three "Know..." responsibilities. Collaborators are limited to the other two entities.
- **Relationships and multiplicities:**
  - `CurrencyPair` has `TradeSetup`, `1` to `0..*`
  - `CurrencyPair` has `BacktestResult`, `1` to `0..*`
  - `BacktestResult` is based on `TradeSetup`, `0..1` to `0..*`
- No attributes, methods, inheritance, interfaces, or design patterns were defined, in line with Phase 01 scope.
- **Diagrams:** three PlantUML files were created in `docs/design/uml/`:
  - `use-cases.puml`: the Trader actor and UC1–UC4 inside a "NEXUS Trade" boundary
  - `crc.puml`: one card per entity, with no relationship arrows between cards
  - `domain-model.puml`: the three entities, shown by name only, with the three named associations and their multiplicities
- All three files use `skinparam classAttributeIconSize 0`. No members exist yet, so no visibility markers appear.

## AI Assistance

- Claude Code (Claude Opus 5.5) worked under `AGENTS.md`, which reserves engineering decisions for Daniel.
- Claude Code proposed candidate entity sets, labeled as suggestions. Daniel chose the suggested set of `CurrencyPair`, `TradeSetup`, and `BacktestResult`.
- Claude Code drafted `docs/design/requirements.md` from the executive summary and that entity choice, and listed its own judgment calls for Daniel to review: a single actor, price data not being an entity, the three market-structure values, ranking by win rate, leaving out numeric trading rules, and the `BacktestResult`–`TradeSetup` relationship.
- At Daniel's request, Claude Code updated `AGENTS.md`, `docs/phase-workflow.md`, and `README.md` to the new requirements location and deleted `docs/requirements/`.
- Claude Code generated the three `.puml` files from `requirements.md` without adding entities, attributes, methods, relationships, or multiplicities.
- Claude Code checked the diagrams with PlantUML's syntax check and rendered them outside the repository. This is not a substitute for Daniel's own visual check.

## Verification

- Daniel opened `use-cases.puml`, `crc.puml`, and `domain-model.puml` in IntelliJ and confirmed that all three rendered and match `docs/design/requirements.md`.
- Daniel approved every decision in `docs/design/requirements.md`.
- Before Daniel's check, Claude Code ran PlantUML's syntax check on all three files, and all three passed.

## End State

- On `phase-01`, uncommitted:
  - new: `docs/design/requirements.md`
  - new: `docs/design/uml/use-cases.puml`, `crc.puml`, `domain-model.puml`
  - new: `docs/evolution/phase-01.md`
  - modified: `AGENTS.md`, `README.md`, `docs/phase-workflow.md`
  - deleted: `docs/requirements/.gitkeep`
- No Python domain classes were added, and no files in `tools/` changed.
- The `phase-01-v1` tag does not exist yet. The next step is the V1 checkpoint in Section 5 of the Phase 01 guide.
