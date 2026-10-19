"""Tests for Candle (Phase 05, FR6). Fixed data only."""

from datetime import date

import pytest

from tests.models.conftest import T0
from tools.models import Candle, Timeframe

NAN = float("nan")


def make_candle(pair, **changes):
    values = {"pair": pair, "timeframe": Timeframe.H1, "time": T0, "open_": 1.0842,
              "high": 1.0865, "low": 1.0820, "close": 1.0854, "volume": 18432, "complete": True}
    values.update(changes)
    return Candle(**values)


def test_valid_candle_stores_values(eur_usd):
    candle = make_candle(eur_usd)
    assert candle.pair is eur_usd
    assert candle.timeframe is Timeframe.H1
    assert candle.time == T0
    assert (candle.open, candle.high, candle.low, candle.close) == (1.0842, 1.0865, 1.0820, 1.0854)
    assert candle.volume == 18432


def test_integer_prices_are_stored_as_floats(usd_jpy):
    candle = make_candle(usd_jpy, open_=150, high=151, low=149, close=150)
    assert isinstance(candle.high, float)


def test_high_equal_to_low_is_allowed(eur_usd):
    candle = make_candle(eur_usd, open_=1.08, high=1.08, low=1.08, close=1.08)
    assert candle.high == candle.low


@pytest.mark.parametrize("complete", [False, None, "yes", 1])
def test_incomplete_candle_is_rejected(complete, eur_usd):
    with pytest.raises(ValueError):
        make_candle(eur_usd, complete=complete)


@pytest.mark.parametrize("field, value", [
    ("open_", 1.0866), ("open_", 1.0819), ("close", 1.0866), ("close", 1.0819),
])
def test_open_or_close_outside_low_high_is_rejected(field, value, eur_usd):
    # low 1.0820, high 1.0865
    with pytest.raises(ValueError):
        make_candle(eur_usd, **{field: value})


@pytest.mark.parametrize("open_, close", [(1.0820, 1.0865), (1.0865, 1.0820)])
def test_open_and_close_may_equal_low_or_high(open_, close, eur_usd):
    candle = make_candle(eur_usd, open_=open_, close=close)
    assert (candle.open, candle.close) == (open_, close)


def test_high_below_low_is_rejected(eur_usd):
    with pytest.raises(ValueError):
        make_candle(eur_usd, high=1.0810, low=1.0820)


@pytest.mark.parametrize("field", ["open_", "high", "low", "close"])
@pytest.mark.parametrize("value", [0, -1.08, NAN, "1.08", True, None])
def test_invalid_price_is_rejected(field, value, eur_usd):
    with pytest.raises(ValueError):
        make_candle(eur_usd, **{field: value})


@pytest.mark.parametrize("pair", ["EUR_USD", None])
def test_pair_must_be_a_currency_pair(pair):
    with pytest.raises(ValueError):
        make_candle(pair)


@pytest.mark.parametrize("timeframe", ["H1", None])
def test_timeframe_must_be_a_timeframe(timeframe, eur_usd):
    with pytest.raises(ValueError):
        make_candle(eur_usd, timeframe=timeframe)


@pytest.mark.parametrize("time", ["2026-10-15T14:00:00Z", date(2026, 10, 15), None])
def test_time_must_be_a_datetime(time, eur_usd):
    with pytest.raises(ValueError):
        make_candle(eur_usd, time=time)


@pytest.mark.parametrize("volume", [-1, 1.5, True, None])
def test_invalid_volume_is_rejected(volume, eur_usd):
    with pytest.raises(ValueError):
        make_candle(eur_usd, volume=volume)


def test_candle_is_read_only(eur_usd):
    candle = make_candle(eur_usd)
    with pytest.raises(AttributeError):
        candle.close = 1.09
