"""Tests for OandaCandleAdapter (Phase 09 Adapter). Fixed OANDA-format data only; nothing calls OANDA."""

from datetime import datetime, timezone

import pytest

from tools.models import Candle, CandleSource, OandaCandleAdapter, Timeframe


def _response(instrument="EUR_USD", granularity="H4", candles=None):
    if candles is None:
        candles = [
            {"time": "2026-10-15T14:00:00.000000000Z", "volume": 15210, "complete": True,
             "mid": {"o": "1.08920", "h": "1.09110", "l": "1.08870", "c": "1.09050"}},
            {"time": "2026-10-15T18:00:00.000000000Z", "volume": 18432, "complete": True,
             "mid": {"o": "1.09050", "h": "1.09750", "l": "1.08980", "c": "1.09620"}},
        ]
    return {"instrument": instrument, "granularity": granularity, "candles": candles}


def test_adapter_is_a_candle_source(eur_usd):
    assert isinstance(OandaCandleAdapter(_response(), eur_usd), CandleSource)


def test_bare_candle_source_is_rejected():
    with pytest.raises(TypeError):
        CandleSource()


def test_oanda_candles_become_candle_objects(eur_usd):
    first, second = OandaCandleAdapter(_response(), eur_usd).candles()
    assert isinstance(first, Candle)
    assert first.pair is eur_usd
    assert first.timeframe is Timeframe.H4
    assert first.time == datetime(2026, 10, 15, 14, 0, tzinfo=timezone.utc)
    assert (first.open, first.high, first.low, first.close) == (1.0892, 1.0911, 1.0887, 1.0905)
    assert first.volume == 15210
    assert second.close == 1.0962


def test_incomplete_candle_is_skipped(eur_usd):
    candles = _response()["candles"] + [
        {"time": "2026-10-15T22:00:00.000000000Z", "volume": 2031, "complete": False,
         "mid": {"o": "1.09620", "h": "1.09700", "l": "1.09550", "c": "1.09600"}}]
    assert len(OandaCandleAdapter(_response(candles=candles), eur_usd).candles()) == 2


def test_empty_response_gives_no_candles(eur_usd):
    assert OandaCandleAdapter(_response(candles=[]), eur_usd).candles() == []


def test_response_for_another_pair_is_rejected(eur_usd):
    with pytest.raises(ValueError):
        OandaCandleAdapter(_response(instrument="GBP_USD"), eur_usd)


def test_unsupported_granularity_is_rejected(eur_usd):
    with pytest.raises(ValueError):
        OandaCandleAdapter(_response(granularity="D"), eur_usd)


def test_pair_name_string_is_rejected():
    with pytest.raises(ValueError):
        OandaCandleAdapter(_response(), "EUR_USD")


def test_invalid_oanda_prices_are_rejected_by_candle(eur_usd):
    bad = [{"time": "2026-10-15T14:00:00.000000000Z", "volume": 10, "complete": True,
            "mid": {"o": "1.09", "h": "1.08", "l": "1.10", "c": "1.09"}}]
    with pytest.raises(ValueError):
        OandaCandleAdapter(_response(candles=bad), eur_usd).candles()
