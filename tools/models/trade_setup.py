"""TradeSetup: a suggested trade on one currency pair (Phase 01 entity)."""

from tools.models.currency_pair import to_price, validate_pair_name

_DIRECTIONS = ("buy", "sell")


class TradeSetup:
    """A buy or sell setup with an entry price, a stop loss, and a take profit."""

    def __init__(self, pair_name, direction, entry, stop_loss, take_profit):
        self._pair_name = validate_pair_name(pair_name)
        if direction not in _DIRECTIONS:
            raise ValueError(f"direction must be 'buy' or 'sell', got {direction!r}")
        entry = to_price(entry, "entry")
        stop_loss = to_price(stop_loss, "stop loss")
        take_profit = to_price(take_profit, "take profit")
        if entry <= 0 or stop_loss <= 0 or take_profit <= 0:
            raise ValueError("entry, stop loss, and take profit must be greater than 0")
        if direction == "buy" and not stop_loss < entry < take_profit:
            raise ValueError("a buy needs stop loss < entry < take profit")
        if direction == "sell" and not take_profit < entry < stop_loss:
            raise ValueError("a sell needs take profit < entry < stop loss")
        self._direction = direction
        self._entry = entry
        self._stop_loss = stop_loss
        self._take_profit = take_profit

    @property
    def pair_name(self):
        return self._pair_name

    @property
    def direction(self):
        return self._direction

    @property
    def entry(self):
        return self._entry

    @property
    def stop_loss(self):
        return self._stop_loss

    @property
    def take_profit(self):
        return self._take_profit

    def reward_to_risk(self):
        """Return reward divided by risk. The minimum of 2 is not enforced here."""
        reward = abs(self._take_profit - self._entry)
        risk = abs(self._entry - self._stop_loss)
        return reward / risk
