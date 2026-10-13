# Workflow 06 — Run Backtest

## Objective
Replay historical candle data bar by bar, simulate every valid signal with full SL/TP logic, and output performance stats: win rate, average R, max drawdown, profit factor, and an equity curve.

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
|-------|---------|-------|
| `--pair` | required | e.g. EUR_USD |
| `--from-date` | required | YYYY-MM-DD |
| `--to-date` | required | YYYY-MM-DD |
| `--step` | 4 | H1 bars between analysis windows. Higher = faster. |

## How It Works

### Data
- Fetches H1 + H4 candles for the full date range (M1/M5 exceed OANDA's per-request limit for ranges > 1 week)
- Requires both H1 and H4 to agree (2/2) since M1/M5 are unavailable

### Replay
Steps through H1 candles from bar 50 onward (min warmup), advancing by `--step` bars per window. At each step, slices all candle data to the current timestamp — no lookahead bias.

### Signal logic
For each window:
1. Run full analysis (swings → structure → BOS/CHoCH → trend)
2. Score confluence — valid if both H1 + H4 agree
3. Build trade plan — entry at latest close, SL at last swing ± buffer
4. Gate: skip if RR < 2.0
5. Minimum 24 H1 bars between signals (prevents over-trading same structure)

### Outcome simulation
Scans forward 500 H1 bars to find the first event:
- `win`  — TP1 hit (2:1 R:R)
- `loss` — SL hit (-1R)
- `open` — neither hit within 500 bars (trade still running at end of data)

## Output
Results written to `.tmp/backtest/{run_id}_results.json` when triggered via API.

## Stats Calculated
| Metric | Description |
|--------|-------------|
| Win rate | % of closed trades that hit TP1 |
| Avg R | Mean R multiple across closed trades |
| Total R | Sum of all R multiples |
| Max drawdown | Largest peak-to-trough in cumulative R |
| Profit factor | Gross profit R / Gross loss R |
| Equity curve | Cumulative R after each closed trade |

## Interpreting "Open" Trades
"Open" means neither SL nor TP was reached within 500 H1 bars (~3 weeks). This happens when:
- The trade was entered late in the date range and the period ended before resolution
- The SL/TP targets are wide (H4-anchored setups can take weeks to resolve)
Open trades are excluded from win rate and profit factor calculations.

## Edge Cases
| Situation | How to Handle |
|-----------|--------------|
| Date range > 3 months | OANDA's H1 data still loads fine. H4 covers any range. |
| Not enough H1 candles (< 50) | Returns error — choose a longer date range |
| No signals found | Usually means both H1+H4 are ranging throughout. Try a trendier period. |
| All losses | Check if SL is too tight relative to H4 swing structure — widen lookback or check pair volatility |
