"""TradePlan: the plan for a valid signal (Phase 05 entity)."""

from tools.models.account import Account
from tools.models.buy_direction import BuyDirection
from tools.models.candle import to_positive_price, validate_timeframe
from tools.models.sell_direction import SellDirection
from tools.models.signal import Signal
from tools.models.trade_setup import TradeSetup

MIN_REWARD_TO_RISK = 2


class TradePlan:
    """A trade setup owned by the plan, plus TP2, lot size, risk amount, and reference timeframe (FR9).

    The plan creates its own TradeSetup, with a BuyDirection or SellDirection from the signal.
    """

    def __init__(self, signal, account, entry, stop_loss, take_profit_1, take_profit_2,
                 lot_size, risk_amount, reference_timeframe):
        if not isinstance(signal, Signal):
            raise ValueError(f"signal must be a Signal, got {signal!r}")
        if not signal.is_valid():
            raise ValueError("a trade plan needs a valid signal")
        if not isinstance(account, Account):
            raise ValueError(f"account must be an Account, got {account!r}")
        self._signal = signal
        self._account = account
        direction = BuyDirection() if signal.trade_direction() == "buy" else SellDirection()
        self._setup = TradeSetup(signal.pair, direction, entry, stop_loss, take_profit_1)
        if round(self._setup.reward_to_risk(), 2) < MIN_REWARD_TO_RISK:
            raise ValueError("reward-to-risk to TP1 must be at least 2")
        take_profit_2 = to_positive_price(take_profit_2, "take profit 2")
        if not direction.is_beyond(take_profit_2, self._setup.take_profit):
            raise ValueError(f"a {direction.name} needs TP2 beyond TP1")
        self._take_profit_2 = take_profit_2
        self._lot_size = to_positive_price(lot_size, "lot size")
        self._risk_amount = to_positive_price(risk_amount, "risk amount")
        if self._risk_amount > account.max_risk_amount():
            raise ValueError("risk amount must not exceed the account's risk percent of its balance")
        self._reference_timeframe = validate_timeframe(reference_timeframe)

    @property
    def signal(self):
        return self._signal

    @property
    def account(self):
        return self._account

    @property
    def setup(self):
        return self._setup

    @property
    def take_profit_2(self):
        return self._take_profit_2

    @property
    def lot_size(self):
        return self._lot_size

    @property
    def risk_amount(self):
        return self._risk_amount

    @property
    def reference_timeframe(self):
        return self._reference_timeframe
