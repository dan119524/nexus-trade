"""Shared CurrencyPair fixtures for the tests in tests/models/. Fixed prices only."""

import pytest

from tools.models import CurrencyPair


@pytest.fixture
def eur_usd():
    return CurrencyPair("EUR_USD", [(1.0850, 1.0800), (1.0900, 1.0840)])


@pytest.fixture
def gbp_usd():
    return CurrencyPair("GBP_USD", [(1.2800, 1.2750), (1.2760, 1.2700)])


@pytest.fixture
def usd_jpy():
    return CurrencyPair("USD_JPY", [(150.20, 149.80), (150.60, 149.70)])


# Phase 05 fixtures. Fixed data and a fake practice account only; nothing calls OANDA.

from datetime import datetime, timezone

from tools.models import Account, Signal, Timeframe, TimeframeAnalysis, TradePlan

T0 = datetime(2026, 10, 15, 14, 0, tzinfo=timezone.utc)


def make_signal(pair, m1, m5, h1, h4, min_score=3):
    """Return a Signal whose four analyses have the given trends and no structure events."""
    return Signal(TimeframeAnalysis(pair, Timeframe.M1, m1),
                  TimeframeAnalysis(pair, Timeframe.M5, m5),
                  TimeframeAnalysis(pair, Timeframe.H1, h1),
                  TimeframeAnalysis(pair, Timeframe.H4, h4),
                  min_score=min_score)


@pytest.fixture
def practice_account():
    return Account("FAKE-ACCOUNT-001", balance=5000, currency="USD",
                   environment="practice", risk_percent=1.0)


@pytest.fixture
def bullish_signal(eur_usd):
    return make_signal(eur_usd, "uptrend", "uptrend", "uptrend", "ranging")


@pytest.fixture
def bearish_signal(gbp_usd):
    return make_signal(gbp_usd, "downtrend", "downtrend", "ranging", "downtrend")


@pytest.fixture
def buy_plan(bullish_signal, practice_account):
    return TradePlan(bullish_signal, practice_account, entry=1.0900, stop_loss=1.0850,
                     take_profit_1=1.1000, take_profit_2=1.1050, lot_size=1.0,
                     risk_amount=50.0, reference_timeframe=Timeframe.H4)


@pytest.fixture
def sell_plan(bearish_signal, practice_account):
    return TradePlan(bearish_signal, practice_account, entry=1.2700, stop_loss=1.2750,
                     take_profit_1=1.2600, take_profit_2=1.2550, lot_size=0.5,
                     risk_amount=25.0, reference_timeframe=Timeframe.H1)
