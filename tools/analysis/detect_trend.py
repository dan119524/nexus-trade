"""
Determine the trend direction for a timeframe based on labeled structure.

Method: count the last N structure labels (default 6).
  ≥ 4 HH or HL  → bullish
  ≥ 4 LH or LL  → bearish
  else           → ranging
"""

from tools.utils.logger import get_logger

log = get_logger(__name__)

_BULLISH_LABELS = {"HH", "HL"}
_BEARISH_LABELS = {"LH", "LL"}


def detect_trend(
    structure: list[dict],
    lookback: int = 6,
    threshold: int = 4,
) -> str:
    """
    Determine trend direction from labeled structure points.

    Args:
        structure: Time-sorted labeled structure from label_structure().
        lookback:  Number of recent structure points to evaluate.
        threshold: Minimum count of aligned labels to declare a trend.

    Returns:
        "bullish" | "bearish" | "ranging"
    """
    if not structure:
        return "ranging"

    # Filter to only meaningful labels (skip first_high / first_low)
    meaningful = [
        s for s in structure
        if s.get("label") in _BULLISH_LABELS | _BEARISH_LABELS
    ]

    if len(meaningful) < 2:
        return "ranging"

    recent = meaningful[-lookback:]
    bullish_count = sum(1 for s in recent if s["label"] in _BULLISH_LABELS)
    bearish_count = sum(1 for s in recent if s["label"] in _BEARISH_LABELS)

    if bullish_count >= threshold:
        trend = "bullish"
    elif bearish_count >= threshold:
        trend = "bearish"
    else:
        trend = "ranging"

    log.info(
        f"Trend: {trend} (bullish_labels={bullish_count}, bearish_labels={bearish_count}, "
        f"last {len(recent)} structure points)"
    )
    return trend
