# Phase 09 Evolution Record: Adapter and Facade

## Starting State

- Phase 08 was merged into `main` and tagged `phase-08-completed`. The later evolution-record commits ended at merge commit `203e9aa` (pull request #26).
- The `workshop-09` branch was created from a clean `main` at `203e9aa`. `git fetch --tags` brought nothing new, so the branch began from the accepted Phase 08 state.
- The workshop files were copied from `course-content` into `workshops/` (kept out of Git by `.gitignore`). `agents/PROMPTS.md` was created with the Workshop 08 prompts first, unchanged, followed by the Workshop 09 prompts.
- The start check reported WORKSHOP-08 COMPLETION: VERIFIED and WORKSHOP-09 START CHECK: PASS. In Nexus, the Workshop 08 completion tag is `phase-08-completed`.
- `pytest` gave 1003 passed and 0 failed.

## Section 2: V1 Adapter

### AI Use

Nexus is a personal project, not a graded course submission, so Claude carried out Section 2 with Daniel making the decisions (the same arrangement as Phase 08). The workshop's `Main.java` is `tools/models/demo.py` in Nexus.

### Decisions

| Question | Decision |
|---|---|
| Problem | OANDA describes candles in its own terms ("instrument" and "granularity" strings, nanosecond time strings, "mid" o/h/l/c price strings), while NEXUS models a `Candle` with a `CurrencyPair` and a `Timeframe`. Nothing translated between them. |
| Pattern | Adapter. Claude suggested both options; Daniel chose Adapter. Facade was less appropriate: the problem is an incompatible interface, and `run_full_analysis()` already gives the analysis steps one entry point, so a Facade would only rename it. |

### Implementation

Commit `2201088` ("Workshop 09 V1: Adapter for OANDA candles"), tagged `workshop-09-v1-completed` and pushed with `workshop-09`.

- `tools/models/candle_source.py`: the `CandleSource` interface (ABC) with `candles()`.
- `tools/models/oanda_candle_adapter.py`: `OandaCandleAdapter` implements `CandleSource` for one OANDA response and one `CurrencyPair`. It rejects another instrument or a granularity that is not a `Timeframe`, and skips incomplete candles.
- `tools/models/demo.py`: an Adapter section with fixed OANDA-format data and the comment explaining the choice.
- The V1 check reported WORKSHOP-09-V1: READY FOR INSTRUCTOR REVIEW. `pytest` gave 1003 passed.

## Section 4: Structural Design Collaboration

### Review

| Finding | Decision |
|---|---|
| `_poll_closed_trades()` in `weekly_cycle.py` imported the private `execute_trade._build_client()`, called OANDA's `OpenTrades` and `TradeDetails` endpoints, and read OANDA's response shape itself. | **Changed (Facade).** Daniel left the choice to Claude, which recommended it, and he agreed: so only one file talks to OANDA's trade endpoints. |
| `fetch_account()` returns OANDA terms (`NAV`, `marginUsed`) in a dict, and nothing turned it into an `Account`. | Covered by `PipelineAdapter.account()`; no separate adapter. |
| A Facade for the scan steps in `_scan_once`. | **Not changed.** Only one caller runs them, so there is no repeated coordination. |
| The Phase 08 decision to switch `build_trade_plan` to `TradePlanBuilder` in Phase 09, which needs the pipeline dicts turned into domain objects (`docs/evolution/phase-08.md`). | **Changed (Adapter).** Claude first suggested skipping it as too broad, then found the Phase 08 decision. Daniel chose to do it now, after Claude explained that it needs realistic data in two existing test fixtures and may reject a few borderline plans because `TradePlan` rounds the risk itself. |

### Facade: OANDA trade lookups

- `tools/oanda/execute_trade.py`: new `get_trade_details(trade_id)`. With `get_open_trades()` and `close_trade()`, it is the one entry point for OANDA trade lookups.
- `tools/scheduler/weekly_cycle.py`: `_poll_closed_trades()` uses `get_open_trades()` and `get_trade_details()` and no longer builds an OANDA client. Behavior is unchanged.

### Adapter: pipeline dicts to domain objects

- `tools/models/pipeline_adapter.py`: `PipelineAdapter` builds a `CurrencyPair` from the reference timeframe's candles, a `Signal` from the analysis dict, and an `Account` from `fetch_account()`'s dict. It translates bullish/bearish/ranging into uptrend/downtrend/ranging and the most recent BOS or CHoCH into a `BreakOfStructure` or `ChangeOfCharacter` on a `SwingPoint`, using the candle close at the break. A timeframe missing from the analysis becomes ranging with no event, a neutral vote, as in the pipeline's confluence score.
- `parse_oanda_time()` in `oanda_candle_adapter.py` is now public, because both adapters use it.
- `tools/trade_plan/build_trade_plan.py`: after the lot size, it builds the plan with `TradePlanBuilder` from the adapted `Signal` and `Account`. If `TradePlan` rejects it, no plan is written. The written plan's reference timeframe comes from the domain plan. The other plan fields are unchanged.

### Synchronization

- `docs/design/requirements.md`: CRC cards for `CandleSource`, `OandaCandleAdapter`, and `PipelineAdapter`; `CandleSource` in the Interfaces table; the Object Creation note updated; a new Structural Design (Phase 09) section. No functional requirement changed.
- `docs/design/uml/crc.puml` and `docs/design/uml/domain-model.puml`: the three new classes, the `CandleSource` realization, and their dependencies.
- `README.md`: the design-pattern table rows for Adapter and Facade, and the Phase 09 roadmap deliverables, now name what was built.

## Final Review Recommendations

The Prompt 04 review reported WORKSHOP-09: PASSED with two advisory recommendations. Daniel accepted both.

| Recommendation | Decision |
|---|---|
| `_check_trade_milestones()` in `weekly_cycle.py` still built its own OANDA client and called the `PricingInfo` endpoint. | **Changed (Facade).** New `get_mid_prices(pairs)` in `execute_trade.py`; the milestone check uses it. Behavior is unchanged. |
| Phase 08 has a guide in `phases/`; Phase 09 had none. | **Added** `phases/phase-09-adapter-and-facade.md`, following the Phase 08 guide and the steps used in this phase. |

`tests/test_practice_only_env.py::test_weekly_cycle_milestones_use_practice` watched for the OANDA client in `weekly_cycle.py`. The client is now built in `execute_trade.py`, so the test failed although the practice-only rule (FR5) still held. With Daniel's approval, its patch target changed from `oandapyV20.API` to `tools.oanda.execute_trade.API`; its assertion is unchanged.

## Tests

- `tests/models/test_oanda_candle_adapter.py`: 9 tests.
- `tests/test_trade_access.py`: 6 tests (3 for trade lookups, 3 for prices). The two scheduler tests fail on the old `weekly_cycle.py`.
- `tests/models/test_pipeline_adapter.py`: 10 tests.
- `tests/test_pipeline_adapter_votes.py`: 3 tests that run the real analysis tools on fixed synthetic candles and check that the domain `Signal` votes exactly like `score_confluence`.
- `tests/test_calculate_lot_size.py`: two fixtures now hold realistic data (an analysis that agrees with the signal's votes, two candles, and a full fake account dict), because `TradePlan` rebuilds the signal from them. What the tests check is unchanged. Two new tests: no plan when the analysis gives no valid signal, and the reference timeframe comes from the domain signal.
- `pytest`: 1033 passed and 0 failed.

## Notes for Later Phases

- `tools/api/server.py` still builds its own OANDA client for its `/prices` endpoint; it could use `get_mid_prices()`.
- The pipeline still caches and analyzes candle dicts; `OandaCandleAdapter` is used only in the demo and tests.
- `OrderFactory` stays deferred to Phase 10.
