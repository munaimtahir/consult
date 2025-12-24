import { useEffect, useState, useRef } from 'react';
import { useAuth } from './useAuth';

/**
 * A custom hook for managing a WebSocket connection for real-time
 * notifications.
 *
 * This hook establishes a WebSocket connection, handles incoming messages,
 * and manages the connection state. It also includes logic for
 * auto-reconnection and browser notifications.
 *
 * Keystone Compatibility: Supports path-based routing by constructing
 * WebSocket URL relative to the configured WS endpoint.
 *
 * @returns {{
 *   notifications: object[],
 *   isConnected: boolean,
 *   clearNotifications: () => void
 * }} An object containing the list of notifications, the connection
 * status, and a function to clear notifications.
 */
export const useWebSocket = () => {
    const { user } = useAuth();
    const socketRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);
    const [notifications, setNotifications] = useState([]);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        // Request notification permission
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }

        if (!user) return;

        const connect = () => {
            const token = localStorage.getItem('access_token');
            // Keystone Compatibility: Use configured WS URL (includes subpath if needed)
            // The VITE_WS_URL should be configured as ws://VPS_IP/{APP_SLUG}/ws or ws://VPS_IP/ws
            const wsUrl = `${import.meta.env.VITE_WS_URL}/notifications/?token=${token}`;

            const ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log('WebSocket connected');
                setIsConnected(true);
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                setNotifications((prev) => [data, ...prev]);

                // Show browser notification if permitted
                if (Notification.permission === 'granted') {
                    new Notification(data.message || 'New notification', {
                        body: data.message,
                        icon: '/icon.png',
                    });
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            ws.onclose = () => {
                console.log('WebSocket disconnected');
                setIsConnected(false);
                // Attempt to reconnect after 5 seconds
                reconnectTimeoutRef.current = setTimeout(connect, 5000);
            };

            socketRef.current = ws;
        };

        connect();

        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (socketRef.current) {
                socketRef.current.close();
            }
        };
    }, [user]);

    const clearNotifications = () => {
        setNotifications([]);
    };

    return {
        notifications,
        isConnected,
        clearNotifications,
    };
};
