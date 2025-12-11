import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { adminAPI, departmentsAPI } from '../../api';
import { useAuth } from '../../hooks/useAuth';

/**
 * Department Dashboard Page.
 * Shows consult statistics for a specific department.
 */
export default function DepartmentDashboardPage() {
    const { user } = useAuth();
    const isSuperAdmin = user?.is_superuser || user?.is_admin_user;
    
    const [selectedDepartment, setSelectedDepartment] = useState('');
    const [consultType, setConsultType] = useState('all');
    const [filters, setFilters] = useState({
        status: '',
        urgency: '',
        overdue: '',
    });

    // Fetch departments for selector (only for superadmins)
    const { data: departmentsData } = useQuery({
        queryKey: ['departments'],
        queryFn: () => departmentsAPI.getDepartments(),
        enabled: isSuperAdmin,
    });

    const departments = departmentsData?.results || departmentsData || [];

    // Fetch dashboard data
    const {
        data: dashboardData,
        isLoading,
        isError,
        error,
    } = useQuery({
        queryKey: ['department-dashboard', selectedDepartment, consultType, filters],
        queryFn: () =>
            adminAPI.getDepartmentDashboard({
                department_id: selectedDepartment || undefined,
                type: consultType,
                ...filters,
            }),
    });

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return '-';
        return new Date(dateStr).toLocaleString();
    };

    const getUrgencyBadge = (urgency) => {
        const classes = {
            EMERGENCY: 'bg-red-100 text-red-800',
            URGENT: 'bg-orange-100 text-orange-800',
            ROUTINE: 'bg-blue-100 text-blue-800',
        };
        return classes[urgency] || 'bg-gray-100 text-gray-800';
    };

    const getStatusBadge = (status) => {
        const classes = {
            PENDING: 'bg-yellow-100 text-yellow-800',
            ACKNOWLEDGED: 'bg-blue-100 text-blue-800',
            IN_PROGRESS: 'bg-purple-100 text-purple-800',
            COMPLETED: 'bg-green-100 text-green-800',
            CANCELLED: 'bg-gray-100 text-gray-800',
        };
        return classes[status] || 'bg-gray-100 text-gray-800';
    };

    const renderConsultTable = (consults, title) => (
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
            <div className="px-6 py-4 border-b bg-gray-50">
                <h3 className="text-lg font-medium text-gray-900">{title}</h3>
            </div>
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Patient</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">From/To Dept</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Assigned</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Urgency</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {consults.length === 0 ? (
                            <tr>
                                <td colSpan="7" className="px-4 py-4 text-center text-gray-500">
                                    No consults found
                                </td>
                            </tr>
                        ) : (
                            consults.map((consult) => (
                                <tr key={consult.id} className={consult.is_overdue ? 'bg-red-50' : ''}>
                                    <td className="px-4 py-3">
                                        <div className="text-sm font-medium text-gray-900">{consult.patient.name}</div>
                                        <div className="text-xs text-gray-500">MRN: {consult.patient.mrn}</div>
                                        {consult.patient.location && (
                                            <div className="text-xs text-gray-500">{consult.patient.location}</div>
                                        )}
                                    </td>
                                    <td className="px-4 py-3 text-sm text-gray-500">
                                        {title.includes('Received') ? (
                                            <span>From: {consult.requesting_department.name}</span>
                                        ) : (
                                            <span>To: {consult.target_department.name}</span>
                                        )}
                                    </td>
                                    <td className="px-4 py-3 text-sm text-gray-500">
                                        {consult.assigned_to?.name || '-'}
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded-full ${getUrgencyBadge(consult.urgency)}`}>
                                            {consult.urgency}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 text-xs rounded-full ${getStatusBadge(consult.status)}`}>
                                            {consult.status}
                                        </span>
                                        {consult.is_overdue && (
                                            <span className="ml-2 text-xs text-red-600 font-medium">OVERDUE</span>
                                        )}
                                    </td>
                                    <td className="px-4 py-3 text-sm text-gray-500">
                                        {formatDate(consult.created_at)}
                                    </td>
                                    <td className="px-4 py-3">
                                        <Link
                                            to={`/consults/${consult.id}`}
                                            className="text-blue-600 hover:text-blue-900 text-sm"
                                        >
                                            View
                                        </Link>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );

    if (isLoading) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="text-center text-gray-500">Loading dashboard...</div>
            </div>
        );
    }

    if (isError) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
                    <h1 className="text-lg font-semibold text-red-600 mb-2">
                        Failed to load department dashboard
                    </h1>
                    <p className="text-gray-600 text-sm">
                        {error?.response?.data?.detail ||
                            error?.message ||
                            'Please try again later.'}
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 py-8">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Department Dashboard</h1>
                <p className="text-gray-600">
                    {dashboardData?.department?.name || user?.department_name || 'Your Department'}
                </p>
            </div>

            {/* Department Selector (SuperAdmin only) */}
            {isSuperAdmin && (
                <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Select Department
                    </label>
                    <select
                        value={selectedDepartment}
                        onChange={(e) => setSelectedDepartment(e.target.value)}
                        className="border rounded-md px-3 py-2 w-full md:w-64"
                    >
                        <option value="">My Department</option>
                        {departments.map(dept => (
                            <option key={dept.id} value={dept.id}>{dept.name}</option>
                        ))}
                    </select>
                </div>
            )}

            {/* Summary Cards */}
            {dashboardData?.summary && (
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
                    <div className="bg-white rounded-lg shadow-sm border p-4">
                        <div className="text-sm text-gray-500">Active</div>
                        <div className="text-2xl font-bold text-gray-900">{dashboardData.summary.total_active}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm border p-4">
                        <div className="text-sm text-gray-500">Pending</div>
                        <div className="text-2xl font-bold text-yellow-600">{dashboardData.summary.pending}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm border p-4">
                        <div className="text-sm text-gray-500">Acknowledged</div>
                        <div className="text-2xl font-bold text-blue-600">{dashboardData.summary.acknowledged}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm border p-4">
                        <div className="text-sm text-gray-500">In Progress</div>
                        <div className="text-2xl font-bold text-purple-600">{dashboardData.summary.in_progress}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm border p-4">
                        <div className="text-sm text-gray-500">Completed Today</div>
                        <div className="text-2xl font-bold text-green-600">{dashboardData.summary.completed_today}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm border p-4">
                        <div className="text-sm text-gray-500">Overdue</div>
                        <div className="text-2xl font-bold text-red-600">{dashboardData.summary.overdue}</div>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
                <div className="flex flex-wrap gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">View</label>
                        <select
                            value={consultType}
                            onChange={(e) => setConsultType(e.target.value)}
                            className="border rounded-md px-3 py-2"
                        >
                            <option value="all">All Consults</option>
                            <option value="received">Received Only</option>
                            <option value="sent">Sent Only</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                        <select
                            value={filters.status}
                            onChange={(e) => handleFilterChange('status', e.target.value)}
                            className="border rounded-md px-3 py-2"
                        >
                            <option value="">All Status</option>
                            <option value="PENDING">Pending</option>
                            <option value="ACKNOWLEDGED">Acknowledged</option>
                            <option value="IN_PROGRESS">In Progress</option>
                            <option value="COMPLETED">Completed</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Urgency</label>
                        <select
                            value={filters.urgency}
                            onChange={(e) => handleFilterChange('urgency', e.target.value)}
                            className="border rounded-md px-3 py-2"
                        >
                            <option value="">All Urgency</option>
                            <option value="EMERGENCY">Emergency</option>
                            <option value="URGENT">Urgent</option>
                            <option value="ROUTINE">Routine</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Overdue</label>
                        <select
                            value={filters.overdue}
                            onChange={(e) => handleFilterChange('overdue', e.target.value)}
                            className="border rounded-md px-3 py-2"
                        >
                            <option value="">All</option>
                            <option value="true">Overdue Only</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Consult Tables */}
            <div className="space-y-6">
                {(consultType === 'all' || consultType === 'received') && (
                    renderConsultTable(
                        dashboardData?.received_consults || [],
                        'Received Consults'
                    )
                )}
                
                {(consultType === 'all' || consultType === 'sent') && (
                    renderConsultTable(
                        dashboardData?.sent_consults || [],
                        'Sent Consults'
                    )
                )}
            </div>
        </div>
    );
}
