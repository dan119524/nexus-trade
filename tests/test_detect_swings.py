"""
Tests for the analysis engine: detect_swings, label_structure,
detect_bos_choch, detect_trend, detect_channels.

All tests use synthetic candle data — no API calls needed.
Run: pytest tests/test_detect_swings.py -v
"""

import pytest


# ── Candle factory ────────────────────────────────────────────────────────────

def make_candle(i: int, o: float, h: float, l: float, c: float) -> dict:
    return {
        "time": f"2025-01-{i+1:02d}T00:00:00Z",
        "open": o, "high": h, "low": l, "close": c,
        "volume": 1000, "complete": True,
        "granularity": "H1", "pair": "EUR_USD",
        "bar_index": i,
    }


def zigzag_candles(prices: list[float]) -> list[dict]:
    """
    Build candles from a list of close prices.
    High = close + 0.0005, Low = close - 0.0005.
    """
    candles = []
    for i, p in enumerate(prices):
        candles.append(make_candle(i, p, p + 0.0005, p - 0.0005, p))
    return candles


# ── Swing Detection ───────────────────────────────────────────────────────────

def test_detects_correct_swing_high():
    from tools.analysis.detect_swings import detect_swings
    # Bar 5 is clearly the highest in a 5-bar window each side
    prices = [1.10, 1.11, 1.12, 1.13, 1.14, 1.20, 1.14, 1.13, 1.12, 1.11, 1.10]
    candles = zigzag_candles(prices)
    result = detect_swings(candles, lookback=3)
    high_bars = [s["bar_index"] for s in result["highs"]]
    assert 5 in high_bars, f"Expected swing high at bar 5, got: {high_bars}"


def test_detects_correct_swing_low():
    from tools.analysis.detect_swings import detect_swings
    prices = [1.20, 1.19, 1.18, 1.17, 1.16, 1.10, 1.16, 1.17, 1.18, 1.19, 1.20]
    candles = zigzag_candles(prices)
    result = detect_swings(candles, lookback=3)
    low_bars = [s["bar_index"] for s in result["lows"]]
    assert 5 in low_bars, f"Expected swing low at bar 5, got: {low_bars}"


def test_no_swings_on_flat_data():
    from tools.analysis.detect_swings import detect_swings
    prices = [1.1000] * 20
    candles = zigzag_candles(prices)
    result = detect_swings(candles, lookback=3)
    assert result["highs"] == []
    assert result["lows"] == []


def test_insufficient_candles_returns_empty():
    from tools.analysis.detect_swings import detect_swings
    candles = zigzag_candles([1.10, 1.11, 1.12])
    result = detect_swings(candles, lookback=5)
    assert result == {"highs": [], "lows": []}


def test_all_swings_confirmed():
    from tools.analysis.detect_swings import detect_swings
    prices = [1.10, 1.15, 1.08, 1.18, 1.05, 1.20, 1.07, 1.16, 1.09, 1.14, 1.11]
    candles = zigzag_candles(prices)
    result = detect_swings(candles, lookback=2)
    for s in result["highs"] + result["lows"]:
        assert s["confirmed"] is True


# ── Structure Labeling ────────────────────────────────────────────────────────

def test_ascending_highs_labeled_HH():
    from tools.analysis.label_structure import label_structure
    highs = [
        {"type": "high", "price": 1.10, "bar_index": 0, "time": "t0", "confirmed": True},
        {"type": "high", "price": 1.12, "bar_index": 2, "time": "t2", "confirmed": True},
        {"type": "high", "price": 1.15, "bar_index": 4, "time": "t4", "confirmed": True},
    ]
    result = label_structure(highs, [])
    labels = [s["label"] for s in result if s["type"] == "high"]
    assert labels == ["first_high", "HH", "HH"]


def test_descending_highs_labeled_LH():
    from tools.analysis.label_structure import label_structure
    highs = [
        {"type": "high", "price": 1.15, "bar_index": 0, "time": "t0", "confirmed": True},
        {"type": "high", "price": 1.12, "bar_index": 2, "time": "t2", "confirmed": True},
        {"type": "high", "price": 1.10, "bar_index": 4, "time": "t4", "confirmed": True},
    ]
    result = label_structure(highs, [])
    labels = [s["label"] for s in result if s["type"] == "high"]
    assert labels == ["first_high", "LH", "LH"]


def test_ascending_lows_labeled_HL():
    from tools.analysis.label_structure import label_structure
    lows = [
        {"type": "low", "price": 1.05, "bar_index": 1, "time": "t1", "confirmed": True},
        {"type": "low", "price": 1.07, "bar_index": 3, "time": "t3", "confirmed": True},
        {"type": "low", "price": 1.09, "bar_index": 5, "time": "t5", "confirmed": True},
    ]
    result = label_structure([], lows)
    labels = [s["label"] for s in result if s["type"] == "low"]
    assert labels == ["first_low", "HL", "HL"]


def test_descending_lows_labeled_LL():
    from tools.analysis.label_structure import label_structure
    lows = [
        {"type": "low", "price": 1.09, "bar_index": 1, "time": "t1", "confirmed": True},
        {"type": "low", "price": 1.07, "bar_index": 3, "time": "t3", "confirmed": True},
        {"type": "low", "price": 1.05, "bar_index": 5, "time": "t5", "confirmed": True},
    ]
    result = label_structure([], lows)
    labels = [s["label"] for s in result if s["type"] == "low"]
    assert labels == ["first_low", "LL", "LL"]


def test_structure_sorted_by_bar_index():
    from tools.analysis.label_structure import label_structure
    highs = [
        {"type": "high", "price": 1.10, "bar_index": 0, "time": "t0", "confirmed": True},
        {"type": "high", "price": 1.12, "bar_index": 4, "time": "t4", "confirmed": True},
    ]
    lows = [
        {"type": "low", "price": 1.05, "bar_index": 2, "time": "t2", "confirmed": True},
    ]
    result = label_structure(highs, lows)
    indices = [s["bar_index"] for s in result]
    assert indices == sorted(indices)


# ── BOS / CHoCH Detection ─────────────────────────────────────────────────────

def test_bos_bullish_detected():
    from tools.analysis.detect_bos_choch import detect_bos_choch
    # HH at bar 2 price 1.15 — candle at bar 5 closes above it → BOS
    structure = [
        {"type": "high", "label": "HH", "price": 1.15, "bar_index": 2, "time": "t2", "confirmed": True},
    ]
    candles = zigzag_candles([1.10, 1.12, 1.15, 1.13, 1.14, 1.16])
    # bar 5 close = 1.16 > 1.15
    result = detect_bos_choch(candles, structure)
    assert len(result["bos"]) >= 1
    bos = result["bos"][0]
    assert bos["direction"] == "bullish"
    assert bos["level"] == 1.15


def test_bos_bearish_detected():
    from tools.analysis.detect_bos_choch import detect_bos_choch
    structure = [
        {"type": "low", "label": "LL", "price": 1.08, "bar_index": 2, "time": "t2", "confirmed": True},
    ]
    candles = zigzag_candles([1.12, 1.10, 1.08, 1.09, 1.09, 1.07])
    result = detect_bos_choch(candles, structure)
    assert len(result["bos"]) >= 1
    assert result["bos"][0]["direction"] == "bearish"


def test_choch_detected():
    from tools.analysis.detect_bos_choch import detect_bos_choch
    # HL at bar 2 price 1.09 — close below it = CHoCH bearish
    structure = [
        {"type": "low", "label": "HL", "price": 1.09, "bar_index": 2, "time": "t2", "confirmed": True},
    ]
    candles = zigzag_candles([1.12, 1.10, 1.09, 1.10, 1.09, 1.08])
    result = detect_bos_choch(candles, structure)
    assert len(result["choch"]) >= 1
    assert result["choch"][0]["direction"] == "bearish"


def test_no_false_bos_when_no_break():
    from tools.analysis.detect_bos_choch import detect_bos_choch
    structure = [
        {"type": "high", "label": "HH", "price": 1.20, "bar_index": 2, "time": "t2", "confirmed": True},
    ]
    candles = zigzag_candles([1.10, 1.12, 1.20, 1.18, 1.17, 1.16])
    result = detect_bos_choch(candles, structure)
    assert result["bos"] == []


# ── Trend Detection ───────────────────────────────────────────────────────────

def test_trend_bullish():
    from tools.analysis.detect_trend import detect_trend
    structure = [
        {"label": "HH"}, {"label": "HL"}, {"label": "HH"},
        {"label": "HL"}, {"label": "HH"}, {"label": "HL"},
    ]
    assert detect_trend(structure) == "bullish"


def test_trend_bearish():
    from tools.analysis.detect_trend import detect_trend
    structure = [
        {"label": "LH"}, {"label": "LL"}, {"label": "LH"},
        {"label": "LL"}, {"label": "LH"}, {"label": "LL"},
    ]
    assert detect_trend(structure) == "bearish"


def test_trend_ranging_mixed():
    from tools.analysis.detect_trend import detect_trend
    structure = [
        {"label": "HH"}, {"label": "LL"}, {"label": "HL"},
        {"label": "LH"}, {"label": "HH"}, {"label": "LL"},
    ]
    assert detect_trend(structure) == "ranging"


def test_trend_empty_structure():
    from tools.analysis.detect_trend import detect_trend
    assert detect_trend([]) == "ranging"


# ── Channel Detection ─────────────────────────────────────────────────────────

def test_channel_ascending():
    from tools.analysis.detect_channels import detect_channels
    highs = [
        {"price": 1.10, "bar_index": 0},
        {"price": 1.12, "bar_index": 5},
        {"price": 1.14, "bar_index": 10},
        {"price": 1.16, "bar_index": 15},
    ]
    lows = [
        {"price": 1.05, "bar_index": 2},
        {"price": 1.07, "bar_index": 7},
        {"price": 1.09, "bar_index": 12},
        {"price": 1.11, "bar_index": 17},
    ]
    channel = detect_channels(highs, lows)
    assert channel["channel_type"] == "ascending"
    assert channel["resistance_slope"] > 0
    assert channel["support_slope"] > 0


def test_channel_descending():
    from tools.analysis.detect_channels import detect_channels
    highs = [
        {"price": 1.16, "bar_index": 0},
        {"price": 1.14, "bar_index": 5},
        {"price": 1.12, "bar_index": 10},
    ]
    lows = [
        {"price": 1.11, "bar_index": 2},
        {"price": 1.09, "bar_index": 7},
        {"price": 1.07, "bar_index": 12},
    ]
    channel = detect_channels(highs, lows)
    assert channel["channel_type"] == "descending"


def test_channel_empty_when_insufficient_swings():
    from tools.analysis.detect_channels import detect_channels
    channel = detect_channels(
        [{"price": 1.10, "bar_index": 0}],
        [],
    )
    assert channel == {}
