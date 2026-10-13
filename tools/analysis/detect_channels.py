"""
Detect price channels using linear regression on swing highs and lows.

Uses numpy.polyfit on the last N swing points to compute:
  - Resistance trendline (from swing highs)
  - Support trendline    (from swing lows)

Channel type is determined by the average slope of the two lines.
"""

import numpy as np
from tools.utils.logger import get_logger

log = get_logger(__name__)


def detect_channels(
    swing_highs: list[dict],
    swing_lows: list[dict],
    lookback: int = 4,
) -> dict:
    """
    Fit trendlines through recent swing highs and lows.

    Args:
        swing_highs: Swing high points from detect_swings().
        swing_lows:  Swing low points from detect_swings().
        lookback:    Number of recent swings to use for regression.

    Returns:
        Channel dict, or empty dict if not enough swings.
    """
    recent_highs = swing_highs[-lookback:] if len(swing_highs) >= 2 else []
    recent_lows  = swing_lows[-lookback:]  if len(swing_lows)  >= 2 else []

    if not recent_highs or not recent_lows:
        log.info("Not enough swing points to detect a channel.")
        return {}

    res_slope, res_intercept = _fit_line(recent_highs)
    sup_slope, sup_intercept = _fit_line(recent_lows)

    avg_slope = (res_slope + sup_slope) / 2

    if avg_slope > 1e-5:
        channel_type = "ascending"
    elif avg_slope < -1e-5:
        channel_type = "descending"
    else:
        channel_type = "horizontal"

    # Approximate channel width in price units at the most recent bar
    last_bar = max(
        recent_highs[-1]["bar_index"],
        recent_lows[-1]["bar_index"],
    )
    res_price = res_slope * last_bar + res_intercept
    sup_price = sup_slope * last_bar + sup_intercept
    width = round(abs(res_price - sup_price), 5)

    channel = {
        "resistance_slope": round(res_slope, 8),
        "resistance_intercept": round(res_intercept, 5),
        "support_slope": round(sup_slope, 8),
        "support_intercept": round(sup_intercept, 5),
        "channel_type": channel_type,
        "width": width,
        "resistance_highs_used": [s["bar_index"] for s in recent_highs],
        "support_lows_used": [s["bar_index"] for s in recent_lows],
    }

    log.info(f"Channel: {channel_type}, width={width}")
    return channel


def _fit_line(swings: list[dict]) -> tuple[float, float]:
    x = np.array([s["bar_index"] for s in swings], dtype=float)
    y = np.array([s["price"]     for s in swings], dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    return float(slope), float(intercept)
