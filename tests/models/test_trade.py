"""Tests for Trade (Phase 05, FR11). Fixed data only."""

import pytest

from tools.models import Order, Trade


@pytest.fixture
def buy_order(buy_plan, practice_account):
    # entry 1.0900, stop loss 1.0850 (risk 0.0050), TP1 1.1000, TP2 1.1050
    return Order(buy_plan, practice_account, confirmed=True)


@pytest.fixture
def sell_order(sell_plan, practice_account):
    # entry 1.2700, stop loss 1.2750 (risk 0.0050), TP1 1.2600, TP2 1.2550
    return Order(sell_plan, practice_account, confirmed=True)


@pytest.mark.parametrize("outcome, exit_price, r", [
    ("win", 1.1000, 2.0), ("win", 1.1050, 3.0), ("loss", 1.0850, -1.0),
])
def test_buy_trade_r_multiple(outcome, exit_price, r, buy_order):
    assert Trade(buy_order, outcome, exit_price).r_multiple() == pytest.approx(r)


@pytest.mark.parametrize("outcome, exit_price, r", [
    ("win", 1.2600, 2.0), ("win", 1.2550, 3.0), ("loss", 1.2750, -1.0),
])
def test_sell_trade_r_multiple(outcome, exit_price, r, sell_order):
    assert Trade(sell_order, outcome, exit_price).r_multiple() == pytest.approx(r)


def test_open_trade_has_no_exit_price_or_r_multiple(buy_order):
    trade = Trade(buy_order, "open")
    assert trade.outcome == "open"
    assert trade.exit_price is None
    assert trade.r_multiple() is None


def test_trade_knows_its_order(buy_order):
    trade = Trade(buy_order, "win", 1.1000)
    assert trade.order is buy_order
    assert trade.exit_price == 1.1


def test_open_trade_with_exit_price_is_rejected(buy_order):
    with pytest.raises(ValueError):
        Trade(buy_order, "open", 1.1000)


@pytest.mark.parametrize("outcome", ["win", "loss"])
@pytest.mark.parametrize("exit_price", [None, 0, -1.1, "1.10"])
def test_closed_trade_needs_valid_exit_price(outcome, exit_price, buy_order):
    with pytest.raises(ValueError):
        Trade(buy_order, outcome, exit_price)


@pytest.mark.parametrize("outcome", ["WIN", "closed", None])
def test_invalid_outcome_is_rejected(outcome, buy_order):
    with pytest.raises(ValueError):
        Trade(buy_order, outcome, 1.1000)


def test_order_must_be_an_order(buy_plan):
    with pytest.raises(ValueError):
        Trade(buy_plan, "open")


@pytest.mark.parametrize("exit_price", [1.0900, 1.0880, 1.0850])  # at entry (R 0) or below it
def test_buy_win_needs_positive_r_multiple(exit_price, buy_order):
    with pytest.raises(ValueError):
        Trade(buy_order, "win", exit_price)


@pytest.mark.parametrize("exit_price", [1.0900, 1.0920, 1.1000])  # at entry (R 0) or above it
def test_buy_loss_needs_negative_r_multiple(exit_price, buy_order):
    with pytest.raises(ValueError):
        Trade(buy_order, "loss", exit_price)


@pytest.mark.parametrize("outcome, exit_price", [
    ("win", 1.2700), ("win", 1.2750), ("loss", 1.2700), ("loss", 1.2600),
])
def test_sell_outcome_must_match_r_multiple_sign(outcome, exit_price, sell_order):
    with pytest.raises(ValueError):
        Trade(sell_order, outcome, exit_price)
