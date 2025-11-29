/**
 * Storage service wrapper for AsyncStorage.
 * Provides typed methods for storing and retrieving app data.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { ENV } from '../config/env';
import { User } from '../api/types';
import { logger } from './logger';

/**
 * Storage keys enum for type safety.
 */
const KEYS = {
  TOKEN: ENV.TOKEN_STORAGE_KEY,
  USER: ENV.USER_STORAGE_KEY,
  DEVICE_ID: ENV.DEVICE_ID_STORAGE_KEY,
  FCM_TOKEN: ENV.FCM_TOKEN_STORAGE_KEY,
} as const;

/**
 * Storage service with typed methods.
 */
export const storage = {
  /**
   * Store the authentication token.
   */
  async setToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem(KEYS.TOKEN, token);
    } catch (error) {
      logger.error('Failed to store token', error);
      throw error;
    }
  },

  /**
   * Get the stored authentication token.
   */
  async getToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(KEYS.TOKEN);
    } catch (error) {
      logger.error('Failed to get token', error);
      return null;
    }
  },

  /**
   * Remove the authentication token.
   */
  async removeToken(): Promise<void> {
    try {
      await AsyncStorage.removeItem(KEYS.TOKEN);
    } catch (error) {
      logger.error('Failed to remove token', error);
      throw error;
    }
  },

  /**
   * Store user data.
   */
  async setUser(user: User): Promise<void> {
    try {
      await AsyncStorage.setItem(KEYS.USER, JSON.stringify(user));
    } catch (error) {
      logger.error('Failed to store user', error);
      throw error;
    }
  },

  /**
   * Get stored user data.
   */
  async getUser(): Promise<User | null> {
    try {
      const userData = await AsyncStorage.getItem(KEYS.USER);
      if (userData) {
        return JSON.parse(userData) as User;
      }
      return null;
    } catch (error) {
      logger.error('Failed to get user', error);
      return null;
    }
  },

  /**
   * Remove stored user data.
   */
  async removeUser(): Promise<void> {
    try {
      await AsyncStorage.removeItem(KEYS.USER);
    } catch (error) {
      logger.error('Failed to remove user', error);
      throw error;
    }
  },

  /**
   * Clear all authentication data.
   */
  async clearAuth(): Promise<void> {
    try {
      await AsyncStorage.multiRemove([KEYS.TOKEN, KEYS.USER]);
    } catch (error) {
      logger.error('Failed to clear auth data', error);
      throw error;
    }
  },

  /**
   * Store the device ID (for FCM registration).
   */
  async setDeviceId(deviceId: string): Promise<void> {
    try {
      await AsyncStorage.setItem(KEYS.DEVICE_ID, deviceId);
    } catch (error) {
      logger.error('Failed to store device ID', error);
      throw error;
    }
  },

  /**
   * Get the stored device ID.
   */
  async getDeviceId(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(KEYS.DEVICE_ID);
    } catch (error) {
      logger.error('Failed to get device ID', error);
      return null;
    }
  },

  /**
   * Store the FCM token.
   */
  async setFcmToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem(KEYS.FCM_TOKEN, token);
    } catch (error) {
      logger.error('Failed to store FCM token', error);
      throw error;
    }
  },

  /**
   * Get the stored FCM token.
   */
  async getFcmToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(KEYS.FCM_TOKEN);
    } catch (error) {
      logger.error('Failed to get FCM token', error);
      return null;
    }
  },

  /**
   * Clear all app data.
   */
  async clearAll(): Promise<void> {
    try {
      const keys = Object.values(KEYS);
      await AsyncStorage.multiRemove(keys);
    } catch (error) {
      logger.error('Failed to clear all data', error);
      throw error;
    }
  },
};
