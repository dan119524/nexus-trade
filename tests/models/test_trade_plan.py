"""Tests for TradePlan (Phases 05-06, FR2 and FR9). Fake practice accounts only."""

import pytest

from tests.models.conftest import make_signal
from tools.models import Account, BuyDirection, CurrencyPair, SellDirection, Timeframe, TradePlan

UP, DOWN, RANGE = "uptrend", "downtrend", "ranging"


def make_plan(signal, account, **changes):
    # 50 stop-loss pips on a USD-quote pair: $10 per pip per lot, so 0.1 lots risks $50
    values = {"entry": 1.0900, "stop_loss": 1.0850, "take_profit_1": 1.1000, "take_profit_2": 1.1050,
              "lot_size": 0.1}
    values.update(changes)
    return TradePlan(signal, account, **values)


def make_account(**changes):
    values = {"account_id": "FAKE-ACCOUNT-002", "balance": 5000, "currency": "USD",
              "environment": "practice", "risk_percent": 1.0}
    values.update(changes)
    return Account(**values)


def test_buy_plan_owns_a_buy_setup_on_the_signal_pair(buy_plan, bullish_signal):
    assert isinstance(buy_plan.setup.trade_direction, BuyDirection)
    assert buy_plan.setup.direction == "buy"
    assert buy_plan.setup.pair is bullish_signal.pair
    assert (buy_plan.setup.entry, buy_plan.setup.stop_loss, buy_plan.setup.take_profit) == (1.09, 1.085, 1.10)


def test_sell_plan_owns_a_sell_setup(sell_plan, bearish_signal):
    assert isinstance(sell_plan.setup.trade_direction, SellDirection)
    assert sell_plan.setup.direction == "sell"
    assert sell_plan.setup.pair is bearish_signal.pair


def test_plan_stores_its_own_values(buy_plan, bullish_signal, practice_account):
    assert buy_plan.signal is bullish_signal
    assert buy_plan.account is practice_account
    assert buy_plan.take_profit_2 == 1.105
    assert buy_plan.lot_size == 0.1


def test_each_plan_creates_its_own_setup(bullish_signal, practice_account):
    first = make_plan(bullish_signal, practice_account)
    second = make_plan(bullish_signal, practice_account)
    assert first.setup is not second.setup


# Risk amount (FR9): lot size × stop-loss pips × pip value per lot

def test_stop_loss_pips_are_rounded_to_1_decimal(buy_plan):
    # 1.0900 − 1.0850 is 0.004999999999999893 in floating point
    assert buy_plan.stop_loss_pips == 50.0


def test_risk_amount_is_derived_from_lot_size(buy_plan, sell_plan):
    assert buy_plan.risk_amount == 50.0   # 0.1 × 50 × 10
    assert sell_plan.risk_amount == 25.0  # 0.05 × 50 × 10


def test_risk_amount_equal_to_account_maximum_is_allowed(buy_plan, practice_account):
    assert buy_plan.risk_amount == practice_account.max_risk_amount()


def test_risk_amount_above_account_maximum_is_rejected(bullish_signal, practice_account):
    with pytest.raises(ValueError):
        make_plan(bullish_signal, practice_account, lot_size=0.11)  # $55 > $50


def test_lot_size_with_huge_risk_is_rejected(bullish_signal, practice_account):
    with pytest.raises(ValueError):
        make_plan(bullish_signal, practice_account, lot_size=100.0)  # $50,000


def test_usd_jpy_uses_its_pip_size_and_pip_value(practice_account):
    usd_jpy = CurrencyPair("USD_JPY", [(150.20, 149.80), (150.60, 149.70)])
    signal = make_signal(usd_jpy, UP, UP, UP, UP)
    plan = make_plan(signal, practice_account, entry=150.00, stop_loss=149.50,
                     take_profit_1=151.00, take_profit_2=151.50, lot_size=0.1)
    assert plan.stop_loss_pips == 50.0
    assert plan.risk_amount == 33.33  # 0.1 × 50 × 6.6667 (1,000 / 150 to 4 decimals) = 33.3335, in cents


def test_risk_is_rounded_to_cents_so_an_exactly_at_limit_plan_passes(practice_account):
    # 0.15 × 50 × 6.6667 = 50.00025, which rounds to $50.00, the account's maximum
    usd_jpy = CurrencyPair("USD_JPY", [(150.20, 149.80), (150.60, 149.70)])
    signal = make_signal(usd_jpy, UP, UP, UP, UP)
    plan = make_plan(signal, practice_account, entry=150.00, stop_loss=149.50,
                     take_profit_1=151.00, take_profit_2=151.50, lot_size=0.15)
    assert plan.risk_amount == 50.00 == practice_account.max_risk_amount()


def test_risk_one_cent_over_the_maximum_is_rejected(bullish_signal):
    # max = 4,999 × 1% = $49.99; 0.1 lots × 50 pips × $10 = $50.00, one cent over
    account = make_account(balance=4999)
    assert account.max_risk_amount() == pytest.approx(49.99)
    with pytest.raises(ValueError):
        make_plan(bullish_signal, account, lot_size=0.1)


def test_usd_base_pair_uses_10_divided_by_price(practice_account):
    usd_cad = CurrencyPair("USD_CAD", [(1.3650, 1.3600), (1.3680, 1.3620)])
    plan = make_plan(make_signal(usd_cad, UP, UP, UP, UP), practice_account, entry=1.3600,
                     stop_loss=1.3550, take_profit_1=1.3700, take_profit_2=1.3750, lot_size=0.1)
    assert plan.risk_amount == 36.76  # 0.1 × 50 × 7.3529 (10 / 1.36 to 4 decimals) = 36.7645, in cents


def test_cross_pair_is_rejected(practice_account):
    eur_gbp = CurrencyPair("EUR_GBP", [(0.8550, 0.8500), (0.8580, 0.8520)])
    with pytest.raises(ValueError):
        make_plan(make_signal(eur_gbp, UP, UP, UP, UP), practice_account, entry=0.8500,
                  stop_loss=0.8450, take_profit_1=0.8600, take_profit_2=0.8650, lot_size=0.01)


def test_non_usd_account_is_rejected(bullish_signal):
    with pytest.raises(ValueError):
        make_plan(bullish_signal, make_account(currency="EUR"))


def test_risk_amount_and_reference_timeframe_are_not_parameters(bullish_signal, practice_account):
    with pytest.raises(TypeError):
        make_plan(bullish_signal, practice_account, risk_amount=50.0)
    with pytest.raises(TypeError):
        make_plan(bullish_signal, practice_account, reference_timeframe=Timeframe.H4)


# Reference timeframe (FR9): the highest timeframe that voted with the signal

def test_reference_timeframe_comes_from_the_signal(buy_plan, sell_plan):
    assert buy_plan.reference_timeframe is Timeframe.H1   # bullish signal: H4 is neutral
    assert sell_plan.reference_timeframe is Timeframe.H4  # bearish signal: H4 voted bearish


def test_reference_timeframe_is_h4_when_h4_agrees(eur_usd, practice_account):
    plan = make_plan(make_signal(eur_usd, UP, UP, RANGE, UP), practice_account)
    assert plan.reference_timeframe is Timeframe.H4


# Signal, reward-to-risk, and TP2 (Phase 05)

def test_invalid_signal_is_rejected(eur_usd, practice_account):
    tie = make_signal(eur_usd, UP, UP, DOWN, DOWN)
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
                  take_profit_1=1.2600, take_profit_2=take_profit_2, lot_size=0.05)


@pytest.mark.parametrize("field, value", [
    ("lot_size", 0), ("lot_size", -1), ("lot_size", "0.1"), ("take_profit_2", "1.105"),
])
def test_invalid_plan_values_are_rejected(field, value, bullish_signal, practice_account):
    with pytest.raises(ValueError):
        make_plan(bullish_signal, practice_account, **{field: value})


def test_signal_and_account_types_are_checked(bullish_signal, practice_account):
    with pytest.raises(ValueError):
        make_plan("bullish", practice_account)
    with pytest.raises(ValueError):
        make_plan(bullish_signal, "FAKE-ACCOUNT-001")


# Lot size steps (Phase 06 final review A2)

@pytest.mark.parametrize("lot_size", [1e-12, 0.000001, 0.009, 0.015, 0.105, 0.0999])  # 1e-12 is caught only by the minimum
def test_lot_size_must_be_at_least_0_01_in_steps_of_0_01(lot_size, bullish_signal, practice_account):
    with pytest.raises(ValueError):
        make_plan(bullish_signal, practice_account, lot_size=lot_size)


@pytest.mark.parametrize("lot_size", [0.01, 0.05, 0.07, 0.1])
def test_lot_sizes_in_0_01_steps_are_accepted(lot_size, bullish_signal, practice_account):
    # 0.07 × 100 is 7.000000000000001 in floating point
    assert make_plan(bullish_signal, practice_account, lot_size=lot_size).lot_size == lot_size
