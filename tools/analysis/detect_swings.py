"""
Detect swing highs and swing lows from a candle list.

Algorithm: pivot-point with a configurable lookback window n.
A bar at index i is a swing high if its high is the maximum of the
window [i-n : i+n+1].  Same logic inverted for swing lows.

The n-bar lag is intentional — swings are only confirmed once n bars
have formed on the right side.  This makes signals non-repainting.
"""

import pandas as pd
import numpy as np
from tools.utils.logger import get_logger

log = get_logger(__name__)


def detect_swings(
    candles: list[dict],
    lookback: int = 5,
) -> dict[str, list[dict]]:
    """
    Detect swing highs and lows from a candle list.

    Args:
        candles:  List of normalized candle dicts (must have 'high', 'low', 'time').
        lookback: Number of bars required on each side to confirm a swing.

    Returns:
        {"highs": [swing_point, ...], "lows": [swing_point, ...]}
        Each swing_point: {type, price, time, bar_index, confirmed}
    """
    if len(candles) < lookback * 2 + 1:
        log.warning(
            f"Not enough candles ({len(candles)}) to detect swings with lookback={lookback}. "
            f"Need at least {lookback * 2 + 1}."
        )
        return {"highs": [], "lows": []}

    highs = np.array([c["high"] for c in candles])
    lows  = np.array([c["low"]  for c in candles])
    n = len(candles)

    swing_highs = []
    swing_lows  = []

    for i in range(lookback, n - lookback):
        window_h = highs[i - lookback : i + lookback + 1]
        window_l = lows[i  - lookback : i + lookback + 1]

        if highs[i] == window_h.max() and list(window_h).count(highs[i]) == 1:
            swing_highs.append({
                "type": "high",
                "price": round(highs[i], 5),
                "time": candles[i]["time"],
                "bar_index": i,
                "confirmed": True,
            })

        if lows[i] == window_l.min() and list(window_l).count(lows[i]) == 1:
            swing_lows.append({
                "type": "low",
                "price": round(lows[i], 5),
                "time": candles[i]["time"],
                "bar_index": i,
                "confirmed": True,
            })

    log.info(
        f"Detected {len(swing_highs)} swing highs and {len(swing_lows)} swing lows "
        f"from {n} candles (lookback={lookback})"
    )
    return {"highs": swing_highs, "lows": swing_lows}
