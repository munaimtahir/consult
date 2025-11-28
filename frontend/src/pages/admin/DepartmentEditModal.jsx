import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminAPI } from '../../api';

/**
 * Modal for editing/creating departments.
 */
export default function DepartmentEditModal({ department, isCreating, onClose, departments }) {
    const queryClient = useQueryClient();
    const [formData, setFormData] = useState(() => {
        if (department) {
            return {
                name: department.name || '',
                code: department.code || '',
                department_type: department.department_type || 'CLINICAL',
                parent: department.parent || '',
                head: department.head || '',
                contact_number: department.contact_number || '',
                is_active: department.is_active ?? true,
                emergency_sla: department.emergency_sla || 60,
                urgent_sla: department.urgent_sla || 240,
                routine_sla: department.routine_sla || 1380,
            };
        }
        return {
            name: '',
            code: '',
            department_type: 'CLINICAL',
            parent: '',
            head: '',
            contact_number: '',
            is_active: true,
            emergency_sla: 60,
            urgent_sla: 240,
            routine_sla: 1380,
        };
    });
    const [error, setError] = useState('');

    // Fetch users for HOD selection
    const { data: usersData } = useQuery({
        queryKey: ['admin-users-for-hod'],
        queryFn: () => adminAPI.getUsers({ role: 'HOD' }),
    });

    const hodUsers = usersData?.results || usersData || [];

    const createMutation = useMutation({
        mutationFn: (data) => adminAPI.createDepartment(data),
        onSuccess: () => {
            queryClient.invalidateQueries(['admin-departments']);
            onClose();
        },
        onError: (err) => {
            setError(err.response?.data?.name?.[0] || err.response?.data?.code?.[0] || err.response?.data?.detail || 'Failed to create department');
        },
    });

    const updateMutation = useMutation({
        mutationFn: (data) => adminAPI.updateDepartment(department.id, data),
        onSuccess: () => {
            queryClient.invalidateQueries(['admin-departments']);
            onClose();
        },
        onError: (err) => {
            setError(err.response?.data?.detail || 'Failed to update department');
        },
    });

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value,
        }));
    };

    const handleSubmit = () => {
        setError('');
        
        const data = {
            name: formData.name,
            code: formData.code,
            department_type: formData.department_type,
            parent: formData.parent || null,
            head: formData.head || null,
            contact_number: formData.contact_number,
            is_active: formData.is_active,
            emergency_sla: parseInt(formData.emergency_sla) || 60,
            urgent_sla: parseInt(formData.urgent_sla) || 240,
            routine_sla: parseInt(formData.routine_sla) || 1380,
        };

        if (isCreating) {
            createMutation.mutate(data);
        } else {
            updateMutation.mutate(data);
        }
    };

    const isLoading = createMutation.isPending || updateMutation.isPending;

    // Filter out current department from parent options to prevent self-reference
    const parentOptions = departments.filter(d => d.id !== department?.id);

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-xl max-h-[90vh] overflow-hidden">
                {/* Header */}
                <div className="px-6 py-4 border-b flex justify-between items-center">
                    <h2 className="text-xl font-semibold text-gray-900">
                        {isCreating ? 'Create New Department' : `Edit Department: ${department?.name}`}
                    </h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                        ✕
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto max-h-[70vh]">
                    {error && (
                        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
                            {error}
                        </div>
                    )}

                    <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Name *
                                </label>
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleInputChange}
                                    className="w-full border rounded-md px-3 py-2"
                                    placeholder="Cardiology"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Code *
                                </label>
                                <input
                                    type="text"
                                    name="code"
                                    value={formData.code}
                                    onChange={handleInputChange}
                                    className="w-full border rounded-md px-3 py-2"
                                    placeholder="CARDIO"
                                    maxLength={10}
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Type
                                </label>
                                <select
                                    name="department_type"
                                    value={formData.department_type}
                                    onChange={handleInputChange}
                                    className="w-full border rounded-md px-3 py-2"
                                >
                                    <option value="CLINICAL">Clinical</option>
                                    <option value="ADMINISTRATIVE">Administrative</option>
                                    <option value="SUPPORT">Support</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Parent Department
                                </label>
                                <select
                                    name="parent"
                                    value={formData.parent}
                                    onChange={handleInputChange}
                                    className="w-full border rounded-md px-3 py-2"
                                >
                                    <option value="">None (Top-level)</option>
                                    {parentOptions.map(dept => (
                                        <option key={dept.id} value={dept.id}>{dept.name}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Head of Department
                                </label>
                                <select
                                    name="head"
                                    value={formData.head}
                                    onChange={handleInputChange}
                                    className="w-full border rounded-md px-3 py-2"
                                >
                                    <option value="">No HOD assigned</option>
                                    {hodUsers.map(user => (
                                        <option key={user.id} value={user.id}>
                                            {user.first_name} {user.last_name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Contact Number
                                </label>
                                <input
                                    type="tel"
                                    name="contact_number"
                                    value={formData.contact_number}
                                    onChange={handleInputChange}
                                    className="w-full border rounded-md px-3 py-2"
                                />
                            </div>
                        </div>

                        {/* SLA Settings */}
                        <div className="border-t pt-4 mt-4">
                            <h3 className="text-sm font-medium text-gray-900 mb-3">SLA Configuration (minutes)</h3>
                            <div className="grid grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm text-gray-600 mb-1">
                                        Emergency
                                    </label>
                                    <input
                                        type="number"
                                        name="emergency_sla"
                                        value={formData.emergency_sla}
                                        onChange={handleInputChange}
                                        className="w-full border rounded-md px-3 py-2"
                                        min="1"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm text-gray-600 mb-1">
                                        Urgent
                                    </label>
                                    <input
                                        type="number"
                                        name="urgent_sla"
                                        value={formData.urgent_sla}
                                        onChange={handleInputChange}
                                        className="w-full border rounded-md px-3 py-2"
                                        min="1"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm text-gray-600 mb-1">
                                        Routine
                                    </label>
                                    <input
                                        type="number"
                                        name="routine_sla"
                                        value={formData.routine_sla}
                                        onChange={handleInputChange}
                                        className="w-full border rounded-md px-3 py-2"
                                        min="1"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center">
                            <input
                                type="checkbox"
                                name="is_active"
                                checked={formData.is_active}
                                onChange={handleInputChange}
                                className="mr-2"
                            />
                            <label className="text-sm text-gray-700">Active</label>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t flex justify-end space-x-3">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={isLoading}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                        {isLoading ? 'Saving...' : (isCreating ? 'Create Department' : 'Save Changes')}
                    </button>
                </div>
            </div>
        </div>
    );
}
