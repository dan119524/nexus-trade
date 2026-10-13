# Workflow 05 — Generate Trade Summary

## Objective
Call the Claude API to generate a plain English explanation of the trade setup: why it's valid, what would invalidate it, and what to watch while the trade is active. Attach the summary to the signal file.

## Prerequisite
- Workflows 01-04 complete: signal exists with `status: "active"` and a populated `trade_plan`
- `ANTHROPIC_API_KEY` set in `.env`
- Confluence score ≥ 3 AND R:R ≥ 2.0 (enforced automatically — API not called otherwise)

## Tool
`tools/ai/generate_summary.py`

## Steps

### 1. Run the summary generator
```
python -m tools.ai.generate_summary --pair EUR_USD
```

### 2. Verify output
The signal file at `.tmp/signals/{pair}_signals.json` should now have:
- `status: "ready"`
- `summary` field with three sections: SUMMARY, INVALIDATION, LESSON

## Expected Output Format
```
SUMMARY:
EUR/USD is showing bearish confluence across 3 of 4 timeframes, with M1, M5,
and H4 all printing Lower Highs and Lower Lows. The H4 timeframe recently broke
structure to the downside with a confirmed BOS at 1.1560, shifting the higher
timeframe bias firmly bearish. Price is currently consolidating just below the
broken structure level, offering a high-probability short entry near 1.1539
with a defined risk point above the last H4 swing high.

INVALIDATION:
Setup is cancelled if price closes above 1.1642 on the H4 timeframe, which
would reclaim the broken structure level and invalidate the bearish bias.

LESSON:
Watch for a lower timeframe CHoCH back to the upside on M5 as an early warning
sign that sellers are losing control before the SL is hit.
```

## Cost Control
The API is only called when **both** conditions are met:
- `confluence.signal_valid == true` (score ≥ 3)
- `trade_plan.risk_reward >= 2.0`

This prevents API spend on setups that would be rejected anyway.

Each call uses approximately 500-700 output tokens (~$0.002 per summary at current rates).

## Edge Cases

| Situation | How to Handle |
|-----------|--------------|
| `ANTHROPIC_API_KEY` missing | Raises `EnvironmentError`. Add key to `.env`. |
| No trade_plan on signal | Logs error, returns None. Run Workflow 04 first. |
| Signal not valid | Logs warning, skips API call. |
| API rate limit / timeout | Let the exception propagate. Retry manually — don't loop automatically. |
| Summary is empty or garbled | Log it and retry once. If still bad, proceed without summary. |

## Notes
- The summary is informational only. It does not affect the trade plan numbers.
- The model used is `claude-opus-4-6` for the highest quality reasoning about market structure.
- Re-running this workflow overwrites the previous summary. Useful if market conditions have changed.
