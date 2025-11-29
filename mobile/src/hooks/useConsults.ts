/**
 * Consults hook for managing consult data and actions.
 */

import { useState, useCallback } from 'react';
import {
  ConsultListItem,
  ConsultDetail,
  ConsultNote,
  AddNoteRequest,
  PaginatedResponse,
} from '../api/types';
import * as consultsApi from '../api/consults';
import { ConsultListParams } from '../api/consults';
import { logger } from '../services/logger';

/**
 * Consults state.
 */
interface ConsultsState {
  consults: ConsultListItem[];
  currentConsult: ConsultDetail | null;
  isLoading: boolean;
  isRefreshing: boolean;
  isLoadingMore: boolean;
  error: string | null;
  hasMore: boolean;
  page: number;
  totalCount: number;
}

/**
 * Initial state.
 */
const initialState: ConsultsState = {
  consults: [],
  currentConsult: null,
  isLoading: false,
  isRefreshing: false,
  isLoadingMore: false,
  error: null,
  hasMore: true,
  page: 1,
  totalCount: 0,
};

/**
 * Hook for managing my consults.
 */
export function useMyConsults() {
  const [state, setState] = useState<ConsultsState>(initialState);

  /**
   * Fetch consults with optional filters.
   */
  const fetchConsults = useCallback(async (params: ConsultListParams = {}, refresh = false) => {
    try {
      if (refresh) {
        setState(prev => ({ ...prev, isRefreshing: true, error: null }));
      } else if (state.page === 1) {
        setState(prev => ({ ...prev, isLoading: true, error: null }));
      } else {
        setState(prev => ({ ...prev, isLoadingMore: true, error: null }));
      }

      const page = refresh ? 1 : state.page;
      const response = await consultsApi.getMyConsults({ ...params, page });

      setState(prev => ({
        ...prev,
        consults: refresh || page === 1 ? response.results : [...prev.consults, ...response.results],
        isLoading: false,
        isRefreshing: false,
        isLoadingMore: false,
        hasMore: response.next !== null,
        page: refresh ? 2 : prev.page + 1,
        totalCount: response.count,
        error: null,
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch consults';
      setState(prev => ({
        ...prev,
        isLoading: false,
        isRefreshing: false,
        isLoadingMore: false,
        error: errorMessage,
      }));
    }
  }, [state.page]);

  /**
   * Refresh consults.
   */
  const refresh = useCallback((params: ConsultListParams = {}) => {
    setState(prev => ({ ...prev, page: 1 }));
    return fetchConsults(params, true);
  }, [fetchConsults]);

  /**
   * Load more consults.
   */
  const loadMore = useCallback((params: ConsultListParams = {}) => {
    if (state.hasMore && !state.isLoadingMore) {
      return fetchConsults(params);
    }
  }, [state.hasMore, state.isLoadingMore, fetchConsults]);

  /**
   * Clear error.
   */
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    fetchConsults,
    refresh,
    loadMore,
    clearError,
  };
}

/**
 * Hook for managing department consults.
 */
export function useDepartmentConsults() {
  const [state, setState] = useState<ConsultsState>(initialState);

  /**
   * Fetch department consults.
   */
  const fetchConsults = useCallback(async (params: ConsultListParams = {}, refresh = false) => {
    try {
      if (refresh) {
        setState(prev => ({ ...prev, isRefreshing: true, error: null }));
      } else if (state.page === 1) {
        setState(prev => ({ ...prev, isLoading: true, error: null }));
      } else {
        setState(prev => ({ ...prev, isLoadingMore: true, error: null }));
      }

      const page = refresh ? 1 : state.page;
      const response = await consultsApi.getDepartmentConsults({ ...params, page });

      setState(prev => ({
        ...prev,
        consults: refresh || page === 1 ? response.results : [...prev.consults, ...response.results],
        isLoading: false,
        isRefreshing: false,
        isLoadingMore: false,
        hasMore: response.next !== null,
        page: refresh ? 2 : prev.page + 1,
        totalCount: response.count,
        error: null,
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch department consults';
      setState(prev => ({
        ...prev,
        isLoading: false,
        isRefreshing: false,
        isLoadingMore: false,
        error: errorMessage,
      }));
    }
  }, [state.page]);

  const refresh = useCallback((params: ConsultListParams = {}) => {
    setState(prev => ({ ...prev, page: 1 }));
    return fetchConsults(params, true);
  }, [fetchConsults]);

  const loadMore = useCallback((params: ConsultListParams = {}) => {
    if (state.hasMore && !state.isLoadingMore) {
      return fetchConsults(params);
    }
  }, [state.hasMore, state.isLoadingMore, fetchConsults]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    fetchConsults,
    refresh,
    loadMore,
    clearError,
  };
}

/**
 * Hook for managing a single consult detail.
 */
export function useConsultDetail(consultId: number) {
  const [consult, setConsult] = useState<ConsultDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch consult details.
   */
  const fetchConsult = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const data = await consultsApi.getConsultById(consultId);
      setConsult(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch consult details';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [consultId]);

  /**
   * Acknowledge the consult.
   */
  const acknowledge = useCallback(async () => {
    try {
      setIsActionLoading(true);
      setError(null);

      const data = await consultsApi.acknowledgeConsult(consultId);
      setConsult(data);
      
      logger.info('Consult acknowledged', { consultId });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to acknowledge consult';
      setError(errorMessage);
      throw err;
    } finally {
      setIsActionLoading(false);
    }
  }, [consultId]);

  /**
   * Complete the consult.
   */
  const complete = useCallback(async () => {
    try {
      setIsActionLoading(true);
      setError(null);

      const data = await consultsApi.completeConsult(consultId);
      setConsult(data);
      
      logger.info('Consult completed', { consultId });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to complete consult';
      setError(errorMessage);
      throw err;
    } finally {
      setIsActionLoading(false);
    }
  }, [consultId]);

  /**
   * Add a note to the consult.
   */
  const addNote = useCallback(async (note: AddNoteRequest): Promise<ConsultNote> => {
    try {
      setIsActionLoading(true);
      setError(null);

      const newNote = await consultsApi.addNoteToConsult(consultId, note);
      
      // Refresh consult to get updated notes
      await fetchConsult();
      
      logger.info('Note added to consult', { consultId });
      
      return newNote;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to add note';
      setError(errorMessage);
      throw err;
    } finally {
      setIsActionLoading(false);
    }
  }, [consultId, fetchConsult]);

  /**
   * Clear error.
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    consult,
    isLoading,
    isActionLoading,
    error,
    fetchConsult,
    acknowledge,
    complete,
    addNote,
    clearError,
  };
}
