"""Phase 02-06 tests for CurrencyPair and rank_pairs. Fixed price data only; no OANDA API calls."""

from datetime import date

import pytest

from tools.models import BacktestResult, BuyDirection, CurrencyPair, TradeSetup, rank_pairs

NAN = float("nan")
INF = float("inf")


def test_valid_construction_stores_name_and_price_data():
    pair = CurrencyPair("EUR_USD", [(1.0850, 1.0800), (1.0900, 1.0840)])

    assert pair.name == "EUR_USD"
    assert pair.price_data == ((1.0850, 1.0800), (1.0900, 1.0840))


def test_integer_prices_are_stored_as_floats():
    pair = CurrencyPair("USD_JPY", [(151, 150), (152, 151)])

    assert pair.price_data == ((151.0, 150.0), (152.0, 151.0))
    assert all(isinstance(price, float) for point in pair.price_data for price in point)


def test_high_equal_to_low_is_allowed():
    pair = CurrencyPair("EUR_USD", [(1.08, 1.08), (1.09, 1.09)])

    assert pair.price_data == ((1.08, 1.08), (1.09, 1.09))


@pytest.mark.parametrize("name", ["EUR/USD", "eur_usd", "EURUSD", "EUR_US", "EUR_EUR", "", None, 123])
def test_invalid_name_raises_value_error(name):
    with pytest.raises(ValueError):
        CurrencyPair(name, [(1.09, 1.08), (1.10, 1.09)])


@pytest.mark.parametrize("price_data", [[], [(1.09, 1.08)], iter([]), iter([(1.09, 1.08)])])
def test_fewer_than_two_price_points_raises_value_error(price_data):
    with pytest.raises(ValueError):
        CurrencyPair("EUR_USD", price_data)


def test_non_iterable_price_data_raises_value_error():
    with pytest.raises(ValueError):
        CurrencyPair("EUR_USD", 5)


@pytest.mark.parametrize("point", [[1.09, 1.08], (1.09,), (1.09, 1.08, 1.07), "ab"])
def test_price_point_that_is_not_a_high_low_tuple_raises_value_error(point):
    with pytest.raises(ValueError):
        CurrencyPair("EUR_USD", [(1.09, 1.08), point])


@pytest.mark.parametrize("point", [
    (NAN, 1.08), (1.09, NAN),
    (INF, 1.08), (1.09, -INF),
    (0, 0), (1.09, 0), (1.09, -1.08),
    ("1.09", 1.08), (True, 1.08),
])
def test_invalid_price_raises_value_error(point):
    with pytest.raises(ValueError):
        CurrencyPair("EUR_USD", [(1.09, 1.08), point])


def test_high_below_low_raises_value_error():
    with pytest.raises(ValueError):
        CurrencyPair("EUR_USD", [(1.09, 1.08), (1.07, 1.08)])


def test_market_structure_uptrend_with_higher_highs_and_higher_lows():
    pair = CurrencyPair("EUR_USD", [(1.0850, 1.0800), (1.0900, 1.0840), (1.0950, 1.0880)])

    assert pair.market_structure() == "uptrend"


def test_market_structure_downtrend_with_lower_highs_and_lower_lows():
    pair = CurrencyPair("GBP_USD", [(1.2800, 1.2750), (1.2760, 1.2700), (1.2720, 1.2650)])

    assert pair.market_structure() == "downtrend"


@pytest.mark.parametrize("price_data", [
    # higher high, then lower high
    [(150.20, 149.80), (150.60, 149.70), (150.40, 150.00)],
    # higher high but lower low (outside bar)
    [(1.09, 1.08), (1.10, 1.07)],
    # equal high counts as ranging (FR1 strict rule)
    [(1.09, 1.08), (1.09, 1.085)],
    # equal low counts as ranging
    [(1.09, 1.08), (1.10, 1.08)],
    # uptrend that breaks on the last point
    [(1.08, 1.07), (1.09, 1.08), (1.10, 1.09), (1.095, 1.091)],
])
def test_market_structure_ranging_when_not_strictly_trending(price_data):
    pair = CurrencyPair("USD_JPY" if price_data[0][0] > 100 else "EUR_USD", price_data)

    assert pair.market_structure() == "ranging"


# Pip size and pip value (Phase 06, FR9)

@pytest.mark.parametrize("name, pip", [("EUR_USD", 0.0001), ("USD_CAD", 0.0001), ("USD_JPY", 0.01), ("GBP_JPY", 0.01)])
def test_pip_size(name, pip):
    assert CurrencyPair(name, [(1.1, 1.0), (1.2, 1.1)]).pip_size() == pip


@pytest.mark.parametrize("name", ["EUR_USD", "GBP_USD", "AUD_USD", "NZD_USD"])
def test_usd_quote_pip_value_is_10(name):
    assert CurrencyPair(name, [(1.1, 1.0), (1.2, 1.1)]).pip_value_per_lot(1.08) == 10.0


def test_usd_jpy_pip_value_is_1000_divided_by_price():
    assert CurrencyPair("USD_JPY", [(151, 150), (152, 151)]).pip_value_per_lot(150.0) == round(1000 / 150, 4)


@pytest.mark.parametrize("name, price", [("USD_CHF", 0.88), ("USD_CAD", 1.36), ("USD_SGD", 1.34)])
def test_other_usd_base_pip_value_is_10_divided_by_price(name, price):
    assert CurrencyPair(name, [(1.1, 1.0), (1.2, 1.1)]).pip_value_per_lot(price) == round(10 / price, 4)


@pytest.mark.parametrize("name", ["EUR_GBP", "GBP_JPY", "EUR_JPY", "USD_HKD"])
def test_cross_pair_has_no_pip_value(name):
    with pytest.raises(ValueError):
        CurrencyPair(name, [(1.1, 1.0), (1.2, 1.1)]).pip_value_per_lot(1.0)


@pytest.mark.parametrize("price", [0, -1.0, "1.08", None, NAN])
def test_pip_value_needs_a_positive_price(price):
    with pytest.raises(ValueError):
        CurrencyPair("EUR_USD", [(1.1, 1.0), (1.2, 1.1)]).pip_value_per_lot(price)


# Backtest results (Phase 06, FR4)

PRICES = [(1.0850, 1.0800), (1.0900, 1.0840)]
TEST_DATE = date(2026, 10, 15)


def win(pair):
    return TradeSetup(pair, BuyDirection(), entry=1.0820, stop_loss=1.0790, take_profit=1.0880)


def loss(pair):
    return TradeSetup(pair, BuyDirection(), entry=1.0820, stop_loss=1.0805, take_profit=1.0950)


def still_open(pair):
    return TradeSetup(pair, BuyDirection(), entry=1.0820, stop_loss=1.0700, take_profit=1.1000)


def backtest(pair, *setup_makers):
    result = BacktestResult(pair, TEST_DATE)
    for make in setup_makers:
        result.add_setup(make(pair))
    return result


def test_new_pair_has_no_backtests(eur_usd):
    assert eur_usd.backtests == ()
    assert eur_usd.latest_backtest() is None


def test_backtests_are_returned_as_a_tuple_and_latest_is_the_last_added(eur_usd):
    first, second = backtest(eur_usd, win), backtest(eur_usd, loss)
    eur_usd.add_backtest(first)
    eur_usd.add_backtest(second)

    assert eur_usd.backtests == (first, second)
    assert isinstance(eur_usd.backtests, tuple)
    assert eur_usd.latest_backtest() is second


def test_returned_backtests_cannot_change_the_pair(eur_usd):
    eur_usd.add_backtest(backtest(eur_usd, win))
    with pytest.raises(AttributeError):
        eur_usd.backtests.append(backtest(eur_usd, loss))
    assert len(eur_usd.backtests) == 1


def test_backtest_for_another_pair_is_rejected(eur_usd, gbp_usd):
    with pytest.raises(ValueError):
        eur_usd.add_backtest(BacktestResult(gbp_usd, TEST_DATE))


def test_backtest_for_a_different_pair_object_with_the_same_name_is_rejected(eur_usd):
    other = CurrencyPair("EUR_USD", PRICES)
    with pytest.raises(ValueError):
        eur_usd.add_backtest(BacktestResult(other, TEST_DATE))


def test_same_backtest_cannot_be_added_twice(eur_usd):
    result = backtest(eur_usd, win)
    eur_usd.add_backtest(result)
    with pytest.raises(ValueError):
        eur_usd.add_backtest(result)


@pytest.mark.parametrize("result", ["result", None, 0.5])
def test_non_backtest_is_rejected(result, eur_usd):
    with pytest.raises(ValueError):
        eur_usd.add_backtest(result)


def test_remove_backtest_changes_the_latest(eur_usd):
    first, second = backtest(eur_usd, win), backtest(eur_usd, loss)
    eur_usd.add_backtest(first)
    eur_usd.add_backtest(second)

    eur_usd.remove_backtest(second)

    assert eur_usd.backtests == (first,)
    assert eur_usd.latest_backtest() is first


def test_backtest_dated_before_the_latest_is_rejected(eur_usd):
    eur_usd.add_backtest(BacktestResult(eur_usd, date(2026, 10, 15)))
    with pytest.raises(ValueError):
        eur_usd.add_backtest(BacktestResult(eur_usd, date(2026, 10, 14)))
    assert len(eur_usd.backtests) == 1


def test_backtests_on_the_same_or_a_later_date_are_accepted(eur_usd):
    same_day, later = BacktestResult(eur_usd, date(2026, 10, 15)), BacktestResult(eur_usd, date(2026, 10, 16))
    eur_usd.add_backtest(BacktestResult(eur_usd, date(2026, 10, 15)))
    eur_usd.add_backtest(same_day)
    eur_usd.add_backtest(later)
    assert eur_usd.latest_backtest() is later


def test_removing_the_latest_lets_an_earlier_date_be_added(eur_usd):
    early, late = BacktestResult(eur_usd, date(2026, 10, 1)), BacktestResult(eur_usd, date(2026, 10, 15))
    eur_usd.add_backtest(early)
    eur_usd.add_backtest(late)
    eur_usd.remove_backtest(late)
    eur_usd.add_backtest(BacktestResult(eur_usd, date(2026, 10, 8)))
    assert eur_usd.latest_backtest().test_date == date(2026, 10, 8)


def test_removing_a_backtest_it_does_not_hold_is_rejected(eur_usd):
    with pytest.raises(ValueError):
        eur_usd.remove_backtest(backtest(eur_usd, win))


# rank_pairs (Phase 06, FR4)

def pair_with_backtests(name, *backtest_setups):
    """Return a pair holding one backtest per tuple of setup makers, in order."""
    pair = CurrencyPair(name, PRICES)
    for setups in backtest_setups:
        pair.add_backtest(backtest(pair, *setups))
    return pair


def test_pairs_are_ranked_by_latest_win_rate():
    low = pair_with_backtests("EUR_USD", (win, loss, loss))      # 1/3
    high = pair_with_backtests("GBP_USD", (win, win, loss))      # 2/3
    best = pair_with_backtests("AUD_USD", (win,))                # 1/1
    assert rank_pairs([low, high, best]) == [best, high, low]


def test_only_the_most_recent_backtest_counts():
    improved = pair_with_backtests("EUR_USD", (loss,), (win,))   # latest 1/1
    declined = pair_with_backtests("GBP_USD", (win,), (loss,))   # latest 0/1
    assert rank_pairs([declined, improved]) == [improved, declined]


def test_pairs_with_no_backtest_or_zero_trades_are_ranked_last():
    no_backtest = pair_with_backtests("EUR_USD")
    zero_trades = pair_with_backtests("GBP_USD", (still_open,))
    zero_win_rate = pair_with_backtests("AUD_USD", (loss,))
    assert rank_pairs([no_backtest, zero_trades, zero_win_rate]) == [zero_win_rate, no_backtest, zero_trades]


def test_ties_keep_input_order():
    first = pair_with_backtests("EUR_USD", (win, loss))
    second = pair_with_backtests("GBP_USD", (loss, win))
    unranked_a = pair_with_backtests("AUD_USD")
    unranked_b = pair_with_backtests("NZD_USD")
    assert rank_pairs([unranked_b, first, unranked_a, second]) == [first, second, unranked_b, unranked_a]
    assert rank_pairs([second, first]) == [second, first]


def test_rank_pairs_returns_a_new_list_and_leaves_the_input_alone():
    low = pair_with_backtests("EUR_USD", (loss,))
    high = pair_with_backtests("GBP_USD", (win,))
    pairs = [low, high]
    ranked = rank_pairs(pairs)
    assert ranked == [high, low]
    assert pairs == [low, high]


def test_rank_pairs_of_nothing_is_empty():
    assert rank_pairs([]) == []


@pytest.mark.parametrize("pairs", [["EUR_USD"], [None]])
def test_rank_pairs_rejects_non_pairs(pairs):
    with pytest.raises(ValueError):
        rank_pairs(pairs)


def test_rank_pairs_rejects_duplicate_pairs():
    pair = pair_with_backtests("EUR_USD", (win,))
    with pytest.raises(ValueError):
        rank_pairs([pair, pair_with_backtests("GBP_USD"), pair])


def test_rank_pairs_accepts_different_pair_objects_with_the_same_name():
    first, second = pair_with_backtests("EUR_USD", (win,)), pair_with_backtests("EUR_USD", (loss,))
    assert rank_pairs([second, first]) == [first, second]
