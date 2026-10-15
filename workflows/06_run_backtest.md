# Workflow 06 · Run Backtest

## Objective

Replay historical candles bar by bar, simulate every valid signal with full SL/TP logic, and report performance: win rate, average R, max drawdown, profit factor, and an equity curve.

## Pipeline Position

Runs on its own, usually on weekends via the scheduler. It reuses the logic from Workflows 02–04 on historical data.

## Requirements Trace

Traces to the functional requirement in `docs/design/requirements.md` for backtesting a strategy before using it on the demo account. Add the requirement IDs here once Phase 01 defines them.

## Permissions

| Activity | Agent |
|---|---|
| Run a backtest | Allowed |
| Change `--step`, warmup bars, the 24-bar spacing, or the 500-bar outcome window | Ask Daniel first |
| Change signal, SL, or TP logic just for backtesting | Ask Daniel first |
| Present results as a promise of future performance | **Never** |

---

## Tool

`tools/backtest/simulate_signals.py`

## Usage

```bash
python -m tools.backtest.simulate_signals \
  --pair EUR_USD \
  --from-date 2025-01-01 \
  --to-date 2025-06-30 \
  --step 4
```

## Parameters

| Param | Default | Notes |
|---|---|---|
| `--pair` | required | e.g. `EUR_USD` |
| `--from-date` | required | `YYYY-MM-DD` |
| `--to-date` | required | `YYYY-MM-DD` |
| `--step` | 4 | H1 bars between analysis windows. Higher = faster. |

---

## How It Works

### Data

- Fetches H1 and H4 candles for the full range. M1/M5 are skipped because they exceed OANDA's per-request limit for ranges over a week.
- Requires **H1 and H4 to agree (2/2)**, since M1/M5 aren't available.

### Replay

Steps through H1 candles from bar 50 (warmup), moving forward `--step` bars each window. At each step, all candle data is cut off at the current timestamp, so there's **no lookahead bias**.

### Signal logic (per window)

1. Run the full analysis (swings → structure → BOS/CHoCH → trend)
2. Score confluence: valid if H1 and H4 agree
3. Build the trade plan: entry at the latest close, SL at the last swing ± buffer
4. Skip if R:R < 2.0
5. Require at least 24 H1 bars between signals (prevents over-trading the same structure)

### Outcome simulation

Scans forward up to 500 H1 bars for the first event:

- **win**: TP1 hit (+2R)
- **loss**: SL hit (−1R)
- **open**: neither hit within 500 bars

---

## Steps

### 1. Run the backtest

Use the command in **Usage**.

### 2. Verify the output

- [ ] the run reports at least one signal (if not, see Edge Cases)
- [ ] win + loss + open = total signals
- [ ] win rate uses closed trades only
- [ ] the last equity curve value equals Total R

## Expected Output

Results are written to `.tmp/backtest/{run_id}_results.json` when triggered through the API.

| Metric | Description |
|---|---|
| Win rate | % of closed trades that hit TP1 |
| Avg R | Mean R multiple across closed trades |
| Total R | Sum of all R multiples |
| Max drawdown | Largest peak-to-trough drop in cumulative R |
| Profit factor | Gross profit R ÷ gross loss R |
| Equity curve | Cumulative R after each closed trade |

### Open trades

"Open" means neither SL nor TP was hit within 500 H1 bars (about 3 weeks). This happens when the trade started near the end of the range, or when H4-anchored targets are wide. Open trades are **excluded** from win rate and profit factor.

---

## Edge Cases

| Situation | How to handle |
|---|---|
| Range longer than 3 months | H1 still loads fine, and H4 covers any range. |
| Fewer than 50 H1 candles | Returns an error. Use a longer range. |
| No signals found | Usually H1 and H4 were ranging the whole time. Try a trendier period. |
| All losses | Check whether the SL is too tight for the H4 swing structure. Report it to Daniel before changing lookback. |

---

## Tests

- No tests exist yet. Add them in `tests/test_simulate_signals.py`.
- Use saved historical fixtures, never live OANDA.
- Cover: no lookahead (data after the current bar is never used), the 24-bar spacing, win/loss/open outcomes, every stat formula, and open trades excluded from win rate.

## Done When

The backtest completes and the stats pass every check in Step 2.

---

## Notes

- The backtest uses a **2/2 (H1 + H4)** rule, while live trading uses **3 of 4** timeframes. Backtest results don't exactly match the live strategy.
- Past performance doesn't guarantee future results.

## Change Log

| Date | Change | Why |
|---|---|---|
| | | |
