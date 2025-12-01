import { useQuery } from '@tanstack/react-query';
import { adminAPI } from '../../api';
import DoctorAnalyticsTable from '../../components/admin/DoctorAnalyticsTable';

const fetchDoctorAnalytics = async () => {
    const { data } = await adminAPI.get('/analytics/doctors/');
    return data;
};

export default function DoctorAnalyticsPage() {
    const { data: analyticsData, isLoading } = useQuery({
        queryKey: ['doctorAnalytics'],
        queryFn: fetchDoctorAnalytics,
    });

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-xl">Loading doctor analytics...</div>
            </div>
        );
    }

    return (
        <div className="min-h-full bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Doctor Analytics</h1>
                    <p className="text-gray-600">Performance metrics for each doctor.</p>
                </div>
                <DoctorAnalyticsTable data={analyticsData} />
            </div>
        </div>
    );
}
