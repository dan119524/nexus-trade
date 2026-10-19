"""Tests for TradePlan (Phase 05, FR2 and FR9). Fake practice account only."""

import pytest

from tests.models.conftest import make_signal
from tools.models import Account, BuySetup, SellSetup, Timeframe, TradePlan


def make_plan(signal, account, **changes):
    values = {"entry": 1.0900, "stop_loss": 1.0850, "take_profit_1": 1.1000, "take_profit_2": 1.1050,
              "lot_size": 1.0, "risk_amount": 50.0, "reference_timeframe": Timeframe.H4}
    values.update(changes)
    return TradePlan(signal, account, **values)


def test_buy_plan_owns_a_buy_setup_on_the_signal_pair(buy_plan, bullish_signal):
    assert isinstance(buy_plan.setup, BuySetup)
    assert buy_plan.setup.pair is bullish_signal.pair
    assert (buy_plan.setup.entry, buy_plan.setup.stop_loss, buy_plan.setup.take_profit) == (1.09, 1.085, 1.10)


def test_sell_plan_owns_a_sell_setup(sell_plan, bearish_signal):
    assert isinstance(sell_plan.setup, SellSetup)
    assert sell_plan.setup.pair is bearish_signal.pair


def test_plan_stores_its_own_values(buy_plan, bullish_signal, practice_account):
    assert buy_plan.signal is bullish_signal
    assert buy_plan.account is practice_account
    assert buy_plan.take_profit_2 == 1.105
    assert buy_plan.lot_size == 1.0
    assert buy_plan.risk_amount == 50.0
    assert buy_plan.reference_timeframe is Timeframe.H4


def test_each_plan_creates_its_own_setup(bullish_signal, practice_account):
    first = make_plan(bullish_signal, practice_account)
    second = make_plan(bullish_signal, practice_account)
    assert first.setup is not second.setup


def test_invalid_signal_is_rejected(eur_usd, practice_account):
    tie = make_signal(eur_usd, "uptrend", "uptrend", "downtrend", "downtrend")
    with pytest.raises(ValueError):
        make_plan(tie, practice_account)


def test_reward_to_risk_below_2_is_rejected(bullish_signal, practice_account):
    with pytest.raises(ValueError):
        make_plan(bullish_signal, practice_account, take_profit_1=1.0990, take_profit_2=1.1050)


def test_reward_to_risk_rounding_to_2_is_accepted(bullish_signal, practice_account):
    # reward 0.0099999 / risk 0.005 = 1.99998, which rounds to 2.00
    plan = make_plan(bullish_signal, practice_account, take_profit_1=1.0999999)
    assert round(plan.setup.reward_to_risk(), 2) == 2.0


def test_reward_to_risk_rounding_to_1_99_is_rejected(bullish_signal, practice_account):
    # reward 0.00997 / risk 0.005 = 1.994, which rounds to 1.99
    with pytest.raises(ValueError):
        make_plan(bullish_signal, practice_account, take_profit_1=1.09997)


def test_wrong_price_order_for_signal_direction_is_rejected(bearish_signal, practice_account):
    # buy-ordered prices on a bearish (sell) signal
    with pytest.raises(ValueError):
        make_plan(bearish_signal, practice_account)


@pytest.mark.parametrize("take_profit_2", [1.1000, 1.0990])
def test_buy_tp2_must_be_above_tp1(take_profit_2, bullish_signal, practice_account):
    with pytest.raises(ValueError):
        make_plan(bullish_signal, practice_account, take_profit_2=take_profit_2)


@pytest.mark.parametrize("take_profit_2", [1.2600, 1.2610])
def test_sell_tp2_must_be_below_tp1(take_profit_2, bearish_signal, practice_account):
    with pytest.raises(ValueError):
        make_plan(bearish_signal, practice_account, entry=1.2700, stop_loss=1.2750,
                  take_profit_1=1.2600, take_profit_2=take_profit_2)


def test_risk_amount_above_account_maximum_is_rejected(bullish_signal, practice_account):
    with pytest.raises(ValueError):
        make_plan(bullish_signal, practice_account, risk_amount=50.01)


def test_risk_amount_equal_to_account_maximum_is_allowed(bullish_signal):
    account = Account("FAKE-ACCOUNT-002", balance=10000, currency="USD",
                      environment="practice", risk_percent=2)
    assert make_plan(bullish_signal, account, risk_amount=200.0).risk_amount == 200.0


@pytest.mark.parametrize("field, value", [
    ("lot_size", 0), ("lot_size", -1), ("risk_amount", 0), ("take_profit_2", "1.105"),
    ("reference_timeframe", "H4"),
])
def test_invalid_plan_values_are_rejected(field, value, bullish_signal, practice_account):
    with pytest.raises(ValueError):
        make_plan(bullish_signal, practice_account, **{field: value})


def test_signal_and_account_types_are_checked(bullish_signal, practice_account):
    with pytest.raises(ValueError):
        make_plan("bullish", practice_account)
    with pytest.raises(ValueError):
        make_plan(bullish_signal, "FAKE-ACCOUNT-001")
