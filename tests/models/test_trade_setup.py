"""Phase 02-04 tests for TradeSetup, BuySetup, and SellSetup. Fixed prices only; no OANDA API calls."""

import pytest

from tools.models import BuySetup, SellSetup, TradeSetup

NAN = float("nan")
INF = float("inf")


def test_valid_buy_stores_values(eur_usd):
    setup = BuySetup(eur_usd, entry=1.0900, stop_loss=1.0850, take_profit=1.1000)

    assert setup.pair_name == "EUR_USD"
    assert setup.direction == "buy"
    assert setup.entry == 1.0900
    assert setup.stop_loss == 1.0850
    assert setup.take_profit == 1.1000


def test_valid_sell_stores_values(gbp_usd):
    setup = SellSetup(gbp_usd, entry=1.2700, stop_loss=1.2750, take_profit=1.2550)

    assert setup.pair_name == "GBP_USD"
    assert setup.direction == "sell"
    assert setup.entry == 1.2700
    assert setup.stop_loss == 1.2750
    assert setup.take_profit == 1.2550


def test_integer_prices_are_stored_as_floats(usd_jpy):
    setup = BuySetup(usd_jpy, entry=150, stop_loss=149, take_profit=153)

    assert isinstance(setup.entry, float)
    assert isinstance(setup.stop_loss, float)
    assert isinstance(setup.take_profit, float)


def test_pair_is_the_currency_pair_object_passed_in(eur_usd):
    setup = BuySetup(eur_usd, entry=1.0900, stop_loss=1.0850, take_profit=1.1000)

    assert setup.pair is eur_usd
    assert setup.pair_name == eur_usd.name


def test_setup_can_use_its_pair(eur_usd):
    setup = BuySetup(eur_usd, entry=1.0900, stop_loss=1.0850, take_profit=1.1000)

    assert setup.pair.market_structure() == "uptrend"


def test_pair_is_read_only(eur_usd, gbp_usd):
    setup = BuySetup(eur_usd, entry=1.0900, stop_loss=1.0850, take_profit=1.1000)

    with pytest.raises(AttributeError):
        setup.pair = gbp_usd


@pytest.mark.parametrize("pair", ["EUR_USD", None, 1, ("EUR_USD", [(1.09, 1.08), (1.10, 1.09)])])
def test_pair_that_is_not_a_currency_pair_raises_value_error(pair):
    with pytest.raises(ValueError):
        BuySetup(pair, entry=1.09, stop_loss=1.08, take_profit=1.11)


def test_bare_trade_setup_cannot_be_created(eur_usd):
    with pytest.raises(NotImplementedError):
        TradeSetup(eur_usd, entry=1.09, stop_loss=1.08, take_profit=1.11)


def test_buy_and_sell_setups_are_trade_setups(eur_usd):
    buy = BuySetup(eur_usd, entry=1.0900, stop_loss=1.0850, take_profit=1.1000)
    sell = SellSetup(eur_usd, entry=1.0900, stop_loss=1.0950, take_profit=1.0800)

    assert isinstance(buy, TradeSetup)
    assert isinstance(sell, TradeSetup)


def test_direction_is_read_only(eur_usd):
    setup = BuySetup(eur_usd, entry=1.0900, stop_loss=1.0850, take_profit=1.1000)

    with pytest.raises(AttributeError):
        setup.direction = "sell"


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
def test_invalid_price_raises_value_error(prices, eur_usd):
    with pytest.raises(ValueError):
        BuySetup(eur_usd, **prices)


def test_sell_with_zero_take_profit_raises_value_error(eur_usd):
    with pytest.raises(ValueError):
        SellSetup(eur_usd, entry=1.09, stop_loss=1.10, take_profit=0)


@pytest.mark.parametrize("entry, stop_loss, take_profit", [
    (1.09, 1.10, 1.11),  # stop loss above entry
    (1.09, 1.08, 1.07),  # take profit below entry
    (1.09, 1.09, 1.11),  # stop loss equal to entry
    (1.09, 1.08, 1.09),  # take profit equal to entry
])
def test_buy_with_wrong_price_order_raises_value_error(entry, stop_loss, take_profit, eur_usd):
    with pytest.raises(ValueError):
        BuySetup(eur_usd, entry=entry, stop_loss=stop_loss, take_profit=take_profit)


@pytest.mark.parametrize("entry, stop_loss, take_profit", [
    (1.09, 1.08, 1.07),  # stop loss below entry
    (1.09, 1.10, 1.11),  # take profit above entry
    (1.09, 1.09, 1.07),  # stop loss equal to entry
    (1.09, 1.10, 1.09),  # take profit equal to entry
])
def test_sell_with_wrong_price_order_raises_value_error(entry, stop_loss, take_profit, eur_usd):
    with pytest.raises(ValueError):
        SellSetup(eur_usd, entry=entry, stop_loss=stop_loss, take_profit=take_profit)


def test_reward_and_risk_for_buy(usd_jpy):
    setup = BuySetup(usd_jpy, entry=150.0, stop_loss=149.0, take_profit=153.0)

    assert setup.reward() == pytest.approx(3.0)
    assert setup.risk() == pytest.approx(1.0)


def test_reward_and_risk_for_sell(gbp_usd):
    setup = SellSetup(gbp_usd, entry=1.2700, stop_loss=1.2750, take_profit=1.2550)

    assert setup.reward() == pytest.approx(0.0150)
    assert setup.risk() == pytest.approx(0.0050)


def test_reward_to_risk_for_buy(usd_jpy):
    setup = BuySetup(usd_jpy, entry=150.0, stop_loss=149.0, take_profit=153.0)

    assert setup.reward_to_risk() == pytest.approx(3.0)


def test_reward_to_risk_for_sell(gbp_usd):
    setup = SellSetup(gbp_usd, entry=1.2700, stop_loss=1.2750, take_profit=1.2550)

    assert setup.reward_to_risk() == pytest.approx(3.0)


def test_reward_to_risk_below_two_is_returned_not_rejected(usd_jpy):
    # FR2's minimum of 2 is deferred in Phase 02 (finding 7).
    setup = BuySetup(usd_jpy, entry=150.0, stop_loss=148.0, take_profit=151.0)

    assert setup.reward_to_risk() == pytest.approx(0.5)
