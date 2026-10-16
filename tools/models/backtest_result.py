"""BacktestResult: the outcome of backtesting one currency pair (Phase 01 entity)."""

from datetime import date

from tools.models.currency_pair import validate_pair_name


def _to_count(value, label):
    """Return value if it is a whole number of 0 or more. Otherwise raise ValueError."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be a whole number, got {value!r}")
    if value < 0:
        raise ValueError(f"{label} must not be negative, got {value!r}")
    return value


class BacktestResult:
    """A backtest outcome: pair name, test date, and setup, trade, and win counts."""

    def __init__(self, pair_name, test_date, setups_tested, trade_count, win_count):
        self._pair_name = validate_pair_name(pair_name)
        if not isinstance(test_date, date):
            raise ValueError(f"test date must be a datetime.date, got {test_date!r}")
        self._test_date = test_date
        self._setups_tested = _to_count(setups_tested, "setups tested")
        self._trade_count = _to_count(trade_count, "trade count")
        self._win_count = _to_count(win_count, "win count")
        if self._win_count > self._trade_count:
            raise ValueError("win count must not be greater than trade count")
        if self._trade_count > self._setups_tested:
            raise ValueError("trade count must not be greater than setups tested")

    @property
    def pair_name(self):
        return self._pair_name

    @property
    def test_date(self):
        return self._test_date

    @property
    def setups_tested(self):
        return self._setups_tested

    @property
    def trade_count(self):
        return self._trade_count

    @property
    def win_count(self):
        return self._win_count

    def win_rate(self):
        """Return wins divided by trades, or None when there were no trades."""
        if self._trade_count == 0:
            return None
        return self._win_count / self._trade_count
