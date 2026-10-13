// Core data types — mirror the Python data formats exactly

export interface Candle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  complete: boolean;
  granularity: string;
  pair: string;
}

export interface SwingPoint {
  type: 'high' | 'low';
  label: string; // HH | HL | LH | LL | first_high | first_low
  price: number;
  time: string;
  bar_index: number;
  confirmed: boolean;
}

export interface StructureEvent {
  event_type: 'BOS' | 'CHoCH';
  direction: 'bullish' | 'bearish';
  level: number;
  broken_at_time: string;
  broken_at_bar: number;
  source_swing: SwingPoint;
}

export interface Channel {
  resistance_slope: number;
  resistance_intercept: number;
  support_slope: number;
  support_intercept: number;
  channel_type: 'ascending' | 'descending' | 'horizontal';
  width: number;
}

export interface TimeframeAnalysis {
  candle_count: number;
  trend: 'bullish' | 'bearish' | 'ranging';
  swing_highs: SwingPoint[];
  swing_lows: SwingPoint[];
  structure: SwingPoint[];
  bos_events: StructureEvent[];
  choch_events: StructureEvent[];
  channel: Channel | Record<string, never>;
}

export interface Analysis {
  pair: string;
  generated_at: string;
  timeframes: Record<string, TimeframeAnalysis>;
}

export interface ConfluenceResult {
  score: number;
  weighted_score: number;
  max_score: number;
  direction: 'bullish' | 'bearish';
  votes: Record<string, string>;
  dissenting_timeframes: string[];
  neutral_timeframes: string[];
  signal_valid: boolean;
  min_score_required: number;
  pair: string;
  scored_at: string;
}

export interface TradePlan {
  pair: string;
  direction: 'bullish' | 'bearish';
  reference_timeframe: string;
  entry_price: number;
  stop_loss: number;
  take_profit_1: number;
  take_profit_2: number;
  sl_pips: number;
  risk_reward: number;
  lot_size: number;
  risk_amount_usd: number;
  risk_percent: number;
  account_balance: number;
  confluence_score: number;
  invalidation_note: string;
  generated_at: string;
}

export interface Signal {
  id: string;
  pair: string;
  status: 'pending_trade_plan' | 'active' | 'ready' | 'closed';
  confluence: ConfluenceResult;
  trade_plan: TradePlan | null;
  summary: string | null;
  created_at: string;
}

export interface AccountInfo {
  account_id: string;
  balance: number;
  nav: number;
  margin_used: number;
  margin_available: number;
  open_trade_count: number;
  currency: string;
  env: string;
}

export type Timeframe = 'M1' | 'M5' | 'H1' | 'H4';
export type Direction = 'bullish' | 'bearish';
