"""
Tests for tools/confluence/score_confluence.py

Run: pytest tests/test_score_confluence.py -v
"""

import pytest
from tools.confluence.score_confluence import score_confluence, _cast_vote


# ── Helpers ───────────────────────────────────────────────────────────────────

def tf_data(trend: str, last_event_dir: str | None = None, bar: int = 10) -> dict:
    """Build a minimal timeframe data dict for testing."""
    bos = []
    if last_event_dir:
        bos = [{"direction": last_event_dir, "broken_at_bar": bar, "event_type": "BOS"}]
    return {"trend": trend, "bos_events": bos, "choch_events": []}


def analysis(m1: str, m5: str, h1: str, h4: str) -> dict:
    """Build a minimal analysis dict with trend votes per timeframe."""
    return {
        "M1": tf_data(m1),
        "M5": tf_data(m5),
        "H1": tf_data(h1),
        "H4": tf_data(h4),
    }


# ── Vote casting ──────────────────────────────────────────────────────────────

def test_vote_bullish_trend_no_event():
    assert _cast_vote(tf_data("bullish")) == "bullish"


def test_vote_bearish_trend_no_event():
    assert _cast_vote(tf_data("bearish")) == "bearish"


def test_vote_bullish_trend_confirmed_by_bullish_event():
    assert _cast_vote(tf_data("bullish", "bullish")) == "bullish"


def test_vote_bullish_trend_contradicted_by_bearish_event():
    assert _cast_vote(tf_data("bullish", "bearish")) == "neutral"


def test_vote_bearish_trend_contradicted_by_bullish_event():
    assert _cast_vote(tf_data("bearish", "bullish")) == "neutral"


def test_vote_ranging_bullish_event():
    assert _cast_vote(tf_data("ranging", "bullish")) == "bullish"


def test_vote_ranging_bearish_event():
    assert _cast_vote(tf_data("ranging", "bearish")) == "bearish"


def test_vote_ranging_no_event():
    assert _cast_vote(tf_data("ranging")) == "neutral"


# ── Score calculation ─────────────────────────────────────────────────────────

def test_score_4_of_4_bullish():
    result = score_confluence(analysis("bullish", "bullish", "bullish", "bullish"))
    assert result["score"] == 4
    assert result["direction"] == "bullish"
    assert result["signal_valid"] is True


def test_score_3_of_4_bullish_is_valid():
    a = analysis("bullish", "bullish", "bullish", "bearish")
    result = score_confluence(a, min_score=3)
    assert result["score"] == 3
    assert result["direction"] == "bullish"
    assert result["signal_valid"] is True


def test_score_2_of_4_is_invalid():
    a = analysis("bullish", "bullish", "bearish", "bearish")
    result = score_confluence(a, min_score=3)
    assert result["score"] == 2
    assert result["signal_valid"] is False


def test_score_1_of_4_is_invalid():
    # Only M1 is bullish; the rest are neutral → majority is bullish with score 1
    a = {
        "M1": tf_data("bullish"),
        "M5": tf_data("ranging"),
        "H1": tf_data("ranging"),
        "H4": tf_data("ranging"),
    }
    result = score_confluence(a, min_score=3)
    assert result["score"] == 1
    assert result["signal_valid"] is False


def test_score_all_neutral_is_invalid():
    a = {
        "M1": tf_data("ranging"),
        "M5": tf_data("ranging"),
        "H1": tf_data("ranging"),
        "H4": tf_data("ranging"),
    }
    result = score_confluence(a, min_score=3)
    assert result["signal_valid"] is False


def test_score_4_of_4_bearish():
    result = score_confluence(analysis("bearish", "bearish", "bearish", "bearish"))
    assert result["score"] == 4
    assert result["direction"] == "bearish"
    assert result["signal_valid"] is True


def test_max_score_equals_number_of_timeframes():
    a = analysis("bullish", "bullish", "bullish", "bullish")
    result = score_confluence(a)
    assert result["max_score"] == 4


def test_dissenting_timeframes_identified():
    a = analysis("bullish", "bullish", "bullish", "bearish")
    result = score_confluence(a, min_score=3)
    assert "H4" in result["dissenting_timeframes"]


def test_neutral_timeframes_identified():
    a = {
        "M1": tf_data("bullish"),
        "M5": tf_data("bullish"),
        "H1": tf_data("bullish"),
        "H4": tf_data("ranging"),   # neutral
    }
    result = score_confluence(a, min_score=3)
    assert "H4" in result["neutral_timeframes"]
    assert result["score"] == 3
    assert result["signal_valid"] is True


def test_votes_dict_contains_all_timeframes():
    a = analysis("bullish", "bearish", "bullish", "neutral")
    result = score_confluence(a)
    assert set(result["votes"].keys()) == {"M1", "M5", "H1", "H4"}


def test_min_score_threshold_respected():
    # With min_score=4, a 3/4 should be invalid
    a = analysis("bullish", "bullish", "bullish", "bearish")
    result = score_confluence(a, min_score=4)
    assert result["signal_valid"] is False

    # With min_score=2, a 3/4 should be valid
    result2 = score_confluence(a, min_score=2)
    assert result2["signal_valid"] is True


def test_latest_event_used_not_earliest():
    """Most recent BOS/CHoCH should determine vote, not the first one."""
    tf = {
        "trend": "bullish",
        "bos_events": [
            {"direction": "bearish", "broken_at_bar": 5, "event_type": "BOS"},
            {"direction": "bullish", "broken_at_bar": 20, "event_type": "BOS"},  # most recent
        ],
        "choch_events": [],
    }
    vote = _cast_vote(tf)
    assert vote == "bullish"  # most recent event = bullish, confirms trend
