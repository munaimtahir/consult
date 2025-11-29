/**
 * Dashboard hook for managing HOD dashboard data.
 */

import { useState, useCallback } from 'react';
import { HODDashboardData, getHODDashboard } from '../api/dashboard';
import { logger } from '../services/logger';

/**
 * Dashboard state.
 */
interface DashboardState {
  data: HODDashboardData | null;
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
}

/**
 * Initial state.
 */
const initialState: DashboardState = {
  data: null,
  isLoading: false,
  isRefreshing: false,
  error: null,
};

/**
 * Hook for managing HOD dashboard data.
 */
export function useDashboard() {
  const [state, setState] = useState<DashboardState>(initialState);

  /**
   * Fetch dashboard data.
   */
  const fetchDashboard = useCallback(async (refresh = false) => {
    try {
      if (refresh) {
        setState(prev => ({ ...prev, isRefreshing: true, error: null }));
      } else {
        setState(prev => ({ ...prev, isLoading: true, error: null }));
      }

      const data = await getHODDashboard();

      setState({
        data,
        isLoading: false,
        isRefreshing: false,
        error: null,
      });

      logger.info('Dashboard data fetched');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch dashboard data';
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        isRefreshing: false,
        error: errorMessage,
      }));

      logger.error('Failed to fetch dashboard data', error);
    }
  }, []);

  /**
   * Refresh dashboard data.
   */
  const refresh = useCallback(() => {
    return fetchDashboard(true);
  }, [fetchDashboard]);

  /**
   * Clear error.
   */
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    fetchDashboard,
    refresh,
    clearError,
  };
}
