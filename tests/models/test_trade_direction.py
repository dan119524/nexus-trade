"""Tests for TradeDirection, BuyDirection, and SellDirection (Phase 06, FR2 and FR3)."""

import pytest

from tools.models import BuyDirection, SellDirection, TradeDirection


def test_bare_trade_direction_cannot_be_created():
    with pytest.raises(TypeError):
        TradeDirection()


def test_both_directions_are_trade_directions():
    assert isinstance(BuyDirection(), TradeDirection)
    assert isinstance(SellDirection(), TradeDirection)


def test_names():
    assert BuyDirection().name == "buy"
    assert SellDirection().name == "sell"


def test_units_sign():
    assert BuyDirection().units_sign == 1
    assert SellDirection().units_sign == -1


@pytest.mark.parametrize("price, reference, buy_beyond, sell_beyond", [
    (1.11, 1.10, True, False),
    (1.09, 1.10, False, True),
    (1.10, 1.10, False, False),
])
def test_is_beyond(price, reference, buy_beyond, sell_beyond):
    assert BuyDirection().is_beyond(price, reference) is buy_beyond
    assert SellDirection().is_beyond(price, reference) is sell_beyond


def test_check_price_order():
    BuyDirection().check_price_order(1.10, 1.09, 1.12)
    SellDirection().check_price_order(1.10, 1.11, 1.08)
    with pytest.raises(ValueError):
        BuyDirection().check_price_order(1.10, 1.11, 1.08)
    with pytest.raises(ValueError):
        SellDirection().check_price_order(1.10, 1.09, 1.12)


def test_reward_and_risk():
    assert BuyDirection().reward(1.10, 1.12) == pytest.approx(0.02)
    assert BuyDirection().risk(1.10, 1.09) == pytest.approx(0.01)
    assert SellDirection().reward(1.10, 1.08) == pytest.approx(0.02)
    assert SellDirection().risk(1.10, 1.11) == pytest.approx(0.01)


def test_outcome_on_price_data():
    price_data = ((1.105, 1.095), (1.120, 1.100))
    assert BuyDirection().outcome(price_data, stop_loss=1.09, take_profit=1.12) == "win"
    assert SellDirection().outcome(price_data, stop_loss=1.11, take_profit=1.08) == "loss"
