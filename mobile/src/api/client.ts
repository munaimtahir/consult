/**
 * Base API client using Axios.
 * Handles authentication tokens, request/response interceptors, and error handling.
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { ENV } from '../config/env';
import { storage } from '../services/storage';
import { ApiError } from './types';

/**
 * Create the base axios instance with default configuration.
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: ENV.API_BASE_URL,
  timeout: ENV.REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

/**
 * Request interceptor to add authentication token.
 */
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    try {
      const token = await storage.getToken();
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      // Silently fail if storage is not available
      console.warn('Failed to get auth token from storage:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for error handling.
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    // Handle 401 Unauthorized - clear token and redirect to login
    if (error.response?.status === 401) {
      await storage.clearAuth();
      // The auth hook will handle navigation to login
    }
    
    // Format error message for display
    const errorMessage = getErrorMessage(error);
    
    return Promise.reject({
      ...error,
      message: errorMessage,
    });
  }
);

/**
 * Extract a user-friendly error message from an Axios error.
 */
function getErrorMessage(error: AxiosError<ApiError>): string {
  // Check for network errors
  if (!error.response) {
    if (error.code === 'ECONNABORTED') {
      return 'Request timed out. Please check your connection and try again.';
    }
    return 'Network error. Please check your internet connection.';
  }

  // Check for server errors
  if (error.response.status >= 500) {
    return 'Server error. Please try again later.';
  }

  // Try to extract error message from response
  const data = error.response.data;
  if (data) {
    if (typeof data === 'string') {
      return data;
    }
    if (data.detail) {
      return data.detail;
    }
    if (data.error) {
      return data.error;
    }
    if (data.message) {
      return data.message;
    }
    // Check for field-level errors
    const firstKey = Object.keys(data)[0];
    if (firstKey && Array.isArray(data[firstKey])) {
      return `${firstKey}: ${data[firstKey][0]}`;
    }
  }

  // Default messages based on status code
  switch (error.response.status) {
    case 400:
      return 'Invalid request. Please check your input.';
    case 401:
      return 'Session expired. Please log in again.';
    case 403:
      return 'You do not have permission to perform this action.';
    case 404:
      return 'The requested resource was not found.';
    case 422:
      return 'Validation error. Please check your input.';
    default:
      return 'An unexpected error occurred. Please try again.';
  }
}

/**
 * Check if an error is a network error.
 */
export function isNetworkError(error: unknown): boolean {
  if (error && typeof error === 'object' && 'response' in error) {
    return !(error as AxiosError).response;
  }
  return false;
}

/**
 * Check if an error is a server error (5xx).
 */
export function isServerError(error: unknown): boolean {
  if (error && typeof error === 'object' && 'response' in error) {
    const status = (error as AxiosError).response?.status;
    return status !== undefined && status >= 500;
  }
  return false;
}

export default apiClient;
