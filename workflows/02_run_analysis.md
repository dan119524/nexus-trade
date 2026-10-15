# Workflow 02 · Run Structural Analysis

## Objective

Run the full market structure analysis on a currency pair across all four timeframes: detect swing highs/lows, label HH/HL/LH/LL, identify BOS and CHoCH events, determine trend direction, and detect channels. Write the result to `.tmp/analysis/{pair}_analysis.json`.

## Pipeline Position

| Before | This workflow | After |
|---|---|---|
| 01 Fetch Candles | **02 Run Structural Analysis** | 03 Score Confluence |

## Requirements Trace

Traces to the functional requirements in `docs/design/requirements.md` covering market structure detection. Add the requirement IDs here once Phase 01 defines them.

## Permissions

| Activity | Agent |
|---|---|
| Run this workflow | Allowed |
| Re-run Workflow 01 if candle files are missing | Allowed |
| Change the swing `lookback`, minimum candle count, or trend rules | Ask Daniel first |
| Change how BOS/CHoCH are defined | Ask Daniel first |

---

## Prerequisite

Workflow 01 has been run. These files exist:

```
.tmp/candles/{pair}_M1.json
.tmp/candles/{pair}_M5.json
.tmp/candles/{pair}_H1.json
.tmp/candles/{pair}_H4.json
```

## Tool

`tools/analysis/run_analysis.py`

---

## Steps

### 1. Confirm candle files exist

Check that all 4 candle files are present and recent. If any are missing, run Workflow 01 first.

### 2. Run the analysis

```bash
python -m tools.analysis.run_analysis --pair EUR_USD
```

### 3. Verify the output

Confirm before continuing:

- [ ] `.tmp/analysis/EUR_USD_analysis.json` exists
- [ ] `timeframes` has entries for M1, M5, H1, H4
- [ ] each timeframe has `trend`, `swing_highs`, `swing_lows`, `structure`, `bos_events`, `choch_events`, `channel`
- [ ] `trend` is one of `"bullish"`, `"bearish"`, `"ranging"`
- [ ] at least 2 swing highs and 2 swing lows per timeframe (fewer means the data may be insufficient)

---

## Expected Output

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

---

## Edge Cases

| Situation | How to handle |
|---|---|
| Candle file missing | Skip that timeframe, log a warning, continue with the others. |
| Fewer than 20 candles | Skip the timeframe. Swing detection needs at least `lookback * 2 + 1` bars. |
| No swings detected | Likely a flat, low-volatility period. Channel empty, BOS/CHoCH empty, trend = `"ranging"`. |
| All 4 timeframes ranging | Workflow 03 will score 0 and produce no signal. No action needed. |

---

## Tests

- Tests live in `tests/test_detect_swings.py`. Add trend and BOS/CHoCH tests there or in a new `tests/test_run_analysis.py`.
- Use fixed candle fixtures with a known shape (a clear uptrend, a clear downtrend, a flat range, a BOS, a CHoCH).
- Cover: correct HH/HL/LH/LL labels, BOS and CHoCH detected on the right bar, trend result, skipped timeframe on too few candles.

## Done When

The analysis file exists and passes every check in Step 3.

---

## Notes

- The `lookback` window (default 5) confirms a swing after 5 bars form on each side, so there's always a 5-bar lag at the right edge of the chart.
- BOS and CHoCH events accumulate historically. Workflow 03 uses only the **most recent** event per timeframe.
- Re-running overwrites the previous analysis file on purpose, so the freshest data is always used.

## Change Log

| Date | Change | Why |
|---|---|---|
| | | |
