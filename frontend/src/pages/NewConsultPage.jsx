import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { consultsAPI, departmentsAPI } from '../api';
import { useAuth } from '../hooks/useAuth';

const NewConsultPage = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [formData, setFormData] = useState({
        patient_name: '',
        patient_location: '',
        patient_age: '',
        primary_diagnosis: '',
        target_department: '',
        urgency: 'ROUTINE',
        reason_for_consult: '',
        clinical_question: '',
        relevant_history: '',
        current_medications: '',
        vital_signs: {
            hr: '',
            bp: '',
            rr: '',
            temp: '',
            rpo2: '',
            other: '',
        },
        investigations: {
            cbc: '',
            cmp: '',
            chest_xray: '',
            ecg: '',
            other: '',
        },
        investigations_other: '',
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
        if (!formData.patient_name) {
            setError('Please enter patient name');
            return;
        }
        if (!formData.target_department) {
            setError('Please select a target department');
            return;
        }

        // Convert vitals object to string for backend
        const vitalSignsString = Object.entries(formData.vital_signs)
            .filter(([_, value]) => value)
            .map(([key, value]) => `${key.toUpperCase()}: ${value}`)
            .join(', ') || '';

        // Convert investigations object to string for backend
        const investigationsString = Object.entries(formData.investigations)
            .filter(([_, value]) => value)
            .map(([key, value]) => `${key.replace(/_/g, ' ').toUpperCase()}: ${value}`)
            .concat(formData.investigations_other ? [`Other: ${formData.investigations_other}`] : [])
            .join(', ') || '';

        const payload = {
            patient_name: formData.patient_name,
            patient_location: formData.patient_location,
            patient_age: formData.patient_age,
            primary_diagnosis: formData.primary_diagnosis,
            target_department: formData.target_department,
            urgency: formData.urgency,
            reason_for_consult: formData.reason_for_consult,
            clinical_question: formData.clinical_question,
            relevant_history: formData.relevant_history,
            current_medications: formData.current_medications,
            vital_signs: vitalSignsString,
            lab_results: investigationsString,
            requesting_department: user?.department?.id || user?.department,
        };

        createConsultMutation.mutate(payload);
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleVitalChange = (field, value) => {
        setFormData((prev) => ({
            ...prev,
            vital_signs: {
                ...prev.vital_signs,
                [field]: value,
            },
        }));
    };

    const handleInvestigationChange = (field, value) => {
        setFormData((prev) => ({
            ...prev,
            investigations: {
                ...prev.investigations,
                [field]: value,
            },
        }));
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
                        {/* Patient Information */}
                        <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">
                                    Patient Name
                                </label>
                                <input
                                    type="text"
                                    name="patient_name"
                                    required
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                                    value={formData.patient_name}
                                    onChange={handleChange}
                                    placeholder="Enter patient name"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">
                                    Patient Location
                                </label>
                                <input
                                    type="text"
                                    name="patient_location"
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                                    value={formData.patient_location}
                                    onChange={handleChange}
                                    placeholder="Enter patient location"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">
                                    Patient Age
                                </label>
                                <input
                                    type="text"
                                    name="patient_age"
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                                    value={formData.patient_age}
                                    onChange={handleChange}
                                    placeholder="Enter patient age"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">
                                    Primary Diagnosis
                                </label>
                                <input
                                    type="text"
                                    name="primary_diagnosis"
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                                    value={formData.primary_diagnosis}
                                    onChange={handleChange}
                                    placeholder="Enter primary diagnosis"
                                />
                            </div>
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
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Vital Signs
                                </label>
                                <div className="mt-1 overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-md">
                                    <table className="min-w-full divide-y divide-gray-300">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th className="py-2 px-3 text-left text-xs font-medium text-gray-700">Parameter</th>
                                                <th className="py-2 px-3 text-left text-xs font-medium text-gray-700">Value</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-200 bg-white">
                                            <tr>
                                                <td className="py-2 px-3 text-sm text-gray-700">HR</td>
                                                <td className="py-2 px-3">
                                                    <input
                                                        type="text"
                                                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-1"
                                                        value={formData.vital_signs.hr}
                                                        onChange={(e) => handleVitalChange('hr', e.target.value)}
                                                        placeholder="Heart Rate"
                                                    />
                                                </td>
                                            </tr>
                                            <tr>
                                                <td className="py-2 px-3 text-sm text-gray-700">BP</td>
                                                <td className="py-2 px-3">
                                                    <input
                                                        type="text"
                                                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-1"
                                                        value={formData.vital_signs.bp}
                                                        onChange={(e) => handleVitalChange('bp', e.target.value)}
                                                        placeholder="Blood Pressure"
                                                    />
                                                </td>
                                            </tr>
                                            <tr>
                                                <td className="py-2 px-3 text-sm text-gray-700">RR</td>
                                                <td className="py-2 px-3">
                                                    <input
                                                        type="text"
                                                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-1"
                                                        value={formData.vital_signs.rr}
                                                        onChange={(e) => handleVitalChange('rr', e.target.value)}
                                                        placeholder="Respiratory Rate"
                                                    />
                                                </td>
                                            </tr>
                                            <tr>
                                                <td className="py-2 px-3 text-sm text-gray-700">TEMP</td>
                                                <td className="py-2 px-3">
                                                    <input
                                                        type="text"
                                                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-1"
                                                        value={formData.vital_signs.temp}
                                                        onChange={(e) => handleVitalChange('temp', e.target.value)}
                                                        placeholder="Temperature"
                                                    />
                                                </td>
                                            </tr>
                                            <tr>
                                                <td className="py-2 px-3 text-sm text-gray-700">RPO2</td>
                                                <td className="py-2 px-3">
                                                    <input
                                                        type="text"
                                                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-1"
                                                        value={formData.vital_signs.rpo2}
                                                        onChange={(e) => handleVitalChange('rpo2', e.target.value)}
                                                        placeholder="O2 Saturation"
                                                    />
                                                </td>
                                            </tr>
                                            <tr>
                                                <td className="py-2 px-3 text-sm text-gray-700">Other</td>
                                                <td className="py-2 px-3">
                                                    <input
                                                        type="text"
                                                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-1"
                                                        value={formData.vital_signs.other}
                                                        onChange={(e) => handleVitalChange('other', e.target.value)}
                                                        placeholder="Other significant vitals"
                                                    />
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Investigations
                                </label>
                                <div className="mt-1 overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-md">
                                    <table className="min-w-full divide-y divide-gray-300">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th className="py-2 px-3 text-left text-xs font-medium text-gray-700">Investigation</th>
                                                <th className="py-2 px-3 text-left text-xs font-medium text-gray-700">Result</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-200 bg-white">
                                            <tr>
                                                <td className="py-2 px-3 text-sm text-gray-700">CBC</td>
                                                <td className="py-2 px-3">
                                                    <input
                                                        type="text"
                                                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-1"
                                                        value={formData.investigations.cbc}
                                                        onChange={(e) => handleInvestigationChange('cbc', e.target.value)}
                                                        placeholder="Complete Blood Count"
                                                    />
                                                </td>
                                            </tr>
                                            <tr>
                                                <td className="py-2 px-3 text-sm text-gray-700">CMP</td>
                                                <td className="py-2 px-3">
                                                    <input
                                                        type="text"
                                                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-1"
                                                        value={formData.investigations.cmp}
                                                        onChange={(e) => handleInvestigationChange('cmp', e.target.value)}
                                                        placeholder="Comprehensive Metabolic Panel"
                                                    />
                                                </td>
                                            </tr>
                                            <tr>
                                                <td className="py-2 px-3 text-sm text-gray-700">Chest X-Ray</td>
                                                <td className="py-2 px-3">
                                                    <input
                                                        type="text"
                                                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-1"
                                                        value={formData.investigations.chest_xray}
                                                        onChange={(e) => handleInvestigationChange('chest_xray', e.target.value)}
                                                        placeholder="Chest X-Ray findings"
                                                    />
                                                </td>
                                            </tr>
                                            <tr>
                                                <td className="py-2 px-3 text-sm text-gray-700">ECG</td>
                                                <td className="py-2 px-3">
                                                    <input
                                                        type="text"
                                                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-1"
                                                        value={formData.investigations.ecg}
                                                        onChange={(e) => handleInvestigationChange('ecg', e.target.value)}
                                                        placeholder="ECG findings"
                                                    />
                                                </td>
                                            </tr>
                                            <tr>
                                                <td className="py-2 px-3 text-sm text-gray-700">Other</td>
                                                <td className="py-2 px-3">
                                                    <input
                                                        type="text"
                                                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-1"
                                                        value={formData.investigations.other}
                                                        onChange={(e) => handleInvestigationChange('other', e.target.value)}
                                                        placeholder="Other investigations"
                                                    />
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                                <div className="mt-2">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Other Significant Investigations
                                    </label>
                                    <textarea
                                        name="investigations_other"
                                        rows={2}
                                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                                        value={formData.investigations_other}
                                        onChange={handleChange}
                                        placeholder="Any other significant investigations or findings"
                                    />
                                </div>
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
        </div>
    );
};

export default NewConsultPage;
