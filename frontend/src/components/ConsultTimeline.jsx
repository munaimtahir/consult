import { useState } from 'react';
import { useAddNote } from '../hooks/useConsults';
import { formatTimeAgo } from '../utils/time';
import { FaPlus, FaCheck, FaUserMd, FaInfoCircle, FaTimes, FaStickyNote } from 'react-icons/fa';

const noteTypeStyles = {
    PROGRESS_UPDATE: {
        icon: FaStickyNote,
        color: 'blue',
        label: 'Progress Update',
    },
    PLAN_MANAGEMENT: {
        icon: FaStickyNote,
        color: 'purple',
        label: 'Plan/Management',
    },
    REQUEST_MORE_INFO: {
        icon: FaInfoCircle,
        color: 'orange',
        label: 'More Info Requested',
    },
    ASSIGNED_TO: {
        icon: FaUserMd,
        color: 'green',
        label: 'Assigned To',
    },
    FOLLOW_UP_NEEDED: {
        icon: FaStickyNote,
        color: 'teal',
        label: 'Follow-up Needed',
    },
    CLOSE_CONSULT: {
        icon: FaCheck,
        color: 'gray',
        label: 'Consult Closed',
    },
    SUBMITTED: {
        icon: FaPlus,
        color: 'gray',
        label: 'Consult Submitted',
    },
    ACKNOWLEDGED: {
        icon: FaCheck,
        color: 'blue',
        label: 'Consult Acknowledged',
    },
};

export default function ConsultTimeline({ consult }) {
    const addNoteMutation = useAddNote();
    const [noteContent, setNoteContent] = useState('');
    const [noteType, setNoteType] = useState('PROGRESS_UPDATE');
    const [recommendations, setRecommendations] = useState('');

    const handleAddNote = async (e) => {
        e.preventDefault();

        try {
            await addNoteMutation.mutateAsync({
                id: consult.id,
                noteData: {
                    content: noteContent,
                    note_type: noteType,
                    recommendations,
                },
            });

            setNoteContent('');
            setRecommendations('');
        } catch (error) {
            console.error('Failed to add note:', error);
        }
    };

    const timelineEvents = [
        {
            type: 'SUBMITTED',
            timestamp: consult.created_at,
            author: consult.requester.full_name,
            content: `Consult submitted by ${consult.requester.full_name} from ${consult.requesting_department.name}.`,
        },
        ...(consult.acknowledged_at
            ? [
                  {
                      type: 'ACKNOWLEDGED',
                      timestamp: consult.acknowledged_at,
                      author: consult.acknowledged_by?.full_name || 'System',
                      content: `Consult acknowledged by ${consult.acknowledged_by?.full_name || 'System'}.`,
                  },
              ]
            : []),
        ...consult.notes.map((note) => ({
            type: note.note_type,
            timestamp: note.created_at,
            author: note.author_name,
            content: note.content,
            recommendations: note.recommendations,
        })),
    ].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    return (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Consult Timeline</h2>

            {timelineEvents.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No events yet</p>
            ) : (
                <div className="space-y-4 mb-6">
                    {timelineEvents.map((event, index) => {
                        const style = noteTypeStyles[event.type] || noteTypeStyles.PROGRESS_UPDATE;
                        const Icon = style.icon;

                        return (
                            <div key={index} className={`border-l-4 border-${style.color}-500 pl-4 py-2`}>
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center">
                                        <Icon className={`text-${style.color}-500 mr-2`} />
                                        <span className="font-semibold text-gray-900">{event.author}</span>
                                        <span className="text-gray-500 text-sm ml-2">- {style.label}</span>
                                    </div>
                                    <span className="text-sm text-gray-500">
                                        {formatTimeAgo(event.timestamp)}
                                    </span>
                                </div>
                                <p className="text-gray-800 whitespace-pre-wrap">{event.content}</p>
                                {event.recommendations && (
                                    <div className="mt-2 p-3 bg-blue-50 rounded">
                                        <p className="text-sm font-semibold text-blue-900">Recommendations:</p>
                                        <p className="text-blue-800">{event.recommendations}</p>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Add Note Form */}
            {consult.status !== 'COMPLETED' && consult.status !== 'CLOSED' && (
                <form onSubmit={handleAddNote} className="border-t pt-6">
                    <h3 className="text-lg font-semibold mb-4">Add a New Note</h3>

                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Select Note Type
                        </label>
                        <select
                            value={noteType}
                            onChange={(e) => setNoteType(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                        >
                            <option value="PROGRESS_UPDATE">Progress Update</option>
                            <option value="PLAN_MANAGEMENT">Plan / Management</option>
                            <option value="REQUEST_MORE_INFO">Request More Information</option>
                            <option value="ASSIGNED_TO">Assigned To</option>
                            <option value="FOLLOW_UP_NEEDED">Follow-up Needed</option>
                            <option value="CLOSE_CONSULT">Close Consult</option>
                        </select>
                    </div>

                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Note Content
                        </label>
                        <textarea
                            value={noteContent}
                            onChange={(e) => setNoteContent(e.target.value)}
                            required
                            rows={4}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                            placeholder="Enter your note..."
                        />
                    </div>

                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Recommendations (Optional)
                        </label>
                        <textarea
                            value={recommendations}
                            onChange={(e) => setRecommendations(e.target.value)}
                            rows={3}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                            placeholder="Enter recommendations..."
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={addNoteMutation.isPending}
                        className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-blue-300"
                    >
                        {addNoteMutation.isPending ? 'Adding...' : 'Add Note'}
                    </button>
                </form>
            )}
        </div>
    );
}
