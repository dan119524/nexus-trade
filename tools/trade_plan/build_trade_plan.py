"""
Assemble a complete trade plan from a valid confluence signal.

Sequence:
  1. Load signal from .tmp/signals/
  2. Fetch current account balance
  3. Load analysis for reference timeframe (H1)
  4. calculate_entry()
  5. calculate_sl_tp()
  6. Gate: reject if RR < MIN_RISK_REWARD
  7. calculate_lot_size()
  8. Attach trade plan to signal and write back to .tmp/signals/

Usage (CLI):
    python -m tools.trade_plan.build_trade_plan --pair EUR_USD
    python -m tools.trade_plan.build_trade_plan --pair EUR_USD --risk 1.5
"""

import argparse
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from tools.trade_plan.calculate_entry   import calculate_entry
from tools.trade_plan.calculate_sl_tp   import calculate_sl_tp
from tools.trade_plan.calculate_lot_size import calculate_lot_size
from tools.oanda.fetch_account           import fetch_account
from tools.utils.file_io import (
    get_signal_path, get_analysis_path,
    read_json, write_json, file_exists,
)
from tools.utils.logger import get_logger

load_dotenv()
log = get_logger(__name__)

# Reference timeframe for entry/SL placement (highest that voted in direction)
_REFERENCE_TF_PRIORITY = ["H4", "H1", "M5", "M1"]


def _pick_reference_tf(confluence: dict) -> str:
    """Return the highest timeframe that voted with the signal direction."""
    direction = confluence["direction"]
    votes = confluence.get("votes", {})
    for tf in _REFERENCE_TF_PRIORITY:
        if votes.get(tf) == direction:
            return tf
    # Fallback: use H1
    return "H1"


def build_trade_plan(
    pair: str,
    risk_percent: float | None = None,
) -> dict | None:
    """
    Build a complete trade plan for a valid signal.

    Args:
        pair:         e.g. "EUR_USD"
        risk_percent: Override for risk % (defaults to RISK_PERCENT in .env).

    Returns:
        The updated signal dict with trade_plan populated, or None if rejected.
    """
    if risk_percent is None:
        risk_percent = float(os.getenv("RISK_PERCENT", 1.0))
    min_rr = float(os.getenv("MIN_RISK_REWARD", 2.0))

    # ── Load signal ────────────────────────────────────────────────────────────
    signal_path = get_signal_path(pair)
    if not file_exists(signal_path):
        log.error(f"No signal file for {pair}. Run score_confluence first.")
        return None

    signal = read_json(signal_path)
    confluence = signal.get("confluence", {})

    if not confluence.get("signal_valid"):
        log.error(f"Signal for {pair} is not valid (score < {confluence.get('min_score_required')}).")
        return None

    direction = confluence["direction"]

    # ── Load analysis ──────────────────────────────────────────────────────────
    analysis_path = get_analysis_path(pair)
    if not file_exists(analysis_path):
        log.error(f"No analysis file for {pair}.")
        return None

    analysis = read_json(analysis_path)
    ref_tf = _pick_reference_tf(confluence)
    tf_data = analysis["timeframes"].get(ref_tf)

    if not tf_data:
        log.error(f"No {ref_tf} data in analysis for {pair}.")
        return None

    log.info(f"Building trade plan for {pair} {direction} using {ref_tf} structure...")

    # Load candles for entry price
    from tools.utils.file_io import get_candle_path
    candle_path = get_candle_path(pair, ref_tf)
    candles = read_json(candle_path) if file_exists(candle_path) else []

    if not candles:
        log.error(f"No candles for {pair} {ref_tf}.")
        return None

    # ── Calculate components ───────────────────────────────────────────────────
    entry = calculate_entry(candles, direction)

    sl_tp = calculate_sl_tp(
        entry=entry,
        direction=direction,
        swing_highs=tf_data["swing_highs"],
        swing_lows=tf_data["swing_lows"],
        pair=pair,
    )

    # ── RR gate ────────────────────────────────────────────────────────────────
    if sl_tp["risk_reward"] < min_rr:
        log.warning(
            f"Setup rejected: RR={sl_tp['risk_reward']} < minimum {min_rr}. "
            f"Not a worthwhile trade."
        )
        return None

    # ── Fetch account balance ──────────────────────────────────────────────────
    try:
        account = fetch_account()
        balance = account["balance"]
        if balance <= 0:
            log.warning("Account balance is 0. Using fallback of 10,000 for sizing.")
            balance = 10_000.0
    except Exception as e:
        log.warning(f"Could not fetch account balance ({e}). Using fallback of 10,000.")
        balance = 10_000.0

    sizing = calculate_lot_size(
        account_balance=balance,
        risk_percent=risk_percent,
        sl_pips=sl_tp["sl_pips"],
        pair=pair,
        entry_price=entry,
    )

    # ── Build invalidation note ────────────────────────────────────────────────
    if direction == "bearish":
        invalidation = (
            f"Setup invalid if price closes above {sl_tp['stop_loss']} "
            f"(SL level). Bearish bias cancelled."
        )
    else:
        invalidation = (
            f"Setup invalid if price closes below {sl_tp['stop_loss']} "
            f"(SL level). Bullish bias cancelled."
        )

    # ── Assemble trade plan ────────────────────────────────────────────────────
    trade_plan = {
        "pair": pair,
        "direction": direction,
        "reference_timeframe": ref_tf,
        "entry_price": entry,
        "stop_loss": sl_tp["stop_loss"],
        "take_profit_1": sl_tp["take_profit_1"],
        "take_profit_2": sl_tp["take_profit_2"],
        "sl_pips": sl_tp["sl_pips"],
        "risk_reward": sl_tp["risk_reward"],
        "lot_size": sizing["lot_size"],
        "risk_amount_usd": sizing["risk_amount_usd"],
        "risk_percent": risk_percent,
        "account_balance": balance,
        "confluence_score": confluence["score"],
        "invalidation_note": invalidation,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    # ── Attach to signal and save ──────────────────────────────────────────────
    signal["trade_plan"] = trade_plan
    signal["status"] = "active"
    write_json(signal_path, signal)
    log.info(f"Trade plan attached to signal → {signal_path}")

    return signal


def _print_plan(signal: dict) -> None:
    plan = signal["trade_plan"]
    c = signal["confluence"]
    print(f"\n{'='*55}")
    print(f"  TRADE PLAN — {plan['pair']}  ({plan['direction'].upper()})")
    print(f"{'='*55}")
    print(f"  Confluence : {c['score']}/{c['max_score']}  {c['votes']}")
    print(f"  Ref TF     : {plan['reference_timeframe']}")
    print(f"  Entry      : {plan['entry_price']}")
    print(f"  Stop Loss  : {plan['stop_loss']}  ({plan['sl_pips']} pips)")
    print(f"  TP1        : {plan['take_profit_1']}  (RR {plan['risk_reward']}:1)")
    print(f"  TP2        : {plan['take_profit_2']}  (RR 3:1)")
    print(f"  Lot Size   : {plan['lot_size']}")
    print(f"  Risk       : ${plan['risk_amount_usd']}  ({plan['risk_percent']}%)")
    print(f"  Balance    : ${plan['account_balance']}")
    print(f"  Note       : {plan['invalidation_note']}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a trade plan for a valid signal")
    parser.add_argument("--pair", required=True)
    parser.add_argument("--risk", type=float, default=None, help="Risk % override")
    args = parser.parse_args()

    result = build_trade_plan(args.pair, risk_percent=args.risk)
    if result:
        _print_plan(result)
    else:
        print(f"\n✗ No trade plan generated for {args.pair}")
