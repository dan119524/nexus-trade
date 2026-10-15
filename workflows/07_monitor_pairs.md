# Workflow 07 · Monitor Pairs

## Objective

Run a continuous loop that scans every pair in the watchlist on a schedule. When a new valid signal appears (score ≥ 3), build the trade plan and send a push notification to all registered devices.

## Pipeline Position

Runs Workflows 01 → 02 → 03 → 04 for each pair on a schedule, then notifies. Runs on weekdays via the scheduler.

## Requirements Trace

Traces to the functional requirements in `docs/design/requirements.md` for monitoring the watchlist and alerting only when 3 of 4 timeframes agree. Add the requirement IDs here once Phase 01 defines them.

## Permissions

| Activity | Agent |
|---|---|
| Start, stop, or restart the monitor on the **practice** account | Allowed |
| Send a test notification | Allowed |
| Change the watchlist or interval | Ask Daniel first |
| Start a 24/7 background process (`nohup`, `pm2`) | Ask Daniel first |
| Place, modify, or close an order | **Never** (this workflow only alerts) |
| Print, log, or commit a push token | **Never** |

---

## Tool

`tools/oanda/stream_prices.py`

## Usage

**Default** (6 major pairs, every 5 minutes):

```bash
python -m tools.oanda.stream_prices
```

**Custom pairs and interval:**

```bash
python -m tools.oanda.stream_prices \
  --pairs EUR_USD GBP_USD USD_JPY AUD_USD EUR_GBP \
  --interval 300
```

**With push notifications:** get your Expo push token from the app console when it starts, then:

```bash
python -m tools.oanda.stream_prices \
  --pairs EUR_USD GBP_USD USD_JPY \
  --push-token "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]"
```

**Through the API:** when the app has already registered its token, run the loop from Python and the server uses its registered token list automatically.

## Default Watchlist

```
EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, EUR_GBP
```

---

## Scan Cycle (per pair)

```
1. fetch_all_timeframes(pair, count=300)   → .tmp/candles/
2. run_full_analysis(pair)                 → .tmp/analysis/
3. run_confluence_for_pair(pair)           → .tmp/signals/ (if score ≥ 3)
4. build_trade_plan(pair)                  → attaches plan to signal
5. send_push_notification(token, ...)      → only if the signal is new
```

## Push Notification Flow

1. App starts → `usePushNotifications()` requests permission
2. Token is posted to `POST /push/register` on the NEXUS server
3. The monitor calls `notify_new_signal()`, which hits Expo's push API
4. Device receives: pair, direction, entry/SL/TP, R:R

## Signal De-duplication

Each signal has a unique ID (`pair_YYYYMMDD_HHMM`). `SignalTracker` remembers which IDs were already sent this session, so the same signal is never pushed twice across cycles.

---

## Steps

### 1. Test notifications

With the server running and the app open:

```
POST http://localhost:8000/push/test
```

- [ ] a test notification arrives on the device

### 2. Start the monitor

Use one of the commands in **Usage**.

### 3. Verify the first cycle

- [ ] every watchlist pair is scanned (check the log)
- [ ] a failing pair is logged and skipped without stopping the loop
- [ ] any new valid signal has a trade plan and triggers exactly one notification

---

## Edge Cases

| Situation | How to handle |
|---|---|
| OANDA rate limit (429) | `fetch_candles` logs a warning and skips that pair this cycle. |
| A pair scan throws an error | Log it and move to the next pair. Never crash the loop. |
| No push token registered | Signals still save to `.tmp/` and show through the API. Push is skipped. |
| Push delivery fails | Log a warning and continue. Expo delivery is best-effort. |
| Signal already active | `SignalTracker` blocks a duplicate push. The signal file updates in place. |

---

## Running 24/7 (ask Daniel first)

On macOS, keep it running after the terminal closes:

```bash
nohup python -m tools.oanda.stream_prices --interval 300 > monitor.log 2>&1 &
```

Or with `pm2`:

```bash
pm2 start "python -m tools.oanda.stream_prices" --name nexus-monitor
```

Make sure `monitor.log` is in `.gitignore`.

---

## Tests

- No tests exist yet. Add them in `tests/test_monitor_pairs.py`.
- Use a fake broker and a fake push sender. Never call OANDA or Expo.
- Cover: one pair failing doesn't stop the others, de-duplication across cycles, no push when no token is registered, no push when score < 3.

## Done When

The monitor completes full cycles over the watchlist, and new valid signals produce exactly one notification each.

---

## Notes

- A full 6-pair cycle takes about 10–20 seconds because of OANDA calls.
- The interval timer starts **after** a cycle finishes, not when it starts.
- Signals update every cycle. If confluence drops below 3, the signal file stays but no new push is sent.
- `SignalTracker` only remembers IDs for the current session. After a restart, an active signal could be pushed again.

## Change Log

| Date | Change | Why |
|---|---|---|
| | | |
