# Phase 07 Evolution Record: Evaluating Object-Oriented Design

## Starting State

- Phase 06 was merged into `main` through pull request #11 (merge commit `04e417f`) and tagged `phase-06-completed`.
- After Phase 06, five fixes were merged through pull requests #12 to #16 (lot size rounds down, minimum lot over the risk limit, practice-only OANDA clients, the 2% risk cap, and no fallback balance). They are recorded in `docs/evolution/phase-06.md` under "Fix After Phase 06".
- Before Phase 07 started, three test isolation fixes were merged (see below). After them, `pytest` gave 976 passed and 0 failed. The 2 known failures recorded in `docs/evolution/phase-02.md` were fixed by pull request #17.
- No Phase 07 guide exists in `docs/`. The README roadmap row ("Evaluating OO Design: design review notes in `docs/design/`") was used.
- The `workshop-07` branch was created from `main` at `17fbfcb`. The working tree was clean and in sync with `origin/main`. The branch name follows Daniel's request, not the `phase-NN` pattern in `AGENTS.md`.

## Test Isolation Fixes Before Phase 07

| PR | Branch | Commits | Change |
|---|---|---|---|
| #17 | `fix/mock-oanda-404-tests` | `dcb0f14`, `9d2b024` (merge `52cfc3c`) | `GET /candles/{pair}/{timeframe}` now runs `validate_pair_format` and `validate_granularity` before calling OANDA and returns 404 if either fails. OANDA's invalid-instrument `V20Error` (400) is mapped to 404, as Daniel decided; other OANDA errors stay 502. `test_get_candles_unknown_pair_404` and `test_get_candles_unknown_timeframe_404` mock the OANDA client. `test_get_candles_returns_list` and `test_get_candles_has_required_fields` use a fake OANDA client with fake candles and a `tmp_path` candle cache. This fixed the 2 known failures. |
| #18 | `fix/tmp-independent-tests` | `996a5b8` (merge `e33e90a`) | A `fake_tmp` fixture points `file_io._TMP` at `tmp_path` with a small EUR_USD signal, analysis, and candle file. The 8 signal, analysis, trade plan, and pairs tests use it. Their asserts are unchanged. |
| #19 | `fix/rr-gate-test` | `ddd35c6`, `786495b`, `a402c2a` (merge `17fbfcb`) | `fake_tmp` moved to `tests/conftest.py`. `test_get_all_signals_returns_list` and the 4 `FAKE_PAIR` 404 tests use it. `test_rr_gate_rejects_low_rr`, which had only checked "no signal file returns `None`", was rewritten: with `calculate_sl_tp` and `fetch_account` mocked, R:R 1.5 returns `None` and R:R 2.0 returns a plan. Notes in `requirements.md` and `workflows/04_generate_trade_plan.md` record that R:R was fixed at `rr_tp1 = 2.0`. |

After #19, a run with network connections blocked and `.tmp/` pointed at an empty directory gave 976 passed, with no network attempts and no test reading the real `.tmp/`.

## Design Review

Claude Code reviewed every class in `tools/models/` and every module in `tools/` for cohesion, coupling, and separation of concerns. The main finding: the 18 domain classes hold the trading rules, but no tool imports them, so the pipeline implements pip size, the reference timeframe order, the reward-to-risk minimum, and the buy and sell rules again.

Five modules were listed as doing too much: `build_trade_plan`, `calculate_sl_tp`, `weekly_cycle`, `server`, and `stream_prices`. Claude Code noted that the roadmap places refactoring in Phase 10. Daniel chose to refactor `calculate_sl_tp` in Phase 07 and plan the other four for Phases 08 to 10.

The review is recorded in `docs/design/phase-07-review.md`.

## Decisions

| Question | Decision |
|---|---|
| Which refactor | `calculate_sl_tp` only: use the shared pip size, and return the measured R:R instead of `rr_tp1`. SL and TP placement unchanged. `build_trade_plan`, `simulate_signals`, and other modules not changed. |
| How `calculate_sl_tp` gets the pip size, since it receives only a pair name | Add `pip_size_for(name)` in `currency_pair.py`. `CurrencyPair.pip_size` calls it. `TradeSetup` is not used yet, because it needs a `CurrencyPair` with price data. It comes with `TradePlanBuilder` in Phase 08. |
| SL fallback | While checking the refactor, Claude Code found that when no swing was beyond entry, `calculate_sl_tp` fell back to swings on the wrong side. A sell at 1.1050 with swing highs at 1.1000 and 1.1010 got SL 1.1012 below entry and TP1 1.1126 above it, still reported as R:R 2.0 (against FR2). Daniel decided to fix it: never place an SL on the wrong side of entry, and skip the trade. |
| How to skip | A `None` return would have needed changes in `build_trade_plan` and `simulate_signals` (which reads `sl_tp["risk_reward"]` outside its `try`). Daniel chose to raise `ValueError`: `simulate_signals` already catches it and skips the window, and the `weekly_cycle` scan catches it per pair. |
| Tag name | `phase-07-v1`, following the repo convention. |
| TP1 from market structure | Left open as a requirements decision for Daniel. |

## Implementation

Commit `8613a3e` ("Phase 07: measure R:R and use the shared pip size in calculate_sl_tp"), tagged `phase-07-v1`.

- `tools/models/currency_pair.py`: new `pip_size_for(name)`. It does not validate the name, so `calculate_sl_tp` accepts the same names as before. `CurrencyPair.pip_size` calls it.
- `tools/trade_plan/calculate_sl_tp.py`: `_pip_size` removed, `pip_size_for` used. `risk_reward` is measured from entry, SL, and TP1, rounded to 2 decimals as `TradePlan` does. With no swing beyond entry, it raises `ValueError` ("No swing high above entry…" or "No swing low below entry…"). The existing errors for an empty swing list are unchanged.
- `workflows/04_generate_trade_plan.md`: the "No swing high/low beyond entry" edge case now says the trade is skipped, the test coverage line no longer mentions the fallback, and the R:R note says the ratio is measured.
- `docs/design/requirements.md`: the R:R note says the ratio is measured and, for the fixed placement, always 2.00. No FR changed.

Commit `0774bd1` ("Add Phase 07 design review notes") added `docs/design/phase-07-review.md`.

## Tests

New tests in `tests/test_calculate_lot_size.py`:

- Measured R:R is 2.00 for bullish and bearish setups on EUR_USD and USD_JPY (4 cases).
- Measured R:R follows `rr_tp1=2.5`.
- A bearish setup with no swing high above entry raises `ValueError` (the 1.1050 example).
- A bullish setup with no swing low below entry raises `ValueError`.

`pytest` gave 983 passed and 0 failed in a normal run, with network blocked and `.tmp/` pointed at an empty directory, and with network blocked and the real `.tmp/` under access tracking. No test attempted a network connection or read the real `.tmp/`.

## Notes for Later Phases

| Phase | Note |
|---|---|
| 08 | `build_trade_plan` should build the existing `TradePlan` (`TradePlanBuilder`). `calculate_sl_tp` should use `TradeSetup` and `TradeDirection` instead of `bullish`/`bearish` branches. |
| 09 | `weekly_cycle` and `server` build their own OANDA clients. Move those calls into `tools/oanda/` (`OandaAdapter`, `TradingFacade`). |
| 10 | Move ranking in `weekly_cycle` to `rank_pairs` (FR4 conflict). Move the equity curve out of `server`. Move the pipeline loop and push notifications out of `stream_prices`. The reference timeframe order and the `MIN_RISK_REWARD` reads are still duplicated. |
| Open | Whether TP1 should come from market structure is a requirements decision. If it changes, R:R becomes variable and the gate starts rejecting setups. |
| Open | The `build_trade_plan` CLI exits with the `ValueError` when no swing is beyond entry, instead of reporting a skipped trade. |

## AI Assistance

- Claude Code (Claude Opus 5.5) worked under `AGENTS.md`, which reserves engineering decisions for Daniel.
- Claude Code merged pull requests #17 to #19 at Daniel's request, ran the test isolation audits, reviewed the design, reported the SL fallback bug and the conflicts between instructions, implemented only Daniel's decisions, and wrote this record.
- While finding the cause of the 502 in #17, Claude Code made one read-only candles request for `FAKE_PAIR` to the OANDA practice API outside the tests. It changed nothing on the account.
- Claude Code committed `8613a3e` and `0774bd1` and created `phase-07-v1` at Daniel's request.

## End State

- `phase-07-v1` points to `8613a3e`, the `calculate_sl_tp` refactor. It is pushed to `origin`.
- The review notes and this record were committed on `workshop-07` after `phase-07-v1`. This record was written before the merge. At Daniel's request, `workshop-07` is merged into `main` through a pull request and the merge commit is tagged `phase-07-completed`.
- Since the branch started at `17fbfcb`, the changed files are `tools/models/currency_pair.py`, `tools/trade_plan/calculate_sl_tp.py`, `tests/test_calculate_lot_size.py`, `workflows/04_generate_trade_plan.md`, `docs/design/requirements.md`, `docs/design/phase-07-review.md`, and this record. The README roadmap still shows Phase 07 as not done.

## Verification Confirmation

To be completed by Daniel.
