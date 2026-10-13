import React, { useCallback, useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, SafeAreaView,
  TouchableOpacity, RefreshControl, ScrollView,
} from 'react-native';
import { SignalList } from '../components/SignalList';
import { fetchAllSignals } from '../api/nexusApi';
import type { Signal } from '../types';

interface Props {
  onSelectSignal: (signal: Signal) => void;
}

export function HomeScreen({ onSelectSignal }: Props) {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  const load = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);
    setError(null);
    try {
      const data = await fetchAllSignals();
      setSignals(data);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Could not connect to NEXUS server');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>NEXUS</Text>
          <Text style={styles.subtitle}>TRADE SIGNALS</Text>
        </View>
        <TouchableOpacity style={styles.refreshBtn} onPress={() => load(true)}>
          <Text style={styles.refreshText}>↻</Text>
        </TouchableOpacity>
      </View>

      {lastUpdated ? (
        <Text style={styles.updated}>Updated {lastUpdated}</Text>
      ) : null}

      {error ? (
        <View style={styles.errorBox}>
          <Text style={styles.errorTitle}>Cannot reach server</Text>
          <Text style={styles.errorText}>{error}</Text>
          <Text style={styles.errorHint}>Start: uvicorn tools.api.server:app --port 8000</Text>
        </View>
      ) : (
        <ScrollView
          style={styles.scroll}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={() => load(true)} tintColor="#555" />
          }
        >
          <SignalList signals={signals} onPress={onSelectSignal} loading={loading} />
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0D0D1A' },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 8,
  },
  title: { color: '#FFF', fontSize: 28, fontWeight: '900', letterSpacing: 2 },
  subtitle: { color: '#555', fontSize: 10, fontWeight: '700', letterSpacing: 3 },
  updated: { color: '#333', fontSize: 11, paddingHorizontal: 20, marginBottom: 8 },
  refreshBtn: {
    width: 40, height: 40,
    borderRadius: 20,
    backgroundColor: '#1A1A2E',
    alignItems: 'center',
    justifyContent: 'center',
  },
  refreshText: { color: '#555', fontSize: 20 },
  scroll: { flex: 1, paddingHorizontal: 16 },
  errorBox: {
    margin: 20,
    backgroundColor: '#1A1A2E',
    borderRadius: 12,
    padding: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#FF4D6D',
  },
  errorTitle: { color: '#FF4D6D', fontWeight: '700', marginBottom: 6 },
  errorText: { color: '#888', fontSize: 12, marginBottom: 8 },
  errorHint: { color: '#555', fontSize: 11, fontFamily: 'monospace' },
});
