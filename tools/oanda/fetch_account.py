"""
Fetch OANDA account details: balance, margin, open positions.

Usage (CLI):
    python -m tools.oanda.fetch_account
"""

import os

from dotenv import load_dotenv
from oandapyV20 import API
from oandapyV20.endpoints import accounts

from tools.utils.logger import get_logger

load_dotenv()
log = get_logger(__name__)


def _build_client(env: str) -> API:
    api_key = os.getenv("OANDA_API_KEY")
    if not api_key:
        raise EnvironmentError("OANDA_API_KEY not set in .env")
    environment = "practice" if env == "practice" else "live"
    return API(access_token=api_key, environment=environment)


def fetch_account(env: str | None = None) -> dict:
    """
    Fetch account summary from OANDA.

    Returns:
        Dict with balance, NAV, margin used/available, open trade count.
    """
    resolved_env = env or os.getenv("OANDA_ENV", "practice")
    account_id = os.getenv("OANDA_ACCOUNT_ID")
    if not account_id:
        raise EnvironmentError("OANDA_ACCOUNT_ID not set in .env")

    client = _build_client(resolved_env)
    req = accounts.AccountSummary(accountID=account_id)
    client.request(req)

    summary = req.response.get("account", {})
    result = {
        "account_id": summary.get("id"),
        "balance": float(summary.get("balance", 0)),
        "nav": float(summary.get("NAV", 0)),
        "margin_used": float(summary.get("marginUsed", 0)),
        "margin_available": float(summary.get("marginAvailable", 0)),
        "open_trade_count": int(summary.get("openTradeCount", 0)),
        "currency": summary.get("currency", "USD"),
        "env": resolved_env,
    }

    log.info(
        f"Account {result['account_id']} | "
        f"Balance: {result['balance']} {result['currency']} | "
        f"Open trades: {result['open_trade_count']}"
    )
    return result


if __name__ == "__main__":
    account = fetch_account()
    import json
    print(json.dumps(account, indent=2))
