"""ChangeOfCharacter: a break against the trend (Phase 05 subclass of StructureEvent)."""

from tools.models.structure_event import StructureEvent


class ChangeOfCharacter(StructureEvent):
    """A CHoCH: a close above an LH (bullish) or below an HL (bearish) (FR7)."""

    def __init__(self, swing, time, close):
        super().__init__(swing, time, close)

    def _direction_for(self, label):
        if label == "LH":
            return "bullish"
        if label == "HL":
            return "bearish"
        raise ValueError(f"a change of character must break an LH or an HL, got {label!r}")
