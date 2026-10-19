"""BreakOfStructure: a break with the trend (Phase 05 subclass of StructureEvent)."""

from tools.models.structure_event import StructureEvent


class BreakOfStructure(StructureEvent):
    """A BOS: a close above an HH (bullish) or below an LL (bearish) (FR7)."""

    def __init__(self, swing, time, close):
        super().__init__(swing, time, close)

    def _direction_for(self, label):
        if label == "HH":
            return "bullish"
        if label == "LL":
            return "bearish"
        raise ValueError(f"a break of structure must break an HH or an LL, got {label!r}")
