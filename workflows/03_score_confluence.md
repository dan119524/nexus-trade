# Workflow 03 · Score Confluence

## Objective

Cross-reference all 4 timeframes and produce a confluence score. Flag a setup only when at least 3 of 4 timeframes agree on direction. Write a signal stub to `.tmp/signals/` if valid.

## Pipeline Position

| Before | This workflow | After |
|---|---|---|
| 02 Run Structural Analysis | **03 Score Confluence** | 04 Generate Trade Plan |

## Requirements Trace

Traces to the functional requirement in `docs/design/requirements.md` for alerting only when at least 3 of 4 timeframes agree. Add the requirement IDs here once Phase 01 defines them.

## Permissions

| Activity | Agent |
|---|---|
| Run this workflow | Allowed |
| Re-run Workflow 02 if the analysis file is missing | Allowed |
| Change the voting table, weights, or `MIN_CONFLUENCE_SCORE` | Ask Daniel first |
| Continue to Workflow 04 when score < 3 | **Never** |

---

## Prerequisite

Workflow 02 has been run. `.tmp/analysis/{pair}_analysis.json` exists.

## Tool

`tools/confluence/score_confluence.py`

---

## Voting Logic

Each timeframe casts one vote: `bullish`, `bearish`, or `neutral`.

| Trend | Most recent BOS/CHoCH | Vote |
|---|---|---|
| bullish | bullish or none | bullish |
| bullish | bearish | neutral |
| bearish | bearish or none | bearish |
| bearish | bullish | neutral |
| ranging | bullish | bullish |
| ranging | bearish | bearish |
| ranging | none | neutral |

**Score** = number of timeframes matching the majority direction (max 4). A signal is valid only if **score ≥ 3**.

Timeframe weights (M1 = 1, M5 = 1, H1 = 2, H4 = 3) are informational only. The raw count is the validity gate.

---

## Steps

### 1. Run the scorer

```bash
python -m tools.confluence.score_confluence --pair EUR_USD
```

### 2. Read the output

The scorer prints each timeframe's vote and the final score. If valid, it writes `.tmp/signals/EUR_USD_signals.json`.

### 3. Verify the output

- [ ] each of the 4 votes matches the voting table for that timeframe's analysis
- [ ] `score` equals the number of votes matching the majority direction
- [ ] `signal_valid` is `true` only when `score ≥ min_score_required`

### 4. If there's no valid signal

Score < 3 means the timeframes disagree. Log it and **stop**. Do not run Workflow 04. Re-run Workflows 01–03 after the next candle close.

---

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

---

## Edge Cases

| Situation | How to handle |
|---|---|
| Analysis file missing | Log the error and stop. Run Workflow 02 first. |
| All 4 timeframes neutral | Score 0, no signal. Expected in low volatility. |
| 2/2 split (e.g. M1 + M5 bullish, H1 + H4 bearish) | Score 2, invalid. Log and stop. |
| Score exactly 3 | Valid. Continue to Workflow 04. |
| Score 4/4 | Strong signal. Continue to Workflow 04. |

---

## Tests

- Tests live in `tests/test_score_confluence.py`.
- Use fixed analysis fixtures, not live data.
- Cover **every row** of the voting table, plus: 4/4, 3/4, 2/2 split, all neutral, and a custom `MIN_CONFLUENCE_SCORE`.

## Done When

Either a valid signal file is written with a score ≥ 3, or the run is logged as invalid and the pipeline stops.

---

## Notes

- The signal file is a stub at this stage. `trade_plan` and `summary` stay `null` until Workflows 04 and 05 fill them in.
- Re-running overwrites the previous signal file.
- `MIN_CONFLUENCE_SCORE` is set in `.env`. Default is 3.

## Change Log

| Date | Change | Why |
|---|---|---|
| | | |
