import { StatusBar } from 'expo-status-bar';
import React, { useState, useEffect } from 'react';
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { HomeScreen } from './src/screens/HomeScreen';
import { SignalDetailScreen } from './src/screens/SignalDetailScreen';
import { BacktestScreen } from './src/screens/BacktestScreen';
import { WatchlistScreen, STORAGE_KEY } from './src/screens/WatchlistScreen';
import { usePushNotifications } from './src/hooks/usePushNotifications';
import type { Signal } from './src/types';

type Screen = 'home' | 'signal' | 'backtest' | 'watchlist';

const DEFAULT_WATCHLIST = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD', 'USD_CAD'];

export default function App() {
  usePushNotifications();
  const [screen, setScreen] = useState<Screen>('home');
  const [selectedSignal, setSelectedSignal] = useState<Signal | null>(null);
  const [watchlist, setWatchlist] = useState<string[]>(DEFAULT_WATCHLIST);

  // Load persisted watchlist on startup
  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY).then((stored) => {
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          if (Array.isArray(parsed) && parsed.length > 0) {
            setWatchlist(parsed);
          }
        } catch { /* use default */ }
      }
    });
  }, []);

  return (
    <View style={styles.root}>
      <StatusBar style="light" />

      {screen === 'home' && (
        <HomeScreen
          onSelectSignal={(signal) => {
            setSelectedSignal(signal);
            setScreen('signal');
          }}
        />
      )}
      {screen === 'signal' && selectedSignal && (
        <SignalDetailScreen
          signal={selectedSignal}
          onBack={() => setScreen('home')}
        />
      )}
      {screen === 'backtest' && (
        <BacktestScreen onBack={() => setScreen('home')} />
      )}
      {screen === 'watchlist' && (
        <WatchlistScreen
          watchlist={watchlist}
          onWatchlistChange={setWatchlist}
        />
      )}

      {/* Tab bar — hidden on signal detail */}
      {screen !== 'signal' && (
        <View style={styles.tabBar}>
          <Tab icon="◉" label="Signals"   active={screen === 'home'}      onPress={() => setScreen('home')} />
          <Tab icon="⟳" label="Backtest"  active={screen === 'backtest'}  onPress={() => setScreen('backtest')} />
          <Tab icon="☰" label="Watchlist" active={screen === 'watchlist'} onPress={() => setScreen('watchlist')} />
        </View>
      )}
    </View>
  );
}

function Tab({ icon, label, active, onPress }: {
  icon: string; label: string; active: boolean; onPress: () => void;
}) {
  return (
    <TouchableOpacity style={styles.tab} onPress={onPress}>
      <Text style={[styles.tabIcon, active && styles.tabIconActive]}>{icon}</Text>
      <Text style={[styles.tabLabel, active && styles.tabLabelActive]}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#0D0D1A' },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#111122',
    borderTopWidth: 1,
    borderTopColor: '#1E1E30',
    paddingBottom: 24,
    paddingTop: 10,
  },
  tab: { flex: 1, alignItems: 'center', gap: 3 },
  tabIcon: { fontSize: 18, color: '#333' },
  tabIconActive: { color: '#00C896' },
  tabLabel: { color: '#444', fontSize: 11, fontWeight: '600' },
  tabLabelActive: { color: '#00C896' },
});
