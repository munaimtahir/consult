import { useParams } from 'react-router-dom';
import { useConsult } from '../hooks/useConsults';
import ConsultDetailHeader from '../components/ConsultDetailHeader';
import ConsultTimeline from '../components/ConsultTimeline';

/**
 * Renders the detailed view of a single consult.
 *
 * This component orchestrates the display of the consult detail page,
 * including the header and notes sections.
 *
 * @returns {React.ReactElement} The rendered consult detail page.
 */
export default function ConsultDetailPage() {
    const { id } = useParams();
    const { data: consult, isLoading } = useConsult(id);

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
                <div className="text-xl text-red-600">This consult does not belong to your department.</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 py-8">
                <ConsultDetailHeader consult={consult} />
                <ConsultNotes consult={consult} />
            </div>
        </div>
    );
}
