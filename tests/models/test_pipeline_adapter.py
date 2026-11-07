"""Tests for PipelineAdapter (Phase 09 Adapter). Fixed pipeline dicts only; nothing calls OANDA."""

from datetime import datetime, timezone

import pytest

from tools.models import (
    Account, BreakOfStructure, ChangeOfCharacter, CurrencyPair, PipelineAdapter, Signal, Timeframe,
)

T = "2026-10-15T14:00:00.000000000Z"


def _candles(close=1.0900, count=3):
    return [{"time": T, "open": close, "high": close + 0.0010, "low": close - 0.0010, "close": close}
            for _ in range(count)]


def _adapter(timeframes, candles_by_tf=None):
    candles_by_tf = candles_by_tf or {tf: _candles() for tf in ("M1", "M5", "H1", "H4")}
    return PipelineAdapter("EUR_USD", {"timeframes": timeframes}, candles_by_tf, price_timeframe="H1")


def test_pair_comes_from_the_price_timeframe_candles():
    pair = _adapter({}).pair()
    assert isinstance(pair, CurrencyPair)
    assert pair.name == "EUR_USD"
    assert len(pair.price_data) == 3
    assert pair.price_data[0] == pytest.approx((1.091, 1.089))


def test_pipeline_trends_become_domain_trends():
    signal = _adapter({"M1": {"trend": "bullish"}, "M5": {"trend": "bearish"},
                       "H1": {"trend": "ranging"}, "H4": {"trend": "bullish"}}).signal()
    assert isinstance(signal, Signal)
    assert (signal.m1.trend, signal.m5.trend, signal.h1.trend, signal.h4.trend) == \
        ("uptrend", "downtrend", "ranging", "uptrend")


def test_missing_timeframe_is_a_neutral_vote():
    signal = _adapter({"M1": {"trend": "bullish"}, "M5": {"trend": "bullish"},
                       "H1": {"trend": "bullish"}}).signal()
    assert signal.h4.trend == "ranging" and signal.h4.latest_event is None
    assert signal.h4.vote() == "neutral"
    assert signal.direction() == "bullish" and signal.score() == 3 and signal.is_valid()


def test_signal_uses_the_minimum_score():
    signal = _adapter({"M1": {"trend": "bullish"}, "M5": {"trend": "bullish"},
                       "H1": {"trend": "bullish"}}).signal(min_score=4)
    assert not signal.is_valid()


def test_latest_bos_becomes_a_break_of_structure():
    h1_candles = _candles(close=1.0900) + [{"time": T, "open": 1.0950, "high": 1.0975,
                                            "low": 1.0945, "close": 1.0970}]
    bos = {"event_type": "BOS", "direction": "bullish", "level": 1.0960,
           "broken_at_time": "2026-10-15T18:00:00.000000000Z", "broken_at_bar": 3,
           "source_swing": {"price": 1.0960, "time": T, "label": "HH", "type": "high"}}
    old_choch = {"event_type": "CHoCH", "direction": "bearish", "level": 1.0880,
                 "broken_at_time": T, "broken_at_bar": 1,
                 "source_swing": {"price": 1.0950, "time": T, "label": "HL", "type": "low"}}
    candles = {tf: _candles() for tf in ("M1", "M5", "H4")}
    candles["H1"] = h1_candles
    signal = _adapter({"H1": {"trend": "ranging", "bos_events": [bos], "choch_events": [old_choch]}},
                      candles).signal()
    event = signal.h1.latest_event
    assert isinstance(event, BreakOfStructure)
    assert event.swing.label == "HH" and event.swing.price == 1.0960
    assert event.swing.timeframe is Timeframe.H1 and event.swing.pair is signal.pair
    assert event.time == datetime(2026, 10, 15, 18, 0, tzinfo=timezone.utc)
    assert event.close == 1.0970 and event.direction == "bullish"
    assert signal.h1.vote() == "bullish"


def test_choch_becomes_a_change_of_character():
    choch = {"event_type": "CHoCH", "direction": "bearish", "level": 1.0950,
             "broken_at_time": T, "broken_at_bar": 2,
             "source_swing": {"price": 1.0950, "time": T, "label": "HL", "type": "low"}}
    signal = _adapter({"M5": {"trend": "bullish", "choch_events": [choch]}}).signal()
    assert isinstance(signal.m5.latest_event, ChangeOfCharacter)
    assert signal.m5.vote() == "neutral"


def test_unknown_trend_is_rejected():
    with pytest.raises(ValueError):
        _adapter({"H1": {"trend": "sideways"}}).signal()


def test_account_comes_from_fetch_account_data():
    account = _adapter({}).account({"account_id": "FAKE-ACCOUNT", "balance": 5000.0,
                                    "currency": "USD", "env": "practice"}, risk_percent=1.0)
    assert isinstance(account, Account)
    assert (account.account_id, account.balance, account.currency, account.environment) == \
        ("FAKE-ACCOUNT", 5000.0, "USD", "practice")
    assert account.max_risk_amount() == 50.0


def test_live_account_is_rejected():
    with pytest.raises(ValueError):
        _adapter({}).account({"account_id": "X", "balance": 5000.0, "currency": "USD", "env": "live"}, 1.0)


def test_fewer_than_two_candles_is_rejected():
    with pytest.raises(ValueError):
        PipelineAdapter("EUR_USD", {"timeframes": {}}, {"H1": _candles(count=1)}, price_timeframe="H1")
