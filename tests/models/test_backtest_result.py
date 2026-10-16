"""Phase 02 tests for BacktestResult. Fixed counts only; no OANDA API calls."""

from datetime import date

import pytest

from tools.models import BacktestResult

TEST_DATE = date(2026, 10, 15)


def test_valid_construction_stores_values():
    result = BacktestResult("EUR_USD", TEST_DATE, setups_tested=12, trade_count=10, win_count=6)

    assert result.pair_name == "EUR_USD"
    assert result.test_date == TEST_DATE
    assert result.setups_tested == 12
    assert result.trade_count == 10
    assert result.win_count == 6


def test_all_zero_counts_are_allowed():
    result = BacktestResult("GBP_USD", TEST_DATE, setups_tested=0, trade_count=0, win_count=0)

    assert result.setups_tested == 0
    assert result.trade_count == 0
    assert result.win_count == 0


def test_equal_counts_are_allowed():
    result = BacktestResult("EUR_USD", TEST_DATE, setups_tested=5, trade_count=5, win_count=5)

    assert result.win_rate() == 1.0


@pytest.mark.parametrize("pair_name", ["EUR/USD", "eurusd", "EUR_EUR", None])
def test_invalid_pair_name_raises_value_error(pair_name):
    with pytest.raises(ValueError):
        BacktestResult(pair_name, TEST_DATE, setups_tested=1, trade_count=1, win_count=0)


@pytest.mark.parametrize("test_date", ["2026-10-15", None, 20261015])
def test_test_date_that_is_not_a_date_raises_value_error(test_date):
    with pytest.raises(ValueError):
        BacktestResult("EUR_USD", test_date, setups_tested=1, trade_count=1, win_count=0)


@pytest.mark.parametrize("counts", [
    {"setups_tested": -1, "trade_count": 0, "win_count": 0},
    {"setups_tested": 5, "trade_count": -1, "win_count": 0},
    {"setups_tested": 5, "trade_count": 3, "win_count": -1},
])
def test_negative_count_raises_value_error(counts):
    with pytest.raises(ValueError):
        BacktestResult("EUR_USD", TEST_DATE, **counts)


@pytest.mark.parametrize("counts", [
    {"setups_tested": 5.0, "trade_count": 3, "win_count": 1},
    {"setups_tested": 5, "trade_count": "3", "win_count": 1},
    {"setups_tested": 5, "trade_count": 3, "win_count": True},
    {"setups_tested": 5, "trade_count": 3, "win_count": None},
])
def test_count_that_is_not_a_whole_number_raises_value_error(counts):
    with pytest.raises(ValueError):
        BacktestResult("EUR_USD", TEST_DATE, **counts)


def test_wins_greater_than_trades_raises_value_error():
    with pytest.raises(ValueError):
        BacktestResult("EUR_USD", TEST_DATE, setups_tested=10, trade_count=3, win_count=4)


def test_trades_greater_than_setups_tested_raises_value_error():
    with pytest.raises(ValueError):
        BacktestResult("EUR_USD", TEST_DATE, setups_tested=0, trade_count=10, win_count=6)


def test_win_rate_is_wins_divided_by_trades():
    result = BacktestResult("EUR_USD", TEST_DATE, setups_tested=12, trade_count=10, win_count=6)

    assert result.win_rate() == pytest.approx(0.6)


def test_win_rate_is_zero_when_no_trade_wins():
    result = BacktestResult("EUR_USD", TEST_DATE, setups_tested=4, trade_count=4, win_count=0)

    assert result.win_rate() == 0.0


def test_win_rate_is_none_for_zero_trades():
    result = BacktestResult("GBP_USD", TEST_DATE, setups_tested=3, trade_count=0, win_count=0)

    assert result.win_rate() is None
