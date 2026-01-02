import { useAuth } from '../hooks/useAuth';
import { Link, useNavigate } from 'react-router-dom';

/**
 * A shared layout component for the application.
 *
 * This component provides the main structure for all pages, including a
 * navigation bar with links to the dashboard and consults, a user menu
 * with a logout button, and a real-time notification indicator.
 *
 * @param {object} props - The component's props.
 * @param {React.ReactNode} props.children - The child components to be
 *   rendered within the layout.
 * @returns {React.ReactElement} The rendered layout component.
 */
export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Check if user has admin panel access
  const hasAdminAccess = user?.has_admin_panel_access || 
    user?.is_admin_user || 
    user?.is_superuser ||
    user?.permissions?.can_manage_users ||
    user?.permissions?.can_manage_departments ||
    user?.permissions?.can_view_department_dashboard ||
    user?.permissions?.can_view_global_dashboard ||
    user?.permissions?.can_manage_consults_globally ||
    user?.permissions?.can_manage_permissions;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-8">
              <Link to="/dashboard" className="text-xl font-bold text-blue-600">
                Consult System
              </Link>
              <div className="flex space-x-4">
                <Link
                  to="/dashboard"
                  className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Dashboard
                </Link>
                <Link
                  to="/consults"
                  className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Consults
                </Link>
                <Link
                  to="/finance"
                  className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Finance
                </Link>
                {hasAdminAccess && (
                  <Link
                    to="/adminpanel"
                    className="text-purple-700 hover:text-purple-900 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Admin Panel
                  </Link>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* New Consult Button */}
              <Link
                to="/consults/new"
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700"
              >
                + New Consult
              </Link>
              {/* User Menu */}
              <div className="flex items-center space-x-3">
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">
                    {user?.first_name} {user?.last_name}
                  </div>
                  <div className="text-xs text-gray-500">{user?.role}</div>
                </div>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>{children}</main>
    </div>
  );
}
