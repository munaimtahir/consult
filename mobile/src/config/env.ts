/**
 * Environment configuration for the Consult mobile app.
 * Uses React Native's __DEV__ flag to switch between environments.
 * 
 * ⚠️ IMPORTANT: Update API_BASE_URL for your staging/production server
 * The URL must point to a valid Django REST API backend running the
 * Hospital Consult System.
 */

declare const __DEV__: boolean;

export const ENV = {
  /**
   * Base URL for the API.
   * In development, points to the dev server.
   * In production, points to the production server.
   * 
   * ⚠️ Update these URLs to match your actual backend deployment:
   * - Development: Your local or staging server URL
   * - Production: Your production server URL
   * 
   * The API endpoints are relative to this base URL:
   * - Auth: /auth/token/, /auth/users/me/
   * - Consults: /consults/requests/
   * - Dashboard: /admin/dashboard/department/
   * - Devices: /devices/register/, /devices/update-token/
   */
  API_BASE_URL: __DEV__
    ? 'https://dev-consult.pmc.edu.pk/api/v1'  // ← Update for your dev server
    : 'https://consult.pmc.edu.pk/api/v1',     // ← Update for your prod server

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
   * Request timeout in milliseconds (30 seconds).
   */
  REQUEST_TIMEOUT: 30000,
};
