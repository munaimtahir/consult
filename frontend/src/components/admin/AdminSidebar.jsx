import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const AdminSidebar = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [searchTerm, setSearchTerm] = useState('');
    const [openMenus, setOpenMenus] = useState({
        dashboard: false,
        students: false,
        faculty: false,
        attendance: false,
        results: false,
        finance: false,
    });

    const permissions = user?.permissions || {};
    const isSuperAdmin = user?.is_superuser || user?.is_admin_user;

    const toggleMenu = (menu) => {
        setOpenMenus(prev => ({
            ...prev,
            [menu]: !prev[menu]
        }));
    };

    const handleSearch = (e) => {
        e.preventDefault();
        if (searchTerm.trim()) {
            // Navigate to search results page or filter current page
            navigate(`/adminpanel/search?q=${encodeURIComponent(searchTerm)}`);
        }
    };

    const menuItems = [
        {
            id: 'dashboard',
            label: '📊 Dashboard',
            icon: '📊',
            submenu: [
                { label: 'Master Dashboard', path: '/adminpanel/dashboard/master' },
                { label: 'Analytics', path: '/adminpanel/dashboard/analytics' },
            ]
        },
        {
            id: 'students',
            label: '👥 Students',
            icon: '👥',
            submenu: [
                { label: 'Programs', path: '/adminpanel/students/programs' },
                { label: 'Class/Batch', path: '/adminpanel/students/batches' },
                { label: 'Academic Period', path: '/adminpanel/students/academic-periods' },
            ]
        },
        {
            id: 'faculty',
            label: '👨‍🏫 Faculty',
            icon: '👨‍🏫',
            submenu: [
                { label: 'Departments', path: '/adminpanel/faculty/departments' },
            ]
        },
        {
            id: 'attendance',
            label: '✅ Overview',
            icon: '✅',
            submenu: [
                { label: 'Overview', path: '/adminpanel/attendance/overview' },
                { label: 'Attendance Input', path: '/adminpanel/attendance/input' },
                { label: 'Attendance/Eligibility Report', path: '/adminpanel/attendance/report' },
            ]
        },
        {
            id: 'results',
            label: '📋 Results',
            icon: '📋',
            submenu: [
                { label: 'Overview', path: '/adminpanel/results/overview' },
                { label: 'Batch wise result', path: '/adminpanel/results/batch-wise' },
                { label: 'Academic period results', path: '/adminpanel/results/academic-period' },
                { label: 'Grade', path: '/adminpanel/results/grade' },
                { label: 'Academic period wise assessment report', path: '/adminpanel/results/assessment-report' },
            ]
        },
        {
            id: 'finance',
            label: '💰 Finance',
            icon: '💰',
            submenu: [
                { label: 'Finance Dashboard', path: '/adminpanel/finance/dashboard' },
                { label: 'Fee plans/Voucher Generation', path: '/adminpanel/finance/fee-plans' },
                { label: 'Voucher Lists', path: '/adminpanel/finance/vouchers' },
                { label: 'Payment/Collection Report', path: '/adminpanel/finance/payment-report' },
            ]
        },
        {
            id: 'admin',
            label: '⚙️ Admin',
            icon: '⚙️',
            path: '/adminpanel',
            noSubmenu: true
        },
    ];

    return (
        <aside className="fixed lg:sticky top-0 left-0 h-screen bg-[#0F172A] text-white z-50 transition-all duration-150 ease-in-out w-64 flex flex-col">
            {/* Search Bar */}
            <div className="p-4 border-b border-gray-700">
                <form onSubmit={handleSearch} className="relative">
                    <input
                        type="text"
                        placeholder="Search..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full px-4 py-2 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <button
                        type="submit"
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                    >
                        🔍
                    </button>
                </form>
            </div>

            {/* Navigation Menu */}
            <nav className="flex-1 overflow-y-auto py-4">
                <ul className="space-y-1 px-2">
                    {menuItems.map((item) => (
                        <li key={item.id}>
                            {item.noSubmenu ? (
                                <NavLink
                                    to={item.path}
                                    end
                                    className={({ isActive }) =>
                                        `flex items-center px-4 py-3 rounded-lg transition-all duration-150 ${
                                            isActive
                                                ? 'bg-blue-600 text-white'
                                                : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                                        }`
                                    }
                                >
                                    <span className="text-xl mr-3">{item.icon}</span>
                                    <span className="font-medium">{item.label.replace(/^[^\s]+\s/, '')}</span>
                                </NavLink>
                            ) : (
                                <>
                                    <button
                                        onClick={() => toggleMenu(item.id)}
                                        className={`w-full flex items-center justify-between px-4 py-3 rounded-lg transition-all duration-150 ${
                                            openMenus[item.id]
                                                ? 'bg-gray-800 text-white'
                                                : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                                        }`}
                                    >
                                        <div className="flex items-center">
                                            <span className="text-xl mr-3">{item.icon}</span>
                                            <span className="font-medium">{item.label.replace(/^[^\s]+\s/, '')}</span>
                                        </div>
                                        <span className={`transform transition-transform ${openMenus[item.id] ? 'rotate-180' : ''}`}>
                                            ▼
                                        </span>
                                    </button>
                                    {openMenus[item.id] && (
                                        <ul className="ml-4 mt-1 space-y-1">
                                            {item.submenu.map((subItem) => (
                                                <li key={subItem.path}>
                                                    <NavLink
                                                        to={subItem.path}
                                                        className={({ isActive }) =>
                                                            `block px-4 py-2 rounded-lg transition-all duration-150 ${
                                                                isActive
                                                                    ? 'bg-blue-600 text-white'
                                                                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                                                            }`
                                                        }
                                                    >
                                                        {subItem.label}
                                                    </NavLink>
                                                </li>
                                            ))}
                                        </ul>
                                    )}
                                </>
                            )}
                        </li>
                    ))}
                </ul>
            </nav>

            {/* User Info */}
            <div className="p-4 border-t border-gray-700">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                        {user?.first_name?.[0] || user?.email?.[0] || 'U'}
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">
                            {user?.first_name} {user?.last_name}
                        </p>
                        <p className="text-xs text-gray-400 truncate">{user?.role || 'User'}</p>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default AdminSidebar;
