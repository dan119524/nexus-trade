"""
Consistent read/write helpers for all .tmp/ data files.
Every tool script uses these functions — never raw open() calls.
"""

import json
import os
from pathlib import Path

# Root of .tmp/ relative to this file's project root
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_TMP = _PROJECT_ROOT / ".tmp"


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


# ── Path helpers ──────────────────────────────────────────────────────────────

def get_candle_path(pair: str, granularity: str) -> str:
    return str(_TMP / "candles" / f"{pair}_{granularity}.json")


def get_analysis_path(pair: str) -> str:
    return str(_TMP / "analysis" / f"{pair}_analysis.json")


def get_signal_path(pair: str) -> str:
    return str(_TMP / "signals" / f"{pair}_signals.json")


def get_backtest_path(run_id: str) -> str:
    return str(_TMP / "backtest" / f"{run_id}_results.json")


# ── Read / Write ──────────────────────────────────────────────────────────────

def read_json(path: str) -> dict | list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str, data: dict | list) -> None:
    _ensure_dir(Path(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def file_exists(path: str) -> bool:
    return os.path.isfile(path)


def list_signals() -> list[str]:
    """Return all pair names that have a signal file in .tmp/signals/."""
    signals_dir = _TMP / "signals"
    if not signals_dir.exists():
        return []
    return [
        f.stem.replace("_signals", "")
        for f in signals_dir.glob("*_signals.json")
    ]


def list_candle_files() -> list[dict]:
    """Return list of {pair, granularity} dicts for all cached candle files."""
    candles_dir = _TMP / "candles"
    if not candles_dir.exists():
        return []
    results = []
    for f in candles_dir.glob("*.json"):
        parts = f.stem.rsplit("_", 1)
        if len(parts) == 2:
            results.append({"pair": parts[0], "granularity": parts[1]})
    return results
