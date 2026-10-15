# NEXUS Trade

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white)
![React Native](https://img.shields.io/badge/React%20Native-Expo-61DAFB?logo=react&logoColor=black)
![OANDA](https://img.shields.io/badge/OANDA-Demo%20Account-orange)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Tests](https://img.shields.io/badge/Tests-pytest-0A9EDC?logo=pytest&logoColor=white)

NEXUS Trade is an automated forex trading system built in Python around Smart Money Concepts (SMC): market structure, order blocks, fair value gaps (FVGs), break of structure / change of character (BOS/CHoCH), and multi-timeframe confluence. It connects to the OANDA API for live market data and trade execution.

The project follows the same software-engineering process as SFSU CSC 413 (Software Development): requirements first, then a domain model, then objects, design patterns, architecture, and testing.

> **Status:** Actively in development. Runs only against an OANDA **demo** account. Not live with real funds.

---

## How It Works

NEXUS runs a seven-stage pipeline. Each stage has a documented workflow in `workflows/` and a deterministic Python tool in `tools/`.

| Stage | What it does |
|---|---|
| 1. Fetch candles | Pull OHLC data from OANDA on M1, M5, H1, and H4 for each watched pair |
| 2. Structural analysis | Detect swing highs/lows, label HH/HL/LH/LL, find BOS/CHoCH, determine trend, detect channels |
| 3. Confluence scoring | Compare all 4 timeframes and flag a setup only when at least 3 of 4 agree on direction |
| 4. Trade plan | Compute entry, stop loss, take profit, R:R, and position size from balance and risk %. A plan is only produced when R:R ≥ 2 |
| 5. AI summary | Use the Claude API to explain in plain English why the setup is valid, what invalidates it, and what to watch |
| 6. Backtest | Replay historical candles bar by bar and report win rate, average R, max drawdown, profit factor, and equity curve |
| 7. Monitor | Scan the watchlist on a schedule and push a notification when a new signal clears the confluence threshold |

A weekly scheduler runs live monitoring on weekdays and backtesting on weekends.

---

## Requirements

### User stories
- As a trader, I want to see the current trend on each timeframe so I know which direction to trade.
- As a trader, I want to be alerted only when at least 3 of 4 timeframes agree, so I avoid weak setups.
- As a trader, I want every trade plan to include entry, SL, TP, and position size, so I never risk more than my set percentage.
- As a trader, I want to backtest a strategy on past data before using it on my demo account.
- As a trader, I want a plain-English summary of each setup so I understand why it was flagged.

### Constraints
- Only the OANDA practice (demo) environment is used.
- API keys live in `.env` and are never committed to Git.
- No trade plan is produced with R:R below 2.

---

## Domain Model

| Class | Responsibility |
|---|---|
| `Instrument` | A currency pair, such as EUR_USD |
| `Candle` | One OHLC bar with time and timeframe |
| `Chart` | A series of candles for one instrument and timeframe |
| `SwingPoint` | A swing high or low, labeled HH/HL/LH/LL |
| `StructureEvent` | A BOS or CHoCH |
| `Signal` | A detected setup with direction and confluence score |
| `TradePlan` | Entry, SL, TP, R:R, and position size |
| `Order` | An order sent to the broker (market, limit, or stop) |
| `Trade` | An open or closed position |
| `Account` | Balance, risk %, and trades |

Domain classes live in `tools/models/`. Design diagrams live in `docs/design/`.

---

## Design Highlights

| Concept | Where it is used |
|---|---|
| Inheritance | `Order` → `MarketOrder`, `LimitOrder`, `StopOrder` |
| Interfaces & polymorphism | `Strategy` abstract base class → `FvgStrategy`, `BosStrategy`, `OrderBlockStrategy` |
| Factory | `OrderFactory` creates the right order type |
| Builder | `TradePlanBuilder` assembles entry, SL, TP, and size step by step |
| Adapter | `OandaAdapter` implements a `BrokerGateway` interface, so a `FakeBroker` can be swapped in for tests |
| Facade | `TradingFacade` exposes one simple call for the whole pipeline |
| MVC | Model = domain classes, View = React Native app, Controller = FastAPI routes |

---

## Tech Stack

- **Backend:** Python, FastAPI, pandas / numpy / scipy, `oandapyV20`, Anthropic Claude API
- **Frontend:** React Native (Expo) mobile app for signals, trade plans, and charts
- **Architecture:** "Workflows, Agents, Tools" (WAT): Markdown SOPs in `workflows/`, deterministic Python tools in `tools/`
- **Testing:** pytest

---

## Project Structure

```
NEXUS Trade/
├── docs/
│   ├── requirements/     # user stories, constraints
│   ├── design/           # domain model, class diagrams, design decisions
│   └── evolution/        # what changed in each phase and why
├── tools/
│   ├── models/           # Candle, Instrument, Signal, Trade, Account...
│   ├── oanda/            # candles, instruments, account, execution, streaming
│   ├── analysis/         # swing detection, trend, BOS/CHoCH, channels
│   ├── strategy/         # Strategy base class and SMC strategies
│   ├── confluence/       # multi-timeframe confluence scoring
│   ├── trade_plan/       # TradePlanBuilder, entry, SL/TP, lot sizing
│   ├── ai/               # Claude-generated trade summaries
│   ├── backtest/         # candle replay, signal simulation, stats
│   ├── reporting/        # trade journal, loss analysis, email reports
│   ├── scheduler/        # weekly weekday/weekend cycle
│   ├── utils/            # shared helpers
│   └── api/              # FastAPI server (controllers)
├── frontend/             # React Native (Expo) app (view)
├── web/                  # web front end
├── workflows/            # 7 numbered SOPs, one per pipeline stage
├── phases/               # build phases 00–12 (how NEXUS is developed)
├── tests/                # pytest suite
├── .env.example          # template for API keys (real .env is git-ignored)
├── AGENTS.md             # rules for AI coding assistants
├── CLAUDE.md             # points Claude Code to AGENTS.md
├── run_nexus.sh          # starts the FastAPI server + scheduler together
└── requirements.txt
```

---

## Development Roadmap

| Phase | Topic | Nexus deliverable | Status |
|---|---|---|---|
| 00 | Environment and Setup | Virtual env, `.gitignore`, `.env.example`, `docs/`, executive summary | ⬜ |
| 01 | Requirements and Domain Modeling | User stories and domain model in `docs/` | ⬜ |
| 02 | From Design to Objects | Phase 01 entities as Python classes in `tools/models/` | ⬜ |
| 03 | Connecting Objects | Object references between domain classes (no collections yet) | ⬜ |
| 04 | Inheritance | One superclass with at least two subclasses | ⬜ |
| 05 | Polymorphism and Interfaces | One interface (ABC) used polymorphically, plus domain expansion | ⬜ |
| 06 | Growing the Object Model | Typed collections, composition over inheritance, full domain review | ⬜ |
| 07 | Evaluating OO Design | Design review notes in `docs/design/` | ⬜ |
| 08 | Factory and Builder | `OrderFactory`, `TradePlanBuilder` | ⬜ |
| 09 | Adapter and Facade | `OandaAdapter`, `TradingFacade` | ⬜ |
| 10 | Refactoring and SOLID | Clean-up based on phase 07 review | ⬜ |
| 11 | Architecture and MVC | FastAPI controllers + React Native views | ⬜ |
| 12 | Testing and Evolution | pytest suite and backtesting engine | ⬜ |

Each phase ends with a Git checkpoint and a short entry in `docs/evolution/`.

---

## Getting Started

### Backend

```bash
pip install -r requirements.txt
cp .env.example .env                 # add your OANDA practice API key and account ID
./run_nexus.sh                       # default pairs, 5-minute interval
./run_nexus.sh --interval 60         # custom polling interval
./run_nexus.sh --pairs EUR_USD GBP_USD
```

This starts the FastAPI server on `:8000` plus the weekly monitoring/backtest scheduler.

### Frontend

```bash
cd frontend
npm install
npm start
```

### Tests

```bash
pytest
```

---

## Disclaimer

This project is for research and educational purposes. Forex trading carries substantial risk, and nothing here is financial advice.
