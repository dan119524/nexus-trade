"""
Integration tests for the FastAPI server.
Uses httpx TestClient — no running server required.

Run: pytest tests/test_api_endpoints.py -v
"""

import pytest
from fastapi.testclient import TestClient


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

def test_get_all_signals_returns_list(client):
    r = client.get("/signals")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_signal_eur_usd(client):
    r = client.get("/signals/EUR_USD")
    assert r.status_code == 200
    data = r.json()
    assert data["pair"] == "EUR_USD"
    assert "confluence" in data
    assert "trade_plan" in data


def test_get_signal_unknown_pair_404(client):
    r = client.get("/signals/FAKE_PAIR")
    assert r.status_code == 404


# ── Candles ───────────────────────────────────────────────────────────────────

def test_get_candles_returns_list(client):
    r = client.get("/candles/EUR_USD/H1?limit=10")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 10
    assert len(data) > 0


def test_get_candles_has_required_fields(client):
    r = client.get("/candles/EUR_USD/H1?limit=5")
    assert r.status_code == 200
    for c in r.json():
        for field in ("time", "open", "high", "low", "close", "volume"):
            assert field in c, f"Missing field: {field}"


def test_get_candles_unknown_pair_404(client):
    r = client.get("/candles/FAKE_PAIR/H1")
    assert r.status_code == 404


def test_get_candles_unknown_timeframe_404(client):
    r = client.get("/candles/EUR_USD/D1")
    assert r.status_code == 404


# ── Analysis ──────────────────────────────────────────────────────────────────

def test_get_analysis_eur_usd(client):
    r = client.get("/analysis/EUR_USD")
    assert r.status_code == 200
    data = r.json()
    assert data["pair"] == "EUR_USD"
    assert "timeframes" in data
    assert "H1" in data["timeframes"]


def test_get_analysis_has_structure_data(client):
    r = client.get("/analysis/EUR_USD")
    tf = r.json()["timeframes"]["H1"]
    assert "trend" in tf
    assert tf["trend"] in ("bullish", "bearish", "ranging")
    assert "swing_highs" in tf
    assert "bos_events" in tf


def test_get_analysis_timeframe_endpoint(client):
    r = client.get("/analysis/EUR_USD/H1")
    assert r.status_code == 200
    data = r.json()
    assert data["timeframe"] == "H1"
    assert data["pair"] == "EUR_USD"


def test_get_analysis_unknown_pair_404(client):
    r = client.get("/analysis/FAKE_PAIR")
    assert r.status_code == 404


# ── Trade Plan ────────────────────────────────────────────────────────────────

def test_get_trade_plan(client):
    r = client.get("/trade-plan/EUR_USD")
    assert r.status_code == 200
    plan = r.json()
    for field in ("entry_price", "stop_loss", "take_profit_1", "risk_reward", "lot_size"):
        assert field in plan, f"Missing field: {field}"


def test_trade_plan_rr_at_least_2(client):
    r = client.get("/trade-plan/EUR_USD")
    assert r.status_code == 200
    assert r.json()["risk_reward"] >= 2.0


def test_trade_plan_sl_correct_side(client):
    r = client.get("/trade-plan/EUR_USD")
    plan = r.json()
    if plan["direction"] == "bearish":
        assert plan["stop_loss"] > plan["entry_price"]
    else:
        assert plan["stop_loss"] < plan["entry_price"]


def test_get_trade_plan_unknown_pair_404(client):
    r = client.get("/trade-plan/FAKE_PAIR")
    assert r.status_code == 404


# ── Pairs ─────────────────────────────────────────────────────────────────────

def test_get_pairs_returns_list(client):
    r = client.get("/pairs")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert "EUR_USD" in r.json()
