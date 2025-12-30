import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminAPI, departmentsAPI } from '../../api';
import { useAuth } from '../../hooks/useAuth';
import UserEditModal from './UserEditModal';

/**
 * Admin Users List Page.
 * Allows admins to list, filter, and manage users.
 */
export default function AdminUsersPage() {
    const { user: currentUser } = useAuth();
    const queryClient = useQueryClient();
    const [selectedUser, setSelectedUser] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [isCreating, setIsCreating] = useState(false);
    
    // Filters
    const [filters, setFilters] = useState({
        department: '',
        role: '',
        is_active: '',
        search: '',
    });

    // Fetch users
    const {
        data: usersData,
        isLoading: usersLoading,
        isError: isUsersError,
        error: usersError,
    } = useQuery({
        queryKey: ['admin-users', filters],
        queryFn: () => adminAPI.getUsers(filters),
    });

    // Fetch departments for filter
    const {
        data: departmentsData,
        isError: isDepartmentsError,
        error: departmentsError,
    } = useQuery({
        queryKey: ['departments'],
        queryFn: () => departmentsAPI.getDepartments(),
    });

    const users = usersData?.results || usersData || [];
    const departments = departmentsData?.results || departmentsData || [];

    // Activate/deactivate mutations
    const activateMutation = useMutation({
        mutationFn: (userId) => adminAPI.activateUser(userId),
        onSuccess: () => {
            queryClient.invalidateQueries(['admin-users']);
        },
    });

    const deactivateMutation = useMutation({
        mutationFn: (userId) => adminAPI.deactivateUser(userId),
        onSuccess: () => {
            queryClient.invalidateQueries(['admin-users']);
        },
    });

    const handleEditUser = (user) => {
        setSelectedUser(user);
        setIsCreating(false);
        setShowModal(true);
    };

    const handleCreateUser = () => {
        setSelectedUser(null);
        setIsCreating(true);
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setSelectedUser(null);
        setIsCreating(false);
    };

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const canManagePermissions = currentUser?.is_superuser || 
        currentUser?.is_admin_user || 
        currentUser?.permissions?.can_manage_permissions;

    return (
        <div className="max-w-7xl mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Users Management</h1>
                    <p className="text-gray-600">Manage system users and their permissions</p>
                </div>
                <button
                    onClick={handleCreateUser}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                    + Add User
                </button>
            </div>

            {/* Filters */}
            <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
                {isDepartmentsError && (
                    <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md text-sm">
                        Failed to load departments for filtering:{' '}
                        {departmentsError?.response?.data?.detail ||
                            departmentsError?.message ||
                            'Please try again later.'}
                    </div>
                )}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Search
                        </label>
                        <input
                            type="text"
                            placeholder="Name or email..."
                            value={filters.search}
                            onChange={(e) => handleFilterChange('search', e.target.value)}
                            className="w-full border rounded-md px-3 py-2"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Department
                        </label>
                        <select
                            value={filters.department}
                            onChange={(e) => handleFilterChange('department', e.target.value)}
                            className="w-full border rounded-md px-3 py-2"
                        >
                            <option value="">All Departments</option>
                            {departments.map(dept => (
                                <option key={dept.id} value={dept.id}>{dept.name}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Role
                        </label>
                        <select
                            value={filters.role}
                            onChange={(e) => handleFilterChange('role', e.target.value)}
                            className="w-full border rounded-md px-3 py-2"
                        >
                            <option value="">All Roles</option>
                            <option value="DOCTOR">Doctor</option>
                            <option value="DEPARTMENT_USER">Department User</option>
                            <option value="HOD">Head of Department</option>
                            <option value="ADMIN">Administrator</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Status
                        </label>
                        <select
                            value={filters.is_active}
                            onChange={(e) => handleFilterChange('is_active', e.target.value)}
                            className="w-full border rounded-md px-3 py-2"
                        >
                            <option value="">All Status</option>
                            <option value="true">Active</option>
                            <option value="false">Inactive</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Users Table */}
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                User
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Department
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Role
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Status
                            </th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {isUsersError ? (
                            <tr>
                                <td colSpan="5" className="px-6 py-4 text-center text-red-600">
                                    Failed to load users:{' '}
                                    {usersError?.response?.data?.detail ||
                                        usersError?.message ||
                                        'Please try again later.'}
                                </td>
                            </tr>
                        ) : usersLoading ? (
                            <tr>
                                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                                    Loading...
                                </td>
                            </tr>
                        ) : users.length === 0 ? (
                            <tr>
                                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                                    No users found
                                </td>
                            </tr>
                        ) : (
                            users.map((user) => (
                                <tr key={user.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <div>
                                                <div className="text-sm font-medium text-gray-900">
                                                    {user.first_name} {user.last_name}
                                                </div>
                                                <div className="text-sm text-gray-500">
                                                    {user.email}
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {user.department_name || '-'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 py-1 text-xs rounded-full ${
                                            user.role === 'ADMIN' ? 'bg-purple-100 text-purple-800' :
                                            user.role === 'HOD' ? 'bg-blue-100 text-blue-800' :
                                            user.role === 'DEPARTMENT_USER' ? 'bg-green-100 text-green-800' :
                                            'bg-gray-100 text-gray-800'
                                        }`}>
                                            {user.role}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 py-1 text-xs rounded-full ${
                                            user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                        }`}>
                                            {user.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <button
                                            onClick={() => handleEditUser(user)}
                                            className="text-blue-600 hover:text-blue-900 mr-4"
                                        >
                                            Edit
                                        </button>
                                        {user.id !== currentUser?.id && (
                                            user.is_active ? (
                                                <button
                                                    onClick={() => deactivateMutation.mutate(user.id)}
                                                    className="text-red-600 hover:text-red-900"
                                                    disabled={deactivateMutation.isPending}
                                                >
                                                    Deactivate
                                                </button>
                                            ) : (
                                                <button
                                                    onClick={() => activateMutation.mutate(user.id)}
                                                    className="text-green-600 hover:text-green-900"
                                                    disabled={activateMutation.isPending}
                                                >
                                                    Activate
                                                </button>
                                            )
                                        )}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Edit/Create Modal */}
            {showModal && (
                <UserEditModal
                    user={selectedUser}
                    isCreating={isCreating}
                    onClose={handleCloseModal}
                    canManagePermissions={canManagePermissions}
                    departments={departments}
                />
            )}
        </div>
    );
}
