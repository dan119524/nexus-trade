"""TradeSetup: a suggested trade on one currency pair (Phase 01 entity, Phase 04 superclass)."""

from tools.models.currency_pair import to_price, validate_pair


class TradeSetup:
    """A setup with an entry price, a stop loss, and a take profit.

    Only BuySetup and SellSetup can be built. A bare TradeSetup raises
    NotImplementedError from its price-order check.
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

    def _check_price_order(self):
        """Raise ValueError if the prices are in the wrong order for this direction (FR2)."""
        raise NotImplementedError("TradeSetup cannot be created directly; use BuySetup or SellSetup")

    @property
    def pair(self):
        return self._pair

    @property
    def pair_name(self):
        return self._pair.name

    @property
    def direction(self):
        raise NotImplementedError("TradeSetup has no direction; use BuySetup or SellSetup")

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
        raise NotImplementedError("TradeSetup has no reward; use BuySetup or SellSetup")

    def risk(self):
        """Return the price distance from entry to stop loss."""
        raise NotImplementedError("TradeSetup has no risk; use BuySetup or SellSetup")

    def reward_to_risk(self):
        """Return reward divided by risk. The minimum of 2 is not enforced here."""
        return self.reward() / self.risk()
