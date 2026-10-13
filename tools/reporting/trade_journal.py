"""
Trade journal — records every executed trade and its outcome.

Entries are appended to .tmp/journal/trades.json.
When OANDA closes a trade (SL or TP hit), the outcome is patched in.
"""

import os
from datetime import datetime, timezone
from pathlib import Path

from tools.utils.logger import get_logger

log = get_logger(__name__)

JOURNAL_PATH = Path(__file__).resolve().parents[2] / ".tmp" / "journal" / "trades.json"


def _load() -> list[dict]:
    JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not JOURNAL_PATH.exists():
        return []
    import json
    try:
        return json.loads(JOURNAL_PATH.read_text())
    except Exception:
        return []


def _save(entries: list[dict]) -> None:
    import json
    JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    JOURNAL_PATH.write_text(json.dumps(entries, indent=2))


def append_trade(trade: dict) -> None:
    """Record a newly executed trade."""
    entries = _load()
    # Avoid duplicates by trade_id
    trade_id = trade.get("trade_id") or trade.get("id")
    if any(e.get("trade_id") == trade_id for e in entries):
        return
    entry = {
        "trade_id":       trade_id,
        "pair":           trade.get("pair"),
        "direction":      trade.get("direction"),
        "entry_price":    trade.get("entry_price"),
        "stop_loss":      trade.get("stop_loss"),
        "take_profit":    trade.get("take_profit"),
        "lot_size":       trade.get("lot_size"),
        "units":          trade.get("units"),
        "risk_amount":    trade.get("risk_amount"),
        "confluence_score": trade.get("confluence_score"),
        "risk_reward":    trade.get("risk_reward"),
        "executed_at":    trade.get("executed_at") or datetime.now(timezone.utc).isoformat(),
        "outcome":        None,   # "win" | "loss" | "open"
        "exit_price":     None,
        "exit_time":      None,
        "pnl_usd":        None,
        "r_multiple":     None,
        "loss_analysis":  None,
    }
    entries.append(entry)
    _save(entries)
    log.info(f"Journal: recorded trade {trade_id} ({trade.get('pair')})")


def patch_outcome(trade_id: str, outcome: str, exit_price: float,
                  exit_time: str, pnl_usd: float) -> dict | None:
    """Update an open journal entry with its outcome once the trade closes."""
    entries = _load()
    for e in entries:
        if str(e.get("trade_id")) == str(trade_id):
            entry_px = e.get("entry_price") or 0
            sl       = e.get("stop_loss") or 0
            sl_dist  = abs(entry_px - sl) if entry_px and sl else 1
            exit_dist = abs(exit_price - entry_px) if entry_px else 0
            r = round(exit_dist / sl_dist, 2) if sl_dist else 0
            if outcome == "loss":
                r = -r

            e["outcome"]    = outcome
            e["exit_price"] = exit_price
            e["exit_time"]  = exit_time
            e["pnl_usd"]    = round(pnl_usd, 2)
            e["r_multiple"] = r
            _save(entries)
            log.info(f"Journal: patched {trade_id} → {outcome} ${pnl_usd:+.2f}")
            return e
    return None


def attach_loss_analysis(trade_id: str, analysis: dict) -> None:
    """Attach Claude AI loss analysis to a journal entry."""
    entries = _load()
    for e in entries:
        if str(e.get("trade_id")) == str(trade_id):
            e["loss_analysis"] = analysis
            _save(entries)
            return


def get_all() -> list[dict]:
    return _load()


def get_open() -> list[dict]:
    return [e for e in _load() if e.get("outcome") is None]


def get_closed() -> list[dict]:
    return [e for e in _load() if e.get("outcome") is not None]


def get_losses() -> list[dict]:
    return [e for e in _load() if e.get("outcome") == "loss"]


def get_period(days: int = 30) -> list[dict]:
    """Return entries from the last N days."""
    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    return [e for e in _load() if (e.get("executed_at") or "") >= cutoff]
