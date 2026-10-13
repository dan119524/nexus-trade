# Workflow 03 — Score Confluence

## Objective
Cross-reference all 4 timeframes and generate a confluence score. Only flag setups where at least 3 of 4 timeframes agree on direction. Write a signal stub to `.tmp/signals/` if valid.

## Prerequisite
Workflow 02 must have been run. `.tmp/analysis/{pair}_analysis.json` must exist.

## Tool
`tools/confluence/score_confluence.py`

## Voting Logic

Each timeframe casts one vote: `"bullish"`, `"bearish"`, or `"neutral"`.

| Trend | Most Recent BOS/CHoCH | Vote |
|-------|----------------------|------|
| bullish | bullish or none | bullish |
| bullish | bearish | neutral |
| bearish | bearish or none | bearish |
| bearish | bullish | neutral |
| ranging | bullish event | bullish |
| ranging | bearish event | bearish |
| ranging | none | neutral |

Score = number of timeframes matching the majority direction (max 4).
**Signal is only valid if score ≥ 3.**

Timeframes also carry weights (M1=1, M5=1, H1=2, H4=3) for informational purposes, but the raw count (≥3) is the validity gate.

## Steps

### 1. Run the scorer
```
python -m tools.confluence.score_confluence --pair EUR_USD
```

### 2. Read the output
The scorer prints each timeframe's vote and the final score. If valid, it writes to `.tmp/signals/EUR_USD_signals.json`.

### 3. If no valid signal
Score < 3 means the timeframes disagree. Log it and stop. Do not proceed to Workflow 04. Come back after the next candle close and re-run Workflows 01-03.

## Expected Output (valid signal)
```json
{
  "id": "EUR_USD_20250115_1700",
  "pair": "EUR_USD",
  "status": "pending_trade_plan",
  "confluence": {
    "score": 3,
    "max_score": 4,
    "direction": "bullish",
    "votes": { "M1": "bullish", "M5": "bullish", "H1": "bullish", "H4": "neutral" },
    "dissenting_timeframes": [],
    "neutral_timeframes": ["H4"],
    "signal_valid": true,
    "min_score_required": 3
  },
  "trade_plan": null,
  "summary": null
}
```

## Edge Cases

| Situation | How to Handle |
|-----------|--------------|
| Analysis file missing | Log error, stop. Run Workflow 02 first. |
| All 4 timeframes neutral | Score = 0, no signal. Expected in low-volatility periods. |
| 2/2 split (e.g. M1+M5 bullish, H1+H4 bearish) | Score = 2, invalid. Log and stop. |
| Score exactly 3 | Valid. Proceed to Workflow 04. |
| Score 4/4 | Strong signal. Proceed to Workflow 04. |

## Notes
- The signal file at `.tmp/signals/` is a stub at this stage. `trade_plan` and `summary` are `null` until Workflows 04 and 05 populate them.
- Re-running this workflow overwrites the previous signal file.
- The `MIN_CONFLUENCE_SCORE` threshold is configurable in `.env`. Default is 3.
