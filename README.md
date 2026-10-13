# NEXUS Trade

NEXUS Trade is an automated forex trading system built around Smart Money Concepts (SMC) — market structure, order blocks, fair value gaps (FVGs), break of structure / change of character (BOS/CHoCH), and multi-timeframe confluence — integrated with the OANDA API for live market data and trade execution.

## How it works

The system runs a structured pipeline, each stage backed by a documented workflow and a deterministic Python tool:

1. **Fetch candles** — pull fresh OHLC data from OANDA across M1, M5, H1, and H4 for the watched pairs
2. **Run structural analysis** — detect swing highs/lows, label HH/HL/LH/LL, identify BOS/CHoCH events, determine trend, and detect channels
3. **Score confluence** — cross-reference all 4 timeframes; only flag a setup when at least 3 of 4 agree on direction
4. **Generate a trade plan** — compute entry, stop loss, take profit, R:R ratio, and position size from account balance and risk %, gated on R:R ≥ 2
5. **Generate a summary** — use the Claude API to explain, in plain English, why a setup is valid, what invalidates it, and what to watch
6. **Backtest** — replay historical candles bar-by-bar and report win rate, average R, max drawdown, profit factor, and equity curve
7. **Monitor pairs** — continuously scan the watchlist on a schedule and push a notification when a new signal clears the confluence threshold

A weekly scheduler switches between live monitoring on weekdays and backtesting on weekends.

## Tech stack

- **Backend:** Python, FastAPI (serves the analysis pipeline to the app), pandas/numpy/scipy for analysis, `oandapyV20` for the OANDA API, Anthropic Claude API for trade summaries
- **Frontend:** React Native (Expo) mobile app for monitoring signals, trade plans, and charts
- **Architecture:** "Workflows, Agents, Tools" (WAT) pattern — Markdown SOPs in `workflows/`, deterministic Python tools organized by stage in `tools/` (oanda, analysis, confluence, trade_plan, ai, backtest, reporting, scheduler)
- **Testing:** pytest

## Project structure

```
NEXUS Trade/
├── tools/
│   ├── oanda/          # candles, instruments, account, execution, price streaming
│   ├── analysis/        # swing detection, trend, BOS/CHoCH, channels
│   ├── confluence/      # multi-timeframe confluence scoring
│   ├── trade_plan/      # entry, SL/TP, lot sizing
│   ├── ai/               # Claude-generated trade summaries
│   ├── backtest/         # candle replay, signal simulation, stats
│   ├── reporting/        # trade journal, loss analysis, email reports
│   ├── scheduler/        # weekly weekday/weekend cycle
│   └── api/               # FastAPI server bridging Python pipeline to the app
├── frontend/             # React Native (Expo) app
├── workflows/            # 7 numbered SOPs, one per pipeline stage
├── tests/                # pytest suite
├── run_nexus.sh          # starts the FastAPI server + scheduler together
└── requirements.txt
```

## Getting started

**Backend**

```bash
pip install -r requirements.txt
./run_nexus.sh                       # default pairs, 5-minute interval
./run_nexus.sh --interval 60         # custom polling interval
./run_nexus.sh --pairs EUR_USD GBP_USD
```

This starts the FastAPI server on `:8000` plus the weekly monitoring/backtest scheduler. Requires an `OANDA_API_KEY` (and related config) in a `.env` file.

**Frontend**

```bash
cd frontend
npm install
npm start
```

## Status

Actively in development — trading forex on an OANDA demo account while the SMC signal logic, backtesting, and reporting are refined. Not yet live with real funds.

## Disclaimer

This project is for research and educational purposes. Trading forex carries substantial risk, and nothing here constitutes financial advice.
