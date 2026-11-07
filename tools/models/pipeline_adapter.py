"""PipelineAdapter: lets the pipeline's dicts be used as domain objects (Phase 09 Adapter)."""

from tools.models.account import Account
from tools.models.break_of_structure import BreakOfStructure
from tools.models.change_of_character import ChangeOfCharacter
from tools.models.currency_pair import CurrencyPair
from tools.models.oanda_candle_adapter import parse_oanda_time
from tools.models.signal import Signal
from tools.models.swing_point import SwingPoint
from tools.models.timeframe import Timeframe
from tools.models.timeframe_analysis import TimeframeAnalysis

# The analysis tools say bullish/bearish; TimeframeAnalysis says uptrend/downtrend (FR12).
_TRENDS = {"bullish": "uptrend", "bearish": "downtrend", "ranging": "ranging"}
_EVENTS = {"BOS": BreakOfStructure, "CHoCH": ChangeOfCharacter}


class PipelineAdapter:
    """Translates one pair's pipeline data into domain objects.

    The pipeline passes dicts: candle dicts per timeframe, the analysis dict from run_analysis,
    and the account dict from fetch_account. This adapter turns them into a CurrencyPair,
    a Signal (four TimeframeAnalysis objects with their latest StructureEvent), and an Account.
    It reads no files and calls no API.
    """

    def __init__(self, pair_name, analysis, candles_by_timeframe, price_timeframe):
        self._analysis = analysis.get("timeframes", {})
        self._candles = candles_by_timeframe
        candles = candles_by_timeframe.get(price_timeframe, [])
        self._pair = CurrencyPair(pair_name, [(c["high"], c["low"]) for c in candles])

    def pair(self):
        """Return the CurrencyPair, with the price data of the price timeframe's candles."""
        return self._pair

    def signal(self, min_score=3):
        """Return a Signal built from the M1, M5, H1, and H4 analyses.

        A timeframe missing from the analysis becomes ranging with no event (a neutral vote),
        the same as the pipeline's confluence score, which only counts the timeframes it has.
        """
        m1, m5, h1, h4 = (self._timeframe_analysis(tf) for tf in (Timeframe.M1, Timeframe.M5,
                                                                   Timeframe.H1, Timeframe.H4))
        return Signal(m1, m5, h1, h4, min_score=min_score)

    def account(self, account_data, risk_percent):
        """Return an Account from fetch_account's dict and the risk percent."""
        return Account(account_data.get("account_id"), account_data.get("balance"),
                       account_data.get("currency"), account_data.get("env"), risk_percent)

    def _timeframe_analysis(self, timeframe):
        data = self._analysis.get(timeframe.value)
        if data is None:
            return TimeframeAnalysis(self._pair, timeframe, "ranging")
        trend = data.get("trend", "ranging")
        if trend not in _TRENDS:
            raise ValueError(f"unknown {timeframe.value} trend {trend!r}")
        return TimeframeAnalysis(self._pair, timeframe, _TRENDS[trend],
                                 latest_event=self._latest_event(timeframe, data))

    def _latest_event(self, timeframe, data):
        """Return the most recent BOS or CHoCH as a StructureEvent, or None."""
        events = data.get("bos_events", []) + data.get("choch_events", [])
        if not events:
            return None
        latest = max(events, key=lambda e: e["broken_at_bar"])
        source = latest["source_swing"]
        swing = SwingPoint(self._pair, timeframe, parse_oanda_time(source["time"]),
                           source["price"], source["label"])
        close = self._candles[timeframe.value][latest["broken_at_bar"]]["close"]
        return _EVENTS[latest["event_type"]](swing, parse_oanda_time(latest["broken_at_time"]), close)
