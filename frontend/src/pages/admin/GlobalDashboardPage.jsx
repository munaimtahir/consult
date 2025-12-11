import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { adminAPI, departmentsAPI } from '../../api';
import { useAuth } from '../../hooks/useAuth';

/**
 * Global Dashboard Page.
 * Shows system-wide consult statistics across all departments.
 */
export default function GlobalDashboardPage() {
    const { user } = useAuth();
    const queryClient = useQueryClient();
    const canManageConsults = user?.is_superuser || user?.permissions?.can_manage_consults_globally;
    
    const [filters, setFilters] = useState({
        requesting_department: '',
        target_department: '',
        status: '',
        urgency: '',
        overdue: '',
    });
    const [activeTab, setActiveTab] = useState('consults');
    const [selectedConsult, setSelectedConsult] = useState(null);
    const [reassignModalOpen, setReassignModalOpen] = useState(false);
    const [forceCloseModalOpen, setForceCloseModalOpen] = useState(false);

    // Fetch departments for filters
    const { data: departmentsData } = useQuery({
        queryKey: ['departments'],
        queryFn: () => departmentsAPI.getDepartments(),
    });

    const departments = departmentsData?.results || departmentsData || [];

    // Fetch global dashboard data
    const {
        data: dashboardData,
        isLoading,
        isError,
        error,
    } = useQuery({
        queryKey: ['global-dashboard', filters],
        queryFn: () => adminAPI.getGlobalDashboard(filters),
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

    const formatMinutes = (minutes) => {
        if (minutes === null || minutes === undefined) return '-';
        if (minutes < 60) return `${Math.round(minutes)} min`;
        const hours = Math.floor(minutes / 60);
        const mins = Math.round(minutes % 60);
        return `${hours}h ${mins}m`;
    };

    if (isLoading) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="text-center text-gray-500">Loading global dashboard...</div>
            </div>
        );
    }

    if (isError) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
                    <h1 className="text-lg font-semibold text-red-600 mb-2">
                        Failed to load global dashboard
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
                <h1 className="text-2xl font-bold text-gray-900">Global Dashboard</h1>
                <p className="text-gray-600">System-wide consult statistics and analytics</p>
            </div>

            {/* Global KPIs */}
            {dashboardData?.global_kpis && (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
                    <div className="bg-white rounded-lg shadow-sm border p-4">
                        <div className="text-sm text-gray-500">Total Open</div>
                        <div className="text-2xl font-bold text-gray-900">{dashboardData.global_kpis.total_open}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm border p-4">
                        <div className="text-sm text-gray-500">Today</div>
                        <div className="text-2xl font-bold text-blue-600">{dashboardData.global_kpis.total_today}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm border p-4">
                        <div className="text-sm text-gray-500">Pending</div>
                        <div className="text-2xl font-bold text-yellow-600">{dashboardData.global_kpis.pending_count}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm border p-4">
                        <div className="text-sm text-gray-500">In Progress</div>
                        <div className="text-2xl font-bold text-purple-600">{dashboardData.global_kpis.in_progress_count}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm border p-4">
                        <div className="text-sm text-gray-500">Completed Today</div>
                        <div className="text-2xl font-bold text-green-600">{dashboardData.global_kpis.completed_today}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm border p-4">
                        <div className="text-sm text-gray-500">Overdue</div>
                        <div className="text-2xl font-bold text-red-600">{dashboardData.global_kpis.overdue_count}</div>
                    </div>
                </div>
            )}

            {/* Tabs */}
            <div className="border-b mb-6">
                <div className="flex space-x-8">
                    <button
                        onClick={() => setActiveTab('consults')}
                        className={`py-3 text-sm font-medium border-b-2 ${
                            activeTab === 'consults'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                        }`}
                    >
                        All Consults
                    </button>
                    <button
                        onClick={() => setActiveTab('departments')}
                        className={`py-3 text-sm font-medium border-b-2 ${
                            activeTab === 'departments'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                        }`}
                    >
                        Department Summary
                    </button>
                </div>
            </div>

            {/* Consults Tab */}
            {activeTab === 'consults' && (
                <>
                    {/* Filters */}
                    <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
                        <div className="flex flex-wrap gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Requesting Dept</label>
                                <select
                                    value={filters.requesting_department}
                                    onChange={(e) => handleFilterChange('requesting_department', e.target.value)}
                                    className="border rounded-md px-3 py-2"
                                >
                                    <option value="">All</option>
                                    {departments.map(dept => (
                                        <option key={dept.id} value={dept.id}>{dept.name}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Target Dept</label>
                                <select
                                    value={filters.target_department}
                                    onChange={(e) => handleFilterChange('target_department', e.target.value)}
                                    className="border rounded-md px-3 py-2"
                                >
                                    <option value="">All</option>
                                    {departments.map(dept => (
                                        <option key={dept.id} value={dept.id}>{dept.name}</option>
                                    ))}
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
                                    <option value="CANCELLED">Cancelled</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Urgency</label>
                                <select
                                    value={filters.urgency}
                                    onChange={(e) => handleFilterChange('urgency', e.target.value)}
                                    className="border rounded-md px-3 py-2"
                                >
                                    <option value="">All</option>
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

                    {/* Consults Table */}
                    <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Patient</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">From</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">To</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Assigned</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Urgency</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {(dashboardData?.consults || []).length === 0 ? (
                                        <tr>
                                            <td colSpan="8" className="px-4 py-4 text-center text-gray-500">
                                                No consults found
                                            </td>
                                        </tr>
                                    ) : (
                                        (dashboardData?.consults || []).map((consult) => (
                                            <tr key={consult.id} className={consult.is_overdue ? 'bg-red-50' : ''}>
                                                <td className="px-4 py-3">
                                                    <div className="text-sm font-medium text-gray-900">{consult.patient.name}</div>
                                                    <div className="text-xs text-gray-500">MRN: {consult.patient.mrn}</div>
                                                </td>
                                                <td className="px-4 py-3 text-sm text-gray-500">
                                                    {consult.requesting_department.name}
                                                </td>
                                                <td className="px-4 py-3 text-sm text-gray-500">
                                                    {consult.target_department.name}
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
                                                        <span className="ml-1 text-xs text-red-600 font-medium">!</span>
                                                    )}
                                                </td>
                                                <td className="px-4 py-3 text-sm text-gray-500">
                                                    {formatDate(consult.created_at)}
                                                </td>
                                                <td className="px-4 py-3">
                                                    <Link
                                                        to={`/consults/${consult.id}`}
                                                        className="text-blue-600 hover:text-blue-900 text-sm mr-2"
                                                    >
                                                        View
                                                    </Link>
                                                    {canManageConsults && !['COMPLETED', 'CANCELLED'].includes(consult.status) && (
                                                        <>
                                                            <button
                                                                onClick={() => {
                                                                    setSelectedConsult(consult);
                                                                    setReassignModalOpen(true);
                                                                }}
                                                                className="text-purple-600 hover:text-purple-900 text-sm mr-2"
                                                            >
                                                                Reassign
                                                            </button>
                                                            <button
                                                                onClick={() => {
                                                                    setSelectedConsult(consult);
                                                                    setForceCloseModalOpen(true);
                                                                }}
                                                                className="text-red-600 hover:text-red-900 text-sm"
                                                            >
                                                                Close
                                                            </button>
                                                        </>
                                                    )}
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}

            {/* Department Summary Tab */}
            {activeTab === 'departments' && (
                <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Department</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Open Received</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Open Sent</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Overdue</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Ack Time</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Completion</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {(dashboardData?.department_stats || []).map((stat) => (
                                    <tr key={stat.department_id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 text-sm font-medium text-gray-900">
                                            {stat.department_name}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-500">
                                            {stat.open_received_count}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-500">
                                            {stat.open_sent_count}
                                        </td>
                                        <td className="px-6 py-4 text-sm">
                                            <span className={stat.overdue_count > 0 ? 'text-red-600 font-medium' : 'text-gray-500'}>
                                                {stat.overdue_count}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-500">
                                            {formatMinutes(stat.average_ack_time_minutes)}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-500">
                                            {formatMinutes(stat.average_completion_time_minutes)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Reassign Modal */}
            {reassignModalOpen && selectedConsult && (
                <ReassignModal
                    consult={selectedConsult}
                    departments={departments}
                    onClose={() => {
                        setReassignModalOpen(false);
                        setSelectedConsult(null);
                    }}
                    onSuccess={() => {
                        queryClient.invalidateQueries(['global-dashboard']);
                        setReassignModalOpen(false);
                        setSelectedConsult(null);
                    }}
                />
            )}

            {/* Force Close Modal */}
            {forceCloseModalOpen && selectedConsult && (
                <ForceCloseModal
                    consult={selectedConsult}
                    onClose={() => {
                        setForceCloseModalOpen(false);
                        setSelectedConsult(null);
                    }}
                    onSuccess={() => {
                        queryClient.invalidateQueries(['global-dashboard']);
                        setForceCloseModalOpen(false);
                        setSelectedConsult(null);
                    }}
                />
            )}
        </div>
    );
}

function ReassignModal({ consult, departments, onClose, onSuccess }) {
    const [targetDepartment, setTargetDepartment] = useState(consult.target_department.id);
    const [assignedTo, setAssignedTo] = useState(consult.assigned_to?.id || '');
    const [error, setError] = useState('');

    // Fetch users for the target department
    const { data: usersData } = useQuery({
        queryKey: ['admin-department-users', targetDepartment],
        queryFn: () => adminAPI.getDepartmentUsers(targetDepartment),
        enabled: !!targetDepartment,
    });

    const departmentUsers = usersData || [];

    const reassignMutation = useMutation({
        mutationFn: () => adminAPI.reassignConsult(consult.id, {
            target_department: targetDepartment !== consult.target_department.id ? targetDepartment : undefined,
            assigned_to: assignedTo || undefined,
        }),
        onSuccess: () => {
            onSuccess();
        },
        onError: (err) => {
            setError(err.response?.data?.error || 'Failed to reassign consult');
        },
    });

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
                <h3 className="text-lg font-semibold mb-4">Reassign Consult</h3>
                
                {error && (
                    <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm">{error}</div>
                )}

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Target Department</label>
                        <select
                            value={targetDepartment}
                            onChange={(e) => {
                                setTargetDepartment(e.target.value);
                                setAssignedTo('');
                            }}
                            className="w-full border rounded-md px-3 py-2"
                        >
                            {departments.map(dept => (
                                <option key={dept.id} value={dept.id}>{dept.name}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Assign To</label>
                        <select
                            value={assignedTo}
                            onChange={(e) => setAssignedTo(e.target.value)}
                            className="w-full border rounded-md px-3 py-2"
                        >
                            <option value="">Unassigned</option>
                            {departmentUsers.map(user => (
                                <option key={user.id} value={user.id}>
                                    {user.first_name} {user.last_name}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                <div className="mt-6 flex justify-end space-x-3">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={() => reassignMutation.mutate()}
                        disabled={reassignMutation.isPending}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                        {reassignMutation.isPending ? 'Saving...' : 'Reassign'}
                    </button>
                </div>
            </div>
        </div>
    );
}

function ForceCloseModal({ consult, onClose, onSuccess }) {
    const [reason, setReason] = useState('');
    const [action, setAction] = useState('complete');
    const [error, setError] = useState('');

    const forceCloseMutation = useMutation({
        mutationFn: () => adminAPI.forceCloseConsult(consult.id, { reason, action }),
        onSuccess: () => {
            onSuccess();
        },
        onError: (err) => {
            setError(err.response?.data?.error || 'Failed to close consult');
        },
    });

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
                <h3 className="text-lg font-semibold mb-4">Force Close Consult</h3>
                
                {error && (
                    <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm">{error}</div>
                )}

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Action</label>
                        <select
                            value={action}
                            onChange={(e) => setAction(e.target.value)}
                            className="w-full border rounded-md px-3 py-2"
                        >
                            <option value="complete">Mark as Completed</option>
                            <option value="cancel">Cancel Consult</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Reason *</label>
                        <textarea
                            value={reason}
                            onChange={(e) => setReason(e.target.value)}
                            className="w-full border rounded-md px-3 py-2"
                            rows={3}
                            placeholder="Enter reason for force closing..."
                        />
                    </div>
                </div>

                <div className="mt-6 flex justify-end space-x-3">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={() => forceCloseMutation.mutate()}
                        disabled={!reason || forceCloseMutation.isPending}
                        className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
                    >
                        {forceCloseMutation.isPending ? 'Closing...' : 'Force Close'}
                    </button>
                </div>
            </div>
        </div>
    );
}
