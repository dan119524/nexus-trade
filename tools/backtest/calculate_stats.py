"""
Calculate aggregate performance statistics from a list of completed trades.
"""

from tools.utils.logger import get_logger

log = get_logger(__name__)


def calculate_stats(trades: list[dict]) -> dict:
    """
    Compute win rate, R:R, drawdown, equity curve, and profit factor.

    Args:
        trades: List of trade result dicts from simulate_signals.

    Returns:
        Stats dict.
    """
    if not trades:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "open": 0,
            "win_rate_pct": 0.0,
            "avg_r_multiple": 0.0,
            "total_r": 0.0,
            "max_drawdown_r": 0.0,
            "profit_factor": 0.0,
            "equity_curve": [],
            "best_trade_r": 0.0,
            "worst_trade_r": 0.0,
        }

    closed = [t for t in trades if t["result"] in ("win", "loss")]
    wins   = [t for t in closed if t["result"] == "win"]
    losses = [t for t in closed if t["result"] == "loss"]
    open_  = [t for t in trades if t["result"] == "open"]

    win_rate = round(len(wins) / len(closed) * 100, 1) if closed else 0.0

    r_multiples = [t["r_multiple"] for t in closed]
    avg_r = round(sum(r_multiples) / len(r_multiples), 2) if r_multiples else 0.0
    total_r = round(sum(r_multiples), 2)

    gross_profit = sum(t["r_multiple"] for t in wins)
    gross_loss   = abs(sum(t["r_multiple"] for t in losses))
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else float("inf")

    best_r  = round(max((t["r_multiple"] for t in closed), default=0), 2)
    worst_r = round(min((t["r_multiple"] for t in closed), default=0), 2)

    # Equity curve (cumulative R) and max drawdown
    equity_curve = []
    running_r = 0.0
    peak_r = 0.0
    max_dd = 0.0

    for t in closed:
        running_r += t["r_multiple"]
        equity_curve.append(round(running_r, 2))
        if running_r > peak_r:
            peak_r = running_r
        dd = peak_r - running_r
        if dd > max_dd:
            max_dd = dd

    stats = {
        "total_trades": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "open": len(open_),
        "win_rate_pct": win_rate,
        "avg_r_multiple": avg_r,
        "total_r": total_r,
        "max_drawdown_r": round(max_dd, 2),
        "profit_factor": profit_factor,
        "equity_curve": equity_curve,
        "best_trade_r": best_r,
        "worst_trade_r": worst_r,
    }

    log.info(
        f"Stats — {len(trades)} trades | WR={win_rate}% | "
        f"AvgR={avg_r} | Total={total_r}R | MaxDD={round(max_dd,2)}R"
    )
    return stats
