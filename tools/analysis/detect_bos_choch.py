"""
Detect Break of Structure (BOS) and Change of Character (CHoCH).

BOS   = price closes BEYOND a prior swing in the DIRECTION of the trend.
        (confirms trend continuation)
CHoCH = price closes BEYOND a prior swing AGAINST the trend.
        (signals potential reversal)

How they're distinguished:
  In a bullish trend (HH/HL sequence):
    BOS   → close above the previous HH
    CHoCH → close below the previous HL

  In a bearish trend (LH/LL sequence):
    BOS   → close below the previous LL
    CHoCH → close above the previous LH
"""

from tools.utils.logger import get_logger

log = get_logger(__name__)

_BULLISH_STRUCTURE = {"HH", "HL"}
_BEARISH_STRUCTURE = {"LH", "LL"}


def detect_bos_choch(
    candles: list[dict],
    structure: list[dict],
) -> dict[str, list[dict]]:
    """
    Scan candles for BOS and CHoCH events relative to labeled structure.

    Args:
        candles:   Full list of candle dicts.
        structure: Time-sorted labeled structure from label_structure().

    Returns:
        {"bos": [event, ...], "choch": [event, ...]}
    """
    if not structure or not candles:
        return {"bos": [], "choch": []}

    bos_events   = []
    choch_events = []

    # Work through structure points to find levels to watch
    swing_highs = [s for s in structure if s["type"] == "high" and s["label"] not in ("first_high", "first_low")]
    swing_lows  = [s for s in structure if s["type"] == "low"  and s["label"] not in ("first_high", "first_low")]

    # Build a list of (level, direction, event_type, source_swing) to check
    levels_to_watch = []

    for swing in swing_highs:
        if swing["label"] == "HH":
            # In a bullish trend, a close above the prior HH = BOS bullish
            levels_to_watch.append({
                "level": swing["price"],
                "break_direction": "bullish",
                "event_type": "BOS",
                "source_swing": swing,
                "watch_from_bar": swing["bar_index"] + 1,
            })
        elif swing["label"] == "LH":
            # A close above a LH in bearish trend = CHoCH bullish
            levels_to_watch.append({
                "level": swing["price"],
                "break_direction": "bullish",
                "event_type": "CHoCH",
                "source_swing": swing,
                "watch_from_bar": swing["bar_index"] + 1,
            })

    for swing in swing_lows:
        if swing["label"] == "LL":
            # In a bearish trend, a close below the prior LL = BOS bearish
            levels_to_watch.append({
                "level": swing["price"],
                "break_direction": "bearish",
                "event_type": "BOS",
                "source_swing": swing,
                "watch_from_bar": swing["bar_index"] + 1,
            })
        elif swing["label"] == "HL":
            # A close below a HL in bullish trend = CHoCH bearish
            levels_to_watch.append({
                "level": swing["price"],
                "break_direction": "bearish",
                "event_type": "CHoCH",
                "source_swing": swing,
                "watch_from_bar": swing["bar_index"] + 1,
            })

    # Track which levels have already been broken (avoid duplicate events)
    broken_levels = set()

    for watch in levels_to_watch:
        level      = watch["level"]
        direction  = watch["break_direction"]
        start_bar  = watch["watch_from_bar"]

        if level in broken_levels:
            continue

        for i in range(start_bar, len(candles)):
            candle = candles[i]
            broke  = False

            if direction == "bullish" and candle["close"] > level:
                broke = True
            elif direction == "bearish" and candle["close"] < level:
                broke = True

            if broke:
                event = {
                    "event_type": watch["event_type"],
                    "direction": direction,
                    "level": level,
                    "broken_at_time": candle["time"],
                    "broken_at_bar": i,
                    "source_swing": watch["source_swing"],
                }
                if watch["event_type"] == "BOS":
                    bos_events.append(event)
                else:
                    choch_events.append(event)
                broken_levels.add(level)
                break

    log.info(f"Detected {len(bos_events)} BOS and {len(choch_events)} CHoCH events")
    return {"bos": bos_events, "choch": choch_events}
