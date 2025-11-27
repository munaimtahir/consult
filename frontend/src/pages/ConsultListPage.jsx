import { useSearchParams, Link } from 'react-router-dom';
import { useConsults } from '../hooks/useConsults';

const urgencyColors = {
    EMERGENCY: 'bg-red-100 text-red-800',
    URGENT: 'bg-orange-100 text-orange-800',
    ROUTINE: 'bg-blue-100 text-blue-800',
};

const statusColors = {
    PENDING: 'bg-yellow-100 text-yellow-800',
    ACKNOWLEDGED: 'bg-blue-100 text-blue-800',
    IN_PROGRESS: 'bg-purple-100 text-purple-800',
    COMPLETED: 'bg-green-100 text-green-800',
    CANCELLED: 'bg-gray-100 text-gray-800',
};

/**
 * Renders a list of consults with filtering options.
 *
 * This component displays a list of consults and allows the user to filter
 * them by view (e.g., 'my_department', 'assigned_to_me'), status, and
 * urgency. The filters are managed via URL search parameters.
 *
 * @returns {React.ReactElement} The rendered consult list page component.
 */
export default function ConsultListPage() {
    const [searchParams, setSearchParams] = useSearchParams();
    const view = searchParams.get('view') || 'all';
    const status = searchParams.get('status') || '';
    const urgency = searchParams.get('urgency') || '';

    const { data: consults, isLoading } = useConsults({ view, status, urgency });

    const handleFilterChange = (key, value) => {
        const params = new URLSearchParams(searchParams);
        if (value) {
            params.set(key, value);
        } else {
            params.delete(key);
        }
        setSearchParams(params);
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-xl">Loading consults...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Consults</h1>
                </div>

                {/* Filters */}
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                View
                            </label>
                            <select
                                value={view}
                                onChange={(e) => handleFilterChange('view', e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                            >
                                <option value="all">All Consults</option>
                                <option value="my_department">My Department</option>
                                <option value="assigned_to_me">Assigned to Me</option>
                                <option value="my_requests">My Requests</option>
                                <option value="pending_assignment">Pending Assignment</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Status
                            </label>
                            <select
                                value={status}
                                onChange={(e) => handleFilterChange('status', e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                            >
                                <option value="">All Statuses</option>
                                <option value="PENDING">Pending</option>
                                <option value="ACKNOWLEDGED">Acknowledged</option>
                                <option value="IN_PROGRESS">In Progress</option>
                                <option value="COMPLETED">Completed</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Urgency
                            </label>
                            <select
                                value={urgency}
                                onChange={(e) => handleFilterChange('urgency', e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                            >
                                <option value="">All Urgencies</option>
                                <option value="EMERGENCY">Emergency</option>
                                <option value="URGENT">Urgent</option>
                                <option value="ROUTINE">Routine</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Consults List */}
                <div className="space-y-4">
                    {consults?.results?.length === 0 ? (
                        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
                            No consults found
                        </div>
                    ) : (
                        consults?.results?.map((consult) => (
                            <Link
                                key={consult.id}
                                to={`/consults/${consult.id}`}
                                className="block bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6"
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${urgencyColors[consult.urgency]}`}>
                                                {consult.urgency}
                                            </span>
                                            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${statusColors[consult.status]}`}>
                                                {consult.status.replace('_', ' ')}
                                            </span>
                                            {consult.is_overdue && (
                                                <span className="px-3 py-1 rounded-full text-sm font-semibold bg-red-600 text-white">
                                                    OVERDUE
                                                </span>
                                            )}
                                        </div>

                                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                            {consult.patient_name} (MRN: {consult.patient_mrn})
                                        </h3>

                                        <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                                            <div>
                                                <span className="font-medium">Location:</span> {consult.patient_location}
                                            </div>
                                            <div>
                                                <span className="font-medium">Requester:</span> {consult.requester_name}
                                            </div>
                                            <div>
                                                <span className="font-medium">From:</span> {consult.requesting_department_name}
                                            </div>
                                            <div>
                                                <span className="font-medium">To:</span> {consult.target_department_name}
                                            </div>
                                        </div>

                                        <p className="mt-3 text-gray-700 line-clamp-2">
                                            {consult.reason_for_consult}
                                        </p>
                                    </div>

                                    <div className="ml-4 text-right text-sm text-gray-500">
                                        <div>{new Date(consult.created_at).toLocaleDateString()}</div>
                                        <div>{new Date(consult.created_at).toLocaleTimeString()}</div>
                                        {consult.notes_count > 0 && (
                                            <div className="mt-2 text-blue-600 font-semibold">
                                                {consult.notes_count} note{consult.notes_count !== 1 ? 's' : ''}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </Link>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
