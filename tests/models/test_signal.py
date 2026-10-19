"""Tests for Signal (Phase 05, FR8). Fixed data only."""

import pytest

from tests.models.conftest import make_signal
from tools.models import CurrencyPair, Signal, Timeframe, TimeframeAnalysis

UP, DOWN, RANGE = "uptrend", "downtrend", "ranging"


@pytest.mark.parametrize("trends, direction, score, valid", [
    ((UP, UP, UP, UP), "bullish", 4, True),
    ((UP, UP, UP, RANGE), "bullish", 3, True),
    ((DOWN, DOWN, DOWN, UP), "bearish", 3, True),
    ((UP, UP, DOWN, RANGE), "bullish", 2, False),
    ((UP, UP, DOWN, DOWN), None, 0, False),
    ((RANGE, RANGE, RANGE, RANGE), None, 0, False),
])
def test_direction_score_and_validity(trends, direction, score, valid, eur_usd):
    signal = make_signal(eur_usd, *trends)
    assert signal.direction() == direction
    assert signal.score() == score
    assert signal.is_valid() is valid


def test_tie_is_invalid_even_with_a_low_minimum(eur_usd):
    signal = make_signal(eur_usd, UP, UP, DOWN, DOWN, min_score=1)
    assert signal.direction() is None
    assert signal.is_valid() is False


def test_custom_minimum_score(eur_usd):
    assert make_signal(eur_usd, UP, UP, DOWN, RANGE, min_score=2).is_valid() is True
    assert make_signal(eur_usd, UP, UP, UP, RANGE, min_score=4).is_valid() is False


def test_default_minimum_score_is_three(eur_usd):
    assert make_signal(eur_usd, UP, UP, UP, UP).min_score == 3


@pytest.mark.parametrize("min_score", [0, 5, 3.0, True, None])
def test_minimum_score_must_be_whole_number_from_1_to_4(min_score, eur_usd):
    with pytest.raises(ValueError):
        make_signal(eur_usd, UP, UP, UP, UP, min_score=min_score)


@pytest.mark.parametrize("trends, trade_direction", [
    ((UP, UP, UP, UP), "buy"), ((DOWN, DOWN, DOWN, DOWN), "sell"), ((UP, UP, DOWN, DOWN), None),
])
def test_trade_direction_maps_bullish_to_buy(trends, trade_direction, eur_usd):
    assert make_signal(eur_usd, *trends).trade_direction() == trade_direction


def test_signal_holds_its_four_named_analyses(eur_usd):
    analyses = [TimeframeAnalysis(eur_usd, tf, UP) for tf in Timeframe]
    signal = Signal(*analyses)
    assert (signal.m1, signal.m5, signal.h1, signal.h4) == tuple(analyses)
    assert signal.pair is eur_usd


def test_analysis_on_the_wrong_timeframe_is_rejected(eur_usd):
    m1 = TimeframeAnalysis(eur_usd, Timeframe.M1, UP)
    h1 = TimeframeAnalysis(eur_usd, Timeframe.H1, UP)
    h4 = TimeframeAnalysis(eur_usd, Timeframe.H4, UP)
    with pytest.raises(ValueError):
        Signal(m1, h1, h1, h4)


def test_analyses_for_different_pairs_are_rejected(eur_usd):
    other = CurrencyPair("EUR_USD", [(1.09, 1.08), (1.10, 1.09)])
    with pytest.raises(ValueError):
        Signal(TimeframeAnalysis(eur_usd, Timeframe.M1, UP),
               TimeframeAnalysis(eur_usd, Timeframe.M5, UP),
               TimeframeAnalysis(eur_usd, Timeframe.H1, UP),
               TimeframeAnalysis(other, Timeframe.H4, UP))


def test_non_analysis_is_rejected(eur_usd):
    analysis = TimeframeAnalysis(eur_usd, Timeframe.M5, UP)
    with pytest.raises(ValueError):
        Signal("bullish", analysis, analysis, analysis)
