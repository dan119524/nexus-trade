"""Tests for Timeframe (Phase 05 value, FR6)."""

from tools.models import Timeframe


def test_there_are_exactly_four_timeframes():
    assert [tf.value for tf in Timeframe] == ["M1", "M5", "H1", "H4"]


def test_timeframe_can_be_looked_up_by_oanda_name():
    assert Timeframe("H4") is Timeframe.H4
