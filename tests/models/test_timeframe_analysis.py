"""Tests for TimeframeAnalysis and its vote (Phase 05, FR8 voting table)."""

import pytest

from tests.models.conftest import T0
from tools.models import (
    BreakOfStructure, ChangeOfCharacter, CurrencyPair, SwingPoint, Timeframe, TimeframeAnalysis,
)


def event(pair, direction, timeframe=Timeframe.H1):
    """Return a structure event with the given direction on pair and timeframe, or None."""
    if direction is None:
        return None
    if direction == "bullish":
        return BreakOfStructure(SwingPoint(pair, timeframe, T0, 1.09, "HH"), T0, 1.10)
    return ChangeOfCharacter(SwingPoint(pair, timeframe, T0, 1.09, "HL"), T0, 1.08)


@pytest.mark.parametrize("trend, event_direction, vote", [
    ("uptrend", "bullish", "bullish"),
    ("uptrend", None, "bullish"),
    ("uptrend", "bearish", "neutral"),
    ("downtrend", "bearish", "bearish"),
    ("downtrend", None, "bearish"),
    ("downtrend", "bullish", "neutral"),
    ("ranging", "bullish", "bullish"),
    ("ranging", "bearish", "bearish"),
    ("ranging", None, "neutral"),
])
def test_vote_follows_the_voting_table(trend, event_direction, vote, eur_usd):
    analysis = TimeframeAnalysis(eur_usd, Timeframe.H1, trend, event(eur_usd, event_direction))
    assert analysis.vote() == vote


def test_valid_analysis_stores_values(eur_usd):
    latest = event(eur_usd, "bullish", Timeframe.H4)
    analysis = TimeframeAnalysis(eur_usd, Timeframe.H4, "uptrend", latest)
    assert analysis.pair is eur_usd
    assert analysis.timeframe is Timeframe.H4
    assert analysis.trend == "uptrend"
    assert analysis.latest_event is latest


def test_latest_event_defaults_to_none(eur_usd):
    assert TimeframeAnalysis(eur_usd, Timeframe.M1, "ranging").latest_event is None


@pytest.mark.parametrize("trend", ["bullish", "bearish", "Uptrend", None])
def test_trend_must_use_market_structure_vocabulary(trend, eur_usd):
    with pytest.raises(ValueError):
        TimeframeAnalysis(eur_usd, Timeframe.H1, trend)


def test_latest_event_must_be_a_structure_event(eur_usd):
    with pytest.raises(ValueError):
        TimeframeAnalysis(eur_usd, Timeframe.H1, "uptrend", "bullish")


def test_pair_and_timeframe_are_checked(eur_usd):
    with pytest.raises(ValueError):
        TimeframeAnalysis("EUR_USD", Timeframe.H1, "uptrend")
    with pytest.raises(ValueError):
        TimeframeAnalysis(eur_usd, "H1", "uptrend")


def test_event_on_another_timeframe_is_rejected(eur_usd):
    with pytest.raises(ValueError):
        TimeframeAnalysis(eur_usd, Timeframe.H4, "uptrend", event(eur_usd, "bullish", Timeframe.H1))


def test_event_on_another_pair_is_rejected(eur_usd, gbp_usd):
    with pytest.raises(ValueError):
        TimeframeAnalysis(eur_usd, Timeframe.H1, "uptrend", event(gbp_usd, "bullish"))


def test_event_on_a_different_pair_object_with_the_same_name_is_rejected(eur_usd):
    other = CurrencyPair("EUR_USD", [(1.09, 1.08), (1.10, 1.09)])
    with pytest.raises(ValueError):
        TimeframeAnalysis(eur_usd, Timeframe.H1, "uptrend", event(other, "bullish"))
