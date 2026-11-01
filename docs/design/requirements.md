# NEXUS Trade Requirements and Initial Domain Model

## Domain Entities

| Entity | Description |
|---|---|
| **CurrencyPair** | A forex market NEXUS analyzes, such as EUR_USD, together with its past price data, its current market structure, its pip size and pip value, and its backtest results. |
| **TradeSetup** | A suggested trade on one currency pair, with a direction, an entry price, a stop loss, and a take profit. Its direction rules come from its TradeDirection. |
| **TradeDirection** | The rules that differ between buying and selling: price order, reward, risk, outcome, which price is beyond another, and the units sign. Its kind comes from BuyDirection or SellDirection. |
| **BuyDirection** | The buy rules: stop loss < entry < take profit, and higher prices are in the trade's favor. |
| **SellDirection** | The sell rules: take profit < entry < stop loss, and lower prices are in the trade's favor. |
| **BacktestResult** | The outcome of testing trade setups on one currency pair's past price data, showing how well they would have performed. It holds the setups it tested. |
| **Candle** | One complete OHLC bar for a currency pair on one timeframe, with its time and volume. |
| **SwingPoint** | A confirmed swing high or swing low on one timeframe, labeled HH, HL, LH, or LL. |
| **StructureEvent** | A candle close beyond a labeled swing point, in a bullish or bearish direction. Its kind comes from BreakOfStructure or ChangeOfCharacter. |
| **BreakOfStructure** | A structure event that breaks a swing point with the trend: a close above an HH (bullish) or below an LL (bearish). |
| **ChangeOfCharacter** | A structure event that breaks a swing point against the trend: a close above an LH (bullish) or below an HL (bearish). |
| **TimeframeAnalysis** | The analysis of one currency pair on one timeframe: its trend, its most recent structure event, and the vote it casts. |
| **Signal** | A confluence result for one currency pair, combining the votes of its M1, M5, H1, and H4 analyses into a direction and a score. |
| **TradePlan** | The plan for a valid signal: a trade setup plus a second take profit and a lot size. Its risk amount comes from its lot size, and its reference timeframe comes from its signal. |
| **Account** | The OANDA practice account a trade plan is sized for, with its balance, currency, environment, and risk percent, and the trades it records. |
| **Order** | A market order created from a trade plan for a practice account, after the trader's explicit confirmation. |
| **Trade** | A position opened by an order, with its outcome (win, loss, or open) and its R multiple. |

## Values

| Value | Description |
|---|---|
| **Timeframe** | One of M1, M5, H1, or H4. An enumeration, not an entity. |

## Use Cases

| ID | Actor | Goal |
|---|---|---|
| UC1 | Trader | Review the market structure of a currency pair |
| UC2 | Trader | Review a suggested trade setup before deciding whether to act on it |
| UC3 | Trader | Backtest trade setups for a currency pair on past price data |
| UC4 | Trader | See which currency pairs performed best in backtests |
| UC5 | Trader | Be alerted only when enough timeframes agree on a direction |
| UC6 | Trader | Place a practice market order from a trade plan |
| UC7 | Trader | Review recorded trades and their outcomes |

## Functional Requirements

| ID | Requirement | Use case |
|---|---|---|
| FR1 | NEXUS shall identify the market structure of a selected currency pair as uptrend, downtrend, or ranging, using that pair's past price data. An uptrend means every price point has a higher high and a higher low than the one before it. A downtrend means every price point has a lower high and a lower low than the one before it. Anything else, including any equal high or low, is ranging. | UC1 |
| FR2 | NEXUS shall suggest trade setups for a currency pair, each with a direction (buy or sell), an entry price, a stop loss, and a take profit, and shall not suggest any setup with a reward-to-risk ratio below 2. For a buy, stop loss < entry < take profit. For a sell, take profit < entry < stop loss. | UC2 |
| FR3 | NEXUS shall backtest trade setups for a currency pair on past price data and report the number of trades and the win rate. A win is a trade that hits its take profit before its stop loss. | UC3 |
| FR4 | NEXUS shall rank currency pairs from best to worst by the win rate of each pair's most recent backtest result. Pairs with zero trades or no backtest result are ranked last. | UC4 |
| FR5 | NEXUS shall work only with an OANDA practice account and shall never trade real money. | All |
| FR6 | NEXUS shall represent complete OHLC candles on M1, M5, H1, and H4, rejecting incomplete candles and any candle with high < low, open or close outside [low, high], or a price <= 0. | UC1 |
| FR7 | NEXUS shall identify swing highs and lows labeled HH/HL/LH/LL, and detect a BOS (a break with the trend) and a CHoCH (a break against the trend). | UC1 |
| FR8 | NEXUS shall flag a signal only when at least the minimum confluence score (default 3) of the 4 timeframes vote the same direction. | UC5 |
| FR9 | For a valid signal, NEXUS shall produce a trade plan with entry, stop loss, TP1, TP2, a lot size, and a reference timeframe. The reference timeframe is the highest timeframe that voted with the signal's direction, in the order H4, H1, M5, M1. The plan's risk is lot size × stop-loss distance in pips × pip value per lot, and it shall never exceed the account's risk percent of its balance, capped at 2%. A plan is produced only for a USD account and only for a USD-quote or USD-base currency pair; cross pairs are rejected until a real conversion exists. | UC2 |
| FR10 | NEXUS shall create only market orders, only for a practice account, and only after the trader's explicit confirmation. | UC6 |
| FR11 | NEXUS shall record each trade with its outcome (win, loss, or open) and its R multiple. | UC7 |
| FR12 | NEXUS shall take each timeframe's trend (uptrend, downtrend, or ranging) from that timeframe's swing labels, as computed by the analysis tool (`tools/analysis/detect_trend.py`). This is separate from a currency pair's market structure in FR1. | UC1 |

## Vocabularies

NEXUS uses three separate direction vocabularies. Each belongs to one concept.

| Vocabulary | Values | Used for |
|---|---|---|
| Trade direction | buy, sell | TradeSetup, TradePlan, Order, Trade |
| Timeframe vote | bullish, bearish, neutral | TimeframeAnalysis vote, Signal direction, StructureEvent direction (bullish or bearish only) |
| Market structure | uptrend, downtrend, ranging | CurrencyPair market structure (FR1), TimeframeAnalysis trend |

- A bullish signal leads to a buy. A bearish signal leads to a sell.
- A bullish vote or structure event matches an uptrend. A bearish vote or structure event matches a downtrend.

## Voting

A TimeframeAnalysis casts its vote from its trend and its most recent structure event (from `workflows/03_score_confluence.md`).

| Trend | Most recent structure event | Vote |
|---|---|---|
| uptrend | bullish or none | bullish |
| uptrend | bearish | neutral |
| downtrend | bearish or none | bearish |
| downtrend | bullish | neutral |
| ranging | bullish | bullish |
| ranging | bearish | bearish |
| ranging | none | neutral |

- A Signal's direction is the majority of its bullish and bearish votes. Neutral votes do not count. A tie, including no bullish or bearish votes at all, gives no direction, so the signal is invalid.
- `tools/confluence/score_confluence.py` picks bullish on a tie. Signal does not follow the tool on this point.

## Reward-to-Risk Minimum

- A TradePlan rejects a setup whose reward-to-risk ratio to TP1, rounded to 2 decimals, is below 2.
- This closes Phase 02 decision D5 (FR2's minimum reward-to-risk of 2). TradeSetup itself still does not enforce the minimum; TradePlan does.
- In the tools, the reward-to-risk ratio is currently fixed at `rr_tp1 = 2.0`: `build_trade_plan` calls `calculate_sl_tp` with its default `rr_tp1`, and `calculate_sl_tp` places TP1 at entry ± (stop-loss distance × `rr_tp1`) and returns `risk_reward` measured from entry, SL and TP1, rounded to 2 decimals (Phase 07), which for this fixed placement is always 2.00. The gate in `build_trade_plan` (reject when the ratio is below `MIN_RISK_REWARD`) therefore only matters if `rr_tp1` changes or `MIN_RISK_REWARD` is set above 2. `test_rr_gate_rejects_low_rr` mocks `calculate_sl_tp` to test the gate itself. Whether TP1 and the ratio should come from market structure instead is open for Workshop 07.

## Pip Size and Pip Value

From `tools/trade_plan/calculate_sl_tp.py` and `tools/trade_plan/calculate_lot_size.py`.

| Rule | Value |
|---|---|
| Pip size | 0.01 for a pair containing JPY, 0.0001 otherwise |
| Pip value per standard lot (USD), USD-quote pairs (EUR_USD, GBP_USD, AUD_USD, NZD_USD) | 10.0 |
| Pip value per standard lot (USD), USD_JPY | 1,000 / price, rounded to 4 decimals |
| Pip value per standard lot (USD), other USD-base pairs (USD_CHF, USD_CAD, USD_SGD) | 10 / price, rounded to 4 decimals |
| Any other pair (cross pair) | Rejected: no pip value until a real conversion exists |

- A TradePlan's lot size is at least 0.01, in steps of 0.01.
- A TradePlan's stop-loss distance in pips is its setup's risk divided by its pair's pip size, rounded to 1 decimal (as in `calculate_sl_tp.py`).
- A TradePlan's risk amount is lot size × stop-loss pips × pip value per lot at its entry price, rounded to cents (2 decimals). It must be at most the account's maximum risk amount. Rounding to cents keeps floating-point noise from rejecting an exactly-at-limit plan; a risk one cent or more over the maximum is rejected.

## Ranking

- FR4 ranks currency pairs by the win rate of each pair's most recent backtest result, the one added last. A currency pair rejects a backtest result dated earlier than its most recent one, so the one added last is never older than the others. Pairs with no backtest result, or whose most recent result has zero trades, are ranked last.
- Pairs with equal win rates, and the pairs ranked last, keep their input order.
- A currency pair passed to the ranking more than once (the same object) is rejected.

## Known Conflicts

| Conflict | Files | Decision |
|---|---|---|
| FR4 ranks pairs by win rate. `_rank_and_select_pairs` scores pairs by 40% win rate, 40% total R, and 20% profit factor, skips pairs with fewer than 3 trades, and keeps the top 8. | `requirements.md` FR4, `tools/scheduler/weekly_cycle.py` | FR4 is implemented as written in `tools/models/`. The tool is not changed. |

- The Phase 05 conflict between FR1 and `detect_trend.py` was resolved in Phase 06 by FR12: FR1 is a currency pair's market structure, and a timeframe's trend comes from its swing labels.
- The conflict between `calculate_lot_size` rounding the lot size to the nearest 0.01 (which could round up past the account's maximum risk) and FR9 was resolved after Phase 06: the tool now rounds the lot size down to 0.01, and when even the 0.01 minimum lot would risk more than the limit it returns no trade instead of forcing 0.01.
- The conflict between FR5 and the OANDA clients in `fetch_candles`, `fetch_account`, `fetch_instruments`, `execute_trade`, `weekly_cycle`, and `server` (each connected to the live environment when `OANDA_ENV=live`) was resolved after Phase 06: every client now calls `require_practice_env` and refuses any environment except practice, and the unused `validate_env` helper accepts practice only.
- The conflict between FR9's 2% cap and `calculate_lot_size` (which accepted a risk percent up to 10) was resolved after Phase 06: the tool now rejects a risk percent above 2 with `ValueError`, the same cap as `Account`, and so does the unused `validate_risk_percent` helper.
- The conflict between FR9 (a plan's risk is sized from the account's balance) and `build_trade_plan` (which sized against a made-up $10,000 balance when the account fetch failed or the balance was 0) was resolved after Phase 06: the tool now writes no plan in either case.

## Model Rules

- Domain classes in `tools/models/` hold data and check rules only. They never call the OANDA API or the Claude API.
- Demos and tests use fake account IDs only.
- One-to-many relationships that a requirement needs navigated from the "one" side are stored as typed private lists from Phase 06: BacktestResult → TradeSetup, CurrencyPair → BacktestResult (FR4), and Account → Trade (FR11). The others are deliberately one-way (see Relationships and Multiplicities).

## CRC Analysis

> **Note:** In Phase 01, the NEXUS system performs the actions in FR1, FR2, FR3, and FR4: identifying market structure, suggesting trade setups, backtesting, and ranking currency pairs. Responsible classes are assigned in later phases.

### CurrencyPair

| Responsibilities | Collaborators |
|---|---|
| Know its name (for example, EUR_USD) | |
| Know its past price data | |
| Know its current market structure | |
| Know its pip size (0.01 for a JPY pair, 0.0001 otherwise) | |
| Know its pip value per standard lot in USD at a price, and reject a cross pair (FR9) | |
| Know its backtest results, add or remove one, and know its most recent (the one added last) | BacktestResult |
| Accept only a backtest result for itself (the same object) that it does not already hold and that is not dated earlier than its most recent | BacktestResult |

### TradeSetup

| Responsibilities | Collaborators |
|---|---|
| Know which currency pair it belongs to | CurrencyPair |
| Know its trade direction, and whether it is a buy or a sell | TradeDirection |
| Know its entry price, stop loss, and take profit, in the price order its direction requires (FR2) | TradeDirection |
| Know its reward, its risk, and its reward-to-risk ratio | TradeDirection |
| Know its outcome (win, loss, or open) on its pair's price data (FR3) | TradeDirection |

### TradeDirection

| Responsibilities | Collaborators |
|---|---|
| Know whether it is buy or sell (kind comes from BuyDirection or SellDirection) | |
| Check the price order of an entry, a stop loss, and a take profit | |
| Know the reward and the risk for an entry, a stop loss, and a take profit | |
| Know the outcome (win, loss, or open) of a stop loss and a take profit on price data | |
| Know whether one price is beyond another in the trade's favor | |
| Know its units sign | |

### BuyDirection

| Responsibilities | Collaborators |
|---|---|
| Know that it is buy | |
| Require stop loss < entry < take profit | |
| Know the reward (take profit − entry) and the risk (entry − stop loss) | |
| Know the outcome: a win when a high reaches take profit, a loss when a low reaches stop loss | |
| Know that a price is beyond another when it is higher, and that its units sign is positive | |

### SellDirection

| Responsibilities | Collaborators |
|---|---|
| Know that it is sell | |
| Require take profit < entry < stop loss | |
| Know the reward (entry − take profit) and the risk (stop loss − entry) | |
| Know the outcome: a win when a low reaches take profit, a loss when a high reaches stop loss | |
| Know that a price is beyond another when it is lower, and that its units sign is negative | |

### BacktestResult

| Responsibilities | Collaborators |
|---|---|
| Know which currency pair was tested | CurrencyPair |
| Know which trade setups were tested, and add or remove one | TradeSetup |
| Accept only a trade setup on its own currency pair (the same object) that it does not already hold | TradeSetup |
| Know its number of setups tested, trades, and wins from each setup's outcome; open setups are not trades (FR3) | TradeSetup |
| Know its win rate: wins divided by trades | |
| Know when the test was run | |

### Candle

| Responsibilities | Collaborators |
|---|---|
| Know its currency pair and timeframe | CurrencyPair, Timeframe |
| Know its time, open, high, low, close, and volume | |
| Reject an incomplete candle, a high below its low, an open or close outside [low, high], and any price <= 0 (FR6) | |

### SwingPoint

| Responsibilities | Collaborators |
|---|---|
| Know its currency pair and timeframe | CurrencyPair, Timeframe |
| Know its time, its price, and whether it is a high or a low | |
| Know its label: HH or LH for a high, HL or LL for a low (FR7) | |

### StructureEvent

| Responsibilities | Collaborators |
|---|---|
| Know the swing point it broke | SwingPoint |
| Know the time and the close price of the break | |
| Know its direction, bullish or bearish (kind comes from BreakOfStructure or ChangeOfCharacter) | |
| Require the close to be beyond the swing point's price in its direction | |

### BreakOfStructure

| Responsibilities | Collaborators |
|---|---|
| Require the broken swing point to be an HH (bullish) or an LL (bearish) | |

### ChangeOfCharacter

| Responsibilities | Collaborators |
|---|---|
| Require the broken swing point to be an LH (bullish) or an HL (bearish) | |

### TimeframeAnalysis

| Responsibilities | Collaborators |
|---|---|
| Know its currency pair and timeframe | CurrencyPair, Timeframe |
| Know its trend: uptrend, downtrend, or ranging, as computed by the analysis tool from its swing labels (FR12) | |
| Know its most recent structure event, if any, on its own currency pair and timeframe | StructureEvent |
| Know its vote (bullish, bearish, or neutral) from its trend and its most recent structure event (see Voting) | |

### Signal

| Responsibilities | Collaborators |
|---|---|
| Know its M1, M5, H1, and H4 analyses, all for the same currency pair | TimeframeAnalysis |
| Know its direction: the majority of the bullish and bearish votes, or no direction on a tie | |
| Know its score: the number of timeframes voting its direction (0 when it has no direction) | |
| Know its minimum confluence score, a whole number from 1 to 4 (default 3) | |
| Know whether it is valid: it has a direction and its score is at least the minimum (FR8) | |
| Know its trade direction: a BuyDirection when bullish, a SellDirection when bearish, none with no direction | TradeDirection |
| Know its reference timeframe: the highest timeframe that voted with its direction, in the order H4, H1, M5, M1 (FR9) | Timeframe |

### TradePlan

| Responsibilities | Collaborators |
|---|---|
| Know the valid signal it is based on | Signal |
| Own a trade setup with its entry, stop loss, and take profit (TP1), in the signal's trade direction | TradeSetup, TradeDirection |
| Know its TP2, beyond TP1 in its trade direction | TradeDirection |
| Reject a reward-to-risk ratio (to TP1) below 2, rounded to 2 decimals before comparing (FR2) | |
| Know its lot size and its stop-loss distance in pips | CurrencyPair |
| Know its risk amount: lot size × stop-loss pips × pip value per lot, rounded to cents (FR9) | CurrencyPair |
| Require its risk amount not to exceed the account's maximum risk amount (FR9) | Account |
| Require a USD account and reject a cross pair (FR9) | Account, CurrencyPair |
| Require a lot size of at least 0.01, in steps of 0.01 (FR9) | |
| Know its reference timeframe from its signal (FR9) | Signal |

### TradePlanBuilder

| Responsibilities | Collaborators |
|---|---|
| Collect a trade plan's signal, account, entry, stop loss, TP1, TP2, and lot size, one part at a time | |
| Build the TradePlan, or reject a build with any part missing, naming the missing parts | TradePlan |
| Add no rules of its own: the TradePlan it builds does all the validation | TradePlan |

### Account

| Responsibilities | Collaborators |
|---|---|
| Know its account ID, balance, and currency | |
| Know its environment and reject any environment other than practice (FR5) | |
| Know its risk percent, greater than 0 and at most 2 (FR9) | |
| Know its maximum risk amount per trade | |
| Know its trades, add or remove one, and know its open and its closed trades (FR11) | Trade |
| Accept only a trade whose order is for this account and has no recorded trade yet (one trade per order) | Trade, Order |
| Replace an open trade it holds with the closed trade for the same order (FR11) | Trade |

### Order

| Responsibilities | Collaborators |
|---|---|
| Know the trade plan it was created from | TradePlan |
| Know the account it is for, which must be its trade plan's account and a practice account (FR10) | Account |
| Know that its type is market | |
| Require the trader's explicit confirmation (FR10) | |
| Know its units: lot size × 100,000 times its direction's units sign (positive for a buy, negative for a sell) | TradeDirection |

### Trade

| Responsibilities | Collaborators |
|---|---|
| Know the order that opened it | Order |
| Know its outcome: win, loss, or open (FR11), where a win has an R multiple above 0 and a loss an R multiple below 0 | |
| Know its exit price once closed | |
| Know its R multiple (FR11): the price move from entry to exit in its trade direction, divided by its setup's risk; none while open | TradeDirection |

### rank_pairs (function)

| Responsibilities | Collaborators |
|---|---|
| Rank currency pairs by the win rate of each pair's most recent backtest result; pairs with no result or zero trades last; ties keep input order (FR4) | CurrencyPair, BacktestResult |
| Reject a currency pair passed more than once | CurrencyPair |

## Relationships and Multiplicities

| From | Relationship | To | Multiplicity | Classification |
|---|---|---|---|---|
| CurrencyPair | has | TradeSetup | `1` to `0..*` | Association |
| CurrencyPair | has | BacktestResult | `1` to `0..*` | Association |
| BacktestResult | is based on | TradeSetup | `0..1` to `0..*` | Aggregation |
| TradeSetup | follows the rules of | TradeDirection | `0..*` to `1` | Association |
| CurrencyPair | has | Candle | `1` to `0..*` | Association |
| CurrencyPair | has | SwingPoint | `1` to `0..*` | Association |
| CurrencyPair | has | TimeframeAnalysis | `1` to `0..*` | Association |
| StructureEvent | breaks | SwingPoint | `0..1` to `1` | Association |
| TimeframeAnalysis | knows its most recent | StructureEvent | `0..*` to `0..1` | Association |
| Signal | combines (as m1, m5, h1, h4) | TimeframeAnalysis | `0..*` to `4` | Aggregation |
| TradePlan | is based on | Signal | `0..1` to `1` | Association |
| TradePlan | owns | TradeSetup | `1` to `1` | Composition |
| TradePlan | is sized for | Account | `0..*` to `1` | Association |
| Order | is created from | TradePlan | `0..1` to `1` | Association |
| Order | is for | Account | `0..*` to `1` | Association |
| Trade | is opened by | Order | `0..1` to `1` | Association |
| Account | records | Trade | `1` to `0..*` | Aggregation |

- Each trade setup belongs to exactly one currency pair. A pair can have no setups.
- Each backtest result belongs to exactly one currency pair. A pair can have no backtest results yet.
- A backtest result is based on zero or more trade setups, since a test may find none. A trade setup belongs to at most one backtest result, because a live suggestion is not part of any backtest.
- All trade setups in a backtest result must belong to the same currency pair as that backtest result.
- Each TradeSetup and each BacktestResult holds a reference to its CurrencyPair. The CurrencyPair–BacktestResult association is two-way from Phase 06: a CurrencyPair holds its backtest results in a private list (FR4). It accepts a result only if the result's currency pair is the same object as itself, it does not already hold that result, and the result is not dated earlier than its most recent one. The CurrencyPair–TradeSetup association stays one-way.
- A BacktestResult holds its trade setups in a private list. It accepts a setup only if the setup's currency pair is the same object as its own and it does not already hold that setup. It returns the setups as a tuple.
- That a trade setup belongs to at most one backtest result is documented only. It is not enforced, because a setup holds no reference to its backtest results.
- Candle, SwingPoint, and TimeframeAnalysis each hold a one-way reference to their CurrencyPair. They stay deliberately one-way, because no requirement needs a currency pair to navigate to them.
- A Signal holds four named references to TimeframeAnalysis objects, m1, m5, h1, and h4, not a collection.
- A TradePlan creates and owns its TradeSetup. The setup does not exist without the plan.
- An Account records its trades in a private list (FR11). It accepts a trade only if the trade's order is for this account (the same object) and it records no trade for that order yet, so each order has at most one recorded trade. Because a Trade cannot change, an open trade is closed by replacing it with the closed Trade for the same order; that is the only way to replace a recorded trade.
- Order → Account and TradePlan → Account stay deliberately one-way. An Account reaches its orders through its trades.

## Inheritance

| Subclass | Relationship | Superclass |
|---|---|---|
| BuyDirection | is a | TradeDirection |
| SellDirection | is a | TradeDirection |
| BreakOfStructure | is a | StructureEvent |
| ChangeOfCharacter | is a | StructureEvent |

- BuyDirection and SellDirection exist because FR2 gives every trade setup a direction, buy or sell, and the two directions need opposite rules.
- TradeDirection is an abstract base class, so a bare TradeDirection cannot be created; only BuyDirection and SellDirection can.
- TradeSetup is a concrete class. It holds the currency pair, the entry price, the stop loss, the take profit, price validation, and the reward-to-risk ratio, and it delegates everything that differs by direction to its TradeDirection.
- StructureEvent is an abstract base class, so a bare StructureEvent cannot be created; only BreakOfStructure and ChangeOfCharacter can.
- BreakOfStructure and ChangeOfCharacter exist because FR7 separates a break with the trend from a break against it. StructureEvent holds the broken swing point, the time, the close price, the direction, and the check that the close is beyond the swing point. Each subclass supplies which swing labels it may break.

## Interfaces

| Interface | Abstract method | Implemented by | Used through the interface by | Requirement |
|---|---|---|---|---|
| TradeDirection | name, check_price_order(), reward(), risk(), outcome(), is_beyond(), units_sign | BuyDirection, SellDirection | TradeSetup (delegation), TradePlan (is_beyond for TP2), Order and Trade (units_sign) | FR2, FR3, FR9, FR10, FR11 |

- TradeSetup.outcome() returns its direction's outcome for the setup's stop loss and take profit on its currency pair's price data. evaluate_setup(setup: TradeSetup) still accepts any TradeSetup and returns its outcome, without knowing its direction.
- outcome() returns "win", "loss", or "open" by reading the setup's currency pair price data from the first price point.
- A buy wins when a high reaches its take profit and loses when a low reaches its stop loss. A sell is the mirror: it wins when a low reaches its take profit and loses when a high reaches its stop loss.
- If one price point touches both the take profit and the stop loss, the outcome is a loss. If neither is reached, the outcome is "open".

## Composition over Inheritance

- Phase 04 made BuySetup and SellSetup subclasses of TradeSetup only to change the direction rules, while TradePlan, Order, and Trade still branched on the "buy" and "sell" strings for TP2, the units sign, and the R multiple. A new direction-dependent rule therefore had to be added in four or five places, and TradeSetup's constructor called a method that subclasses overrode before their own state existed (Phase 04 finding 6).
- TradeSetup now holds a TradeDirection object and delegates to it, so every direction rule lives in BuyDirection or SellDirection, TradePlan, Order, and Trade ask the same object instead of branching, and the direction exists before the price-order check runs.

## Object Creation

- A TradePlan has seven parts. `TradePlanBuilder` (Phase 08, Builder) collects them one at a time and builds the TradePlan, so a plan is assembled step by step and a missing part is named. The caller passes every value: the builder reads no files and calls no API.
- Direct construction stays everywhere else. Each other class has a short constructor with no optional parts, and `Signal.trade_direction()` is the only place in the domain that chooses between `BuyDirection` and `SellDirection`, so no Factory was added in Phase 08.
