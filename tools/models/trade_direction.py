"""TradeDirection: the rules that differ between buying and selling (Phase 06 interface)."""

from abc import ABC, abstractmethod


class TradeDirection(ABC):
    """Direction rules a TradeSetup delegates to (FR2, FR3).

    TradeDirection is abstract. Only BuyDirection and SellDirection can be built.
    """

    @property
    @abstractmethod
    def name(self):
        """Return "buy" or "sell"."""

    @abstractmethod
    def check_price_order(self, entry, stop_loss, take_profit):
        """Raise ValueError if the prices are in the wrong order for this direction (FR2)."""

    @abstractmethod
    def reward(self, entry, take_profit):
        """Return the price distance from entry to take profit."""

    @abstractmethod
    def risk(self, entry, stop_loss):
        """Return the price distance from entry to stop loss."""

    @abstractmethod
    def outcome(self, price_data, stop_loss, take_profit):
        """Return "win", "loss", or "open" from (high, low) price data, starting at the first point (FR3).

        A win reaches take profit before stop loss. A point that touches both is a loss.
        If neither is reached, the outcome is "open".
        """

    @abstractmethod
    def is_beyond(self, price, reference):
        """Return True if price is further than reference in the trade's favor."""

    @property
    @abstractmethod
    def units_sign(self):
        """Return 1 for a buy and -1 for a sell."""
