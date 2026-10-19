"""Candle: one complete OHLC bar for a currency pair (Phase 05 entity)."""

from datetime import datetime

from tools.models.currency_pair import to_price, validate_pair
from tools.models.timeframe import Timeframe


def validate_timeframe(timeframe):
    """Return timeframe if it is a Timeframe. Otherwise raise ValueError."""
    if not isinstance(timeframe, Timeframe):
        raise ValueError(f"timeframe must be a Timeframe, got {timeframe!r}")
    return timeframe


def validate_time(time):
    """Return time if it is a datetime. Otherwise raise ValueError."""
    if not isinstance(time, datetime):
        raise ValueError(f"time must be a datetime, got {time!r}")
    return time


def to_positive_price(value, label):
    """Return value as a float if it is a finite number > 0. Otherwise raise ValueError."""
    price = to_price(value, label)
    if price <= 0:
        raise ValueError(f"{label} must be greater than 0, got {value!r}")
    return price


class Candle:
    """A complete candle: pair, timeframe, time, open, high, low, close, and volume (FR6)."""

    def __init__(self, pair, timeframe, time, open_, high, low, close, volume, complete):
        if complete is not True:
            raise ValueError("an incomplete candle is rejected")
        self._pair = validate_pair(pair)
        self._timeframe = validate_timeframe(timeframe)
        self._time = validate_time(time)
        self._open = to_positive_price(open_, "open")
        self._high = to_positive_price(high, "high")
        self._low = to_positive_price(low, "low")
        self._close = to_positive_price(close, "close")
        if self._high < self._low:
            raise ValueError("high must not be below low")
        if not self._low <= self._open <= self._high or not self._low <= self._close <= self._high:
            raise ValueError("open and close must lie between low and high")
        if isinstance(volume, bool) or not isinstance(volume, int) or volume < 0:
            raise ValueError(f"volume must be a whole number of 0 or more, got {volume!r}")
        self._volume = volume

    @property
    def pair(self):
        return self._pair

    @property
    def timeframe(self):
        return self._timeframe

    @property
    def time(self):
        return self._time

    @property
    def open(self):
        return self._open

    @property
    def high(self):
        return self._high

    @property
    def low(self):
        return self._low

    @property
    def close(self):
        return self._close

    @property
    def volume(self):
        return self._volume
