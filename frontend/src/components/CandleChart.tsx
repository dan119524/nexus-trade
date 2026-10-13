import React, { useMemo } from 'react';
import { View, Text, StyleSheet, ScrollView, Dimensions } from 'react-native';
import type { Candle, StructureEvent, SwingPoint } from '../types';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const BAR_WIDTH = 6;
const BAR_GAP = 2;
const CHART_HEIGHT = 200;
const VISIBLE_BARS = Math.floor(SCREEN_WIDTH / (BAR_WIDTH + BAR_GAP));

interface Props {
  candles: Candle[];
  swingHighs?: SwingPoint[];
  swingLows?: SwingPoint[];
  bosEvents?: StructureEvent[];
  chochEvents?: StructureEvent[];
  timeframe: string;
}

export function CandleChart({
  candles,
  swingHighs = [],
  swingLows = [],
  bosEvents = [],
  chochEvents = [],
  timeframe,
}: Props) {
  const visible = candles.slice(-VISIBLE_BARS);

  const { minPrice, maxPrice, priceRange } = useMemo(() => {
    if (!visible.length) return { minPrice: 0, maxPrice: 1, priceRange: 1 };
    const min = Math.min(...visible.map((c) => c.low));
    const max = Math.max(...visible.map((c) => c.high));
    const padding = (max - min) * 0.1;
    return { minPrice: min - padding, maxPrice: max + padding, priceRange: max - min + 2 * padding };
  }, [visible]);

  const toY = (price: number) =>
    CHART_HEIGHT - ((price - minPrice) / priceRange) * CHART_HEIGHT;

  // Mark which bars have BOS/CHoCH overlays
  const startBar = candles.length - VISIBLE_BARS;
  const eventBars = new Map<number, { type: string; color: string }>();
  [...bosEvents, ...chochEvents].forEach((e) => {
    const relIdx = e.broken_at_bar - startBar;
    if (relIdx >= 0 && relIdx < VISIBLE_BARS) {
      eventBars.set(relIdx, {
        type: e.event_type,
        color: e.event_type === 'BOS'
          ? (e.direction === 'bullish' ? '#00C896' : '#FF4D6D')
          : '#FFD700',
      });
    }
  });

  return (
    <View style={styles.container}>
      <Text style={styles.tfLabel}>{timeframe}</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View style={[styles.chart, { width: visible.length * (BAR_WIDTH + BAR_GAP) }]}>
          {/* BOS/CHoCH horizontal lines */}
          {[...bosEvents, ...chochEvents]
            .filter((e) => {
              const relIdx = e.broken_at_bar - startBar;
              return relIdx >= 0 && relIdx < VISIBLE_BARS;
            })
            .map((e, i) => {
              const y = toY(e.level);
              const color = e.event_type === 'BOS'
                ? (e.direction === 'bullish' ? '#00C896' : '#FF4D6D')
                : '#FFD700';
              return (
                <View
                  key={i}
                  style={[styles.levelLine, { top: y, borderColor: color }]}
                >
                  <View style={[styles.levelLabel, { backgroundColor: color }]}>
                    <Text style={styles.levelLabelText}>{e.event_type}</Text>
                  </View>
                </View>
              );
            })}

          {/* Candle bars */}
          {visible.map((c, i) => {
            const isBull = c.close >= c.open;
            const bodyTop = toY(Math.max(c.open, c.close));
            const bodyBot = toY(Math.min(c.open, c.close));
            const bodyH = Math.max(1, bodyBot - bodyTop);
            const wickTop = toY(c.high);
            const wickBot = toY(c.low);
            const color = isBull ? '#00C896' : '#FF4D6D';
            const x = i * (BAR_WIDTH + BAR_GAP);

            const event = eventBars.get(i);

            return (
              <View key={i} style={[styles.barWrapper, { left: x }]}>
                {/* Wick */}
                <View style={[styles.wick, {
                  top: wickTop,
                  height: wickBot - wickTop,
                  left: BAR_WIDTH / 2,
                  backgroundColor: color,
                }]} />
                {/* Body */}
                <View style={[styles.body, {
                  top: bodyTop,
                  height: bodyH,
                  backgroundColor: color,
                }]} />
                {/* Event marker dot */}
                {event && (
                  <View style={[styles.eventDot, {
                    top: bodyTop - 8,
                    backgroundColor: event.color,
                  }]} />
                )}
              </View>
            );
          })}

          {/* Swing high/low markers */}
          {swingHighs.filter((s) => s.bar_index >= startBar).map((s, i) => (
            <View key={`sh${i}`} style={[styles.swingMarker, {
              left: (s.bar_index - startBar) * (BAR_WIDTH + BAR_GAP),
              top: toY(s.price) - 14,
            }]}>
              <Text style={styles.swingHighLabel}>{s.label?.replace('first_high', '').slice(0, 2)}</Text>
            </View>
          ))}
          {swingLows.filter((s) => s.bar_index >= startBar).map((s, i) => (
            <View key={`sl${i}`} style={[styles.swingMarker, {
              left: (s.bar_index - startBar) * (BAR_WIDTH + BAR_GAP),
              top: toY(s.price) + 2,
            }]}>
              <Text style={styles.swingLowLabel}>{s.label?.replace('first_low', '').slice(0, 2)}</Text>
            </View>
          ))}
        </View>
      </ScrollView>

      {/* Price axis labels */}
      <View style={styles.priceAxis}>
        <Text style={styles.priceLabel}>{maxPrice.toFixed(4)}</Text>
        <Text style={styles.priceLabel}>{((maxPrice + minPrice) / 2).toFixed(4)}</Text>
        <Text style={styles.priceLabel}>{minPrice.toFixed(4)}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#0D0D1A',
    borderRadius: 12,
    padding: 10,
    marginBottom: 12,
    overflow: 'hidden',
  },
  tfLabel: {
    color: '#555',
    fontSize: 10,
    fontWeight: '700',
    marginBottom: 6,
    letterSpacing: 1,
  },
  chart: {
    height: CHART_HEIGHT,
    position: 'relative',
  },
  barWrapper: {
    position: 'absolute',
    width: BAR_WIDTH,
    height: CHART_HEIGHT,
  },
  wick: {
    position: 'absolute',
    width: 1,
  },
  body: {
    position: 'absolute',
    width: BAR_WIDTH,
    borderRadius: 1,
  },
  eventDot: {
    position: 'absolute',
    width: 5,
    height: 5,
    borderRadius: 3,
    left: 0,
  },
  levelLine: {
    position: 'absolute',
    left: 0,
    right: 0,
    borderTopWidth: 1,
    borderStyle: 'dashed',
    flexDirection: 'row',
    alignItems: 'center',
  },
  levelLabel: {
    paddingHorizontal: 3,
    paddingVertical: 1,
    borderRadius: 3,
  },
  levelLabelText: {
    color: '#000',
    fontSize: 8,
    fontWeight: '800',
  },
  swingMarker: {
    position: 'absolute',
    alignItems: 'center',
  },
  swingHighLabel: { color: '#00C896', fontSize: 7, fontWeight: '700' },
  swingLowLabel: { color: '#FF4D6D', fontSize: 7, fontWeight: '700' },
  priceAxis: {
    position: 'absolute',
    right: 4,
    top: 28,
    bottom: 4,
    justifyContent: 'space-between',
  },
  priceLabel: { color: '#444', fontSize: 8 },
});
