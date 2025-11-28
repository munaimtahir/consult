import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { adminAPI } from '../../api';

/**
 * Modal for editing/creating users.
 * Has tabs for Profile, Department & Role, and Permissions.
 */
export default function UserEditModal({ user, isCreating, onClose, canManagePermissions, departments }) {
    const queryClient = useQueryClient();
    const [activeTab, setActiveTab] = useState('profile');
    const [formData, setFormData] = useState(() => {
        if (user) {
            return {
                email: user.email || '',
                password: '',
                first_name: user.first_name || '',
                last_name: user.last_name || '',
                phone_number: user.phone_number || '',
                is_active: user.is_active ?? true,
                department: user.department || '',
                designation: user.designation || '',
                role: user.role || 'DOCTOR',
                is_staff: user.is_staff || false,
                can_manage_users: user.can_manage_users || false,
                can_manage_departments: user.can_manage_departments || false,
                can_view_department_dashboard: user.can_view_department_dashboard || false,
                can_view_global_dashboard: user.can_view_global_dashboard || false,
                can_manage_consults_globally: user.can_manage_consults_globally || false,
                can_manage_permissions: user.can_manage_permissions || false,
            };
        }
        return {
            email: '',
            password: '',
            first_name: '',
            last_name: '',
            phone_number: '',
            is_active: true,
            department: '',
            designation: '',
            role: 'DOCTOR',
            is_staff: false,
            can_manage_users: false,
            can_manage_departments: false,
            can_view_department_dashboard: false,
            can_view_global_dashboard: false,
            can_manage_consults_globally: false,
            can_manage_permissions: false,
        };
    });
    const [error, setError] = useState('');

    const createMutation = useMutation({
        mutationFn: (data) => adminAPI.createUser(data),
        onSuccess: () => {
            queryClient.invalidateQueries(['admin-users']);
            onClose();
        },
        onError: (err) => {
            setError(err.response?.data?.email?.[0] || err.response?.data?.detail || 'Failed to create user');
        },
    });

    const updateMutation = useMutation({
        mutationFn: (data) => adminAPI.updateUser(user.id, data),
        onSuccess: () => {
            queryClient.invalidateQueries(['admin-users']);
            onClose();
        },
        onError: (err) => {
            setError(err.response?.data?.detail || 'Failed to update user');
        },
    });

    const permissionsMutation = useMutation({
        mutationFn: (permissions) => adminAPI.updateUserPermissions(user.id, permissions),
        onSuccess: () => {
            queryClient.invalidateQueries(['admin-users']);
        },
        onError: (err) => {
            setError(err.response?.data?.detail || 'Failed to update permissions');
        },
    });

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value,
        }));
    };

    const handleProfileSave = () => {
        setError('');
        const profileData = {
            first_name: formData.first_name,
            last_name: formData.last_name,
            phone_number: formData.phone_number,
            is_active: formData.is_active,
        };

        if (isCreating) {
            createMutation.mutate({
                ...profileData,
                email: formData.email,
                password: formData.password || undefined,
                department: formData.department || null,
                designation: formData.designation || undefined,
                role: formData.role,
            });
        } else {
            updateMutation.mutate(profileData);
        }
    };

    const handleDepartmentSave = () => {
        setError('');
        updateMutation.mutate({
            department: formData.department || null,
            designation: formData.designation || null,
            role: formData.role,
            is_staff: formData.is_staff,
        });
    };

    const handlePermissionsSave = () => {
        setError('');
        permissionsMutation.mutate({
            can_manage_users: formData.can_manage_users,
            can_manage_departments: formData.can_manage_departments,
            can_view_department_dashboard: formData.can_view_department_dashboard,
            can_view_global_dashboard: formData.can_view_global_dashboard,
            can_manage_consults_globally: formData.can_manage_consults_globally,
            can_manage_permissions: formData.can_manage_permissions,
        });
    };

    const designationOptions = [
        { value: '', label: 'Select Designation' },
        { value: 'RESIDENT_1', label: 'Resident 1' },
        { value: 'RESIDENT_2', label: 'Resident 2' },
        { value: 'RESIDENT_3', label: 'Resident 3' },
        { value: 'RESIDENT_4', label: 'Resident 4' },
        { value: 'RESIDENT_5', label: 'Resident 5' },
        { value: 'SENIOR_REGISTRAR', label: 'Senior Registrar' },
        { value: 'ASSISTANT_PROFESSOR', label: 'Assistant Professor' },
        { value: 'PROFESSOR', label: 'Professor' },
        { value: 'HOD', label: 'Head of Department' },
    ];

    const isLoading = createMutation.isPending || updateMutation.isPending || permissionsMutation.isPending;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
                {/* Header */}
                <div className="px-6 py-4 border-b flex justify-between items-center">
                    <h2 className="text-xl font-semibold text-gray-900">
                        {isCreating ? 'Create New User' : `Edit User: ${user?.first_name} ${user?.last_name}`}
                    </h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                        ✕
                    </button>
                </div>

                {/* Tabs */}
                <div className="border-b">
                    <div className="flex">
                        <button
                            onClick={() => setActiveTab('profile')}
                            className={`px-6 py-3 text-sm font-medium ${
                                activeTab === 'profile'
                                    ? 'border-b-2 border-blue-500 text-blue-600'
                                    : 'text-gray-500 hover:text-gray-700'
                            }`}
                        >
                            Profile
                        </button>
                        {!isCreating && (
                            <button
                                onClick={() => setActiveTab('department')}
                                className={`px-6 py-3 text-sm font-medium ${
                                    activeTab === 'department'
                                        ? 'border-b-2 border-blue-500 text-blue-600'
                                        : 'text-gray-500 hover:text-gray-700'
                                }`}
                            >
                                Department & Role
                            </button>
                        )}
                        {!isCreating && canManagePermissions && (
                            <button
                                onClick={() => setActiveTab('permissions')}
                                className={`px-6 py-3 text-sm font-medium ${
                                    activeTab === 'permissions'
                                        ? 'border-b-2 border-blue-500 text-blue-600'
                                        : 'text-gray-500 hover:text-gray-700'
                                }`}
                            >
                                Admin Permissions
                            </button>
                        )}
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto max-h-[60vh]">
                    {error && (
                        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
                            {error}
                        </div>
                    )}

                    {/* Profile Tab */}
                    {activeTab === 'profile' && (
                        <div className="space-y-4">
                            {isCreating && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Email *
                                    </label>
                                    <input
                                        type="email"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleInputChange}
                                        className="w-full border rounded-md px-3 py-2"
                                        placeholder="user@pmc.edu.pk"
                                    />
                                </div>
                            )}
                            {isCreating && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Password
                                    </label>
                                    <input
                                        type="password"
                                        name="password"
                                        value={formData.password}
                                        onChange={handleInputChange}
                                        className="w-full border rounded-md px-3 py-2"
                                        placeholder="Leave blank for no password"
                                    />
                                </div>
                            )}
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        First Name *
                                    </label>
                                    <input
                                        type="text"
                                        name="first_name"
                                        value={formData.first_name}
                                        onChange={handleInputChange}
                                        className="w-full border rounded-md px-3 py-2"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Last Name *
                                    </label>
                                    <input
                                        type="text"
                                        name="last_name"
                                        value={formData.last_name}
                                        onChange={handleInputChange}
                                        className="w-full border rounded-md px-3 py-2"
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Phone Number
                                </label>
                                <input
                                    type="tel"
                                    name="phone_number"
                                    value={formData.phone_number}
                                    onChange={handleInputChange}
                                    className="w-full border rounded-md px-3 py-2"
                                />
                            </div>
                            {isCreating && (
                                <>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Department
                                        </label>
                                        <select
                                            name="department"
                                            value={formData.department}
                                            onChange={handleInputChange}
                                            className="w-full border rounded-md px-3 py-2"
                                        >
                                            <option value="">Select Department</option>
                                            {departments.map(dept => (
                                                <option key={dept.id} value={dept.id}>{dept.name}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Designation
                                        </label>
                                        <select
                                            name="designation"
                                            value={formData.designation}
                                            onChange={handleInputChange}
                                            className="w-full border rounded-md px-3 py-2"
                                        >
                                            {designationOptions.map(opt => (
                                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                                            ))}
                                        </select>
                                    </div>
                                </>
                            )}
                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    name="is_active"
                                    checked={formData.is_active}
                                    onChange={handleInputChange}
                                    className="mr-2"
                                />
                                <label className="text-sm text-gray-700">Active</label>
                            </div>
                            <button
                                onClick={handleProfileSave}
                                disabled={isLoading}
                                className="w-full py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                            >
                                {isLoading ? 'Saving...' : (isCreating ? 'Create User' : 'Save Profile')}
                            </button>
                        </div>
                    )}

                    {/* Department & Role Tab */}
                    {activeTab === 'department' && !isCreating && (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Department
                                </label>
                                <select
                                    name="department"
                                    value={formData.department}
                                    onChange={handleInputChange}
                                    className="w-full border rounded-md px-3 py-2"
                                >
                                    <option value="">No Department</option>
                                    {departments.map(dept => (
                                        <option key={dept.id} value={dept.id}>{dept.name}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Designation
                                </label>
                                <select
                                    name="designation"
                                    value={formData.designation}
                                    onChange={handleInputChange}
                                    className="w-full border rounded-md px-3 py-2"
                                >
                                    {designationOptions.map(opt => (
                                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Role
                                </label>
                                <select
                                    name="role"
                                    value={formData.role}
                                    onChange={handleInputChange}
                                    className="w-full border rounded-md px-3 py-2"
                                >
                                    <option value="DOCTOR">Doctor</option>
                                    <option value="DEPARTMENT_USER">Department User</option>
                                    <option value="HOD">Head of Department</option>
                                    <option value="ADMIN">Administrator</option>
                                </select>
                            </div>
                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    name="is_staff"
                                    checked={formData.is_staff}
                                    onChange={handleInputChange}
                                    className="mr-2"
                                />
                                <label className="text-sm text-gray-700">Staff Status (can access Django admin)</label>
                            </div>
                            <button
                                onClick={handleDepartmentSave}
                                disabled={isLoading}
                                className="w-full py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                            >
                                {isLoading ? 'Saving...' : 'Save Department & Role'}
                            </button>
                        </div>
                    )}

                    {/* Permissions Tab */}
                    {activeTab === 'permissions' && !isCreating && canManagePermissions && (
                        <div className="space-y-4">
                            <p className="text-sm text-gray-600 mb-4">
                                Configure what admin features this user can access:
                            </p>
                            <div className="space-y-3">
                                <div className="flex items-center">
                                    <input
                                        type="checkbox"
                                        name="can_manage_users"
                                        checked={formData.can_manage_users}
                                        onChange={handleInputChange}
                                        className="mr-3"
                                    />
                                    <div>
                                        <div className="text-sm font-medium text-gray-700">Can Manage Users</div>
                                        <div className="text-xs text-gray-500">Create, edit, and manage system users</div>
                                    </div>
                                </div>
                                <div className="flex items-center">
                                    <input
                                        type="checkbox"
                                        name="can_manage_departments"
                                        checked={formData.can_manage_departments}
                                        onChange={handleInputChange}
                                        className="mr-3"
                                    />
                                    <div>
                                        <div className="text-sm font-medium text-gray-700">Can Manage Departments</div>
                                        <div className="text-xs text-gray-500">Create, edit, and manage departments</div>
                                    </div>
                                </div>
                                <div className="flex items-center">
                                    <input
                                        type="checkbox"
                                        name="can_view_department_dashboard"
                                        checked={formData.can_view_department_dashboard}
                                        onChange={handleInputChange}
                                        className="mr-3"
                                    />
                                    <div>
                                        <div className="text-sm font-medium text-gray-700">Can View Department Dashboard</div>
                                        <div className="text-xs text-gray-500">Access department-level statistics and consult data</div>
                                    </div>
                                </div>
                                <div className="flex items-center">
                                    <input
                                        type="checkbox"
                                        name="can_view_global_dashboard"
                                        checked={formData.can_view_global_dashboard}
                                        onChange={handleInputChange}
                                        className="mr-3"
                                    />
                                    <div>
                                        <div className="text-sm font-medium text-gray-700">Can View Global Dashboard</div>
                                        <div className="text-xs text-gray-500">Access system-wide statistics across all departments</div>
                                    </div>
                                </div>
                                <div className="flex items-center">
                                    <input
                                        type="checkbox"
                                        name="can_manage_consults_globally"
                                        checked={formData.can_manage_consults_globally}
                                        onChange={handleInputChange}
                                        className="mr-3"
                                    />
                                    <div>
                                        <div className="text-sm font-medium text-gray-700">Can Manage Consults Globally</div>
                                        <div className="text-xs text-gray-500">Reassign and force-close consults across all departments</div>
                                    </div>
                                </div>
                                <div className="flex items-center">
                                    <input
                                        type="checkbox"
                                        name="can_manage_permissions"
                                        checked={formData.can_manage_permissions}
                                        onChange={handleInputChange}
                                        className="mr-3"
                                    />
                                    <div>
                                        <div className="text-sm font-medium text-gray-700">Can Manage Permissions</div>
                                        <div className="text-xs text-gray-500">Modify admin permissions for other users (SuperAdmin only)</div>
                                    </div>
                                </div>
                            </div>
                            <button
                                onClick={handlePermissionsSave}
                                disabled={isLoading}
                                className="w-full py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                            >
                                {isLoading ? 'Saving...' : 'Save Permissions'}
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
