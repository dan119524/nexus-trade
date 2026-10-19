"""Trade: a position opened by an order (Phase 05 entity)."""

from tools.models.candle import to_positive_price
from tools.models.order import Order

_OUTCOMES = ("win", "loss", "open")


class Trade:
    """A trade with its outcome (win, loss, or open), exit price once closed, and R multiple (FR11)."""

    def __init__(self, order, outcome, exit_price=None):
        if not isinstance(order, Order):
            raise ValueError(f"order must be an Order, got {order!r}")
        if outcome not in _OUTCOMES:
            raise ValueError(f"outcome must be win, loss, or open, got {outcome!r}")
        if outcome == "open" and exit_price is not None:
            raise ValueError("an open trade has no exit price")
        if outcome != "open":
            exit_price = to_positive_price(exit_price, "exit price")
        self._order = order
        self._outcome = outcome
        self._exit_price = exit_price
        if outcome == "win" and self.r_multiple() <= 0:
            raise ValueError("a win needs an R multiple above 0")
        if outcome == "loss" and self.r_multiple() >= 0:
            raise ValueError("a loss needs an R multiple below 0")

    @property
    def order(self):
        return self._order

    @property
    def outcome(self):
        return self._outcome

    @property
    def exit_price(self):
        return self._exit_price

    def r_multiple(self):
        """Return the move from entry to exit in the trade direction divided by the setup's risk, or None while open."""
        if self._outcome == "open":
            return None
        setup = self._order.plan.setup
        move = self._exit_price - setup.entry
        if setup.direction == "sell":
            move = -move
        return move / setup.risk()
