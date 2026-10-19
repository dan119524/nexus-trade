"""SellDirection: the sell rules (Phase 06 implementation of TradeDirection)."""

from tools.models.trade_direction import TradeDirection


class SellDirection(TradeDirection):
    """Sell: take profit < entry < stop loss, and lower prices are in the trade's favor (FR2)."""

    @property
    def name(self):
        return "sell"

    def check_price_order(self, entry, stop_loss, take_profit):
        if not take_profit < entry < stop_loss:
            raise ValueError("a sell needs take profit < entry < stop loss")

    def reward(self, entry, take_profit):
        return entry - take_profit

    def risk(self, entry, stop_loss):
        return stop_loss - entry

    def outcome(self, price_data, stop_loss, take_profit):
        for high, low in price_data:
            if high >= stop_loss:
                return "loss"
            if low <= take_profit:
                return "win"
        return "open"

    def is_beyond(self, price, reference):
        return price < reference

    @property
    def units_sign(self):
        return -1
