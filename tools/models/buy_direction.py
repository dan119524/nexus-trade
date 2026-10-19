"""BuyDirection: the buy rules (Phase 06 implementation of TradeDirection)."""

from tools.models.trade_direction import TradeDirection


class BuyDirection(TradeDirection):
    """Buy: stop loss < entry < take profit, and higher prices are in the trade's favor (FR2)."""

    @property
    def name(self):
        return "buy"

    def check_price_order(self, entry, stop_loss, take_profit):
        if not stop_loss < entry < take_profit:
            raise ValueError("a buy needs stop loss < entry < take profit")

    def reward(self, entry, take_profit):
        return take_profit - entry

    def risk(self, entry, stop_loss):
        return entry - stop_loss

    def outcome(self, price_data, stop_loss, take_profit):
        for high, low in price_data:
            if low <= stop_loss:
                return "loss"
            if high >= take_profit:
                return "win"
        return "open"

    def is_beyond(self, price, reference):
        return price > reference

    @property
    def units_sign(self):
        return 1
