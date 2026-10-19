"""Account: the OANDA practice account a trade plan is sized for (Phase 05 entity)."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tools.models.candle import to_positive_price
from tools.models.currency_pair import to_price

if TYPE_CHECKING:
    from tools.models.trade import Trade

_CURRENCY_PATTERN = re.compile(r"[A-Z]{3}")
MAX_RISK_PERCENT = 2.0


class Account:
    """A practice account with its ID, balance, currency, risk percent, and recorded trades (FR5, FR9, FR11).

    Holds data only. It never calls the OANDA API.
    """

    def __init__(self, account_id, balance, currency, environment, risk_percent):
        if not isinstance(account_id, str) or not account_id.strip():
            raise ValueError(f"account ID must be a non-empty string, got {account_id!r}")
        self._account_id = account_id
        self._balance = to_positive_price(balance, "balance")
        if not isinstance(currency, str) or not _CURRENCY_PATTERN.fullmatch(currency):
            raise ValueError(f"currency must look like 'USD', got {currency!r}")
        self._currency = currency
        if environment != "practice":
            raise ValueError(f"only a practice account is allowed, got {environment!r}")
        self._environment = environment
        risk_percent = to_price(risk_percent, "risk percent")
        if not 0 < risk_percent <= MAX_RISK_PERCENT:
            raise ValueError(f"risk percent must be greater than 0 and at most 2, got {risk_percent!r}")
        self._risk_percent = risk_percent
        self._trades: list[Trade] = []

    @property
    def account_id(self):
        return self._account_id

    @property
    def balance(self):
        return self._balance

    @property
    def currency(self):
        return self._currency

    @property
    def environment(self):
        return self._environment

    @property
    def risk_percent(self):
        return self._risk_percent

    def max_risk_amount(self):
        """Return the most this account may risk on one trade: balance × risk percent / 100."""
        return self._balance * self._risk_percent / 100

    def _holds(self, trade):
        return any(held is trade for held in self._trades)

    def _check_new_trade(self, trade, replacing=None):
        from tools.models.trade import Trade
        if not isinstance(trade, Trade):
            raise ValueError(f"trade must be a Trade, got {trade!r}")
        if trade.order.account is not self:
            raise ValueError("trade's order must be for this account")
        if self._holds(trade):
            raise ValueError("trade is already recorded by this account")
        if any(held.order is trade.order and held is not replacing for held in self._trades):
            raise ValueError("this account already records a trade for that order")

    def add_trade(self, trade):
        """Record a Trade whose order is for this account (the same object) and has no recorded trade yet (FR11)."""
        self._check_new_trade(trade)
        self._trades.append(trade)

    def remove_trade(self, trade):
        """Remove a trade this account holds. Raise ValueError if it does not hold it."""
        if not self._holds(trade):
            raise ValueError("trade is not recorded by this account")
        self._trades = [held for held in self._trades if held is not trade]

    def close_trade(self, open_trade, closed_trade):
        """Replace an open trade it holds with the closed Trade for the same order, in the same position (FR11)."""
        if not self._holds(open_trade):
            raise ValueError("open trade is not recorded by this account")
        if open_trade.outcome != "open":
            raise ValueError("only an open trade can be closed")
        self._check_new_trade(closed_trade, replacing=open_trade)
        if closed_trade.outcome == "open":
            raise ValueError("the closing trade must be a win or a loss")
        if closed_trade.order is not open_trade.order:
            raise ValueError("the closing trade must be for the same order")
        self._trades = [closed_trade if held is open_trade else held for held in self._trades]

    @property
    def trades(self):
        """Return the recorded trades as a tuple, in the order they were added."""
        return tuple(self._trades)

    def open_trades(self):
        """Return the recorded trades whose outcome is open, as a tuple."""
        return tuple(trade for trade in self._trades if trade.outcome == "open")

    def closed_trades(self):
        """Return the recorded trades whose outcome is a win or a loss, as a tuple."""
        return tuple(trade for trade in self._trades if trade.outcome != "open")
