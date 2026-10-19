"""Tests for Account (Phase 05, FR5 and FR9). Fake account IDs only."""

import pytest

from tools.models import Account


def make_account(**changes):
    values = {"account_id": "FAKE-ACCOUNT-001", "balance": 5000, "currency": "USD",
              "environment": "practice", "risk_percent": 1.0}
    values.update(changes)
    return Account(**values)


def test_valid_account_stores_values():
    account = make_account()
    assert account.account_id == "FAKE-ACCOUNT-001"
    assert account.balance == 5000.0
    assert account.currency == "USD"
    assert account.environment == "practice"
    assert account.risk_percent == 1.0


def test_max_risk_amount_is_balance_times_risk_percent():
    assert make_account(balance=5000, risk_percent=1.0).max_risk_amount() == 50.0
    assert make_account(balance=10000, risk_percent=2).max_risk_amount() == 200.0


@pytest.mark.parametrize("environment", ["live", "Practice", "", None])
def test_only_practice_environment_is_allowed(environment):
    with pytest.raises(ValueError):
        make_account(environment=environment)


@pytest.mark.parametrize("risk_percent", [0, -1, 2.01, 5, float("nan"), "1", True])
def test_risk_percent_must_be_above_0_and_at_most_2(risk_percent):
    with pytest.raises(ValueError):
        make_account(risk_percent=risk_percent)


def test_risk_percent_of_exactly_2_is_allowed():
    assert make_account(risk_percent=2).risk_percent == 2.0


@pytest.mark.parametrize("balance", [0, -100, "5000", None])
def test_invalid_balance_is_rejected(balance):
    with pytest.raises(ValueError):
        make_account(balance=balance)


@pytest.mark.parametrize("currency", ["usd", "US", "USDX", None])
def test_invalid_currency_is_rejected(currency):
    with pytest.raises(ValueError):
        make_account(currency=currency)


@pytest.mark.parametrize("account_id", ["", "   ", None, 101])
def test_invalid_account_id_is_rejected(account_id):
    with pytest.raises(ValueError):
        make_account(account_id=account_id)


def test_account_is_read_only():
    account = make_account()
    with pytest.raises(AttributeError):
        account.environment = "live"
