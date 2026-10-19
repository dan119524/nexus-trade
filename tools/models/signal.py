"""Signal: a confluence result across four timeframes (Phase 05 entity)."""

from tools.models.timeframe import Timeframe
from tools.models.timeframe_analysis import TimeframeAnalysis


def _check_analysis(analysis, timeframe):
    """Return analysis if it is a TimeframeAnalysis on timeframe. Otherwise raise ValueError."""
    if not isinstance(analysis, TimeframeAnalysis):
        raise ValueError(f"{timeframe.value} must be a TimeframeAnalysis, got {analysis!r}")
    if analysis.timeframe is not timeframe:
        raise ValueError(f"{timeframe.value} analysis is on {analysis.timeframe.value}")
    return analysis


class Signal:
    """The M1, M5, H1, and H4 analyses of one pair, combined into a direction and a score (FR8)."""

    def __init__(self, m1, m5, h1, h4, min_score=3):
        self._m1 = _check_analysis(m1, Timeframe.M1)
        self._m5 = _check_analysis(m5, Timeframe.M5)
        self._h1 = _check_analysis(h1, Timeframe.H1)
        self._h4 = _check_analysis(h4, Timeframe.H4)
        if not (m1.pair is m5.pair is h1.pair is h4.pair):
            raise ValueError("all four analyses must be for the same currency pair")
        if isinstance(min_score, bool) or not isinstance(min_score, int) or not 1 <= min_score <= 4:
            raise ValueError(f"minimum score must be a whole number from 1 to 4, got {min_score!r}")
        self._min_score = min_score

    @property
    def m1(self):
        return self._m1

    @property
    def m5(self):
        return self._m5

    @property
    def h1(self):
        return self._h1

    @property
    def h4(self):
        return self._h4

    @property
    def pair(self):
        return self._m1.pair

    @property
    def min_score(self):
        return self._min_score

    def _count(self, vote):
        return sum(1 for analysis in (self._m1, self._m5, self._h1, self._h4)
                   if analysis.vote() == vote)

    def direction(self):
        """Return the majority of the bullish and bearish votes, or None on a tie."""
        bullish = self._count("bullish")
        bearish = self._count("bearish")
        if bullish == bearish:
            return None
        return "bullish" if bullish > bearish else "bearish"

    def score(self):
        """Return the number of timeframes voting this signal's direction, or 0 with no direction."""
        direction = self.direction()
        return 0 if direction is None else self._count(direction)

    def is_valid(self):
        """Return True when the signal has a direction and its score is at least the minimum."""
        return self.direction() is not None and self.score() >= self._min_score

    def trade_direction(self):
        """Return "buy" for bullish, "sell" for bearish, or None with no direction."""
        direction = self.direction()
        if direction is None:
            return None
        return "buy" if direction == "bullish" else "sell"
