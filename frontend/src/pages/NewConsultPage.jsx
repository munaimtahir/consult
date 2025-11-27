import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { consultsAPI, departmentsAPI } from '../api';
import { useAuth } from '../context/AuthContext';
import PatientSearch from '../components/PatientSearch';
import PatientCreateModal from '../components/PatientCreateModal';

const NewConsultPage = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [selectedPatient, setSelectedPatient] = useState(null);
    const [isPatientModalOpen, setIsPatientModalOpen] = useState(false);
    const [formData, setFormData] = useState({
        target_department: '',
        urgency: 'ROUTINE',
        reason_for_consult: '',
        clinical_question: '',
        relevant_history: '',
        current_medications: '',
        vital_signs: '',
        lab_results: '',
    });
    const [error, setError] = useState('');

    const { data: departments } = useQuery({
        queryKey: ['departments'],
        queryFn: departmentsAPI.getDepartments,
    });

    const createConsultMutation = useMutation({
        mutationFn: consultsAPI.createConsult,
        onSuccess: (data) => {
            navigate(`/consults/${data.id}`);
        },
        onError: (err) => {
            setError(err.response?.data?.detail || 'Failed to create consult request');
        },
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!selectedPatient) {
            setError('Please select a patient');
            return;
        }
        if (!formData.target_department) {
            setError('Please select a target department');
            return;
        }

        // Ensure requesting department is sent if needed, or backend handles it.
        // Based on serializer, we might need to send it if it's not read-only for creation.
        // But usually backend sets it from user. Let's try sending it if user has one.
        const payload = {
            ...formData,
            patient: selectedPatient.id,
            requesting_department: user?.department?.id || user?.department, // Handle both object or ID
        };

        createConsultMutation.mutate(payload);
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    return (
        <div className="max-w-3xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="md:flex md:items-center md:justify-between mb-6">
                <div className="min-w-0 flex-1">
                    <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
                        New Consult Request
                    </h2>
                </div>
            </div>

            <div className="bg-white shadow sm:rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                    {error && (
                        <div className="mb-4 p-2 bg-red-100 text-red-700 rounded text-sm">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Patient Selection */}
                        <div>
                            <div className="flex justify-between items-center mb-1">
                                <label className="block text-sm font-medium text-gray-700">
                                    Patient
                                </label>
                                <button
                                    type="button"
                                    onClick={() => setIsPatientModalOpen(true)}
                                    className="text-sm text-indigo-600 hover:text-indigo-500"
                                >
                                    + Create New Patient
                                </button>
                            </div>
                            <PatientSearch
                                selectedPatient={selectedPatient}
                                onSelect={setSelectedPatient}
                            />
                        </div>

                        {/* Target Department */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Target Department
                            </label>
                            <select
                                name="target_department"
                                required
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                                value={formData.target_department}
                                onChange={handleChange}
                            >
                                <option value="">Select Department</option>
                                {departments?.results?.map((dept) => (
                                    <option key={dept.id} value={dept.id}>
                                        {dept.name}
                                    </option>
                                )) || departments?.map((dept) => (
                                    <option key={dept.id} value={dept.id}>
                                        {dept.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Urgency */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Urgency
                            </label>
                            <select
                                name="urgency"
                                required
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                                value={formData.urgency}
                                onChange={handleChange}
                            >
                                <option value="ROUTINE">Routine</option>
                                <option value="URGENT">Urgent</option>
                                <option value="EMERGENCY">Emergency</option>
                            </select>
                        </div>

                        {/* Reason for Consult */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Reason for Consult
                            </label>
                            <textarea
                                name="reason_for_consult"
                                required
                                rows={3}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                                value={formData.reason_for_consult}
                                onChange={handleChange}
                                placeholder="Why is this consult being requested?"
                            />
                        </div>

                        {/* Clinical Question */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Specific Question
                            </label>
                            <textarea
                                name="clinical_question"
                                rows={2}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                                value={formData.clinical_question}
                                onChange={handleChange}
                                placeholder="What specific question do you have for the consulting team?"
                            />
                        </div>

                        {/* Additional Info */}
                        <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">
                                    Relevant History
                                </label>
                                <textarea
                                    name="relevant_history"
                                    rows={3}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                                    value={formData.relevant_history}
                                    onChange={handleChange}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">
                                    Current Medications
                                </label>
                                <textarea
                                    name="current_medications"
                                    rows={3}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                                    value={formData.current_medications}
                                    onChange={handleChange}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">
                                    Vital Signs
                                </label>
                                <textarea
                                    name="vital_signs"
                                    rows={3}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                                    value={formData.vital_signs}
                                    onChange={handleChange}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">
                                    Lab Results
                                </label>
                                <textarea
                                    name="lab_results"
                                    rows={3}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                                    value={formData.lab_results}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        <div className="flex justify-end">
                            <button
                                type="button"
                                onClick={() => navigate('/dashboard')}
                                className="mr-3 rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={createConsultMutation.isPending}
                                className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                            >
                                {createConsultMutation.isPending ? 'Submitting...' : 'Submit Request'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <PatientCreateModal
                isOpen={isPatientModalOpen}
                onClose={() => setIsPatientModalOpen(false)}
                onPatientCreated={(patient) => {
                    setSelectedPatient(patient);
                    setIsPatientModalOpen(false);
                }}
            />
        </div>
    );
};

export default NewConsultPage;
