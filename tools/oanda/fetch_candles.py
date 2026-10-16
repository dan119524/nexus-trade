"""
Fetch OANDA candle data for a currency pair and granularity.

Usage (CLI):
    python -m tools.oanda.fetch_candles --pair EUR_USD --granularity H1
    python -m tools.oanda.fetch_candles --pair EUR_USD --granularity H1 --count 200
    python -m tools.oanda.fetch_candles --pair EUR_USD --granularity H1 \
        --from-time 2024-01-01T00:00:00Z --to-time 2024-06-30T23:59:59Z

Output:
    Writes .tmp/candles/{pair}_{granularity}.json
"""

import argparse
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from oandapyV20 import API
from oandapyV20.endpoints import instruments

from tools.utils.file_io import get_candle_path, write_json
from tools.utils.logger import get_logger
from tools.utils.validators import validate_granularity, validate_pair_format

load_dotenv()
log = get_logger(__name__)

TIMEFRAME_MAP = {
    "M1":  "M1",
    "M2":  "M2",
    "M5":  "M5",
    "M10": "M10",
    "M15": "M15",
    "M30": "M30",
    "H1":  "H1",
    "H4":  "H4",
    "D":   "D",
    "W":   "W",
    "M":   "M",
}

# Core timeframes used by the analysis + confluence pipeline
ALL_TIMEFRAMES = ["M1", "M5", "H1", "H4"]

# Default candle counts per timeframe (gives roughly 6–12 months of data)
DEFAULT_COUNTS = {
    "M1": 500, "M2": 500, "M5": 500, "M10": 500, "M15": 500, "M30": 500,
    "H1": 500, "H4": 500,
    "D": 365, "W": 156, "M": 60,
}


def _build_client(env: str) -> API:
    api_key = os.getenv("OANDA_API_KEY")
    if not api_key:
        raise EnvironmentError("OANDA_API_KEY not set in .env")
    environment = "live" if env == "live" else "practice"
    return API(access_token=api_key, environment=environment)


def _normalize_candle(raw: dict, pair: str, granularity: str) -> dict:
    mid = raw.get("mid", {})
    return {
        "time": raw["time"],
        "open": float(mid.get("o", 0)),
        "high": float(mid.get("h", 0)),
        "low": float(mid.get("l", 0)),
        "close": float(mid.get("c", 0)),
        "volume": int(raw.get("volume", 0)),
        "complete": raw.get("complete", True),
        "granularity": granularity,
        "pair": pair,
    }


def fetch_candles(
    pair: str,
    granularity: str,
    count: int = 500,
    from_time: str | None = None,
    to_time: str | None = None,
    env: str | None = None,
) -> list[dict]:
    """
    Fetch candles from OANDA and write to .tmp/candles/{pair}_{granularity}.json.

    Args:
        pair:        Instrument name, e.g. "EUR_USD"
        granularity: "M1" | "M5" | "H1" | "H4"
        count:       Number of candles to fetch (ignored when from_time/to_time set)
        from_time:   ISO8601 start, e.g. "2024-01-01T00:00:00Z"
        to_time:     ISO8601 end, e.g. "2024-06-30T23:59:59Z"
        env:         "practice" | "live" (defaults to OANDA_ENV in .env)

    Returns:
        List of normalized candle dicts.
    """
    validate_pair_format(pair)
    validate_granularity(granularity)

    resolved_env = env or os.getenv("OANDA_ENV", "practice")
    client = _build_client(resolved_env)

    params: dict = {"granularity": TIMEFRAME_MAP[granularity], "price": "M"}
    if from_time and to_time:
        params["from"] = from_time
        params["to"] = to_time
    else:
        params["count"] = count

    log.info(f"Fetching {pair} {granularity} from OANDA ({resolved_env})...")
    req = instruments.InstrumentsCandles(instrument=pair, params=params)
    client.request(req)

    raw_candles = req.response.get("candles", [])
    # Only keep complete candles (exclude the in-progress current bar)
    complete = [c for c in raw_candles if c.get("complete", True)]
    normalized = [_normalize_candle(c, pair, granularity) for c in complete]

    if len(normalized) < 50:
        log.warning(
            f"Only {len(normalized)} complete candles returned for {pair} {granularity}. "
            "Market may be closed or data unavailable."
        )

    out_path = get_candle_path(pair, granularity)
    write_json(out_path, normalized)
    log.info(f"Saved {len(normalized)} candles → {out_path}")

    return normalized


def fetch_all_timeframes(
    pair: str,
    count: int = 500,
    from_time: str | None = None,
    to_time: str | None = None,
    env: str | None = None,
) -> dict[str, list[dict]]:
    """
    Fetch all 4 timeframes (M1, M5, H1, H4) for a pair in one call.

    Returns:
        Dict keyed by granularity, e.g. {"M1": [...], "M5": [...], ...}
    """
    results = {}
    for tf in ALL_TIMEFRAMES:
        results[tf] = fetch_candles(pair, tf, count=count,
                                    from_time=from_time, to_time=to_time, env=env)
    return results


def fetch_multiple_pairs(
    pairs: list[str],
    count: int = 500,
    env: str | None = None,
) -> dict[str, dict[str, list[dict]]]:
    """
    Fetch all 4 timeframes for multiple pairs.

    Returns:
        Nested dict: {pair: {granularity: [candles]}}
    """
    results = {}
    for pair in pairs:
        log.info(f"=== Fetching all timeframes for {pair} ===")
        results[pair] = fetch_all_timeframes(pair, count=count, env=env)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch OANDA candle data")
    parser.add_argument("--pair", required=True, help="e.g. EUR_USD")
    parser.add_argument("--granularity", default=None,
                        help="M1 | M5 | H1 | H4 (omit to fetch all 4)")
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--from-time", default=None)
    parser.add_argument("--to-time", default=None)
    parser.add_argument("--env", default=None, help="practice | live")
    args = parser.parse_args()

    if args.granularity:
        fetch_candles(
            pair=args.pair,
            granularity=args.granularity,
            count=args.count,
            from_time=args.from_time,
            to_time=args.to_time,
            env=args.env,
        )
    else:
        fetch_all_timeframes(
            pair=args.pair,
            count=args.count,
            from_time=args.from_time,
            to_time=args.to_time,
            env=args.env,
        )
