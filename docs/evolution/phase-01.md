# Phase 01 Evolution Record: Requirements and Initial Domain Modeling

## Starting State

- Phase 00 was merged into `main` through pull request #2 (merge commit `f0b42f3`) and tagged `phase-00-completed`.
- The `phase-01` branch was created from that commit.
- The baseline was `docs/executive-summary.md`. It describes the problem (traders struggle to read market structure, find strong setups, and know whether a strategy works), the intended users (anyone interested in forex trading), the general purpose (analyze the market, pick setups, backtest them, highlight top-performing pairs), and the initial scope. The original scope said NEXUS works on an OANDA practice account only, will not trade real money, and "will never plan a trade that risks more than the set risk limit." That last clause changed during the engineering review.
- `docs/design/` contained only an empty `uml/` folder. No requirements, use cases, or diagrams existed.

## Requirements and Analysis

- `docs/design/requirements.md` was created with the five sections required by the Phase 01 guide.
- **Use cases:** four, all with the actor Trader: review market structure (UC1), review a suggested trade setup (UC2), backtest trade setups (UC3), and see the best-performing pairs (UC4). Each maps to a goal in the executive summary's General Purpose. The use cases did not change during the review.
- **Functional requirements, initial version** (commit `0d90179`, tag `phase-01-v1`): five "NEXUS shall" statements (FR1–FR5), each linked to a use case. FR3 said NEXUS "shall not suggest any trade setup whose risk is greater than the set risk limit," taken from the executive summary's Initial Scope. The initial version contained no numeric trading rules.
- **Functional requirements, after review:** the requirements were made more precise, the risk-limit rule was replaced by a reward-to-risk rule, and a practice-account requirement was added, giving six. The old FR2 and FR3 were then merged, leaving five (FR1–FR5). See Engineering Review.
- The source-of-truth location for requirements changed. `AGENTS.md` section 6, `docs/phase-workflow.md`, and the README project tree now point to `docs/design/requirements.md`, and the empty `docs/requirements/` folder was deleted. This resolved a conflict between `AGENTS.md`, which named `docs/requirements/`, and the Phase 01 guide, which places the file in `docs/design/`.

## Domain Modeling

- **Entities:** exactly three, `CurrencyPair`, `TradeSetup`, and `BacktestResult`. They match the three activities in the executive summary: analyzing pairs, picking setups, and backtesting them. The entities did not change during the review.
- Past price data and market structure were treated as things a `CurrencyPair` knows, not as separate entities.
- **CRC analysis:** each entity has three "Know..." responsibilities. In the initial version, each entity listed the other two entities as collaborators where they were related. After the review, `CurrencyPair` lists no collaborators, and `TradeSetup` knows its reward-to-risk ratio instead of whether its risk is within a risk limit.
- **Relationships and multiplicities:**
  - `CurrencyPair` has `TradeSetup`, `1` to `0..*`
  - `CurrencyPair` has `BacktestResult`, `1` to `0..*`
  - `BacktestResult` is based on `TradeSetup`, `0..1` to `0..*`
  - After the review, a constraint was added: all trade setups in a backtest result must belong to the same currency pair as that backtest result.
- No attributes, methods, inheritance, interfaces, or design patterns were defined, in line with Phase 01 scope.
- **Diagrams:** three PlantUML files were created in `docs/design/uml/`:
  - `use-cases.puml`: the Trader actor and UC1–UC4 inside a "NEXUS Trade" boundary. Unchanged by the review.
  - `crc.puml`: one card per entity, with no relationship arrows between cards. Updated after the review to match the revised CRC cards.
  - `domain-model.puml`: the three entities, shown by name only, with the three named associations and their multiplicities. A note showing the same-pair constraint was added after the review.
- All three files use `skinparam classAttributeIconSize 0`. No members exist yet, so no visibility markers appear.

## AI Assistance

- Claude Code (Claude Opus 5.5) worked under `AGENTS.md`, which reserves engineering decisions for Daniel.
- Claude Code proposed candidate entity sets, labeled as suggestions. Daniel chose the suggested set of `CurrencyPair`, `TradeSetup`, and `BacktestResult`.
- Claude Code drafted `docs/design/requirements.md` from the executive summary and that entity choice, and listed its own judgment calls for Daniel to review: a single actor, price data not being an entity, the three market-structure values, ranking by win rate, leaving out numeric trading rules, and the `BacktestResult`–`TradeSetup` relationship.
- At Daniel's request, Claude Code updated `AGENTS.md`, `docs/phase-workflow.md`, and `README.md` to the new requirements location and deleted `docs/requirements/`.
- Claude Code generated the three `.puml` files from `requirements.md` without adding entities, attributes, methods, relationships, or multiplicities.
- Claude Code ran the Phase 01 engineering review without modifying files and reported eleven numbered findings: seven real problems and four optional ideas. Claude Code had drafted the material under review.
- Daniel decided every finding. Claude Code then applied the decisions in the order Daniel set: `requirements.md` first, then the diagrams, then `AGENTS.md`. Claude Code also made follow-up edits at Daniel's request: to the executive summary, to the ranking requirement (now FR4), merging the old FR2 and FR3 into the current FR2, and restoring the buy and sell price rule to FR2.

## Engineering Review

The review ran against the `phase-01-v1` design. Daniel's decisions and the resulting changes are below. The Finding column uses the requirement numbers at review time, which match `phase-01-v1`. The Change made column uses the current numbering.

| # | Finding | Decision | Change made |
|---|---|---|---|
| 1 | FR3's "risk" and "risk limit" were undefined, and no entity owned the limit. | MODIFY | The risk-limit rule was replaced by a rule that NEXUS shall not suggest any setup with a reward-to-risk ratio below 2. This rule is now part of FR2. `TradeSetup`'s CRC responsibility became "Know its reward-to-risk ratio." |
| 2 | No entity owns the actions in FR1, FR2, FR4, and FR5. | DEFER | A note in the CRC section says the NEXUS system performs these actions in Phase 01, and responsible classes are assigned in later phases. |
| 3 | FR5 did not say which backtest result to use or how to rank pairs with zero trades. | MODIFY | FR4 ranks by the win rate of each pair's most recent backtest result. A follow-up edit ranks pairs with zero trades or no backtest result last. |
| 4 | FR1 gave no criteria for uptrend, downtrend, or ranging. | MODIFY | FR1 defines an uptrend as higher highs and higher lows, a downtrend as lower highs and lower lows, and anything else as ranging. |
| 5 | `CurrencyPair`'s collaborators did not follow from its responsibilities. | ACCEPT | `CurrencyPair`'s collaborators were removed from the CRC table and `crc.puml`. |
| 6 | `AGENTS.md` section 10 allowed only implemented designs in `docs/design/`, which conflicts with Phase 01. | ACCEPT | Section 10 now allows design-only diagrams based on `docs/design/requirements.md` in Phase 01, before any code exists. |
| 7 | This evolution record was out of date after the v1 checkpoint. | DEFER | Fixed by this update. |
| 8 | FR4 did not define a win. | ACCEPT | FR3 defines a win as a trade that hits its take profit before its stop loss. |
| 9 | The model allowed a backtest result to include setups from another pair. | ACCEPT | A same-pair constraint was added to the relationships section and as a note in `domain-model.puml`. |
| 10 | FR2 did not require consistent prices. | ACCEPT | FR2 required stop loss < entry < take profit for a buy, and the reverse for a sell. The rule was dropped when FR2 and FR3 were merged, then restored to FR2; see the post-review change below. |
| 11 | The practice-account-only scope was not a requirement. | ACCEPT | FR5 says NEXUS shall work only with an OANDA practice account and shall never trade real money. |

**Follow-up change:** the executive summary's Initial Scope now ends with "and it will never suggest a trade with a reward-to-risk ratio below 2," so it agrees with the reward-to-risk rule in FR2.

**Post-review change:** the review left six functional requirements, above the Phase 01 guide's limit of four to five. Daniel merged the old FR2 and FR3 into a single FR2 and renumbered the rest: old FR4 became FR3, old FR5 became FR4, and old FR6 became FR5. The merged FR2 at first left out the buy and sell price rule added for finding 10. Daniel then restored the rule to FR2 as part of the same requirement: for a buy, stop loss < entry < take profit; for a sell, take profit < entry < stop loss. The count stayed at five.

## Verification

- Before the review, Daniel opened `use-cases.puml`, `crc.puml`, and `domain-model.puml` in IntelliJ and confirmed that all three rendered and matched `docs/design/requirements.md`.
- Before the review, Daniel approved every decision in `docs/design/requirements.md`.
- Before Daniel's check, Claude Code ran PlantUML's syntax check on all three files, and all three passed.
- After the review, `crc.puml` and `domain-model.puml` changed. Claude Code ran PlantUML's syntax check on all three files again, and all three passed. `use-cases.puml` has not changed since Daniel's check.
- After the review, Daniel re-checked the changed `crc.puml` and `domain-model.puml` in IntelliJ.

## End State

- `phase-01-v1` points to commit `0d90179`, the design before review.
- Review changes are uncommitted on `phase-01`:
  - modified: `docs/design/requirements.md`, `docs/design/uml/crc.puml`, `docs/design/uml/domain-model.puml`
  - modified: `docs/executive-summary.md`, `AGENTS.md`
  - modified: `docs/evolution/phase-01.md`
- The design has 3 entities, 4 use cases, and 5 functional requirements.
- No Python domain classes were added, and no files in `tools/`, `tests/`, or `frontend/` changed since `phase-00-completed`.
