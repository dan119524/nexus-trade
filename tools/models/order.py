"""Order: a confirmed market order for a practice account (Phase 05 entity)."""

from tools.models.account import Account
from tools.models.trade_plan import TradePlan

UNITS_PER_LOT = 100_000


class Order:
    """A market order created from a trade plan after the trader's explicit confirmation (FR10).

    Holds data only. It never sends anything to OANDA.
    """

    def __init__(self, plan, account, confirmed):
        if not isinstance(plan, TradePlan):
            raise ValueError(f"plan must be a TradePlan, got {plan!r}")
        if not isinstance(account, Account):
            raise ValueError(f"account must be an Account, got {account!r}")
        if account is not plan.account:
            raise ValueError("an order's account must be its trade plan's account")
        if account.environment != "practice":
            raise ValueError("an order is only allowed for a practice account")
        if confirmed is not True:
            raise ValueError("an order needs the trader's explicit confirmation")
        self._plan = plan
        self._account = account

    @property
    def plan(self):
        return self._plan

    @property
    def account(self):
        return self._account

    @property
    def order_type(self):
        return "MARKET"

    def units(self):
        """Return lot size × 100,000, positive for a buy and negative for a sell."""
        units = round(self._plan.lot_size * UNITS_PER_LOT)
        return units if self._plan.setup.direction == "buy" else -units
