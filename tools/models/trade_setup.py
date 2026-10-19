"""TradeSetup: a suggested trade on one currency pair (Phase 01 entity, Phase 05 abstract base class)."""

from abc import ABC, abstractmethod

from tools.models.currency_pair import to_price, validate_pair


class TradeSetup(ABC):
    """A setup with an entry price, a stop loss, and a take profit.

    TradeSetup is abstract. Only BuySetup and SellSetup can be built.
    """

    def __init__(self, pair, entry, stop_loss, take_profit):
        self._pair = validate_pair(pair)
        entry = to_price(entry, "entry")
        stop_loss = to_price(stop_loss, "stop loss")
        take_profit = to_price(take_profit, "take profit")
        if entry <= 0 or stop_loss <= 0 or take_profit <= 0:
            raise ValueError("entry, stop loss, and take profit must be greater than 0")
        self._entry = entry
        self._stop_loss = stop_loss
        self._take_profit = take_profit
        self._check_price_order()

    @abstractmethod
    def _check_price_order(self):
        """Raise ValueError if the prices are in the wrong order for this direction (FR2)."""

    @property
    def pair(self):
        return self._pair

    @property
    def pair_name(self):
        return self._pair.name

    @property
    @abstractmethod
    def direction(self):
        """Return "buy" or "sell"."""

    @property
    def entry(self):
        return self._entry

    @property
    def stop_loss(self):
        return self._stop_loss

    @property
    def take_profit(self):
        return self._take_profit

    @abstractmethod
    def reward(self):
        """Return the price distance from entry to take profit."""

    @abstractmethod
    def risk(self):
        """Return the price distance from entry to stop loss."""

    def reward_to_risk(self):
        """Return reward divided by risk. The minimum of 2 is not enforced here."""
        return self.reward() / self.risk()

    @abstractmethod
    def outcome(self):
        """Return "win", "loss", or "open" from this pair's price data, starting at the first point (FR3).

        A win reaches take profit before stop loss. A point that touches both is a loss.
        If neither is reached, the outcome is "open".
        """


def evaluate_setup(setup: TradeSetup) -> str:
    """Return the outcome of any TradeSetup, through the TradeSetup interface (FR3)."""
    return setup.outcome()
