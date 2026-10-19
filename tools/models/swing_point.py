"""SwingPoint: a confirmed swing high or low (Phase 05 entity)."""

from tools.models.candle import to_positive_price, validate_time, validate_timeframe
from tools.models.currency_pair import validate_pair

_HIGH_LABELS = ("HH", "LH")
_LOW_LABELS = ("HL", "LL")


class SwingPoint:
    """A swing point labeled HH or LH (a high), or HL or LL (a low) (FR7)."""

    def __init__(self, pair, timeframe, time, price, label):
        self._pair = validate_pair(pair)
        self._timeframe = validate_timeframe(timeframe)
        self._time = validate_time(time)
        self._price = to_positive_price(price, "price")
        if label not in _HIGH_LABELS + _LOW_LABELS:
            raise ValueError(f"label must be HH, HL, LH, or LL, got {label!r}")
        self._label = label

    @property
    def pair(self):
        return self._pair

    @property
    def timeframe(self):
        return self._timeframe

    @property
    def time(self):
        return self._time

    @property
    def price(self):
        return self._price

    @property
    def label(self):
        return self._label

    @property
    def kind(self):
        """Return "high" for HH or LH, and "low" for HL or LL."""
        return "high" if self._label in _HIGH_LABELS else "low"
