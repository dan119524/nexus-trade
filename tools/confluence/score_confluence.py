"""
Cross-timeframe confluence scoring.

Each timeframe casts a vote: "bullish", "bearish", or "neutral".
Vote is determined by combining:
  1. Trend direction (detect_trend output)
  2. Most recent BOS/CHoCH direction (if any)

Scoring:
  score = number of timeframes matching the majority direction
  signal_valid = True only if score >= MIN_CONFLUENCE_SCORE (default 3)

Usage (CLI):
    python -m tools.confluence.score_confluence --pair EUR_USD
"""

import argparse
import os
from collections import Counter

from dotenv import load_dotenv

from tools.utils.file_io import get_analysis_path, get_signal_path, read_json, write_json, file_exists
from tools.utils.logger import get_logger
from datetime import datetime, timezone

load_dotenv()
log = get_logger(__name__)

ALL_TIMEFRAMES = ["M1", "M5", "H1", "H4"]
# Higher timeframes carry more weight in the vote
TIMEFRAME_WEIGHT = {"M1": 1, "M5": 1, "H1": 2, "H4": 3}


def _cast_vote(tf_data: dict) -> str:
    """
    Cast a directional vote for a single timeframe.

    Combines trend + most recent BOS/CHoCH:
    - If both agree → strong vote in that direction
    - If only trend is available → vote on trend
    - If most recent event contradicts trend → vote "neutral"
    """
    trend = tf_data.get("trend", "ranging")

    # Get most recent BOS/CHoCH direction (if any)
    all_events = tf_data.get("bos_events", []) + tf_data.get("choch_events", [])
    recent_event_dir = None
    if all_events:
        # Events are in detection order; last one is most recent break
        latest = max(all_events, key=lambda e: e["broken_at_bar"])
        recent_event_dir = latest["direction"]

    if trend == "bullish":
        if recent_event_dir is None or recent_event_dir == "bullish":
            return "bullish"
        else:
            return "neutral"  # trend says bullish but last break was bearish
    elif trend == "bearish":
        if recent_event_dir is None or recent_event_dir == "bearish":
            return "bearish"
        else:
            return "neutral"
    else:
        # Ranging trend — follow the most recent event if available
        if recent_event_dir == "bullish":
            return "bullish"
        elif recent_event_dir == "bearish":
            return "bearish"
        return "neutral"


def score_confluence(
    analysis_by_timeframe: dict[str, dict],
    min_score: int | None = None,
) -> dict:
    """
    Score confluence across timeframes.

    Args:
        analysis_by_timeframe: Dict keyed by granularity ("M1", "M5", "H1", "H4"),
                               each value is the timeframe sub-dict from run_analysis().
        min_score:             Minimum score to mark signal as valid. Defaults to
                               MIN_CONFLUENCE_SCORE from .env (or 3).

    Returns:
        Confluence result dict.
    """
    if min_score is None:
        min_score = int(os.getenv("MIN_CONFLUENCE_SCORE", 3))

    votes: dict[str, str] = {}
    for tf, tf_data in analysis_by_timeframe.items():
        votes[tf] = _cast_vote(tf_data)

    # Weighted tally
    weighted: dict[str, float] = {"bullish": 0, "bearish": 0, "neutral": 0}
    for tf, vote in votes.items():
        weighted[vote] += TIMEFRAME_WEIGHT.get(tf, 1)

    # Majority direction (excluding neutral)
    directional = {k: v for k, v in weighted.items() if k != "neutral"}
    majority_dir = max(directional, key=directional.get)

    # Raw count (unweighted) of timeframes agreeing with majority
    raw_score = sum(1 for v in votes.values() if v == majority_dir)
    weighted_score = weighted[majority_dir]
    signal_valid = raw_score >= min_score

    dissenting = [tf for tf, v in votes.items() if v != majority_dir and v != "neutral"]
    neutral_tfs = [tf for tf, v in votes.items() if v == "neutral"]

    result = {
        "score": raw_score,
        "weighted_score": round(weighted_score, 1),
        "max_score": len(votes),
        "direction": majority_dir,
        "votes": votes,
        "dissenting_timeframes": dissenting,
        "neutral_timeframes": neutral_tfs,
        "signal_valid": signal_valid,
        "min_score_required": min_score,
    }

    log.info(
        f"Confluence: {majority_dir.upper()} {raw_score}/{len(votes)} "
        f"(weighted={weighted_score:.1f}) | valid={signal_valid}"
    )
    for tf, vote in votes.items():
        log.info(f"  {tf:4s} → {vote}")

    return result


def run_confluence_for_pair(pair: str) -> dict | None:
    """
    Load analysis from .tmp/, score confluence, write signal to .tmp/signals/.

    Returns the signal dict if valid (score >= min), else None.
    """
    analysis_path = get_analysis_path(pair)
    if not file_exists(analysis_path):
        log.error(f"No analysis file for {pair}. Run tools.analysis.run_analysis first.")
        return None

    analysis = read_json(analysis_path)
    tf_data = analysis.get("timeframes", {})

    if not tf_data:
        log.error(f"Analysis file for {pair} contains no timeframe data.")
        return None

    confluence = score_confluence(tf_data)
    confluence["pair"] = pair
    confluence["analysed_at"] = analysis.get("generated_at")
    confluence["scored_at"] = datetime.now(timezone.utc).isoformat()

    if not confluence["signal_valid"]:
        log.info(
            f"No valid signal for {pair}. "
            f"Score {confluence['score']}/{confluence['max_score']} "
            f"— need {confluence['min_score_required']}."
        )
        return None

    # Write signal stub (trade plan will be attached in Workflow 04)
    signal = {
        "id": f"{pair}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}",
        "pair": pair,
        "status": "pending_trade_plan",
        "confluence": confluence,
        "trade_plan": None,
        "summary": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    signal_path = get_signal_path(pair)
    write_json(signal_path, signal)
    log.info(f"Signal written → {signal_path}")

    return signal


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Score confluence for a pair")
    parser.add_argument("--pair", required=True, help="e.g. EUR_USD")
    args = parser.parse_args()

    signal = run_confluence_for_pair(args.pair)
    if signal:
        import json
        c = signal["confluence"]
        print(f"\n✓ Valid signal: {c['direction'].upper()} on {args.pair}")
        print(f"  Score: {c['score']}/{c['max_score']}  Votes: {c['votes']}")
    else:
        print(f"\n✗ No valid signal for {args.pair}")
