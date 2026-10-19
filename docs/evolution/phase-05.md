# Phase 05 Evolution Record: Polymorphism, Interfaces, and Domain Expansion

## Starting State

- Phase 04 was merged into `main` through pull request #8 (merge commit `e100236`) and tagged `phase-04-completed`. `phase-04-v1` points to `573ed95`.
- The `phase-05` branch was created from `e100236`. The Phase 05 start check reported PHASE-04 V1 TAG: VERIFIED and PHASE-05 START CHECK: PASS: local `main` matched `origin/main`, the tree was clean, and `pytest` gave 202 passed and 2 failed, the 2 known failures recorded in `docs/evolution/phase-02.md`.
- The baseline was the Phase 04 code: `TradeSetup` with `BuySetup` and `SellSetup`, where a bare `TradeSetup` was blocked by stubs that raised `NotImplementedError`. `tools/models/` had 5 classes: `CurrencyPair`, `TradeSetup`, `BuySetup`, `SellSetup`, and `BacktestResult`.

## Part 1: Interface and Polymorphism

### Design Decisions

Claude Code suggested three options: `TradeSetup` itself as the interface (FR2), an outcome check on past prices (FR3), and a "reviewable" capability across unrelated classes (UC1 to UC3). Daniel decided:

| # | Decision |
|---|---|
| 1 | Option B. `TradeSetup` becomes an ABC. `_check_price_order()`, `direction`, `reward()`, `risk()`, and a new `outcome()` are `@abstractmethod`. The old `NotImplementedError` stubs are removed. |
| 2 | `outcome()` returns `"win"`, `"loss"`, or `"open"` from `self.pair.price_data`, starting at the first point. A buy wins when a high reaches take profit and loses when a low reaches stop loss. A sell is the mirror. A point that touches both is a loss. If neither is reached, the outcome is `"open"`. |
| 3 | A function `evaluate_setup(setup: TradeSetup) -> str` works through the interface type and is called in `demo.py` with a `BuySetup` and a `SellSetup`. |
| 4 | The bare `TradeSetup` test changes to expect `TypeError` (this closes Phase 04 finding 8). |
| 5 | Phase 04 finding 6 (`__init__` calls an overridable check) stays as recorded. |
| 6 | `requirements.md`: the Inheritance bullet is updated, and an "Interfaces" section traces `outcome()` to FR3. |

### Implementation

Commit `dcd948c` ("Complete Phase 05 interface"), tagged `phase-05-v1` ("Phase 05 before domain expansion").

- `trade_setup.py`: `TradeSetup(ABC)` with the five abstract members, and the module-level `evaluate_setup(setup: TradeSetup) -> str`, which returns `setup.outcome()`.
- `buy_setup.py` and `sell_setup.py`: each implements `outcome()`. Each point checks the stop loss first, so a point that touches both is a loss. "Reaches" includes equality.
- `demo.py`: calls `evaluate_setup` on four setups (loss, loss, win, open). The two original demo setups lose because their first price point already reaches the stop loss, so a winning buy and an open sell were added. The bare `TradeSetup` line catches `TypeError`.
- `test_trade_setup.py`: the bare `TradeSetup` test expects `TypeError`. 10 new tests: win, loss, open, and same-point for each subclass (the win and loss data also reach the opposite level later), opposite outcomes on the same data, and `evaluate_setup` with both subclasses.

The Phase 05 v1 check reported PHASE-05 V1: READY. `pytest` gave 212 passed and the 2 known failures.

## Part 2: Domain Expansion

### Recommendations and Decisions

Claude Code read the README, the 7 workflows, and the pipeline tools, and recommended 12 candidates. It reported four conflicts first. Daniel decided:

| Conflict | Decision |
|---|---|
| Most pipeline stages had no requirement. | Add FR6 to FR11 before any code. |
| FR1 (every price point) disagrees with `tools/analysis/detect_trend.py` (4 of the last 6 swing labels). | FR1 stays. The conflict is recorded in `requirements.md` and resolved in Phase 06. |
| Three direction vocabularies (buy/sell, bullish/bearish, uptrend/downtrend). | Keep all three with a recorded mapping: buy/sell is trade direction, bullish/bearish/neutral is the timeframe vote, uptrend/downtrend/ranging is market structure. Bullish leads to buy and matches uptrend. |
| The README lists `Instrument` and `Order` subtypes that no tool implements. | Rename `Instrument` to `CurrencyPair` in the README. Support market orders only. |

| Candidate | Decision |
|---|---|
| Candle | Accept. `CurrencyPair.price_data` stays as (high, low) tuples for now. |
| Timeframe | Accept as an `Enum` value, without weights or priority. |
| SwingPoint | Accept as one class with a label. |
| StructureEvent | Accept as an ABC with subclasses `BreakOfStructure` and `ChangeOfCharacter`. |
| TimeframeAnalysis | Accept. Its trend uses uptrend/downtrend/ranging. |
| Signal | Accept, with four named `TimeframeAnalysis` references `m1`, `m5`, `h1`, `h4`. A tie has no direction, so the signal is invalid. The minimum score is 1 to 4, default 3. |
| TradePlan | Accept. It owns a `TradeSetup` (composition) and adds TP2, lot size, risk amount, and reference timeframe. It rejects a reward-to-risk ratio below 2, rounded to 2 decimals. This closes Phase 02 D5. |
| Account | Accept. |
| Order | Accept, market only. Units are lot size × 100,000, positive for a buy and negative for a sell. No order ID or fill status. |
| Trade | Accept. Its R multiple is calculated from the exit price and the setup's risk, and is `None` while open. |
| Channel | Reject. |
| TradeSummary | Reject. |

Daniel also confirmed six details Claude Code added to the draft requirements: UC5 to UC7 and the FR-to-use-case mapping, bullish/bearish as the StructureEvent direction, the labels each StructureEvent subclass may break, TP2 beyond TP1, the multiplicities, and no weights on Timeframe.

Rules for the expansion (Daniel): model classes hold data and check rules only; they never call OANDA or the Claude API; demos and tests use fake account IDs; no lists, dicts, or sets for relationships.

### Requirements

- New FRs: FR6 (candles), FR7 (swings, BOS, CHoCH), FR8 (confluence), FR9 (trade plan and risk), FR10 (market orders, practice only, confirmed), FR11 (trade outcome and R multiple).
- New use cases: UC5 (be alerted only when enough timeframes agree), UC6 (place a practice market order from a trade plan), UC7 (review recorded trades and their outcomes).
- New sections: Values, Vocabularies, Voting (the Workflow 03 table in market-structure terms, plus the tie rule), Reward-to-Risk Minimum (closes D5), Known Conflicts, and Model Rules.
- Domain Entities rows, CRC cards, relationship rows, and inheritance rows for every new class. The `TradeSetup`, `BuySetup`, and `SellSetup` CRC cards gained their Part 1 `outcome()` responsibility.

### Implementation

New files in `tools/models/`:

| File | Contents |
|---|---|
| `timeframe.py` | `Timeframe(Enum)`: M1, M5, H1, H4. |
| `candle.py` | `Candle`, plus the shared helpers `validate_timeframe`, `validate_time`, and `to_positive_price`. Rejects `complete` other than `True`, high < low, prices <= 0, and a negative or non-whole volume. |
| `swing_point.py` | `SwingPoint` with label HH, HL, LH, or LL. `kind` ("high" or "low") is derived from the label. |
| `structure_event.py` | `StructureEvent(ABC)`. `__init__` sets the direction from the abstract `_direction_for(label)` and checks that the close is beyond the swing price in that direction. |
| `break_of_structure.py` | `BreakOfStructure`: HH is bullish, LL is bearish, anything else raises `ValueError`. |
| `change_of_character.py` | `ChangeOfCharacter`: LH is bullish, HL is bearish, anything else raises `ValueError`. |
| `timeframe_analysis.py` | `TimeframeAnalysis` with `vote()` implementing the voting table. |
| `signal.py` | `Signal` with `direction()`, `score()`, `is_valid()`, and `trade_direction()`. Checks each slot's timeframe and that all four analyses share one `CurrencyPair` object. |
| `account.py` | `Account`. Only `"practice"` is accepted. Risk percent > 0 and <= 2 (`MAX_RISK_PERCENT`). `max_risk_amount()`. |
| `trade_plan.py` | `TradePlan`. Builds its own `BuySetup` or `SellSetup` from the signal. Checks the signal is valid, rounded R:R >= 2 (`MIN_REWARD_TO_RISK`), TP2 beyond TP1, and risk amount <= the account's maximum. |
| `order.py` | `Order`. Requires `confirmed is True` and a practice account. `order_type` is `"MARKET"`. `units()` uses `round()` (`UNITS_PER_LOT`). |
| `trade.py` | `Trade`. An open trade has no exit price. `r_multiple()` uses the plan setup's `risk()`. |

Other changes:

- `__init__.py` exports the new classes.
- `demo.py` gained a pipeline section (candle, BOS and CHoCH, four analyses and their votes, signal, account, trade plan, order, and three trades) and seven new rejected cases.
- `README.md`: see the README section below.
- `tests/models/conftest.py` gained shared fixtures: a fake practice account, bullish and bearish signals, and buy and sell plans.

A mutation check confirmed that the tests depend on the rounding and tie rules. Without rounding, even a plain 2:1 plan (entry 1.0900, stop loss 1.0850, TP1 1.1000) is rejected, because floating point gives 1.99999…. Removing the tie rule fails 4 Signal tests.

### Rules Added After Review of the Expansion

Claude Code reported three rules that nobody had decided. Daniel decided to add all three:

| Class | Rule | Tests |
|---|---|---|
| `TimeframeAnalysis` | Rejects a latest event whose swing point's pair (same object) or timeframe differs from the analysis. | 3 new (other timeframe, other pair, other pair object with the same name). `test_valid_analysis_stores_values` now builds its event on H4, because the rule is an approved requirement change. |
| `Order` | Rejects an account that is not its plan's account (same object). | 1 new. |
| `Trade` | Rejects a win with an R multiple <= 0 and a loss with an R multiple >= 0. | 10 new (buy win and loss at entry and on the wrong side, sell win and loss). |

- A mutation check removed each rule in turn. Each removal failed tests (3, 1, 5, and 5).
- `demo.py`: the H1 analysis now uses its own H1 break of structure, because it had reused the H4 one.
- `requirements.md`, `crc.puml`, and the ValidationRules note in `domain-model.puml` record the three rules.

### README

- `Instrument` is renamed to `CurrencyPair` in the Domain Model table. After the final review, the table lists all 17 classes (A3).
- The Design Highlights table now matches the code and has a Status column. Implemented: inheritance (`TradeSetup` → `BuySetup`/`SellSetup`, `StructureEvent` → `BreakOfStructure`/`ChangeOfCharacter`), the `TradeSetup.outcome()` interface used through `evaluate_setup`, `TradePlan` composition, and market-only orders. Planned: Factory and Builder (Phase 08), Adapter and Facade (Phase 09), MVC (Phase 11). The `Order` subtypes and the `Strategy` interface were removed, because no code implements them.

### Diagram Sync

- **`domain-model.puml`:** synced to the Phase 05 code. `TradeSetup` and `StructureEvent` are `abstract class` with `{abstract}` members, `outcome()` is on all setup classes, and a note names `evaluate_setup`. There are new boxes for the 11 new classes and the `Timeframe` enum, generalization arrows for the StructureEvent subclasses, the 12 new associations with their multiplicities (aggregation for Signal, composition for TradePlan → TradeSetup), and updated notes for helpers, constants, and validation rules. A script compared every class box with the code (attributes, properties, methods, and abstract members); all 16 boxes and the enum matched.
- **`crc.puml`:** cards for every new class, and the `outcome()` responsibility on the three setup cards, mirroring `requirements.md`.
- **`use-cases.puml`:** UC5, UC6, and UC7 added, because they are new actor goals.
- All three files pass PlantUML's `-checkonly` (the jar bundled with IntelliJ's PlantUML plugin) and render without errors.

## Tests

| File | `phase-04-completed` | `phase-05-v1` | Now |
|---|---|---|---|
| `test_currency_pair.py` | 37 | 37 | 37 |
| `test_trade_setup.py` | 53 | 63 | 63 |
| `test_backtest_result.py` | 25 | 25 | 25 |
| `test_timeframe.py` | — | — | 2 |
| `test_candle.py` | — | — | 50 |
| `test_swing_point.py` | — | — | 16 |
| `test_structure_event.py` | — | — | 19 |
| `test_timeframe_analysis.py` | — | — | 20 |
| `test_signal.py` | — | — | 21 |
| `test_account.py` | — | — | 27 |
| `test_trade_plan.py` | — | — | 21 |
| `test_order.py` | — | — | 12 |
| `test_trade.py` | — | — | 31 |

The tests use fixed data and fake account IDs and never call OANDA or the Claude API.

Results: `tests/models/` gives 344 passed. The full suite gives 431 passed and 2 failed, and the 2 failures are the known failures recorded in `docs/evolution/phase-02.md`.

## Final Review

Claude Code ran the Phase 05 final review and check without committing. It reported PHASE-05: PASSED on all ten required items:

- The interface is used polymorphically.
- Phase 03 and 04 work is preserved.
- 11 new entities and 1 value exist since `phase-05-v1`.
- No collections are used for relationships.
- Requirements, CRC, and the domain model match the code.
- `pytest` gave 425 passed and only the 2 known failures.
- This record exists.
- `phase-05-v1` is on the remote.
- No pipeline tools changed.
- There are no secrets in the diff.

Advisory recommendations and Daniel's decisions:

| # | Recommendation | Decision | Change made |
|---|---|---|---|
| A1 | `TradePlan` does not tie the lot size to the risk: a plan with lot size 100 and declared risk 50 is accepted. FR9 says the lot size's risk never exceeds the risk percent. | DEFER to Phase 06, first item | None. Recorded as a known FR9 gap (see Notes for Later Phases). |
| A2 | `TradePlan` does not check that its reference timeframe voted with the signal (the Workflow 04 rule, H4 → H1 → M5 → M1). | DEFER to Phase 06, with A1 | None. |
| A3 | The README Domain Model table still lists `Chart` and does not list the Phase 05 classes. | ACCEPT | The table lists the 17 classes in `tools/models/`, with `Chart` marked as planned for Phase 06. |
| A4 | The shared helpers `validate_timeframe`, `validate_time`, and `to_positive_price` live in `candle.py` and are imported by 6 other modules. | DEFER to Phase 10 | None. |
| A5 | `Candle` does not check that open and close lie between low and high. | ACCEPT | FR6 now reads "…any candle with high < low, open or close outside [low, high], or a price <= 0". `Candle` rejects an open or close outside [low, high]. 6 new tests (4 rejections, 2 boundary values). A mutation check that removed the rule failed 4 tests. `requirements.md`, `crc.puml`, and the `domain-model.puml` ValidationRules note are updated. |
| A6 | The module `tools/models/signal.py` has the same name as the standard library `signal`. | REJECT | None. Reason: it would only shadow the standard library if a file inside `tools/models/` were run directly as a script. All entry points use `python -m` and package imports, and the demo and the full suite run cleanly. Revisit in Phase 10 if the module layout changes. |

## Observations

- `tools/confluence/score_confluence.py` picks bullish on a tie. `Signal` gives no direction instead, as decided. The pipeline tool was not changed.

## Known Bug: Separate Fix After Phase 05

| Item | Detail |
|---|---|
| Where | `tools/oanda/execute_trade.py`, `_units_from_lot` |
| Bug | `int(lot_size * 100_000)` truncates a floating-point product. 0.29 lots gives 28,999 units instead of 29,000 (also 0.57 and 0.58 lots). The order sent to OANDA practice is 1 unit short. |
| Model behavior | `Order.units()` uses `round()` and gives 29,000, covered by `test_fractional_lot_size_gives_exact_units`. |
| Why not fixed now | Phase 05 rules say pipeline tools outside `tools/models/` are not changed. |
| Plan | Fix in a separate change after Phase 05 is merged, with a test, following the Section 5 tool-failure steps in `AGENTS.md`. |

## Notes for Later Phases

| Phase | Note |
|---|---|
| After 05 | Fix the `_units_from_lot` truncation bug (see Known Bug). |
| 06 | **First item. Known FR9 gap (A1):** `TradePlan` checks the declared risk amount but not that the lot size produces it. Needs the stop-loss distance in pips and the pip value per lot (`tools/trade_plan/calculate_lot_size.py`). |
| 06 | With A1: `TradePlan` reference timeframe must be the highest timeframe that voted with the signal, H4 → H1 → M5 → M1 (A2, Workflow 04). Amend FR9 for A1 and A2 together. |
| 06 | Resolve the FR1 vs `detect_trend.py` conflict. |
| 06 | One-to-many relationships: CurrencyPair to Candle, SwingPoint, and TimeframeAnalysis; Account to Order and Trade; BacktestResult to TradeSetup and the same-pair rule (still deferred from Phase 02). |
| 06 | Decide whether `CurrencyPair.price_data` is replaced by candles. |
| 06 | Phase 04 finding 6 (`TradeSetup.__init__` and `StructureEvent.__init__` call an overridable method before a subclass's own state exists) is still open. |
| 06 | `BuySetup` and `SellSetup` remain a candidate for composition (Phase 04 finding 10). |
| 10 | Move the shared helpers out of `candle.py` into a module of their own (A4). Revisit the `signal.py` module name if the layout changes (A6). |

## AI Assistance

- Claude Code (Claude Opus 5.5) worked under `AGENTS.md`, which reserves engineering decisions for Daniel.
- Claude Code ran the start check and the v1 check, suggested interface options and domain candidates, reported conflicts, implemented only Daniel's decisions, synced the diagrams, and wrote this record.
- Claude Code committed `dcd948c` and created `phase-05-v1` at Daniel's request.

## End State

- `phase-05-v1` points to `dcd948c`, the interface before domain expansion. It is pushed to `origin/phase-05`.
- The domain expansion, the three added rules, the final review changes (A3, A5), the diagram sync, the README updates (Domain Model, Design Highlights, and the Phase 05 roadmap ✅), and this record are in the commit "Complete Phase 05 polymorphism, interfaces, and domain expansion", made after `phase-05-v1`. It was merged into `main` through a pull request and tagged `phase-05-completed`.
- No files outside `tools/models/`, `tests/models/`, `docs/`, and the README changed since `phase-04-completed`.

## Verification Confirmation
I personally inspected domain-model.puml, crc.puml, and use-cases.puml in IntelliJ and confirmed they match my approved Phase 05 decisions.
