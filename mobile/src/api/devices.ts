/**
 * Device registration API functions for push notifications.
 */

import apiClient from './client';
import { DeviceRegistrationRequest, DeviceRegistrationResponse } from './types';
import { logger } from '../services/logger';

/**
 * Register a device for push notifications.
 * This should be called after login and whenever the FCM token refreshes.
 * 
 * NOTE: The backend device registration endpoint may not exist yet.
 * This function handles the error gracefully and returns a mock response for development.
 */
export async function registerDevice(
  deviceId: string,
  fcmToken: string,
  platform: 'android' | 'ios' = 'android'
): Promise<DeviceRegistrationResponse> {
  logger.apiRequest('POST', '/devices/register/', { device_id: deviceId, platform });
  
  const payload: DeviceRegistrationRequest = {
    device_id: deviceId,
    fcm_token: fcmToken,
    platform,
  };
  
  try {
    const response = await apiClient.post<DeviceRegistrationResponse>('/devices/register/', payload);
    
    logger.apiResponse('POST', '/devices/register/', 200);
    
    return response.data;
  } catch (error) {
    // Log the error but don't fail completely - the app should still work without push notifications
    // This allows development to continue even if the backend endpoint doesn't exist yet
    logger.warn('Device registration failed. Push notifications may not work.', error);
    
    // Return a mock response indicating registration was not successful
    return {
      id: 0,
      device_id: deviceId,
      fcm_token: fcmToken,
      platform,
      is_active: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }
}

/**
 * Unregister a device from push notifications.
 * This should be called on logout.
 */
export async function unregisterDevice(deviceId: string): Promise<void> {
  logger.apiRequest('POST', '/devices/unregister/', { device_id: deviceId });
  
  try {
    await apiClient.post('/devices/unregister/', {
      device_id: deviceId,
    });
    
    logger.apiResponse('POST', '/devices/unregister/', 200);
  } catch (error) {
    // Log but don't fail - the device will be cleaned up eventually
    logger.warn('Device unregistration failed', error);
  }
}

/**
 * Update the FCM token for an existing device registration.
 */
export async function updateFcmToken(deviceId: string, newFcmToken: string): Promise<void> {
  logger.apiRequest('PATCH', '/devices/update-token/', { device_id: deviceId });
  
  try {
    await apiClient.patch('/devices/update-token/', {
      device_id: deviceId,
      fcm_token: newFcmToken,
    });
    
    logger.apiResponse('PATCH', '/devices/update-token/', 200);
  } catch (error) {
    // Fall back to full registration
    logger.warn('Token update failed, attempting full registration', error);
    await registerDevice(deviceId, newFcmToken);
  }
}
