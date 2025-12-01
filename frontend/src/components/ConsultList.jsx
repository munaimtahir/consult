import { Link } from 'react-router-dom';
import { formatTimeAgo } from '../utils/time';

const urgencyColors = {
    EMERGENCY: 'bg-red-100 text-red-800',
    URGENT: 'bg-orange-100 text-orange-800',
    ROUTINE: 'bg-blue-100 text-blue-800',
};

const statusColors = {
    SUBMITTED: 'bg-yellow-100 text-yellow-800',
    ACKNOWLEDGED: 'bg-blue-100 text-blue-800',
    IN_PROGRESS: 'bg-purple-100 text-purple-800',
    MORE_INFO_REQUIRED: 'bg-pink-100 text-pink-800',
    COMPLETED: 'bg-green-100 text-green-800',
    CLOSED: 'bg-gray-100 text-gray-800',
};

export default function ConsultList({ consults }) {
    return (
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
                                <div>{formatTimeAgo(consult.created_at)}</div>
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
    );
}
