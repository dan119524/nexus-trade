"""Tests for Account and its trades (Phases 05-06, FR5, FR9, FR11). Fake account IDs only."""

import pytest

from tools.models import Account, Order, Trade


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


# Recorded trades (Phase 06, FR11)

@pytest.fixture
def new_order(buy_plan, practice_account):
    """Return a function that makes a new Order on the buy plan: entry 1.0900, stop loss 1.0850, TP1 1.1000."""
    return lambda: Order(buy_plan, practice_account, confirmed=True)


def test_new_account_has_no_trades(practice_account):
    assert practice_account.trades == ()
    assert practice_account.open_trades() == ()
    assert practice_account.closed_trades() == ()


def test_trades_are_recorded_in_order_and_returned_as_a_tuple(practice_account, new_order):
    first, second = Trade(new_order(), "open"), Trade(new_order(), "win", 1.1000)
    practice_account.add_trade(first)
    practice_account.add_trade(second)

    assert practice_account.trades == (first, second)
    assert isinstance(practice_account.trades, tuple)


def test_open_and_closed_trades(practice_account, new_order):
    still_open = Trade(new_order(), "open")
    won = Trade(new_order(), "win", 1.1000)
    lost = Trade(new_order(), "loss", 1.0850)
    for trade in (still_open, won, lost):
        practice_account.add_trade(trade)

    assert practice_account.open_trades() == (still_open,)
    assert practice_account.closed_trades() == (won, lost)


def test_returned_trades_cannot_change_the_account(practice_account, new_order):
    practice_account.add_trade(Trade(new_order(), "open"))
    with pytest.raises(AttributeError):
        practice_account.trades.append(Trade(new_order(), "open"))
    assert len(practice_account.trades) == 1


def test_trade_for_another_account_is_rejected(new_order):
    other = make_account(account_id="FAKE-ACCOUNT-009")
    with pytest.raises(ValueError):
        other.add_trade(Trade(new_order(), "open"))


def test_same_trade_cannot_be_added_twice(practice_account, new_order):
    trade = Trade(new_order(), "open")
    practice_account.add_trade(trade)
    with pytest.raises(ValueError):
        practice_account.add_trade(trade)


@pytest.mark.parametrize("second_outcome, exit_price", [("open", None), ("win", 1.1000), ("loss", 1.0850)])
def test_only_one_trade_per_order_can_be_recorded(second_outcome, exit_price, practice_account, new_order):
    order = new_order()
    practice_account.add_trade(Trade(order, "open"))
    with pytest.raises(ValueError):
        practice_account.add_trade(Trade(order, second_outcome, exit_price))
    assert len(practice_account.trades) == 1


@pytest.mark.parametrize("trade", ["trade", None, 1])
def test_non_trade_is_rejected(trade, practice_account):
    with pytest.raises(ValueError):
        practice_account.add_trade(trade)


def test_remove_trade(practice_account, new_order):
    first, second = Trade(new_order(), "open"), Trade(new_order(), "win", 1.1000)
    practice_account.add_trade(first)
    practice_account.add_trade(second)

    practice_account.remove_trade(first)

    assert practice_account.trades == (second,)


def test_removing_a_trade_frees_its_order(practice_account, new_order):
    order = new_order()
    first = Trade(order, "open")
    practice_account.add_trade(first)
    practice_account.remove_trade(first)

    practice_account.add_trade(Trade(order, "win", 1.1000))
    assert len(practice_account.trades) == 1


def test_removing_a_trade_it_does_not_hold_is_rejected(practice_account, new_order):
    with pytest.raises(ValueError):
        practice_account.remove_trade(Trade(new_order(), "open"))


def test_close_trade_replaces_the_open_trade_in_place(practice_account, new_order):
    order = new_order()
    before = Trade(new_order(), "win", 1.1000)
    still_open = Trade(order, "open")
    after = Trade(new_order(), "loss", 1.0850)
    for trade in (before, still_open, after):
        practice_account.add_trade(trade)
    closed = Trade(order, "win", 1.1000)

    practice_account.close_trade(still_open, closed)

    assert practice_account.trades == (before, closed, after)
    assert practice_account.open_trades() == ()


def test_close_trade_needs_an_open_trade_it_holds(practice_account, new_order):
    order = new_order()
    with pytest.raises(ValueError):
        practice_account.close_trade(Trade(order, "open"), Trade(order, "win", 1.1000))
    won_order = new_order()
    won = Trade(won_order, "win", 1.1000)
    practice_account.add_trade(won)
    with pytest.raises(ValueError):
        practice_account.close_trade(won, Trade(won_order, "loss", 1.0850))


def test_close_trade_needs_a_closed_trade_for_the_same_order(practice_account, new_order, sell_plan):
    order = new_order()
    still_open = Trade(order, "open")
    practice_account.add_trade(still_open)
    with pytest.raises(ValueError):
        practice_account.close_trade(still_open, Trade(order, "open"))
    other_order = Order(sell_plan, practice_account, confirmed=True)
    with pytest.raises(ValueError):
        practice_account.close_trade(still_open, Trade(other_order, "win", 1.2600))
    assert practice_account.trades == (still_open,)


def test_close_trade_rejects_a_trade_already_recorded_for_another_order(practice_account, new_order):
    still_open, won = Trade(new_order(), "open"), Trade(new_order(), "win", 1.1000)
    practice_account.add_trade(still_open)
    practice_account.add_trade(won)
    with pytest.raises(ValueError):
        practice_account.close_trade(still_open, won)
