"""
Email reporting — builds and sends HTML reports via Gmail SMTP.

Required .env keys:
    EMAIL_TO   = recipient address  (danilefsshaye892@gmail.com)
    EMAIL_USER = your Gmail address
    EMAIL_PASS = Gmail App Password  (not your account password)
                 https://myaccount.google.com/apppasswords
    EMAIL_SMTP = smtp.gmail.com   (default)
    EMAIL_PORT = 587              (default)
"""

import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from tools.utils.logger import get_logger

load_dotenv()
log = get_logger(__name__)


# ── HTML helpers ──────────────────────────────────────────────────────────────

def _row(label: str, value: str, color: str = "") -> str:
    style = f"color:{color};font-weight:700" if color else ""
    return f"""
      <tr>
        <td style="padding:8px 16px;color:#94A3B8;font-size:12px;border-bottom:1px solid #1E293B">{label}</td>
        <td style="padding:8px 16px;font-size:12px;border-bottom:1px solid #1E293B;{style}">{value}</td>
      </tr>"""


def _trade_row(t: dict, i: int) -> str:
    outcome = t.get("outcome") or "open"
    pair    = (t.get("pair") or "").replace("_", "/")
    dirn    = (t.get("direction") or "").upper()
    pnl     = t.get("pnl_usd")
    r       = t.get("r_multiple")
    pnl_str = f"+${pnl:.2f}" if pnl and pnl > 0 else (f"-${abs(pnl):.2f}" if pnl else "—")
    pnl_col = "#00D68F" if pnl and pnl > 0 else ("#F5365C" if pnl and pnl < 0 else "#94A3B8")
    oc_col  = "#00D68F" if outcome == "win" else ("#F5365C" if outcome == "loss" else "#FFAA00")
    exec_dt = (t.get("executed_at") or "")[:10]
    loss_a  = t.get("loss_analysis")
    analysis_html = ""
    if loss_a:
        tips = "".join(f"<li>{tip}</li>" for tip in (loss_a.get("avoidance_tips") or []))
        analysis_html = f"""
          <tr>
            <td colspan="8" style="padding:10px 16px 16px 32px;background:#0F1420;font-size:11px;color:#94A3B8">
              <strong style="color:#F5365C">⚠ Why it lost:</strong> {loss_a.get("what_happened","")}<br>
              <strong style="color:#FFAA00">How to avoid:</strong><ul style="margin:4px 0 0 16px;padding:0">{tips}</ul>
              <em style="color:#475569">Market lesson: {loss_a.get("market_lesson","")}</em>
            </td>
          </tr>"""

    return f"""
      <tr style="background:{'#0A1520' if i%2==0 else '#0D1A2A'}">
        <td style="padding:10px 16px;font-size:13px;font-weight:700">{pair}</td>
        <td style="padding:10px 16px;font-size:11px;color:{'#00D68F' if dirn=='BULLISH' else '#F5365C'}">{dirn}</td>
        <td style="padding:10px 16px;font-size:12px;font-family:monospace">{t.get("entry_price","—")}</td>
        <td style="padding:10px 16px;font-size:12px;color:#F5365C;font-family:monospace">{t.get("stop_loss","—")}</td>
        <td style="padding:10px 16px;font-size:12px;color:#00D68F;font-family:monospace">{t.get("take_profit","—")}</td>
        <td style="padding:10px 16px;font-size:12px;color:{pnl_col};font-weight:700">{pnl_str}</td>
        <td style="padding:10px 16px;font-size:11px;color:{oc_col};font-weight:700;text-transform:uppercase">{outcome}</td>
        <td style="padding:10px 16px;font-size:11px;color:#94A3B8">{exec_dt}</td>
      </tr>{analysis_html}"""


def build_html(
    period_label: str,
    trades: list[dict],
    summary: dict,
    backtest_results: list[dict] | None = None,
) -> str:
    wins    = [t for t in trades if t.get("outcome") == "win"]
    losses  = [t for t in trades if t.get("outcome") == "loss"]
    open_t  = [t for t in trades if not t.get("outcome")]
    wr      = round(len(wins)/len(trades)*100, 1) if trades else 0
    total_pnl = sum(t.get("pnl_usd") or 0 for t in trades)
    total_r   = sum(t.get("r_multiple") or 0 for t in trades)

    pnl_color = "#00D68F" if total_pnl >= 0 else "#F5365C"
    wr_color  = "#00D68F" if wr >= 50 else "#F5365C"

    trade_rows = "".join(_trade_row(t, i) for i, t in enumerate(trades))

    recs_html = ""
    recs = summary.get("recommendations") or []
    if recs:
        recs_html = "<ul style='margin:8px 0 0 16px;padding:0'>" + \
                    "".join(f"<li style='margin-bottom:6px;font-size:12px;color:#94A3B8'>{r}</li>" for r in recs) + \
                    "</ul>"

    bt_html = ""
    if backtest_results:
        bt_rows = "".join(f"""
          <tr>
            <td style="padding:8px 14px;font-weight:700">{b.get('pair','').replace('_','/')}</td>
            <td style="padding:8px 14px;color:{'#00D68F' if (b.get('win_rate') or 0)>=50 else '#F5365C'}">{b.get('win_rate',0)}%</td>
            <td style="padding:8px 14px">{b.get('trades',0)}</td>
            <td style="padding:8px 14px;color:{'#00D68F' if (b.get('total_r') or 0)>=0 else '#F5365C'}">{b.get('total_r',0):+.2f}R</td>
            <td style="padding:8px 14px">{b.get('profit_factor','—')}</td>
          </tr>""" for b in backtest_results)
        bt_html = f"""
          <div style="margin:24px 0">
            <h3 style="color:#3B7BF6;font-size:13px;letter-spacing:2px;margin-bottom:12px">WEEKEND BACKTEST SUMMARY</h3>
            <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse">
              <thead>
                <tr style="background:#0F1420">
                  <th style="padding:8px 14px;text-align:left;font-size:10px;color:#475569;letter-spacing:1.5px">PAIR</th>
                  <th style="padding:8px 14px;text-align:left;font-size:10px;color:#475569;letter-spacing:1.5px">WIN RATE</th>
                  <th style="padding:8px 14px;text-align:left;font-size:10px;color:#475569;letter-spacing:1.5px">TRADES</th>
                  <th style="padding:8px 14px;text-align:left;font-size:10px;color:#475569;letter-spacing:1.5px">TOTAL R</th>
                  <th style="padding:8px 14px;text-align:left;font-size:10px;color:#475569;letter-spacing:1.5px">PROFIT FACTOR</th>
                </tr>
              </thead>
              <tbody>{bt_rows}</tbody>
            </table>
          </div>"""

    now = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#070A12;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#EEF2FF">
  <div style="max-width:680px;margin:0 auto;padding:24px 16px">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#0D1117,#131929);border:1px solid #1A2035;border-radius:14px;padding:24px 28px;margin-bottom:20px">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
        <div style="width:36px;height:36px;background:linear-gradient(135deg,#3B7BF6,#00D68F);border-radius:9px;display:inline-flex;align-items:center;justify-content:center;font-weight:900;color:white;font-size:16px">N</div>
        <div>
          <div style="font-size:18px;font-weight:900;letter-spacing:2px">NEXUS TRADE</div>
          <div style="font-size:10px;letter-spacing:2px;color:#475569">ALGORITHMIC TRADING REPORT</div>
        </div>
      </div>
      <div style="font-size:13px;color:#94A3B8;margin-top:8px">{period_label} · Generated {now}</div>
    </div>

    <!-- KPI Strip -->
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px">
      <div style="background:#101520;border:1px solid #1A2035;border-radius:10px;padding:14px 16px;border-top:2px solid #3B7BF6">
        <div style="font-size:9px;color:#475569;letter-spacing:2px;margin-bottom:6px">TOTAL TRADES</div>
        <div style="font-size:22px;font-weight:800">{len(trades)}</div>
        <div style="font-size:10px;color:#94A3B8;margin-top:3px">{len(wins)}W · {len(losses)}L · {len(open_t)} open</div>
      </div>
      <div style="background:#101520;border:1px solid #1A2035;border-radius:10px;padding:14px 16px;border-top:2px solid {wr_color}">
        <div style="font-size:9px;color:#475569;letter-spacing:2px;margin-bottom:6px">WIN RATE</div>
        <div style="font-size:22px;font-weight:800;color:{wr_color}">{wr}%</div>
      </div>
      <div style="background:#101520;border:1px solid #1A2035;border-radius:10px;padding:14px 16px;border-top:2px solid {pnl_color}">
        <div style="font-size:9px;color:#475569;letter-spacing:2px;margin-bottom:6px">TOTAL P/L</div>
        <div style="font-size:22px;font-weight:800;color:{pnl_color}">{'+' if total_pnl>=0 else ''}${total_pnl:.2f}</div>
      </div>
      <div style="background:#101520;border:1px solid #1A2035;border-radius:10px;padding:14px 16px;border-top:2px solid #7B61FF">
        <div style="font-size:9px;color:#475569;letter-spacing:2px;margin-bottom:6px">TOTAL R</div>
        <div style="font-size:22px;font-weight:800;color:#7B61FF">{'+' if total_r>=0 else ''}{total_r:.2f}R</div>
      </div>
    </div>

    <!-- AI Recommendations -->
    {f'''<div style="background:#0F1A2A;border:1px solid #1A2035;border-left:3px solid #FFAA00;border-radius:10px;padding:16px 20px;margin-bottom:20px">
      <div style="font-size:11px;font-weight:700;letter-spacing:2px;color:#FFAA00;margin-bottom:8px">⚠ LOSS PREVENTION INSIGHTS</div>
      {recs_html}
    </div>''' if recs else ''}

    {bt_html}

    <!-- Trade log -->
    <div style="background:#101520;border:1px solid #1A2035;border-radius:12px;overflow:hidden;margin-bottom:20px">
      <div style="padding:14px 16px;border-bottom:1px solid #1A2035">
        <span style="font-size:11px;font-weight:700;letter-spacing:2px;color:#94A3B8">TRADE LOG</span>
      </div>
      <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:12px">
        <thead>
          <tr style="background:#0A1020">
            <th style="padding:8px 16px;text-align:left;font-size:9px;color:#475569;letter-spacing:1.5px">PAIR</th>
            <th style="padding:8px 16px;text-align:left;font-size:9px;color:#475569;letter-spacing:1.5px">DIR</th>
            <th style="padding:8px 16px;text-align:left;font-size:9px;color:#475569;letter-spacing:1.5px">ENTRY</th>
            <th style="padding:8px 16px;text-align:left;font-size:9px;color:#475569;letter-spacing:1.5px">SL</th>
            <th style="padding:8px 16px;text-align:left;font-size:9px;color:#475569;letter-spacing:1.5px">TP</th>
            <th style="padding:8px 16px;text-align:left;font-size:9px;color:#475569;letter-spacing:1.5px">P/L</th>
            <th style="padding:8px 16px;text-align:left;font-size:9px;color:#475569;letter-spacing:1.5px">RESULT</th>
            <th style="padding:8px 16px;text-align:left;font-size:9px;color:#475569;letter-spacing:1.5px">DATE</th>
          </tr>
        </thead>
        <tbody>
          {trade_rows if trades else '<tr><td colspan="8" style="padding:24px;text-align:center;color:#475569">No trades in this period</td></tr>'}
        </tbody>
      </table>
    </div>

    <!-- Footer -->
    <div style="text-align:center;font-size:10px;color:#475569;padding:12px">
      NEXUS Trade · Automated Algorithmic Trading · Practice Account Only
    </div>
  </div>
</body>
</html>"""


def send(subject: str, html: str) -> bool:
    """Send an HTML email. Uses Resend API if RESEND_API_KEY is set, else Gmail SMTP."""
    to_addr   = os.getenv("EMAIL_TO", "danilefsshaye892@gmail.com")
    resend_key = os.getenv("RESEND_API_KEY", "")

    # ── Resend API (preferred — no SMTP auth issues) ──────────────────
    if resend_key:
        try:
            import resend
            resend.api_key = resend_key
            resend.Emails.send({
                "from":    "NEXUS Trade <onboarding@resend.dev>",
                "to":      [to_addr],
                "subject": f"NEXUS Trade — {subject}",
                "html":    html,
            })
            log.info(f"Email sent via Resend → {to_addr}: {subject}")
            return True
        except Exception as e:
            log.error(f"Resend failed: {e}")
            return False

    # ── Gmail SMTP fallback ───────────────────────────────────────────
    from_addr = os.getenv("EMAIL_USER", "")
    password  = os.getenv("EMAIL_PASS", "")
    smtp_host = os.getenv("EMAIL_SMTP", "smtp.gmail.com")
    smtp_port = int(os.getenv("EMAIL_PORT", "587"))

    if not from_addr or not password:
        log.warning("Email not configured. Add RESEND_API_KEY or EMAIL_USER/EMAIL_PASS to .env.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"NEXUS Trade — {subject}"
    msg["From"]    = f"NEXUS Trade <{from_addr}>"
    msg["To"]      = to_addr
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(from_addr, password)
            server.sendmail(from_addr, to_addr, msg.as_string())
        log.info(f"Email sent via SMTP → {to_addr}: {subject}")
        return True
    except smtplib.SMTPAuthenticationError:
        log.error("Gmail authentication failed. Use an App Password or set RESEND_API_KEY.")
        return False
    except Exception as e:
        log.error(f"Email failed: {e}")
        return False


def send_loss_alert(trade: dict, analysis: dict) -> bool:
    """Send an immediate email when a trade closes at a loss."""
    pair     = (trade.get("pair") or "").replace("_", "/")
    pnl      = trade.get("pnl_usd", 0) or 0
    what     = analysis.get("what_happened", "")
    tips     = analysis.get("avoidance_tips") or []
    tips_html = "".join(f"<li style='margin-bottom:6px'>{t}</li>" for t in tips)
    severity  = analysis.get("severity", "moderate")
    sev_color = "#F5365C" if severity == "critical" else ("#FFAA00" if severity == "moderate" else "#94A3B8")

    html = f"""<!DOCTYPE html>
<html><body style="margin:0;padding:24px;background:#070A12;font-family:-apple-system,sans-serif;color:#EEF2FF;max-width:600px">
  <div style="background:#1A0A0F;border:1px solid #F5365C33;border-left:4px solid #F5365C;border-radius:12px;padding:20px 24px;margin-bottom:20px">
    <div style="font-size:16px;font-weight:800;color:#F5365C;margin-bottom:4px">⚠ Trade Loss Alert</div>
    <div style="font-size:13px;color:#94A3B8">{pair} · ${abs(pnl):.2f} loss · Severity: <span style="color:{sev_color};font-weight:700">{severity.upper()}</span></div>
  </div>
  <div style="background:#101520;border:1px solid #1A2035;border-radius:10px;padding:20px;margin-bottom:16px">
    <div style="font-size:10px;color:#475569;letter-spacing:2px;margin-bottom:8px">WHAT HAPPENED</div>
    <div style="font-size:13px;color:#94A3B8;line-height:1.6">{what}</div>
  </div>
  <div style="background:#101520;border:1px solid #1A2035;border-radius:10px;padding:20px;margin-bottom:16px">
    <div style="font-size:10px;color:#475569;letter-spacing:2px;margin-bottom:8px">HOW TO AVOID IN FUTURE</div>
    <ul style="margin:0;padding-left:20px;color:#94A3B8;font-size:13px;line-height:1.8">{tips_html}</ul>
  </div>
  <div style="background:#0F1A10;border:1px solid #00D68F22;border-radius:10px;padding:16px 20px">
    <div style="font-size:10px;color:#475569;letter-spacing:2px;margin-bottom:6px">MARKET LESSON</div>
    <div style="font-size:12px;color:#00D68F;font-style:italic">{analysis.get("market_lesson","")}</div>
  </div>
  <div style="text-align:center;font-size:10px;color:#475569;margin-top:20px">NEXUS Trade · Practice Account</div>
</body></html>"""

    return send(f"Loss Alert — {pair} (-${abs(pnl):.2f})", html)


def _confluence_table_html(conf: dict) -> str:
    """Build the multi-timeframe votes table rows."""
    votes = conf.get("votes") or {}
    direction = conf.get("direction", "")
    rows = ""
    for tf in ["H4", "H1", "M5", "M1"]:
        vote = votes.get(tf, "—")
        if vote == direction:
            icon, col = "✓", "#00D68F"
        elif vote == "neutral":
            icon, col = "–", "#FFAA00"
        else:
            icon, col = "✗", "#F5365C"
        vote_label = vote.upper() if vote != "—" else "—"
        rows += (
            f'<tr style="border-bottom:1px solid #1A2035">'
            f'<td style="padding:8px 14px;font-size:12px;color:#94A3B8;width:30%">{tf}</td>'
            f'<td style="padding:8px 14px;font-size:12px;font-weight:700;color:{col}">'
            f'{icon} {vote_label}</td></tr>'
        )
    return rows


def _structure_html(ref_tf_data: dict, direction: str) -> str:
    """Build the market structure narrative from analysis data."""
    trend   = (ref_tf_data.get("trend") or "unknown").upper()
    channel = (ref_tf_data.get("channel") or {}).get("channel_type", "unknown").upper()

    t_col = "#00D68F" if "BULL" in trend else ("#F5365C" if "BEAR" in trend else "#FFAA00")
    c_col = "#00D68F" if channel == "ASCENDING" else ("#F5365C" if channel == "DESCENDING" else "#94A3B8")

    # Most recent structural event (CHoCH preferred, then BOS)
    event_html = ""
    choch = ref_tf_data.get("choch_events") or []
    bos   = ref_tf_data.get("bos_events")   or []
    events = choch + bos
    if events:
        evt = events[-1]
        etype   = evt.get("event_type", "")
        edir    = (evt.get("direction") or "").upper()
        elevel  = evt.get("level", "")
        etime   = (evt.get("broken_at_time") or "")[:10]
        e_col   = "#00D68F" if "BULL" in edir else "#F5365C"
        e_label = "Change of Character — trend flip signal" if etype == "CHoCH" else "Break of Structure — continuation signal"
        event_html = (
            f'<div style="margin-top:10px;padding:10px 14px;background:#0A1020;border-left:3px solid {e_col};border-radius:6px">'
            f'<span style="font-size:10px;font-weight:700;color:{e_col};letter-spacing:1px">{etype} {edir}</span>'
            f'<span style="font-size:11px;color:#94A3B8"> at {elevel} ({etime})</span>'
            f'<div style="font-size:11px;color:#475569;margin-top:3px">{e_label}</div>'
            f'</div>'
        )

    # Nearest key levels
    highs = ref_tf_data.get("swing_highs") or []
    lows  = ref_tf_data.get("swing_lows")  or []
    nearest_res = max((h["price"] for h in highs[-3:] if "price" in h), default=None)
    nearest_sup = min((l["price"] for l in lows[-3:]  if "price" in l), default=None)
    levels_html = ""
    if nearest_res or nearest_sup:
        levels_html = (
            '<div style="margin-top:10px;display:flex;gap:12px">'
            + (f'<div style="flex:1;padding:8px 12px;background:#0A1020;border-radius:6px">'
               f'<div style="font-size:9px;color:#475569;letter-spacing:1px;margin-bottom:3px">RESISTANCE</div>'
               f'<div style="font-size:13px;font-family:monospace;color:#F5365C">{nearest_res}</div></div>' if nearest_res else "")
            + (f'<div style="flex:1;padding:8px 12px;background:#0A1020;border-radius:6px">'
               f'<div style="font-size:9px;color:#475569;letter-spacing:1px;margin-bottom:3px">SUPPORT</div>'
               f'<div style="font-size:13px;font-family:monospace;color:#00D68F">{nearest_sup}</div></div>' if nearest_sup else "")
            + '</div>'
        )

    return (
        f'<div style="display:flex;gap:12px;margin-bottom:8px">'
        f'<div style="flex:1;padding:10px 14px;background:#0A1020;border-radius:6px">'
        f'<div style="font-size:9px;color:#475569;letter-spacing:1px;margin-bottom:4px">TREND</div>'
        f'<div style="font-size:13px;font-weight:700;color:{t_col}">{trend}</div>'
        f'</div>'
        f'<div style="flex:1;padding:10px 14px;background:#0A1020;border-radius:6px">'
        f'<div style="font-size:9px;color:#475569;letter-spacing:1px;margin-bottom:4px">CHANNEL</div>'
        f'<div style="font-size:13px;font-weight:700;color:{c_col}">{channel}</div>'
        f'</div></div>'
        f'{event_html}{levels_html}'
    )


def send_trade_executed_email(signal: dict, order_id: str) -> bool:
    """Send a rich execution email: WHY we took it + THE PLAN + INVALIDATION."""
    plan     = signal.get("trade_plan") or {}
    conf     = signal.get("confluence") or {}
    exec_    = signal.get("execution") or {}

    pair_raw  = plan.get("pair") or signal.get("pair") or ""
    pair      = pair_raw.replace("_", "/")
    dirn      = (plan.get("direction") or conf.get("direction") or "").upper()
    entry     = plan.get("entry_price", "—")
    sl        = plan.get("stop_loss", "—")
    tp        = plan.get("take_profit_1") or plan.get("take_profit", "—")
    lots      = plan.get("lot_size", "—")
    risk      = plan.get("risk_amount_usd", "—")
    rr        = plan.get("risk_reward", "—")
    ts        = (exec_.get("executed_at") or "")[:19].replace("T", " ") + " UTC"
    dir_col   = "#00D68F" if dirn == "BULLISH" else "#F5365C"

    score        = conf.get("score", "—")
    max_score    = conf.get("max_score", "—")
    dissent      = conf.get("dissenting_timeframes") or []
    neutral      = conf.get("neutral_timeframes") or []
    ref_tf       = plan.get("reference_timeframe", "H1")
    invalidation = plan.get("invalidation_note", "")
    sl_pips      = plan.get("sl_pips", "—")

    conf_rows  = _confluence_table_html(conf) if conf.get("votes") else (
        f'<tr><td colspan="2" style="padding:10px 14px;color:#475569;font-size:12px">'
        f'Score: {score}/{max_score}</td></tr>'
    )
    dissent_html = (
        f'<div style="margin-top:8px;font-size:11px;color:#FFAA00">'
        f'⚠ Dissenting: {", ".join(dissent)}</div>' if dissent else ""
    )

    # ── Market structure section (from embedded analysis if cached) ────
    structure_html = ""
    try:
        from tools.utils.file_io import get_analysis_path, file_exists, read_json as _rj
        apath = get_analysis_path(pair_raw)
        if file_exists(apath):
            analysis = _rj(apath)
            ref_data = (analysis.get("timeframes") or {}).get(ref_tf, {})
            if ref_data:
                structure_html = f"""
    <div style="margin-bottom:20px">
      <div style="font-size:10px;font-weight:700;letter-spacing:2px;color:#3B7BF6;margin-bottom:10px">
        MARKET STRUCTURE ({ref_tf} — Reference Timeframe)
      </div>
      {_structure_html(ref_data, dirn.lower())}
    </div>"""
    except Exception:
        pass

    # ── What to watch ─────────────────────────────────────────────────
    watch_items = []
    for tf in neutral:
        watch_items.append(f"<strong>{tf}</strong> is neutral — wait for {tf} confirmation before scaling")
    for tf in dissent:
        watch_items.append(f"<strong>{tf}</strong> voted against — higher-risk setup, reduce size if unsure")
    if not watch_items:
        watch_items.append("All timeframes aligned — clean setup, full position size is appropriate")
    watch_html = "".join(
        f'<li style="margin-bottom:5px;font-size:12px;color:#94A3B8">{w}</li>'
        for w in watch_items
    )

    # ── Invalidation note ─────────────────────────────────────────────
    inval_html = ""
    if invalidation:
        inval_html = f"""
    <div style="background:#1A100A;border:1px solid #F5365C33;border-left:3px solid #FFAA00;
                border-radius:8px;padding:12px 16px;margin-bottom:20px">
      <div style="font-size:10px;font-weight:700;letter-spacing:2px;color:#FFAA00;margin-bottom:4px">
        INVALIDATION — SETUP IS CANCELLED IF
      </div>
      <div style="font-size:12px;color:#94A3B8">{invalidation}</div>
    </div>"""

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#070A12;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#EEF2FF">
<div style="max-width:640px;margin:0 auto;padding:24px 16px">

  <!-- Header -->
  <div style="background:linear-gradient(135deg,#0D1117,#0D1A10);border:1px solid #1A3525;
              border-left:4px solid #00D68F;border-radius:14px;padding:20px 24px;margin-bottom:20px">
    <div style="font-size:18px;font-weight:900;color:#00D68F;letter-spacing:1px">✓ Trade Executed</div>
    <div style="font-size:14px;color:#EEF2FF;margin-top:6px;font-weight:700">
      {pair} · <span style="color:{dir_col}">{dirn}</span>
    </div>
    <div style="font-size:11px;color:#475569;margin-top:4px">Order ID: {order_id} · {ts}</div>
  </div>

  <!-- WHY WE TOOK THIS TRADE -->
  <div style="background:#101520;border:1px solid #1A2035;border-radius:12px;padding:18px 20px;margin-bottom:16px">
    <div style="font-size:11px;font-weight:700;letter-spacing:2px;color:#3B7BF6;margin-bottom:14px">
      WHY WE TOOK THIS TRADE
    </div>

    <!-- Consensus summary -->
    <div style="background:#0A1020;border-radius:8px;padding:10px 14px;margin-bottom:14px">
      <div style="font-size:12px;color:#94A3B8">
        <strong style="color:#EEF2FF">{score}/{max_score}</strong> timeframes voted
        <strong style="color:{dir_col}">{dirn}</strong> — confluence threshold passed ✓
      </div>
      {dissent_html}
    </div>

    <!-- TF votes table -->
    <div style="margin-bottom:14px">
      <div style="font-size:10px;color:#475569;letter-spacing:1.5px;margin-bottom:6px">TIMEFRAME BREAKDOWN</div>
      <table width="100%" cellpadding="0" cellspacing="0"
             style="border-collapse:collapse;border:1px solid #1A2035;border-radius:8px;overflow:hidden">
        <thead>
          <tr style="background:#0A1020">
            <th style="padding:6px 14px;text-align:left;font-size:9px;color:#475569;letter-spacing:1.5px">TIMEFRAME</th>
            <th style="padding:6px 14px;text-align:left;font-size:9px;color:#475569;letter-spacing:1.5px">VOTE</th>
          </tr>
        </thead>
        <tbody>{conf_rows}</tbody>
      </table>
    </div>

    <!-- Setup quality -->
    <div style="margin-top:8px;font-size:12px;color:#94A3B8">
      SL placed <strong style="color:#EEF2FF">{sl_pips} pips</strong> away at market structure
      · Reference timeframe: <strong style="color:#EEF2FF">{ref_tf}</strong>
    </div>
    {structure_html}
  </div>

  <!-- WHAT TO WATCH -->
  <div style="background:#0D1520;border:1px solid #1A2035;border-radius:10px;padding:16px 20px;margin-bottom:16px">
    <div style="font-size:10px;font-weight:700;letter-spacing:2px;color:#3B7BF6;margin-bottom:8px">WHAT TO WATCH</div>
    <ul style="margin:0;padding-left:18px">{watch_html}</ul>
  </div>

  <!-- THE PLAN -->
  <div style="background:#101520;border:1px solid #1A2035;border-radius:12px;overflow:hidden;margin-bottom:16px">
    <div style="padding:12px 16px;border-bottom:1px solid #1A2035">
      <span style="font-size:11px;font-weight:700;letter-spacing:2px;color:#94A3B8">THE PLAN</span>
    </div>
    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse">
      <tr><td style="padding:10px 16px;color:#475569;font-size:12px;border-bottom:1px solid #1A2035;width:42%">Entry Price</td>
          <td style="padding:10px 16px;font-size:13px;font-family:monospace;border-bottom:1px solid #1A2035">{entry}</td></tr>
      <tr><td style="padding:10px 16px;color:#475569;font-size:12px;border-bottom:1px solid #1A2035">Stop Loss</td>
          <td style="padding:10px 16px;font-size:13px;font-family:monospace;color:#F5365C;border-bottom:1px solid #1A2035">{sl} <span style="font-size:11px;color:#475569">({sl_pips}p)</span></td></tr>
      <tr><td style="padding:10px 16px;color:#475569;font-size:12px;border-bottom:1px solid #1A2035">Take Profit</td>
          <td style="padding:10px 16px;font-size:13px;font-family:monospace;color:#00D68F;border-bottom:1px solid #1A2035">{tp}</td></tr>
      <tr><td style="padding:10px 16px;color:#475569;font-size:12px;border-bottom:1px solid #1A2035">Lot Size</td>
          <td style="padding:10px 16px;font-size:13px;border-bottom:1px solid #1A2035">{lots} lots</td></tr>
      <tr><td style="padding:10px 16px;color:#475569;font-size:12px;border-bottom:1px solid #1A2035">Risk / Reward</td>
          <td style="padding:10px 16px;font-size:13px;border-bottom:1px solid #1A2035">{rr}:1</td></tr>
      <tr><td style="padding:10px 16px;color:#475569;font-size:12px">Risk Amount</td>
          <td style="padding:10px 16px;font-size:13px;color:#FFAA00;font-weight:700">${risk}</td></tr>
    </table>
  </div>

  {inval_html}

  <div style="text-align:center;font-size:10px;color:#475569">
    NEXUS Trade · Practice Account · Automated
  </div>
</div>
</body></html>"""

    return send(f"Trade Placed — {pair} {dirn}", html)


def send_trade_win_email(trade: dict) -> bool:
    """Send an immediate win notification when a trade closes in profit."""
    pair     = (trade.get("pair") or "").replace("_", "/")
    pnl      = trade.get("pnl_usd", 0) or 0
    r        = trade.get("r_multiple", 0) or 0
    dirn     = (trade.get("direction") or "").upper()
    entry    = trade.get("entry_price", "—")
    tp       = trade.get("take_profit", "—")
    exit_p   = trade.get("exit_price", "—")
    rr       = trade.get("risk_reward", "—")
    dur_note = ""
    try:
        opened = datetime.fromisoformat((trade.get("executed_at") or "").replace("Z", "+00:00"))
        closed = datetime.fromisoformat((trade.get("closed_at") or "").replace("Z", "+00:00"))
        mins   = int((closed - opened).total_seconds() / 60)
        if mins < 60:
            dur_note = f"{mins} min"
        else:
            dur_note = f"{mins//60}h {mins%60}m"
    except Exception:
        pass

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:24px;background:#070A12;font-family:-apple-system,sans-serif;color:#EEF2FF;max-width:600px">
  <div style="background:linear-gradient(135deg,#0D1A10,#091A09);border:1px solid #1A3525;
              border-left:4px solid #00D68F;border-radius:12px;padding:20px 24px;margin-bottom:20px">
    <div style="font-size:20px;font-weight:900;color:#00D68F">🏆 Trade Won!</div>
    <div style="font-size:14px;color:#EEF2FF;margin-top:6px">
      {pair} · {dirn} · +${pnl:.2f} <span style="color:#7B61FF">({r:+.2f}R)</span>
    </div>
    {f'<div style="font-size:11px;color:#475569;margin-top:4px">Duration: {dur_note}</div>' if dur_note else ""}
  </div>

  <div style="background:#101520;border:1px solid #1A2035;border-radius:10px;overflow:hidden;margin-bottom:16px">
    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse">
      <tr><td style="padding:10px 16px;color:#475569;font-size:12px;border-bottom:1px solid #1A2035;width:42%">Entry</td>
          <td style="padding:10px 16px;font-size:13px;font-family:monospace;border-bottom:1px solid #1A2035">{entry}</td></tr>
      <tr><td style="padding:10px 16px;color:#475569;font-size:12px;border-bottom:1px solid #1A2035">Exit</td>
          <td style="padding:10px 16px;font-size:13px;font-family:monospace;color:#00D68F;border-bottom:1px solid #1A2035">{exit_p}</td></tr>
      <tr><td style="padding:10px 16px;color:#475569;font-size:12px;border-bottom:1px solid #1A2035">Take Profit Target</td>
          <td style="padding:10px 16px;font-size:13px;font-family:monospace;border-bottom:1px solid #1A2035">{tp}</td></tr>
      <tr><td style="padding:10px 16px;color:#475569;font-size:12px">R/R</td>
          <td style="padding:10px 16px;font-size:13px">{rr}:1</td></tr>
    </table>
  </div>

  <div style="background:#091A09;border:1px solid #00D68F22;border-radius:8px;padding:14px 18px;text-align:center">
    <div style="font-size:11px;color:#475569;letter-spacing:2px;margin-bottom:6px">PROFIT CAPTURED</div>
    <div style="font-size:28px;font-weight:900;color:#00D68F">+${pnl:.2f}</div>
    <div style="font-size:14px;color:#7B61FF;margin-top:4px">{r:+.2f}R achieved</div>
  </div>

  <div style="text-align:center;font-size:10px;color:#475569;margin-top:20px">
    NEXUS Trade · Practice Account
  </div>
</body></html>"""

    return send(f"Win! — {pair} +${pnl:.2f}", html)


def send_trade_status_email(trade: dict, current_price: float, milestone: str) -> bool:
    """
    Send a mid-trade status update when price hits a meaningful milestone.
    milestone: "TP50" | "TP80" | "SL50" | "SL80"
    """
    pair   = (trade.get("pair") or "").replace("_", "/")
    dirn   = (trade.get("direction") or "").upper()
    entry  = float(trade.get("entry_price") or 0)
    sl     = float(trade.get("stop_loss") or 0)
    tp     = float(trade.get("take_profit") or 0)
    rr     = trade.get("risk_reward", "—")

    is_long    = dirn == "BULLISH"
    tp_dist    = abs(tp - entry)
    sl_dist    = abs(sl - entry)
    tp_progress = abs(current_price - entry) / tp_dist * 100 if tp_dist else 0
    sl_progress = abs(current_price - entry) / sl_dist * 100 if sl_dist else 0

    moving_toward_tp = (is_long and current_price > entry) or (not is_long and current_price < entry)

    if "TP" in milestone:
        pct = int(milestone[2:])
        icon   = "📈" if moving_toward_tp else "📉"
        banner_col = "#00D68F"
        headline   = f"{icon} Trade is {pct}% of the way to Take Profit"
        sub        = "Performing as planned — moving in the right direction."
        detail     = f"Price is {tp_progress:.0f}% of the distance from entry to TP."
    else:
        pct = int(milestone[2:])
        icon   = "⚠" if pct < 80 else "🚨"
        banner_col = "#FFAA00" if pct < 80 else "#F5365C"
        headline   = f"{icon} Trade is {pct}% toward Stop Loss"
        sub        = "Not going as planned — price moving against the position." if pct < 80 \
                     else "URGENT: Trade near stop loss — monitor closely!"
        detail     = f"Price is {sl_progress:.0f}% of the distance from entry to SL."

    price_bar_tp = f"{min(tp_progress, 100):.0f}%"
    price_bar_sl = f"{min(sl_progress, 100):.0f}%"

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:24px;background:#070A12;font-family:-apple-system,sans-serif;color:#EEF2FF;max-width:600px">
  <div style="background:#101520;border:1px solid #1A2035;border-left:4px solid {banner_col};
              border-radius:12px;padding:18px 22px;margin-bottom:20px">
    <div style="font-size:16px;font-weight:800;color:{banner_col}">{headline}</div>
    <div style="font-size:13px;color:#94A3B8;margin-top:4px">{pair} · {dirn}</div>
    <div style="font-size:12px;color:#475569;margin-top:4px">{sub}</div>
  </div>

  <div style="background:#101520;border:1px solid #1A2035;border-radius:10px;
              overflow:hidden;margin-bottom:16px">
    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse">
      <tr><td style="padding:10px 16px;color:#475569;font-size:12px;border-bottom:1px solid #1A2035;width:42%">Current Price</td>
          <td style="padding:10px 16px;font-size:13px;font-family:monospace;font-weight:700;
                     color:{banner_col};border-bottom:1px solid #1A2035">{current_price}</td></tr>
      <tr><td style="padding:10px 16px;color:#475569;font-size:12px;border-bottom:1px solid #1A2035">Entry</td>
          <td style="padding:10px 16px;font-size:13px;font-family:monospace;border-bottom:1px solid #1A2035">{entry}</td></tr>
      <tr><td style="padding:10px 16px;color:#475569;font-size:12px;border-bottom:1px solid #1A2035">Stop Loss</td>
          <td style="padding:10px 16px;font-size:13px;font-family:monospace;color:#F5365C;border-bottom:1px solid #1A2035">{sl}</td></tr>
      <tr><td style="padding:10px 16px;color:#475569;font-size:12px">Take Profit</td>
          <td style="padding:10px 16px;font-size:13px;font-family:monospace;color:#00D68F">{tp}</td></tr>
    </table>
  </div>

  <div style="background:#0A1020;border-radius:8px;padding:14px 18px;margin-bottom:16px">
    <div style="font-size:10px;color:#475569;letter-spacing:1.5px;margin-bottom:10px">TRADE PROGRESS</div>
    <div style="margin-bottom:8px">
      <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:4px">
        <span style="color:#00D68F">→ Take Profit</span>
        <span style="color:#00D68F">{price_bar_tp}</span>
      </div>
      <div style="height:6px;background:#1A2035;border-radius:3px">
        <div style="height:6px;background:#00D68F;border-radius:3px;width:{price_bar_tp}"></div>
      </div>
    </div>
    <div>
      <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:4px">
        <span style="color:#F5365C">→ Stop Loss</span>
        <span style="color:#F5365C">{price_bar_sl}</span>
      </div>
      <div style="height:6px;background:#1A2035;border-radius:3px">
        <div style="height:6px;background:#F5365C;border-radius:3px;width:{price_bar_sl}"></div>
      </div>
    </div>
  </div>

  <div style="text-align:center;font-size:10px;color:#475569">
    NEXUS Trade · Practice Account · {detail}
  </div>
</body></html>"""

    label = "TP Alert" if "TP" in milestone else "SL Warning"
    return send(f"{label} — {pair} {dirn} ({milestone})", html)


def send_session_close_email(session: str, open_trades: list[dict], executed_today: list[dict]) -> bool:
    """Send an end-of-session summary: what's open, what ran, P/L so far today."""
    session_times = {
        "ASIAN":  "00:00 – 09:00 UTC",
        "LONDON": "07:00 – 16:00 UTC",
        "NEW YORK": "12:00 – 21:00 UTC",
    }
    session_colors = {
        "ASIAN": "#3B7BF6",
        "LONDON": "#FFAA00",
        "NEW YORK": "#00D68F",
    }
    s_upper = session.upper()
    time_range = session_times.get(s_upper, "")
    s_color    = session_colors.get(s_upper, "#94A3B8")
    now_str    = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")

    # Build open trades table
    if open_trades:
        open_rows = ""
        for t in open_trades:
            pair   = (t.get("pair") or t.get("instrument") or "—").replace("_", "/")
            dirn   = (t.get("direction") or ("LONG" if int(t.get("currentUnits", 0)) > 0 else "SHORT")).upper()
            entry  = t.get("entry_price") or t.get("price") or "—"
            pnl    = float(t.get("unrealizedPL") or t.get("pnl_usd") or 0)
            pnl_col = "#00D68F" if pnl >= 0 else "#F5365C"
            open_rows += (
                f'<tr style="border-bottom:1px solid #1A2035">'
                f'<td style="padding:8px 14px;font-weight:700">{pair}</td>'
                f'<td style="padding:8px 14px;font-size:11px;color:{"#00D68F" if "BULL" in dirn or dirn=="LONG" else "#F5365C"}">{dirn}</td>'
                f'<td style="padding:8px 14px;font-family:monospace">{entry}</td>'
                f'<td style="padding:8px 14px;font-weight:700;color:{pnl_col}">{"+$" if pnl>=0 else "-$"}{abs(pnl):.2f}</td>'
                f'</tr>'
            )
        open_html = f"""
      <div style="background:#101520;border:1px solid #1A2035;border-radius:10px;overflow:hidden;margin-bottom:16px">
        <div style="padding:10px 14px;border-bottom:1px solid #1A2035;font-size:10px;font-weight:700;letter-spacing:2px;color:#94A3B8">OPEN POSITIONS ({len(open_trades)})</div>
        <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:12px">
          <thead><tr style="background:#0A1020">
            <th style="padding:6px 14px;text-align:left;font-size:9px;color:#475569;letter-spacing:1px">PAIR</th>
            <th style="padding:6px 14px;text-align:left;font-size:9px;color:#475569;letter-spacing:1px">DIR</th>
            <th style="padding:6px 14px;text-align:left;font-size:9px;color:#475569;letter-spacing:1px">ENTRY</th>
            <th style="padding:6px 14px;text-align:left;font-size:9px;color:#475569;letter-spacing:1px">LIVE P/L</th>
          </tr></thead>
          <tbody>{open_rows}</tbody>
        </table>
      </div>"""
    else:
        open_html = '<div style="background:#101520;border:1px solid #1A2035;border-radius:10px;padding:16px 20px;margin-bottom:16px;color:#475569;font-size:12px">No open positions at session close.</div>'

    # Trades executed today
    today_pnl = sum(float(t.get("pnl_usd") or 0) for t in executed_today if t.get("outcome"))
    p_col = "#00D68F" if today_pnl >= 0 else "#F5365C"
    exec_rows = ""
    for t in executed_today:
        pair    = (t.get("pair") or "—").replace("_", "/")
        outcome = (t.get("outcome") or "open").upper()
        pnl     = float(t.get("pnl_usd") or 0)
        o_col   = "#00D68F" if outcome == "WIN" else ("#F5365C" if outcome == "LOSS" else "#FFAA00")
        exec_rows += (
            f'<tr style="border-bottom:1px solid #1A2035">'
            f'<td style="padding:8px 14px;font-weight:700">{pair}</td>'
            f'<td style="padding:8px 14px;color:{o_col};font-weight:700;font-size:11px">{outcome}</td>'
            f'<td style="padding:8px 14px;color:{"#00D68F" if pnl>=0 else "#F5365C"};font-weight:700">{"+$" if pnl>=0 else "-$"}{abs(pnl):.2f}</td>'
            f'</tr>'
        )
    exec_html = ""
    if executed_today:
        exec_html = f"""
      <div style="background:#101520;border:1px solid #1A2035;border-radius:10px;overflow:hidden;margin-bottom:16px">
        <div style="padding:10px 14px;border-bottom:1px solid #1A2035;font-size:10px;font-weight:700;letter-spacing:2px;color:#94A3B8">TODAY'S TRADES ({len(executed_today)})</div>
        <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:12px">
          <thead><tr style="background:#0A1020">
            <th style="padding:6px 14px;text-align:left;font-size:9px;color:#475569;letter-spacing:1px">PAIR</th>
            <th style="padding:6px 14px;text-align:left;font-size:9px;color:#475569;letter-spacing:1px">RESULT</th>
            <th style="padding:6px 14px;text-align:left;font-size:9px;color:#475569;letter-spacing:1px">P/L</th>
          </tr></thead>
          <tbody>{exec_rows}</tbody>
        </table>
        <div style="padding:10px 14px;border-top:1px solid #1A2035;font-size:12px">
          Today P/L: <strong style="color:{p_col}">{"+$" if today_pnl>=0 else "-$"}{abs(today_pnl):.2f}</strong>
        </div>
      </div>"""

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#070A12;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#EEF2FF">
<div style="max-width:600px;margin:0 auto;padding:24px 16px">

  <div style="background:linear-gradient(135deg,#0D1117,#131929);border:1px solid #1A2035;
              border-left:4px solid {s_color};border-radius:14px;padding:20px 24px;margin-bottom:20px">
    <div style="font-size:11px;font-weight:700;letter-spacing:3px;color:{s_color};margin-bottom:4px">SESSION CLOSED</div>
    <div style="font-size:20px;font-weight:900">{s_upper} SESSION</div>
    <div style="font-size:11px;color:#475569;margin-top:4px">{time_range} · {now_str}</div>
  </div>

  {open_html}
  {exec_html}

  <div style="text-align:center;font-size:10px;color:#475569;margin-top:16px">
    NEXUS Trade · Practice Account · Session Report
  </div>
</div>
</body></html>"""

    return send(f"{s_upper} Session Closed — {len(open_trades)} open", html)


def send_30day_report(trades: list[dict], summary: dict,
                      backtest_results: list[dict] | None = None) -> bool:
    html = build_html("30-Day Trading Report", trades, summary, backtest_results)
    return send("30-Day Performance Report", html)


def send_weekly_report(trades: list[dict], summary: dict) -> bool:
    html = build_html("Weekly Report", trades, summary)
    return send("Weekly Performance Summary", html)
