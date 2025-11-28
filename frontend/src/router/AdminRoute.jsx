import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

/**
 * A component that protects admin routes from unauthorized access.
 *
 * This component checks if a user has admin panel access. If the user does not
 * have the required permissions, it redirects them to the dashboard page.
 *
 * @param {object} props - The component's props.
 * @param {React.ReactNode} props.children - The child components to be
 *   rendered if the user has admin access.
 * @param {string} [props.requiredPermission] - Optional specific permission required.
 * @returns {React.ReactElement | null} The child components if authorized.
 */
export default function AdminRoute({ children, requiredPermission }) {
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

    // Check if user has admin panel access
    const hasAdminAccess = user.has_admin_panel_access || 
        user.is_admin_user || 
        user.is_superuser ||
        user.permissions?.can_manage_users ||
        user.permissions?.can_manage_departments ||
        user.permissions?.can_view_department_dashboard ||
        user.permissions?.can_view_global_dashboard ||
        user.permissions?.can_manage_consults_globally ||
        user.permissions?.can_manage_permissions;

    if (!hasAdminAccess) {
        return <Navigate to="/dashboard" replace />;
    }

    // Check for specific permission if required
    if (requiredPermission) {
        const hasPermission = user.is_superuser || 
            user.is_admin_user ||
            user.permissions?.[requiredPermission];
        
        if (!hasPermission) {
            return (
                <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                    <div className="text-center">
                        <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
                        <p className="text-gray-600">You do not have permission to access this page.</p>
                    </div>
                </div>
            );
        }
    }

    return children;
}
