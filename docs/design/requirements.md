# NEXUS Trade Requirements and Initial Domain Model

## Domain Entities

| Entity | Description |
|---|---|
| **CurrencyPair** | A forex market NEXUS analyzes, such as EUR/USD, together with its past price data and its current market structure. |
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
| FR1 | NEXUS shall identify the market structure of a selected currency pair as uptrend, downtrend, or ranging, using that pair's past price data. | UC1 |
| FR2 | NEXUS shall suggest trade setups for a currency pair, each with a direction (buy or sell), an entry price, a stop loss, and a take profit. | UC2 |
| FR3 | NEXUS shall not suggest any trade setup whose risk is greater than the set risk limit. | UC2 |
| FR4 | NEXUS shall backtest trade setups for a currency pair on past price data and report the number of trades and the win rate. | UC3 |
| FR5 | NEXUS shall rank currency pairs from best to worst by their backtest win rate. | UC4 |

## CRC Analysis

### CurrencyPair

| Responsibilities | Collaborators |
|---|---|
| Know its name (for example, EUR/USD) | TradeSetup |
| Know its past price data | BacktestResult |
| Know its current market structure | |

### TradeSetup

| Responsibilities | Collaborators |
|---|---|
| Know which currency pair it belongs to | CurrencyPair |
| Know its direction, entry price, stop loss, and take profit | |
| Know whether its risk is within the set risk limit | |

### BacktestResult

| Responsibilities | Collaborators |
|---|---|
| Know which currency pair was tested | CurrencyPair |
| Know which trade setups were tested | TradeSetup |
| Know its number of trades and its win rate | |

## Relationships and Multiplicities

| From | Relationship | To | Multiplicity |
|---|---|---|---|
| CurrencyPair | has | TradeSetup | `1` to `0..*` |
| CurrencyPair | has | BacktestResult | `1` to `0..*` |
| BacktestResult | is based on | TradeSetup | `0..1` to `0..*` |

- Each trade setup belongs to exactly one currency pair. A pair can have no setups.
- Each backtest result belongs to exactly one currency pair. A pair can have no backtest results yet.
- A backtest result is based on zero or more trade setups, since a test may find none. A trade setup belongs to at most one backtest result, because a live suggestion is not part of any backtest.
