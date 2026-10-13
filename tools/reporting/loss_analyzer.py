"""
Loss analyzer — uses Claude AI to understand WHY a trade lost
and produce actionable recommendations to avoid similar losses.

Called automatically when a journalled trade closes with outcome="loss".
"""

import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from tools.utils.logger import get_logger

load_dotenv()
log = get_logger(__name__)


def analyze_loss(trade: dict, recent_losses: list[dict] | None = None) -> dict:
    """
    Send losing trade context to Claude and get back structured insights.

    Returns a dict with:
        what_happened   - plain-English description of why the trade lost
        warning_signs   - signals that should have flagged caution
        avoidance_tips  - concrete rule changes to prevent recurrence
        pattern         - detected recurring pattern (if any)
        severity        - "minor" | "moderate" | "critical"
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return _fallback_analysis(trade)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        pair      = (trade.get("pair") or "").replace("_", "/")
        direction = trade.get("direction", "unknown").upper()
        entry     = trade.get("entry_price", "?")
        sl        = trade.get("stop_loss", "?")
        tp        = trade.get("take_profit", "?")
        score     = trade.get("confluence_score", "?")
        rr        = trade.get("risk_reward", "?")
        pnl       = trade.get("pnl_usd", "?")
        r_mult    = trade.get("r_multiple", "?")
        exec_at   = (trade.get("executed_at") or "")[:19]
        exit_at   = (trade.get("exit_time") or "")[:19]

        # Build pattern context from recent losses
        pattern_ctx = ""
        if recent_losses and len(recent_losses) > 1:
            pairs    = [l.get("pair","") for l in recent_losses[-5:]]
            dirs     = [l.get("direction","") for l in recent_losses[-5:]]
            pattern_ctx = f"\nRecent loss streak: {len(recent_losses)} losses. Pairs: {pairs}. Directions: {dirs}."

        prompt = f"""You are a senior forex risk analyst reviewing a losing trade for the NEXUS algorithmic trading system.

LOSING TRADE DETAILS:
  Pair:             {pair}
  Direction:        {direction}
  Entry Price:      {entry}
  Stop Loss:        {sl}
  Take Profit:      {tp}
  Confluence Score: {score}/4
  Risk:Reward:      {rr}:1
  Executed:         {exec_at}
  Closed (SL hit):  {exit_at}
  P&L:              ${pnl}
  R Multiple:       {r_mult}R
{pattern_ctx}

Analyze this loss and respond in this EXACT JSON format (no markdown, pure JSON):
{{
  "what_happened": "2-3 sentence plain English explanation of why the trade lost",
  "warning_signs": ["sign 1", "sign 2", "sign 3"],
  "avoidance_tips": ["tip 1", "tip 2", "tip 3"],
  "pattern": "brief description of any recurring pattern, or null",
  "severity": "minor|moderate|critical",
  "market_lesson": "one key market insight learned from this loss"
}}"""

        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )

        import json
        text = msg.content[0].text.strip()
        # Strip any accidental markdown fences
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        result["analyzed_at"] = datetime.now(timezone.utc).isoformat()
        result["model"] = "claude-haiku-4-5"
        log.info(f"Loss analysis complete for trade {trade.get('trade_id')} — severity={result.get('severity')}")
        return result

    except Exception as e:
        log.warning(f"Loss analysis failed ({e}), using fallback.")
        return _fallback_analysis(trade)


def _fallback_analysis(trade: dict) -> dict:
    """Basic rule-based analysis when Claude is unavailable."""
    score = trade.get("confluence_score", 0) or 0
    rr    = trade.get("risk_reward", 0) or 0
    tips  = []
    signs = []

    if score < 3:
        signs.append("Low confluence score — market agreement was weak")
        tips.append("Only trade with confluence score ≥ 3 across all timeframes")
    if rr < 2:
        signs.append("Risk:Reward below 2:1 — insufficient reward for the risk taken")
        tips.append("Enforce minimum 2:1 R:R before entry")
    tips.append("Review higher timeframe trend before entering on lower TF signal")
    tips.append("Consider waiting for price to pull back to key structure level")

    return {
        "what_happened": f"Trade hit stop loss. Confluence score was {score}/4 with {rr}:1 R:R.",
        "warning_signs": signs or ["Market moved against position immediately after entry"],
        "avoidance_tips": tips,
        "pattern": None,
        "severity": "moderate",
        "market_lesson": "Not every confluence signal leads to a winning trade — position sizing and patience are key.",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "model": "fallback",
    }


def generate_period_summary(losses: list[dict], wins: list[dict]) -> dict:
    """Generate a high-level summary of what's working and what isn't."""
    if not losses and not wins:
        return {"summary": "No closed trades in this period.", "recommendations": []}

    total   = len(losses) + len(wins)
    wr      = round(len(wins) / total * 100, 1) if total else 0
    total_r = sum(t.get("r_multiple", 0) or 0 for t in wins + losses)

    # Most common loss patterns
    loss_pairs = {}
    loss_dirs  = {}
    for l in losses:
        p = l.get("pair", "?")
        d = l.get("direction", "?")
        loss_pairs[p] = loss_pairs.get(p, 0) + 1
        loss_dirs[d]  = loss_dirs.get(d, 0) + 1

    worst_pair = max(loss_pairs, key=loss_pairs.get) if loss_pairs else None
    worst_dir  = max(loss_dirs,  key=loss_dirs.get)  if loss_dirs  else None

    recs = []
    if wr < 40:
        recs.append("Win rate below 40% — consider tightening confluence requirements to score ≥ 4")
    if worst_pair:
        recs.append(f"Most losses on {worst_pair.replace('_','/')} — temporarily avoid or increase confluence threshold for this pair")
    if worst_dir == "bearish":
        recs.append("More losses on short trades — verify bearish bias against higher-timeframe trend")
    elif worst_dir == "bullish":
        recs.append("More losses on long trades — check if USD strength is overriding local bullish signals")
    if total_r < 0:
        recs.append("Negative R total — reduce position size by 50% until win rate recovers above 45%")

    avg_win_usd  = round(sum(t.get("pnl_usd", 0) or 0 for t in wins) / len(wins), 2) if wins else 0
    avg_loss_usd = round(sum(t.get("pnl_usd", 0) or 0 for t in losses) / len(losses), 2) if losses else 0
    all_rr       = [t.get("risk_reward", 0) or 0 for t in wins + losses if t.get("risk_reward")]
    avg_rr       = round(sum(all_rr) / len(all_rr), 2) if all_rr else 0

    return {
        "period_trades":   total,
        "wins":            len(wins),
        "losses":          len(losses),
        "win_rate":        wr,
        "total_r":         round(total_r, 2),
        "avg_win_usd":     avg_win_usd,
        "avg_loss_usd":    avg_loss_usd,
        "avg_rr":          avg_rr,
        "worst_pair":      worst_pair,
        "worst_direction": worst_dir,
        "recommendations": recs,
    }
