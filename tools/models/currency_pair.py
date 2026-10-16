"""CurrencyPair: a forex market that NEXUS analyzes (Phase 01 entity)."""

import math
import re

_PAIR_NAME_PATTERN = re.compile(r"[A-Z]{3}_[A-Z]{3}")


def validate_pair_name(name):
    """Return name if it is in OANDA format, such as "EUR_USD". Otherwise raise ValueError."""
    if not isinstance(name, str) or not _PAIR_NAME_PATTERN.fullmatch(name):
        raise ValueError(f"pair name must look like 'EUR_USD', got {name!r}")
    base, quote = name.split("_")
    if base == quote:
        raise ValueError(f"pair name must use two different currencies, got {name!r}")
    return name


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
    """A currency pair with its name and its past (high, low) price data."""

    def __init__(self, name, price_data):
        self._name = validate_pair_name(name)
        self._price_data = _validate_price_data(price_data)

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
