# NEXUS Trade Requirements and Initial Domain Model

## Domain Entities

| Entity | Description |
|---|---|
| **CurrencyPair** | A forex market NEXUS analyzes, such as EUR_USD, together with its past price data and its current market structure. |
| **TradeSetup** | A suggested trade on one currency pair, with a direction, an entry price, a stop loss, and a take profit. Its direction comes from BuySetup or SellSetup. |
| **BuySetup** | A trade setup whose direction is buy. Its stop loss is below its entry, and its take profit is above it. |
| **SellSetup** | A trade setup whose direction is sell. Its take profit is below its entry, and its stop loss is above it. |
| **BacktestResult** | The outcome of testing trade setups on one currency pair's past price data, showing how well they would have performed. |
| **Candle** | One complete OHLC bar for a currency pair on one timeframe, with its time and volume. |
| **SwingPoint** | A confirmed swing high or swing low on one timeframe, labeled HH, HL, LH, or LL. |
| **StructureEvent** | A candle close beyond a labeled swing point, in a bullish or bearish direction. Its kind comes from BreakOfStructure or ChangeOfCharacter. |
| **BreakOfStructure** | A structure event that breaks a swing point with the trend: a close above an HH (bullish) or below an LL (bearish). |
| **ChangeOfCharacter** | A structure event that breaks a swing point against the trend: a close above an LH (bullish) or below an HL (bearish). |
| **TimeframeAnalysis** | The analysis of one currency pair on one timeframe: its trend, its most recent structure event, and the vote it casts. |
| **Signal** | A confluence result for one currency pair, combining the votes of its M1, M5, H1, and H4 analyses into a direction and a score. |
| **TradePlan** | The plan for a valid signal: a trade setup plus a second take profit, a lot size, a risk amount, and a reference timeframe. |
| **Account** | The OANDA practice account a trade plan is sized for, with its balance, currency, environment, and risk percent. |
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
| FR9 | For a valid signal, NEXUS shall produce a trade plan with entry, stop loss, TP1, TP2, and a lot size whose risk never exceeds the account's risk percent, capped at 2%. | UC2 |
| FR10 | NEXUS shall create only market orders, only for a practice account, and only after the trader's explicit confirmation. | UC6 |
| FR11 | NEXUS shall record each trade with its outcome (win, loss, or open) and its R multiple. | UC7 |

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

## Known Conflicts

| Conflict | Files | Decision |
|---|---|---|
| FR1 identifies market structure from every price point (each point must make a higher high and higher low). `detect_trend.py` counts the last 6 swing labels (at least 4 aligned means a trend) and returns bullish, bearish, or ranging. | `requirements.md` FR1, `tools/analysis/detect_trend.py` | FR1 stays as written. Resolve in Phase 06. |

## Model Rules

- Domain classes in `tools/models/` hold data and check rules only. They never call the OANDA API or the Claude API.
- Demos and tests use fake account IDs only.
- One-to-many relationships are not stored as lists, dicts, or sets until Phase 06.

## CRC Analysis

> **Note:** In Phase 01, the NEXUS system performs the actions in FR1, FR2, FR3, and FR4: identifying market structure, suggesting trade setups, backtesting, and ranking currency pairs. Responsible classes are assigned in later phases.

### CurrencyPair

| Responsibilities | Collaborators |
|---|---|
| Know its name (for example, EUR_USD) | |
| Know its past price data | |
| Know its current market structure | |

### TradeSetup

| Responsibilities | Collaborators |
|---|---|
| Know which currency pair it belongs to | CurrencyPair |
| Know its direction, entry price, stop loss, and take profit (direction comes from BuySetup or SellSetup) | |
| Know its reward-to-risk ratio | |
| Know its outcome (win, loss, or open) on its pair's price data (FR3; computed by BuySetup or SellSetup) | |

### BuySetup

| Responsibilities | Collaborators |
|---|---|
| Know that its direction is buy | |
| Require stop loss < entry < take profit | |
| Know its reward (take profit − entry) and its risk (entry − stop loss) | |
| Know its outcome: a win when a high reaches take profit, a loss when a low reaches stop loss | |

### SellSetup

| Responsibilities | Collaborators |
|---|---|
| Know that its direction is sell | |
| Require take profit < entry < stop loss | |
| Know its reward (entry − take profit) and its risk (stop loss − entry) | |
| Know its outcome: a win when a low reaches take profit, a loss when a high reaches stop loss | |

### BacktestResult

| Responsibilities | Collaborators |
|---|---|
| Know which currency pair was tested | CurrencyPair |
| Know which trade setups were tested | TradeSetup (Phase 06) |
| Know its number of trades and its win rate | |
| Know when the test was run | |
| Know the number of wins | |

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
| Know its trend: uptrend, downtrend, or ranging | |
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
| Know its trade direction (bullish leads to buy, bearish leads to sell) | |

### TradePlan

| Responsibilities | Collaborators |
|---|---|
| Know the valid signal it is based on | Signal |
| Own a trade setup with its entry, stop loss, and take profit (TP1), in the signal's trade direction | TradeSetup |
| Know its TP2, beyond TP1 | |
| Reject a reward-to-risk ratio (to TP1) below 2, rounded to 2 decimals before comparing (FR2) | |
| Know its lot size, its risk amount, and its reference timeframe | Timeframe |
| Require its risk amount not to exceed the account's risk percent of its balance (FR9) | Account |

### Account

| Responsibilities | Collaborators |
|---|---|
| Know its account ID, balance, and currency | |
| Know its environment and reject any environment other than practice (FR5) | |
| Know its risk percent, greater than 0 and at most 2 (FR9) | |
| Know its maximum risk amount per trade | |

### Order

| Responsibilities | Collaborators |
|---|---|
| Know the trade plan it was created from | TradePlan |
| Know the account it is for, which must be its trade plan's account and a practice account (FR10) | Account |
| Know that its type is market | |
| Require the trader's explicit confirmation (FR10) | |
| Know its units: lot size × 100,000, positive for a buy and negative for a sell | |

### Trade

| Responsibilities | Collaborators |
|---|---|
| Know the order that opened it | Order |
| Know its outcome: win, loss, or open (FR11), where a win has an R multiple above 0 and a loss an R multiple below 0 | |
| Know its exit price once closed | |
| Know its R multiple (FR11): the price move from entry to exit in its trade direction, divided by its setup's risk; none while open | |

## Relationships and Multiplicities

| From | Relationship | To | Multiplicity | Classification |
|---|---|---|---|---|
| CurrencyPair | has | TradeSetup | `1` to `0..*` | Association |
| CurrencyPair | has | BacktestResult | `1` to `0..*` | Association |
| BacktestResult | is based on | TradeSetup | `0..1` to `0..*` | Aggregation |
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

- Each trade setup belongs to exactly one currency pair. A pair can have no setups.
- Each backtest result belongs to exactly one currency pair. A pair can have no backtest results yet.
- A backtest result is based on zero or more trade setups, since a test may find none. A trade setup belongs to at most one backtest result, because a live suggestion is not part of any backtest.
- All trade setups in a backtest result must belong to the same currency pair as that backtest result.
- The two CurrencyPair associations are one-way: each TradeSetup and each BacktestResult holds a reference to its CurrencyPair, and a CurrencyPair holds no references to its setups or results.
- The BacktestResult–TradeSetup aggregation and the same-pair rule are implemented in Phase 06, when collections are introduced.
- Candle, SwingPoint, and TimeframeAnalysis each hold a one-way reference to their CurrencyPair. A CurrencyPair holds no references to them until Phase 06.
- A Signal holds four named references to TimeframeAnalysis objects, m1, m5, h1, and h4, not a collection.
- A TradePlan creates and owns its TradeSetup. The setup does not exist without the plan.
- An Account has zero or more Trades through its Orders. That collection waits for Phase 06.

## Inheritance

| Subclass | Relationship | Superclass |
|---|---|---|
| BuySetup | is a | TradeSetup |
| SellSetup | is a | TradeSetup |
| BreakOfStructure | is a | StructureEvent |
| ChangeOfCharacter | is a | StructureEvent |

- BuySetup and SellSetup exist because FR2 gives every trade setup a direction, buy or sell, and the two directions need opposite price orders.
- TradeSetup holds the state and behavior both directions share: the currency pair, the entry price, the stop loss, the take profit, price validation, and the reward-to-risk ratio (reward divided by risk).
- Each subclass supplies what differs by direction: its direction, its price-order check, its reward, and its risk.
- TradeSetup is an abstract base class, so a bare TradeSetup cannot be created; only BuySetup and SellSetup can. Its price-order check, direction, reward, risk, and outcome are abstract methods that each subclass implements.
- StructureEvent is an abstract base class, so a bare StructureEvent cannot be created; only BreakOfStructure and ChangeOfCharacter can.
- BreakOfStructure and ChangeOfCharacter exist because FR7 separates a break with the trend from a break against it. StructureEvent holds the broken swing point, the time, the close price, the direction, and the check that the close is beyond the swing point. Each subclass supplies which swing labels it may break.

## Interfaces

| Interface | Abstract method | Implemented by | Used through the interface by | Requirement |
|---|---|---|---|---|
| TradeSetup | outcome() | BuySetup, SellSetup | evaluate_setup(setup: TradeSetup) | FR3 |

- outcome() returns "win", "loss", or "open" by reading the setup's currency pair price data from the first price point.
- A buy wins when a high reaches its take profit and loses when a low reaches its stop loss. A sell is the mirror: it wins when a low reaches its take profit and loses when a high reaches its stop loss.
- If one price point touches both the take profit and the stop loss, the outcome is a loss. If neither is reached, the outcome is "open".
- evaluate_setup accepts any TradeSetup and returns its outcome, without knowing whether it is a BuySetup or a SellSetup.
