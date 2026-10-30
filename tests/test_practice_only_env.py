"""
Tests that every OANDA client refuses anything except the practice environment (FR5).

Uses mocks and fake keys only. Never calls OANDA.
Run: pytest tests/test_practice_only_env.py -v
"""

from unittest.mock import MagicMock, patch

import pytest

REFUSED_ENVS = ["live", "LIVE", "Practice", "", "fxtrade"]


@pytest.fixture
def fake_keys(monkeypatch):
    monkeypatch.setenv("OANDA_API_KEY", "fake-key")
    monkeypatch.setenv("OANDA_ACCOUNT_ID", "FAKE-ACCOUNT-001")


# ── The shared check ──────────────────────────────────────────────────────────

def test_practice_env_is_allowed():
    from tools.utils.validators import require_practice_env
    require_practice_env("practice")


@pytest.mark.parametrize("env", REFUSED_ENVS)
def test_any_other_env_is_refused(env):
    from tools.utils.validators import require_practice_env
    with pytest.raises(EnvironmentError, match="Only the practice environment is allowed"):
        require_practice_env(env)


def test_validate_env_accepts_practice():
    from tools.utils.validators import validate_env
    validate_env("practice")


@pytest.mark.parametrize("env", REFUSED_ENVS)
def test_validate_env_rejects_everything_else(env):
    from tools.utils.validators import validate_env
    with pytest.raises(ValueError, match="Must be 'practice'"):
        validate_env(env)


# ── fetch_candles, fetch_account, fetch_instruments ───────────────────────────

CLIENT_MODULES = ["tools.oanda.fetch_candles", "tools.oanda.fetch_account", "tools.oanda.fetch_instruments"]


@pytest.mark.parametrize("module", CLIENT_MODULES)
@pytest.mark.parametrize("env", REFUSED_ENVS)
def test_build_client_refuses_non_practice_env(module, env, fake_keys):
    with patch(f"{module}.API") as api:
        build_client = __import__(module, fromlist=["_build_client"])._build_client
        with pytest.raises(EnvironmentError, match="refused"):
            build_client(env)
    api.assert_not_called()


@pytest.mark.parametrize("module", CLIENT_MODULES)
def test_build_client_uses_practice(module, fake_keys):
    with patch(f"{module}.API") as api:
        __import__(module, fromlist=["_build_client"])._build_client("practice")
    api.assert_called_once_with(access_token="fake-key", environment="practice")


def test_fetch_candles_refuses_live_before_any_request(fake_keys):
    from tools.oanda.fetch_candles import fetch_candles
    with patch("tools.oanda.fetch_candles.API") as api:
        with pytest.raises(EnvironmentError):
            fetch_candles("EUR_USD", "H1", env="live")
    api.assert_not_called()


def test_fetch_candles_refuses_live_from_dotenv(fake_keys, monkeypatch):
    from tools.oanda.fetch_candles import fetch_candles
    monkeypatch.setenv("OANDA_ENV", "live")
    with patch("tools.oanda.fetch_candles.API") as api:
        with pytest.raises(EnvironmentError):
            fetch_candles("EUR_USD", "H1")
    api.assert_not_called()


def test_fetch_account_refuses_live(fake_keys):
    from tools.oanda.fetch_account import fetch_account
    with patch("tools.oanda.fetch_account.API") as api:
        with pytest.raises(EnvironmentError):
            fetch_account(env="live")
    api.assert_not_called()


def test_fetch_instruments_refuses_live(fake_keys, monkeypatch):
    import tools.oanda.fetch_instruments as fi
    monkeypatch.setattr(fi, "_INSTRUMENTS_CACHE", None)
    with patch("tools.oanda.fetch_instruments.API") as api:
        with pytest.raises(EnvironmentError):
            fi.fetch_instruments(env="live")
    api.assert_not_called()


# ── execute_trade (also used by weekly_cycle to poll trades) ──────────────────

def test_execute_trade_client_refuses_live(fake_keys, monkeypatch):
    from tools.oanda.execute_trade import _build_client
    monkeypatch.setenv("OANDA_ENV", "live")
    with patch("tools.oanda.execute_trade.API") as api:
        with pytest.raises(EnvironmentError):
            _build_client()
    api.assert_not_called()


def test_execute_trade_client_uses_practice(fake_keys, monkeypatch):
    from tools.oanda.execute_trade import _build_client
    monkeypatch.setenv("OANDA_ENV", "practice")
    with patch("tools.oanda.execute_trade.API") as api:
        _, account_id = _build_client()
    api.assert_called_once_with(access_token="fake-key", environment="practice")
    assert account_id == "FAKE-ACCOUNT-001"


# ── weekly_cycle and server build their own pricing clients ───────────────────

def test_weekly_cycle_milestones_never_build_a_live_client(fake_keys, monkeypatch):
    from tools.scheduler.weekly_cycle import _check_trade_milestones
    monkeypatch.setenv("OANDA_ENV", "live")
    with patch("oandapyV20.API") as api:
        _check_trade_milestones([{"pair": "EUR_USD"}], [])
    api.assert_not_called()


def test_weekly_cycle_milestones_use_practice(fake_keys, monkeypatch):
    from tools.scheduler.weekly_cycle import _check_trade_milestones
    monkeypatch.setenv("OANDA_ENV", "practice")
    with patch("oandapyV20.API") as api, patch("oandapyV20.endpoints.pricing.PricingInfo") as info:
        info.return_value = MagicMock(response={"prices": []})
        _check_trade_milestones([{"pair": "EUR_USD"}], [])
    api.assert_called_once_with(access_token="fake-key", environment="practice")


def test_server_prices_refuses_live(fake_keys, monkeypatch):
    from fastapi.testclient import TestClient
    from tools.api.server import app
    monkeypatch.setenv("OANDA_ENV", "live")
    with patch("oandapyV20.API") as api:
        r = TestClient(app).get("/prices?instruments=EUR_USD")
    assert r.status_code == 502
    assert "refused" in r.json()["detail"]
    api.assert_not_called()


def test_server_prices_use_practice(fake_keys, monkeypatch):
    from fastapi.testclient import TestClient
    from tools.api.server import app
    monkeypatch.setenv("OANDA_ENV", "practice")
    with patch("oandapyV20.API") as api, patch("oandapyV20.endpoints.pricing.PricingInfo") as info:
        info.return_value = MagicMock(response={"prices": []})
        r = TestClient(app).get("/prices?instruments=EUR_USD")
    assert r.status_code == 200
    api.assert_called_once_with(access_token="fake-key", environment="practice")
