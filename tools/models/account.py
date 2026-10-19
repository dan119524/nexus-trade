"""Account: the OANDA practice account a trade plan is sized for (Phase 05 entity)."""

import re

from tools.models.candle import to_positive_price
from tools.models.currency_pair import to_price

_CURRENCY_PATTERN = re.compile(r"[A-Z]{3}")
MAX_RISK_PERCENT = 2.0


class Account:
    """A practice account with its ID, balance, currency, and risk percent (FR5, FR9).

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
