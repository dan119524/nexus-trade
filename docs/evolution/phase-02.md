# Phase 02 Evolution Record: From Design to Objects

## Starting State

- Phase 01 was merged into `main` through pull request #3 (merge commit `72a4d44`) and tagged `phase-01-completed`.
- The `phase-02` branch was created from that commit.
- The baseline was the Phase 01 design in `docs/design/requirements.md` and the three diagrams in `docs/design/uml/`: 3 entities (`CurrencyPair`, `TradeSetup`, `BacktestResult`), 4 use cases, and 5 functional requirements. `domain-model.puml` showed the classes by name only.
- `tools/models/` did not exist. `README.md` listed it in the project tree as `# Candle, Instrument, Signal, Trade, Account...`.

## From Design to Classes

The initial implementation is commit `0774262` ("Complete Phase 02 initial implementation"), tagged `phase-02-v1`. It added one file per entity in `tools/models/`, plus `__init__.py` and `demo.py`, and changed the README tree line to `# CurrencyPair, TradeSetup, BacktestResult`.

Each CRC responsibility became stored state or a method that uses only the object's own data:

| Class | CRC responsibility | Implementation |
|---|---|---|
| `CurrencyPair` | Know its name | `_name`, an OANDA-style name such as `EUR_USD` |
| | Know its past price data | `_price_data`, a tuple of `(high, low)` float tuples, the only data FR1 needs |
| | Know its current market structure | `market_structure()` calculates it from `_price_data` instead of storing it |
| `TradeSetup` | Know which currency pair it belongs to | `_pair_name`, a string, not a `CurrencyPair` object |
| | Know its direction, entry price, stop loss, and take profit | `_direction`, `_entry`, `_stop_loss`, `_take_profit` |
| | Know its reward-to-risk ratio | `reward_to_risk()` returns reward divided by risk |
| `BacktestResult` | Know which currency pair was tested | `_pair_name`, a string |
| | Know which trade setups were tested | `_setups_tested`, a count only (see finding 4) |
| | Know its number of trades and its win rate | `_trade_count`, `_win_count`, and `win_rate()`, which returns `None` for zero trades |
| | (no CRC line) | `_test_date`, a `datetime.date` |

- Every attribute is private and exposed as a read-only `@property`. No class has a setter.
- Every `__init__` raises `ValueError` on bad data. FR2's buy and sell price order is enforced in `TradeSetup.__init__`. FR2's minimum reward-to-risk of 2 is not enforced.
- No class holds or calls another class. The Phase 01 relationships are represented only by the `pair_name` string. No inheritance, interfaces, or design patterns were used.
- `currency_pair.py` defined `validate_pair_name`, which `trade_setup.py` and `backtest_result.py` import. Each of `currency_pair.py` and `trade_setup.py` had its own copy of a private `_to_price` helper.
- `demo.py` creates two or three objects of each class, calls every property and method, and builds one invalid buy setup inside `try/except`. It uses fixed data and does not call the OANDA API.

## Known Test Failures

Daniel recorded two existing API tests as known failures from before Phase 01. They are not caused by Phase 02 work.

| Test | Expected | Actual |
|---|---|---|
| `tests/test_api_endpoints.py::test_get_candles_unknown_pair_404` | 404 for `/candles/FAKE_PAIR/H1` | 502 |
| `tests/test_api_endpoints.py::test_get_candles_unknown_timeframe_404` | 404 for `/candles/EUR_USD/D1` | 502 |

**Evidence:**

- `tests/test_api_endpoints.py` and `tools/api/server.py` have not changed since the repository's first commit (`e4b62a2`), and are identical at `phase-00-completed`.
- No code outside `tools/models/` imports `tools.models`.
- In the first full `pytest` run of Phase 02, these were the only failures: 87 passed, 2 failed.

**Likely cause (requirement → test → code):**

- No requirement in `docs/design/requirements.md` covers the API endpoints. The tests come from code written before Phase 01.
- The tests expect 404 for an unknown pair or an unsupported timeframe.
- The candles endpoint does not validate the pair or timeframe. When no cached file exists, it tries to fetch from OANDA and returns 502 when that fails. Both tests therefore cause a fetch attempt against the OANDA practice API.

The code and the tests were left unchanged. The Phase 02 guide forbids changes to existing tools, and `AGENTS.md` forbids changing a test only because the code fails it. After review finding 8, the Phase 02 guide requires "no new test failures" instead of every test passing.

## AI Assistance

- Claude Code (Claude Opus 5.5) worked under `AGENTS.md`, which reserves engineering decisions for Daniel.
- Claude Code ran the Phase 02 engineering review against `phase-02-v1` without modifying files. It read the required files, diffed the branch against `main`, ran the demo and `pytest`, and probed edge cases with throwaway scripts. It reported 16 numbered findings: 8 real problems and 8 optional ideas.
- Daniel decided every finding. Claude Code applied only the ACCEPT and MODIFY decisions and recorded the deferrals.
- At Daniel's request, Claude Code then removed a check that had become unreachable, changed the remaining test rules in the Phase 02 guide, and committed and pushed the result.
- Claude Code ran the diagram sync, reported where requirements and code disagree without choosing, and wrote the `tests/models/` tests.

## Engineering Review

Daniel's decisions and the resulting changes are below. The ACCEPT and MODIFY changes, the deferral notes, and the follow-up changes are in commit `ef0d3fd` ("Apply Phase 02 engineering review"). DEFER, "note for sync", and "no action" decisions without a recorded note appear only in this record.

**Real problems**

| # | Finding | Decision | Change made |
|---|---|---|---|
| 1 | An empty iterator got past the "price data must not be empty" check. | ACCEPT | `_validate_price_data` turns the input into a tuple before checking it. |
| 2 | NaN and infinity were accepted as prices. | ACCEPT | The price helper rejects non-finite numbers, for `CurrencyPair` and `TradeSetup`. |
| 3 | `market_structure()` raised `ValueError` for fewer than 2 points, where FR1 says "anything else is ranging". | MODIFY | `CurrencyPair.__init__` requires at least 2 price points. |
| 4 | `BacktestResult` stores a count of setups tested, not which setups were tested (CRC: "Know which trade setups were tested"). | DEFER to Phase 03 | None. Holding `TradeSetup` objects is object collaboration, which starts in Phase 03. |
| 5 | Pair names had to be `EUR_USD`, but `requirements.md` used "EUR/USD". | MODIFY | `requirements.md` uses `EUR_USD` in the Domain Entities table and the `CurrencyPair` CRC card. |
| 6 | `BacktestResult` accepted more trades than setups tested. | ACCEPT | `__init__` raises `ValueError` when trade count is greater than setups tested. |
| 7 | The demo buy setup's reward-to-risk is `1.9999999999999556`, which prints as `2.00`. FR2's minimum of 2 is not enforced. | DEFER | None. The minimum stays unenforced in Phase 02. When it is enforced, reward-to-risk is rounded to 2 decimals before comparing with 2. |
| 8 | The guide required every existing test to pass, but the 2 known failures remain, and those tests cause OANDA fetch attempts, against `AGENTS.md` section 9. | MODIFY | Phase 02 guide section 2 requires "no new test failures". The 2 pre-existing failures stay recorded. |

**Optional ideas**

| # | Finding | Decision | Change made |
|---|---|---|---|
| 9 | `_to_price` was duplicated in `currency_pair.py` and `trade_setup.py`. | ACCEPT | It became public `to_price` in `currency_pair.py`, imported by `trade_setup.py` the same way as `validate_pair_name`. |
| 10 | `trade_setup.py` and `backtest_result.py` import `validate_pair_name` from `currency_pair.py`. | Note for sync | Shown in `domain-model.puml` during the sync. |
| 11 | Price points must be tuples, so lists are rejected. | DEFER | None. |
| 12 | Non-iterable price data raised `TypeError`, not `ValueError`. | ACCEPT | It raises `ValueError`. |
| 13 | FR1 was implemented strictly: every point must make both a higher (or lower) high and low. | ACCEPT | FR1 in `requirements.md` states the strict rule, and any equal high or low counts as ranging. |
| 14 | `test_date` is a date, so two backtests on the same day cannot be ordered. | DEFER | None. |
| 15 | The evolution record was started in section 2, not section 8. | No action | None. |
| 16 | `domain-model.puml` still showed the classes by name only. | No action | Handled by the sync. |

**Follow-up changes in `ef0d3fd`:**

- The `len < 2` check in `market_structure()` was removed, because `__init__` now guarantees at least 2 points.
- Phase 02 guide sections 7 and 9 now say "no new test failures" instead of "every test passes" and "all of `pytest` passes".

## Diagram Sync

- **`domain-model.puml`:**
  - The header comment now names `tools/models/` as the source of attributes and methods.
  - Each class lists its private attributes (`-`) with types, its `+ __init__(...)`, its read-only properties (`+`), and its public method.
  - A new note, "SharedHelpers", shows `validate_pair_name` (used by all three classes) and `to_price` (used by `CurrencyPair` and `TradeSetup`) as functions in `currency_pair.py`.
  - The three associations, their multiplicities, and the same-pair note were not changed.
- **`crc.puml`:** "EUR/USD" became "EUR_USD". No responsibilities changed.
- **`use-cases.puml`:** unchanged, because no actor goal changed.
- Claude Code could not run PlantUML's syntax check, because PlantUML is not installed in its environment.

Claude Code reported five points where requirements and code disagree. It did not choose. Daniel decided each one:

| # | Disagreement | Decision | Change made |
|---|---|---|---|
| D1 | The three associations are in the requirements and the diagram, but the code holds no object references, only `pair_name` strings. The same-pair rule is not enforced. | DEFER to Phase 03 | `domain-model.puml` has a note on the associations: "linked by pair_name only; object references and same-pair check in Phase 03". |
| D2 | "Know which trade setups were tested" is stored only as a count (deferred as finding 4). | Closed as a duplicate of finding 4 | None. |
| D3 | `BacktestResult` stores `test_date` and `win_count`, which no CRC card lists. FR4's "most recent" implies a date but does not state it. | ACCEPT | The `BacktestResult` CRC card in `requirements.md` and `crc.puml` adds "Know when the test was run" and "Know the number of wins". FR4 is unchanged. |
| D4 | The validation rules, such as the name format, at least 2 points, finite positive prices, high ≥ low, and wins ≤ trades ≤ setups tested, are not stated in `requirements.md`. The buy and sell price order comes from FR2. | ACCEPT | `domain-model.puml` has a "Validation rules" note listing them as design decisions. |
| D5 | FR2's minimum reward-to-risk of 2 is not enforced (deferred as finding 7). | DEFER, same as finding 7 | None. |

## Tests

`tests/models/` adds 91 tests across four files. They use only fixed data and public properties and methods, and they do not call the OANDA API. No existing test was changed.

| File | Tests | Coverage |
|---|---|---|
| `__init__.py` | — | Empty. Matches `tests/__init__.py`. |
| `test_currency_pair.py` | 37 | Stored values; invalid names; fewer than 2 points, including from an iterator; non-iterable data; malformed points; NaN, infinity, prices ≤ 0, strings, and bools; high below low; uptrend, downtrend, and 5 ranging cases, including equal highs and lows |
| `test_trade_setup.py` | 32 | Stored values for buy and sell; invalid names; wrong direction; NaN, infinity, prices ≤ 0, strings, and bools; wrong price order for buy and sell, including equal prices; `reward_to_risk()` for buy (3.0), sell (3.0), and below 2 (0.5, returned, not rejected) |
| `test_backtest_result.py` | 22 | Stored values, all-zero counts, and equal counts; invalid names and dates; negative and non-whole counts; wins greater than trades; trades greater than setups tested; `win_rate()` of 0.6, 0.0, 1.0, and `None` for zero trades |

> **Note:** The per-file counts were corrected in Phase 03. They originally read 33, 30, and 28. The total of 91 was correct.

Results: `tests/models/` gives 91 passed. The full suite gives 178 passed and 2 failed, and the 2 failures are the known failures above.

## End State

- `phase-02-v1` points to commit `0774262`, the implementation before review.
- `ef0d3fd`, the reviewed state, is pushed to `origin/phase-02`.
- Commit `16e791d` ("Auto-save 2026-10-16 15:22"), also pushed to `origin/phase-02`, contains the diagram sync (`domain-model.puml`, `crc.puml`), the `tests/models/` tests, and a version of this record. Claude Code did not create that commit.
- No files in `tools/` outside `tools/models/` changed since `phase-01-completed`.

## Verification Confirmation
I personally inspected the affected PlantUML diagrams (domain-model.puml and crc.puml) in IntelliJ and confirmed they match my approved Phase 02 decisions.
