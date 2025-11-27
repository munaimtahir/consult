import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';

const PatientSearch = ({ onSelect, selectedPatient }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [debouncedSearch, setDebouncedSearch] = useState('');

    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(searchTerm);
        }, 500);
        return () => clearTimeout(timer);
    }, [searchTerm]);

    const { data: patients, isLoading } = useQuery({
        queryKey: ['patients', debouncedSearch],
        queryFn: async () => {
            if (!debouncedSearch) return [];
            const response = await apiClient.get(`/patients/?search=${debouncedSearch}`);
            return response.data.results || response.data;
        },
        enabled: !!debouncedSearch,
    });

    return (
        <div className="relative">
            <label className="block text-sm font-medium text-gray-700 mb-1">
                Patient Search
            </label>
            <div className="flex gap-2">
                <input
                    type="text"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                    placeholder="Search by Name or MRN..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </div>

            {isLoading && <div className="text-sm text-gray-500 mt-1">Searching...</div>}

            {patients && patients.length > 0 && !selectedPatient && (
                <ul className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                    {patients.map((patient) => (
                        <li
                            key={patient.id}
                            className="relative cursor-default select-none py-2 pl-3 pr-9 hover:bg-indigo-600 hover:text-white"
                            onClick={() => {
                                onSelect(patient);
                                setSearchTerm('');
                            }}
                        >
                            <div className="flex flex-col">
                                <span className="font-semibold">{patient.name}</span>
                                <span className="text-xs text-gray-500 hover:text-gray-200">
                                    MRN: {patient.mrn} | Age: {patient.age} | {patient.gender}
                                </span>
                            </div>
                        </li>
                    ))}
                </ul>
            )}

            {selectedPatient && (
                <div className="mt-2 p-3 bg-indigo-50 rounded-md border border-indigo-100 flex justify-between items-center">
                    <div>
                        <p className="font-medium text-indigo-900">{selectedPatient.name}</p>
                        <p className="text-sm text-indigo-700">MRN: {selectedPatient.mrn}</p>
                    </div>
                    <button
                        type="button"
                        onClick={() => onSelect(null)}
                        className="text-sm text-indigo-600 hover:text-indigo-800"
                    >
                        Change
                    </button>
                </div>
            )}
        </div>
    );
};

export default PatientSearch;
