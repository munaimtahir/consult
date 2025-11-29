/**
 * Notifications hook for managing push notifications.
 */

import { useState, useEffect, useCallback } from 'react';
import {
  initializeNotifications,
  onNotification,
  NotificationPayload,
  getConsultIdFromNotification,
} from '../services/notifications';
import { logger } from '../services/logger';

/**
 * Notification state.
 */
interface NotificationState {
  isInitialized: boolean;
  lastNotification: NotificationPayload | null;
  pendingConsultId: number | null;
}

/**
 * Initial state.
 */
const initialState: NotificationState = {
  isInitialized: false,
  lastNotification: null,
  pendingConsultId: null,
};

/**
 * Hook for managing push notifications.
 */
export function useNotifications() {
  const [state, setState] = useState<NotificationState>(initialState);

  /**
   * Initialize notifications on mount.
   */
  useEffect(() => {
    let unsubscribe: (() => void) | null = null;

    const init = async () => {
      try {
        const success = await initializeNotifications();
        
        if (success) {
          // Subscribe to notifications
          unsubscribe = onNotification((payload) => {
            handleNotification(payload);
          });
          
          setState(prev => ({ ...prev, isInitialized: true }));
          logger.info('Notifications initialized');
        }
      } catch (error) {
        logger.error('Failed to initialize notifications', error);
      }
    };

    init();

    return () => {
      if (unsubscribe) {
        unsubscribe();
      }
    };
  }, []);

  /**
   * Handle an incoming notification.
   */
  const handleNotification = useCallback((payload: NotificationPayload) => {
    logger.info('Notification received in hook', payload);
    
    const consultId = getConsultIdFromNotification(payload);
    
    setState(prev => ({
      ...prev,
      lastNotification: payload,
      pendingConsultId: consultId,
    }));
  }, []);

  /**
   * Clear the pending consult ID (after navigation).
   */
  const clearPendingConsultId = useCallback(() => {
    setState(prev => ({ ...prev, pendingConsultId: null }));
  }, []);

  /**
   * Clear the last notification.
   */
  const clearLastNotification = useCallback(() => {
    setState(prev => ({ ...prev, lastNotification: null }));
  }, []);

  return {
    ...state,
    clearPendingConsultId,
    clearLastNotification,
  };
}
