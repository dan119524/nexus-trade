import React, { useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, SafeAreaView,
  ScrollView, TouchableOpacity, ActivityIndicator, Alert,
} from 'react-native';
import { CandleChart } from '../components/CandleChart';
import { ConfluenceBar } from '../components/ConfluenceBar';
import { TradePlanCard } from '../components/TradePlanCard';
import { fetchCandles, fetchTimeframeAnalysis, executeTradeConfirm } from '../api/nexusApi';
import type { Candle, Signal, TimeframeAnalysis } from '../types';

const TIMEFRAMES = ['M1', 'M5', 'H1', 'H4'] as const;

type ExecStatus = 'idle' | 'executing' | 'success' | 'error';

interface Props {
  signal: Signal;
  onBack: () => void;
}

export function SignalDetailScreen({ signal, onBack }: Props) {
  const [selectedTf, setSelectedTf] = useState<string>('H1');
  const [candles, setCandles] = useState<Candle[]>([]);
  const [tfAnalysis, setTfAnalysis] = useState<TimeframeAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [execStatus, setExecStatus] = useState<ExecStatus>('idle');
  const [execMessage, setExecMessage] = useState('');

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      try {
        const [c, a] = await Promise.all([
          fetchCandles(signal.pair, selectedTf, 100),
          fetchTimeframeAnalysis(signal.pair, selectedTf),
        ]);
        if (!cancelled) {
          setCandles(c);
          setTfAnalysis(a);
        }
      } catch {
        // handled silently — chart just shows empty
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, [signal.pair, selectedTf]);

  const plan = signal.trade_plan;

  const handleExecute = () => {
    if (!plan) return;
    Alert.alert(
      `Execute ${signal.pair.replace('_', '/')} ${plan.direction.toUpperCase()}?`,
      `Entry: ${plan.entry_price}\nSL: ${plan.stop_loss}\nTP: ${plan.take_profit_1}\nLot: ${plan.lot_size}\nRisk: $${plan.risk_amount_usd}\n\nThis will place a LIVE order on your PRACTICE account.`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Execute',
          style: 'destructive',
          onPress: async () => {
            setExecuting(true);
            setExecStatus('executing');
            setExecMessage('Submitting order to OANDA...');
            try {
              const res = await executeTradeConfirm(signal.pair) as any;
              const orderId = res?.orderFillTransaction?.id
                ?? res?.relatedTransactionIDs?.[0]
                ?? '—';
              setExecStatus('success');
              setExecMessage(
                `Order placed — ${signal.pair.replace('_', '/')} ${plan.direction.toUpperCase()} · ID: ${orderId}`
              );
            } catch (e: unknown) {
              setExecStatus('error');
              setExecMessage(e instanceof Error ? e.message : 'Order failed. Check server logs.');
            } finally {
              setExecuting(false);
            }
          },
        },
      ]
    );
  };

  const statusBannerColor =
    execStatus === 'executing' ? '#B8860B'
    : execStatus === 'success' ? '#00C896'
    : execStatus === 'error' ? '#FF4D6D'
    : 'transparent';

  const statusBannerBg =
    execStatus === 'executing' ? '#2A220A'
    : execStatus === 'success' ? '#0A2A1E'
    : execStatus === 'error' ? '#2A0A10'
    : 'transparent';

  const statusIcon =
    execStatus === 'executing' ? '⏳'
    : execStatus === 'success' ? '✓'
    : execStatus === 'error' ? '✗'
    : '';

  return (
    <SafeAreaView style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backBtn}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>{signal.pair.replace('_', '/')}</Text>
        <View style={styles.headerRight} />
      </View>

      <ScrollView style={styles.scroll} showsVerticalScrollIndicator={false}>
        {/* Confluence */}
        <ConfluenceBar confluence={signal.confluence} />

        {/* Timeframe selector */}
        <View style={styles.tfRow}>
          {TIMEFRAMES.map((tf) => {
            const vote = signal.confluence.votes[tf] ?? 'neutral';
            const dotColor =
              vote === 'bullish' ? '#00C896'
              : vote === 'bearish' ? '#FF4D6D'
              : '#444';
            return (
              <TouchableOpacity
                key={tf}
                style={[styles.tfBtn, selectedTf === tf && styles.tfBtnActive]}
                onPress={() => setSelectedTf(tf)}
              >
                <View style={[styles.tfDot, { backgroundColor: dotColor }]} />
                <Text style={[styles.tfText, selectedTf === tf && styles.tfTextActive]}>
                  {tf}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>

        {/* Chart */}
        {loading ? (
          <View style={styles.chartPlaceholder}>
            <ActivityIndicator color="#555" />
          </View>
        ) : (
          <CandleChart
            candles={candles}
            swingHighs={tfAnalysis?.swing_highs}
            swingLows={tfAnalysis?.swing_lows}
            bosEvents={tfAnalysis?.bos_events}
            chochEvents={tfAnalysis?.choch_events}
            timeframe={selectedTf}
          />
        )}

        {/* Trade Plan */}
        {plan && <TradePlanCard plan={plan} />}

        {/* Execute button */}
        {plan && (
          <TouchableOpacity
            style={[styles.executeBtn, executing && styles.executeBtnDisabled]}
            onPress={handleExecute}
            disabled={executing}
          >
            {executing ? (
              <ActivityIndicator color="#000" size="small" />
            ) : (
              <>
                <Text style={styles.executeBtnIcon}>⚡</Text>
                <Text style={styles.executeBtnText}>EXECUTE ON PRACTICE ACCOUNT</Text>
              </>
            )}
          </TouchableOpacity>
        )}

        {/* Execution status banner */}
        {execStatus !== 'idle' && (
          <View style={[styles.statusBanner, { backgroundColor: statusBannerBg, borderColor: statusBannerColor }]}>
            <Text style={[styles.statusIcon, { color: statusBannerColor }]}>{statusIcon}</Text>
            <Text style={[styles.statusText, { color: statusBannerColor }]}>{execMessage}</Text>
          </View>
        )}

        {/* Summary */}
        {signal.summary && (
          <View style={styles.summaryCard}>
            <Text style={styles.summaryTitle}>ANALYSIS</Text>
            {signal.summary.split('\n\n').map((section, i) => (
              <Text key={i} style={styles.summaryText}>{section}</Text>
            ))}
          </View>
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
  headerRight: { width: 60 },
  scroll: { flex: 1, paddingHorizontal: 16 },
  tfRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 12,
  },
  tfBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 5,
    backgroundColor: '#1A1A2E',
    borderRadius: 8,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  tfBtnActive: { borderColor: '#444' },
  tfDot: { width: 7, height: 7, borderRadius: 4 },
  tfText: { color: '#555', fontSize: 12, fontWeight: '700' },
  tfTextActive: { color: '#FFF' },
  chartPlaceholder: {
    height: 220,
    backgroundColor: '#1A1A2E',
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  summaryCard: {
    backgroundColor: '#1A1A2E',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  summaryTitle: {
    color: '#555',
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1,
    marginBottom: 12,
  },
  summaryText: {
    color: '#AAA',
    fontSize: 13,
    lineHeight: 20,
    marginBottom: 12,
  },
  executeBtn: {
    backgroundColor: '#00C896',
    borderRadius: 12,
    paddingVertical: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    marginBottom: 10,
  },
  executeBtnDisabled: { backgroundColor: '#1A3D32' },
  executeBtnIcon: { fontSize: 16 },
  executeBtnText: { color: '#000', fontSize: 13, fontWeight: '800', letterSpacing: 1 },
  statusBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    borderRadius: 10,
    borderWidth: 1,
    padding: 14,
    marginBottom: 12,
  },
  statusIcon: { fontSize: 16, fontWeight: '700' },
  statusText: { fontSize: 13, fontWeight: '600', flex: 1 },
});
