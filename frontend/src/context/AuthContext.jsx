import { useState, useEffect, useCallback } from 'react';
import { authAPI } from '../api';
import { AuthContext } from './authContextValue';

/**
 * Provides authentication state and functions to the application.
 *
 * This component manages the user's authentication state, including the
 * current user object, and provides `login` and `logout` functions. It also
 * handles loading the user's data from the server when the application
 * starts.
 *
 * @param {object} props - The component's props.
 * @param {React.ReactNode} props.children - The child components to be
 *   rendered within the provider.
 * @returns {React.ReactElement} The rendered auth provider component.
 */
export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const logout = useCallback(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
    }, []);

    const loadUser = useCallback(async () => {
        try {
            const userData = await authAPI.getCurrentUser();
            setUser(userData);
        } catch (error) {
            console.error('Failed to load user:', error);
            logout();
        } finally {
            setLoading(false);
        }
    }, [logout]);

    useEffect(() => {
        // Check if user is logged in on mount
        const token = localStorage.getItem('access_token');
        if (token) {
            loadUser();
        } else {
            setLoading(false);
        }
    }, [loadUser]);

    const login = async (email, password) => {
        const data = await authAPI.login(email, password);
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        await loadUser();
        return data;
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}
