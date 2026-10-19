"""SellSetup: a trade setup that sells (Phase 04 subclass of TradeSetup)."""

from tools.models.trade_setup import TradeSetup


class SellSetup(TradeSetup):
    """A sell setup: take profit < entry < stop loss (FR2)."""

    def __init__(self, pair, entry, stop_loss, take_profit):
        super().__init__(pair, entry, stop_loss, take_profit)

    def _check_price_order(self):
        if not self._take_profit < self._entry < self._stop_loss:
            raise ValueError("a sell needs take profit < entry < stop loss")

    @property
    def direction(self):
        return "sell"

    def reward(self):
        return self._entry - self._take_profit

    def risk(self):
        return self._stop_loss - self._entry

    def outcome(self):
        for high, low in self.pair.price_data:
            if high >= self._stop_loss:
                return "loss"
            if low <= self._take_profit:
                return "win"
        return "open"
