import { NavLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const AdminSidebar = () => {
    const { user } = useAuth();

    // Gracefully handle cases where user or permissions are not yet loaded
    const permissions = user?.permissions || {};
    const isSuperAdmin = user?.is_superuser || user?.is_admin_user;

    return (
        <div className="w-64 bg-white border-r">
            <div className="p-4">
                <h2 className="text-xl font-bold">Admin Panel</h2>
            </div>
            <nav className="mt-4">
                <ul>
                    <li>
                        <NavLink
                            to="/adminpanel"
                            end
                            className={({ isActive }) =>
                                `block px-4 py-2 ${isActive ? 'bg-blue-100 text-blue-600' : ''}`
                            }
                        >
                            Home
                        </NavLink>
                    </li>

                    {(permissions.can_manage_users || isSuperAdmin) && (
                        <li>
                            <NavLink
                                to="/adminpanel/users"
                                className={({ isActive }) =>
                                    `block px-4 py-2 ${isActive ? 'bg-blue-100 text-blue-600' : ''}`
                                }
                            >
                                Users
                            </NavLink>
                        </li>
                    )}

                    {(permissions.can_manage_departments || isSuperAdmin) && (
                        <li>
                            <NavLink
                                to="/adminpanel/departments"
                                className={({ isActive }) =>
                                    `block px-4 py-2 ${isActive ? 'bg-blue-100 text-blue-600' : ''}`
                                }
                            >
                                Departments
                            </NavLink>
                        </li>
                    )}

                    {(permissions.can_view_department_dashboard || isSuperAdmin) && (
                        <li>
                            <NavLink
                                to="/adminpanel/dashboards/department"
                                className={({ isActive }) =>
                                    `block px-4 py-2 ${isActive ? 'bg-blue-100 text-blue-600' : ''}`
                                }
                            >
                                Department Dashboard
                            </NavLink>
                        </li>
                    )}

                    {(permissions.can_view_global_dashboard || isSuperAdmin) && (
                        <>
                            <li>
                                <NavLink
                                    to="/adminpanel/dashboards/global"
                                    className={({ isActive }) =>
                                        `block px-4 py-2 ${isActive ? 'bg-blue-100 text-blue-600' : ''}`
                                    }
                                >
                                    Global Dashboard
                                </NavLink>
                            </li>
                            <li>
                                <NavLink
                                    to="/adminpanel/analytics/doctors"
                                    className={({ isActive }) =>
                                        `block px-4 py-2 ${isActive ? 'bg-blue-100 text-blue-600' : ''}`
                                    }
                                >
                                    Doctor Analytics
                                </NavLink>
                            </li>
                        </>
                    )}
                </ul>
            </nav>
        </div>
    );
};

export default AdminSidebar;
