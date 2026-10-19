"""TimeframeAnalysis: one pair's analysis on one timeframe (Phase 05 entity)."""

from tools.models.candle import validate_timeframe
from tools.models.currency_pair import validate_pair
from tools.models.structure_event import StructureEvent

_TRENDS = ("uptrend", "downtrend", "ranging")


class TimeframeAnalysis:
    """A trend, the most recent structure event (or None), and the vote they give (FR8)."""

    def __init__(self, pair, timeframe, trend, latest_event=None):
        self._pair = validate_pair(pair)
        self._timeframe = validate_timeframe(timeframe)
        if trend not in _TRENDS:
            raise ValueError(f"trend must be uptrend, downtrend, or ranging, got {trend!r}")
        self._trend = trend
        if latest_event is not None and not isinstance(latest_event, StructureEvent):
            raise ValueError(f"latest event must be a StructureEvent or None, got {latest_event!r}")
        if latest_event is not None and (latest_event.swing.pair is not self._pair
                                         or latest_event.swing.timeframe is not self._timeframe):
            raise ValueError("latest event must be on this analysis's pair and timeframe")
        self._latest_event = latest_event

    @property
    def pair(self):
        return self._pair

    @property
    def timeframe(self):
        return self._timeframe

    @property
    def trend(self):
        return self._trend

    @property
    def latest_event(self):
        return self._latest_event

    def vote(self):
        """Return "bullish", "bearish", or "neutral" from the voting table in requirements.md."""
        event = self._latest_event.direction if self._latest_event is not None else None
        if self._trend == "uptrend":
            return "neutral" if event == "bearish" else "bullish"
        if self._trend == "downtrend":
            return "neutral" if event == "bullish" else "bearish"
        return event if event is not None else "neutral"
