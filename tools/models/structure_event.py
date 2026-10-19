"""StructureEvent: a close beyond a swing point (Phase 05 abstract base class)."""

from abc import ABC, abstractmethod

from tools.models.candle import to_positive_price, validate_time
from tools.models.swing_point import SwingPoint


class StructureEvent(ABC):
    """A candle close beyond a labeled swing point, bullish or bearish (FR7).

    StructureEvent is abstract. Only BreakOfStructure and ChangeOfCharacter can be built.
    """

    def __init__(self, swing, time, close):
        if not isinstance(swing, SwingPoint):
            raise ValueError(f"swing must be a SwingPoint, got {swing!r}")
        self._swing = swing
        self._time = validate_time(time)
        self._close = to_positive_price(close, "close")
        self._direction = self._direction_for(swing.label)
        if self._direction == "bullish" and not self._close > swing.price:
            raise ValueError("a bullish break needs a close above the swing point")
        if self._direction == "bearish" and not self._close < swing.price:
            raise ValueError("a bearish break needs a close below the swing point")

    @abstractmethod
    def _direction_for(self, label):
        """Return "bullish" or "bearish" for a swing label this event may break, or raise ValueError."""

    @property
    def swing(self):
        return self._swing

    @property
    def time(self):
        return self._time

    @property
    def close(self):
        return self._close

    @property
    def direction(self):
        return self._direction
