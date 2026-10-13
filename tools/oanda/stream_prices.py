"""
Multi-pair monitoring loop.

Runs continuously, cycling through a watchlist of pairs. For each pair:
  1. Fetch latest candles (all 4 timeframes)
  2. Run structural analysis
  3. Score confluence
  4. If valid signal (score >= 3), build trade plan + fire push notification

The loop sleeps between cycles to respect OANDA rate limits and avoid
re-triggering signals that are already active.

Usage (CLI):
    python -m tools.oanda.stream_prices
    python -m tools.oanda.stream_prices --pairs EUR_USD GBP_USD USD_JPY
    python -m tools.oanda.stream_prices --interval 300   # check every 5 min
"""

import argparse
import os
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from tools.oanda.fetch_candles import fetch_all_timeframes
from tools.analysis.run_analysis import run_full_analysis
from tools.confluence.score_confluence import run_confluence_for_pair
from tools.trade_plan.build_trade_plan import build_trade_plan
from tools.utils.file_io import get_signal_path, file_exists, read_json
from tools.utils.logger import get_logger

load_dotenv()
log = get_logger(__name__)

DEFAULT_PAIRS = [
    "EUR_USD", "GBP_USD", "USD_JPY",
    "AUD_USD", "USD_CAD", "EUR_GBP",
]
DEFAULT_INTERVAL = 300   # seconds between full scan cycles
PUSH_ENDPOINT = "https://exp.host/--/api/v2/push/send"


# ── Push notification ─────────────────────────────────────────────────────────

def send_push_notification(
    expo_token: str,
    title: str,
    body: str,
    data: dict | None = None,
) -> bool:
    """
    Send a push notification via Expo's push service.

    Args:
        expo_token: The device's Expo push token (stored by the API server).
        title:      Notification title.
        body:       Notification body text.
        data:       Optional extra payload delivered to the app.

    Returns:
        True if accepted by Expo, False otherwise.
    """
    payload = {
        "to": expo_token,
        "title": title,
        "body": body,
        "sound": "default",
        "data": data or {},
    }
    try:
        r = requests.post(PUSH_ENDPOINT, json=payload, timeout=10)
        result = r.json().get("data", {})
        status = result.get("status", "unknown")
        if status == "ok":
            log.info(f"Push sent → {expo_token[:20]}... | {title}")
            return True
        else:
            log.warning(f"Push not accepted: {result}")
            return False
    except Exception as e:
        log.warning(f"Push failed: {e}")
        return False


def notify_new_signal(signal: dict, push_tokens: list[str]) -> None:
    """Send a push to all registered devices for a new valid signal."""
    if not push_tokens:
        return
    plan = signal.get("trade_plan", {}) or {}
    conf = signal.get("confluence", {})
    pair = signal["pair"].replace("_", "/")
    direction = conf.get("direction", "").upper()
    score = conf.get("score", 0)
    entry = plan.get("entry_price", "")

    title = f"NEXUS: {pair} {direction} {score}/4"
    body = (
        f"Entry {entry}  |  "
        f"SL {plan.get('stop_loss', '')}  |  "
        f"TP {plan.get('take_profit_1', '')}  |  "
        f"{plan.get('risk_reward', '')}:1 R:R"
    )

    for token in push_tokens:
        send_push_notification(
            token, title, body,
            data={"pair": signal["pair"], "signal_id": signal.get("id")},
        )


# ── Signal state tracking ─────────────────────────────────────────────────────

class SignalTracker:
    """Remember which signal IDs have already been notified."""
    def __init__(self):
        self._seen: set[str] = set()

    def is_new(self, signal_id: str) -> bool:
        return signal_id not in self._seen

    def mark_seen(self, signal_id: str) -> None:
        self._seen.add(signal_id)


# ── Monitoring loop ───────────────────────────────────────────────────────────

def monitor_pairs(
    pairs: list[str],
    interval: int = DEFAULT_INTERVAL,
    push_tokens: list[str] | None = None,
) -> None:
    """
    Continuously monitor a list of pairs for valid signals.

    Args:
        pairs:       List of OANDA pair names to watch.
        interval:    Seconds between full scan cycles.
        push_tokens: Expo push tokens to notify on new signals.
    """
    tokens = push_tokens or []
    tracker = SignalTracker()

    log.info(f"Monitor starting — watching {len(pairs)} pairs, interval={interval}s")
    log.info(f"Pairs: {', '.join(pairs)}")

    cycle = 0
    while True:
        cycle += 1
        cycle_start = time.time()
        log.info(f"\n{'='*50}")
        log.info(f"Cycle {cycle} — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
        log.info(f"{'='*50}")

        for pair in pairs:
            try:
                log.info(f"Scanning {pair}...")

                # 1. Fetch candles
                fetch_all_timeframes(pair, count=300)

                # 2. Run analysis
                run_full_analysis(pair)

                # 3. Score confluence
                signal = run_confluence_for_pair(pair)

                if signal is None:
                    log.info(f"  {pair}: No signal")
                    continue

                # 4. Build trade plan
                signal = build_trade_plan(pair)

                if signal is None:
                    log.info(f"  {pair}: Signal valid but trade plan rejected (RR too low)")
                    continue

                conf = signal["confluence"]
                plan = signal["trade_plan"]
                signal_id = signal.get("id", "")

                log.info(
                    f"  {pair}: SIGNAL {conf['direction'].upper()} "
                    f"{conf['score']}/4 | "
                    f"Entry={plan['entry_price']} SL={plan['stop_loss']} "
                    f"TP={plan['take_profit_1']} RR={plan['risk_reward']}"
                )

                # 5. Notify only if this is a new signal
                if tracker.is_new(signal_id):
                    tracker.mark_seen(signal_id)
                    notify_new_signal(signal, tokens)
                    log.info(f"  {pair}: Push sent to {len(tokens)} device(s)")
                else:
                    log.info(f"  {pair}: Signal already notified, skipping push")

            except Exception as e:
                log.error(f"  {pair}: Error during scan — {e}")
                continue

        elapsed = time.time() - cycle_start
        sleep_time = max(0, interval - elapsed)
        log.info(f"\nCycle {cycle} complete in {elapsed:.1f}s. Next scan in {sleep_time:.0f}s...")
        time.sleep(sleep_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor multiple pairs for signals")
    parser.add_argument(
        "--pairs", nargs="+", default=DEFAULT_PAIRS,
        help="Pairs to watch (default: 6 majors)"
    )
    parser.add_argument(
        "--interval", type=int, default=DEFAULT_INTERVAL,
        help="Seconds between scan cycles (default: 300)"
    )
    parser.add_argument(
        "--push-token", type=str, default=None,
        help="Expo push token to notify (optional)"
    )
    args = parser.parse_args()

    tokens = [args.push_token] if args.push_token else []
    monitor_pairs(args.pairs, interval=args.interval, push_tokens=tokens)
