"""Timeframe: the candle timeframes NEXUS analyzes (Phase 05 value)."""

from enum import Enum


class Timeframe(Enum):
    """One of the four timeframes in the pipeline (FR6)."""

    M1 = "M1"
    M5 = "M5"
    H1 = "H1"
    H4 = "H4"
