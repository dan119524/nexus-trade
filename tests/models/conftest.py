"""Shared CurrencyPair fixtures for the tests in tests/models/. Fixed prices only."""

import pytest

from tools.models import CurrencyPair


@pytest.fixture
def eur_usd():
    return CurrencyPair("EUR_USD", [(1.0850, 1.0800), (1.0900, 1.0840)])


@pytest.fixture
def gbp_usd():
    return CurrencyPair("GBP_USD", [(1.2800, 1.2750), (1.2760, 1.2700)])


@pytest.fixture
def usd_jpy():
    return CurrencyPair("USD_JPY", [(150.20, 149.80), (150.60, 149.70)])
