"""Phase 05 demo. Run with: python -m tools.models.demo

Uses fixed example data only. It does not call the OANDA API.
"""

from datetime import date, datetime, timezone

from tools.models import (
    Account, BacktestResult, BreakOfStructure, BuySetup, Candle, ChangeOfCharacter, CurrencyPair,
    Order, SellSetup, Signal, StructureEvent, SwingPoint, Timeframe, TimeframeAnalysis, Trade,
    TradePlan, TradeSetup, evaluate_setup,
)


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

    print("\n== Interface: evaluate_setup(setup: TradeSetup) ==")
    buy_win = BuySetup(eur_usd, entry=1.0830, stop_loss=1.0750, take_profit=1.0940)
    sell_open = SellSetup(gbp_usd, entry=1.2700, stop_loss=1.2900, take_profit=1.2500)
    for setup in (buy, sell, buy_win, sell_open):
        # Same function for every setup; each subclass supplies its own outcome() (FR3)
        print(f"{type(setup).__name__} {setup.pair_name} entry {setup.entry}, "
              f"stop loss {setup.stop_loss}, take profit {setup.take_profit}: "
              f"outcome = {evaluate_setup(setup)}")

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

    print("\n== Pipeline: candle -> structure -> confluence -> plan -> order -> trade ==")
    t0 = datetime(2026, 10, 15, 14, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 10, 15, 18, 0, tzinfo=timezone.utc)
    candle = Candle(eur_usd, Timeframe.H4, t1, open_=1.0905, high=1.0975, low=1.0898,
                    close=1.0962, volume=18432, complete=True)
    print(f"Candle {candle.pair.name} {candle.timeframe.value} at {candle.time:%Y-%m-%d %H:%M}: "
          f"O {candle.open} H {candle.high} L {candle.low} C {candle.close}")

    higher_high = SwingPoint(eur_usd, Timeframe.H4, t0, price=1.0950, label="HH")
    higher_low = SwingPoint(eur_usd, Timeframe.M5, t0, price=1.0880, label="HL")
    h1_higher_high = SwingPoint(eur_usd, Timeframe.H1, t0, price=1.0940, label="HH")
    bos = BreakOfStructure(higher_high, candle.time, candle.close)
    h1_bos = BreakOfStructure(h1_higher_high, t1, close=1.0955)
    choch = ChangeOfCharacter(higher_low, t1, close=1.0875)
    for event in (bos, choch):
        print(f"{type(event).__name__} is a StructureEvent: {isinstance(event, StructureEvent)}, "
              f"broke {event.swing.label} ({event.swing.kind}) at {event.swing.price}, "
              f"direction = {event.direction}")

    m1 = TimeframeAnalysis(eur_usd, Timeframe.M1, "uptrend")
    m5 = TimeframeAnalysis(eur_usd, Timeframe.M5, "uptrend", latest_event=choch)
    h1 = TimeframeAnalysis(eur_usd, Timeframe.H1, "ranging", latest_event=h1_bos)
    h4 = TimeframeAnalysis(eur_usd, Timeframe.H4, "uptrend", latest_event=bos)
    for analysis in (m1, m5, h1, h4):
        event_name = type(analysis.latest_event).__name__ if analysis.latest_event else "none"
        print(f"  {analysis.timeframe.value}: trend {analysis.trend}, latest event {event_name} "
              f"-> vote {analysis.vote()}")
    signal = Signal(m1, m5, h1, h4)
    print(f"Signal {signal.pair.name}: direction {signal.direction()}, score {signal.score()}/4, "
          f"minimum {signal.min_score}, valid = {signal.is_valid()}, trade direction = {signal.trade_direction()}")

    account = Account("FAKE-ACCOUNT-001", balance=5000, currency="USD",
                      environment="practice", risk_percent=1.0)
    print(f"Account {account.account_id} ({account.environment}): balance {account.balance} "
          f"{account.currency}, risk {account.risk_percent}% -> max risk {account.max_risk_amount()}")

    plan = TradePlan(signal, account, entry=1.0900, stop_loss=1.0850, take_profit_1=1.1000,
                     take_profit_2=1.1050, lot_size=1.0, risk_amount=50.0,
                     reference_timeframe=Timeframe.H4)
    print(f"TradePlan owns a {type(plan.setup).__name__}: entry {plan.setup.entry}, "
          f"stop loss {plan.setup.stop_loss}, TP1 {plan.setup.take_profit}, TP2 {plan.take_profit_2}, "
          f"R:R {plan.setup.reward_to_risk():.2f}, lot {plan.lot_size}, risk {plan.risk_amount}, "
          f"reference {plan.reference_timeframe.value}")
    print(f"  the plan's setup runs through the same interface: outcome = {evaluate_setup(plan.setup)}")

    order = Order(plan, account, confirmed=True)
    print(f"Order: {order.order_type}, units {order.units():+,} (data only, nothing sent to OANDA)")
    for trade in (Trade(order, "win", exit_price=1.1000), Trade(order, "loss", exit_price=1.0850),
                  Trade(order, "open")):
        r = trade.r_multiple()
        print(f"  Trade {trade.outcome}: exit {trade.exit_price}, "
              f"R multiple = {'None' if r is None else f'{r:+.2f}'}")

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
    except TypeError as error:
        print(f"Rejected bare TradeSetup: {error}")
    try:
        Candle(eur_usd, Timeframe.H1, t0, open_=1.09, high=1.10, low=1.08, close=1.09,
               volume=0, complete=False)
    except ValueError as error:
        print(f"Rejected incomplete candle: {error}")
    try:
        StructureEvent(higher_high, t1, 1.0962)
    except TypeError as error:
        print(f"Rejected bare StructureEvent: {error}")
    try:
        tie = Signal(m1, m5, TimeframeAnalysis(eur_usd, Timeframe.H1, "downtrend"),
                     TimeframeAnalysis(eur_usd, Timeframe.H4, "downtrend"))
        TradePlan(tie, account, entry=1.0900, stop_loss=1.0850, take_profit_1=1.1000,
                  take_profit_2=1.1050, lot_size=1.0, risk_amount=50.0, reference_timeframe=Timeframe.H4)
    except ValueError as error:
        print(f"Rejected trade plan for a tied signal: {error}")
    try:
        TradePlan(signal, account, entry=1.0900, stop_loss=1.0850, take_profit_1=1.0990,
                  take_profit_2=1.1050, lot_size=1.0, risk_amount=50.0, reference_timeframe=Timeframe.H4)
    except ValueError as error:
        print(f"Rejected trade plan with R:R 1.8: {error}")
    try:
        Account("FAKE-ACCOUNT-002", balance=5000, currency="USD", environment="live", risk_percent=1.0)
    except ValueError as error:
        print(f"Rejected live account: {error}")
    try:
        Order(plan, account, confirmed=False)
    except ValueError as error:
        print(f"Rejected unconfirmed order: {error}")


if __name__ == "__main__":
    main()
