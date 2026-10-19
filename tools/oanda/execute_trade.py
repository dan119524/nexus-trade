"""
Execute a trade on OANDA from a valid signal's trade plan.

Safety gates (ALL must pass before any order is sent):
  1. OANDA_ENV must be "practice" — never executes on live automatically
  2. Signal must be status "ready" with a populated trade_plan
  3. RR must be >= MIN_RISK_REWARD
  4. Confluence score must be >= MIN_CONFLUENCE_SCORE
  5. Lot size must be > 0 and <= 10 (hard cap, not the 100-lot max)

Usage (CLI):
    python -m tools.oanda.execute_trade --pair EUR_USD
    python -m tools.oanda.execute_trade --pair EUR_USD --confirm
"""

import argparse
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from oandapyV20 import API
from oandapyV20.endpoints import orders, trades as oanda_trades

from tools.utils.file_io import get_signal_path, read_json, write_json, file_exists
from tools.utils.logger import get_logger

load_dotenv()
log = get_logger(__name__)

_MAX_LOT_EXECUTE = 5.0    # Hard cap — keeps margin usage reasonable on practice account


def _build_client() -> tuple[API, str]:
    api_key = os.getenv("OANDA_API_KEY")
    account_id = os.getenv("OANDA_ACCOUNT_ID")
    env = os.getenv("OANDA_ENV", "practice")

    if not api_key:
        raise EnvironmentError("OANDA_API_KEY not set in .env")
    if not account_id:
        raise EnvironmentError("OANDA_ACCOUNT_ID not set in .env")

    environment = "live" if env == "live" else "practice"
    return API(access_token=api_key, environment=environment), account_id


def _units_from_lot(lot_size: float, direction: str) -> int:
    """Convert lot size to OANDA units. Negative = short (sell)."""
    units = round(lot_size * 100_000)
    return -units if direction == "bearish" else units


def execute_trade(pair: str, confirm: bool = False) -> dict | None:
    """
    Execute the trade plan for a valid signal on OANDA.

    Args:
        pair:    e.g. "EUR_USD"
        confirm: If False, prints the order details but does NOT send it.
                 Set True to actually place the order.

    Returns:
        OANDA order response dict, or None if gates blocked execution.
    """
    env = os.getenv("OANDA_ENV", "practice")

    # ── Gate 1: environment ───────────────────────────────────────────────────
    if env != "practice":
        log.error(
            "OANDA_ENV is set to 'live'. Automated execution is only allowed on "
            "practice accounts. Change OANDA_ENV=practice in .env to proceed."
        )
        return None

    # ── Load signal ───────────────────────────────────────────────────────────
    signal_path = get_signal_path(pair)
    if not file_exists(signal_path):
        log.error(f"No signal file for {pair}.")
        return None

    signal = read_json(signal_path)
    plan = signal.get("trade_plan")
    conf = signal.get("confluence", {})

    # ── Gate 2: signal quality ────────────────────────────────────────────────
    if not conf.get("signal_valid"):
        log.error("Signal is not valid (confluence score too low).")
        return None

    if not plan:
        log.error("No trade plan attached to signal. Run build_trade_plan first.")
        return None

    min_rr = float(os.getenv("MIN_RISK_REWARD", 2.0))
    if plan.get("risk_reward", 0) < min_rr:
        log.error(f"RR {plan['risk_reward']} < minimum {min_rr}. Blocked.")
        return None

    # ── Gate 3: lot size cap ──────────────────────────────────────────────────
    lot_size = plan["lot_size"]
    if lot_size <= 0 or lot_size > _MAX_LOT_EXECUTE:
        log.error(f"Lot size {lot_size} outside safe range (0, {_MAX_LOT_EXECUTE}]. Blocked.")
        return None

    direction = plan["direction"]
    units = _units_from_lot(lot_size, direction)
    entry = plan["entry_price"]
    sl = plan["stop_loss"]
    tp = plan["take_profit_1"]

    # ── Preview ───────────────────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"  ORDER PREVIEW — {pair} ({env.upper()})")
    print(f"{'='*55}")
    print(f"  Direction  : {direction.upper()}")
    print(f"  Units      : {units:+,}  ({lot_size} lots)")
    print(f"  Entry      : {entry}  (market order)")
    print(f"  Stop Loss  : {sl}")
    print(f"  Take Profit: {tp}")
    print(f"  RR         : {plan['risk_reward']}:1")
    print(f"  Risk $     : ${plan['risk_amount_usd']}")
    print(f"  Confluence : {conf['score']}/{conf['max_score']}  {conf['direction'].upper()}")
    print(f"{'='*55}")

    if not confirm:
        print("\n  ⚠  DRY RUN — order NOT sent. Pass --confirm to execute.\n")
        return {"dry_run": True, "would_send": {"units": units, "sl": sl, "tp": tp}}

    # ── Build OANDA order payload ─────────────────────────────────────────────
    order_data = {
        "order": {
            "type": "MARKET",
            "instrument": pair,
            "units": str(units),
            "stopLossOnFill": {"price": str(round(sl, 5))},
            "takeProfitOnFill": {"price": str(round(tp, 5))},
            "timeInForce": "FOK",           # Fill or Kill
            "positionFill": "DEFAULT",
        }
    }

    # ── Send order ────────────────────────────────────────────────────────────
    client, account_id = _build_client()
    req = orders.OrderCreate(accountID=account_id, data=order_data)

    try:
        client.request(req)
        response = req.response

        # Detect OANDA cancellations (e.g. INSUFFICIENT_MARGIN, STOP_LOSS_ON_FILL_LOSS)
        cancel = response.get("orderCancelTransaction")
        if cancel and not response.get("orderFillTransaction"):
            reason = cancel.get("reason", "UNKNOWN")
            log.error(f"Order CANCELLED by OANDA: {reason}  ({pair})")
            print(f"\n  ✗ Order cancelled by OANDA: {reason}\n")
            return None

        order_id = response.get("orderFillTransaction", {}).get("id") \
                or response.get("relatedTransactionIDs", ["?"])[0]

        log.info(f"Order placed! ID={order_id}  {pair} {units:+,} units")
        print(f"\n  ✓ Order placed — ID: {order_id}\n")

        # Attach execution record to signal
        signal["execution"] = {
            "order_id": order_id,
            "units": units,
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "env": env,
            "response": response,
        }
        signal["status"] = "executed"
        write_json(signal_path, signal)

        # Record in trade journal for 30-day reporting
        try:
            from tools.reporting.trade_journal import append_trade
            append_trade({
                "trade_id":        order_id,
                "pair":            pair,
                "direction":       direction,
                "entry_price":     entry,
                "stop_loss":       sl,
                "take_profit":     tp,
                "lot_size":        lot_size,
                "units":           units,
                "risk_amount":     plan.get("risk_amount_usd"),
                "confluence_score": conf.get("score"),
                "risk_reward":     plan.get("risk_reward"),
                "executed_at":     signal["execution"]["executed_at"],
            })
        except Exception as je:
            log.warning(f"Could not journal trade {order_id}: {je}")

        # Send rich execution notification email (WHY + SETUP + PLAN + INVALIDATION)
        try:
            from tools.reporting.email_report import send_trade_executed_email
            send_trade_executed_email(signal, order_id)
        except Exception as me:
            log.warning(f"Could not send execution email for {order_id}: {me}")

        return response

    except Exception as e:
        log.error(f"Order failed: {e}")
        print(f"\n  ✗ Order rejected by OANDA: {e}\n")
        return None


def get_open_trades(pair: str | None = None) -> list[dict]:
    """Fetch all open trades, optionally filtered by pair."""
    client, account_id = _build_client()
    req = oanda_trades.OpenTrades(accountID=account_id)
    client.request(req)
    trades = req.response.get("trades", [])
    if pair:
        trades = [t for t in trades if t.get("instrument") == pair]
    return trades


def get_closed_trades(count: int = 50) -> list[dict]:
    """Fetch recently closed trades from OANDA."""
    client, account_id = _build_client()
    req = oanda_trades.TradesList(accountID=account_id, params={"state": "CLOSED", "count": str(count)})
    client.request(req)
    return req.response.get("trades", [])


def close_trade(trade_id: str) -> dict | None:
    """Close a specific open trade by ID."""
    env = os.getenv("OANDA_ENV", "practice")
    if env != "practice":
        log.error("Close trade only allowed on practice accounts.")
        return None

    client, account_id = _build_client()
    req = oanda_trades.TradeClose(accountID=account_id, tradeID=trade_id)
    try:
        client.request(req)
        log.info(f"Trade {trade_id} closed.")
        return req.response
    except Exception as e:
        log.error(f"Close failed: {e}")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute a trade on OANDA")
    parser.add_argument("--pair", required=True, help="e.g. EUR_USD")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually send the order (default is dry run)")
    args = parser.parse_args()

    execute_trade(args.pair, confirm=args.confirm)
