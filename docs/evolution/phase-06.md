# Phase 06 Evolution Record: Growing the Object Model

## Starting State

- Phase 05 was merged into `main` through pull request #9 (merge commit `ddfba2e`) and tagged `phase-05-completed`.
- After Phase 05, the `_units_from_lot` truncation fix was merged through pull request #10 (`a130675`, merge commit `30a057e`).
- The `phase-06` branch was created from `main` at `30a057e`. The Phase 06 start check reported PHASE-05 COMPLETION: VERIFIED and PHASE-06 START CHECK: PASS, with one deviation that Daniel accepted: the branch starts one merge after `phase-05-completed` (the units fix), because the guide also says to branch from a clean, synced `main`.
- At the start, `pytest` gave 433 passed and 2 failed, the 2 known failures recorded in `docs/evolution/phase-02.md`.
- Items deferred to Phase 06: A1 and A2 (Phase 05 final review), R3, Phase 02 finding 4, the same-pair rule and its same-object-or-same-name question (Phases 02–03), the FR1 vs `detect_trend.py` conflict, replacing `CurrencyPair.price_data` with candles, Phase 04 finding 6, the `BuySetup`/`SellSetup` refactor (Phase 04 finding 10), the remaining one-to-many relationships, and the README's planned `Chart`.

## Part 1: Composition and Collection (Section 2)

### Decisions

Claude Code suggested three options for each task. Daniel decided:

| Task | Decision |
|---|---|
| Task 1 | Remove `BuySetup` and `SellSetup`. Add a `TradeDirection` interface (ABC), implemented by `BuyDirection` and `SellDirection`, that supplies the price-order check, reward, risk, outcome, the "beyond" comparison, and the units sign. `TradeSetup` becomes concrete, constructed as `TradeSetup(pair, direction, entry, stop_loss, take_profit)`, and delegates to its direction. `setup.direction` still returns "buy" or "sell". `TradePlan`, `Order`, and `Trade` use the direction object instead of branching on strings. `evaluate_setup` keeps working. `requirements.md` first; Daniel approved changing "TradeSetup is an ABC". |
| Task 2 | `BacktestResult` keeps a private `list[TradeSetup]` with add, get (a tuple), and remove. It accepts only a `TradeSetup` whose pair is the same object (`is`) and that it does not already hold. Setups tested, trades, and wins come from each setup's `outcome()`. Open setups are excluded from trades and the win rate. "At most one backtest result" stays documented only. |

This closed R3, Phase 02 finding 4, the same-pair rule (as same object), and Phase 04 findings 6 (for setups) and 10.

### Implementation

Commit `4ea0bf4` ("Complete Phase 06 composition and collection"), tagged `phase-06-v1` ("Phase 06 before domain-wide review").

- `requirements.md`: Domain Entities rows and CRC cards for `TradeDirection`, `BuyDirection`, and `SellDirection`. The Inheritance and Interfaces tables changed, and a "Composition over Inheritance" section explains the limitation and the improvement. The `BacktestResult` card and the relationship notes describe the collection.
- New `trade_direction.py`, `buy_direction.py`, and `sell_direction.py`. `buy_setup.py` and `sell_setup.py` were deleted.
- `trade_setup.py`: concrete `TradeSetup` with `trade_direction` (the object) and `direction` (its name). The direction exists before the price-order check runs.
- `trade_plan.py` uses `is_beyond` for TP2; `order.py` and `trade.py` use `units_sign`.
- `backtest_result.py`: `BacktestResult(pair, test_date)` with `add_setup`, `remove_setup`, `setups`, and derived counts. The unused `_to_count` helper was removed.
- Tests: `test_trade_setup.py` converted to the new constructor, `test_backtest_result.py` rewritten (the count-validation tests no longer applied), new `test_trade_direction.py`.
- `demo.py`: "Composition" and "Collection" sections; the EUR_USD backtest holds 3 setups.
- A mutation check (same-pair by name, no duplicate check, open counted as a trade, list exposed, no TP2 check, sell units sign flipped) failed tests every time.

The Phase 06 v1 check reported PHASE-06 V1: READY. `pytest` gave 447 passed and the 2 known failures.

## Part 2: Domain-Wide Object Model Review (Section 4)

### Recommendations and Decisions

Claude Code reviewed the whole domain and grouped 11 recommendations. While checking FR4, it found that `tools/scheduler/weekly_cycle.py` ranks pairs by a composite score, not by win rate. Daniel decided:

| # | Recommendation | Level | Decision |
|---|---|---|---|
| R1 | A1: `TradePlan` should derive its risk from lot size × stop-loss pips × pip value, not trust a declared risk amount (FR9 gap). | Must-fix 🔒 | ACCEPT. Pip size and pip value on `CurrencyPair`, rules from `calculate_lot_size.py`. Strict, no tolerance (later: risk rounded to cents before comparing, see below); the tool should round lot size down, as a separate fix after Phase 06. Reject cross pairs until a real conversion exists. Require a USD account. Derive `risk_amount` instead of taking it as input. |
| R2 | A2: reference timeframe should be the highest agreeing timeframe. | Optional 🔒 | ACCEPT. `Signal` works it out (H4 → H1 → M5 → M1), and `TradePlan` uses it instead of a parameter. FR9 amended once for R1 and R2. |
| R3 | FR1 vs `detect_trend.py`. | Must-fix (decide) | Option (a): FR1 stays pair-level. New FR12: a timeframe's trend comes from its swing labels as computed by the analysis tool. Removed from Known Conflicts. |
| R4 | Replace `CurrencyPair.price_data` with candles. | Optional | KEEP the tuples. Reason: no requirement needs a pair to hold candles, and replacing them would ripple through FR1, `outcome()`, and every fixture. Closed. |
| R5 | Move the direction choice from `TradePlan` to `Signal`. | Optional | ACCEPT. `Signal.trade_direction()` returns a `BuyDirection`, a `SellDirection`, or `None`. |
| R6 | Account → Trade (FR11). | Must-fix | ACCEPT option (a): `Account` holds a private `list[Trade]`; an open trade is closed by replacing it with the closed `Trade` for the same order, so `Trade` stays immutable. |
| R7 | CurrencyPair → BacktestResult (for FR4). | Must-fix | ACCEPT. Most recent = added last. |
| R8 | CurrencyPair → Candle, and `Chart`. | Optional | REJECT. Reason: no requirement needs it. `Chart` removed from the README. |
| R9 | Other one-to-many relationships. | Optional | KEEP one-way and document it in `requirements.md`. |
| R10 | FR4 ranking is not implemented anywhere. | Must-fix 🔒 | Option (a): implement FR4 as written; ties keep input order; record the conflict with `weekly_cycle.py`. |
| R11 | `StructureEvent` subclasses. | Optional | KEEP the inheritance. Close Phase 04 finding 6 for `StructureEvent`: it is safe because `BreakOfStructure` and `ChangeOfCharacter` have no state of their own. |

### Requirements

Updated first, and shown to Daniel as a diff before any code:

- FR9 amended for R1 and R2: reference timeframe, risk = lot size × stop-loss pips × pip value, USD account, no cross pairs.
- New FR12 (timeframe trend from swing labels).
- New sections "Pip Size and Pip Value" and "Ranking".
- Known Conflicts: the FR1 row was replaced by a resolution note. Two new rows: FR4 vs `weekly_cycle.py`, and `calculate_lot_size` rounding vs strict FR9.
- Model Rules: which one-to-many relationships are stored as lists, and that the others are deliberately one-way.
- CRC: `CurrencyPair` (pip size, pip value, backtests), `Signal` (trade direction object, reference timeframe), `TimeframeAnalysis` (FR12), `TradePlan` (derived risk, USD, cross pairs, reference timeframe), `Account` (trades), and a `rank_pairs` card.
- Relationships: `Account records Trade` (`1` to `0..*`, aggregation); the CurrencyPair–BacktestResult association is two-way; the deliberately one-way relationships are listed.

### Implementation

| File | Change |
|---|---|
| `currency_pair.py` | `pip_size()`, `pip_value_per_lot(price)` (USD-quote 10.0; USD_JPY 1,000 / price; other USD-base 10 / price, both rounded to 4 decimals; anything else raises `ValueError`). A private `list[BacktestResult]` with `add_backtest`, `remove_backtest`, `backtests` (tuple), and `latest_backtest()`. Module function `rank_pairs(pairs)`. `BacktestResult` is imported inside `add_backtest`, because `backtest_result.py` imports `currency_pair.py`. |
| `signal.py` | `trade_direction()` returns a direction object or `None`. New `reference_timeframe()`. |
| `trade_plan.py` | Constructor is `TradePlan(signal, account, entry, stop_loss, take_profit_1, take_profit_2, lot_size)`. Requires a USD account. New `stop_loss_pips` (risk / pip size, rounded to 1 decimal). `risk_amount` is computed in `__init__` and must be at most the account's maximum. `reference_timeframe` comes from the signal. No more string branch. |
| `account.py` | A private `list[Trade]` with `add_trade`, `remove_trade`, `close_trade(open_trade, closed_trade)`, `trades` (tuple), `open_trades()`, and `closed_trades()`. `Trade` is imported inside the methods, because `trade.py` imports `order.py`, which imports `account.py`. |
| `__init__.py` | Exports `rank_pairs`. |
| `demo.py` | Signal reference timeframe and direction class; the plan's risk calculation; new "Account records its Trades" and "CurrencyPair holds its BacktestResults; rank_pairs" sections; rejected cases for a $500-risk plan and a cross pair. |
| `README.md` | Domain Model lists the 18 classes in `tools/models/` (`BuySetup`, `SellSetup`, and `Chart` removed; `TradeDirection`, `BuyDirection`, `SellDirection` added). Design Highlights show inheritance, the `TradeDirection` interface, composition and delegation, and collections. |

- Fixture change: a 1.0-lot plan with a 50-pip stop risks $500, so the `buy_plan` and `sell_plan` fixtures use 0.1 and 0.05 lots ($50 and $25). `test_order.py` expectations changed to 10,000 and −5,000 units, and the 0.29-lot test uses a $20,000 account.
- A mutation check removed or changed each new rule: a 1-cent risk tolerance, no USD check, an approximate cross pair, a wrong JPY pip value, the reference timeframe lowest-first, latest = first added, the unranked group reversed, the backtest pair compared by name, no trade-account check, no same-order check on close, and close appending instead of replacing in place. Every one failed tests.
- During the mutation check, one same-size edit restored within the same second left a stale Python bytecode file, which made later runs show 8 extra failures. The bytecode cache was cleared, and every mutation was rerun with bytecode writing off. The counts above come from that clean run.

### Diagram Sync

- **`domain-model.puml`:** synced to the Phase 06 code.
  - `TradeSetup` is concrete. `TradeDirection` is an abstract class with `{abstract}` members, and `BuyDirection` and `SellDirection` have generalization arrows to it.
  - `BuySetup` and `SellSetup` were removed.
  - The collections are private `list[...]` attributes with tuple getters.
  - New arrows: `TradeSetup --> TradeDirection`, `CurrencyPair -- BacktestResult` (two-way), `BacktestResult o--> TradeSetup` (now implemented), and `Account o--> Trade`.
  - The notes were updated for associations, helpers (including `rank_pairs`), constants, and validation rules. The Signal label now matches the requirements wording ("combines (as m1, m5, h1, h4)").
  - A script compared all 17 class boxes with the code (attributes, properties, methods, abstract members, and visibility), the generalization arrows, and the enum. All matched. It also compared the 17 relationship rows in `requirements.md` with the 17 diagram arrows (classification, label, and multiplicities), and all matched.
- **`crc.puml`:** generated from the CRC tables in `requirements.md` by a script, so its 18 cards (including `rank_pairs`) match the requirements exactly.
- **`use-cases.puml`:** unchanged, because no actor goal changed.
- All three files pass PlantUML's `-checkonly`.

### Risk Rounded to Cents

Daniel decided after the object model report that `TradePlan` rounds its computed risk to cents (2 decimals) before comparing it with `account.max_risk_amount()`, so floating-point noise cannot reject an exactly-at-limit plan. A risk one cent or more over the limit is still rejected.

- `trade_plan.py`: `risk_amount` is `round(lot_size × stop_loss_pips × pip_value, 2)`.
- `test_trade_plan.py`:
  - The test that expected 0.15 lots of USD_JPY with a 50-pip stop to be rejected now expects it to pass, at $50.00 (the requirement changed).
  - A new test rejects a plan one cent over: $50.00 against a $49.99 maximum.
  - The USD_JPY and USD_CAD risk assertions expect cents ($33.33 and $36.76).
- A mutation check that removed the rounding failed 3 tests.
- `requirements.md` (Pip Size and Pip Value, the TradePlan CRC card, Known Conflicts), `crc.puml` (regenerated), and the `domain-model.puml` notes say the risk is rounded to cents.

## Final Review

Claude Code ran the Phase 06 final review and check without committing. It reported PHASE-06: PASSED. All ten required items passed:

- The remaining one-to-many relationships use typed collections with add, get, and remove.
- Inheritance was evaluated and improved where justified.
- Placeholder behavior was replaced (FR4, FR9, FR11).
- Phase 03–05 work is preserved.
- Requirements, CRC, and the domain model match the code.
- `pytest` gave 522 passed and the 2 known failures, and the demo ran.
- This record exists.
- `phase-06-v1` is on the remote.
- No patterns, persistence, or service layers were added.
- There are no secrets in the diff.

The scope item passed with one exception that Daniel confirmed: `README.md` is outside `tools/models/`, `tests/`, `docs/`, and `phases/`, but its changes were directed by Daniel (R8 and the README sync).

Claude Code confirmed each advisory finding with a throwaway script. Daniel accepted all four:

| # | Finding | Decision | Change made |
|---|---|---|---|
| A1 | `Account` recorded both an open and a winning `Trade` for one order, so the order counted twice. | ACCEPT | One recorded trade per order. `_check_new_trade` rejects a trade whose order already has a recorded trade; `close_trade` passes the open trade as `replacing`, so it is the only way to replace one. 2 new tests (one trade per order, 3 cases; removing a trade frees its order). The existing account tests now give each trade its own order (the requirement changed). The demo's second trade uses its own order and shows the new rejection. |
| A2 | A plan with lot size 0.000001 was accepted, and its order had 0 units. | ACCEPT | `TradePlan` requires a lot size of at least 0.01 in steps of 0.01 (`LOT_STEP`), with a 1e-9 float tolerance on the step check (0.07 × 100 = 7.000000000000001). 10 new test cases. The minimum also catches a lot so small it rounds to 0 steps (1e-12). |
| A3 | A backtest dated 2026-10-01 added after one dated 2026-10-15 became the "most recent". | ACCEPT | `CurrencyPair.add_backtest` rejects a result dated earlier than its latest. Same-day and later results are accepted. 3 new tests. |
| A4 | `rank_pairs` ranked a pair passed twice twice. | ACCEPT | `rank_pairs` raises `ValueError` for a pair passed more than once (the same object). 2 new tests (including different pair objects with the same name, which are allowed). |

- A mutation check removed or changed each rule: no one-per-order check, `close_trade` blocked by its own order, no step check, no minimum, an exact float comparison, no date check, same day rejected, no duplicate check, duplicates compared by name. Every one failed tests.
- `requirements.md` (Pip Size and Pip Value, Ranking, the CurrencyPair, TradePlan, Account, and `rank_pairs` CRC cards, and the relationship notes), `crc.puml` (regenerated), and `domain-model.puml` (the validation rules, the `LOT_STEP` constant, and the `_check_new_trade` signature) are updated.

## Tests

| File | `phase-05-completed` | `phase-06-v1` | Now |
|---|---|---|---|
| `test_currency_pair.py` | 37 | 37 | 82 |
| `test_trade_setup.py` | 63 | 65 | 65 |
| `test_trade_direction.py` | — | 10 | 10 |
| `test_backtest_result.py` | 25 | 27 | 27 |
| `test_candle.py` | 50 | 50 | 50 |
| `test_swing_point.py` | 16 | 16 | 16 |
| `test_structure_event.py` | 19 | 19 | 19 |
| `test_timeframe.py` | 2 | 2 | 2 |
| `test_timeframe_analysis.py` | 20 | 20 | 20 |
| `test_signal.py` | 21 | 21 | 30 |
| `test_account.py` | 27 | 27 | 46 |
| `test_trade_plan.py` | 21 | 21 | 42 |
| `test_order.py` | 12 | 12 | 12 |
| `test_trade.py` | 31 | 31 | 31 |

The tests use fixed data and fake account IDs and never call OANDA or the Claude API.

Results: `tests/models/` gives 452 passed. The full suite gives 541 passed and 2 failed, and the 2 failures are the known failures recorded in `docs/evolution/phase-02.md`.

## Observations

- As first built, `TradePlan` compared its raw risk with the account maximum, so floating point could reject an exactly-at-limit plan: 0.15 lots × 50 pips × 6.6667 = 50.00025 for USD_JPY. See "Risk Rounded to Cents" below.
- `tools/scheduler/weekly_cycle.py` ranks pairs differently from FR4 (recorded in Known Conflicts). The tool was not changed.
- `tools/trade_plan/calculate_lot_size.py` could round a lot size up past the account maximum. The tool was not changed during Phase 06; it was fixed afterwards (see "Fix After Phase 06").

## Fix After Phase 06: Lot Size Rounds Down

| Item | Detail |
|---|---|
| Where | `tools/trade_plan/calculate_lot_size.py`, `calculate_lot_size` |
| Bug | `round(raw_lots, 2)` rounded to the nearest 0.01, so a lot could round up past the risk limit. For example, 0.996 lots became 1.00. `TradePlan` (R1) would reject such a plan. |
| Fix | Made after Phase 06 on branch `fix/lot-round-down`, merged into `main` through a pull request. The lot size is `math.floor(raw_lots * 100 + 1e-9) / 100`, which always rounds down. The tiny tolerance keeps exact values such as 0.29 (0.29 × 100 = 28.999999999999996) from dropping a step. The 0.01 minimum and 100 maximum caps are unchanged. |
| Tests | `tests/test_calculate_lot_size.py`: 0.996 becomes 0.99; 0.07, 0.29, 0.57, and 0.58 stay exact; and the rounded lot's risk never exceeds the limit across 360 combinations of pair (EUR_USD, USD_JPY, USD_CAD), balance, risk percent, and stop-loss pips. With the old rounding, 187 of the new tests fail. |
| Minimum lot | At first the 0.01 minimum cap was kept, so when even 0.01 lots risked more than the limit, the tool still forced 0.01 and exceeded it. A second fix after Phase 06 (branch `fix/lot-min-over-risk`, merged through a pull request) changed this: `calculate_lot_size` logs a warning and returns `None` (no trade), and `build_trade_plan` logs "Setup rejected" and returns `None` without writing a plan, the same way it handles a low R:R. `test_lot_size_minimum_cap` now expects `None` (the requirement changed). New tests: a $50 account with a 20-pip stop gives no trade; a minimum lot exactly at the limit is still a trade; a normal account is unchanged; and `build_trade_plan` (with fixed files and a fake account, no OANDA) writes no plan for a tiny account but still writes a 0.09-lot plan for a $10,000 account. Without the new guard, `build_trade_plan` crashed with `TypeError`. |
| Records | The Known Conflicts row in `requirements.md` became a resolution note. |

## Fix After Phase 06: Practice-Only OANDA Clients

| Item | Detail |
|---|---|
| Where | `tools/oanda/fetch_candles.py`, `fetch_account.py`, `fetch_instruments.py`, and `execute_trade.py` (`_build_client`); `tools/scheduler/weekly_cycle.py` (`_check_trade_milestones`); `tools/api/server.py` (`/prices`) |
| Bug | Each client used `"live" if env == "live" else "practice"`, so `OANDA_ENV=live` (or `--env live`) connected to the live environment, against FR5. Only order execution and trade closing refused live. |
| Fix | Made after Phase 06 on branch `fix/practice-only-env`. A new `require_practice_env(env)` in `tools/utils/validators.py` raises `EnvironmentError` for anything except `"practice"`. Every client calls it before building its `API`, and every `API` is built with `environment="practice"`. The API's existing broad `except` turns the refusal into a 502. The unused `validate_env` helper also allowed `"live"`; it now accepts `"practice"` only, so it can't be reused to allow live. |
| Tests | `tests/test_practice_only_env.py` (40 tests, mocks and fake keys only, no OANDA): the check refuses `live`, `LIVE`, `Practice`, an empty string, and `fxtrade`; each `_build_client` refuses them without building an `API` and builds a practice `API` otherwise; `fetch_candles`, `fetch_account`, and `fetch_instruments` refuse `live`; `weekly_cycle` and `/prices` build no client under `OANDA_ENV=live` and a practice client otherwise; `validate_env` accepts `"practice"` and rejects the same five values. Against the old code, 29 of the 40 fail. |
| Records | A resolution note was added under Known Conflicts in `requirements.md`. |

## Fix After Phase 06: Risk Percent Capped at 2%

| Item | Detail |
|---|---|
| Where | `tools/trade_plan/calculate_lot_size.py`, `calculate_lot_size` |
| Bug | The tool accepted a risk percent up to 10, but FR9 and `Account` cap it at 2. A `RISK_PERCENT` or `--risk` above 2 sized a trade past the limit. |
| Fix | Made after Phase 06 on branch `fix/risk-cap-2pct`. A new `_MAX_RISK_PERCENT = 2.0` replaces the 10, and a risk percent above it raises `ValueError` ("must be greater than 0 and at most 2"). `build_trade_plan` does not catch it, so no plan is written. The unused `validate_risk_percent` helper in `tools/utils/validators.py` also allowed up to 10; it now caps at 2 as well. |
| Tests | `tests/test_calculate_lot_size.py`: exactly 2% is allowed (0.50 lots on $5,000 over 20 pips); 2.01, 2.5, 3, 5, and 10 are rejected; `build_trade_plan` with 3% raises and leaves the signal file unchanged; and `validate_risk_percent` allows 0.5, 1, and 2 and rejects 0, -1, 2.01, 3, and 10. `test_lot_size_maximum_cap` used 10% to reach the 100-lot cap; it now uses 2%, which still reaches the cap (20,000 lots before capping), because 10% breaks FR9. Against the old code, 11 of the 15 new tests fail. |
| Records | A resolution note was added under Known Conflicts in `requirements.md`. |

## Fix After Phase 06: No Fallback Balance

| Item | Detail |
|---|---|
| Where | `tools/trade_plan/build_trade_plan.py`, `build_trade_plan` |
| Bug | When `fetch_account()` raised, or returned a balance of 0 or less, the tool logged a warning and sized the trade against a $10,000 balance. The plan's lot size and risk then had nothing to do with the real account (FR9). |
| Fix | Made after Phase 06 on branch `fix/no-fallback-balance`. Both cases now log "Setup rejected" as an error and return `None` without writing a plan, the same way the tool handles a low R:R or a minimum lot over the limit. |
| Tests | `tests/test_calculate_lot_size.py`, with the fixed files and fake account from the minimum-lot fix: a fetch that raises `EnvironmentError`, `ConnectionError`, or `KeyError` writes no plan and leaves the signal file unchanged; a balance of 0, 0.0, or -50 does the same; and a failed fetch never reaches `calculate_lot_size`. The existing $10,000 test still writes a 0.09-lot plan. Against the old code, all 7 new tests fail. |
| Records | A resolution note was added under Known Conflicts in `requirements.md`. The checklist and the "Account fetch fails" edge case in `workflows/04_generate_trade_plan.md` no longer describe the fallback. |

## Notes for Later Phases

| Phase | Note |
|---|---|
| After 06 | Fixed: `calculate_lot_size` rounds the lot size down (see "Fix After Phase 06"). |
| 10 | Move the shared helpers out of `candle.py` (Phase 05 A4). Revisit the `signal.py` module name if the layout changes (Phase 05 A6). The two in-method imports (`Account` → `Trade`, `CurrencyPair` → `BacktestResult`) exist only to avoid circular imports and may change with the module layout. |
| Still open | Phase 02 finding 11 (price points must be tuples) and finding 14 (same-day backtests). Finding 14 is now handled for FR4 by "most recent = added last". |

## AI Assistance

- Claude Code (Claude Opus 5.5) worked under `AGENTS.md`, which reserves engineering decisions for Daniel.
- Claude Code ran the start check and the v1 check, suggested options, reviewed the domain, reported conflicts, implemented only Daniel's decisions, synced the diagrams and README, and wrote this record.
- Claude Code committed `4ea0bf4` and created `phase-06-v1` at Daniel's request.
- Claude Code ran the final review and check, applied only the advisory changes Daniel accepted, and prepared the merge at his request.

## End State

- `phase-06-v1` points to `4ea0bf4`, the composition and collection work before the domain-wide review. It is pushed to `origin/phase-06`.
- The Section 4 changes, the risk rounding, the final review changes (A1–A4), the diagram sync, the README updates (Domain Model, Design Highlights, and the Phase 06 roadmap ✅), and this record are in the commit "Complete Phase 06 growing the object model", made after `phase-06-v1`. It was merged into `main` through a pull request and tagged `phase-06-completed`.
- Since the branch started at `30a057e`, no files outside `tools/models/`, `tests/models/`, `docs/`, and the README changed. Daniel confirmed the README exception.

## Verification Confirmation
I personally inspected domain-model.puml and crc.puml in IntelliJ and confirmed they match my approved Phase 06 decisions.
