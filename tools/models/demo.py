"""Phase 04 demo. Run with: python -m tools.models.demo

Uses fixed example data only. It does not call the OANDA API.
"""

from datetime import date

from tools.models import BacktestResult, BuySetup, CurrencyPair, SellSetup, TradeSetup


def main():
    print("== CurrencyPair ==")
    eur_usd = CurrencyPair("EUR_USD", [(1.0850, 1.0800), (1.0900, 1.0840), (1.0950, 1.0880)])
    gbp_usd = CurrencyPair("GBP_USD", [(1.2800, 1.2750), (1.2760, 1.2700), (1.2720, 1.2650)])
    usd_jpy = CurrencyPair("USD_JPY", [(150.20, 149.80), (150.60, 149.70), (150.40, 150.00)])
    for pair in (eur_usd, gbp_usd, usd_jpy):
        print(f"{pair.name}: {len(pair.price_data)} price points, "
              f"market structure = {pair.market_structure()}")

    print("\n== TradeSetup: BuySetup and SellSetup ==")
    buy = BuySetup(eur_usd, entry=1.0900, stop_loss=1.0850, take_profit=1.1000)
    sell = SellSetup(gbp_usd, entry=1.2700, stop_loss=1.2750, take_profit=1.2550)
    for setup in (buy, sell):
        print(f"{type(setup).__name__} is a TradeSetup: {isinstance(setup, TradeSetup)}")
        # Inherited from TradeSetup: pair_name, entry, stop_loss, take_profit, reward_to_risk()
        print(f"  inherited:  {setup.pair_name}, entry {setup.entry}, "
              f"stop loss {setup.stop_loss}, take profit {setup.take_profit}, "
              f"reward-to-risk = {setup.reward_to_risk():.2f}")
        # Overridden in each subclass: direction, reward(), risk()
        print(f"  overridden: direction = {setup.direction}, "
              f"reward = {setup.reward():.4f}, risk = {setup.risk():.4f}")

    print("\n== BacktestResult ==")
    tested = BacktestResult(eur_usd, date(2026, 10, 15), setups_tested=12, trade_count=10, win_count=6)
    no_trades = BacktestResult(gbp_usd, date(2026, 10, 15), setups_tested=0, trade_count=0, win_count=0)
    for result in (tested, no_trades):
        print(f"{result.pair_name} on {result.test_date}: {result.setups_tested} setups, "
              f"{result.trade_count} trades, {result.win_count} wins, "
              f"win rate = {result.win_rate()}")

    print("\n== Connected objects ==")
    print(f"buy setup and EUR_USD backtest share one CurrencyPair: {buy.pair is tested.pair is eur_usd}")
    print(f"buy setup reads its pair's market structure: {buy.pair.market_structure()}")
    print(f"backtest reads its pair's price data: {len(tested.pair.price_data)} price points")

    print("\n== Invalid objects ==")
    try:
        BuySetup(eur_usd, entry=1.0900, stop_loss=1.0950, take_profit=1.1000)
    except ValueError as error:
        print(f"Rejected invalid buy setup: {error}")
    try:
        SellSetup(gbp_usd, entry=1.2700, stop_loss=1.2650, take_profit=1.2550)
    except ValueError as error:
        print(f"Rejected invalid sell setup: {error}")
    try:
        BuySetup("EUR_USD", entry=1.0900, stop_loss=1.0850, take_profit=1.1000)
    except ValueError as error:
        print(f"Rejected pair name string: {error}")
    try:
        TradeSetup(eur_usd, entry=1.0900, stop_loss=1.0850, take_profit=1.1000)
    except NotImplementedError as error:
        print(f"Rejected bare TradeSetup: {error}")


if __name__ == "__main__":
    main()
