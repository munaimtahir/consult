/**
 * Environment configuration for the Consult mobile app.
 * Uses React Native's __DEV__ flag to switch between environments.
 */

declare const __DEV__: boolean;

export const ENV = {
  /**
   * Base URL for the API.
   * In development, points to the dev server.
   * In production, points to the production server.
   */
  API_BASE_URL: __DEV__
    ? 'https://dev-consult.pmc.edu.pk/api/v1'
    : 'https://consult.pmc.edu.pk/api/v1',

  /**
   * Token storage key for AsyncStorage.
   */
  TOKEN_STORAGE_KEY: '@consult_auth_token',

  /**
   * User data storage key for AsyncStorage.
   */
  USER_STORAGE_KEY: '@consult_user_data',

  /**
   * Device registration storage key.
   */
  DEVICE_ID_STORAGE_KEY: '@consult_device_id',

  /**
   * FCM token storage key.
   */
  FCM_TOKEN_STORAGE_KEY: '@consult_fcm_token',

  /**
   * Request timeout in milliseconds.
   */
  REQUEST_TIMEOUT: 30000,
};
