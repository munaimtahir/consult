import { useContext } from 'react';
import { AuthContext } from '../context/authContextValue';

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
