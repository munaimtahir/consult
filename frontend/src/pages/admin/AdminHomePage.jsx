import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

/**
 * Admin Panel Home Page.
 * Shows quick links to admin sections the user can access.
 */
export default function AdminHomePage() {
    const { user } = useAuth();
    const permissions = user?.permissions || {};
    const isSuperAdmin = user?.is_superuser || user?.is_admin_user;

    const adminSections = [
        {
            title: 'Users Management',
            description: 'Create, edit, and manage system users',
            link: '/admin/users',
            icon: '👥',
            permission: 'can_manage_users',
        },
        {
            title: 'Departments Management',
            description: 'Manage departments and their hierarchy',
            link: '/admin/departments',
            icon: '🏥',
            permission: 'can_manage_departments',
        },
        {
            title: 'Department Dashboard',
            description: 'View department-level consult statistics',
            link: '/admin/dashboards/department',
            icon: '📊',
            permission: 'can_view_department_dashboard',
        },
        {
            title: 'Global Dashboard',
            description: 'View system-wide statistics and analytics',
            link: '/admin/dashboards/global',
            icon: '🌐',
            permission: 'can_view_global_dashboard',
        },
    ];

    const accessibleSections = adminSections.filter(
        section => isSuperAdmin || permissions[section.permission]
    );

    return (
        <div className="max-w-7xl mx-auto px-4 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
                <p className="text-gray-600 mt-2">
                    Manage users, departments, and view system analytics
                </p>
            </div>

            {/* Admin Sections Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {accessibleSections.map((section) => (
                    <Link
                        key={section.link}
                        to={section.link}
                        className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow"
                    >
                        <div className="text-4xl mb-4">{section.icon}</div>
                        <h2 className="text-xl font-semibold text-gray-900 mb-2">
                            {section.title}
                        </h2>
                        <p className="text-gray-600">{section.description}</p>
                    </Link>
                ))}
            </div>

            {/* User Info Card */}
            <div className="mt-8 bg-white rounded-lg shadow-sm border p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Admin Access</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="flex items-center space-x-2">
                        <span className={`w-3 h-3 rounded-full ${isSuperAdmin ? 'bg-green-500' : 'bg-gray-300'}`} />
                        <span className="text-sm text-gray-700">System Admin</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <span className={`w-3 h-3 rounded-full ${permissions.can_manage_users || isSuperAdmin ? 'bg-green-500' : 'bg-gray-300'}`} />
                        <span className="text-sm text-gray-700">Manage Users</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <span className={`w-3 h-3 rounded-full ${permissions.can_manage_departments || isSuperAdmin ? 'bg-green-500' : 'bg-gray-300'}`} />
                        <span className="text-sm text-gray-700">Manage Departments</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <span className={`w-3 h-3 rounded-full ${permissions.can_view_department_dashboard || isSuperAdmin ? 'bg-green-500' : 'bg-gray-300'}`} />
                        <span className="text-sm text-gray-700">Dept Dashboard</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <span className={`w-3 h-3 rounded-full ${permissions.can_view_global_dashboard || isSuperAdmin ? 'bg-green-500' : 'bg-gray-300'}`} />
                        <span className="text-sm text-gray-700">Global Dashboard</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <span className={`w-3 h-3 rounded-full ${permissions.can_manage_permissions || isSuperAdmin ? 'bg-green-500' : 'bg-gray-300'}`} />
                        <span className="text-sm text-gray-700">Manage Permissions</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
