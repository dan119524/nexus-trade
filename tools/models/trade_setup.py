"""TradeSetup: a suggested trade on one currency pair (Phase 01 entity, Phase 06 delegates to TradeDirection)."""

from tools.models.currency_pair import to_price, validate_pair
from tools.models.trade_direction import TradeDirection


class TradeSetup:
    """A setup with a direction, an entry price, a stop loss, and a take profit.

    Everything that differs between a buy and a sell is delegated to its TradeDirection.
    """

    def __init__(self, pair, direction, entry, stop_loss, take_profit):
        self._pair = validate_pair(pair)
        if not isinstance(direction, TradeDirection):
            raise ValueError(f"direction must be a TradeDirection, got {direction!r}")
        self._direction = direction
        entry = to_price(entry, "entry")
        stop_loss = to_price(stop_loss, "stop loss")
        take_profit = to_price(take_profit, "take profit")
        if entry <= 0 or stop_loss <= 0 or take_profit <= 0:
            raise ValueError("entry, stop loss, and take profit must be greater than 0")
        direction.check_price_order(entry, stop_loss, take_profit)
        self._entry = entry
        self._stop_loss = stop_loss
        self._take_profit = take_profit

    @property
    def pair(self):
        return self._pair

    @property
    def pair_name(self):
        return self._pair.name

    @property
    def trade_direction(self):
        """Return the TradeDirection this setup delegates to."""
        return self._direction

    @property
    def direction(self):
        """Return "buy" or "sell"."""
        return self._direction.name

    @property
    def entry(self):
        return self._entry

    @property
    def stop_loss(self):
        return self._stop_loss

    @property
    def take_profit(self):
        return self._take_profit

    def reward(self):
        """Return the price distance from entry to take profit."""
        return self._direction.reward(self._entry, self._take_profit)

    def risk(self):
        """Return the price distance from entry to stop loss."""
        return self._direction.risk(self._entry, self._stop_loss)

    def reward_to_risk(self):
        """Return reward divided by risk. The minimum of 2 is not enforced here."""
        return self.reward() / self.risk()

    def outcome(self):
        """Return "win", "loss", or "open" from this pair's price data, starting at the first point (FR3)."""
        return self._direction.outcome(self._pair.price_data, self._stop_loss, self._take_profit)


def evaluate_setup(setup: TradeSetup) -> str:
    """Return the outcome of any TradeSetup, through the TradeSetup interface (FR3)."""
    return setup.outcome()
