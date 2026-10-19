"""Tests for lot-to-units conversion in tools/oanda/execute_trade.py. Never calls OANDA."""

from tools.oanda.execute_trade import _units_from_lot


def test_buy_lot_size_rounds_to_units():
    # 0.29 * 100_000 is 28999.999999999996 in floating point; truncating gave 28999
    assert _units_from_lot(0.29, "bullish") == 29000


def test_sell_lot_size_rounds_to_negative_units():
    assert _units_from_lot(0.29, "bearish") == -29000
