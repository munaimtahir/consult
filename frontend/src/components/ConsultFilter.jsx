import { useSearchParams } from 'react-router-dom';

export default function ConsultFilter() {
    const [searchParams, setSearchParams] = useSearchParams();
    const view = searchParams.get('view') || 'all';
    const status = searchParams.get('status') || '';
    const urgency = searchParams.get('urgency') || '';

    const handleFilterChange = (key, value) => {
        const params = new URLSearchParams(searchParams);
        if (value) {
            params.set(key, value);
        } else {
            params.delete(key);
        }
        setSearchParams(params);
    };

    return (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Filter by View
                    </label>
                    <select
                        value={view}
                        onChange={(e) => handleFilterChange('view', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    >
                        <option value="all">All Consults</option>
                        <option value="my_department">My Department</option>
                        <option value="assigned_to_me">Assigned to Me</option>
                        <option value="my_requests">My Outgoing Requests</option>
                        <option value="pending_assignment">Pending Assignment</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Filter by Status
                    </label>
                    <select
                        value={status}
                        onChange={(e) => handleFilterChange('status', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    >
                        <option value="">All Statuses</option>
                        <option value="SUBMITTED">Submitted</option>
                        <option value="ACKNOWLEDGED">Acknowledged</option>
                        <option value="IN_PROGRESS">In Progress</option>
                        <option value="MORE_INFO_REQUIRED">More Info Required</option>
                        <option value="COMPLETED">Completed</option>
                        <option value="CLOSED">Closed</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Filter by Urgency
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
                <div className="flex items-end">
                    <button
                        onClick={() => setSearchParams({})}
                        className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                    >
                        Clear All Filters
                    </button>
                </div>
            </div>
        </div>
    );
}
