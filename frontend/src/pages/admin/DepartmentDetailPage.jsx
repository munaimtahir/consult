import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { adminAPI } from '../../api';
import { DepartmentMemberTable } from '../../components/admin/DepartmentMemberTable';

export default function DepartmentDetailPage() {
    const { id } = useParams();

    const {
        data: department,
        isLoading: isLoadingDepartment,
        isError: isDepartmentError,
        error: departmentError,
    } = useQuery({
        queryKey: ['department', id],
        queryFn: () => adminAPI.getDepartment(id),
    });

    const {
        data: overviewData,
        isLoading: isLoadingOverview,
        isError: isOverviewError,
        error: overviewError,
    } = useQuery({
        queryKey: ['departmentOverview', id],
        queryFn: () => adminAPI.getDepartmentOverview(id),
    });

    if (isLoadingDepartment || isLoadingOverview) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-xl">Loading department details...</div>
            </div>
        );
    }

    if (isDepartmentError || isOverviewError) {
        const message =
            departmentError?.response?.data?.detail ||
            overviewError?.response?.data?.detail ||
            departmentError?.message ||
            overviewError?.message ||
            'Unable to load department details.';

        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-center">
                    <h1 className="text-xl font-semibold text-red-600 mb-2">
                        Failed to load department details
                    </h1>
                    <p className="text-gray-600 text-sm">{message}</p>
                </div>
            </div>
        );
    }

    const members = Array.isArray(overviewData) ? overviewData : overviewData?.results || [];

    return (
        <div className="min-h-full bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">{department?.name}</h1>
                </div>

                {members.length === 0 ? (
                    <div className="bg-white rounded-lg shadow-sm border p-6 text-center text-gray-500">
                        No department members found.
                    </div>
                ) : (
                    <DepartmentMemberTable members={members} />
                )}
            </div>
        </div>
    );
}
