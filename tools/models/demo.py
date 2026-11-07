"""NEXUS demo (through Phase 09). Run with: python -m tools.models.demo

Uses fixed example data only. It does not call the OANDA API.
"""

from datetime import date, datetime, timezone

from tools.models import (
    Account, BacktestResult, BreakOfStructure, BuyDirection, Candle, CandleSource, ChangeOfCharacter,
    CurrencyPair, OandaCandleAdapter, Order, SellDirection, Signal, StructureEvent, SwingPoint, Timeframe, TimeframeAnalysis, Trade,
    TradeDirection, TradePlanBuilder, TradeSetup, evaluate_setup, rank_pairs,
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
          f"minimum {signal.min_score}, valid = {signal.is_valid()}, "
          f"trade direction = {type(signal.trade_direction()).__name__}, "
          f"reference timeframe = {signal.reference_timeframe().value}")

    account = Account("FAKE-ACCOUNT-001", balance=5000, currency="USD",
                      environment="practice", risk_percent=1.0)
    print(f"Account {account.account_id} ({account.environment}): balance {account.balance} "
          f"{account.currency}, risk {account.risk_percent}% -> max risk {account.max_risk_amount()}")

    plan = (TradePlanBuilder().signal(signal).account(account).entry(1.0900).stop_loss(1.0850)
            .take_profit_1(1.1000).take_profit_2(1.1050).lot_size(0.1).build())
    print(f"TradePlan owns a {plan.setup.direction} TradeSetup: entry {plan.setup.entry}, "
          f"stop loss {plan.setup.stop_loss}, TP1 {plan.setup.take_profit}, TP2 {plan.take_profit_2}, "
          f"R:R {plan.setup.reward_to_risk():.2f}, reference {plan.reference_timeframe.value} (from the signal)")
    print(f"  risk = lot {plan.lot_size} x {plan.stop_loss_pips} pips x "
          f"${eur_usd.pip_value_per_lot(plan.setup.entry)} per pip per lot = ${plan.risk_amount:.2f} "
          f"(max ${account.max_risk_amount():.2f})")
    print(f"  the plan's setup runs through the same interface: outcome = {evaluate_setup(plan.setup)}")

    order = Order(plan, account, confirmed=True)
    print(f"Order: {order.order_type}, units {order.units():+,} (data only, nothing sent to OANDA)")
    for trade in (Trade(order, "win", exit_price=1.1000), Trade(order, "loss", exit_price=1.0850),
                  Trade(order, "open")):
        r = trade.r_multiple()
        print(f"  Trade {trade.outcome}: exit {trade.exit_price}, "
              f"R multiple = {'None' if r is None else f'{r:+.2f}'}")

    print("\n== Collection: Account records its Trades (FR11) ==")
    first_trade = Trade(order, "win", exit_price=1.1000)
    second_order = Order(plan, account, confirmed=True)
    open_trade = Trade(second_order, "open")
    account.add_trade(first_trade)
    account.add_trade(open_trade)
    print(f"recorded {len(account.trades)} trades: {len(account.open_trades())} open, "
          f"{len(account.closed_trades())} closed")
    account.close_trade(open_trade, Trade(second_order, "loss", exit_price=1.0850))
    print(f"after closing the open trade: {[t.outcome for t in account.trades]}, "
          f"{len(account.open_trades())} open, {len(account.closed_trades())} closed, "
          f"total R = {sum(t.r_multiple() for t in account.closed_trades()):+.2f}")
    try:
        account.add_trade(Trade(order, "open"))
    except ValueError as error:
        print(f"Rejected a second trade for the same order: {error}")

    print("\n== Collection: CurrencyPair holds its BacktestResults; rank_pairs (FR4) ==")
    older = BacktestResult(eur_usd, date(2026, 10, 8))
    older.add_setup(TradeSetup(eur_usd, BuyDirection(), entry=1.0820, stop_loss=1.0805, take_profit=1.0950))
    eur_usd.add_backtest(older)
    eur_usd.add_backtest(tested)
    gbp_usd.add_backtest(no_trades)
    aud_usd = CurrencyPair("AUD_USD", [(0.6650, 0.6600), (0.6700, 0.6640), (0.6750, 0.6680)])
    aud_result = BacktestResult(aud_usd, date(2026, 10, 15))
    aud_result.add_setup(TradeSetup(aud_usd, BuyDirection(), entry=0.6620, stop_loss=0.6590, take_profit=0.6680))
    aud_result.add_setup(TradeSetup(aud_usd, BuyDirection(), entry=0.6620, stop_loss=0.6605, take_profit=0.6750))
    aud_usd.add_backtest(aud_result)
    print(f"EUR_USD holds {len(eur_usd.backtests)} backtests; most recent (added last) has "
          f"win rate {eur_usd.latest_backtest().win_rate()} (the older one had {older.win_rate()})")
    for rank, pair in enumerate(rank_pairs([usd_jpy, gbp_usd, eur_usd, aud_usd]), start=1):
        latest = pair.latest_backtest()
        if latest is None:
            detail = "no backtest"
        elif latest.trade_count == 0:
            detail = "0 trades"
        else:
            detail = f"win rate {latest.win_rate()}"
        print(f"  #{rank} {pair.name}: {detail}")

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
        (TradePlanBuilder().signal(tie).account(account).entry(1.0900).stop_loss(1.0850)
         .take_profit_1(1.1000).take_profit_2(1.1050).lot_size(0.1).build())
    except ValueError as error:
        print(f"Rejected trade plan for a tied signal: {error}")
    try:
        (TradePlanBuilder().signal(signal).account(account).entry(1.0900).stop_loss(1.0850)
         .take_profit_1(1.0990).take_profit_2(1.1050).lot_size(0.1).build())
    except ValueError as error:
        print(f"Rejected trade plan with R:R 1.8: {error}")
    try:
        (TradePlanBuilder().signal(signal).account(account).entry(1.0900).stop_loss(1.0850)
         .take_profit_1(1.1000).take_profit_2(1.1050).lot_size(1.0).build())
    except ValueError as error:
        print(f"Rejected trade plan risking $500 (1.0 lot x 50 pips x $10): {error}")
    try:
        eur_gbp = CurrencyPair("EUR_GBP", [(0.8550, 0.8500), (0.8580, 0.8520)])
        eur_gbp.pip_value_per_lot(0.85)
    except ValueError as error:
        print(f"Rejected cross pair pip value: {error}")
    try:
        Account("FAKE-ACCOUNT-002", balance=5000, currency="USD", environment="live", risk_percent=1.0)
    except ValueError as error:
        print(f"Rejected live account: {error}")
    try:
        Order(plan, account, confirmed=False)
    except ValueError as error:
        print(f"Rejected unconfirmed order: {error}")

    print("\n== Builder: TradePlanBuilder assembles a TradePlan one part at a time (Phase 08) ==")
    built = (TradePlanBuilder()
             .signal(signal)
             .account(account)
             .entry(1.0900)
             .stop_loss(1.0850)
             .take_profit_1(1.1000)
             .take_profit_2(1.1050)
             .lot_size(0.1)
             .build())
    print(f"Built TradePlan: {built.setup.pair_name} {built.setup.direction}, entry {built.setup.entry}, "
          f"stop loss {built.setup.stop_loss}, TP1 {built.setup.take_profit}, TP2 {built.take_profit_2}, "
          f"lot {built.lot_size}, risk ${built.risk_amount:.2f}, "
          f"R:R {built.setup.reward_to_risk():.2f}, reference {built.reference_timeframe.value}")
    try:
        TradePlanBuilder().signal(signal).account(account).entry(1.0900).stop_loss(1.0850).build()
    except ValueError as error:
        print(f"Rejected incomplete builder: {error}")

    # Why Adapter: OANDA describes a candle in its own terms ("instrument" and "granularity" strings,
    # and prices as "mid" o/h/l/c strings), but NEXUS works with Candle objects that hold a
    # CurrencyPair and a Timeframe. Without a translation point, OANDA's format spreads through
    # the analysis code as plain dicts. OandaCandleAdapter fixes this by making an OANDA response
    # usable through NEXUS's own CandleSource interface, so the rest of NEXUS only sees Candle objects
    # and OANDA's format lives in one class. Facade was less appropriate: the problem is an
    # incompatible interface, not a complicated subsystem, and run_full_analysis() already gives
    # the analysis steps a single entry point, so a Facade would only rename it.
    print("\n== Adapter: OandaCandleAdapter turns an OANDA response into Candles (Phase 09) ==")
    oanda_response = {  # fixed example in OANDA's format; no API call
        "instrument": "EUR_USD",
        "granularity": "H4",
        "candles": [
            {"time": "2026-10-15T14:00:00.000000000Z", "volume": 15210, "complete": True,
             "mid": {"o": "1.08920", "h": "1.09110", "l": "1.08870", "c": "1.09050"}},
            {"time": "2026-10-15T18:00:00.000000000Z", "volume": 18432, "complete": True,
             "mid": {"o": "1.09050", "h": "1.09750", "l": "1.08980", "c": "1.09620"}},
            {"time": "2026-10-15T22:00:00.000000000Z", "volume": 2031, "complete": False,
             "mid": {"o": "1.09620", "h": "1.09700", "l": "1.09550", "c": "1.09600"}},
        ],
    }
    source = OandaCandleAdapter(oanda_response, eur_usd)
    print(f"OandaCandleAdapter is a CandleSource: {isinstance(source, CandleSource)}")
    adapted = source.candles()
    print(f"{len(oanda_response['candles'])} OANDA candles in -> {len(adapted)} Candle objects out "
          f"(the incomplete one is skipped)")
    for c in adapted:
        print(f"  {type(c).__name__} {c.pair.name} {c.timeframe.value} at {c.time:%Y-%m-%d %H:%M}: "
              f"O {c.open} H {c.high} L {c.low} C {c.close}, volume {c.volume}")
    print(f"adapted candles share the existing CurrencyPair: {all(c.pair is eur_usd for c in adapted)}")
    try:
        OandaCandleAdapter({"instrument": "EUR_USD", "granularity": "D", "candles": []}, eur_usd)
    except ValueError as error:
        print(f"Rejected OANDA response: {error}")


if __name__ == "__main__":
    main()
