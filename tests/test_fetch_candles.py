"""
Tests for tools/oanda/fetch_candles.py

These tests use mocking so no real OANDA API key is required.
Run: pytest tests/test_fetch_candles.py -v
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_raw_candle(time: str, o: float, h: float, l: float, c: float,
                    complete: bool = True) -> dict:
    return {
        "time": time,
        "mid": {"o": str(o), "h": str(h), "l": str(l), "c": str(c)},
        "volume": 1000,
        "complete": complete,
    }


MOCK_CANDLES = [
    make_raw_candle("2025-01-15T10:00:00Z", 1.0800, 1.0850, 1.0780, 1.0830),
    make_raw_candle("2025-01-15T11:00:00Z", 1.0830, 1.0900, 1.0820, 1.0875),
    make_raw_candle("2025-01-15T12:00:00Z", 1.0875, 1.0920, 1.0860, 1.0910),
    make_raw_candle("2025-01-15T13:00:00Z", 1.0910, 1.0950, 1.0890, 1.0940),
    make_raw_candle("2025-01-15T14:00:00Z", 1.0940, 1.0980, 1.0930, 1.0960, complete=False),  # in-progress
]

MOCK_RESPONSE = {"candles": MOCK_CANDLES}


def make_mock_client(response: dict) -> MagicMock:
    mock_req = MagicMock()
    mock_req.response = response
    mock_client = MagicMock()
    mock_client.request = MagicMock(return_value=mock_req)
    return mock_client, mock_req


# ── Tests: _normalize_candle ───────────────────────────────────────────────────

def test_normalize_candle_fields():
    from tools.oanda.fetch_candles import _normalize_candle
    raw = make_raw_candle("2025-01-15T10:00:00Z", 1.08, 1.09, 1.07, 1.085)
    result = _normalize_candle(raw, "EUR_USD", "H1")
    assert result["time"] == "2025-01-15T10:00:00Z"
    assert result["open"] == 1.08
    assert result["high"] == 1.09
    assert result["low"] == 1.07
    assert result["close"] == 1.085
    assert result["volume"] == 1000
    assert result["pair"] == "EUR_USD"
    assert result["granularity"] == "H1"
    assert result["complete"] is True


# ── Tests: fetch_candles (mocked) ─────────────────────────────────────────────

@patch.dict(os.environ, {
    "OANDA_API_KEY": "test-key",
    "OANDA_ACCOUNT_ID": "101-001-test",
    "OANDA_ENV": "practice",
})
@patch("tools.oanda.fetch_candles._build_client")
@patch("tools.oanda.fetch_candles.instruments")
def test_fetch_candles_writes_file(mock_instruments_module, mock_build_client, tmp_path, monkeypatch):
    from tools.oanda import fetch_candles as fc_module

    # Redirect .tmp/ to a temp directory
    monkeypatch.setattr(
        "tools.utils.file_io._TMP",
        tmp_path,
    )
    (tmp_path / "candles").mkdir(parents=True)

    # Mock OANDA API response
    mock_req = MagicMock()
    mock_req.response = MOCK_RESPONSE
    mock_client = MagicMock()
    mock_client.request = MagicMock()
    mock_instruments_module.InstrumentsCandles.return_value = mock_req
    mock_build_client.return_value = mock_client

    candles = fc_module.fetch_candles("EUR_USD", "H1", count=10)

    # Should filter out the incomplete candle
    assert len(candles) == 4
    # All returned candles should be complete
    assert all(c["complete"] for c in candles)
    # All required fields present
    for c in candles:
        for field in ("time", "open", "high", "low", "close", "volume", "pair", "granularity"):
            assert field in c, f"Missing field: {field}"


@patch.dict(os.environ, {
    "OANDA_API_KEY": "test-key",
    "OANDA_ACCOUNT_ID": "101-001-test",
    "OANDA_ENV": "practice",
})
@patch("tools.oanda.fetch_candles._build_client")
@patch("tools.oanda.fetch_candles.instruments")
def test_fetch_candles_sorted_by_time(mock_instruments_module, mock_build_client, tmp_path, monkeypatch):
    from tools.oanda import fetch_candles as fc_module

    monkeypatch.setattr("tools.utils.file_io._TMP", tmp_path)
    (tmp_path / "candles").mkdir(parents=True)

    mock_req = MagicMock()
    mock_req.response = MOCK_RESPONSE
    mock_client = MagicMock()
    mock_instruments_module.InstrumentsCandles.return_value = mock_req
    mock_build_client.return_value = mock_client

    candles = fc_module.fetch_candles("EUR_USD", "H1")
    times = [c["time"] for c in candles]
    assert times == sorted(times), "Candles should be in chronological order"


@patch.dict(os.environ, {
    "OANDA_API_KEY": "test-key",
    "OANDA_ACCOUNT_ID": "101-001-test",
    "OANDA_ENV": "practice",
})
@patch("tools.oanda.fetch_candles._build_client")
@patch("tools.oanda.fetch_candles.instruments")
def test_fetch_candles_no_duplicates(mock_instruments_module, mock_build_client, tmp_path, monkeypatch):
    from tools.oanda import fetch_candles as fc_module

    monkeypatch.setattr("tools.utils.file_io._TMP", tmp_path)
    (tmp_path / "candles").mkdir(parents=True)

    mock_req = MagicMock()
    mock_req.response = MOCK_RESPONSE
    mock_client = MagicMock()
    mock_instruments_module.InstrumentsCandles.return_value = mock_req
    mock_build_client.return_value = mock_client

    candles = fc_module.fetch_candles("EUR_USD", "H1")
    times = [c["time"] for c in candles]
    assert len(times) == len(set(times)), "Duplicate candle timestamps found"


# ── Tests: validators ─────────────────────────────────────────────────────────

def test_validate_granularity_valid():
    from tools.utils.validators import validate_granularity
    for tf in ("M1", "M5", "H1", "H4"):
        validate_granularity(tf)  # should not raise


def test_validate_granularity_invalid():
    from tools.utils.validators import validate_granularity
    with pytest.raises(ValueError):
        validate_granularity("D1")


def test_validate_pair_format_valid():
    from tools.utils.validators import validate_pair_format
    validate_pair_format("EUR_USD")
    validate_pair_format("GBP_JPY")


def test_validate_pair_format_invalid():
    from tools.utils.validators import validate_pair_format
    with pytest.raises(ValueError):
        validate_pair_format("EURUSD")  # missing underscore


# ── Tests: file_io path helpers ───────────────────────────────────────────────

def test_candle_path_format():
    from tools.utils.file_io import get_candle_path
    path = get_candle_path("EUR_USD", "H1")
    assert path.endswith("EUR_USD_H1.json")
    assert "candles" in path


def test_analysis_path_format():
    from tools.utils.file_io import get_analysis_path
    path = get_analysis_path("EUR_USD")
    assert path.endswith("EUR_USD_analysis.json")
    assert "analysis" in path


def test_signal_path_format():
    from tools.utils.file_io import get_signal_path
    path = get_signal_path("EUR_USD")
    assert path.endswith("EUR_USD_signals.json")
    assert "signals" in path


def test_write_and_read_json(tmp_path):
    from tools.utils import file_io
    test_path = str(tmp_path / "test.json")
    data = {"pair": "EUR_USD", "values": [1, 2, 3]}
    file_io.write_json(test_path, data)
    loaded = file_io.read_json(test_path)
    assert loaded == data


# ── Tests: missing env vars ───────────────────────────────────────────────────

def test_missing_api_key_raises():
    from tools.oanda.fetch_candles import _build_client
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(EnvironmentError, match="OANDA_API_KEY"):
            _build_client("practice")
