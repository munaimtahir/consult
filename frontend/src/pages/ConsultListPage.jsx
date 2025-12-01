import { useSearchParams } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useConsults } from '../hooks/useConsults';
import ConsultFilter from '../components/ConsultFilter';
import ConsultList from '../components/ConsultList';

/**
 * Renders the main consult list page.
 *
 * This component orchestrates the display of the consult list, including
 * the filter controls and the list of consults. It fetches the consults
 * based on the current filter settings and applies a default filter based
 * on the user's role.
 *
 * @returns {React.ReactElement} The rendered consult list page.
 */
export default function ConsultListPage() {
    const { user: currentUser } = useAuth();
    const [searchParams, setSearchParams] = useSearchParams();

    useEffect(() => {
        if (currentUser && !searchParams.has('view')) {
            const params = new URLSearchParams(searchParams);
            let defaultView = 'all';
            if (currentUser.role === 'DOCTOR') {
                defaultView = 'assigned_to_me';
            } else if (currentUser.role === 'HOD' || currentUser.role === 'DEPARTMENT_USER') {
                defaultView = 'my_department';
            }
            params.set('view', defaultView);
            setSearchParams(params, { replace: true });
        }
    }, [searchParams, setSearchParams, currentUser]);

    const view = searchParams.get('view') || 'all';
    const status = searchParams.get('status') || '';
    const urgency = searchParams.get('urgency') || '';

    const { data: consults, isLoading } = useConsults({ view, status, urgency });

    if (isLoading || !currentUser) {
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
                <ConsultFilter />
                <ConsultList consults={consults} />
            </div>
        </div>
    );
}
