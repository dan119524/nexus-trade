# Workflow 04 — Generate Trade Plan

## Objective
Build a complete trade plan for a valid confluence signal: entry price, stop loss, take profit levels, R:R ratio, and lot size based on account balance and risk %. Attach the plan to the signal file and gate it on R:R ≥ 2.

## Prerequisite
- Workflow 03 produced a valid signal (`signal_valid: true`, score ≥ 3)
- `.tmp/signals/{pair}_signals.json` exists with `status: "pending_trade_plan"`
- `.tmp/analysis/{pair}_analysis.json` exists
- `.tmp/candles/{pair}_{ref_tf}.json` exists
- OANDA credentials set in `.env` (for account balance fetch)

## Tool
`tools/trade_plan/build_trade_plan.py`

## Steps

### 1. Run the trade plan generator
```
python -m tools.trade_plan.build_trade_plan --pair EUR_USD
python -m tools.trade_plan.build_trade_plan --pair EUR_USD --risk 1.5
```

### 2. Verify output
The signal file at `.tmp/signals/{pair}_signals.json` should now have `status: "active"` and a populated `trade_plan` object.

Check:
- `stop_loss` is on the correct side of `entry_price`
  - Bearish: SL > entry
  - Bullish: SL < entry
- `risk_reward` ≥ 2.0
- `lot_size` is reasonable (not 0.01 or 100.0 — those are the safety caps)

## Trade Plan Logic

### Entry
Latest close of the reference timeframe candle (market order approach).

### Reference Timeframe Selection
The highest timeframe that voted with the signal direction is used for SL placement:
Priority order: H4 → H1 → M5 → M1

### Stop Loss
- **Bearish**: SL placed 2 pips above the most recent swing HIGH above entry
- **Bullish**: SL placed 2 pips below the most recent swing LOW below entry

### Take Profit
- **TP1** = entry ± (SL distance × 2) → 2:1 R:R
- **TP2** = entry ± (SL distance × 3) → 3:1 R:R

### Lot Size
```
risk_amount     = account_balance × (risk_percent / 100)
pip_value/lot   = $10 for USD-quote pairs (EUR_USD, GBP_USD, etc.)
lot_size        = risk_amount / (sl_pips × pip_value_per_lot)
```

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

## Edge Cases

| Situation | How to Handle |
|-----------|--------------|
| No valid signal | Script logs error and returns None. Run Workflows 01-03 first. |
| No swing highs/lows above/below entry | Falls back to the 3 most recent swings of the correct type |
| RR < 2.0 | Setup rejected. Log warning. Do not write trade plan. Wait for a better setup. |
| Account fetch fails | Falls back to $10,000 balance. Log a warning. |
| Lot size rounds to 0.01 or hits 100 cap | Log warning — SL is too wide or account is too small/large for the calculated size |

## Notes
- `RISK_PERCENT` and `MIN_RISK_REWARD` are configurable in `.env`
- Never risk more than 2% per trade. Default is 1%.
- The lot size formula assumes a USD-denominated account. For non-USD accounts, pip values need adjustment.
- Always confirm the trade plan makes sense before proceeding to Workflow 05 (summary generation costs an API call).
