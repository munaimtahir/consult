/**
 * Authentication hook for managing user authentication state.
 */

import React, { useState, useEffect, useCallback, createContext, useContext, ReactNode } from 'react';
import { User } from '../api/types';
import * as authApi from '../api/auth';
import { storage } from '../services/storage';
import { logger } from '../services/logger';

/**
 * Auth context state.
 */
interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

/**
 * Auth context value with actions.
 */
interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  clearError: () => void;
}

/**
 * Create the auth context.
 */
const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * Auth provider props.
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Auth provider component.
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
    error: null,
  });

  /**
   * Check authentication status on mount.
   */
  useEffect(() => {
    checkAuth();
  }, []);

  /**
   * Check if the user is authenticated.
   */
  const checkAuth = async () => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const user = await authApi.checkAuth();
      
      if (user) {
        setState({
          user,
          isLoading: false,
          isAuthenticated: true,
          error: null,
        });
      } else {
        setState({
          user: null,
          isLoading: false,
          isAuthenticated: false,
          error: null,
        });
      }
    } catch (error) {
      logger.error('Auth check failed', error);
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
        error: null,
      });
    }
  };

  /**
   * Login with email and password.
   */
  const login = useCallback(async (email: string, password: string) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const user = await authApi.login(email, password);
      
      setState({
        user,
        isLoading: false,
        isAuthenticated: true,
        error: null,
      });
      
      logger.info('User logged in', { userId: user.id });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed. Please check your credentials.';
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      
      throw error;
    }
  }, []);

  /**
   * Logout the current user.
   */
  const logout = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, isLoading: true }));
      
      await authApi.logout();
      
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
        error: null,
      });
      
      logger.info('User logged out');
    } catch (error) {
      logger.error('Logout failed', error);
      
      // Still clear the state even if API call fails
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
        error: null,
      });
    }
  }, []);

  /**
   * Refresh the user data.
   */
  const refreshUser = useCallback(async () => {
    try {
      const user = await authApi.getCurrentUser();
      
      setState(prev => ({
        ...prev,
        user,
      }));
    } catch (error) {
      logger.error('Failed to refresh user', error);
    }
  }, []);

  /**
   * Clear the error state.
   */
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const value: AuthContextValue = {
    ...state,
    login,
    logout,
    refreshUser,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to access auth context.
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}
