"""
Calculate position size (lot size) based on account risk.

Formula:
    risk_amount  = account_balance × (risk_percent / 100)
    pip_value    = pip_value_per_lot (depends on pair and account currency)
    lot_size     = risk_amount / (sl_pips × pip_value_per_lot)

Pip value per standard lot (100,000 units) in USD:
  - Quote currency USD (EUR/USD, GBP/USD, AUD/USD):  $10.00 per pip
  - Base currency USD  (USD/JPY, USD/CHF, USD/CAD):  10 / current_price per pip
  - Cross pair         (EUR/GBP, GBP/JPY, EUR/JPY):  approximate via quote pip value

Lot size is capped at 100 and rounded to 2 decimal places.
"""

from tools.utils.logger import get_logger

log = get_logger(__name__)

# Pairs where USD is the quote (pip value = $10/lot fixed)
_USD_QUOTE_PAIRS = {
    "EUR_USD", "GBP_USD", "AUD_USD", "NZD_USD",
}

# Pairs where USD is the base (pip value = 10 / price per lot)
_USD_BASE_PAIRS = {
    "USD_JPY", "USD_CHF", "USD_CAD", "USD_SGD",
}

_LOT_UNITS = 100_000  # 1 standard lot
_MAX_LOT   = 100.0
_MIN_LOT   = 0.01


def pip_value_per_lot(pair: str, price: float) -> float:
    """
    Return the USD value of 1 pip per standard lot for the given pair.

    Args:
        pair:  e.g. "EUR_USD"
        price: Current mid price (used for USD-base pairs).
    """
    if pair in _USD_QUOTE_PAIRS:
        return 10.0  # always $10/pip/lot for USD-quote majors
    elif pair in _USD_BASE_PAIRS:
        if pair == "USD_JPY":
            return round(1_000 / price, 4)  # 0.01 pip × 100,000 / price
        return round(10.0 / price, 4)
    else:
        # Cross pair — approximate: 1 pip ≈ $10 (acceptable for initial sizing)
        log.warning(
            f"Pair {pair} is a cross pair. Using approximate pip value of $10/lot. "
            "Refine for production."
        )
        return 10.0


def calculate_lot_size(
    account_balance: float,
    risk_percent: float,
    sl_pips: float,
    pair: str,
    entry_price: float,
) -> dict:
    """
    Calculate the lot size for a trade.

    Args:
        account_balance: Account equity in USD.
        risk_percent:    Percentage of balance to risk (e.g. 1.0 for 1%).
        sl_pips:         Stop loss distance in pips.
        pair:            Instrument name.
        entry_price:     Current price (used for pip value on USD-base pairs).

    Returns:
        Dict with lot_size, risk_amount, pip_val, and derived fields.
    """
    if sl_pips <= 0:
        raise ValueError(f"sl_pips must be positive, got {sl_pips}")
    if not (0 < risk_percent <= 10):
        raise ValueError(f"risk_percent must be between 0 and 10, got {risk_percent}")
    if account_balance <= 0:
        raise ValueError(f"account_balance must be positive, got {account_balance}")

    risk_amount = round(account_balance * (risk_percent / 100), 2)
    pip_val = pip_value_per_lot(pair, entry_price)
    raw_lots = risk_amount / (sl_pips * pip_val)

    lot_size = max(_MIN_LOT, min(_MAX_LOT, round(raw_lots, 2)))

    result = {
        "lot_size": lot_size,
        "risk_amount_usd": risk_amount,
        "pip_value_per_lot": pip_val,
        "sl_pips": sl_pips,
        "risk_percent": risk_percent,
        "account_balance": account_balance,
    }

    log.info(
        f"Lot size: {lot_size}  "
        f"(risk=${risk_amount:.2f}, SL={sl_pips}pips, pip_val=${pip_val}/lot)"
    )
    return result
