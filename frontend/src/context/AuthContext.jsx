import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../api';

const AuthContext = createContext(null);

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
export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if user is logged in on mount
        const token = localStorage.getItem('access_token');
        if (token) {
            loadUser();
        } else {
            setLoading(false);
        }
    }, []);

    const loadUser = async () => {
        try {
            const userData = await authAPI.getCurrentUser();
            setUser(userData);
        } catch (error) {
            console.error('Failed to load user:', error);
            logout();
        } finally {
            setLoading(false);
        }
    };

    const login = async (email, password) => {
        const data = await authAPI.login(email, password);
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        await loadUser();
        return data;
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

/**
 * A custom hook for accessing the authentication context.
 *
 * This hook provides an easy way to access the `user` object, `login` and
 * `logout` functions, and the `loading` state from the `AuthContext`.
 *
 * @returns {{
 *   user: object | null,
 *   login: (email, password) => Promise<object>,
 *   logout: () => void,
 *   loading: boolean
 * }} The authentication context.
 */
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};
