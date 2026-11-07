"""OandaCandleAdapter: lets an OANDA candle response be used as a CandleSource (Phase 09 Adapter)."""

from datetime import datetime, timezone

from tools.models.candle import Candle
from tools.models.candle_source import CandleSource
from tools.models.currency_pair import validate_pair
from tools.models.timeframe import Timeframe


def parse_oanda_time(text):
    """Return an OANDA time such as "2026-10-15T18:00:00.000000000Z" as a UTC datetime."""
    if not isinstance(text, str) or not text.endswith("Z"):
        raise ValueError(f"time must be an OANDA UTC time string, got {text!r}")
    return datetime.strptime(text[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)


class OandaCandleAdapter(CandleSource):
    """Translates OANDA's candle format ("instrument", "granularity", "mid" o/h/l/c strings)
    into NEXUS Candle objects with a CurrencyPair and a Timeframe."""

    def __init__(self, response, pair):
        self._response = response
        self._pair = validate_pair(pair)
        instrument = response.get("instrument")
        if instrument != pair.name:
            raise ValueError(f"response is for {instrument!r}, not {pair.name!r}")
        try:
            self._timeframe = Timeframe(response.get("granularity"))
        except ValueError:
            raise ValueError(f"unsupported granularity {response.get('granularity')!r}")

    def candles(self):
        """Return the complete OANDA candles as Candle objects. Incomplete candles are skipped."""
        result = []
        for raw in self._response.get("candles", []):
            if raw.get("complete") is not True:
                continue
            mid = raw["mid"]
            result.append(Candle(
                self._pair, self._timeframe, parse_oanda_time(raw["time"]),
                open_=float(mid["o"]), high=float(mid["h"]), low=float(mid["l"]), close=float(mid["c"]),
                volume=raw["volume"], complete=True,
            ))
        return result
