"""Phase 02-04 tests for BacktestResult. Fixed counts only; no OANDA API calls."""

from datetime import date

import pytest

from tools.models import BacktestResult, BuySetup

TEST_DATE = date(2026, 10, 15)


def test_valid_construction_stores_values(eur_usd):
    result = BacktestResult(eur_usd, TEST_DATE, setups_tested=12, trade_count=10, win_count=6)

    assert result.pair_name == "EUR_USD"
    assert result.test_date == TEST_DATE
    assert result.setups_tested == 12
    assert result.trade_count == 10
    assert result.win_count == 6


def test_all_zero_counts_are_allowed(gbp_usd):
    result = BacktestResult(gbp_usd, TEST_DATE, setups_tested=0, trade_count=0, win_count=0)

    assert result.setups_tested == 0
    assert result.trade_count == 0
    assert result.win_count == 0


def test_equal_counts_are_allowed(eur_usd):
    result = BacktestResult(eur_usd, TEST_DATE, setups_tested=5, trade_count=5, win_count=5)

    assert result.win_rate() == 1.0


def test_pair_is_the_currency_pair_object_passed_in(eur_usd):
    result = BacktestResult(eur_usd, TEST_DATE, setups_tested=12, trade_count=10, win_count=6)

    assert result.pair is eur_usd
    assert result.pair_name == eur_usd.name


def test_result_and_setup_can_share_one_pair(eur_usd):
    setup = BuySetup(eur_usd, entry=1.0900, stop_loss=1.0850, take_profit=1.1000)
    result = BacktestResult(eur_usd, TEST_DATE, setups_tested=12, trade_count=10, win_count=6)

    assert result.pair is setup.pair


def test_pair_is_read_only(eur_usd, gbp_usd):
    result = BacktestResult(eur_usd, TEST_DATE, setups_tested=12, trade_count=10, win_count=6)

    with pytest.raises(AttributeError):
        result.pair = gbp_usd


@pytest.mark.parametrize("pair", ["EUR_USD", None, 1, ("EUR_USD", [(1.09, 1.08), (1.10, 1.09)])])
def test_pair_that_is_not_a_currency_pair_raises_value_error(pair):
    with pytest.raises(ValueError):
        BacktestResult(pair, TEST_DATE, setups_tested=1, trade_count=1, win_count=0)


@pytest.mark.parametrize("test_date", ["2026-10-15", None, 20261015])
def test_test_date_that_is_not_a_date_raises_value_error(test_date, eur_usd):
    with pytest.raises(ValueError):
        BacktestResult(eur_usd, test_date, setups_tested=1, trade_count=1, win_count=0)


@pytest.mark.parametrize("counts", [
    {"setups_tested": -1, "trade_count": 0, "win_count": 0},
    {"setups_tested": 5, "trade_count": -1, "win_count": 0},
    {"setups_tested": 5, "trade_count": 3, "win_count": -1},
])
def test_negative_count_raises_value_error(counts, eur_usd):
    with pytest.raises(ValueError):
        BacktestResult(eur_usd, TEST_DATE, **counts)


@pytest.mark.parametrize("counts", [
    {"setups_tested": 5.0, "trade_count": 3, "win_count": 1},
    {"setups_tested": 5, "trade_count": "3", "win_count": 1},
    {"setups_tested": 5, "trade_count": 3, "win_count": True},
    {"setups_tested": 5, "trade_count": 3, "win_count": None},
])
def test_count_that_is_not_a_whole_number_raises_value_error(counts, eur_usd):
    with pytest.raises(ValueError):
        BacktestResult(eur_usd, TEST_DATE, **counts)


def test_wins_greater_than_trades_raises_value_error(eur_usd):
    with pytest.raises(ValueError):
        BacktestResult(eur_usd, TEST_DATE, setups_tested=10, trade_count=3, win_count=4)


def test_trades_greater_than_setups_tested_raises_value_error(eur_usd):
    with pytest.raises(ValueError):
        BacktestResult(eur_usd, TEST_DATE, setups_tested=0, trade_count=10, win_count=6)


def test_win_rate_is_wins_divided_by_trades(eur_usd):
    result = BacktestResult(eur_usd, TEST_DATE, setups_tested=12, trade_count=10, win_count=6)

    assert result.win_rate() == pytest.approx(0.6)


def test_win_rate_is_zero_when_no_trade_wins(eur_usd):
    result = BacktestResult(eur_usd, TEST_DATE, setups_tested=4, trade_count=4, win_count=0)

    assert result.win_rate() == 0.0


def test_win_rate_is_none_for_zero_trades(gbp_usd):
    result = BacktestResult(gbp_usd, TEST_DATE, setups_tested=3, trade_count=0, win_count=0)

    assert result.win_rate() is None
