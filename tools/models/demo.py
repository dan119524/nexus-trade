"""Phase 06 demo. Run with: python -m tools.models.demo

Uses fixed example data only. It does not call the OANDA API.
"""

from datetime import date, datetime, timezone

from tools.models import (
    Account, BacktestResult, BreakOfStructure, BuyDirection, Candle, ChangeOfCharacter, CurrencyPair,
    Order, SellDirection, Signal, StructureEvent, SwingPoint, Timeframe, TimeframeAnalysis, Trade,
    TradeDirection, TradePlan, TradeSetup, evaluate_setup,
)


def main():
    print("== CurrencyPair ==")
    eur_usd = CurrencyPair("EUR_USD", [(1.0850, 1.0800), (1.0900, 1.0840), (1.0950, 1.0880)])
    gbp_usd = CurrencyPair("GBP_USD", [(1.2800, 1.2750), (1.2760, 1.2700), (1.2720, 1.2650)])
    usd_jpy = CurrencyPair("USD_JPY", [(150.20, 149.80), (150.60, 149.70), (150.40, 150.00)])
    for pair in (eur_usd, gbp_usd, usd_jpy):
        print(f"{pair.name}: {len(pair.price_data)} price points, "
              f"market structure = {pair.market_structure()}")

    print("\n== Composition: TradeSetup delegates to its TradeDirection ==")
    buy = TradeSetup(eur_usd, BuyDirection(), entry=1.0900, stop_loss=1.0850, take_profit=1.1000)
    sell = TradeSetup(gbp_usd, SellDirection(), entry=1.2700, stop_loss=1.2750, take_profit=1.2550)
    for setup in (buy, sell):
        rules = setup.trade_direction
        print(f"TradeSetup with a {type(rules).__name__} "
              f"(a TradeDirection: {isinstance(rules, TradeDirection)}): direction = {setup.direction}")
        # Held by TradeSetup: pair, prices, reward_to_risk()
        print(f"  held by TradeSetup:  {setup.pair_name}, entry {setup.entry}, "
              f"stop loss {setup.stop_loss}, take profit {setup.take_profit}, "
              f"reward-to-risk = {setup.reward_to_risk():.2f}")
        # Delegated to the direction: reward(), risk(), is_beyond(), units_sign
        print(f"  delegated to {rules.name}: reward = {setup.reward():.4f}, risk = {setup.risk():.4f}, "
              f"TP beyond entry = {rules.is_beyond(setup.take_profit, setup.entry)}, "
              f"units sign = {rules.units_sign:+d}")

    print("\n== Interface: evaluate_setup(setup: TradeSetup) ==")
    buy_win = TradeSetup(eur_usd, BuyDirection(), entry=1.0830, stop_loss=1.0750, take_profit=1.0940)
    sell_open = TradeSetup(gbp_usd, SellDirection(), entry=1.2700, stop_loss=1.2900, take_profit=1.2500)
    for setup in (buy, sell, buy_win, sell_open):
        # Same function for every setup; its TradeDirection supplies the outcome rules (FR3)
        print(f"{setup.direction} {setup.pair_name} entry {setup.entry}, "
              f"stop loss {setup.stop_loss}, take profit {setup.take_profit}: "
              f"outcome = {evaluate_setup(setup)}")

    print("\n== Collection: BacktestResult holds its TradeSetups ==")
    eur_sell_open = TradeSetup(eur_usd, SellDirection(), entry=1.0870, stop_loss=1.1000, take_profit=1.0700)
    tested = BacktestResult(eur_usd, date(2026, 10, 15))
    for setup in (buy, buy_win, eur_sell_open):
        tested.add_setup(setup)
    no_trades = BacktestResult(gbp_usd, date(2026, 10, 15))
    for result in (tested, no_trades):
        outcomes = ", ".join(f"{s.direction} {s.outcome()}" for s in result.setups) or "none"
        print(f"{result.pair_name} on {result.test_date}: setups [{outcomes}] -> "
              f"{result.setups_tested} setups, {result.trade_count} trades, {result.win_count} wins, "
              f"win rate = {result.win_rate()}")
    print(f"setups are returned as a {type(tested.setups).__name__}")
    try:
        tested.add_setup(sell)
    except ValueError as error:
        print(f"Rejected GBP_USD setup in the EUR_USD backtest: {error}")
    try:
        tested.add_setup(buy)
    except ValueError as error:
        print(f"Rejected the same setup twice: {error}")
    tested.remove_setup(buy)
    print(f"after removing the losing buy: {tested.setups_tested} setups, {tested.trade_count} trades, "
          f"{tested.win_count} wins, win rate = {tested.win_rate()}")

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
    print(f"TradePlan owns a {plan.setup.direction} TradeSetup: entry {plan.setup.entry}, "
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
        TradeSetup(eur_usd, BuyDirection(), entry=1.0900, stop_loss=1.0950, take_profit=1.1000)
    except ValueError as error:
        print(f"Rejected invalid buy setup: {error}")
    try:
        TradeSetup(gbp_usd, SellDirection(), entry=1.2700, stop_loss=1.2650, take_profit=1.2550)
    except ValueError as error:
        print(f"Rejected invalid sell setup: {error}")
    try:
        TradeSetup("EUR_USD", BuyDirection(), entry=1.0900, stop_loss=1.0850, take_profit=1.1000)
    except ValueError as error:
        print(f"Rejected pair name string: {error}")
    try:
        TradeDirection()
    except TypeError as error:
        print(f"Rejected bare TradeDirection: {error}")
    try:
        TradeSetup(eur_usd, "buy", entry=1.0900, stop_loss=1.0850, take_profit=1.1000)
    except ValueError as error:
        print(f"Rejected direction string: {error}")
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
