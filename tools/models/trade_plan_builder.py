"""TradePlanBuilder: assembles a TradePlan one part at a time (Phase 08 Builder)."""

from tools.models.trade_plan import TradePlan

_PARTS = ("signal", "account", "entry", "stop_loss", "take_profit_1", "take_profit_2", "lot_size")


class TradePlanBuilder:
    """Collects the seven parts of a TradePlan, then builds it.

    The caller passes in every value. The builder never reads files or calls OANDA,
    and it adds no rules: build() checks only that every part was given, and
    TradePlan's own constructor does all the validation.
    """

    def __init__(self):
        self._parts = {}

    def signal(self, signal):
        self._parts["signal"] = signal
        return self

    def account(self, account):
        self._parts["account"] = account
        return self

    def entry(self, entry):
        self._parts["entry"] = entry
        return self

    def stop_loss(self, stop_loss):
        self._parts["stop_loss"] = stop_loss
        return self

    def take_profit_1(self, take_profit_1):
        self._parts["take_profit_1"] = take_profit_1
        return self

    def take_profit_2(self, take_profit_2):
        self._parts["take_profit_2"] = take_profit_2
        return self

    def lot_size(self, lot_size):
        self._parts["lot_size"] = lot_size
        return self

    def build(self):
        """Return a new TradePlan, or raise ValueError if a part is missing or TradePlan rejects a value."""
        missing = [part for part in _PARTS if part not in self._parts]
        if missing:
            raise ValueError(f"a trade plan is missing: {', '.join(missing)}")
        return TradePlan(**self._parts)
