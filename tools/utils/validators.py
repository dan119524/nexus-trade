"""
Input validation helpers used by tool scripts.
"""

VALID_GRANULARITIES = {
    "M1", "M2", "M5", "M10", "M15", "M30",
    "H1", "H4",
    "D", "W", "M",
}
VALID_ENVS = {"practice", "live"}


def validate_granularity(granularity: str) -> None:
    if granularity not in VALID_GRANULARITIES:
        raise ValueError(
            f"Invalid granularity '{granularity}'. "
            f"Must be one of: {sorted(VALID_GRANULARITIES)}"
        )


def validate_env(env: str) -> None:
    if env not in VALID_ENVS:
        raise ValueError(
            f"Invalid OANDA env '{env}'. Must be 'practice' or 'live'."
        )


def validate_pair_format(pair: str) -> None:
    """Basic format check — OANDA pairs use underscore, e.g. EUR_USD."""
    if "_" not in pair or len(pair) < 6:
        raise ValueError(
            f"Invalid pair format '{pair}'. Expected format: BASE_QUOTE (e.g. EUR_USD)."
        )


def validate_risk_percent(risk_percent: float) -> None:
    if not (0 < risk_percent <= 2):  # FR9 cap
        raise ValueError(
            f"risk_percent must be greater than 0 and at most 2. Got: {risk_percent}"
        )
