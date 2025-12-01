import { Link } from 'react-router-dom';

const urgencyColors = {
    EMERGENCY: 'bg-red-100 text-red-800 border-red-300',
    URGENT: 'bg-orange-100 text-orange-800 border-orange-300',
    ROUTINE: 'bg-blue-100 text-blue-800 border-blue-300',
};

const statusColors = {
    SUBMITTED: 'bg-yellow-100 text-yellow-800',
    ACKNOWLEDGED: 'bg-blue-100 text-blue-800',
    IN_PROGRESS: 'bg-purple-100 text-purple-800',
    MORE_INFO_REQUIRED: 'bg-pink-100 text-pink-800',
    COMPLETED: 'bg-green-100 text-green-800',
    CLOSED: 'bg-gray-100 text-gray-800',
};


export default function ConsultDetailHeader({ consult }) {
    return (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex items-start justify-between mb-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">
                        Consult #{consult.id}
                    </h1>
                </div>
                <div>
                    <Link
                        to="/consults/new"
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
                    >
                        + New Consult
                    </Link>
                    <div className="flex items-center gap-3">
                        <span className={`px-4 py-2 rounded-lg text-sm font-semibold border-2 ${urgencyColors[consult.urgency]}`}>
                            {consult.urgency}
                        </span>
                        <span className={`px-4 py-2 rounded-lg text-sm font-semibold ${statusColors[consult.status]}`}>
                            {consult.status.replace('_', ' ')}
                        </span>
                        {consult.is_overdue && (
                            <span className="px-4 py-2 rounded-lg text-sm font-semibold bg-red-600 text-white">
                                OVERDUE
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {/* Patient Info */}
            <div className="grid grid-cols-2 gap-6 mt-6">
                <div>
                    <h3 className="text-sm font-semibold text-gray-500 mb-2">PATIENT</h3>
                    <p className="text-lg font-semibold">{consult.patient.name}</p>
                    <p className="text-gray-600">MRN: {consult.patient.mrn}</p>
                    <p className="text-gray-600">Age: {consult.patient.age} | Gender: {consult.patient.gender}</p>
                    <p className="text-gray-600">Location: {consult.patient.ward}, Bed {consult.patient.bed_number}</p>
                </div>

                <div>
                    <h3 className="text-sm font-semibold text-gray-500 mb-2">CONSULT INFO</h3>
                    <p className="text-gray-700">
                        <span className="font-semibold">From:</span> {consult.requesting_department.name}
                    </p>
                    <p className="text-gray-700">
                        <span className="font-semibold">To:</span> {consult.target_department.name}
                    </p>
                    <p className="text-gray-700">
                        <span className="font-semibold">Requester:</span> {consult.requester.first_name} {consult.requester.last_name}
                    </p>
                    {consult.assigned_to && (
                        <p className="text-gray-700">
                            <span className="font-semibold">Assigned to:</span> {consult.assigned_to.first_name} {consult.assigned_to.last_name}
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}
