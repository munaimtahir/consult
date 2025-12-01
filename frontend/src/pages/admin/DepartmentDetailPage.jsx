import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { adminAPI as api } from '../../api';
import { DepartmentMemberTable } from '../../components/admin/DepartmentMemberTable';

const fetchDepartmentDetails = async (id) => {
    const { data } = await api.get(`/admin/departments/${id}/`);
    return data;
};

const fetchDepartmentOverview = async (id) => {
    const { data } = await api.get(`/admin/departments/${id}/overview/`);
    return data;
};

export default function DepartmentDetailPage() {
    const { id } = useParams();

    const { data: department, isLoading: isLoadingDepartment } = useQuery({
        queryKey: ['department', id],
        queryFn: () => fetchDepartmentDetails(id),
    });

    const { data: overviewData, isLoading: isLoadingOverview } = useQuery({
        queryKey: ['departmentOverview', id],
        queryFn: () => fetchDepartmentOverview(id),
    });

    if (isLoadingDepartment || isLoadingOverview) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-xl">Loading department details...</div>
            </div>
        );
    }

    return (
        <div className="min-h-full bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">{department.name}</h1>
                </div>
                <DepartmentMemberTable members={overviewData} />
            </div>
        </div>
    );
}
