# Phase 10 Evolution Record: Refactoring

## Starting State

- Workshop 09 was merged into `main` (pull request #27, merge commit `dedf031`) and tagged `workshop-09-completed` on GitHub.
- The `workshop-10` branch starts at `dedf031`.
- `pytest` gave 1033 passed and 0 failed.

## V1 Refactoring

### Problem

`build_trade_plan.py` had its own reference-timeframe rule (`_REFERENCE_TF_PRIORITY` and `_pick_reference_tf()`), a copy of the FR9 rule that the domain `Signal` already owns in `reference_timeframe()`. The tool also loaded the candle files twice: once for the entry price and once for the domain check.

### Implementation

Commit `95bc004` ("Workshop 10 V1: Signal owns reference timeframe rule in build_trade_plan"), pushed with `workshop-10` and tagged `workshop-10-v1-completed`.

- `_pick_reference_tf()` and `_REFERENCE_TF_PRIORITY` were removed. The new `_reference_timeframe()` builds a `Signal` through `PipelineAdapter` and asks it for `reference_timeframe()`.
- Candles for every analysed timeframe are loaded once, into `candles_by_tf`, and used for both the entry price and the domain check.
- At Daniel's request, the H1 fallback and the "No H1 data in analysis" guard were kept, so a signal with no reference timeframe still falls back to H1 as before. Rejecting such a setup instead is a behavior change, left for a separate commit.
- The old rule read `direction` and `votes` from the signal file. `Signal` recomputes them from the analysis file. Both use the order H4, H1, M5, M1, so they agree whenever the two files agree.

The V1 check reported WORKSHOP-10-V1: READY FOR INSTRUCTOR REVIEW. `pytest` gave 1033 passed, and `python -m tools.models.demo` exits 0.

## Refactoring Collaboration

### Review

Claude reviewed the domain models and pipeline tools for duplicated code, long methods, feature envy, repeated type decisions, and unnecessary abstractions, and made three recommendations. Daniel made the decisions:

| Recommendation | Decision | Daniel's rationale |
|---|---|---|
| R1: the FR9 pip value rule existed twice, in `calculate_lot_size.pip_value_per_lot()` (with its own `_USD_QUOTE_PAIRS` and `_USD_BASE_PAIRS`) and in `CurrencyPair.pip_value_per_lot()`. | **Accepted.** | "The pip value is one FR9 rule with two owners, and if the copies drift apart, lot sizing and the TradePlan risk check will disagree. CurrencyPair should own it, the same way pip_size_for() already does." |
| R2: `calculate_lot_size` kept its own `_MAX_RISK_PERCENT = 2.0`, a copy of `Account.MAX_RISK_PERCENT`. | **Accepted**, in the same commit as R1. | "The 2% cap is an Account rule, so the tool should import it instead of keeping its own copy. The value doesn't change." |
| R3: `build_trade_plan()` is a long method (164 lines) and builds `PipelineAdapter` twice. | **Left as is.** | "The method is long but already split into clear steps. Rewriting the file I just refactored in V1 adds risk for mostly cosmetic gain, and this workshop asks for focused refactorings." |

Reviewed and left unchanged, with no code change proposed:

- The vote table appears twice, in `score_confluence._cast_vote()` and `TimeframeAnalysis.vote()`. Merging them would change behavior (see the open item below), and `score_confluence` has no candles to build domain objects from.
- `MIN_RISK_REWARD` read from `.env` in several tools, next to `TradePlan`'s fixed `MIN_REWARD_TO_RISK = 2`. The `.env` value can be set above 2, so these are not the same rule, and changing them touches a trading rule.
- `if direction == "bearish"` string checks in several tools. Replacing them with `TradeDirection` would move the tools onto domain types, which goes beyond this workshop.
- The long functions in `email_report.py` are HTML templates, and sending already goes through one `send()` function.

### Implementation (R1 and R2)

- `tools/models/currency_pair.py`: new module-level `pip_value_for(name, price)`, next to `pip_size_for()`. `CurrencyPair.pip_value_per_lot()` still validates its price, then calls it.
- `tools/trade_plan/calculate_lot_size.py`: `pip_value_per_lot()` keeps its name and signature and calls `pip_value_for()`. The cross-pair check in `calculate_lot_size()` now catches that `ValueError` instead of checking its own pair lists. `_USD_QUOTE_PAIRS`, `_USD_BASE_PAIRS`, and `_MAX_RISK_PERCENT` were removed, and the tool imports `MAX_RISK_PERCENT` from `account.py`.
- The tool still does not validate the price, and `CurrencyPair` still does, so neither caller's behavior changes.

### Behavior Preservation

- `pytest` gave 1033 passed and 0 failed, the same as before the refactoring. `python -m tools.models.demo` exits 0.
- The old `calculate_lot_size.py` (from `95bc004`) and the new one returned the same pip value and the same lot size result on 1485 inputs: 11 pairs (USD-quote, USD-base, and cross) × 5 prices × 3 balances × 3 risk percents × 3 stop-loss sizes. Both reject the risk percents 0, 2.01, and 3.
- Known difference, no effect on behavior: the cross-pair `ValueError` from `calculate_lot_size.pip_value_per_lot()` now uses the domain's wording, "… is a cross pair; no pip value until a real conversion exists", instead of "… is a cross pair: no pip value until a real conversion exists (FR9)". It is still a `ValueError` containing "cross pair", which is what the tests check. The warning that `calculate_lot_size()` logs for a cross pair is unchanged.

### Synchronization

- `docs/design/uml/domain-model.puml`: `pip_value_for` added to the `SharedHelpers` note. `pip_size_for` was added too; it already existed in the code but was missing from the diagram.
- `docs/design/uml/crc.puml`: no change. `CurrencyPair` already knows its pip size and pip value.
- `docs/design/requirements.md`: Daniel updates the source line above the "Pip Size and Pip Value" table himself, as AGENTS.md says the agent does not edit requirements. The rule values do not change.
- Tests: no new tests. The existing pip value tests for `CurrencyPair` and `calculate_lot_size` cover both callers.

## Notes for Later Phases

- **Open: FR8 vote weighting.** `score_confluence` picks the majority direction from weighted votes (M1 = 1, M5 = 1, H1 = 2, H4 = 3), and `Signal` uses unweighted votes, as FR8 describes. They can pick opposite directions: H4 bullish against M1 and M5 bearish gives bullish in the tool and bearish in `Signal`. Whether FR8 should include weighting is a requirements decision for a later phase. (The tie case, where the tool picks bullish and `Signal` gives no direction, is already recorded in requirements.md.)
- The H1 fallback in `build_trade_plan` could be replaced by rejecting a setup with no reference timeframe, in a separate commit.
- R3 (splitting `build_trade_plan()`) was declined for this phase.
