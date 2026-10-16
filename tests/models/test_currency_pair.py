"""Phase 02 tests for CurrencyPair. Fixed price data only; no OANDA API calls."""

import pytest

from tools.models import CurrencyPair

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
