import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import type { TradePlan } from '../types';

interface Props {
  plan: TradePlan;
}

function Row({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={[styles.rowValue, color ? { color } : undefined]}>{value}</Text>
    </View>
  );
}

export function TradePlanCard({ plan }: Props) {
  const [expanded, setExpanded] = useState(false);
  const isBullish = plan.direction === 'bullish';
  const dirColor = isBullish ? '#00C896' : '#FF4D6D';

  return (
    <View style={styles.container}>
      <TouchableOpacity onPress={() => setExpanded(!expanded)} activeOpacity={0.8}>
        <View style={styles.header}>
          <View style={[styles.dirBadge, { backgroundColor: dirColor + '22', borderColor: dirColor }]}>
            <Text style={[styles.dirText, { color: dirColor }]}>
              {plan.direction.toUpperCase()}
            </Text>
          </View>
          <Text style={styles.pair}>{plan.pair.replace('_', '/')}</Text>
          <Text style={styles.tf}>{plan.reference_timeframe}</Text>
          <Text style={styles.chevron}>{expanded ? '▲' : '▼'}</Text>
        </View>

        <View style={styles.keyRow}>
          <View style={styles.keyItem}>
            <Text style={styles.keyLabel}>ENTRY</Text>
            <Text style={styles.keyValue}>{plan.entry_price.toFixed(5)}</Text>
          </View>
          <View style={styles.keyItem}>
            <Text style={styles.keyLabel}>SL</Text>
            <Text style={[styles.keyValue, { color: '#FF4D6D' }]}>{plan.stop_loss.toFixed(5)}</Text>
          </View>
          <View style={styles.keyItem}>
            <Text style={styles.keyLabel}>TP1</Text>
            <Text style={[styles.keyValue, { color: '#00C896' }]}>{plan.take_profit_1.toFixed(5)}</Text>
          </View>
          <View style={styles.keyItem}>
            <Text style={styles.keyLabel}>R:R</Text>
            <Text style={[styles.keyValue, { color: '#FFD700' }]}>{plan.risk_reward}:1</Text>
          </View>
        </View>
      </TouchableOpacity>

      {expanded && (
        <View style={styles.details}>
          <View style={styles.divider} />
          <Row label="TP2" value={plan.take_profit_2.toFixed(5)} color="#00C896" />
          <Row label="SL Distance" value={`${plan.sl_pips} pips`} />
          <Row label="Lot Size" value={plan.lot_size.toString()} />
          <Row label="Risk Amount" value={`$${plan.risk_amount_usd}`} />
          <Row label="Risk %" value={`${plan.risk_percent}%`} />
          <Row label="Account" value={`$${plan.account_balance.toLocaleString()}`} />
          <View style={styles.invalidation}>
            <Text style={styles.invalidationLabel}>⚠ INVALIDATION</Text>
            <Text style={styles.invalidationText}>{plan.invalidation_note}</Text>
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#1A1A2E',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 8,
  },
  dirBadge: {
    borderWidth: 1,
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  dirText: { fontSize: 11, fontWeight: '800', letterSpacing: 1 },
  pair: { color: '#FFF', fontSize: 16, fontWeight: '700', flex: 1 },
  tf: { color: '#888', fontSize: 12 },
  chevron: { color: '#555', fontSize: 12 },
  keyRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  keyItem: { alignItems: 'center' },
  keyLabel: { color: '#555', fontSize: 10, fontWeight: '700', letterSpacing: 0.5 },
  keyValue: { color: '#FFF', fontSize: 13, fontWeight: '700', marginTop: 2 },
  details: { marginTop: 8 },
  divider: { height: 1, backgroundColor: '#2A2A3E', marginBottom: 10 },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 7,
  },
  rowLabel: { color: '#666', fontSize: 12 },
  rowValue: { color: '#CCC', fontSize: 12, fontWeight: '600' },
  invalidation: {
    backgroundColor: '#FF4D6D11',
    borderLeftWidth: 3,
    borderLeftColor: '#FF4D6D',
    borderRadius: 6,
    padding: 10,
    marginTop: 10,
  },
  invalidationLabel: { color: '#FF4D6D', fontSize: 10, fontWeight: '800', marginBottom: 4 },
  invalidationText: { color: '#AAA', fontSize: 12, lineHeight: 18 },
});
