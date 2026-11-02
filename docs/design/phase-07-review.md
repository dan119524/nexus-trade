# Phase 07 Design Review: Cohesion, Coupling, and Separation of Concerns

This review looks at every class in `tools/models/` and every module in `tools/`, and records where responsibilities sit in the wrong place. It is a review of what is implemented on `workshop-07`. The "Planned" column marks suggested changes for later phases. It is not a description of current code.

## Overall Finding

The 18 domain classes in `tools/models/` are cohesive and loosely coupled. They hold the trading rules: the reward-to-risk minimum (`TradePlan`), the reference timeframe (`Signal`), pip size and pip value (`CurrencyPair`), the risk cap (`Account`), and buy and sell rules (`TradeDirection`).

No tool imports them. The pipeline in `tools/` works on dicts and implements the same rules again:

| Rule | Domain model | Duplicated in |
|---|---|---|
| Pip size | `CurrencyPair.pip_size` | `calculate_sl_tp` (fixed in Phase 07, see below) |
| Reference timeframe order H4, H1, M5, M1 | `Signal.reference_timeframe` | `build_trade_plan`, `email_report` |
| Minimum reward-to-risk of 2 | `TradePlan.MIN_REWARD_TO_RISK` | `MIN_RISK_REWARD` read in `build_trade_plan`, `simulate_signals`, `execute_trade`, `generate_summary` |
| Buy and sell price rules | `BuyDirection`, `SellDirection` | `bullish`/`bearish` branches in `calculate_sl_tp` |

## Modules That Do Too Much

| # | Module | Problem | Responsibility to move, and where | Status |
|---|---|---|---|---|
| 1 | `tools/trade_plan/build_trade_plan.py` | Orchestration, file reads and writes, an OANDA call (`fetch_account`), reference timeframe choice, the reward-to-risk gate, dict assembly, and the signal status update in one function. The rules duplicate `Signal` and `TradePlan`. | Build the existing `TradePlan`, which owns the rules. Signal, analysis, and balance are passed in by the caller instead of being read and fetched inside. | Phase 08: `TradePlanBuilder` added in `tools/models/`. Switching `build_trade_plan` to it is deferred to Phase 09, because it needs the pipeline dicts turned into domain objects. |
| 2 | `tools/trade_plan/calculate_sl_tp.py` | SL placement from swings, a fixed-multiple TP, its own pip size, and `bullish`/`bearish` branches that repeat `BuyDirection`/`SellDirection`. It returned the intended `rr_tp1` instead of the measured reward-to-risk. | Pip size from `currency_pair.py`. Reward-to-risk measured from prices. Direction rules from `TradeDirection`. | Partly done in Phase 07 (see below). `TradeSetup` and `TradeDirection` come with the `build_trade_plan` switch in Phase 09. |
| 3 | `tools/scheduler/weekly_cycle.py` | Scheduling, session and milestone state files, its own OANDA client (bypassing `tools/oanda/`), emails, and pair ranking that conflicts with FR4 (see Known Conflicts in `requirements.md`). | OANDA calls to `tools/oanda/`. Ranking to `rank_pairs`. Keep only the scheduling loop. | Planned for Phase 09 (`OandaAdapter`) and Phase 10 (ranking) |
| 4 | `tools/api/server.py` | 27 endpoints. The HTTP layer contains business logic (the equity curve) and builds its own OANDA pricing client. | Pricing to `tools/oanda/`. Equity curve to `tools/reporting/`. Endpoints only validate, delegate, and return. | Planned for Phase 09 (`OandaAdapter`, `TradingFacade`) and Phase 10 |
| 5 | `tools/oanda/stream_prices.py` | Named after a price stream, but it runs the whole pipeline (fetch, analysis, confluence, plan) and sends push notifications. The OANDA layer depends on the layers above it. | Pipeline loop to the scheduler (workflow 07). Push notifications to their own module. | Planned for Phase 10 |

A smaller case of the same kind is `tools/oanda/execute_trade.py`. It places the order and also writes the trade journal and sends email.

## Phase 07 Refactor: `calculate_sl_tp`

What was implemented on `workshop-07` (tag `phase-07-v1`):

- `pip_size_for(name)` in `tools/models/currency_pair.py` holds the pip size rule. `CurrencyPair.pip_size` and `calculate_sl_tp` both use it.
- `calculate_sl_tp` returns `risk_reward` measured from entry, SL, and TP1, rounded to 2 decimals as `TradePlan` does (FR2). With the fixed placement, TP1 at entry ± (SL distance × `rr_tp1`), it still measures exactly 2.00.
- An SL is never placed on the wrong side of entry (FR2). Before, when no swing was beyond entry, `calculate_sl_tp` fell back to swings on the wrong side. For example, a sell at 1.1050 got SL 1.1012 and TP1 1.1126, and was still reported as reward-to-risk 2.0. It now raises `ValueError`, and the trade is skipped. `simulate_signals` already catches the error and skips the window. The `weekly_cycle` scan catches it per pair.
- SL and TP placement are otherwise unchanged. `build_trade_plan` and `simulate_signals` are not changed.

`calculate_sl_tp` still uses `bullish`/`bearish` branches instead of `TradeSetup` and `TradeDirection`, because `TradeSetup` needs a `CurrencyPair` with price data. That comes with the `build_trade_plan` switch to `TradePlanBuilder`, deferred to Phase 09.

## Open Requirements Decision: TP1 From Market Structure

TP1 is a fixed multiple of the SL distance, so reward-to-risk is always 2.00 and the reward-to-risk gate only matters if `rr_tp1` changes or `MIN_RISK_REWARD` is set above 2. Whether TP1 should come from market structure (an opposing swing or liquidity level) is a trading-rule decision for Daniel. FR2 does not say how TP is chosen, and workflow 04 says TP1 = SL distance × 2.

If TP1 comes from structure:

- Reward-to-risk becomes variable, and the gate rejects real setups. Fewer plans are produced, and backtest results change, because `simulate_signals` uses the same `calculate_sl_tp` and its own gate.
- TP target selection becomes its own responsibility, separate from SL placement.
- The reward-to-risk minimum should live in one place (`TradePlan`). Every copy must round to 2 decimals before comparing, or a ratio such as 1.995 passes one gate and fails another.
- TP2 needs a rule too, because `TradePlan` requires TP2 beyond TP1.
- The decision goes into `requirements.md` before any code changes.
