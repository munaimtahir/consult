# Token Refresh Implementation Guide

## Current Status

The token refresh functionality is **not yet implemented** in the mobile app, although:
- ✅ Backend endpoint exists: `/auth/token/refresh/`
- ✅ Backend uses `django-rest-framework-simplejwt`
- ✅ Login response includes both `access` and `refresh` tokens
- ✅ TypeScript types are defined (`TokenResponse` includes `refresh` field)
- ⚠️ Mobile app currently only stores access token
- ⚠️ No automatic token refresh on 401 errors

## Overview

The Django backend uses JWT (JSON Web Tokens) with SimpleJWT, which provides:
- **Access tokens**: Short-lived (typically 5-60 minutes), used for API authentication
- **Refresh tokens**: Long-lived (typically days/weeks), used to obtain new access tokens

When an access token expires (returns 401 Unauthorized), the app should automatically use the refresh token to get a new access token without requiring the user to log in again.

## Backend API Details

### Endpoint
- **URL**: `/api/v1/auth/token/refresh/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
  ```
- **Response**:
  ```json
  {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
  ```

### Error Responses
- **400 Bad Request**: Invalid refresh token format
- **401 Unauthorized**: Refresh token expired or invalid
- **500 Server Error**: Internal server error

## Implementation Steps

### 1. Add Refresh Token Storage Key

Update `mobile/src/config/env.ts`:

```typescript
export const ENV = {
  // ... existing config
  
  /**
   * Refresh token storage key for AsyncStorage.
   */
  REFRESH_TOKEN_STORAGE_KEY: '@consult_refresh_token',
  
  // ... rest of config
};
```

### 2. Update Storage Service

Add refresh token methods to `mobile/src/services/storage.ts`:

```typescript
// Add to KEYS object
const KEYS = {
  TOKEN: ENV.TOKEN_STORAGE_KEY,
  REFRESH_TOKEN: ENV.REFRESH_TOKEN_STORAGE_KEY, // Add this
  USER: ENV.USER_STORAGE_KEY,
  // ... existing keys
} as const;

// Add to storage object
export const storage = {
  // ... existing methods
  
  /**
   * Store the refresh token.
   */
  async setRefreshToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem(KEYS.REFRESH_TOKEN, token);
    } catch (error) {
      logger.error('Failed to store refresh token', error);
      throw error;
    }
  },

  /**
   * Get the stored refresh token.
   */
  async getRefreshToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(KEYS.REFRESH_TOKEN);
    } catch (error) {
      logger.error('Failed to get refresh token', error);
      return null;
    }
  },

  /**
   * Remove the refresh token.
   */
  async removeRefreshToken(): Promise<void> {
    try {
      await AsyncStorage.removeItem(KEYS.REFRESH_TOKEN);
    } catch (error) {
      logger.error('Failed to remove refresh token', error);
      throw error;
    }
  },

  /**
   * Clear all authentication data (update existing method).
   */
  async clearAuth(): Promise<void> {
    try {
      await AsyncStorage.multiRemove([
        KEYS.TOKEN,
        KEYS.REFRESH_TOKEN, // Add this
        KEYS.USER
      ]);
    } catch (error) {
      logger.error('Failed to clear auth data', error);
      throw error;
    }
  },
  
  // ... rest of methods
};
```

### 3. Update Login Function

Update `mobile/src/api/auth.ts` to store refresh token:

```typescript
export async function login(email: string, password: string): Promise<User> {
  logger.apiRequest('POST', '/auth/token/');
  
  // Get JWT tokens
  const tokenResponse = await apiClient.post<TokenResponse>('/auth/token/', {
    email,
    password,
  });
  
  const { access, refresh } = tokenResponse.data;
  
  // Store both tokens
  await storage.setToken(access);
  await storage.setRefreshToken(refresh); // Add this
  
  // Get user profile
  const user = await getCurrentUser();
  
  logger.info('User logged in successfully', { userId: user.id });
  
  return user;
}
```

### 4. Implement Refresh Token Function

Update the `refreshToken` function in `mobile/src/api/auth.ts`:

```typescript
/**
 * Refresh the authentication token.
 * Uses the stored refresh token to get a new access token.
 */
export async function refreshToken(): Promise<string | null> {
  try {
    const refreshTokenValue = await storage.getRefreshToken();
    
    if (!refreshTokenValue) {
      logger.warn('No refresh token available');
      return null;
    }
    
    logger.apiRequest('POST', '/auth/token/refresh/');
    
    // Create a new axios instance without interceptors to avoid infinite loop
    const response = await axios.post<TokenResponse>(
      `${ENV.API_BASE_URL}/auth/token/refresh/`,
      { refresh: refreshTokenValue },
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: ENV.REQUEST_TIMEOUT,
      }
    );
    
    const { access, refresh: newRefreshToken } = response.data;
    
    // Store new tokens
    await storage.setToken(access);
    await storage.setRefreshToken(newRefreshToken);
    
    logger.info('Token refreshed successfully');
    
    return access;
  } catch (error) {
    logger.error('Token refresh failed', error);
    
    // If refresh fails, clear auth data (refresh token expired)
    await storage.clearAuth();
    
    return null;
  }
}
```

**Note**: Import `axios` directly at the top of the file:
```typescript
import axios from 'axios';
import { ENV } from '../config/env';
```

### 5. Update API Client Interceptor

Update `mobile/src/api/client.ts` to automatically refresh tokens on 401 errors:

```typescript
import { refreshToken } from './auth';

// ... existing code ...

/**
 * Response interceptor for error handling and automatic token refresh.
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    // Handle 401 Unauthorized - try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Attempt to refresh the token
        const newAccessToken = await refreshToken();
        
        if (newAccessToken && originalRequest.headers) {
          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, clear auth and let the error propagate
        logger.warn('Token refresh failed in interceptor', refreshError);
      }
      
      // If refresh failed, clear auth data
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
```

### 6. Update Check Auth Function

Update `checkAuth` in `mobile/src/api/auth.ts` to handle token refresh:

```typescript
/**
 * Check if the user is authenticated by validating the stored token.
 * Automatically refreshes token if expired.
 * Returns the user if authenticated, null otherwise.
 */
export async function checkAuth(): Promise<User | null> {
  try {
    const token = await storage.getToken();
    
    if (!token) {
      return null;
    }
    
    // Try to get the current user (validates the token)
    try {
      const user = await getCurrentUser();
      return user;
    } catch (error) {
      // Token might be expired, try to refresh
      const axiosError = error as AxiosError;
      
      if (axiosError.response?.status === 401) {
        logger.info('Access token expired, attempting refresh');
        const newToken = await refreshToken();
        
        if (newToken) {
          // Retry getting user with new token
          const user = await getCurrentUser();
          return user;
        }
      }
      
      // Refresh failed or other error
      throw error;
    }
  } catch (error) {
    // Token is invalid or expired, and refresh failed
    logger.warn('Auth check failed, clearing stored auth data', error);
    await storage.clearAuth();
    return null;
  }
}
```

### 7. Update Logout Function

Ensure logout clears refresh token (already handled by `clearAuth`, but verify):

```typescript
export async function logout(): Promise<void> {
  logger.info('User logging out');
  
  // Clear all auth data (including refresh token)
  await storage.clearAuth();
  
  logger.info('User logged out successfully');
}
```

## Testing

### Manual Testing

1. **Login and Token Storage**
   - Login successfully
   - Check AsyncStorage contains both access and refresh tokens
   - Verify tokens are stored with correct keys

2. **Token Refresh on Expiry**
   - Wait for access token to expire (or manually clear it from storage)
   - Make an API call
   - Verify refresh token is used automatically
   - Verify new tokens are stored
   - Verify original request succeeds

3. **Refresh Token Expiry**
   - Clear refresh token or wait for it to expire
   - Make an API call
   - Verify user is logged out automatically
   - Verify navigation to login screen

4. **Network Error Handling**
   - Disconnect network
   - Attempt token refresh
   - Verify graceful error handling
   - Verify user isn't logged out on network errors

### Test Cases

```typescript
// Test case 1: Successful token refresh
describe('Token Refresh', () => {
  it('should refresh token when access token expires', async () => {
    // Mock expired access token
    // Mock refresh endpoint
    // Verify new tokens are stored
    // Verify request succeeds
  });

  it('should logout when refresh token expires', async () => {
    // Mock expired refresh token
    // Verify auth is cleared
    // Verify navigation to login
  });
});
```

## Error Handling

### Scenarios to Handle

1. **Refresh Token Expired**
   - Clear all auth data
   - Navigate to login screen
   - Show message: "Session expired. Please log in again."

2. **Network Error During Refresh**
   - Don't clear auth data immediately
   - Show network error message
   - Allow user to retry

3. **Invalid Refresh Token**
   - Clear auth data
   - Navigate to login screen

4. **Concurrent Refresh Requests**
   - Prevent multiple simultaneous refresh attempts
   - Queue requests and retry after refresh completes

### Implementation for Concurrent Requests

Add a refresh promise cache to prevent concurrent refresh attempts:

```typescript
// In auth.ts
let refreshTokenPromise: Promise<string | null> | null = null;

export async function refreshToken(): Promise<string | null> {
  // If already refreshing, return the existing promise
  if (refreshTokenPromise) {
    return refreshTokenPromise;
  }
  
  refreshTokenPromise = (async () => {
    try {
      // ... existing refresh logic ...
      return access;
    } finally {
      // Clear the promise after completion
      refreshTokenPromise = null;
    }
  })();
  
  return refreshTokenPromise;
}
```

## Security Considerations

1. **Token Storage**
   - ✅ Tokens stored in AsyncStorage (encrypted on iOS, can use secure storage libraries)
   - ⚠️ Consider using `react-native-keychain` for enhanced security on both platforms
   - ⚠️ Never log tokens in production

2. **Token Transmission**
   - ✅ Always use HTTPS
   - ✅ Tokens sent in Authorization header, not URL
   - ✅ Refresh token only sent to refresh endpoint

3. **Token Expiry**
   - Access tokens should be short-lived (backend configurable)
   - Refresh tokens should expire after reasonable period
   - Clear tokens on logout

4. **Token Rotation**
   - Backend returns new refresh token on each refresh
   - Always store the new refresh token
   - This invalidates old refresh tokens for security

## Configuration

### Backend Token Settings

Verify backend JWT settings in Django (`settings.py`):

```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # 1 hour
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # 7 days
    'ROTATE_REFRESH_TOKENS': True,                   # Issue new refresh token on refresh
    'BLACKLIST_AFTER_ROTATION': True,                # Blacklist old refresh tokens
}
```

## Migration Notes

### For Existing Users

If implementing token refresh after initial release:
- Existing users will need to log in again (no refresh tokens stored)
- Consider showing a message: "Please log in again for improved security"

### Version Compatibility

- Backend already supports token refresh (no backend changes needed)
- Frontend web app already implements this pattern
- Mobile app implementation should match frontend behavior

## References

- [Django REST Framework SimpleJWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [React Native AsyncStorage Documentation](https://react-native-async-storage.github.io/async-storage/)
- Frontend web implementation: `frontend/src/api/client.js` (lines 22-53)

## Implementation Checklist

- [ ] Add `REFRESH_TOKEN_STORAGE_KEY` to `env.ts`
- [ ] Add refresh token methods to `storage.ts`
- [ ] Update `login()` to store refresh token
- [ ] Implement `refreshToken()` function
- [ ] Update API client interceptor for automatic refresh
- [ ] Update `checkAuth()` to handle token refresh
- [ ] Test login and token storage
- [ ] Test automatic token refresh
- [ ] Test refresh token expiry handling
- [ ] Test network error scenarios
- [ ] Add error handling for concurrent refresh requests
- [ ] Update logout to clear refresh token
- [ ] Verify security best practices

## Next Steps After Implementation

1. Test thoroughly on physical devices
2. Monitor token refresh success rates
3. Add analytics for token refresh events
4. Consider implementing token refresh before expiry (proactive refresh)
5. Add user-facing error messages for refresh failures

