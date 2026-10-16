"""Phase 02 demo. Run with: python -m tools.models.demo

Uses fixed example data only. It does not call the OANDA API.
"""

from datetime import date

from tools.models import BacktestResult, CurrencyPair, TradeSetup


def main():
    print("== CurrencyPair ==")
    eur_usd = CurrencyPair("EUR_USD", [(1.0850, 1.0800), (1.0900, 1.0840), (1.0950, 1.0880)])
    gbp_usd = CurrencyPair("GBP_USD", [(1.2800, 1.2750), (1.2760, 1.2700), (1.2720, 1.2650)])
    usd_jpy = CurrencyPair("USD_JPY", [(150.20, 149.80), (150.60, 149.70), (150.40, 150.00)])
    for pair in (eur_usd, gbp_usd, usd_jpy):
        print(f"{pair.name}: {len(pair.price_data)} price points, "
              f"market structure = {pair.market_structure()}")

    print("\n== TradeSetup ==")
    buy = TradeSetup("EUR_USD", "buy", entry=1.0900, stop_loss=1.0850, take_profit=1.1000)
    sell = TradeSetup("GBP_USD", "sell", entry=1.2700, stop_loss=1.2750, take_profit=1.2550)
    for setup in (buy, sell):
        print(f"{setup.pair_name} {setup.direction}: entry {setup.entry}, "
              f"stop loss {setup.stop_loss}, take profit {setup.take_profit}, "
              f"reward-to-risk = {setup.reward_to_risk():.2f}")

    print("\n== BacktestResult ==")
    tested = BacktestResult("EUR_USD", date(2026, 10, 15), setups_tested=12, trade_count=10, win_count=6)
    no_trades = BacktestResult("GBP_USD", date(2026, 10, 15), setups_tested=0, trade_count=0, win_count=0)
    for result in (tested, no_trades):
        print(f"{result.pair_name} on {result.test_date}: {result.setups_tested} setups, "
              f"{result.trade_count} trades, {result.win_count} wins, "
              f"win rate = {result.win_rate()}")

    print("\n== Invalid object ==")
    try:
        TradeSetup("EUR_USD", "buy", entry=1.0900, stop_loss=1.0950, take_profit=1.1000)
    except ValueError as error:
        print(f"Rejected invalid buy setup: {error}")


if __name__ == "__main__":
    main()
