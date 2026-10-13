"""
Replay historical candles bar by bar for backtesting.

Strategy: step through H1 candles one bar at a time.
At each H1 close, slice all 4 timeframes to only include
data available up to that timestamp — simulating real-time
conditions without lookahead bias.

The step interval is H1. Each step represents one H1 bar close.
We only generate a new potential signal every MIN_BARS_BETWEEN_SIGNALS
H1 bars to avoid over-trading the same move.
"""

from datetime import datetime, timezone
from tools.utils.logger import get_logger

log = get_logger(__name__)

# Minimum H1 bars between signal checks (avoids churning signals on same structure)
MIN_BARS_BETWEEN_SIGNALS = 4


def slice_candles_to_time(candles: list[dict], cutoff_time: str) -> list[dict]:
    """Return only candles whose time <= cutoff_time."""
    return [c for c in candles if c["time"] <= cutoff_time]


def build_windows(
    candles_by_tf: dict[str, list[dict]],
    min_candles: int = 50,
    step: int = 1,
) -> list[dict]:
    """
    Build a list of time windows stepped through the H1 candles.

    Each window is a dict:
        {
          "cutoff_time": str,   # ISO8601 timestamp of H1 bar close
          "h1_bar_index": int,  # index in the H1 series
          "candles": {          # sliced candles per TF up to cutoff_time
            "M1": [...],
            "M5": [...],
            "H1": [...],
            "H4": [...],
          }
        }

    Args:
        candles_by_tf: Full candle data for all timeframes.
        min_candles:   Minimum H1 candles required before starting.
        step:          Advance by this many H1 bars per window.
    """
    h1_candles = candles_by_tf.get("H1", [])
    if len(h1_candles) < min_candles:
        log.warning(f"Only {len(h1_candles)} H1 candles — need at least {min_candles} to backtest.")
        return []

    windows = []
    for i in range(min_candles, len(h1_candles), step):
        cutoff = h1_candles[i]["time"]
        window = {
            "cutoff_time": cutoff,
            "h1_bar_index": i,
            "candles": {
                tf: slice_candles_to_time(candles, cutoff)
                for tf, candles in candles_by_tf.items()
            },
        }
        windows.append(window)

    log.info(f"Built {len(windows)} replay windows from {len(h1_candles)} H1 candles")
    return windows
