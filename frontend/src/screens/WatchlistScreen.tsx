import React, { useCallback, useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, SafeAreaView, FlatList,
  TouchableOpacity, TextInput, RefreshControl, Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { fetchInstruments, BASE_URL } from '../api/nexusApi';

const STORAGE_KEY = '@nexus_watchlist';

interface Props {
  watchlist: string[];
  onWatchlistChange: (pairs: string[]) => void;
}

export function WatchlistScreen({ watchlist, onWatchlistChange }: Props) {
  const [availablePairs, setAvailablePairs] = useState<string[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [search, setSearch] = useState('');
  const [deviceCount, setDeviceCount] = useState<number | null>(null);

  const load = useCallback(async () => {
    setRefreshing(true);
    try {
      const instruments = await fetchInstruments();
      if (instruments.length > 0) setAvailablePairs(instruments);
      const r = await fetch(`${BASE_URL}/push/devices`);
      const d = await r.json();
      setDeviceCount(d.count);
    } catch { /* silent */ }
    setRefreshing(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const toggle = async (pair: string) => {
    const updated = watchlist.includes(pair)
      ? watchlist.filter((p) => p !== pair)
      : [...watchlist, pair];
    onWatchlistChange(updated);
    try {
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    } catch { /* silent */ }
  };

  const sendTestPush = async () => {
    try {
      const r = await fetch(`${BASE_URL}/push/test`, { method: 'POST' });
      if (r.ok) {
        Alert.alert('✓ Test sent', 'Check your device for the notification.');
      } else {
        const e = await r.json();
        Alert.alert('Failed', e.detail ?? 'No devices registered.');
      }
    } catch {
      Alert.alert('Error', 'Could not reach server.');
    }
  };

  const filtered = availablePairs.filter((p) =>
    p.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.header}>
        <Text style={styles.title}>WATCHLIST</Text>
        <Text style={styles.subtitle}>{watchlist.length} pairs active</Text>
      </View>

      <View style={styles.searchRow}>
        <TextInput
          style={styles.search}
          placeholder="Search any pair — EUR_USD, XAU_USD, BCO_USD..."
          placeholderTextColor="#444"
          value={search}
          onChangeText={setSearch}
          autoCapitalize="characters"
        />
      </View>

      <FlatList
        data={filtered}
        keyExtractor={(p) => p}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={load} tintColor="#555" />}
        renderItem={({ item: pair }) => {
          const active = watchlist.includes(pair);
          return (
            <TouchableOpacity
              style={[styles.row, active && styles.rowActive]}
              onPress={() => toggle(pair)}
            >
              <View style={[styles.dot, active ? styles.dotActive : styles.dotInactive]} />
              <Text style={[styles.pairText, active && styles.pairTextActive]}>
                {pair.replace('_', '/')}
              </Text>
              <Text style={styles.action}>{active ? '✓ Watching' : '+ Add'}</Text>
            </TouchableOpacity>
          );
        }}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          availablePairs.length === 0 ? (
            <View style={styles.empty}>
              <Text style={styles.emptyText}>Loading instruments...</Text>
            </View>
          ) : (
            <View style={styles.empty}>
              <Text style={styles.emptyText}>No pairs match "{search}"</Text>
            </View>
          )
        }
        ListFooterComponent={
          <View style={styles.footer}>
            <View style={styles.pushStatus}>
              <Text style={styles.pushLabel}>PUSH NOTIFICATIONS</Text>
              <Text style={styles.pushValue}>
                {deviceCount === null ? '...' : `${deviceCount} device${deviceCount !== 1 ? 's' : ''} registered`}
              </Text>
            </View>
            <TouchableOpacity style={styles.testBtn} onPress={sendTestPush}>
              <Text style={styles.testBtnText}>Send Test Push</Text>
            </TouchableOpacity>
          </View>
        }
      />
    </SafeAreaView>
  );
}

export { STORAGE_KEY };

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0D0D1A' },
  header: {
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 4,
  },
  title: { color: '#FFF', fontSize: 28, fontWeight: '900', letterSpacing: 2 },
  subtitle: { color: '#555', fontSize: 11, fontWeight: '700', letterSpacing: 2, marginTop: 2 },
  searchRow: { paddingHorizontal: 16, paddingVertical: 10 },
  search: {
    backgroundColor: '#1A1A2E',
    color: '#FFF',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 14,
  },
  list: { paddingHorizontal: 16, paddingBottom: 20 },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1A1A2E',
    borderRadius: 10,
    padding: 14,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: 'transparent',
    gap: 12,
  },
  rowActive: { borderColor: '#00C89633' },
  dot: { width: 10, height: 10, borderRadius: 5 },
  dotActive: { backgroundColor: '#00C896' },
  dotInactive: { backgroundColor: '#333' },
  pairText: { color: '#666', fontSize: 16, fontWeight: '700', flex: 1 },
  pairTextActive: { color: '#FFF' },
  action: { color: '#444', fontSize: 12 },
  empty: { alignItems: 'center', paddingTop: 40 },
  emptyText: { color: '#555', fontSize: 14 },
  footer: { marginTop: 20, gap: 12 },
  pushStatus: {
    backgroundColor: '#1A1A2E',
    borderRadius: 10,
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  pushLabel: { color: '#555', fontSize: 11, fontWeight: '700', letterSpacing: 1 },
  pushValue: { color: '#FFF', fontSize: 13, fontWeight: '600' },
  testBtn: {
    backgroundColor: '#1A1A2E',
    borderRadius: 10,
    padding: 14,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#2A2A3E',
  },
  testBtnText: { color: '#888', fontSize: 13, fontWeight: '600' },
});
