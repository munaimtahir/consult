import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../api';

const updateHierarchy = async (userId, hierarchyNumber) => {
    const { data } = await api.patch(`/admin/users/${userId}/`, {
        hierarchy_number: hierarchyNumber,
    });
    return data;
};

export function DepartmentMemberTable({ members }) {
    const queryClient = useQueryClient();
    const [editableMembers, setEditableMembers] = useState(
        members.map((m) => ({ ...m, hierarchy_number_edit: m.hierarchy_number }))
    );

    const mutation = useMutation({
        mutationFn: ({ userId, hierarchyNumber }) => updateHierarchy(userId, hierarchyNumber),
        onSuccess: () => {
            queryClient.invalidateQueries(['departmentOverview']);
        },
    });

    const handleHierarchyChange = (userId, value) => {
        setEditableMembers(
            editableMembers.map((m) =>
                m.id === userId ? { ...m, hierarchy_number_edit: value } : m
            )
        );
    };

    const handleSaveChanges = () => {
        editableMembers.forEach((member) => {
            if (member.hierarchy_number !== member.hierarchy_number_edit) {
                mutation.mutate({
                    userId: member.id,
                    hierarchyNumber: member.hierarchy_number_edit,
                });
            }
        });
    };

    return (
        <div className="bg-white rounded-lg shadow">
            <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                    <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Department Member
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Role
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Hierarchy No.
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Active Consults
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Completed Consults
                        </th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {editableMembers.map((member) => (
                        <tr key={member.id}>
                            <td className="px-6 py-4 whitespace-nowrap">{member.full_name}</td>
                            <td className="px-6 py-4 whitespace-nowrap">{member.role}</td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                <input
                                    type="number"
                                    value={member.hierarchy_number_edit}
                                    onChange={(e) =>
                                        handleHierarchyChange(member.id, e.target.value)
                                    }
                                    className="w-20 px-2 py-1 border border-gray-300 rounded-md"
                                />
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                {member.active_consults}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                {member.completed_consults}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <div className="p-4">
                <button
                    onClick={handleSaveChanges}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    disabled={mutation.isLoading}
                >
                    {mutation.isLoading ? 'Saving...' : 'Save Changes'}
                </button>
            </div>
        </div>
    );
}
