"""
Fetch the list of tradeable instruments from OANDA.
Used to validate pair names before running analysis.

Usage (CLI):
    python -m tools.oanda.fetch_instruments
    python -m tools.oanda.fetch_instruments --check EUR_USD
"""

import argparse
import os

from dotenv import load_dotenv
from oandapyV20 import API
from oandapyV20.endpoints import accounts

from tools.utils.logger import get_logger

load_dotenv()
log = get_logger(__name__)

_INSTRUMENTS_CACHE: list[str] | None = None


def _build_client(env: str) -> API:
    api_key = os.getenv("OANDA_API_KEY")
    if not api_key:
        raise EnvironmentError("OANDA_API_KEY not set in .env")
    environment = "practice" if env == "practice" else "live"
    return API(access_token=api_key, environment=environment)


def fetch_instruments(env: str | None = None) -> list[str]:
    """
    Return list of all tradeable instrument names (e.g. ["EUR_USD", "GBP_USD", ...]).
    Results are cached in-process to avoid repeat API calls.
    """
    global _INSTRUMENTS_CACHE
    if _INSTRUMENTS_CACHE is not None:
        return _INSTRUMENTS_CACHE

    resolved_env = env or os.getenv("OANDA_ENV", "practice")
    account_id = os.getenv("OANDA_ACCOUNT_ID")
    if not account_id:
        raise EnvironmentError("OANDA_ACCOUNT_ID not set in .env")

    client = _build_client(resolved_env)
    req = accounts.AccountInstruments(accountID=account_id)
    client.request(req)

    instruments_data = req.response.get("instruments", [])
    names = [i["name"] for i in instruments_data if i.get("type") == "CURRENCY"]
    _INSTRUMENTS_CACHE = sorted(names)

    log.info(f"Fetched {len(names)} tradeable currency pairs from OANDA")
    return _INSTRUMENTS_CACHE


def is_valid_pair(pair: str, env: str | None = None) -> bool:
    """Return True if the pair is in OANDA's instrument list."""
    instruments = fetch_instruments(env=env)
    return pair in instruments


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List OANDA tradeable pairs")
    parser.add_argument("--check", default=None, help="Check if a specific pair is valid")
    args = parser.parse_args()

    pairs = fetch_instruments()
    if args.check:
        valid = args.check in pairs
        print(f"{args.check}: {'VALID' if valid else 'NOT FOUND'}")
    else:
        for p in pairs:
            print(p)
