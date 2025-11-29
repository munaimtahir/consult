/**
 * Authentication API functions.
 */

import apiClient from './client';
import { TokenResponse, User } from './types';
import { storage } from '../services/storage';
import { logger } from '../services/logger';

/**
 * Login with email and password.
 * Uses JWT token authentication.
 */
export async function login(email: string, password: string): Promise<User> {
  logger.apiRequest('POST', '/auth/token/');
  
  // Get JWT token
  const tokenResponse = await apiClient.post<TokenResponse>('/auth/token/', {
    email,
    password,
  });
  
  const { access } = tokenResponse.data;
  // Note: refresh token handling can be added here when backend supports it
  
  // Store the access token
  await storage.setToken(access);
  
  // Get user profile
  const user = await getCurrentUser();
  
  logger.info('User logged in successfully', { userId: user.id });
  
  return user;
}

/**
 * Get the current authenticated user's profile.
 */
export async function getCurrentUser(): Promise<User> {
  logger.apiRequest('GET', '/auth/users/me/');
  
  const response = await apiClient.get<User>('/auth/users/me/');
  
  // Store user data
  await storage.setUser(response.data);
  
  logger.apiResponse('GET', '/auth/users/me/', 200);
  
  return response.data;
}

/**
 * Logout the current user.
 * Clears stored tokens and user data.
 */
export async function logout(): Promise<void> {
  logger.info('User logging out');
  
  // Clear all auth data from storage
  await storage.clearAuth();
  
  logger.info('User logged out successfully');
}

/**
 * Check if the user is authenticated by validating the stored token.
 * Returns the user if authenticated, null otherwise.
 */
export async function checkAuth(): Promise<User | null> {
  try {
    const token = await storage.getToken();
    
    if (!token) {
      return null;
    }
    
    // Try to get the current user (validates the token)
    const user = await getCurrentUser();
    return user;
  } catch (error) {
    // Token is invalid or expired
    logger.warn('Auth check failed, clearing stored auth data', error);
    await storage.clearAuth();
    return null;
  }
}

/**
 * Refresh the authentication token.
 * TODO: Implement token refresh logic if backend supports it.
 */
export async function refreshToken(): Promise<string | null> {
  // TODO: Implement refresh token logic
  // This would call /auth/token/refresh/ with the refresh token
  logger.warn('Token refresh not implemented');
  return null;
}
