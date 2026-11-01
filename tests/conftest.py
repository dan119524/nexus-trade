"""Shared pytest fixtures."""

import json

import pytest


@pytest.fixture
def fake_tmp(monkeypatch, tmp_path):
    """Point .tmp/ at tmp_path with a small EUR_USD signal, analysis, and candle file."""
    monkeypatch.setattr("tools.utils.file_io._TMP", tmp_path)
    for sub in ("signals", "analysis", "candles"):
        (tmp_path / sub).mkdir()

    signal = {
        "id": "test-signal",
        "pair": "EUR_USD",
        "status": "active",
        "confluence": {"score": 3, "max_score": 4, "direction": "bearish", "signal_valid": True},
        "trade_plan": {
            "pair": "EUR_USD",
            "direction": "bearish",
            "reference_timeframe": "H4",
            "entry_price": 1.10000,
            "stop_loss": 1.10200,
            "take_profit_1": 1.09600,
            "take_profit_2": 1.09400,
            "sl_pips": 20.0,
            "risk_reward": 2.0,
            "lot_size": 0.1,
        },
        "created_at": "2024-01-01T00:00:00Z",
    }
    analysis = {
        "pair": "EUR_USD",
        "generated_at": "2024-01-01T00:00:00Z",
        "timeframes": {
            "H1": {"trend": "bearish", "swing_highs": [], "swing_lows": [], "bos_events": []},
        },
    }
    (tmp_path / "signals" / "EUR_USD_signals.json").write_text(json.dumps(signal))
    (tmp_path / "analysis" / "EUR_USD_analysis.json").write_text(json.dumps(analysis))
    (tmp_path / "candles" / "EUR_USD_H1.json").write_text("[]")
    return tmp_path
