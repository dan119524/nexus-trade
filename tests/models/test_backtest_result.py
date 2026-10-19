"""Tests for BacktestResult and its trade setups (Phases 02-06, FR3). Fixed prices only; no OANDA API calls."""

from datetime import date

import pytest

from tools.models import BacktestResult, BuyDirection, CurrencyPair, SellDirection, TradeSetup

TEST_DATE = date(2026, 10, 15)

# eur_usd price data: (1.0850, 1.0800), then (1.0900, 1.0840)


def buy(pair, stop_loss, take_profit, entry=1.0820):
    return TradeSetup(pair, BuyDirection(), entry=entry, stop_loss=stop_loss, take_profit=take_profit)


def sell(pair, stop_loss, take_profit, entry=1.0870):
    return TradeSetup(pair, SellDirection(), entry=entry, stop_loss=stop_loss, take_profit=take_profit)


def buy_win(pair):
    return buy(pair, stop_loss=1.0790, take_profit=1.0880)


def buy_loss(pair):
    return buy(pair, stop_loss=1.0805, take_profit=1.0950)


def buy_open(pair):
    return buy(pair, stop_loss=1.0700, take_profit=1.1000)


def sell_win(pair):
    return sell(pair, stop_loss=1.0950, take_profit=1.0800)


def sell_loss(pair):
    return sell(pair, stop_loss=1.0890, take_profit=1.0700)


def test_fixture_setups_have_the_expected_outcomes(eur_usd):
    assert [s.outcome() for s in (buy_win(eur_usd), buy_loss(eur_usd), buy_open(eur_usd),
                                  sell_win(eur_usd), sell_loss(eur_usd))] == \
        ["win", "loss", "open", "win", "loss"]


def test_new_result_stores_values_and_has_no_setups(eur_usd):
    result = BacktestResult(eur_usd, TEST_DATE)

    assert result.pair is eur_usd
    assert result.pair_name == "EUR_USD"
    assert result.test_date == TEST_DATE
    assert result.setups == ()
    assert (result.setups_tested, result.trade_count, result.win_count) == (0, 0, 0)
    assert result.win_rate() is None


def test_counts_come_from_setup_outcomes(eur_usd):
    result = BacktestResult(eur_usd, TEST_DATE)
    for setup in (buy_win(eur_usd), buy_loss(eur_usd), buy_open(eur_usd), sell_win(eur_usd), sell_loss(eur_usd)):
        result.add_setup(setup)

    assert result.setups_tested == 5
    assert result.trade_count == 4
    assert result.win_count == 2
    assert result.win_rate() == pytest.approx(0.5)


def test_open_setups_are_not_trades(eur_usd):
    result = BacktestResult(eur_usd, TEST_DATE)
    result.add_setup(buy_open(eur_usd))

    assert result.setups_tested == 1
    assert result.trade_count == 0
    assert result.win_rate() is None


def test_win_rate_is_zero_when_no_trade_wins(eur_usd):
    result = BacktestResult(eur_usd, TEST_DATE)
    result.add_setup(buy_loss(eur_usd))
    result.add_setup(sell_loss(eur_usd))

    assert result.win_rate() == 0.0


def test_win_rate_is_one_when_every_trade_wins(eur_usd):
    result = BacktestResult(eur_usd, TEST_DATE)
    result.add_setup(buy_win(eur_usd))
    result.add_setup(sell_win(eur_usd))

    assert result.win_rate() == 1.0


def test_setups_are_returned_as_a_tuple_in_added_order(eur_usd):
    first, second = buy_win(eur_usd), sell_loss(eur_usd)
    result = BacktestResult(eur_usd, TEST_DATE)
    result.add_setup(first)
    result.add_setup(second)

    setups = result.setups
    assert isinstance(setups, tuple)
    assert setups[0] is first and setups[1] is second


def test_returned_setups_cannot_change_the_backtest(eur_usd):
    result = BacktestResult(eur_usd, TEST_DATE)
    result.add_setup(buy_win(eur_usd))

    with pytest.raises(AttributeError):
        result.setups.append(buy_loss(eur_usd))
    assert result.setups_tested == 1


def test_setups_is_read_only(eur_usd):
    result = BacktestResult(eur_usd, TEST_DATE)
    with pytest.raises(AttributeError):
        result.setups = ()


def test_setup_on_another_pair_is_rejected(eur_usd, gbp_usd):
    result = BacktestResult(eur_usd, TEST_DATE)
    with pytest.raises(ValueError):
        result.add_setup(sell(gbp_usd, stop_loss=1.2750, take_profit=1.2550, entry=1.2700))


def test_setup_on_a_different_pair_object_with_the_same_name_is_rejected(eur_usd):
    other = CurrencyPair("EUR_USD", [(1.0850, 1.0800), (1.0900, 1.0840)])
    result = BacktestResult(eur_usd, TEST_DATE)
    with pytest.raises(ValueError):
        result.add_setup(buy_win(other))


def test_same_setup_cannot_be_added_twice(eur_usd):
    setup = buy_win(eur_usd)
    result = BacktestResult(eur_usd, TEST_DATE)
    result.add_setup(setup)

    with pytest.raises(ValueError):
        result.add_setup(setup)
    assert result.setups_tested == 1


def test_equal_but_separate_setups_can_both_be_added(eur_usd):
    result = BacktestResult(eur_usd, TEST_DATE)
    result.add_setup(buy_win(eur_usd))
    result.add_setup(buy_win(eur_usd))

    assert result.setups_tested == 2


@pytest.mark.parametrize("setup", ["setup", None, 1.09])
def test_non_setup_is_rejected(setup, eur_usd):
    with pytest.raises(ValueError):
        BacktestResult(eur_usd, TEST_DATE).add_setup(setup)


def test_remove_setup_updates_the_counts(eur_usd):
    win, loss = buy_win(eur_usd), buy_loss(eur_usd)
    result = BacktestResult(eur_usd, TEST_DATE)
    result.add_setup(win)
    result.add_setup(loss)

    result.remove_setup(loss)

    assert result.setups == (win,)
    assert (result.setups_tested, result.trade_count, result.win_count) == (1, 1, 1)


def test_remove_only_removes_that_setup_object(eur_usd):
    first, second = buy_win(eur_usd), buy_win(eur_usd)
    result = BacktestResult(eur_usd, TEST_DATE)
    result.add_setup(first)
    result.add_setup(second)

    result.remove_setup(first)

    assert result.setups == (second,)


def test_removing_a_setup_it_does_not_hold_is_rejected(eur_usd):
    result = BacktestResult(eur_usd, TEST_DATE)
    with pytest.raises(ValueError):
        result.remove_setup(buy_win(eur_usd))


def test_pair_is_read_only(eur_usd, gbp_usd):
    result = BacktestResult(eur_usd, TEST_DATE)
    with pytest.raises(AttributeError):
        result.pair = gbp_usd


@pytest.mark.parametrize("pair", ["EUR_USD", None, 1, ("EUR_USD", [(1.09, 1.08), (1.10, 1.09)])])
def test_pair_that_is_not_a_currency_pair_raises_value_error(pair):
    with pytest.raises(ValueError):
        BacktestResult(pair, TEST_DATE)


@pytest.mark.parametrize("test_date", ["2026-10-15", None, 20261015])
def test_test_date_that_is_not_a_date_raises_value_error(test_date, eur_usd):
    with pytest.raises(ValueError):
        BacktestResult(eur_usd, test_date)
