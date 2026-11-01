"""CurrencyPair: a forex market that NEXUS analyzes (Phase 01 entity)."""

from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.models.backtest_result import BacktestResult

_PAIR_NAME_PATTERN = re.compile(r"[A-Z]{3}_[A-Z]{3}")

# Pip value rules from tools/trade_plan/calculate_lot_size.py (FR9)
_USD_QUOTE_PAIRS = ("EUR_USD", "GBP_USD", "AUD_USD", "NZD_USD")
_USD_BASE_PAIRS = ("USD_JPY", "USD_CHF", "USD_CAD", "USD_SGD")


def validate_pair_name(name):
    """Return name if it is in OANDA format, such as "EUR_USD". Otherwise raise ValueError."""
    if not isinstance(name, str) or not _PAIR_NAME_PATTERN.fullmatch(name):
        raise ValueError(f"pair name must look like 'EUR_USD', got {name!r}")
    base, quote = name.split("_")
    if base == quote:
        raise ValueError(f"pair name must use two different currencies, got {name!r}")
    return name


def pip_size_for(name):
    """Return the pip size for a pair name: 0.01 for a pair containing JPY, and 0.0001 otherwise."""
    return 0.01 if "JPY" in name else 0.0001


def validate_pair(pair):
    """Return pair if it is a CurrencyPair. Otherwise raise ValueError."""
    if not isinstance(pair, CurrencyPair):
        raise ValueError(f"pair must be a CurrencyPair, got {pair!r}")
    return pair


def to_price(value, label):
    """Return value as a float if it is a finite number. Otherwise raise ValueError."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a number, got {value!r}")
    if not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number, got {value!r}")
    return float(value)


def _validate_price_data(price_data):
    """Return price data as a tuple of (high, low) floats, or raise ValueError."""
    try:
        price_data = tuple(price_data)
    except TypeError:
        raise ValueError(f"price data must be a sequence of (high, low) tuples, got {price_data!r}")
    if len(price_data) < 2:
        raise ValueError("price data must have at least 2 price points")
    points = []
    for point in price_data:
        if not isinstance(point, tuple) or len(point) != 2:
            raise ValueError(f"each price point must be a (high, low) tuple, got {point!r}")
        high = to_price(point[0], "high")
        low = to_price(point[1], "low")
        if high <= 0 or low <= 0:
            raise ValueError(f"prices must be greater than 0, got {point!r}")
        if high < low:
            raise ValueError(f"high must not be below low, got {point!r}")
        points.append((high, low))
    return tuple(points)


class CurrencyPair:
    """A currency pair with its name, its past (high, low) price data, and its backtest results."""

    def __init__(self, name, price_data):
        self._name = validate_pair_name(name)
        self._price_data = _validate_price_data(price_data)
        self._backtests: list[BacktestResult] = []

    @property
    def name(self):
        return self._name

    @property
    def price_data(self):
        return self._price_data

    def market_structure(self):
        """Return "uptrend", "downtrend", or "ranging" from this pair's price data (FR1)."""
        steps = list(zip(self._price_data, self._price_data[1:]))
        if all(high > prev_high and low > prev_low
               for (prev_high, prev_low), (high, low) in steps):
            return "uptrend"
        if all(high < prev_high and low < prev_low
               for (prev_high, prev_low), (high, low) in steps):
            return "downtrend"
        return "ranging"

    def pip_size(self):
        """Return 0.01 for a pair containing JPY, and 0.0001 otherwise."""
        return pip_size_for(self._name)

    def pip_value_per_lot(self, price):
        """Return the USD value of 1 pip per standard lot at price. Raise ValueError for a cross pair (FR9)."""
        price = to_price(price, "price")
        if price <= 0:
            raise ValueError(f"price must be greater than 0, got {price!r}")
        if self._name in _USD_QUOTE_PAIRS:
            return 10.0
        if self._name == "USD_JPY":
            return round(1_000 / price, 4)
        if self._name in _USD_BASE_PAIRS:
            return round(10.0 / price, 4)
        raise ValueError(f"{self._name} is a cross pair; no pip value until a real conversion exists")

    def _holds(self, result):
        return any(held is result for held in self._backtests)

    def add_backtest(self, result):
        """Add a BacktestResult for this pair (the same object), not already held, not dated before the latest."""
        from tools.models.backtest_result import BacktestResult
        if not isinstance(result, BacktestResult):
            raise ValueError(f"result must be a BacktestResult, got {result!r}")
        if result.pair is not self:
            raise ValueError("backtest result must be for this currency pair")
        if self._holds(result):
            raise ValueError("backtest result is already held by this pair")
        latest = self.latest_backtest()
        if latest is not None and result.test_date < latest.test_date:
            raise ValueError("backtest result must not be dated earlier than the most recent one")
        self._backtests.append(result)

    def remove_backtest(self, result):
        """Remove a backtest result this pair holds. Raise ValueError if it does not hold it."""
        if not self._holds(result):
            raise ValueError("backtest result is not held by this pair")
        self._backtests = [held for held in self._backtests if held is not result]

    @property
    def backtests(self):
        """Return the backtest results as a tuple, in the order they were added."""
        return tuple(self._backtests)

    def latest_backtest(self):
        """Return the most recent backtest result (the one added last), or None."""
        return self._backtests[-1] if self._backtests else None


def _ranked_win_rate(pair):
    """Return the win rate of pair's most recent backtest, or None if it ranks last (FR4)."""
    latest = pair.latest_backtest()
    return None if latest is None else latest.win_rate()


def rank_pairs(pairs: list[CurrencyPair]) -> list[CurrencyPair]:
    """Return pairs from best to worst win rate of their most recent backtest (FR4).

    Pairs with no backtest result or zero trades are ranked last. Ties keep input order.
    A pair passed more than once raises ValueError.
    """
    pairs = list(pairs)
    for index, pair in enumerate(pairs):
        validate_pair(pair)
        if any(earlier is pair for earlier in pairs[:index]):
            raise ValueError(f"{pair.name} appears more than once")
    ranked = [pair for pair in pairs if _ranked_win_rate(pair) is not None]
    last = [pair for pair in pairs if _ranked_win_rate(pair) is None]
    return sorted(ranked, key=_ranked_win_rate, reverse=True) + last
