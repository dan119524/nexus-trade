"""TradePlan: the plan for a valid signal (Phase 05 entity, Phase 06 derives its risk and reference timeframe)."""

from tools.models.account import Account
from tools.models.candle import to_positive_price
from tools.models.signal import Signal
from tools.models.trade_setup import TradeSetup

MIN_REWARD_TO_RISK = 2
LOT_STEP = 0.01


class TradePlan:
    """A trade setup owned by the plan, plus TP2 and a lot size (FR9).

    The plan creates its own TradeSetup with its signal's trade direction. Its risk amount comes
    from its lot size, and its reference timeframe comes from its signal.
    """

    def __init__(self, signal, account, entry, stop_loss, take_profit_1, take_profit_2, lot_size):
        if not isinstance(signal, Signal):
            raise ValueError(f"signal must be a Signal, got {signal!r}")
        if not signal.is_valid():
            raise ValueError("a trade plan needs a valid signal")
        if not isinstance(account, Account):
            raise ValueError(f"account must be an Account, got {account!r}")
        if account.currency != "USD":
            raise ValueError(f"a trade plan needs a USD account, got {account.currency!r}")
        self._signal = signal
        self._account = account
        direction = signal.trade_direction()
        self._setup = TradeSetup(signal.pair, direction, entry, stop_loss, take_profit_1)
        if round(self._setup.reward_to_risk(), 2) < MIN_REWARD_TO_RISK:
            raise ValueError("reward-to-risk to TP1 must be at least 2")
        take_profit_2 = to_positive_price(take_profit_2, "take profit 2")
        if not direction.is_beyond(take_profit_2, self._setup.take_profit):
            raise ValueError(f"a {direction.name} needs TP2 beyond TP1")
        self._take_profit_2 = take_profit_2
        self._lot_size = to_positive_price(lot_size, "lot size")
        steps = self._lot_size / LOT_STEP
        if self._lot_size < LOT_STEP or abs(steps - round(steps)) > 1e-9:
            raise ValueError(f"lot size must be at least 0.01, in steps of 0.01, got {lot_size!r}")
        pip_value = signal.pair.pip_value_per_lot(self._setup.entry)
        self._risk_amount = round(self._lot_size * self.stop_loss_pips * pip_value, 2)
        if self._risk_amount > account.max_risk_amount():
            raise ValueError("risk amount must not exceed the account's risk percent of its balance")

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
    def stop_loss_pips(self):
        """Return the stop-loss distance in pips, rounded to 1 decimal."""
        return round(self._setup.risk() / self._setup.pair.pip_size(), 1)

    @property
    def risk_amount(self):
        """Return lot size × stop-loss pips × pip value per lot at entry, in USD, rounded to cents (FR9)."""
        return self._risk_amount

    @property
    def reference_timeframe(self):
        """Return the signal's reference timeframe (FR9)."""
        return self._signal.reference_timeframe()
