import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useConsult, useAddNote } from '../hooks/useConsults';

const urgencyColors = {
    EMERGENCY: 'bg-red-100 text-red-800 border-red-300',
    URGENT: 'bg-orange-100 text-orange-800 border-orange-300',
    ROUTINE: 'bg-blue-100 text-blue-800 border-blue-300',
};

export default function ConsultDetailPage() {
    const { id } = useParams();
    const { data: consult, isLoading } = useConsult(id);
    const addNoteMutation = useAddNote();

    const [noteContent, setNoteContent] = useState('');
    const [noteType, setNoteType] = useState('PROGRESS');
    const [recommendations, setRecommendations] = useState('');

    const handleAddNote = async (e) => {
        e.preventDefault();

        try {
            await addNoteMutation.mutateAsync({
                id,
                noteData: {
                    content: noteContent,
                    note_type: noteType,
                    recommendations,
                    is_final: noteType === 'FINAL',
                },
            });

            setNoteContent('');
            setRecommendations('');
        } catch (error) {
            console.error('Failed to add note:', error);
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-xl">Loading consult...</div>
            </div>
        );
    }

    if (!consult) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-xl text-red-600">Consult not found</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <div className="flex items-start justify-between mb-4">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 mb-2">
                                Consult #{consult.id}
                            </h1>
                            <div className="flex items-center gap-3">
                                <span className={`px-4 py-2 rounded-lg text-sm font-semibold border-2 ${urgencyColors[consult.urgency]}`}>
                                    {consult.urgency}
                                </span>
                                <span className="px-4 py-2 rounded-lg text-sm font-semibold bg-gray-100 text-gray-800">
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

                    {/* Clinical Information */}
                    <div className="mt-6 space-y-4">
                        <div>
                            <h3 className="text-sm font-semibold text-gray-500 mb-2">REASON FOR CONSULT</h3>
                            <p className="text-gray-800">{consult.reason_for_consult}</p>
                        </div>

                        {consult.clinical_question && (
                            <div>
                                <h3 className="text-sm font-semibold text-gray-500 mb-2">CLINICAL QUESTION</h3>
                                <p className="text-gray-800">{consult.clinical_question}</p>
                            </div>
                        )}

                        {consult.relevant_history && (
                            <div>
                                <h3 className="text-sm font-semibold text-gray-500 mb-2">RELEVANT HISTORY</h3>
                                <p className="text-gray-800 whitespace-pre-wrap">{consult.relevant_history}</p>
                            </div>
                        )}

                        {consult.vital_signs && (
                            <div>
                                <h3 className="text-sm font-semibold text-gray-500 mb-2">VITAL SIGNS</h3>
                                <p className="text-gray-800 whitespace-pre-wrap">{consult.vital_signs}</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Notes Section */}
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Notes</h2>

                    {consult.notes.length === 0 ? (
                        <p className="text-gray-500 text-center py-8">No notes yet</p>
                    ) : (
                        <div className="space-y-4 mb-6">
                            {consult.notes.map((note) => (
                                <div key={note.id} className="border-l-4 border-blue-500 pl-4 py-2">
                                    <div className="flex items-center justify-between mb-2">
                                        <div>
                                            <span className="font-semibold text-gray-900">{note.author_name}</span>
                                            <span className="text-gray-500 text-sm ml-2">{note.author_designation}</span>
                                        </div>
                                        <span className="text-sm text-gray-500">
                                            {new Date(note.created_at).toLocaleString()}
                                        </span>
                                    </div>
                                    <p className="text-gray-800 whitespace-pre-wrap">{note.content}</p>
                                    {note.recommendations && (
                                        <div className="mt-2 p-3 bg-blue-50 rounded">
                                            <p className="text-sm font-semibold text-blue-900">Recommendations:</p>
                                            <p className="text-blue-800">{note.recommendations}</p>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Add Note Form */}
                    {consult.status !== 'COMPLETED' && consult.status !== 'CANCELLED' && (
                        <form onSubmit={handleAddNote} className="border-t pt-6">
                            <h3 className="text-lg font-semibold mb-4">Add Note</h3>

                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Note Type
                                </label>
                                <select
                                    value={noteType}
                                    onChange={(e) => setNoteType(e.target.value)}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                >
                                    <option value="PROGRESS">Progress Note</option>
                                    <option value="ASSESSMENT">Assessment</option>
                                    <option value="RECOMMENDATION">Recommendation</option>
                                    <option value="PLAN">Plan</option>
                                    <option value="FINAL">Final Note</option>
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
            </div>
        </div>
    );
}
