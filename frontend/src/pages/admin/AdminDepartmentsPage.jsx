import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminAPI } from '../../api';
import DepartmentEditModal from './DepartmentEditModal';

/**
 * Admin Departments List Page.
 * Allows admins to list, filter, and manage departments.
 */
export default function AdminDepartmentsPage() {
    const queryClient = useQueryClient();
    const [selectedDepartment, setSelectedDepartment] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [isCreating, setIsCreating] = useState(false);
    const [viewMode, setViewMode] = useState('flat'); // 'flat' or 'hierarchy'
    
    // Filters
    const [filters, setFilters] = useState({
        department_type: '',
        is_active: '',
        top_level: '',
    });

    // Fetch departments
    const { data: departmentsData, isLoading } = useQuery({
        queryKey: ['admin-departments', filters],
        queryFn: () => adminAPI.getDepartments(filters),
    });

    // Fetch hierarchy view
    const { data: hierarchyData } = useQuery({
        queryKey: ['admin-departments-hierarchy'],
        queryFn: () => adminAPI.getDepartmentHierarchy(),
        enabled: viewMode === 'hierarchy',
    });

    const departments = departmentsData?.results || departmentsData || [];

    // Activate/deactivate mutations
    const activateMutation = useMutation({
        mutationFn: (deptId) => adminAPI.activateDepartment(deptId),
        onSuccess: () => {
            queryClient.invalidateQueries(['admin-departments']);
        },
    });

    const deactivateMutation = useMutation({
        mutationFn: (deptId) => adminAPI.deactivateDepartment(deptId),
        onSuccess: () => {
            queryClient.invalidateQueries(['admin-departments']);
        },
        onError: (err) => {
            alert(err.response?.data?.error || 'Failed to deactivate department');
        },
    });

    const deleteMutation = useMutation({
        mutationFn: (deptId) => adminAPI.deleteDepartment(deptId),
        onSuccess: () => {
            queryClient.invalidateQueries(['admin-departments']);
        },
        onError: (err) => {
            alert(err.response?.data?.error || 'Failed to delete department');
        },
    });

    const handleEditDepartment = (dept) => {
        setSelectedDepartment(dept);
        setIsCreating(false);
        setShowModal(true);
    };

    const handleCreateDepartment = () => {
        setSelectedDepartment(null);
        setIsCreating(true);
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setSelectedDepartment(null);
        setIsCreating(false);
    };

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const handleDelete = (deptId) => {
        if (window.confirm('Are you sure you want to delete this department? This cannot be undone.')) {
            deleteMutation.mutate(deptId);
        }
    };

    const renderDepartmentRow = (dept, level = 0) => (
        <tr key={dept.id} className="hover:bg-gray-50">
            <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center" style={{ marginLeft: `${level * 20}px` }}>
                    {level > 0 && <span className="text-gray-400 mr-2">└</span>}
                    <div>
                        <div className="text-sm font-medium text-gray-900">{dept.name}</div>
                        <div className="text-sm text-gray-500">{dept.code}</div>
                    </div>
                </div>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {dept.department_type || 'CLINICAL'}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {dept.parent_info?.name || '-'}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {dept.head_name || '-'}
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 py-1 text-xs rounded-full ${
                    dept.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                    {dept.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <Link
                    to={`/adminpanel/departments/${dept.id}`}
                    className="text-indigo-600 hover:text-indigo-900 mr-4"
                >
                    View
                </Link>
                <button
                    onClick={() => handleEditDepartment(dept)}
                    className="text-blue-600 hover:text-blue-900 mr-4"
                >
                    Edit
                </button>
                {dept.is_active ? (
                    <button
                        onClick={() => deactivateMutation.mutate(dept.id)}
                        className="text-yellow-600 hover:text-yellow-900 mr-4"
                        disabled={deactivateMutation.isPending}
                    >
                        Deactivate
                    </button>
                ) : (
                    <button
                        onClick={() => activateMutation.mutate(dept.id)}
                        className="text-green-600 hover:text-green-900 mr-4"
                        disabled={activateMutation.isPending}
                    >
                        Activate
                    </button>
                )}
                <button
                    onClick={() => handleDelete(dept.id)}
                    className="text-red-600 hover:text-red-900"
                    disabled={deleteMutation.isPending}
                >
                    Delete
                </button>
            </td>
        </tr>
    );

    const renderHierarchy = (deptList, level = 0) => {
        return deptList.flatMap(dept => [
            renderDepartmentRow(dept, level),
            ...(dept.children ? renderHierarchy(dept.children, level + 1) : [])
        ]);
    };

    return (
        <div className="max-w-7xl mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Departments Management</h1>
                    <p className="text-gray-600">Manage departments and their hierarchy</p>
                </div>
                <button
                    onClick={handleCreateDepartment}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                    + Add Department
                </button>
            </div>

            {/* Filters and View Toggle */}
            <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
                <div className="flex flex-wrap items-end gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Type
                        </label>
                        <select
                            value={filters.department_type}
                            onChange={(e) => handleFilterChange('department_type', e.target.value)}
                            className="border rounded-md px-3 py-2"
                        >
                            <option value="">All Types</option>
                            <option value="CLINICAL">Clinical</option>
                            <option value="ADMINISTRATIVE">Administrative</option>
                            <option value="SUPPORT">Support</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Status
                        </label>
                        <select
                            value={filters.is_active}
                            onChange={(e) => handleFilterChange('is_active', e.target.value)}
                            className="border rounded-md px-3 py-2"
                        >
                            <option value="">All Status</option>
                            <option value="true">Active</option>
                            <option value="false">Inactive</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Level
                        </label>
                        <select
                            value={filters.top_level}
                            onChange={(e) => handleFilterChange('top_level', e.target.value)}
                            className="border rounded-md px-3 py-2"
                        >
                            <option value="">All Levels</option>
                            <option value="true">Top-level only</option>
                        </select>
                    </div>
                    <div className="ml-auto">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            View
                        </label>
                        <div className="flex border rounded-md overflow-hidden">
                            <button
                                onClick={() => setViewMode('flat')}
                                className={`px-4 py-2 ${viewMode === 'flat' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
                            >
                                Flat
                            </button>
                            <button
                                onClick={() => setViewMode('hierarchy')}
                                className={`px-4 py-2 ${viewMode === 'hierarchy' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
                            >
                                Hierarchy
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Departments Table */}
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Department
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Type
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Parent
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                HOD
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
                        {isLoading ? (
                            <tr>
                                <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                                    Loading...
                                </td>
                            </tr>
                        ) : viewMode === 'hierarchy' && hierarchyData ? (
                            renderHierarchy(hierarchyData)
                        ) : departments.length === 0 ? (
                            <tr>
                                <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                                    No departments found
                                </td>
                            </tr>
                        ) : (
                            departments.map((dept) => renderDepartmentRow(dept))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Edit/Create Modal */}
            {showModal && (
                <DepartmentEditModal
                    department={selectedDepartment}
                    isCreating={isCreating}
                    onClose={handleCloseModal}
                    departments={departments}
                />
            )}
        </div>
    );
}
