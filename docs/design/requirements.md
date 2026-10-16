# NEXUS Trade Requirements and Initial Domain Model

## Domain Entities

| Entity | Description |
|---|---|
| **CurrencyPair** | A forex market NEXUS analyzes, such as EUR_USD, together with its past price data and its current market structure. |
| **TradeSetup** | A suggested trade on one currency pair, with a direction, an entry price, a stop loss, and a take profit. |
| **BacktestResult** | The outcome of testing trade setups on one currency pair's past price data, showing how well they would have performed. |

## Use Cases

| ID | Actor | Goal |
|---|---|---|
| UC1 | Trader | Review the market structure of a currency pair |
| UC2 | Trader | Review a suggested trade setup before deciding whether to act on it |
| UC3 | Trader | Backtest trade setups for a currency pair on past price data |
| UC4 | Trader | See which currency pairs performed best in backtests |

## Functional Requirements

| ID | Requirement | Use case |
|---|---|---|
| FR1 | NEXUS shall identify the market structure of a selected currency pair as uptrend, downtrend, or ranging, using that pair's past price data. An uptrend means every price point has a higher high and a higher low than the one before it. A downtrend means every price point has a lower high and a lower low than the one before it. Anything else, including any equal high or low, is ranging. | UC1 |
| FR2 | NEXUS shall suggest trade setups for a currency pair, each with a direction (buy or sell), an entry price, a stop loss, and a take profit, and shall not suggest any setup with a reward-to-risk ratio below 2. For a buy, stop loss < entry < take profit. For a sell, take profit < entry < stop loss. | UC2 |
| FR3 | NEXUS shall backtest trade setups for a currency pair on past price data and report the number of trades and the win rate. A win is a trade that hits its take profit before its stop loss. | UC3 |
| FR4 | NEXUS shall rank currency pairs from best to worst by the win rate of each pair's most recent backtest result. Pairs with zero trades or no backtest result are ranked last. | UC4 |
| FR5 | NEXUS shall work only with an OANDA practice account and shall never trade real money. | All |

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
| Know its direction, entry price, stop loss, and take profit | |
| Know its reward-to-risk ratio | |

### BacktestResult

| Responsibilities | Collaborators |
|---|---|
| Know which currency pair was tested | CurrencyPair |
| Know which trade setups were tested | TradeSetup |
| Know its number of trades and its win rate | |
| Know when the test was run | |
| Know the number of wins | |

## Relationships and Multiplicities

| From | Relationship | To | Multiplicity |
|---|---|---|---|
| CurrencyPair | has | TradeSetup | `1` to `0..*` |
| CurrencyPair | has | BacktestResult | `1` to `0..*` |
| BacktestResult | is based on | TradeSetup | `0..1` to `0..*` |

- Each trade setup belongs to exactly one currency pair. A pair can have no setups.
- Each backtest result belongs to exactly one currency pair. A pair can have no backtest results yet.
- A backtest result is based on zero or more trade setups, since a test may find none. A trade setup belongs to at most one backtest result, because a live suggestion is not part of any backtest.
- All trade setups in a backtest result must belong to the same currency pair as that backtest result.
