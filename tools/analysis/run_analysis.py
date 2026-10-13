"""
Orchestrate the full structural analysis pipeline for a currency pair.

Sequence per timeframe:
  1. Load candles from .tmp/candles/
  2. detect_swings()
  3. label_structure()
  4. detect_bos_choch()
  5. detect_trend()
  6. detect_channels()

Writes result to .tmp/analysis/{pair}_analysis.json

Usage (CLI):
    python -m tools.analysis.run_analysis --pair EUR_USD
"""

import argparse
from datetime import datetime, timezone

from tools.analysis.detect_swings   import detect_swings
from tools.analysis.label_structure import label_structure
from tools.analysis.detect_bos_choch import detect_bos_choch
from tools.analysis.detect_trend    import detect_trend
from tools.analysis.detect_channels import detect_channels
from tools.utils.file_io import (
    get_candle_path, get_analysis_path,
    read_json, write_json, file_exists,
)
from tools.utils.logger import get_logger

log = get_logger(__name__)

ALL_TIMEFRAMES = ["M1", "M5", "H1", "H4"]


def run_full_analysis(
    pair: str,
    timeframes: list[str] | None = None,
    lookback: int = 5,
) -> dict:
    """
    Run the full analysis pipeline on all timeframes for a pair.

    Args:
        pair:       e.g. "EUR_USD"
        timeframes: List of granularities to analyze. Defaults to all 4.
        lookback:   Swing detection lookback window (bars each side).

    Returns:
        Full analysis dict, also written to .tmp/analysis/{pair}_analysis.json
    """
    if timeframes is None:
        timeframes = ALL_TIMEFRAMES

    analysis = {
        "pair": pair,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "timeframes": {},
    }

    for tf in timeframes:
        candle_path = get_candle_path(pair, tf)
        if not file_exists(candle_path):
            log.warning(f"No candle file found for {pair} {tf} — skipping. Run fetch_candles first.")
            continue

        candles = read_json(candle_path)

        if len(candles) < 20:
            log.warning(f"Only {len(candles)} candles for {pair} {tf} — skipping (insufficient data).")
            continue

        log.info(f"Analysing {pair} {tf} ({len(candles)} candles)...")

        swings    = detect_swings(candles, lookback=lookback)
        structure = label_structure(swings["highs"], swings["lows"])
        bos_choch = detect_bos_choch(candles, structure)
        trend     = detect_trend(structure)
        channel   = detect_channels(swings["highs"], swings["lows"])

        analysis["timeframes"][tf] = {
            "candle_count": len(candles),
            "trend": trend,
            "swing_highs": swings["highs"],
            "swing_lows": swings["lows"],
            "structure": structure,
            "bos_events": bos_choch["bos"],
            "choch_events": bos_choch["choch"],
            "channel": channel,
        }

        log.info(
            f"{pair} {tf} → trend={trend}, "
            f"swings={len(swings['highs'])}H/{len(swings['lows'])}L, "
            f"BOS={len(bos_choch['bos'])}, CHoCH={len(bos_choch['choch'])}"
        )

    if not analysis["timeframes"]:
        log.error(f"No timeframes could be analysed for {pair}. Fetch candles first.")
        return analysis

    out_path = get_analysis_path(pair)
    write_json(out_path, analysis)
    log.info(f"Analysis written → {out_path}")

    return analysis


def _print_summary(analysis: dict) -> None:
    print(f"\n{'='*50}")
    print(f"Analysis: {analysis['pair']}  ({analysis['generated_at']})")
    print(f"{'='*50}")
    for tf, data in analysis["timeframes"].items():
        print(
            f"  {tf:4s} | trend={data['trend']:8s} | "
            f"swings={len(data['swing_highs'])}H/{len(data['swing_lows'])}L | "
            f"BOS={len(data['bos_events'])} CHoCH={len(data['choch_events'])}"
        )
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run full structural analysis on a pair")
    parser.add_argument("--pair", required=True, help="e.g. EUR_USD")
    parser.add_argument("--lookback", type=int, default=5)
    args = parser.parse_args()

    result = run_full_analysis(args.pair, lookback=args.lookback)
    _print_summary(result)
