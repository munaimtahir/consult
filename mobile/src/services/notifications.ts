/**
 * Firebase Cloud Messaging (FCM) service for push notifications.
 * 
 * IMPORTANT: This is a MOCK implementation for development.
 * For production, install @react-native-firebase/messaging and replace the mock functions.
 * 
 * TODO: To enable real push notifications:
 * 1. Install Firebase: npm install @react-native-firebase/app @react-native-firebase/messaging
 * 2. Configure Firebase in android/app/google-services.json
 * 3. Replace mock functions with actual Firebase calls (see TODOs in each function)
 */

import { Platform } from 'react-native';
import { storage } from './storage';
import { logger } from './logger';
import { registerDevice } from '../api/devices';
import { generateDeviceId } from '../utils/helpers';

/**
 * Notification payload structure from FCM.
 */
export interface NotificationPayload {
  title?: string;
  body?: string;
  data?: {
    type?: string;
    consult_id?: string;
    [key: string]: string | undefined;
  };
}

/**
 * Notification handler callback type.
 */
export type NotificationHandler = (payload: NotificationPayload) => void;

/**
 * Notification service state.
 */
let isInitialized = false;
let notificationHandlers: NotificationHandler[] = [];

/**
 * Initialize the notification service.
 * Requests permissions and sets up listeners.
 */
export async function initializeNotifications(): Promise<boolean> {
  if (isInitialized) {
    return true;
  }

  try {
    // TODO: Replace with actual Firebase implementation
    // import messaging from '@react-native-firebase/messaging';
    
    // Request permissions (iOS mainly, Android grants automatically)
    const hasPermission = await requestNotificationPermission();
    
    if (!hasPermission) {
      logger.warn('Notification permission denied');
      return false;
    }
    
    // Get and store the FCM token
    const fcmToken = await getFcmToken();
    
    if (fcmToken) {
      await registerDeviceForNotifications(fcmToken);
    }
    
    // Set up foreground message handler
    setupForegroundHandler();
    
    // Set up background message handler
    setupBackgroundHandler();
    
    // Set up notification opened handler
    setupNotificationOpenedHandler();
    
    isInitialized = true;
    logger.info('Notification service initialized');
    
    return true;
  } catch (error) {
    logger.error('Failed to initialize notifications', error);
    return false;
  }
}

/**
 * Request notification permissions.
 */
async function requestNotificationPermission(): Promise<boolean> {
  try {
    // TODO: Replace with actual Firebase implementation
    // const authStatus = await messaging().requestPermission();
    // return authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
    //        authStatus === messaging.AuthorizationStatus.PROVISIONAL;
    
    // Mock implementation - assume permission granted
    logger.debug('Requesting notification permission (mock)');
    return true;
  } catch (error) {
    logger.error('Failed to request notification permission', error);
    return false;
  }
}

/**
 * Get the FCM token.
 */
async function getFcmToken(): Promise<string | null> {
  try {
    // TODO: Replace with actual Firebase implementation
    // const token = await messaging().getToken();
    
    // Check if we have a stored token
    const storedToken = await storage.getFcmToken();
    if (storedToken) {
      return storedToken;
    }
    
    // Mock implementation - generate a fake token for development
    const mockToken = `mock-fcm-token-${Date.now()}`;
    await storage.setFcmToken(mockToken);
    
    logger.debug('Got FCM token (mock)', { token: mockToken.substring(0, 20) + '...' });
    
    return mockToken;
  } catch (error) {
    logger.error('Failed to get FCM token', error);
    return null;
  }
}

/**
 * Register the device with the backend for push notifications.
 */
async function registerDeviceForNotifications(fcmToken: string): Promise<void> {
  try {
    let deviceId = await storage.getDeviceId();
    
    if (!deviceId) {
      deviceId = generateDeviceId();
      await storage.setDeviceId(deviceId);
    }
    
    const platform = Platform.OS === 'ios' ? 'ios' : 'android';
    
    await registerDevice(deviceId, fcmToken, platform);
    
    logger.info('Device registered for notifications', { deviceId });
  } catch (error) {
    logger.error('Failed to register device for notifications', error);
  }
}

/**
 * Set up the foreground message handler.
 */
function setupForegroundHandler(): void {
  // TODO: Replace with actual Firebase implementation
  // messaging().onMessage(async (remoteMessage) => {
  //   handleNotification(remoteMessage);
  // });
  
  logger.debug('Foreground notification handler set up (mock)');
}

/**
 * Set up the background message handler.
 */
function setupBackgroundHandler(): void {
  // TODO: Replace with actual Firebase implementation
  // messaging().setBackgroundMessageHandler(async (remoteMessage) => {
  //   handleNotification(remoteMessage);
  // });
  
  logger.debug('Background notification handler set up (mock)');
}

/**
 * Set up the notification opened handler.
 */
function setupNotificationOpenedHandler(): void {
  // TODO: Replace with actual Firebase implementation
  // messaging().onNotificationOpenedApp((remoteMessage) => {
  //   handleNotificationOpened(remoteMessage);
  // });
  
  // Check if app was opened from a notification
  // messaging()
  //   .getInitialNotification()
  //   .then((remoteMessage) => {
  //     if (remoteMessage) {
  //       handleNotificationOpened(remoteMessage);
  //     }
  //   });
  
  logger.debug('Notification opened handler set up (mock)');
}

/**
 * Handle an incoming notification.
 * NOTE: This function will be used when FCM is fully integrated.
 * @internal
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function _handleNotification(payload: NotificationPayload): void {
  logger.info('Notification received', payload);
  
  // Notify all registered handlers
  notificationHandlers.forEach(handler => {
    try {
      handler(payload);
    } catch (error) {
      logger.error('Error in notification handler', error);
    }
  });
}

/**
 * Handle a notification that was opened/tapped.
 * NOTE: This function will be used when FCM is fully integrated.
 * @internal
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function _handleNotificationOpened(payload: NotificationPayload): void {
  logger.info('Notification opened', payload);
  
  // Extract consult ID if present
  const consultId = payload.data?.consult_id;
  
  if (consultId) {
    // Navigate to consult detail
    // This should be handled by the navigation service or a global event
    logger.info('Should navigate to consult', { consultId });
  }
  
  // Notify all registered handlers
  notificationHandlers.forEach(handler => {
    try {
      handler(payload);
    } catch (error) {
      logger.error('Error in notification handler', error);
    }
  });
}

/**
 * Register a handler for incoming notifications.
 */
export function onNotification(handler: NotificationHandler): () => void {
  notificationHandlers.push(handler);
  
  // Return unsubscribe function
  return () => {
    notificationHandlers = notificationHandlers.filter(h => h !== handler);
  };
}

/**
 * Get the consult ID from a notification payload.
 */
export function getConsultIdFromNotification(payload: NotificationPayload): number | null {
  const consultIdStr = payload.data?.consult_id;
  
  if (consultIdStr) {
    const consultId = parseInt(consultIdStr, 10);
    if (!isNaN(consultId)) {
      return consultId;
    }
  }
  
  return null;
}
