# Workflow 05 · Generate Trade Summary

## Objective

Call the Claude API to write a plain-English explanation of the trade setup: why it's valid, what would invalidate it, and what to watch while the trade is active. Attach the summary to the signal file.

## Pipeline Position

| Before | This workflow | After |
|---|---|---|
| 04 Generate Trade Plan | **05 Generate Trade Summary** | 07 Monitor Pairs (notification) |

## Requirements Trace

Traces to the functional requirement in `docs/design/requirements.md` for a plain-English summary of each setup. Add the requirement IDs here once Phase 01 defines them.

## Permissions

| Activity | Agent |
|---|---|
| Run once for a signal that passes both gates | Allowed |
| Retry once after an empty or garbled summary | Allowed |
| Retry after a rate limit or timeout | Ask Daniel first (paid call) |
| Change the model, prompt, or output sections | Ask Daniel first |
| Call the API for a signal that fails a gate | **Never** |
| Loop API calls automatically | **Never** |

---

## Prerequisites

- Workflows 01–04 are complete: the signal has `status: "active"` and a filled `trade_plan`
- `ANTHROPIC_API_KEY` is set in `.env`
- Confluence score ≥ 3 **and** R:R ≥ 2.0 (checked automatically; the API isn't called otherwise)

## Tool

`tools/ai/generate_summary.py`

---

## Steps

### 1. Run the generator

```bash
python -m tools.ai.generate_summary --pair EUR_USD
```

### 2. Verify the output

The signal file should now have:

- [ ] `status: "ready"`
- [ ] a `summary` field with three sections: `SUMMARY`, `INVALIDATION`, `LESSON`
- [ ] price levels in the summary that match the `trade_plan` numbers

---

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

---

## Cost Control

The API is only called when both are true:

1. `confluence.signal_valid == true` (score ≥ 3)
2. `trade_plan.risk_reward >= 2.0`

This avoids spending on setups that would be rejected anyway. Each call uses about 500–700 output tokens.

---

## Edge Cases

| Situation | How to handle |
|---|---|
| `ANTHROPIC_API_KEY` missing | Raises `EnvironmentError`. Add the key to `.env`. |
| No `trade_plan` on the signal | Logs an error, returns `None`. Run Workflow 04 first. |
| Signal not valid | Logs a warning, skips the API call. |
| Rate limit or timeout | Let the exception propagate. Retry manually; never loop. |
| Summary empty or garbled | Log it and retry once. If still bad, continue without a summary. |

---

## Tests

- No tests exist yet. Add them in `tests/test_generate_summary.py`.
- **Never call the real Claude API in tests.** Use a fake client that returns a fixed response.
- Cover: API skipped when score < 3, API skipped when R:R < 2, missing key error, missing trade plan, parsing the three sections, the single retry on a garbled response.

## Done When

The signal has `status: "ready"` with all three summary sections, or the run is logged as skipped or failed and the plan continues without a summary.

---

## Notes

- The summary is informational only. It never changes the trade plan numbers.
- The model is set in `tools/ai/generate_summary.py`. Check that it's still a current model before relying on it.
- Re-running overwrites the previous summary, which is useful when conditions change.

## Change Log

| Date | Change | Why |
|---|---|---|
| | | |
