"""
Calculate entry price for a trade setup.

Entry logic:
  - Bearish: enter at the most recent close (market order) or at the
    most recent BOS/CHoCH level (limit order) — whichever is more
    conservative (closer to SL).
  - Bullish: same logic inverted.

We use the latest candle close as entry (market order approach).
The H1 timeframe is used as the reference by default.
"""

from tools.utils.logger import get_logger

log = get_logger(__name__)


def calculate_entry(
    candles: list[dict],
    direction: str,
) -> float:
    """
    Return the entry price for a trade.

    Args:
        candles:   Candle list for the reference timeframe (H1 recommended).
        direction: "bullish" | "bearish"

    Returns:
        Entry price (latest close).
    """
    if not candles:
        raise ValueError("No candles provided to calculate_entry")

    entry = round(candles[-1]["close"], 5)
    log.info(f"Entry price: {entry} ({direction})")
    return entry
