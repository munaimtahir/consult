import { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

/**
 * A custom hook for managing a WebSocket connection for real-time
 * notifications.
 *
 * This hook establishes a WebSocket connection, handles incoming messages,
 * and manages the connection state. It also includes logic for
 * auto-reconnection and browser notifications.
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
    const [socket, setSocket] = useState(null);
    const [notifications, setNotifications] = useState([]);
    const [isConnected, setIsConnected] = useState(false);

    const connect = useCallback(() => {
        if (!user) return;

        const token = localStorage.getItem('access_token');
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
            setTimeout(connect, 5000);
        };

        setSocket(ws);

        return () => {
            ws.close();
        };
    }, [user]);

    useEffect(() => {
        // Request notification permission
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }

        const cleanup = connect();
        return cleanup;
    }, [connect]);

    const clearNotifications = () => {
        setNotifications([]);
    };

    return {
        notifications,
        isConnected,
        clearNotifications,
    };
};
