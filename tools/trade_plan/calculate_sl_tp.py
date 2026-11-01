"""
Calculate Stop Loss and Take Profit levels.

Stop Loss placement:
  - Bearish: SL above the most recent swing HIGH in the reference timeframe
             + a small buffer (default 2 pips above the swing).
  - Bullish: SL below the most recent swing LOW + buffer.

Take Profit:
  - TP1 = entry ± (SL distance × 2)   → 2:1 R:R
  - TP2 = entry ± (SL distance × 3)   → 3:1 R:R
"""

from tools.models.currency_pair import pip_size_for
from tools.utils.logger import get_logger

log = get_logger(__name__)

# Buffer added beyond the swing point (in price units, ~2 pips for majors)
DEFAULT_BUFFER = 0.00020


def calculate_sl_tp(
    entry: float,
    direction: str,
    swing_highs: list[dict],
    swing_lows: list[dict],
    pair: str = "EUR_USD",
    buffer: float = DEFAULT_BUFFER,
    rr_tp1: float = 2.0,
    rr_tp2: float = 3.0,
) -> dict:
    """
    Calculate SL, TP1, TP2 and derived risk metrics.

    Args:
        entry:       Entry price.
        direction:   "bullish" | "bearish"
        swing_highs: Swing high list from detect_swings() for the reference TF.
        swing_lows:  Swing low list.
        pair:        Instrument name (used for pip size).
        buffer:      Buffer beyond swing point in price units.
        rr_tp1:      Risk:reward ratio for TP1.
        rr_tp2:      Risk:reward ratio for TP2.

    Returns:
        Dict with stop_loss, take_profit_1, take_profit_2, sl_pips, rr.
    """
    pip = pip_size_for(pair)

    if direction == "bearish":
        # SL above the most recent swing HIGH
        if not swing_highs:
            raise ValueError("No swing highs available to place SL for bearish trade")
        relevant_swings = [s for s in swing_highs if s["price"] > entry]
        if not relevant_swings:
            # Never place a bearish SL below entry (FR2): skip the trade
            raise ValueError("No swing high above entry to place SL for bearish trade")

        swing_price = max(s["price"] for s in relevant_swings[-3:])
        sl = round(swing_price + buffer, 5)
        sl_distance = round(sl - entry, 5)
        tp1 = round(entry - (sl_distance * rr_tp1), 5)
        tp2 = round(entry - (sl_distance * rr_tp2), 5)

    elif direction == "bullish":
        # SL below the most recent swing LOW
        if not swing_lows:
            raise ValueError("No swing lows available to place SL for bullish trade")
        relevant_swings = [s for s in swing_lows if s["price"] < entry]
        if not relevant_swings:
            # Never place a bullish SL above entry (FR2): skip the trade
            raise ValueError("No swing low below entry to place SL for bullish trade")

        swing_price = min(s["price"] for s in relevant_swings[-3:])
        sl = round(swing_price - buffer, 5)
        sl_distance = round(entry - sl, 5)
        tp1 = round(entry + (sl_distance * rr_tp1), 5)
        tp2 = round(entry + (sl_distance * rr_tp2), 5)

    else:
        raise ValueError(f"Invalid direction: {direction}")

    sl_pips = round(abs(sl_distance) / pip, 1)
    # Measured R:R to TP1 from the returned prices, rounded to 2 decimals as TradePlan does (FR2)
    rr = round(abs(tp1 - entry) / abs(entry - sl), 2)

    result = {
        "stop_loss": sl,
        "take_profit_1": tp1,
        "take_profit_2": tp2,
        "sl_distance": sl_distance,
        "sl_pips": sl_pips,
        "risk_reward": rr,
    }

    log.info(
        f"SL={sl}  TP1={tp1}  TP2={tp2}  "
        f"SL_pips={sl_pips}  RR={rr}"
    )
    return result
