"""Tests for StructureEvent, BreakOfStructure, and ChangeOfCharacter (Phase 05, FR7)."""

import pytest

from tests.models.conftest import T0
from tools.models import BreakOfStructure, ChangeOfCharacter, StructureEvent, SwingPoint, Timeframe

SWING_PRICE = 1.0900
ABOVE = 1.0910
BELOW = 1.0890


def swing(pair, label):
    return SwingPoint(pair, Timeframe.H1, T0, SWING_PRICE, label)


def test_bare_structure_event_cannot_be_created(eur_usd):
    with pytest.raises(TypeError):
        StructureEvent(swing(eur_usd, "HH"), T0, ABOVE)


@pytest.mark.parametrize("event_class, label, close, direction", [
    (BreakOfStructure, "HH", ABOVE, "bullish"),
    (BreakOfStructure, "LL", BELOW, "bearish"),
    (ChangeOfCharacter, "LH", ABOVE, "bullish"),
    (ChangeOfCharacter, "HL", BELOW, "bearish"),
])
def test_direction_comes_from_the_broken_label(event_class, label, close, direction, eur_usd):
    broken = swing(eur_usd, label)
    event = event_class(broken, T0, close)
    assert isinstance(event, StructureEvent)
    assert event.direction == direction
    assert event.swing is broken
    assert event.close == close
    assert event.time == T0


@pytest.mark.parametrize("event_class, label", [
    (BreakOfStructure, "LH"), (BreakOfStructure, "HL"),
    (ChangeOfCharacter, "HH"), (ChangeOfCharacter, "LL"),
])
def test_event_rejects_labels_it_may_not_break(event_class, label, eur_usd):
    with pytest.raises(ValueError):
        event_class(swing(eur_usd, label), T0, ABOVE if label in ("HH", "LH") else BELOW)


@pytest.mark.parametrize("event_class, label, close", [
    (BreakOfStructure, "HH", SWING_PRICE), (BreakOfStructure, "HH", BELOW),
    (BreakOfStructure, "LL", SWING_PRICE), (BreakOfStructure, "LL", ABOVE),
    (ChangeOfCharacter, "LH", SWING_PRICE), (ChangeOfCharacter, "LH", BELOW),
    (ChangeOfCharacter, "HL", SWING_PRICE), (ChangeOfCharacter, "HL", ABOVE),
])
def test_close_must_be_beyond_the_swing_in_its_direction(event_class, label, close, eur_usd):
    with pytest.raises(ValueError):
        event_class(swing(eur_usd, label), T0, close)


def test_swing_must_be_a_swing_point():
    with pytest.raises(ValueError):
        BreakOfStructure(1.09, T0, ABOVE)


def test_time_and_close_are_checked(eur_usd):
    with pytest.raises(ValueError):
        BreakOfStructure(swing(eur_usd, "HH"), "now", ABOVE)
    with pytest.raises(ValueError):
        BreakOfStructure(swing(eur_usd, "HH"), T0, -1)
