# Workflow 07 — Monitor Pairs

## Objective
Run a continuous multi-pair monitoring loop that scans all pairs in the watchlist on a schedule. When a new valid signal is detected (score ≥ 3), build the trade plan and send a push notification to all registered devices.

## Tool
`tools/oanda/stream_prices.py`

## Usage

### Basic (6 major pairs, check every 5 minutes)
```bash
python -m tools.oanda.stream_prices
```

### Custom pairs and interval
```bash
python -m tools.oanda.stream_prices \
  --pairs EUR_USD GBP_USD USD_JPY AUD_USD EUR_GBP \
  --interval 300
```

### With push notifications
First, get your device's Expo push token from the app (shown in the console when the app starts). Then:
```bash
python -m tools.oanda.stream_prices \
  --pairs EUR_USD GBP_USD USD_JPY \
  --push-token "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]"
```

### Via the API (push token already registered by app)
Alternatively, run the monitor loop programmatically from Python, and the server will use its registered token list automatically.

## Default Watchlist
```
EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, EUR_GBP
```

## Scan Cycle (per pair)
```
1. fetch_all_timeframes(pair, count=300)   → .tmp/candles/
2. run_full_analysis(pair)                 → .tmp/analysis/
3. run_confluence_for_pair(pair)           → .tmp/signals/ (if score >= 3)
4. build_trade_plan(pair)                  → attaches plan to signal
5. send_push_notification(token, ...)      → only if signal is new
```

## Push Notification Flow
1. App starts → `usePushNotifications()` hook requests permission
2. Token posted to `POST /push/register` on the NEXUS server
3. Monitor loop calls `notify_new_signal()` which hits Expo's push API
4. Device receives: pair, direction, entry/SL/TP levels, R:R

## Signal De-duplication
Each signal is assigned a unique ID (`pair_YYYYMMDD_HHMM`). The `SignalTracker` class remembers which IDs have been notified this session — the same signal is never pushed twice even across multiple scan cycles.

## Test Push Notifications
With the server running and app open:
```
POST http://localhost:8000/push/test
```
This sends a test notification to all registered devices immediately.

## Edge Cases

| Situation | How to Handle |
|-----------|--------------|
| OANDA rate limit (429) | `fetch_candles` logs a warning and skips the pair for this cycle |
| Pair scan throws error | Log error, continue to next pair — never crash the loop |
| No push token registered | Signals still saved to `.tmp/` and visible via API; push is silently skipped |
| Push delivery fails | Log warning, continue — Expo's service is best-effort |
| Signal already active | `SignalTracker` prevents duplicate pushes; signal file is updated in-place |

## Running in Production
For 24/7 operation, run the monitor in a persistent process. On macOS:
```bash
# Keep running even after terminal closes
nohup python -m tools.oanda.stream_prices --interval 300 > monitor.log 2>&1 &
```
Or use a process manager like `pm2`:
```bash
pm2 start "python -m tools.oanda.stream_prices" --name nexus-monitor
```

## Notes
- Each full cycle (6 pairs) takes approximately 10-20 seconds due to OANDA API calls
- The interval starts counting after the cycle completes (not from the start)
- Signals are updated on every cycle — if confluence drops below 3, the signal file remains but no new push is sent
