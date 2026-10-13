# Workflow 02 — Run Structural Analysis

## Objective
Run the full market structure analysis on a currency pair across all four timeframes. Detects swing highs/lows, labels HH/HL/LH/LL, identifies BOS and CHoCH events, determines trend direction, and detects channels. Writes the result to `.tmp/analysis/{pair}_analysis.json`.

## Prerequisite
Workflow 01 must have been run first. `.tmp/candles/{pair}_M1.json`, `_M5.json`, `_H1.json`, `_H4.json` must all exist.

## Tool
`tools/analysis/run_analysis.py`

## Steps

### 1. Confirm candle files exist
Check that all 4 candle files are present and recent. If any are missing, run Workflow 01 first.

### 2. Run the analysis
```
python -m tools.analysis.run_analysis --pair EUR_USD
```

### 3. Verify the output
`.tmp/analysis/EUR_USD_analysis.json` should contain:
- `timeframes` key with entries for M1, M5, H1, H4
- Each timeframe has: `trend`, `swing_highs`, `swing_lows`, `structure`, `bos_events`, `choch_events`, `channel`
- `trend` is one of: `"bullish"`, `"bearish"`, `"ranging"`
- At least 2 swing highs and 2 swing lows per timeframe (if fewer, data may be insufficient)

## Expected Output Shape
```json
{
  "pair": "EUR_USD",
  "generated_at": "2025-01-15T17:00:00Z",
  "timeframes": {
    "H1": {
      "trend": "bullish",
      "swing_highs": [...],
      "swing_lows": [...],
      "structure": [...],
      "bos_events": [...],
      "choch_events": [...],
      "channel": { "channel_type": "ascending", "width": 0.011 }
    }
  }
}
```

## Edge Cases

| Situation | How to Handle |
|-----------|--------------|
| Candle file missing | Skip that timeframe, log a warning, continue with others |
| Fewer than 20 candles | Skip timeframe — swing detection needs at least `lookback * 2 + 1` bars |
| No swings detected | Likely a very flat/low-volatility period. Channel will be empty. BOS/CHoCH will be empty. Trend = "ranging". |
| All 4 timeframes ranging | Signal will score 0 — Workflow 03 will not produce a valid signal. No action needed. |

## Notes
- The lookback window (default 5) means swings are confirmed after 5 bars form on each side. There will always be a 5-bar lag on the right edge of the chart.
- BOS and CHoCH events accumulate historically — they are not filtered to "recent only". The confluence scorer (Workflow 03) uses only the most recent event per timeframe to cast its vote.
- Re-running this workflow overwrites the previous analysis file. This is intentional — always use the freshest data.
