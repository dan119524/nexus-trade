/**
 * All HTTP calls to the FastAPI backend.
 * Change BASE_URL to your server IP when running on a physical device.
 */

import type {
  AccountInfo,
  Analysis,
  Candle,
  Signal,
  TradePlan,
  TimeframeAnalysis,
} from '../types';

// On iOS simulator / Android emulator use the machine's LAN IP.
// On a physical device, replace with your computer's local IP e.g. http://192.168.1.x:8000
export const BASE_URL = 'http://10.143.44.6:8000';

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body: Record<string, string>): Promise<T> {
  const params = new URLSearchParams(body);
  const res = await fetch(`${BASE_URL}${path}?${params}`, { method: 'POST' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ── Signals ───────────────────────────────────────────────────────────────────

export const fetchAllSignals = (): Promise<Signal[]> =>
  get<Signal[]>('/signals');

export const fetchSignal = (pair: string): Promise<Signal> =>
  get<Signal>(`/signals/${pair}`);

// ── Candles ───────────────────────────────────────────────────────────────────

export const fetchCandles = (
  pair: string,
  timeframe: string,
  limit = 100,
): Promise<Candle[]> =>
  get<Candle[]>(`/candles/${pair}/${timeframe}?limit=${limit}`);

// ── Analysis ──────────────────────────────────────────────────────────────────

export const fetchAnalysis = (pair: string): Promise<Analysis> =>
  get<Analysis>(`/analysis/${pair}`);

export const fetchTimeframeAnalysis = (
  pair: string,
  timeframe: string,
): Promise<TimeframeAnalysis & { pair: string; timeframe: string }> =>
  get(`/analysis/${pair}/${timeframe}`);

// ── Trade Plan ────────────────────────────────────────────────────────────────

export const fetchTradePlan = (pair: string): Promise<TradePlan> =>
  get<TradePlan>(`/trade-plan/${pair}`);

// ── Account ───────────────────────────────────────────────────────────────────

export const fetchAccount = (): Promise<AccountInfo> =>
  get<AccountInfo>('/account');

// ── Pairs ─────────────────────────────────────────────────────────────────────

export const fetchAvailablePairs = (): Promise<string[]> =>
  get<string[]>('/pairs');

export const fetchInstruments = (): Promise<string[]> =>
  get<string[]>('/instruments');

// ── Trade Execution ───────────────────────────────────────────────────────────

export const executeTradeDryRun = (pair: string): Promise<unknown> =>
  post(`/execute-trade/${pair}`, {});

export const executeTradeConfirm = (pair: string): Promise<unknown> =>
  post(`/execute-trade/${pair}`, { confirm: 'true' });

export const fetchOpenTrades = (pair?: string): Promise<unknown[]> =>
  get<unknown[]>(`/trades/open${pair ? `?pair=${pair}` : ''}`);

// ── Backtest ──────────────────────────────────────────────────────────────────

export const triggerBacktest = (
  pair: string,
  fromDate: string,
  toDate: string,
): Promise<{ run_id: string; status: string }> =>
  post('/backtest', { pair, from_date: fromDate, to_date: toDate });

export const fetchBacktestResults = (runId: string): Promise<unknown> =>
  get(`/backtest/${runId}`);
