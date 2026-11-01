# Workflow 04 · Generate Trade Plan

## Objective

Build a complete trade plan for a valid confluence signal: entry, stop loss, take profit levels, R:R, and lot size based on account balance and risk %. Attach the plan to the signal file, gated on R:R ≥ 2.

## Pipeline Position

| Before | This workflow | After |
|---|---|---|
| 03 Score Confluence | **04 Generate Trade Plan** | 05 Generate Trade Summary |

## Requirements Trace

Traces to the functional requirements in `docs/design/requirements.md` covering trade plans, position sizing, and the R:R ≥ 2 rule. Add the requirement IDs here once Phase 01 defines them.

## Permissions

| Activity | Agent |
|---|---|
| Run this workflow on the **practice** account | Allowed |
| Use `--risk` up to 2% | Allowed only when Daniel asks for it |
| Change SL buffer, TP multiples, reference TF priority, lot caps, `RISK_PERCENT`, or `MIN_RISK_REWARD` | Ask Daniel first |
| Risk more than 2% per trade | **Never** |
| Write a plan with R:R < 2.0 | **Never** |
| Place an order from this plan | **Never** (this workflow only plans) |

---

## Prerequisites

- Workflow 03 produced a valid signal (`signal_valid: true`, score ≥ 3)
- `.tmp/signals/{pair}_signals.json` exists with `status: "pending_trade_plan"`
- `.tmp/analysis/{pair}_analysis.json` exists
- `.tmp/candles/{pair}_{ref_tf}.json` exists
- OANDA practice credentials set in `.env` (for the balance fetch)

## Tool

`tools/trade_plan/build_trade_plan.py`

---

## Steps

### 1. Run the generator

```bash
python -m tools.trade_plan.build_trade_plan --pair EUR_USD
```

With a custom risk %:

```bash
python -m tools.trade_plan.build_trade_plan --pair EUR_USD --risk 1.5
```

### 2. Verify the output

The signal file should now have `status: "active"` and a filled `trade_plan`. Confirm:

- [ ] stop loss is on the correct side of entry (bearish: SL > entry, bullish: SL < entry)
- [ ] `risk_reward` ≥ 2.0
- [ ] `lot_size` is not 0.01 or 100.0 (those are the safety caps)
- [ ] `risk_percent` ≤ 2.0
- [ ] `account_balance` is the real practice balance (there is no fallback; a failed fetch writes no plan)

Only continue to Workflow 05 if every box is checked, since the summary costs an API call.

---

## Trade Plan Logic

**Entry:** latest close of the reference timeframe (market order approach).

**Reference timeframe:** the highest timeframe that voted with the signal direction, in priority order H4 → H1 → M5 → M1.

**Stop loss**
- Bearish: 2 pips above the most recent swing **high** above entry
- Bullish: 2 pips below the most recent swing **low** below entry

**Take profit**
- TP1 = entry ± (SL distance × 2) → 2:1 R:R
- TP2 = entry ± (SL distance × 3) → 3:1 R:R

**Lot size**

```
risk_amount   = account_balance × (risk_percent / 100)
pip_value/lot = $10 for USD-quote pairs (EUR_USD, GBP_USD, etc.)
lot_size      = risk_amount / (sl_pips × pip_value_per_lot)
```

---

## Expected Output

```json
{
  "trade_plan": {
    "pair": "EUR_USD",
    "direction": "bearish",
    "reference_timeframe": "H4",
    "entry_price": 1.08320,
    "stop_loss": 1.08590,
    "take_profit_1": 1.07780,
    "take_profit_2": 1.07240,
    "sl_pips": 27.0,
    "risk_reward": 2.0,
    "lot_size": 0.19,
    "risk_amount_usd": 50.00,
    "risk_percent": 1.0,
    "account_balance": 5000.0,
    "confluence_score": 3,
    "invalidation_note": "Setup invalid if price closes above 1.08590."
  }
}
```

---

## Edge Cases

| Situation | How to handle |
|---|---|
| No valid signal | Script logs an error and returns `None`. Run Workflows 01–03 first. |
| No swing high/low beyond entry | Fall back to the 3 most recent swings of the correct type. |
| R:R < 2.0 | Reject the setup. Log a warning. Don't write a plan. Wait for a better setup. |
| Account fetch fails, or balance is 0 or less | Reject the setup. Log an error. Don't write a plan. Check the OANDA practice credentials in `.env`, then rerun. |
| Lot size hits 0.01 or 100 cap | Log a warning. SL is too wide, or the account is too small or large for the size. |

> **Note on the R:R < 2.0 row:** the reward-to-risk ratio is currently fixed at `rr_tp1 = 2.0`. `build_trade_plan` calls `calculate_sl_tp` with its default `rr_tp1`, and `calculate_sl_tp` places TP1 at entry ± (SL distance × `rr_tp1`) and returns `risk_reward = rr_tp1`. The gate therefore only matters if `rr_tp1` changes or `MIN_RISK_REWARD` is set above 2. `test_rr_gate_rejects_low_rr` mocks `calculate_sl_tp` to test the gate itself. Whether TP1 and the ratio should come from market structure instead is open for Workshop 07.

---

## Tests

- Tests live in `tests/test_calculate_lot_size.py`. Add plan-level tests in a new `tests/test_build_trade_plan.py`.
- Use fixed signal, analysis, and candle fixtures, plus a fixed account balance. Never call OANDA.
- Cover: SL side for bullish and bearish, TP1/TP2 math, R:R < 2 rejection, lot size formula, lot caps, reference TF priority, the swing fallback, and risk % above 2 being refused.

## Done When

Either the signal has `status: "active"` with a plan that passes every check in Step 2, or the setup is logged as rejected and the pipeline stops.

---

## Notes

- `RISK_PERCENT` and `MIN_RISK_REWARD` are set in `.env`.
- Never risk more than 2% per trade. Default is 1%.
- The lot size formula assumes a USD account and a USD-quote pair. Other pairs need a different pip value.

## Change Log

| Date | Change | Why |
|---|---|---|
| | | |
