"""
Weekly trading cycle scheduler.

Weekend (Sat 00:00 UTC → Mon 00:00 UTC):
    Runs backtests for every configured pair over the last 30 days,
    saves results to .tmp/backtest/auto_PAIR_YYYYMMDD.json.

Weekday (Mon → Fri):
    Runs the full signal pipeline in a continuous loop:
    fetch candles → analyse structure → score confluence → build trade plan.
    Signals are written to .tmp/signals/ and served by the FastAPI server.

Usage:
    python -m tools.scheduler.weekly_cycle
    python -m tools.scheduler.weekly_cycle --pairs EUR_USD GBP_USD USD_JPY
    python -m tools.scheduler.weekly_cycle --interval 300
"""

import argparse
import json
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

from tools.utils.logger import get_logger

load_dotenv()
log = get_logger(__name__)

STATUS_PATH         = Path(__file__).resolve().parents[2] / ".tmp" / "scheduler_status.json"
REPORT_STATE_PATH   = Path(__file__).resolve().parents[2] / ".tmp" / "report_state.json"
SELECTED_PAIRS_PATH = Path(__file__).resolve().parents[2] / ".tmp" / "selected_pairs.json"
_SESSION_STATE_PATH = Path(__file__).resolve().parents[2] / ".tmp" / "session_email_state.json"

# Session close times in UTC hours (fires within 10 min of close)
_SESSIONS = {
    "ASIAN":     9,   # closes 09:00 UTC
    "LONDON":   16,   # closes 16:00 UTC
    "NEW YORK": 21,   # closes 21:00 UTC
}


def _load_session_state() -> dict:
    if _SESSION_STATE_PATH.exists():
        try:
            return json.loads(_SESSION_STATE_PATH.read_text())
        except Exception:
            pass
    return {}


def _save_session_state(state: dict) -> None:
    _SESSION_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _SESSION_STATE_PATH.write_text(json.dumps(state, indent=2))


def _check_session_close() -> None:
    """Fire a session-close email if we just passed a session boundary (within 10 min window)."""
    try:
        from tools.reporting.email_report import send_session_close_email
        from tools.reporting.trade_journal import get_all as get_journal

        now   = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")
        state = _load_session_state()

        journal = []
        try:
            journal = get_journal()
        except Exception:
            pass

        open_trades  = [t for t in journal if not t.get("outcome")]
        today_trades = [t for t in journal
                        if (t.get("executed_at") or t.get("exit_time") or "").startswith(today)]

        changed = False
        for session, close_hour in _SESSIONS.items():
            key = f"{today}_{session}"
            if state.get(key):
                continue  # already sent today

            minutes_past = (now.hour - close_hour) * 60 + now.minute
            if 0 <= minutes_past < 10:
                try:
                    send_session_close_email(session, open_trades, today_trades)
                    state[key] = now.isoformat()
                    changed = True
                    log.info(f"Session-close email sent: {session}")
                except Exception as e:
                    log.warning(f"Session-close email failed ({session}): {e}")

        if changed:
            _save_session_state(state)

        # Prune keys older than 3 days
        cutoff = (now - timedelta(days=3)).strftime("%Y-%m-%d")
        pruned = {k: v for k, v in state.items() if k[:10] >= cutoff}
        if len(pruned) != len(state):
            _save_session_state(pruned)

    except Exception as e:
        log.warning(f"_check_session_close failed: {e}")

# Full universe tested every weekend — top performers promoted to live trading
PAIR_UNIVERSE = [
    # Majors
    "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD",
    # Euro crosses
    "EUR_GBP", "EUR_JPY", "EUR_AUD", "EUR_CAD", "EUR_CHF",
    # Sterling crosses
    "GBP_JPY", "GBP_AUD", "GBP_CAD",
    # Antipodean / commodity crosses
    "AUD_JPY", "AUD_CAD", "AUD_NZD", "NZD_JPY",
    # Others
    "CAD_JPY", "CHF_JPY",
    # Gold
    "XAU_USD",
]

DEFAULT_PAIRS    = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "EUR_GBP"]
DEFAULT_INTERVAL = 300   # seconds between full scan cycles on weekdays


# ── Helpers ───────────────────────────────────────────────────────────────────

def is_weekend() -> bool:
    """True on Saturday (5) and Sunday (6) UTC."""
    return datetime.now(timezone.utc).weekday() >= 5


def next_switch_time() -> datetime:
    """UTC datetime of the next mode switch (Saturday midnight or Monday midnight)."""
    now = datetime.now(timezone.utc)
    wd  = now.weekday()   # Mon=0 … Sun=6
    if wd < 5:
        days = 5 - wd     # days until Saturday
    else:
        days = 7 - wd     # days until Monday
    return (now + timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)


def write_status(mode: str, detail: str = "", **kwargs) -> None:
    nxt = next_switch_time()
    is_wknd = is_weekend()
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "mode":              mode,
        "detail":            detail,
        "updated_at":        datetime.now(timezone.utc).isoformat(),
        "next_switch":       nxt.isoformat(),
        "next_switch_label": f"{'Monday' if is_wknd else 'Saturday'} {nxt.strftime('%d %b, %H:%M')} UTC",
        **kwargs,
    }
    STATUS_PATH.write_text(json.dumps(payload, indent=2))
    log.info(f"[scheduler] {mode}: {detail}")


# ── Report state helpers ──────────────────────────────────────────────────────

def _load_report_state() -> dict:
    if REPORT_STATE_PATH.exists():
        try:
            return json.loads(REPORT_STATE_PATH.read_text())
        except Exception:
            pass
    return {"last_30day_report": None, "last_weekly_report": None, "trade_start": None}


def _save_report_state(state: dict) -> None:
    REPORT_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_STATE_PATH.write_text(json.dumps(state, indent=2))


# ── Poll OANDA for newly closed trades ────────────────────────────────────────

_STATUS_MILESTONE_PATH = Path(__file__).resolve().parents[2] / ".tmp" / "trade_milestones.json"


def _load_milestones() -> dict:
    if _STATUS_MILESTONE_PATH.exists():
        try:
            return json.loads(_STATUS_MILESTONE_PATH.read_text())
        except Exception:
            pass
    return {}


def _save_milestones(m: dict) -> None:
    _STATUS_MILESTONE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STATUS_MILESTONE_PATH.write_text(json.dumps(m, indent=2))


def _check_trade_milestones(open_entries: list[dict], oanda_open: list[dict]) -> None:
    """Send status emails when open trades hit 50% or 80% progress toward TP or SL."""
    if not open_entries:
        return
    try:
        from tools.reporting.email_report import send_trade_status_email
        import os
        from oandapyV20 import API
        from oandapyV20.endpoints.pricing import PricingInfo

        api_key    = os.getenv("OANDA_API_KEY")
        account_id = os.getenv("OANDA_ACCOUNT_ID")
        env        = os.getenv("OANDA_ENV", "practice")
        client     = API(access_token=api_key, environment="practice" if env == "practice" else "live")

        instruments = ",".join({e.get("pair", "") for e in open_entries if e.get("pair")})
        if not instruments:
            return

        req = PricingInfo(accountID=account_id, params={"instruments": instruments})
        client.request(req)
        prices = {}
        for p in req.response.get("prices", []):
            bid = float(p["bids"][0]["price"]) if p.get("bids") else None
            ask = float(p["asks"][0]["price"]) if p.get("asks") else None
            if bid and ask:
                prices[p["instrument"]] = (bid + ask) / 2

        milestones = _load_milestones()
        changed    = False

        for entry in open_entries:
            tid   = str(entry.get("trade_id", ""))
            pair  = entry.get("pair", "")
            ep    = float(entry.get("entry_price") or 0)
            sl    = float(entry.get("stop_loss")   or 0)
            tp    = float(entry.get("take_profit")  or 0)
            dirn  = (entry.get("direction") or "").upper()
            cur   = prices.get(pair)

            if not cur or not ep or not sl or not tp:
                continue

            is_long = dirn == "BULLISH"
            tp_dist = abs(tp - ep)
            sl_dist = abs(sl - ep)

            tp_pct = abs(cur - ep) / tp_dist * 100 if tp_dist else 0
            sl_pct = abs(cur - ep) / sl_dist * 100 if sl_dist else 0

            moving_to_tp = (is_long and cur > ep) or (not is_long and cur < ep)

            sent = milestones.get(tid, {})

            for pct, tag in [(50, "50"), (80, "80")]:
                # TP milestone
                tp_key = f"TP{pct}"
                if moving_to_tp and tp_pct >= pct and not sent.get(tp_key):
                    try:
                        send_trade_status_email(entry, cur, tp_key)
                        sent[tp_key] = True
                        changed = True
                        log.info(f"Status email sent: {pair} {tp_key}")
                    except Exception as e:
                        log.warning(f"Status email {tp_key} failed: {e}")

                # SL milestone
                sl_key = f"SL{pct}"
                if not moving_to_tp and sl_pct >= pct and not sent.get(sl_key):
                    try:
                        send_trade_status_email(entry, cur, sl_key)
                        sent[sl_key] = True
                        changed = True
                        log.info(f"Status email sent: {pair} {sl_key}")
                    except Exception as e:
                        log.warning(f"Status email {sl_key} failed: {e}")

            milestones[tid] = sent

        if changed:
            _save_milestones(milestones)

    except Exception as e:
        log.warning(f"_check_trade_milestones failed: {e}")


def _poll_closed_trades() -> None:
    """Compare journalled open trades against OANDA; record outcomes for any that closed."""
    try:
        from tools.reporting.trade_journal import (
            get_open, get_losses, patch_outcome, attach_loss_analysis,
        )
        from tools.reporting.loss_analyzer import analyze_loss
        from tools.reporting.email_report import send_loss_alert, send_trade_win_email

        open_entries = get_open()
        if not open_entries:
            return

        from tools.oanda.execute_trade import _build_client
        from oandapyV20.endpoints import trades as oanda_trades

        client, account_id = _build_client()
        req = oanda_trades.OpenTrades(accountID=account_id)
        client.request(req)
        oanda_open = req.response.get("trades", [])
        open_ids   = {t["id"] for t in oanda_open}

        # Check progress milestones for still-open trades
        still_open = [e for e in open_entries if str(e.get("trade_id", "")) in open_ids]
        _check_trade_milestones(still_open, oanda_open)

        for entry in open_entries:
            tid = str(entry.get("trade_id", ""))
            if not tid or tid in open_ids:
                continue

            # Trade is no longer open on OANDA — fetch its details
            try:
                req2 = oanda_trades.TradeDetails(accountID=account_id, tradeID=tid)
                client.request(req2)
                t = req2.response.get("trade", {})

                pnl        = float(t.get("realizedPL", 0))
                exit_price = float(t.get("averageClosePrice") or t.get("price") or 0)
                close_time = t.get("closeTime", datetime.now(timezone.utc).isoformat())
                outcome    = "win" if pnl >= 0 else "loss"

                updated = patch_outcome(tid, outcome, exit_price, close_time, pnl)
                if updated and outcome == "loss":
                    recent_losses = get_losses()
                    analysis = analyze_loss(updated, recent_losses)
                    attach_loss_analysis(tid, analysis)
                    try:
                        send_loss_alert(updated, analysis)
                    except Exception as mail_err:
                        log.warning(f"Loss alert email failed: {mail_err}")
                    log.warning(
                        f"Loss recorded: {entry.get('pair')} ${pnl:+.2f} "
                        f"severity={analysis.get('severity')}"
                    )
                elif updated and outcome == "win":
                    try:
                        send_trade_win_email(updated)
                    except Exception as mail_err:
                        log.warning(f"Win email failed: {mail_err}")
                    log.info(f"Win recorded: {entry.get('pair')} ${pnl:+.2f}")
                else:
                    log.info(f"Win recorded: {entry.get('pair')} ${pnl:+.2f}")

            except Exception as e:
                log.warning(f"Could not fetch closed trade {tid}: {e}")

    except Exception as e:
        log.warning(f"_poll_closed_trades failed: {e}")


# ── Scheduled email reports ───────────────────────────────────────────────────

def _maybe_send_reports(pairs: list[str], backtest_results: list[dict] | None = None) -> None:
    """Send weekly and/or 30-day email reports when their schedule is due."""
    try:
        from tools.reporting.trade_journal import get_period
        from tools.reporting.loss_analyzer import generate_period_summary
        from tools.reporting.email_report import send_weekly_report, send_30day_report

        state = _load_report_state()
        now   = datetime.now(timezone.utc)

        if not state.get("trade_start"):
            state["trade_start"] = now.isoformat()
            _save_report_state(state)

        def _days_since(key: str) -> int:
            last = state.get(key)
            if not last:
                return 9999
            try:
                return (now - datetime.fromisoformat(last)).days
            except Exception:
                return 9999

        # Weekly report (every 7 days)
        if _days_since("last_weekly_report") >= 7:
            try:
                trades  = get_period(days=7)
                wins    = [t for t in trades if t.get("outcome") == "win"]
                losses  = [t for t in trades if t.get("outcome") == "loss"]
                summary = generate_period_summary(losses, wins)
                send_weekly_report(trades, summary)
                state["last_weekly_report"] = now.isoformat()
                _save_report_state(state)
                log.info("Weekly email report sent.")
            except Exception as e:
                log.warning(f"Weekly report failed: {e}")

        # 30-day report
        if _days_since("last_30day_report") >= 30:
            try:
                trades  = get_period(days=30)
                wins    = [t for t in trades if t.get("outcome") == "win"]
                losses  = [t for t in trades if t.get("outcome") == "loss"]
                summary = generate_period_summary(losses, wins)
                send_30day_report(trades, summary, backtest_results or [])
                state["last_30day_report"] = now.isoformat()
                _save_report_state(state)
                log.info("30-day email report sent.")
            except Exception as e:
                log.warning(f"30-day report failed: {e}")

    except Exception as e:
        log.warning(f"_maybe_send_reports failed: {e}")


# ── Pair selection ────────────────────────────────────────────────────────────

def _rank_and_select_pairs(summary: list[dict], top_n: int = 8) -> list[str]:
    """Score each pair from backtest results and return the top N."""
    scored = []
    for s in summary:
        if "error" in s or s.get("trades", 0) < 3:
            continue
        wr  = float(s.get("win_rate",    0) or 0)
        r   = float(s.get("total_r",     0) or 0)
        pf  = float(s.get("profit_factor", 1) or 1)
        # Composite: win-rate + positive R + profit factor (capped)
        score = (wr / 100) * 0.4 + max(r, 0) * 0.4 + (min(pf, 5) / 5) * 0.2
        scored.append({"pair": s["pair"], "score": round(score, 4),
                       "win_rate": wr, "total_r": r, "profit_factor": pf,
                       "trades": s.get("trades", 0)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    log.info("═══ PAIR RANKING ═══")
    for i, s in enumerate(scored):
        log.info(f"  #{i+1:>2} {s['pair']:<12} score={s['score']:.3f}  "
                 f"WR={s['win_rate']}%  R={s['total_r']:+.2f}  PF={s['profit_factor']:.2f}")

    selected = [s["pair"] for s in scored[:top_n]]
    if not selected:
        log.warning("No pairs qualified — falling back to DEFAULT_PAIRS")
        return list(DEFAULT_PAIRS)
    log.info(f"Selected for live trading: {selected}")
    return selected


def _save_selected_pairs(pairs: list[str], ranking: list[dict]) -> None:
    SELECTED_PAIRS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SELECTED_PAIRS_PATH.write_text(json.dumps({
        "selected_at": datetime.now(timezone.utc).isoformat(),
        "pairs": pairs,
        "ranking": ranking,
    }, indent=2))


def _load_selected_pairs() -> list[str]:
    if SELECTED_PAIRS_PATH.exists():
        try:
            data  = json.loads(SELECTED_PAIRS_PATH.read_text())
            pairs = data.get("pairs", [])
            if pairs:
                log.info(f"Auto-selected pairs loaded: {pairs}")
                return pairs
        except Exception:
            pass
    log.info("No auto-selected pairs yet — using DEFAULT_PAIRS")
    return list(DEFAULT_PAIRS)


# ── Weekend: backtests ────────────────────────────────────────────────────────

def run_weekend_backtests(_ignored_pairs: list[str]) -> list[str]:
    """
    Test the full PAIR_UNIVERSE, rank by performance, and return the
    top-performing pairs for the coming week's live trading.
    """
    from tools.backtest.simulate_signals import run_backtest
    from tools.utils.file_io import get_backtest_path, write_json

    pairs     = PAIR_UNIVERSE
    to_date   = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    from_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    completed: list[str]  = []
    summary:   list[dict] = []

    log.info(f"═══ WEEKEND BACKTEST: {len(pairs)} pairs  ({from_date} → {to_date}) ═══")
    write_status("backtest",
                 f"Testing {len(pairs)} pairs to find top performers  {from_date} → {to_date}",
                 pairs=pairs, completed=completed, summary=summary)

    for pair in pairs:
        if _stop_event.is_set():
            break
        write_status("backtest", f"Testing {pair} ({len(completed)+1}/{len(pairs)})…",
                     pairs=pairs, completed=completed, summary=summary)
        try:
            result = run_backtest(pair, from_date, to_date)
            run_id = f"auto_{pair}_{datetime.now(timezone.utc).strftime('%Y%m%d')}"
            result["run_id"] = run_id
            result["status"] = "complete"
            write_json(get_backtest_path(run_id), result)

            stats = result.get("stats", {})
            completed.append(pair)
            entry = {
                "pair":          pair,
                "trades":        stats.get("total_trades", 0),
                "win_rate":      stats.get("win_rate_pct", 0),
                "total_r":       stats.get("total_r", 0),
                "profit_factor": stats.get("profit_factor", 0),
                "run_id":        run_id,
            }
            summary.append(entry)
            log.info(
                f"  ✓ {pair}: {entry['trades']} trades  "
                f"WR={entry['win_rate']}%  R={entry['total_r']:+.2f}"
            )
        except Exception as e:
            log.error(f"  ✗ {pair} failed: {e}")
            summary.append({"pair": pair, "error": str(e)})

    # Auto-select the top-performing pairs for the coming week
    selected = _rank_and_select_pairs(summary, top_n=8)
    _save_selected_pairs(selected, summary)

    write_status(
        "backtest_done",
        f"Backtests done — {len(completed)}/{len(pairs)} pairs tested. "
        f"Top picks: {', '.join(selected[:4])}… Waiting for Monday.",
        pairs=pairs, completed=completed, summary=summary,
        selected_pairs=selected,
    )
    log.info(f"Weekend backtests complete. Auto-selected: {selected}")

    # Send weekly / 30-day report if due
    _maybe_send_reports(selected, backtest_results=summary)

    return selected


# ── Weekday: signal monitoring ────────────────────────────────────────────────

_stop_event = threading.Event()


def _scan_once(pairs: list[str]) -> None:
    """Run one full scan cycle across all pairs and poll for closed trades."""
    from tools.oanda.fetch_candles import fetch_all_timeframes
    from tools.analysis.run_analysis import run_full_analysis
    from tools.confluence.score_confluence import run_confluence_for_pair
    from tools.trade_plan.build_trade_plan import build_trade_plan

    for pair in pairs:
        if _stop_event.is_set():
            return
        try:
            log.info(f"Scanning {pair}…")
            fetch_all_timeframes(pair)
            run_full_analysis(pair)
            run_confluence_for_pair(pair)
            build_trade_plan(pair)
        except Exception as e:
            log.warning(f"{pair}: {e}")

    # Check if any open journal trades have since closed on OANDA
    _poll_closed_trades()
    # Fire session-close emails if we just passed a session boundary
    _check_session_close()


def run_weekday_trading(pairs: list[str], interval: int) -> None:
    log.info(f"═══ WEEKDAY TRADING: monitoring {pairs} every {interval}s ═══")
    write_status("trading",
                 f"Auto-selected {len(pairs)} pairs (by backtest performance) · scanning every {interval}s",
                 pairs=pairs)

    while not _stop_event.is_set():
        cycle_start = datetime.now(timezone.utc)
        _scan_once(pairs)
        _maybe_send_reports(pairs)
        write_status(
            "trading",
            f"Last scan: {cycle_start.strftime('%a %H:%M UTC')} · next in {interval}s",
            pairs=pairs,
        )
        # Sleep in 1-second ticks so stop_event is responsive
        for _ in range(interval):
            if _stop_event.is_set():
                return
            time.sleep(1)


# ── Main orchestrator ─────────────────────────────────────────────────────────

def run(pairs: list[str], interval: int) -> None:
    global _stop_event
    current_mode:    str | None              = None
    trading_thread:  threading.Thread | None = None
    active_pairs:    list[str]               = _load_selected_pairs() or pairs

    log.info(f"NEXUS Scheduler started | initial_pairs={active_pairs} | interval={interval}s")

    while True:
        weekend  = is_weekend()
        new_mode = "backtest" if weekend else "trading"

        if new_mode != current_mode:
            # Stop any running trading thread
            if trading_thread and trading_thread.is_alive():
                log.info("Stopping trading loop for mode switch…")
                _stop_event.set()
                trading_thread.join(timeout=60)
            _stop_event = threading.Event()
            current_mode = new_mode

            if weekend:
                # Backtest full universe and auto-select top pairs for next week
                active_pairs = run_weekend_backtests(pairs)
            else:
                # Use last auto-selected pairs (or fall back to CLI pairs)
                active_pairs = _load_selected_pairs() or pairs
                log.info(f"Starting weekday trading with: {active_pairs}")
                trading_thread = threading.Thread(
                    target=run_weekday_trading,
                    args=(active_pairs, interval),
                    daemon=True,
                )
                trading_thread.start()

        # Re-check mode every 30 minutes
        time.sleep(1800)


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NEXUS weekly trading cycle")
    parser.add_argument("--pairs",    nargs="+", default=DEFAULT_PAIRS)
    parser.add_argument("--interval", type=int,  default=DEFAULT_INTERVAL,
                        help="Weekday scan interval in seconds (default 300)")
    args = parser.parse_args()

    try:
        run(args.pairs, args.interval)
    except KeyboardInterrupt:
        log.info("Scheduler stopped.")
        write_status("idle", "Scheduler stopped manually.")
