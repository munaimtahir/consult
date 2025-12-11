import { useQuery } from '@tanstack/react-query';
import { adminAPI } from '../../api';
import DoctorAnalyticsTable from '../../components/admin/DoctorAnalyticsTable';

export default function DoctorAnalyticsPage() {
    const {
        data: analyticsData,
        isLoading,
        isError,
        error,
    } = useQuery({
        queryKey: ['doctorAnalytics'],
        queryFn: () => adminAPI.getDoctorAnalytics(),
    });

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-xl">Loading doctor analytics...</div>
            </div>
        );
    }

    if (isError) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-center">
                    <h1 className="text-xl font-semibold text-red-600 mb-2">
                        Failed to load doctor analytics
                    </h1>
                    <p className="text-gray-600 text-sm">
                        {error?.response?.data?.detail || error?.message || 'Please try again later.'}
                    </p>
                </div>
            </div>
        );
    }

    const tableData = Array.isArray(analyticsData) ? analyticsData : analyticsData?.results || [];

    return (
        <div className="min-h-full bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Doctor Analytics</h1>
                    <p className="text-gray-600">Performance metrics for each doctor.</p>
                </div>

                {tableData.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-sm border p-6 text-center text-gray-500">
                        No analytics data available.
                    </div>
                ) : (
                    <DoctorAnalyticsTable data={tableData} />
                )}
            </div>
        </div>
    );
}
