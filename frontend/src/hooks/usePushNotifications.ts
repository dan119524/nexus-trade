/**
 * Register for Expo push notifications and post the token to the NEXUS server.
 * Call this once at app startup (from HomeScreen or App.tsx).
 */

import { useEffect } from 'react';
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';
import { BASE_URL } from '../api/nexusApi';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

export function usePushNotifications() {
  useEffect(() => {
    registerForPushNotifications();
  }, []);
}

async function registerForPushNotifications(): Promise<void> {
  // Notifications only work on physical devices via Expo Go / standalone builds
  if (Platform.OS === 'web') return;

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    console.warn('Push notification permission not granted');
    return;
  }

  try {
    const tokenData = await Notifications.getExpoPushTokenAsync();
    const token = tokenData.data;
    console.log('Expo push token:', token);

    // Register with the NEXUS server
    await fetch(`${BASE_URL}/push/register?token=${encodeURIComponent(token)}`, {
      method: 'POST',
    });
    console.log('Push token registered with NEXUS server');
  } catch (e) {
    console.warn('Could not register push token:', e);
  }
}
