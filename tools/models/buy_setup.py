"""BuySetup: a trade setup that buys (Phase 04 subclass of TradeSetup)."""

from tools.models.trade_setup import TradeSetup


class BuySetup(TradeSetup):
    """A buy setup: stop loss < entry < take profit (FR2)."""

    def __init__(self, pair, entry, stop_loss, take_profit):
        super().__init__(pair, entry, stop_loss, take_profit)

    def _check_price_order(self):
        if not self._stop_loss < self._entry < self._take_profit:
            raise ValueError("a buy needs stop loss < entry < take profit")

    @property
    def direction(self):
        return "buy"

    def reward(self):
        return self._take_profit - self._entry

    def risk(self):
        return self._entry - self._stop_loss
