"""
Simulate signals and trade outcomes on historical data.

For each replay window:
  1. Run the full analysis pipeline (detect_swings → label_structure →
     detect_bos_choch → detect_trend → score_confluence)
  2. If confluence score >= 3, build a trade plan
  3. Scan forward candles to determine if SL or TP1 is hit first
  4. Record the outcome (win/loss/open) with P&L in R multiples

Usage (CLI):
    python -m tools.backtest.simulate_signals --pair EUR_USD \
        --from-date 2025-01-01 --to-date 2025-06-30
"""

import argparse
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from tools.analysis.run_analysis import run_full_analysis
from tools.analysis.detect_swings import detect_swings
from tools.analysis.label_structure import label_structure
from tools.analysis.detect_bos_choch import detect_bos_choch
from tools.analysis.detect_trend import detect_trend
from tools.analysis.detect_channels import detect_channels
from tools.confluence.score_confluence import score_confluence
from tools.trade_plan.calculate_entry import calculate_entry
from tools.trade_plan.calculate_sl_tp import calculate_sl_tp
from tools.trade_plan.calculate_lot_size import calculate_lot_size
from tools.backtest.replay_candles import build_windows
from tools.oanda.fetch_candles import fetch_candles
from tools.utils.file_io import get_backtest_path, write_json
from tools.utils.logger import get_logger

load_dotenv()
log = get_logger(__name__)

ALL_TIMEFRAMES = ["M1", "M5", "H1", "H4"]
# Step every N H1 bars to keep backtest fast (1 = every bar, 4 = every 4h)
STEP = 4


def _analyse_window(candles_by_tf: dict[str, list[dict]]) -> dict | None:
    """
    Run analysis on a single window's candles.
    Returns timeframe analysis dict keyed by TF, or None if insufficient data.
    """
    tf_analysis = {}
    for tf, candles in candles_by_tf.items():
        if len(candles) < 20:
            continue
        swings = detect_swings(candles, lookback=5)
        structure = label_structure(swings["highs"], swings["lows"])
        bos_choch = detect_bos_choch(candles, structure)
        trend = detect_trend(structure)
        channel = detect_channels(swings["highs"], swings["lows"])
        tf_analysis[tf] = {
            "trend": trend,
            "swing_highs": swings["highs"],
            "swing_lows": swings["lows"],
            "structure": structure,
            "bos_events": bos_choch["bos"],
            "choch_events": bos_choch["choch"],
            "channel": channel,
            "candle_count": len(candles),
        }
    return tf_analysis if tf_analysis else None


def _simulate_trade_outcome(
    entry: float,
    stop_loss: float,
    take_profit: float,
    direction: str,
    future_candles: list[dict],
) -> dict:
    """
    Scan future candles to determine if SL or TP is hit first.

    Returns outcome dict with result, exit_price, exit_time, r_multiple.
    """
    for candle in future_candles:
        if direction == "bearish":
            if candle["high"] >= stop_loss:
                return {
                    "result": "loss",
                    "exit_price": stop_loss,
                    "exit_time": candle["time"],
                    "r_multiple": -1.0,
                }
            if candle["low"] <= take_profit:
                sl_dist = abs(stop_loss - entry)
                tp_dist = abs(entry - take_profit)
                r = round(tp_dist / sl_dist, 2) if sl_dist > 0 else 0
                return {
                    "result": "win",
                    "exit_price": take_profit,
                    "exit_time": candle["time"],
                    "r_multiple": r,
                }
        else:  # bullish
            if candle["low"] <= stop_loss:
                return {
                    "result": "loss",
                    "exit_price": stop_loss,
                    "exit_time": candle["time"],
                    "r_multiple": -1.0,
                }
            if candle["high"] >= take_profit:
                sl_dist = abs(entry - stop_loss)
                tp_dist = abs(take_profit - entry)
                r = round(tp_dist / sl_dist, 2) if sl_dist > 0 else 0
                return {
                    "result": "win",
                    "exit_price": take_profit,
                    "exit_time": candle["time"],
                    "r_multiple": r,
                }

    return {"result": "open", "exit_price": None, "exit_time": None, "r_multiple": 0.0}


def run_backtest(
    pair: str,
    from_date: str,
    to_date: str,
    risk_percent: float = 1.0,
    step: int = STEP,
) -> dict:
    """
    Run a full backtest for a pair over a date range.

    Args:
        pair:         e.g. "EUR_USD"
        from_date:    ISO8601 or YYYY-MM-DD start date
        to_date:      ISO8601 or YYYY-MM-DD end date
        risk_percent: Risk per trade as % of account
        step:         H1 bar step size (larger = faster backtest)

    Returns:
        Results dict with trades list and summary stats.
    """
    # Normalise date strings
    if len(from_date) == 10:
        from_date += "T00:00:00Z"
    if len(to_date) == 10:
        to_date += "T23:59:59Z"

    log.info(f"Backtesting {pair} from {from_date} to {to_date}...")

    # ── Fetch historical data ─────────────────────────────────────────────────
    # M1/M5 exceed OANDA's per-request candle limit on ranges > ~1 week,
    # so backtests use H1 + H4 only. Min confluence score is adjusted to 2/2.
    candles_by_tf = {}
    for tf in ["H1", "H4"]:
        try:
            candles_by_tf[tf] = fetch_candles(
                pair, tf,
                from_time=from_date,
                to_time=to_date,
            )
        except Exception as e:
            log.warning(f"Could not fetch {tf} candles: {e}")

    if not candles_by_tf.get("H1"):
        return {"error": "No H1 candle data available for the given date range."}

    # With only 2 timeframes, require both to agree
    min_conf = 2

    # ── Build replay windows ──────────────────────────────────────────────────
    windows = build_windows(candles_by_tf, min_candles=50, step=step)
    if not windows:
        return {"error": "Not enough candles to backtest."}

    h1_all = candles_by_tf["H1"]
    # min_conf set above after checking available timeframes
    min_rr = float(os.getenv("MIN_RISK_REWARD", 2.0))

    trades = []
    last_signal_bar = -999  # prevent back-to-back signals on the same structure

    for window in windows:
        idx = window["h1_bar_index"]

        # Skip if too close to the last signal (24 H1 bars = ~1 trading day)
        if idx - last_signal_bar < 24:
            continue

        tf_analysis = _analyse_window(window["candles"])
        if not tf_analysis:
            continue

        confluence = score_confluence(tf_analysis, min_score=min_conf)
        if not confluence["signal_valid"]:
            continue

        # Build trade plan inline
        direction = confluence["direction"]
        ref_tf = "H4" if tf_analysis.get("H4") and confluence["votes"].get("H4") == direction \
                 else "H1"
        tf_data = tf_analysis.get(ref_tf) or tf_analysis.get("H1")
        if not tf_data:
            continue

        candles_ref = window["candles"].get(ref_tf, [])
        if not candles_ref:
            continue

        try:
            entry = calculate_entry(candles_ref, direction)
            sl_tp = calculate_sl_tp(
                entry, direction,
                tf_data["swing_highs"], tf_data["swing_lows"],
                pair=pair,
            )
        except (ValueError, Exception) as e:
            log.debug(f"Skipping window at bar {idx}: {e}")
            continue

        if sl_tp["risk_reward"] < min_rr:
            continue

        # Scan forward H1 candles (500 bars ≈ 3 weeks of H1 data)
        future = h1_all[idx + 1: idx + 500]
        outcome = _simulate_trade_outcome(
            entry=entry,
            stop_loss=sl_tp["stop_loss"],
            take_profit=sl_tp["take_profit_1"],
            direction=direction,
            future_candles=future,
        )

        trade = {
            "pair": pair,
            "direction": direction,
            "entry_price": entry,
            "stop_loss": sl_tp["stop_loss"],
            "take_profit_1": sl_tp["take_profit_1"],
            "sl_pips": sl_tp["sl_pips"],
            "risk_reward": sl_tp["risk_reward"],
            "confluence_score": confluence["score"],
            "signal_bar": idx,
            "signal_time": window["cutoff_time"],
            "votes": confluence["votes"],
            **outcome,
        }
        trades.append(trade)
        last_signal_bar = idx
        log.info(
            f"Trade {len(trades)}: {direction} at {entry} → "
            f"{outcome['result']} (R={outcome['r_multiple']})"
        )

    from tools.backtest.calculate_stats import calculate_stats
    stats = calculate_stats(trades)

    result = {
        "pair": pair,
        "from_date": from_date,
        "to_date": to_date,
        "total_h1_bars": len(h1_all),
        "windows_checked": len(windows),
        "trades": trades,
        "stats": stats,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    log.info(
        f"Backtest complete: {stats['total_trades']} trades | "
        f"Win rate: {stats['win_rate_pct']}% | "
        f"Avg R: {stats['avg_r_multiple']}"
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair", required=True)
    parser.add_argument("--from-date", required=True)
    parser.add_argument("--to-date", required=True)
    parser.add_argument("--risk", type=float, default=1.0)
    parser.add_argument("--step", type=int, default=STEP)
    args = parser.parse_args()

    results = run_backtest(
        args.pair, args.from_date, args.to_date,
        risk_percent=args.risk, step=args.step,
    )

    stats = results.get("stats", {})
    trades = results.get("trades", [])
    print(f"\n{'='*55}")
    print(f"  BACKTEST: {args.pair}  {args.from_date[:10]} → {args.to_date[:10]}")
    print(f"{'='*55}")
    print(f"  Total trades   : {stats.get('total_trades', 0)}")
    print(f"  Win rate       : {stats.get('win_rate_pct', 0)}%")
    print(f"  Avg R multiple : {stats.get('avg_r_multiple', 0)}")
    print(f"  Max drawdown   : {stats.get('max_drawdown_r', 0)}R")
    print(f"  Total R gained : {stats.get('total_r', 0)}")
    print(f"  Profit factor  : {stats.get('profit_factor', 0)}")
    print(f"{'='*55}\n")

    if trades:
        print(f"  {'Time':<22} {'Dir':<8} {'Entry':<10} {'Result':<8} {'R':>5}")
        print(f"  {'-'*60}")
        for t in trades:
            print(
                f"  {t['signal_time'][:19]:<22} "
                f"{t['direction']:<8} "
                f"{t['entry_price']:<10} "
                f"{t['result']:<8} "
                f"{t['r_multiple']:>5}"
            )
