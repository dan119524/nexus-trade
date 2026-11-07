"""Tests that trade lookups go through tools/oanda/execute_trade.py (Phase 09 Facade). Never calls OANDA."""

import pytest

import tools.oanda.execute_trade as execute_trade
import tools.reporting.email_report as email_report
import tools.reporting.trade_journal as trade_journal
from tools.scheduler import weekly_cycle


class _FakeClient:
    """Answers OANDA trade requests with fixed data and records what was asked."""

    def __init__(self, responses):
        self.responses = responses
        self.requested = []

    def request(self, req):
        self.requested.append(type(req).__name__)
        req.response = self.responses[type(req).__name__]


def test_get_trade_details_returns_the_trade(monkeypatch):
    fake = _FakeClient({"TradeDetails": {"trade": {"id": "42", "realizedPL": "12.5"}}})
    monkeypatch.setattr(execute_trade, "_build_client", lambda: (fake, "FAKE-ACCOUNT"))
    assert execute_trade.get_trade_details("42") == {"id": "42", "realizedPL": "12.5"}
    assert fake.requested == ["TradeDetails"]


def test_get_trade_details_missing_trade_gives_empty_dict(monkeypatch):
    fake = _FakeClient({"TradeDetails": {}})
    monkeypatch.setattr(execute_trade, "_build_client", lambda: (fake, "FAKE-ACCOUNT"))
    assert execute_trade.get_trade_details("42") == {}


def test_scheduler_records_closed_trade_through_execute_trade(monkeypatch):
    patched = []
    monkeypatch.setattr(trade_journal, "get_open", lambda: [{"trade_id": "42", "pair": "EUR_USD"}])
    monkeypatch.setattr(trade_journal, "patch_outcome",
                        lambda tid, outcome, exit_price, close_time, pnl:
                        patched.append((tid, outcome, exit_price, pnl)) or {"trade_id": tid})
    monkeypatch.setattr(email_report, "send_trade_win_email", lambda entry: None)
    monkeypatch.setattr(execute_trade, "get_open_trades", lambda: [])
    monkeypatch.setattr(execute_trade, "get_trade_details", lambda tid: {
        "id": tid, "realizedPL": "25.0", "averageClosePrice": "1.1000",
        "closeTime": "2026-10-15T20:00:00Z"})

    def no_client():
        raise AssertionError("the scheduler must not build its own OANDA client")
    monkeypatch.setattr(execute_trade, "_build_client", no_client)

    weekly_cycle._poll_closed_trades()
    assert patched == [("42", "win", 1.1, 25.0)]


def test_get_mid_prices_averages_bid_and_ask(monkeypatch):
    fake = _FakeClient({"PricingInfo": {"prices": [
        {"instrument": "EUR_USD", "bids": [{"price": "1.0900"}], "asks": [{"price": "1.0902"}]},
        {"instrument": "GBP_USD", "bids": [], "asks": [{"price": "1.2700"}]},
    ]}})
    monkeypatch.setattr(execute_trade, "_build_client", lambda: (fake, "FAKE-ACCOUNT"))
    prices = execute_trade.get_mid_prices(["EUR_USD", "GBP_USD"])
    assert prices == {"EUR_USD": pytest.approx(1.0901)}
    assert fake.requested == ["PricingInfo"]


def test_get_mid_prices_with_no_pairs_asks_nothing(monkeypatch):
    def no_client():
        raise AssertionError("no pairs, no OANDA request")
    monkeypatch.setattr(execute_trade, "_build_client", no_client)
    assert execute_trade.get_mid_prices([]) == {}


def test_milestone_check_gets_prices_through_execute_trade(monkeypatch, tmp_path):
    sent = []
    monkeypatch.setattr(execute_trade, "get_mid_prices", lambda pairs: {"EUR_USD": 1.1080})
    monkeypatch.setattr(email_report, "send_trade_status_email",
                        lambda entry, price, key: sent.append((entry["trade_id"], key)))
    monkeypatch.setattr(weekly_cycle, "_load_milestones", lambda: {})
    monkeypatch.setattr(weekly_cycle, "_save_milestones", lambda m: None)

    def no_client():
        raise AssertionError("the scheduler must not build its own OANDA client")
    monkeypatch.setattr(execute_trade, "_build_client", no_client)

    # Buy at 1.1000 with TP 1.1100: 1.1080 is 80% of the way to TP
    entry = {"trade_id": "42", "pair": "EUR_USD", "direction": "bullish",
             "entry_price": 1.1000, "stop_loss": 1.0950, "take_profit": 1.1100}
    weekly_cycle._check_trade_milestones([entry], [])
    assert sent == [("42", "TP50"), ("42", "TP80")]
