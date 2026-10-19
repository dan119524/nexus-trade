"""Tests for SwingPoint (Phase 05, FR7). Fixed data only."""

import pytest

from tests.models.conftest import T0
from tools.models import SwingPoint, Timeframe


def test_valid_swing_point_stores_values(eur_usd):
    swing = SwingPoint(eur_usd, Timeframe.H4, T0, 1.0950, "HH")
    assert swing.pair is eur_usd
    assert swing.timeframe is Timeframe.H4
    assert swing.time == T0
    assert swing.price == 1.0950
    assert swing.label == "HH"


@pytest.mark.parametrize("label, kind", [("HH", "high"), ("LH", "high"), ("HL", "low"), ("LL", "low")])
def test_kind_comes_from_label(label, kind, eur_usd):
    assert SwingPoint(eur_usd, Timeframe.H1, T0, 1.09, label).kind == kind


@pytest.mark.parametrize("label", ["first_high", "first_low", "hh", "BOS", None])
def test_invalid_label_is_rejected(label, eur_usd):
    with pytest.raises(ValueError):
        SwingPoint(eur_usd, Timeframe.H1, T0, 1.09, label)


@pytest.mark.parametrize("price", [0, -1.09, float("inf"), "1.09"])
def test_invalid_price_is_rejected(price, eur_usd):
    with pytest.raises(ValueError):
        SwingPoint(eur_usd, Timeframe.H1, T0, price, "HH")


def test_pair_timeframe_and_time_are_checked(eur_usd):
    with pytest.raises(ValueError):
        SwingPoint("EUR_USD", Timeframe.H1, T0, 1.09, "HH")
    with pytest.raises(ValueError):
        SwingPoint(eur_usd, "H1", T0, 1.09, "HH")
    with pytest.raises(ValueError):
        SwingPoint(eur_usd, Timeframe.H1, "now", 1.09, "HH")


def test_swing_point_is_read_only(eur_usd):
    swing = SwingPoint(eur_usd, Timeframe.H1, T0, 1.09, "HH")
    with pytest.raises(AttributeError):
        swing.label = "LL"
