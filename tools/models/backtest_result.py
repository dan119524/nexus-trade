"""BacktestResult: the outcome of backtesting one currency pair (Phase 01 entity, Phase 06 holds its setups)."""

from datetime import date

from tools.models.currency_pair import validate_pair
from tools.models.trade_setup import TradeSetup


class BacktestResult:
    """A backtest on one currency pair: its test date and the trade setups it tested (FR3).

    Setups tested, trades, and wins come from each setup's outcome(). Open setups are not trades.
    """

    def __init__(self, pair, test_date):
        self._pair = validate_pair(pair)
        if not isinstance(test_date, date):
            raise ValueError(f"test date must be a datetime.date, got {test_date!r}")
        self._test_date = test_date
        self._setups: list[TradeSetup] = []

    @property
    def pair(self):
        return self._pair

    @property
    def pair_name(self):
        return self._pair.name

    @property
    def test_date(self):
        return self._test_date

    def _holds(self, setup):
        return any(held is setup for held in self._setups)

    def add_setup(self, setup):
        """Add a TradeSetup on this backtest's currency pair (the same object) that it does not already hold."""
        if not isinstance(setup, TradeSetup):
            raise ValueError(f"setup must be a TradeSetup, got {setup!r}")
        if setup.pair is not self._pair:
            raise ValueError("setup must be on the same currency pair as the backtest")
        if self._holds(setup):
            raise ValueError("setup is already in this backtest")
        self._setups.append(setup)

    def remove_setup(self, setup):
        """Remove a setup this backtest holds. Raise ValueError if it does not hold it."""
        if not self._holds(setup):
            raise ValueError("setup is not in this backtest")
        self._setups = [held for held in self._setups if held is not setup]

    @property
    def setups(self):
        """Return the tested setups as a tuple, in the order they were added."""
        return tuple(self._setups)

    @property
    def setups_tested(self):
        return len(self._setups)

    @property
    def trade_count(self):
        """Return the number of setups whose outcome is a win or a loss."""
        return sum(1 for setup in self._setups if setup.outcome() != "open")

    @property
    def win_count(self):
        return sum(1 for setup in self._setups if setup.outcome() == "win")

    def win_rate(self):
        """Return wins divided by trades, or None when there were no trades."""
        if self.trade_count == 0:
            return None
        return self.win_count / self.trade_count
