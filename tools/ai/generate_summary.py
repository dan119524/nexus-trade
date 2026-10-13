"""
Generate a plain English trade summary using the Claude API.

Produces two things:
  1. A 3-5 sentence setup summary explaining WHY this trade is valid.
  2. A one-sentence invalidation condition explaining what would cancel the setup.

Cost control: only called when confluence score >= 3 AND RR >= 2.0.
The summary is attached to the signal object and written back to .tmp/signals/.

Usage (CLI):
    python -m tools.ai.generate_summary --pair EUR_USD
"""

import argparse
import os

import anthropic
from dotenv import load_dotenv

from tools.utils.file_io import get_signal_path, get_analysis_path, read_json, write_json, file_exists
from tools.utils.logger import get_logger

load_dotenv()
log = get_logger(__name__)

MODEL = "claude-opus-4-6"


def _build_prompt(signal: dict, analysis: dict) -> str:
    plan = signal["trade_plan"]
    conf = signal["confluence"]
    votes = conf["votes"]
    direction = plan["direction"].upper()
    pair = plan["pair"].replace("_", "/")

    # Collect recent structure events for context
    tf_summaries = []
    for tf in ["M1", "M5", "H1", "H4"]:
        tf_data = analysis["timeframes"].get(tf, {})
        if not tf_data:
            continue
        trend = tf_data.get("trend", "unknown")
        bos_count = len(tf_data.get("bos_events", []))
        choch_count = len(tf_data.get("choch_events", []))
        vote = votes.get(tf, "neutral")
        tf_summaries.append(
            f"  - {tf}: trend={trend}, BOS={bos_count}, CHoCH={choch_count}, vote={vote}"
        )

    tf_block = "\n".join(tf_summaries)

    return f"""You are a professional forex trading analyst. A trading system has detected the following setup. Write a clear, plain English summary for a trader.

SETUP DETAILS:
- Pair: {pair}
- Direction: {direction}
- Confluence score: {conf['score']}/{conf['max_score']} timeframes agree
- Dissenting timeframes: {conf.get('dissenting_timeframes', [])}
- Neutral timeframes: {conf.get('neutral_timeframes', [])}

TIMEFRAME BREAKDOWN:
{tf_block}

TRADE PLAN:
- Entry: {plan['entry_price']}
- Stop Loss: {plan['stop_loss']} ({plan['sl_pips']} pips)
- Take Profit 1: {plan['take_profit_1']} (2:1 R:R)
- Take Profit 2: {plan['take_profit_2']} (3:1 R:R)
- Lot size: {plan['lot_size']} (risking {plan['risk_percent']}% of account)
- Reference timeframe for structure: {plan['reference_timeframe']}

Write your response in exactly this format:

SUMMARY:
[3-5 sentences explaining why this trade is valid. Mention the confluence across timeframes, the key structure (BOS/CHoCH), and what the price action is telling us. Be specific — mention actual price levels where relevant. Write as if briefing a trader before they enter.]

INVALIDATION:
[One sentence: exactly what price action would cancel this setup and why.]

LESSON:
[One sentence: the key thing to watch for while this trade is active.]"""


def generate_summary(
    signal: dict,
    analysis: dict,
) -> str:
    """
    Call Claude API to generate a plain English trade summary.

    Args:
        signal:   Full signal dict (must have trade_plan populated).
        analysis: Full analysis dict from run_analysis().

    Returns:
        Formatted summary string.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY not set in .env")

    plan = signal.get("trade_plan")
    if not plan:
        raise ValueError("Signal has no trade_plan. Run build_trade_plan first.")

    conf = signal.get("confluence", {})
    if not conf.get("signal_valid"):
        raise ValueError("Signal is not valid. Cannot generate summary.")

    client = anthropic.Anthropic(api_key=api_key)
    prompt = _build_prompt(signal, analysis)

    log.info(f"Calling Claude API for {signal['pair']} {plan['direction']} summary...")

    message = client.messages.create(
        model=MODEL,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )

    summary = message.content[0].text.strip()
    log.info(f"Summary generated ({len(summary)} chars, {message.usage.output_tokens} tokens)")
    return summary


def run_summary_for_pair(pair: str) -> dict | None:
    """
    Load signal + analysis, generate summary, attach to signal, write back.

    Returns updated signal dict, or None if prerequisites not met.
    """
    signal_path = get_signal_path(pair)
    analysis_path = get_analysis_path(pair)

    if not file_exists(signal_path):
        log.error(f"No signal file for {pair}. Run workflows 01-04 first.")
        return None

    if not file_exists(analysis_path):
        log.error(f"No analysis file for {pair}.")
        return None

    signal = read_json(signal_path)
    analysis = read_json(analysis_path)

    if not signal.get("trade_plan"):
        log.error(f"Signal for {pair} has no trade_plan. Run build_trade_plan first.")
        return None

    conf = signal.get("confluence", {})
    plan = signal["trade_plan"]

    # Cost gate: only call API for qualifying setups
    if not conf.get("signal_valid"):
        log.warning(f"Signal not valid — skipping API call.")
        return None
    if plan.get("risk_reward", 0) < float(os.getenv("MIN_RISK_REWARD", 2.0)):
        log.warning(f"RR too low — skipping API call.")
        return None

    summary = generate_summary(signal, analysis)

    signal["summary"] = summary
    signal["status"] = "ready"
    write_json(signal_path, signal)
    log.info(f"Summary attached to signal → {signal_path}")

    return signal


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Claude summary for a signal")
    parser.add_argument("--pair", required=True)
    args = parser.parse_args()

    result = run_summary_for_pair(args.pair)
    if result:
        print(f"\n{'='*60}")
        print(f"  {result['pair']} — {result['trade_plan']['direction'].upper()}")
        print(f"{'='*60}")
        print(result["summary"])
        print(f"{'='*60}\n")
    else:
        print(f"\n✗ Could not generate summary for {args.pair}")
