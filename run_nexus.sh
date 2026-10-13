#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# NEXUS Trade — startup script
# Launches FastAPI server + price monitor in parallel.
# Usage:
#   ./run_nexus.sh                    # default pairs + 5-min interval
#   ./run_nexus.sh --interval 60      # poll every 60 seconds
#   ./run_nexus.sh --pairs EUR_USD GBP_USD
# ─────────────────────────────────────────────────────────────

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# ── Defaults ───────────────────────────────────────────────────
INTERVAL=300
PAIRS=("EUR_USD" "GBP_USD" "USD_JPY" "AUD_USD" "USD_CAD")

# ── Argument parsing ───────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --interval)
      INTERVAL="$2"; shift 2 ;;
    --pairs)
      shift
      PAIRS=()
      while [[ $# -gt 0 && "$1" != --* ]]; do
        PAIRS+=("$1"); shift
      done ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1 ;;
  esac
done

# ── Environment check ──────────────────────────────────────────
if [[ ! -f ".env" ]]; then
  echo "ERROR: .env file not found in $PROJECT_DIR" >&2
  exit 1
fi

source .env 2>/dev/null || true

if [[ -z "${OANDA_API_KEY:-}" ]]; then
  echo "ERROR: OANDA_API_KEY not set in .env" >&2
  exit 1
fi

# ── .tmp directories ───────────────────────────────────────────
mkdir -p .tmp/candles .tmp/analysis .tmp/signals .tmp/backtest

# ── Colours ────────────────────────────────────────────────────
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RESET='\033[0m'

echo -e "${CYAN}"
echo "  ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗"
echo "  ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝"
echo "  ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗"
echo "  ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║"
echo "  ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║"
echo "  ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝"
echo -e "${RESET}"
echo -e "${GREEN}NEXUS Trade — starting up${RESET}"
echo    "  Pairs    : ${PAIRS[*]}"
echo    "  Interval : ${INTERVAL}s"
echo    "  Env      : ${OANDA_ENV:-practice}"
echo

# ── PID tracking ───────────────────────────────────────────────
PIDS=()

cleanup() {
  echo -e "\n${YELLOW}Shutting down NEXUS Trade...${RESET}"
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
  echo "Bye."
}
trap cleanup INT TERM

# ── 1. FastAPI server ──────────────────────────────────────────
echo -e "${GREEN}[1/2] Starting FastAPI server on :8000${RESET}"
uvicorn tools.api.server:app \
  --host "${API_HOST:-0.0.0.0}" \
  --port "${API_PORT:-8000}" \
  --log-level info \
  &
PIDS+=($!)
SERVER_PID=$!

# Give the server a moment to bind
sleep 2

if ! kill -0 "$SERVER_PID" 2>/dev/null; then
  echo "ERROR: FastAPI server failed to start. Check logs above." >&2
  exit 1
fi
echo "  → http://localhost:${API_PORT:-8000}"
echo

# ── 2. Weekly cycle scheduler ──────────────────────────────────
DAY=$(python3 -c "from datetime import datetime,timezone; print('WEEKEND' if datetime.now(timezone.utc).weekday()>=5 else 'WEEKDAY')")
echo -e "${GREEN}[2/2] Starting weekly scheduler (today is ${DAY})${RESET}"
if [[ "$DAY" == "WEEKEND" ]]; then
  echo -e "${YELLOW}  → Weekend mode: running backtests then waiting for Monday${RESET}"
else
  echo -e "${GREEN}  → Weekday mode: live signal monitoring every ${INTERVAL}s${RESET}"
fi
python3 -m tools.scheduler.weekly_cycle \
  --pairs "${PAIRS[@]}" \
  --interval "$INTERVAL" \
  &
PIDS+=($!)
echo

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${GREEN}NEXUS Trade is running. Press Ctrl+C to stop.${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo

# Wait for all background processes
wait
