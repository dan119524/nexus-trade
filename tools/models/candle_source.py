"""CandleSource: the interface NEXUS expects for getting candles (Phase 09 interface)."""

from abc import ABC, abstractmethod


class CandleSource(ABC):
    """Anything that can give NEXUS its candles as Candle objects."""

    @abstractmethod
    def candles(self):
        """Return the complete candles as a list of Candle objects, oldest first."""
