import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, FlatList } from 'react-native';
import type { Signal } from '../types';

interface Props {
  signals: Signal[];
  onPress: (signal: Signal) => void;
  loading?: boolean;
}

function SignalRow({ signal, onPress }: { signal: Signal; onPress: () => void }) {
  const conf = signal.confluence;
  const plan = signal.trade_plan;
  const isBullish = conf.direction === 'bullish';
  const dirColor = isBullish ? '#00C896' : '#FF4D6D';

  return (
    <TouchableOpacity style={styles.row} onPress={onPress} activeOpacity={0.75}>
      <View style={[styles.dirStripe, { backgroundColor: dirColor }]} />
      <View style={styles.content}>
        <View style={styles.top}>
          <Text style={styles.pair}>{signal.pair.replace('_', '/')}</Text>
          <Text style={[styles.dir, { color: dirColor }]}>{conf.direction.toUpperCase()}</Text>
          <View style={styles.scoreBadge}>
            <Text style={styles.scoreText}>{conf.score}/{conf.max_score}</Text>
          </View>
        </View>
        {plan && (
          <View style={styles.bottom}>
            <Text style={styles.meta}>Entry {plan.entry_price.toFixed(5)}</Text>
            <Text style={styles.meta}>SL {plan.stop_loss.toFixed(5)}</Text>
            <Text style={[styles.rr, { color: '#FFD700' }]}>{plan.risk_reward}:1</Text>
          </View>
        )}
        <View style={styles.votes}>
          {Object.entries(conf.votes).map(([tf, vote]) => (
            <View
              key={tf}
              style={[
                styles.voteDot,
                {
                  backgroundColor:
                    vote === 'bullish' ? '#00C896'
                    : vote === 'bearish' ? '#FF4D6D'
                    : '#333',
                },
              ]}
            >
              <Text style={styles.voteTf}>{tf}</Text>
            </View>
          ))}
        </View>
      </View>
    </TouchableOpacity>
  );
}

export function SignalList({ signals, onPress, loading }: Props) {
  if (loading) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>Loading signals...</Text>
      </View>
    );
  }

  if (!signals.length) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>No active signals</Text>
        <Text style={styles.emptyHint}>Confluence score must be ≥ 3/4 to appear here</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={signals}
      keyExtractor={(s) => s.id}
      renderItem={({ item }) => (
        <SignalRow signal={item} onPress={() => onPress(item)} />
      )}
      contentContainerStyle={styles.list}
    />
  );
}

const styles = StyleSheet.create({
  list: { paddingBottom: 20 },
  row: {
    flexDirection: 'row',
    backgroundColor: '#1A1A2E',
    borderRadius: 12,
    marginBottom: 10,
    overflow: 'hidden',
  },
  dirStripe: { width: 4 },
  content: { flex: 1, padding: 14 },
  top: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  pair: { color: '#FFF', fontSize: 18, fontWeight: '800', flex: 1 },
  dir: { fontSize: 12, fontWeight: '700', letterSpacing: 1, marginRight: 8 },
  scoreBadge: {
    backgroundColor: '#2A2A3E',
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  scoreText: { color: '#FFF', fontSize: 12, fontWeight: '700' },
  bottom: { flexDirection: 'row', gap: 12, marginBottom: 10 },
  meta: { color: '#888', fontSize: 11 },
  rr: { fontSize: 11, fontWeight: '700' },
  votes: { flexDirection: 'row', gap: 6 },
  voteDot: {
    borderRadius: 5,
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  voteTf: { color: '#FFF', fontSize: 9, fontWeight: '700' },
  empty: { alignItems: 'center', paddingTop: 60 },
  emptyText: { color: '#555', fontSize: 16, fontWeight: '600', marginBottom: 8 },
  emptyHint: { color: '#333', fontSize: 12 },
});
