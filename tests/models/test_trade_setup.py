"""Phase 02 and 03 tests for TradeSetup. Fixed prices only; no OANDA API calls."""

import pytest

from tools.models import CurrencyPair, TradeSetup

NAN = float("nan")
INF = float("inf")

EUR_USD = CurrencyPair("EUR_USD", [(1.0850, 1.0800), (1.0900, 1.0840)])
GBP_USD = CurrencyPair("GBP_USD", [(1.2800, 1.2750), (1.2760, 1.2700)])
USD_JPY = CurrencyPair("USD_JPY", [(150.20, 149.80), (150.60, 149.70)])


def test_valid_buy_stores_values():
    setup = TradeSetup(EUR_USD, "buy", entry=1.0900, stop_loss=1.0850, take_profit=1.1000)

    assert setup.pair_name == "EUR_USD"
    assert setup.direction == "buy"
    assert setup.entry == 1.0900
    assert setup.stop_loss == 1.0850
    assert setup.take_profit == 1.1000


def test_valid_sell_stores_values():
    setup = TradeSetup(GBP_USD, "sell", entry=1.2700, stop_loss=1.2750, take_profit=1.2550)

    assert setup.pair_name == "GBP_USD"
    assert setup.direction == "sell"
    assert setup.entry == 1.2700
    assert setup.stop_loss == 1.2750
    assert setup.take_profit == 1.2550


def test_integer_prices_are_stored_as_floats():
    setup = TradeSetup(USD_JPY, "buy", entry=150, stop_loss=149, take_profit=153)

    assert isinstance(setup.entry, float)
    assert isinstance(setup.stop_loss, float)
    assert isinstance(setup.take_profit, float)


def test_pair_is_the_currency_pair_object_passed_in():
    setup = TradeSetup(EUR_USD, "buy", entry=1.0900, stop_loss=1.0850, take_profit=1.1000)

    assert setup.pair is EUR_USD
    assert setup.pair_name == EUR_USD.name


def test_setup_can_use_its_pair():
    setup = TradeSetup(EUR_USD, "buy", entry=1.0900, stop_loss=1.0850, take_profit=1.1000)

    assert setup.pair.market_structure() == "uptrend"


def test_pair_is_read_only():
    setup = TradeSetup(EUR_USD, "buy", entry=1.0900, stop_loss=1.0850, take_profit=1.1000)

    with pytest.raises(AttributeError):
        setup.pair = GBP_USD


@pytest.mark.parametrize("pair", ["EUR_USD", None, 1, ("EUR_USD", [(1.09, 1.08), (1.10, 1.09)])])
def test_pair_that_is_not_a_currency_pair_raises_value_error(pair):
    with pytest.raises(ValueError):
        TradeSetup(pair, "buy", entry=1.09, stop_loss=1.08, take_profit=1.11)


@pytest.mark.parametrize("direction", ["BUY", "long", "", None])
def test_wrong_direction_raises_value_error(direction):
    with pytest.raises(ValueError):
        TradeSetup(EUR_USD, direction, entry=1.09, stop_loss=1.08, take_profit=1.11)


@pytest.mark.parametrize("prices", [
    {"entry": NAN, "stop_loss": 1.08, "take_profit": 1.11},
    {"entry": 1.09, "stop_loss": NAN, "take_profit": 1.11},
    {"entry": 1.09, "stop_loss": 1.08, "take_profit": NAN},
    {"entry": 1.09, "stop_loss": 1.08, "take_profit": INF},
    {"entry": 1.09, "stop_loss": -INF, "take_profit": 1.11},
    {"entry": 1.09, "stop_loss": 0, "take_profit": 1.11},
    {"entry": 1.09, "stop_loss": -1.08, "take_profit": 1.11},
    {"entry": "1.09", "stop_loss": 1.08, "take_profit": 1.11},
    {"entry": True, "stop_loss": 1.08, "take_profit": 1.11},
])
def test_invalid_price_raises_value_error(prices):
    with pytest.raises(ValueError):
        TradeSetup(EUR_USD, "buy", **prices)


def test_sell_with_zero_take_profit_raises_value_error():
    with pytest.raises(ValueError):
        TradeSetup(EUR_USD, "sell", entry=1.09, stop_loss=1.10, take_profit=0)


@pytest.mark.parametrize("entry, stop_loss, take_profit", [
    (1.09, 1.10, 1.11),  # stop loss above entry
    (1.09, 1.08, 1.07),  # take profit below entry
    (1.09, 1.09, 1.11),  # stop loss equal to entry
    (1.09, 1.08, 1.09),  # take profit equal to entry
])
def test_buy_with_wrong_price_order_raises_value_error(entry, stop_loss, take_profit):
    with pytest.raises(ValueError):
        TradeSetup(EUR_USD, "buy", entry=entry, stop_loss=stop_loss, take_profit=take_profit)


@pytest.mark.parametrize("entry, stop_loss, take_profit", [
    (1.09, 1.08, 1.07),  # stop loss below entry
    (1.09, 1.10, 1.11),  # take profit above entry
    (1.09, 1.09, 1.07),  # stop loss equal to entry
    (1.09, 1.10, 1.09),  # take profit equal to entry
])
def test_sell_with_wrong_price_order_raises_value_error(entry, stop_loss, take_profit):
    with pytest.raises(ValueError):
        TradeSetup(EUR_USD, "sell", entry=entry, stop_loss=stop_loss, take_profit=take_profit)


def test_reward_to_risk_for_buy():
    setup = TradeSetup(USD_JPY, "buy", entry=150.0, stop_loss=149.0, take_profit=153.0)

    assert setup.reward_to_risk() == pytest.approx(3.0)


def test_reward_to_risk_for_sell():
    setup = TradeSetup(GBP_USD, "sell", entry=1.2700, stop_loss=1.2750, take_profit=1.2550)

    assert setup.reward_to_risk() == pytest.approx(3.0)


def test_reward_to_risk_below_two_is_returned_not_rejected():
    # FR2's minimum of 2 is deferred in Phase 02 (finding 7).
    setup = TradeSetup(USD_JPY, "buy", entry=150.0, stop_loss=148.0, take_profit=151.0)

    assert setup.reward_to_risk() == pytest.approx(0.5)
