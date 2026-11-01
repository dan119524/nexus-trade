"""
Integration tests for the FastAPI server.
Uses httpx TestClient — no running server required.

Run: pytest tests/test_api_endpoints.py -v
"""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from oandapyV20.exceptions import V20Error


@pytest.fixture(scope="module")
def client():
    import sys
    sys.path.insert(0, ".")
    from tools.api.server import app
    return TestClient(app)


# ── Health ────────────────────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert "timestamp" in r.json()


# ── Signals ───────────────────────────────────────────────────────────────────

def test_get_all_signals_returns_list(client, fake_tmp):
    r = client.get("/signals")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_signal_eur_usd(client, fake_tmp):
    r = client.get("/signals/EUR_USD")
    assert r.status_code == 200
    data = r.json()
    assert data["pair"] == "EUR_USD"
    assert "confluence" in data
    assert "trade_plan" in data


def test_get_signal_unknown_pair_404(client, fake_tmp):
    r = client.get("/signals/FAKE_PAIR")
    assert r.status_code == 404


# ── Candles ───────────────────────────────────────────────────────────────────

@pytest.fixture
def fake_oanda_candles(monkeypatch, tmp_path):
    """Empty candle cache in tmp_path and a fake OANDA client that returns 60 H1 candles."""
    def fake_candle_path(pair, granularity):
        return str(tmp_path / f"{pair}_{granularity}.json")

    monkeypatch.setattr("tools.api.server.get_candle_path", fake_candle_path)
    monkeypatch.setattr("tools.oanda.fetch_candles.get_candle_path", fake_candle_path)

    raw_candles = [
        {
            "time": f"2024-01-{1 + i // 24:02d}T{i % 24:02d}:00:00.000000000Z",
            "volume": 100 + i,
            "complete": True,
            "mid": {"o": "1.10000", "h": "1.10200", "l": "1.09900", "c": "1.10100"},
        }
        for i in range(60)
    ]

    def fake_request(endpoint):
        endpoint.response = {"candles": raw_candles}

    fake_client = MagicMock()
    fake_client.request.side_effect = fake_request
    monkeypatch.setattr("tools.oanda.fetch_candles._build_client", lambda env: fake_client)
    return fake_client


def test_get_candles_returns_list(client, fake_oanda_candles):
    r = client.get("/candles/EUR_USD/H1?limit=10")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 10
    assert len(data) > 0
    fake_oanda_candles.request.assert_called_once()


def test_get_candles_has_required_fields(client, fake_oanda_candles):
    r = client.get("/candles/EUR_USD/H1?limit=5")
    assert r.status_code == 200
    for c in r.json():
        for field in ("time", "open", "high", "low", "close", "volume"):
            assert field in c, f"Missing field: {field}"
    fake_oanda_candles.request.assert_called_once()


def test_get_candles_unknown_pair_404(client, monkeypatch, fake_tmp):
    # Fake OANDA client: rejects the instrument the way OANDA does
    fake_client = MagicMock()
    fake_client.request.side_effect = V20Error(
        400, '{"errorMessage":"Invalid value specified for \'instrument\'"}'
    )
    monkeypatch.setattr("tools.oanda.fetch_candles._build_client", lambda env: fake_client)

    r = client.get("/candles/FAKE_PAIR/H1")
    assert r.status_code == 404
    fake_client.request.assert_called_once()


def test_get_candles_unknown_timeframe_404(client, monkeypatch):
    fake_build_client = MagicMock()
    monkeypatch.setattr("tools.oanda.fetch_candles._build_client", fake_build_client)

    r = client.get("/candles/EUR_USD/D1")
    assert r.status_code == 404
    fake_build_client.assert_not_called()


# ── Analysis ──────────────────────────────────────────────────────────────────

def test_get_analysis_eur_usd(client, fake_tmp):
    r = client.get("/analysis/EUR_USD")
    assert r.status_code == 200
    data = r.json()
    assert data["pair"] == "EUR_USD"
    assert "timeframes" in data
    assert "H1" in data["timeframes"]


def test_get_analysis_has_structure_data(client, fake_tmp):
    r = client.get("/analysis/EUR_USD")
    tf = r.json()["timeframes"]["H1"]
    assert "trend" in tf
    assert tf["trend"] in ("bullish", "bearish", "ranging")
    assert "swing_highs" in tf
    assert "bos_events" in tf


def test_get_analysis_timeframe_endpoint(client, fake_tmp):
    r = client.get("/analysis/EUR_USD/H1")
    assert r.status_code == 200
    data = r.json()
    assert data["timeframe"] == "H1"
    assert data["pair"] == "EUR_USD"


def test_get_analysis_unknown_pair_404(client, fake_tmp):
    r = client.get("/analysis/FAKE_PAIR")
    assert r.status_code == 404


# ── Trade Plan ────────────────────────────────────────────────────────────────

def test_get_trade_plan(client, fake_tmp):
    r = client.get("/trade-plan/EUR_USD")
    assert r.status_code == 200
    plan = r.json()
    for field in ("entry_price", "stop_loss", "take_profit_1", "risk_reward", "lot_size"):
        assert field in plan, f"Missing field: {field}"


def test_trade_plan_rr_at_least_2(client, fake_tmp):
    r = client.get("/trade-plan/EUR_USD")
    assert r.status_code == 200
    assert r.json()["risk_reward"] >= 2.0


def test_trade_plan_sl_correct_side(client, fake_tmp):
    r = client.get("/trade-plan/EUR_USD")
    plan = r.json()
    if plan["direction"] == "bearish":
        assert plan["stop_loss"] > plan["entry_price"]
    else:
        assert plan["stop_loss"] < plan["entry_price"]


def test_get_trade_plan_unknown_pair_404(client, fake_tmp):
    r = client.get("/trade-plan/FAKE_PAIR")
    assert r.status_code == 404


# ── Pairs ─────────────────────────────────────────────────────────────────────

def test_get_pairs_returns_list(client, fake_tmp):
    r = client.get("/pairs")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert "EUR_USD" in r.json()
