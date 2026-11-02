"""Tests for TradePlanBuilder (Phase 08 Builder). Fixed data and a fake practice account only."""

import pytest

from tools.models import TradePlan, TradePlanBuilder

PARTS = ("signal", "account", "entry", "stop_loss", "take_profit_1", "take_profit_2", "lot_size")


def full_builder(signal, account, skip=None):
    # Same values as the buy_plan fixture: 50 stop-loss pips × $10 per pip per lot × 0.1 lots = $50
    values = {"signal": signal, "account": account, "entry": 1.0900, "stop_loss": 1.0850,
              "take_profit_1": 1.1000, "take_profit_2": 1.1050, "lot_size": 0.1}
    builder = TradePlanBuilder()
    for part, value in values.items():
        if part != skip:
            getattr(builder, part)(value)
    return builder


def test_builds_a_trade_plan_with_the_given_parts(bullish_signal, practice_account):
    plan = full_builder(bullish_signal, practice_account).build()
    assert isinstance(plan, TradePlan)
    assert plan.signal is bullish_signal
    assert plan.account is practice_account
    assert plan.setup.direction == "buy"
    assert (plan.setup.entry, plan.setup.stop_loss, plan.setup.take_profit) == (1.0900, 1.0850, 1.1000)
    assert plan.take_profit_2 == 1.1050
    assert plan.lot_size == 0.1
    assert plan.risk_amount == 50.0


def test_built_plan_matches_a_directly_constructed_plan(bullish_signal, practice_account, buy_plan):
    plan = full_builder(bullish_signal, practice_account).build()
    assert plan.stop_loss_pips == buy_plan.stop_loss_pips
    assert plan.risk_amount == buy_plan.risk_amount
    assert plan.reference_timeframe == buy_plan.reference_timeframe


@pytest.mark.parametrize("missing", PARTS)
def test_missing_part_is_rejected(missing, bullish_signal, practice_account):
    builder = full_builder(bullish_signal, practice_account, skip=missing)
    with pytest.raises(ValueError, match=f"missing: {missing}$"):
        builder.build()


def test_empty_builder_names_every_missing_part():
    with pytest.raises(ValueError, match="missing: " + ", ".join(PARTS) + "$"):
        TradePlanBuilder().build()


def test_trade_plan_validation_still_applies(bullish_signal, practice_account):
    # R:R to TP1 of 1.0 is rejected by TradePlan itself; the builder adds no rules of its own
    builder = full_builder(bullish_signal, practice_account).take_profit_1(1.0950)
    with pytest.raises(ValueError, match="reward-to-risk to TP1 must be at least 2"):
        builder.build()
