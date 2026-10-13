import React, { useState } from 'react';
import {
  View, Text, StyleSheet, SafeAreaView, ScrollView,
  TouchableOpacity, TextInput, ActivityIndicator,
} from 'react-native';
import { triggerBacktest, fetchBacktestResults } from '../api/nexusApi';

interface BacktestStats {
  total_trades: number;
  wins: number;
  losses: number;
  open: number;
  win_rate_pct: number;
  avg_r_multiple: number;
  total_r: number;
  max_drawdown_r: number;
  profit_factor: number;
  equity_curve: number[];
  best_trade_r: number;
  worst_trade_r: number;
}

interface BacktestTrade {
  signal_time: string;
  direction: string;
  entry_price: number;
  result: string;
  r_multiple: number;
  confluence_score: number;
}

interface BacktestResult {
  run_id: string;
  status: string;
  pair: string;
  from_date: string;
  to_date: string;
  windows_checked: number;
  stats: BacktestStats;
  trades: BacktestTrade[];
}

function StatBox({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <View style={styles.statBox}>
      <Text style={styles.statValue} numberOfLines={1} style={[styles.statValue, color ? { color } : undefined]}>
        {value}
      </Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

function EquityCurve({ curve }: { curve: number[] }) {
  if (!curve.length) return null;
  const max = Math.max(...curve, 0);
  const min = Math.min(...curve, 0);
  const range = Math.max(max - min, 1);
  const W = 280;
  const H = 80;
  const barW = Math.max(2, (W / curve.length) - 1);

  return (
    <View style={styles.curveContainer}>
      <Text style={styles.curveLabel}>EQUITY CURVE (R)</Text>
      <View style={{ height: H, flexDirection: 'row', alignItems: 'flex-end', gap: 1 }}>
        {curve.map((v, i) => {
          const h = Math.max(2, (Math.abs(v) / range) * H * 0.9);
          return (
            <View
              key={i}
              style={{
                width: barW,
                height: h,
                backgroundColor: v >= 0 ? '#00C896' : '#FF4D6D',
                borderRadius: 1,
                alignSelf: v >= 0 ? 'flex-end' : 'flex-start',
              }}
            />
          );
        })}
      </View>
      <View style={styles.curveBaseline} />
    </View>
  );
}

interface Props {
  onBack: () => void;
}

export function BacktestScreen({ onBack }: Props) {
  const [pair, setPair] = useState('EUR_USD');
  const [fromDate, setFromDate] = useState('2025-10-01');
  const [toDate, setToDate] = useState('2026-01-01');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const { run_id } = await triggerBacktest(pair, fromDate, toDate);
      // Poll for results
      let attempts = 0;
      const poll = async (): Promise<void> => {
        attempts++;
        const res = await fetchBacktestResults(run_id) as BacktestResult;
        if (res.status === 'complete' || res.status === 'failed') {
          setResult(res);
          setLoading(false);
        } else if (attempts < 60) {
          setTimeout(poll, 2000);
        } else {
          setError('Backtest timed out. Try a shorter date range.');
          setLoading(false);
        }
      };
      setTimeout(poll, 2000);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to start backtest');
      setLoading(false);
    }
  };

  const stats = result?.stats;
  const trades = result?.trades ?? [];
  const closed = trades.filter((t) => t.result !== 'open');

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backBtn}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>BACKTEST</Text>
        <View style={{ width: 60 }} />
      </View>

      <ScrollView style={styles.scroll} showsVerticalScrollIndicator={false}>
        {/* Controls */}
        <View style={styles.controls}>
          <View style={styles.inputRow}>
            <Text style={styles.inputLabel}>PAIR</Text>
            <TextInput
              style={styles.input}
              value={pair}
              onChangeText={setPair}
              autoCapitalize="characters"
              placeholderTextColor="#444"
            />
          </View>
          <View style={styles.inputRow}>
            <Text style={styles.inputLabel}>FROM</Text>
            <TextInput
              style={styles.input}
              value={fromDate}
              onChangeText={setFromDate}
              placeholder="YYYY-MM-DD"
              placeholderTextColor="#444"
            />
          </View>
          <View style={styles.inputRow}>
            <Text style={styles.inputLabel}>TO</Text>
            <TextInput
              style={styles.input}
              value={toDate}
              onChangeText={setToDate}
              placeholder="YYYY-MM-DD"
              placeholderTextColor="#444"
            />
          </View>
          <TouchableOpacity
            style={[styles.runBtn, loading && styles.runBtnDisabled]}
            onPress={run}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#000" size="small" />
            ) : (
              <Text style={styles.runBtnText}>RUN BACKTEST</Text>
            )}
          </TouchableOpacity>
        </View>

        {error && (
          <View style={styles.errorBox}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        {loading && (
          <View style={styles.loadingBox}>
            <ActivityIndicator color="#555" />
            <Text style={styles.loadingText}>Running analysis across all bars...</Text>
          </View>
        )}

        {stats && (
          <>
            {/* Stats grid */}
            <View style={styles.statsGrid}>
              <StatBox label="TRADES" value={String(stats.total_trades)} />
              <StatBox
                label="WIN RATE"
                value={`${stats.win_rate_pct}%`}
                color={stats.win_rate_pct >= 50 ? '#00C896' : '#FF4D6D'}
              />
              <StatBox label="AVG R" value={String(stats.avg_r_multiple)} color={stats.avg_r_multiple >= 0 ? '#00C896' : '#FF4D6D'} />
              <StatBox label="TOTAL R" value={`${stats.total_r}R`} color={stats.total_r >= 0 ? '#00C896' : '#FF4D6D'} />
              <StatBox label="MAX DD" value={`${stats.max_drawdown_r}R`} color="#FF4D6D" />
              <StatBox label="PROF. FACTOR" value={stats.profit_factor === Infinity ? '∞' : String(stats.profit_factor)} color="#FFD700" />
              <StatBox label="BEST" value={`+${stats.best_trade_r}R`} color="#00C896" />
              <StatBox label="WORST" value={`${stats.worst_trade_r}R`} color="#FF4D6D" />
            </View>

            <View style={styles.openNote}>
              <Text style={styles.openNoteText}>
                {stats.wins}W / {stats.losses}L / {stats.open} open (excluded from stats)
              </Text>
            </View>

            {/* Equity curve */}
            {stats.equity_curve.length > 0 && (
              <View style={styles.card}>
                <EquityCurve curve={stats.equity_curve} />
              </View>
            )}

            {/* Trade log */}
            <View style={styles.card}>
              <Text style={styles.sectionTitle}>TRADE LOG ({closed.length} closed)</Text>
              {closed.map((t, i) => (
                <View key={i} style={styles.tradeRow}>
                  <Text style={styles.tradeTime}>{t.signal_time.slice(0, 10)}</Text>
                  <Text style={[styles.tradeDir, { color: t.direction === 'bullish' ? '#00C896' : '#FF4D6D' }]}>
                    {t.direction.slice(0, 4).toUpperCase()}
                  </Text>
                  <Text style={styles.tradeEntry}>{t.entry_price.toFixed(4)}</Text>
                  <Text style={[styles.tradeResult, { color: t.result === 'win' ? '#00C896' : '#FF4D6D' }]}>
                    {t.result.toUpperCase()}
                  </Text>
                  <Text style={[styles.tradeR, { color: t.r_multiple >= 0 ? '#00C896' : '#FF4D6D' }]}>
                    {t.r_multiple >= 0 ? '+' : ''}{t.r_multiple}R
                  </Text>
                </View>
              ))}
            </View>
          </>
        )}

        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0D0D1A' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  backBtn: { paddingRight: 16 },
  backText: { color: '#888', fontSize: 14 },
  title: { color: '#FFF', fontSize: 20, fontWeight: '800', flex: 1, textAlign: 'center' },
  scroll: { flex: 1, paddingHorizontal: 16 },
  controls: {
    backgroundColor: '#1A1A2E',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    gap: 12,
  },
  inputRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  inputLabel: { color: '#555', fontSize: 11, fontWeight: '700', width: 44, letterSpacing: 1 },
  input: {
    flex: 1,
    backgroundColor: '#0D0D1A',
    color: '#FFF',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 14,
    fontWeight: '600',
  },
  runBtn: {
    backgroundColor: '#00C896',
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 4,
  },
  runBtnDisabled: { backgroundColor: '#1A3D32' },
  runBtnText: { color: '#000', fontSize: 14, fontWeight: '800', letterSpacing: 1 },
  errorBox: {
    backgroundColor: '#2A1A1E',
    borderRadius: 10,
    padding: 14,
    marginBottom: 12,
    borderLeftWidth: 3,
    borderLeftColor: '#FF4D6D',
  },
  errorText: { color: '#FF4D6D', fontSize: 13 },
  loadingBox: { alignItems: 'center', paddingVertical: 30, gap: 12 },
  loadingText: { color: '#555', fontSize: 13 },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 8,
  },
  statBox: {
    backgroundColor: '#1A1A2E',
    borderRadius: 10,
    padding: 14,
    alignItems: 'center',
    width: '22%',
    flexGrow: 1,
  },
  statValue: { color: '#FFF', fontSize: 18, fontWeight: '800', marginBottom: 4 },
  statLabel: { color: '#555', fontSize: 9, fontWeight: '700', letterSpacing: 0.5, textAlign: 'center' },
  openNote: { alignItems: 'center', marginBottom: 12 },
  openNoteText: { color: '#444', fontSize: 11 },
  card: {
    backgroundColor: '#1A1A2E',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
  },
  sectionTitle: { color: '#555', fontSize: 11, fontWeight: '700', letterSpacing: 1, marginBottom: 12 },
  curveContainer: { gap: 6 },
  curveLabel: { color: '#555', fontSize: 10, fontWeight: '700', letterSpacing: 1 },
  curveBaseline: { height: 1, backgroundColor: '#2A2A3E' },
  tradeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 7,
    borderBottomWidth: 1,
    borderBottomColor: '#2A2A3E',
    gap: 8,
  },
  tradeTime: { color: '#666', fontSize: 11, flex: 1.5 },
  tradeDir: { fontSize: 11, fontWeight: '700', width: 36 },
  tradeEntry: { color: '#AAA', fontSize: 11, flex: 1 },
  tradeResult: { fontSize: 11, fontWeight: '700', width: 40 },
  tradeR: { fontSize: 12, fontWeight: '800', width: 36, textAlign: 'right' },
});
