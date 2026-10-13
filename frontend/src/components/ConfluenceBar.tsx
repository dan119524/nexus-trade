import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import type { ConfluenceResult } from '../types';

interface Props {
  confluence: ConfluenceResult;
}

const TF_ORDER = ['M1', 'M5', 'H1', 'H4'];

export function ConfluenceBar({ confluence }: Props) {
  const { score, max_score, direction, votes } = confluence;
  const isBullish = direction === 'bullish';

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.label}>CONFLUENCE</Text>
        <Text style={[styles.score, isBullish ? styles.bullish : styles.bearish]}>
          {score}/{max_score}
        </Text>
        <Text style={[styles.direction, isBullish ? styles.bullish : styles.bearish]}>
          {direction.toUpperCase()}
        </Text>
      </View>

      <View style={styles.dots}>
        {TF_ORDER.map((tf) => {
          const vote = votes[tf] ?? 'neutral';
          const dotStyle =
            vote === 'bullish' ? styles.dotBullish
            : vote === 'bearish' ? styles.dotBearish
            : styles.dotNeutral;
          return (
            <View key={tf} style={styles.dotWrapper}>
              <View style={[styles.dot, dotStyle]} />
              <Text style={styles.tfLabel}>{tf}</Text>
            </View>
          );
        })}
      </View>
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
  label: {
    color: '#666',
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1,
    flex: 1,
  },
  score: {
    fontSize: 22,
    fontWeight: '800',
  },
  direction: {
    fontSize: 14,
    fontWeight: '700',
    letterSpacing: 1,
  },
  bullish: { color: '#00C896' },
  bearish: { color: '#FF4D6D' },
  dots: {
    flexDirection: 'row',
    gap: 12,
  },
  dotWrapper: {
    alignItems: 'center',
    gap: 4,
  },
  dot: {
    width: 16,
    height: 16,
    borderRadius: 8,
  },
  dotBullish: { backgroundColor: '#00C896' },
  dotBearish: { backgroundColor: '#FF4D6D' },
  dotNeutral: { backgroundColor: '#444' },
  tfLabel: {
    color: '#888',
    fontSize: 10,
    fontWeight: '600',
  },
});
