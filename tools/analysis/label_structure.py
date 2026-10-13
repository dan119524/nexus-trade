"""
Label swing points with market structure tags: HH, HL, LH, LL.

Rules:
  Swing highs:  current > previous → HH (Higher High)
                current < previous → LH (Lower High)
  Swing lows:   current > previous → HL (Higher Low)
                current < previous → LL (Lower Low)

The first swing of each type gets no comparison label ("first_high" / "first_low").
"""

from tools.utils.logger import get_logger

log = get_logger(__name__)


def label_structure(
    swing_highs: list[dict],
    swing_lows: list[dict],
) -> list[dict]:
    """
    Label each swing point with HH / LH / HL / LL.

    Args:
        swing_highs: List of swing high dicts from detect_swings().
        swing_lows:  List of swing low dicts from detect_swings().

    Returns:
        Combined, time-sorted list of swing points with 'label' field added.
    """
    labeled_highs = _label_series(swing_highs, higher_label="HH", lower_label="LH")
    labeled_lows  = _label_series(swing_lows,  higher_label="HL", lower_label="LL")

    combined = labeled_highs + labeled_lows
    combined.sort(key=lambda x: x["bar_index"])

    log.info(
        f"Labeled {len(labeled_highs)} swing highs and {len(labeled_lows)} swing lows"
    )
    return combined


def _label_series(
    swings: list[dict],
    higher_label: str,
    lower_label: str,
) -> list[dict]:
    labeled = []
    prev_price = None

    for swing in swings:
        s = dict(swing)  # copy so we don't mutate the original
        if prev_price is None:
            s["label"] = f"first_{s['type']}"
        elif s["price"] > prev_price:
            s["label"] = higher_label
        else:
            s["label"] = lower_label
        prev_price = s["price"]
        labeled.append(s)

    return labeled
