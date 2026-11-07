"""Phase 09: the domain Signal built by PipelineAdapter votes the same as the pipeline's confluence score.

Runs the real analysis tools on fixed synthetic candles. Never calls OANDA.
"""

import math
from datetime import datetime, timedelta, timezone

import pytest

from tools.analysis.detect_bos_choch import detect_bos_choch
from tools.analysis.detect_swings import detect_swings
from tools.analysis.detect_trend import detect_trend
from tools.analysis.label_structure import label_structure
from tools.confluence.score_confluence import score_confluence
from tools.models import PipelineAdapter

T0 = datetime(2026, 10, 1, tzinfo=timezone.utc)


def _candles(slope, phase, count=120):
    candles, price = [], 1.08
    for i in range(count):
        price += slope + 0.002 * math.sin(i / 3 + phase)
        candles.append({"time": (T0 + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%S.000000000Z"),
                        "open": price, "high": price + 0.0008, "low": price - 0.0008,
                        "close": price + 0.0002, "volume": 100, "complete": True})
    return candles


def _analyse(slopes):
    candles_by_tf, analysis = {}, {"timeframes": {}}
    for phase, (tf, slope) in enumerate(slopes.items()):
        candles = _candles(slope, phase)
        swings = detect_swings(candles, lookback=3)
        structure = label_structure(swings["highs"], swings["lows"])
        events = detect_bos_choch(candles, structure)
        candles_by_tf[tf] = candles
        analysis["timeframes"][tf] = {"trend": detect_trend(structure), "swing_highs": swings["highs"],
                                      "swing_lows": swings["lows"], "bos_events": events["bos"],
                                      "choch_events": events["choch"]}
    return analysis, candles_by_tf


@pytest.mark.parametrize("slopes", [
    {"M1": 0.0003, "M5": 0.0003, "H1": -0.0003, "H4": 0.0003},
    {"M1": -0.0003, "M5": -0.0003, "H1": -0.0003, "H4": -0.0003},
    {"M1": 0.0, "M5": 0.0003, "H1": -0.0003, "H4": 0.0},
])
def test_domain_signal_votes_like_the_pipeline(slopes):
    analysis, candles_by_tf = _analyse(slopes)
    confluence = score_confluence(analysis["timeframes"], min_score=3)
    signal = PipelineAdapter("EUR_USD", analysis, candles_by_tf, price_timeframe="H1").signal(3)

    domain_votes = {a.timeframe.value: a.vote() for a in (signal.m1, signal.m5, signal.h1, signal.h4)}
    assert domain_votes == confluence["votes"]
    assert signal.is_valid() == confluence["signal_valid"]
    if signal.is_valid():
        assert signal.direction() == confluence["direction"]
        assert signal.score() == confluence["score"]
