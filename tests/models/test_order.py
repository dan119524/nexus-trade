"""Tests for Order (Phase 05, FR10). Nothing is sent to OANDA."""

import pytest

from tools.models import Account, Order, Timeframe, TradePlan


def test_buy_order_has_positive_units(buy_plan, practice_account):
    order = Order(buy_plan, practice_account, confirmed=True)
    assert order.units() == 100_000


def test_sell_order_has_negative_units(sell_plan, practice_account):
    assert Order(sell_plan, practice_account, confirmed=True).units() == -50_000


def test_fractional_lot_size_gives_exact_units(bullish_signal, practice_account):
    plan = TradePlan(bullish_signal, practice_account, entry=1.0900, stop_loss=1.0850,
                     take_profit_1=1.1000, take_profit_2=1.1050, lot_size=0.29,
                     risk_amount=14.5, reference_timeframe=Timeframe.H4)
    assert Order(plan, practice_account, confirmed=True).units() == 29_000


def test_order_type_is_market(buy_plan, practice_account):
    assert Order(buy_plan, practice_account, confirmed=True).order_type == "MARKET"


def test_order_knows_its_plan_and_account(buy_plan, practice_account):
    order = Order(buy_plan, practice_account, confirmed=True)
    assert order.plan is buy_plan
    assert order.account is practice_account


@pytest.mark.parametrize("confirmed", [False, None, "yes", 1])
def test_order_needs_explicit_confirmation(confirmed, buy_plan, practice_account):
    with pytest.raises(ValueError):
        Order(buy_plan, practice_account, confirmed=confirmed)


def test_plan_and_account_types_are_checked(buy_plan, practice_account):
    with pytest.raises(ValueError):
        Order("plan", practice_account, confirmed=True)
    with pytest.raises(ValueError):
        Order(buy_plan, "FAKE-ACCOUNT-001", confirmed=True)


def test_order_is_read_only(buy_plan, practice_account):
    order = Order(buy_plan, practice_account, confirmed=True)
    with pytest.raises(AttributeError):
        order.order_type = "LIMIT"


def test_account_must_be_the_plans_account(buy_plan):
    other = Account("FAKE-ACCOUNT-002", balance=5000, currency="USD",
                    environment="practice", risk_percent=1.0)
    with pytest.raises(ValueError):
        Order(buy_plan, other, confirmed=True)
