"""
FastAPI server — bridges the Python analysis pipeline to React Native.

All endpoints are read-only against .tmp/ files, keeping the server
stateless and fast. The one exception is POST /backtest which enqueues
a background job.

Run:
    uvicorn tools.api.server:app --reload --port 8000

From the project root.
"""

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# In-memory push token store (persists for server lifetime)
# In production, persist these to a database or file
_push_tokens: set[str] = set()

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from tools.utils.file_io import (
    file_exists,
    get_analysis_path,
    get_backtest_path,
    get_candle_path,
    get_signal_path,
    list_candle_files,
    list_signals,
    read_json,
    write_json,
)
from tools.utils.logger import get_logger

load_dotenv()
log = get_logger(__name__)

app = FastAPI(title="NEXUS Trade API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_TMP = Path(__file__).resolve().parents[2] / ".tmp"
_WEB = Path(__file__).resolve().parents[2] / "web"

# Serve the web dashboard at /app
if _WEB.exists():
    app.mount("/app", StaticFiles(directory=str(_WEB), html=True), name="web")


# ── Scheduler status ─────────────────────────────────────────────────────────

_SCHEDULER_STATUS = Path(__file__).resolve().parents[2] / ".tmp" / "scheduler_status.json"

@app.get("/scheduler/status")
def get_scheduler_status() -> dict:
    """Return the current weekly-cycle scheduler status."""
    if not _SCHEDULER_STATUS.exists():
        now = datetime.now(timezone.utc)
        wd  = now.weekday()
        is_wknd = wd >= 5
        if is_wknd:
            days = 7 - wd
            nxt_label = "Monday"
        else:
            days = 5 - wd
            nxt_label = "Saturday"
        from datetime import timedelta
        nxt = (now + timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
        return {
            "mode": "not_started",
            "detail": "Scheduler not running. Start with: python -m tools.scheduler.weekly_cycle",
            "updated_at": now.isoformat(),
            "next_switch": nxt.isoformat(),
            "next_switch_label": f"{nxt_label} {nxt.strftime('%d %b')}",
            "is_weekend": is_wknd,
        }
    try:
        data = read_json(str(_SCHEDULER_STATUS))
        data["is_weekend"] = datetime.now(timezone.utc).weekday() >= 5
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/")
def health() -> dict:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


# ── Signals ───────────────────────────────────────────────────────────────────

@app.get("/signals")
def get_all_signals() -> list[dict]:
    """Return all active signals sorted by created_at descending."""
    pairs = list_signals()
    signals = []
    for pair in pairs:
        path = get_signal_path(pair)
        if file_exists(path):
            try:
                s = read_json(path)
                if s.get("status") in ("active", "ready"):
                    signals.append(s)
            except Exception as e:
                log.warning(f"Could not read signal for {pair}: {e}")

    signals.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return signals


@app.get("/signals/{pair}")
def get_signal(pair: str) -> dict:
    """Return the signal for a specific pair."""
    path = get_signal_path(pair)
    if not file_exists(path):
        raise HTTPException(status_code=404, detail=f"No signal found for {pair}")
    return read_json(path)


# ── Candles ───────────────────────────────────────────────────────────────────

@app.get("/candles/{pair}/{timeframe}")
def get_candles(pair: str, timeframe: str, limit: int = 200) -> list[dict]:
    """
    Return the most recent N candles for a pair/timeframe.
    If the cache file doesn't exist, fetches live from OANDA and caches it.
    Supports: M1 M2 M5 M10 M15 M30 H1 H4 D W M
    """
    tf = timeframe.upper()
    path = get_candle_path(pair, tf)
    if not file_exists(path):
        try:
            from tools.oanda.fetch_candles import fetch_candles, DEFAULT_COUNTS
            count = DEFAULT_COUNTS.get(tf, 500)
            fetch_candles(pair, tf, count=count)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Could not fetch {pair} {tf}: {e}")
    candles = read_json(path)
    return candles[-limit:] if limit > 0 else candles


@app.get("/candles/{pair}/{timeframe}/range")
def get_candles_range(pair: str, timeframe: str, from_time: str, to_time: str) -> list[dict]:
    """Fetch candles directly from OANDA for a specific date range (for backtest chart)."""
    try:
        from tools.oanda.fetch_candles import fetch_candles
        if len(from_time) == 10:
            from_time += "T00:00:00Z"
        if len(to_time) == 10:
            to_time += "T23:59:59Z"
        # Clamp to_time to now so OANDA never receives a future timestamp
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if to_time > now:
            to_time = now
        candles = fetch_candles(pair, timeframe.upper(), from_time=from_time, to_time=to_time)
        return candles
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not fetch candles: {e}")


# ── Analysis ──────────────────────────────────────────────────────────────────

@app.get("/analysis/{pair}")
def get_analysis(pair: str) -> dict:
    """Return the full structural analysis for a pair."""
    path = get_analysis_path(pair)
    if not file_exists(path):
        raise HTTPException(
            status_code=404,
            detail=f"No analysis for {pair}. Run run_analysis first."
        )
    return read_json(path)


@app.get("/analysis/{pair}/{timeframe}")
def get_analysis_timeframe(pair: str, timeframe: str) -> dict:
    """Return analysis for a specific timeframe only (lighter payload)."""
    path = get_analysis_path(pair)
    if not file_exists(path):
        raise HTTPException(status_code=404, detail=f"No analysis for {pair}")
    analysis = read_json(path)
    tf_data = analysis.get("timeframes", {}).get(timeframe.upper())
    if not tf_data:
        raise HTTPException(
            status_code=404,
            detail=f"No {timeframe} data in analysis for {pair}"
        )
    return {"pair": pair, "timeframe": timeframe.upper(), **tf_data}


# ── Trade Plan ────────────────────────────────────────────────────────────────

@app.get("/trade-plan/{pair}")
def get_trade_plan(pair: str) -> dict:
    """Return the trade plan for a pair (extracted from the signal)."""
    path = get_signal_path(pair)
    if not file_exists(path):
        raise HTTPException(status_code=404, detail=f"No signal for {pair}")
    signal = read_json(path)
    plan = signal.get("trade_plan")
    if not plan:
        raise HTTPException(
            status_code=404,
            detail=f"Signal for {pair} exists but has no trade plan yet."
        )
    return plan


# ── Account ───────────────────────────────────────────────────────────────────

@app.get("/account")
def get_account() -> dict:
    """Return current account balance and open trade count."""
    try:
        from tools.oanda.fetch_account import fetch_account
        return fetch_account()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not fetch account: {e}")


# ── Available pairs ───────────────────────────────────────────────────────────

@app.get("/pairs")
def get_available_pairs() -> list[str]:
    """Return all pairs that have candle data in .tmp/."""
    files = list_candle_files()
    return sorted({f["pair"] for f in files})


@app.get("/instruments")
def get_instruments() -> list[str]:
    """Return all tradeable forex instruments from OANDA."""
    try:
        from tools.oanda.fetch_instruments import fetch_instruments
        return fetch_instruments()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not fetch instruments: {e}")


# ── Push Notifications ────────────────────────────────────────────────────────

@app.post("/push/register")
def register_push_token(token: str) -> dict:
    """Register a device's Expo push token for signal notifications."""
    if not token.startswith("ExponentPushToken["):
        raise HTTPException(status_code=400, detail="Invalid Expo push token format")
    _push_tokens.add(token)
    log.info(f"Push token registered: {token[:30]}... ({len(_push_tokens)} total)")
    return {"registered": True, "total_devices": len(_push_tokens)}


@app.delete("/push/register")
def unregister_push_token(token: str) -> dict:
    """Remove a device's push token."""
    _push_tokens.discard(token)
    return {"unregistered": True, "total_devices": len(_push_tokens)}


@app.get("/push/devices")
def get_registered_devices() -> dict:
    return {"count": len(_push_tokens)}


@app.post("/push/test")
def send_test_notification() -> dict:
    """Send a test push to all registered devices."""
    if not _push_tokens:
        raise HTTPException(status_code=404, detail="No devices registered")
    from tools.oanda.stream_prices import send_push_notification
    sent = 0
    for token in _push_tokens:
        if send_push_notification(token, "NEXUS Test", "Push notifications are working ✓"):
            sent += 1
    return {"sent": sent, "total_devices": len(_push_tokens)}


# ── Backtest ──────────────────────────────────────────────────────────────────

@app.post("/backtest")
def trigger_backtest(
    pair: str,
    from_date: str,
    to_date: str,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Trigger a backtest run in the background.
    Returns a run_id immediately — poll GET /backtest/{run_id} for results.
    """
    run_id = f"{pair}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    background_tasks.add_task(_run_backtest_job, run_id, pair, from_date, to_date)
    log.info(f"Backtest queued: {run_id}")
    return {"run_id": run_id, "status": "queued", "pair": pair}


@app.get("/backtest/{run_id}")
def get_backtest_results(run_id: str) -> dict:
    """Return results for a completed backtest run."""
    path = get_backtest_path(run_id)
    if not file_exists(path):
        raise HTTPException(
            status_code=404,
            detail=f"Backtest {run_id} not found or still running."
        )
    return read_json(path)


# ── Trade Execution ───────────────────────────────────────────────────────────

@app.post("/execute-trade/{pair}")
def execute_trade_endpoint(pair: str, confirm: bool = False) -> dict:
    """
    Execute the trade plan for a pair on OANDA.
    Only works when OANDA_ENV=practice. Dry run by default.
    Pass ?confirm=true to actually place the order.
    """
    env = os.getenv("OANDA_ENV", "practice")
    if env != "practice":
        raise HTTPException(
            status_code=403,
            detail="Execution blocked: OANDA_ENV is not 'practice'. "
                   "Set OANDA_ENV=practice in .env to enable automated execution."
        )
    from tools.oanda.execute_trade import execute_trade
    result = execute_trade(pair, confirm=confirm)
    if result is None:
        raise HTTPException(status_code=400, detail="Trade execution blocked by safety gates.")
    return result


@app.get("/scheduler/selected-pairs")
def get_selected_pairs() -> dict:
    """Return the auto-selected pairs and their backtest ranking."""
    path = Path(__file__).resolve().parents[2] / ".tmp" / "selected_pairs.json"
    if not path.exists():
        return {"selected_at": None, "pairs": [], "ranking": []}
    try:
        return read_json(str(path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trades/open")
def get_open_trades(pair: str | None = None) -> list[dict]:
    """Return all currently open trades on the OANDA account."""
    try:
        from tools.oanda.execute_trade import get_open_trades
        return get_open_trades(pair=pair)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/trades/closed")
def get_closed_trades_api(count: int = 50) -> list[dict]:
    """Fetch recently closed trades from OANDA."""
    try:
        from tools.oanda.execute_trade import get_closed_trades
        return get_closed_trades(count=count)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/reports/journal")
def get_journal() -> list[dict]:
    """Return all trade journal entries (executed + journalled trades)."""
    from tools.reporting.trade_journal import get_all
    return get_all()


@app.get("/reports/equity")
def get_equity_curve() -> dict:
    """Return daily equity snapshots and drawdown metrics from the trade journal."""
    from collections import defaultdict
    from tools.reporting.trade_journal import get_all
    try:
        try:
            from tools.oanda.fetch_account import fetch_account
            account_data = fetch_account()
        except Exception:
            account_data = {}

        trades = [t for t in get_all() if t.get("outcome") and t.get("pnl_usd") is not None]
        trades.sort(key=lambda t: t.get("executed_at") or "")

        daily: dict[str, float] = defaultdict(float)
        for t in trades:
            day = (t.get("exit_time") or t.get("executed_at") or "")[:10]
            if day:
                daily[day] += float(t.get("pnl_usd") or 0)

        total_closed_pnl = sum(float(t.get("pnl_usd") or 0) for t in trades)
        current_balance = float(account_data.get("balance") or 100_000)
        start_balance = current_balance - total_closed_pnl

        snapshots, running, peak, max_dd = [], start_balance, start_balance, 0.0
        for day in sorted(daily):
            running += daily[day]
            peak = max(peak, running)
            dd = (running - peak) / peak * 100 if peak > 0 else 0.0
            max_dd = min(max_dd, dd)
            snapshots.append({"date": day, "equity": round(running, 2), "daily_pnl": round(daily[day], 2)})

        peak_equity = max((s["equity"] for s in snapshots), default=current_balance)
        current_equity = snapshots[-1]["equity"] if snapshots else current_balance
        current_dd = round((current_equity - peak_equity) / peak_equity * 100, 2) if peak_equity > 0 else 0.0

        return {
            "snapshots": snapshots,
            "current_drawdown_pct": current_dd,
            "max_drawdown_pct": round(max_dd, 2),
            "start_balance": round(start_balance, 2),
            "current_balance": round(current_balance, 2),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports/summary")
def get_report_summary(days: int = 30) -> dict:
    """Return win/loss summary and recommendations for the last N days."""
    from tools.reporting.trade_journal import get_period
    from tools.reporting.loss_analyzer import generate_period_summary
    trades  = get_period(days=days)
    wins    = [t for t in trades if t.get("outcome") == "win"]
    losses  = [t for t in trades if t.get("outcome") == "loss"]
    return generate_period_summary(losses, wins)


@app.get("/prices")
def get_prices(instruments: str) -> list[dict]:
    """
    Return current bid/ask/mid prices for a comma-separated list of instruments.
    Example: /prices?instruments=EUR_USD,GBP_USD
    """
    try:
        import os
        from oandapyV20 import API
        from oandapyV20.endpoints.pricing import PricingInfo
        from tools.utils.validators import require_practice_env
        require_practice_env(os.getenv("OANDA_ENV", "practice"))
        api_key = os.getenv("OANDA_API_KEY")
        account_id = os.getenv("OANDA_ACCOUNT_ID")
        client = API(access_token=api_key, environment="practice")
        req = PricingInfo(accountID=account_id, params={"instruments": instruments})
        client.request(req)
        result = []
        for p in req.response.get("prices", []):
            bid = float(p["bids"][0]["price"]) if p.get("bids") else None
            ask = float(p["asks"][0]["price"]) if p.get("asks") else None
            mid = round((bid + ask) / 2, 5) if bid and ask else None
            result.append({
                "instrument": p["instrument"],
                "bid": bid,
                "ask": ask,
                "mid": mid,
                "tradeable": p.get("tradeable", False),
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not fetch prices: {e}")


@app.post("/trades/{trade_id}/close")
def close_trade_endpoint(trade_id: str) -> dict:
    """Close a specific open trade by OANDA trade ID."""
    env = os.getenv("OANDA_ENV", "practice")
    if env != "practice":
        raise HTTPException(status_code=403, detail="Close only allowed on practice accounts.")
    from tools.oanda.execute_trade import close_trade
    result = close_trade(trade_id)
    if result is None:
        raise HTTPException(status_code=400, detail="Could not close trade.")
    return result


def _run_backtest_job(run_id: str, pair: str, from_date: str, to_date: str) -> None:
    """Background task — runs the backtest pipeline (Week 10 implementation)."""
    result_path = get_backtest_path(run_id)
    try:
        from tools.backtest.simulate_signals import run_backtest
        results = run_backtest(pair, from_date, to_date)
        results["run_id"] = run_id
        results["status"] = "complete"
        write_json(result_path, results)
        log.info(f"Backtest {run_id} complete")
    except Exception as e:
        log.error(f"Backtest {run_id} failed: {e}")
        write_json(result_path, {
            "run_id": run_id, "status": "failed", "error": str(e)
        })
