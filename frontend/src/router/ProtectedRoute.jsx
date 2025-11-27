import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

/**
 * A component that protects routes from unauthenticated access.
 *
 * This component checks if a user is authenticated. If the user is not
 * authenticated, it redirects them to the login page. While checking the
 * authentication status, it displays a loading indicator.
 *
 * @param {object} props - The component's props.
 * @param {React.ReactNode} props.children - The child components to be
 *   rendered if the user is authenticated.
 * @returns {React.ReactElement | null} The child components if the user is
 *   authenticated, a redirect to the login page if not, or a loading
 *   indicator.
 */
export default function ProtectedRoute({ children }) {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-xl">Loading...</div>
            </div>
        );
    }

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    return children;
}
