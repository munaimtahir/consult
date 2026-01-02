import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { timetableAPI, departmentsAPI } from '../api';
import WeekGrid from '../components/timetable/WeekGrid';
import { useAuth } from '../hooks/useAuth';

/**
 * Timetable Week Editor Page
 * 
 * Allows users to create, edit, verify, and publish weekly timetables.
 */
export default function TimetableWeekEditor() {
    const { user } = useAuth();
    const queryClient = useQueryClient();
    const [selectedWeekId, setSelectedWeekId] = useState(null);
    const [selectedWeekStart, setSelectedWeekStart] = useState(null);

    // Fetch weeks list
    const { data: weeks, isLoading: weeksLoading } = useQuery({
        queryKey: ['timetable', 'weeks'],
        queryFn: () => timetableAPI.getWeeks(),
    });

    // Fetch selected week details
    const { data: weekData, isLoading: weekLoading } = useQuery({
        queryKey: ['timetable', 'week', selectedWeekId],
        queryFn: () => timetableAPI.getWeek(selectedWeekId),
        enabled: !!selectedWeekId,
    });

    // Fetch departments for dropdown
    const { data: departments } = useQuery({
        queryKey: ['departments'],
        queryFn: () => departmentsAPI.getDepartments(),
    });

    // Create next 4 weeks mutation
    const createNext4WeeksMutation = useMutation({
        mutationFn: () => timetableAPI.createNext4Weeks(),
        onSuccess: () => {
            queryClient.invalidateQueries(['timetable', 'weeks']);
        },
    });

    // Save grid mutation
    const saveGridMutation = useMutation({
        mutationFn: ({ weekId, rows, cells }) => timetableAPI.saveGrid(weekId, rows, cells),
        onSuccess: () => {
            queryClient.invalidateQueries(['timetable', 'week', selectedWeekId]);
        },
    });

    // Verify week mutation
    const verifyWeekMutation = useMutation({
        mutationFn: (weekId) => timetableAPI.verifyWeek(weekId),
        onSuccess: () => {
            queryClient.invalidateQueries(['timetable', 'week', selectedWeekId]);
            queryClient.invalidateQueries(['timetable', 'weeks']);
        },
    });

    // Publish week mutation
    const publishWeekMutation = useMutation({
        mutationFn: (weekId) => timetableAPI.publishWeek(weekId),
        onSuccess: () => {
            queryClient.invalidateQueries(['timetable', 'week', selectedWeekId]);
            queryClient.invalidateQueries(['timetable', 'weeks']);
        },
    });

    // Revert to draft mutation
    const revertToDraftMutation = useMutation({
        mutationFn: ({ weekId, reason }) => timetableAPI.revertToDraft(weekId, reason),
        onSuccess: () => {
            queryClient.invalidateQueries(['timetable', 'week', selectedWeekId]);
            queryClient.invalidateQueries(['timetable', 'weeks']);
        },
    });

    // Auto-select first week if available
    useEffect(() => {
        if (weeks && weeks.length > 0 && !selectedWeekId) {
            setSelectedWeekId(weeks[0].id);
            setSelectedWeekStart(weeks[0].week_start_date);
        }
    }, [weeks, selectedWeekId]);

    const handleCreateNext4Weeks = () => {
        if (window.confirm('Create the next 4 weeks? This will create draft weeks if they don\'t exist.')) {
            createNext4WeeksMutation.mutate();
        }
    };

    const handleSaveGrid = (rows, cells) => {
        if (!selectedWeekId) return;
        saveGridMutation.mutate({ weekId: selectedWeekId, rows, cells });
    };

    const handleVerify = () => {
        if (!selectedWeekId) return;
        if (window.confirm('Verify this week? It will become read-only except for HOD/Admin.')) {
            verifyWeekMutation.mutate(selectedWeekId);
        }
    };

    const handlePublish = () => {
        if (!selectedWeekId) return;
        if (window.confirm('Publish this week? This will generate session occurrences and lock the week.')) {
            publishWeekMutation.mutate(selectedWeekId);
        }
    };

    const handleRevertToDraft = () => {
        if (!selectedWeekId) return;
        const reason = window.prompt('Please provide a reason for reverting to draft:');
        if (reason) {
            revertToDraftMutation.mutate({ weekId: selectedWeekId, reason });
        }
    };

    const canEdit = weekData?.status === 'DRAFT' || 
                   (weekData?.status === 'VERIFIED' && (user?.is_admin_user || user?.is_hod)) ||
                   (weekData?.status === 'PUBLISHED' && (user?.is_admin_user || user?.is_hod));
    
    const canVerify = weekData?.status === 'DRAFT' && (user?.is_admin_user || user?.is_hod);
    const canPublish = weekData?.status === 'VERIFIED' && (user?.is_admin_user || user?.is_hod);
    const canRevert = (weekData?.status === 'VERIFIED' || weekData?.status === 'PUBLISHED') && 
                     (user?.is_admin_user || user?.is_hod);

    if (weeksLoading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-xl">Loading weeks...</div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-4">Timetable Editor</h1>
                
                {/* Week Selector */}
                <div className="flex items-center gap-4 mb-4">
                    <label className="text-sm font-medium text-gray-700">Select Week:</label>
                    <select
                        value={selectedWeekId || ''}
                        onChange={(e) => {
                            const weekId = parseInt(e.target.value);
                            setSelectedWeekId(weekId);
                            const week = weeks.find(w => w.id === weekId);
                            if (week) {
                                setSelectedWeekStart(week.week_start_date);
                            }
                        }}
                        className="px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                        <option value="">-- Select Week --</option>
                        {weeks?.map((week) => (
                            <option key={week.id} value={week.id}>
                                {new Date(week.week_start_date).toLocaleDateString()} - {week.status}
                            </option>
                        ))}
                    </select>
                    
                    <button
                        onClick={handleCreateNext4Weeks}
                        disabled={createNext4WeeksMutation.isLoading}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                        {createNext4WeeksMutation.isLoading ? 'Creating...' : 'Create Next 4 Weeks'}
                    </button>
                </div>

                {/* Status and Actions */}
                {weekData && (
                    <div className="flex items-center gap-4 mb-4">
                        <div className="px-3 py-1 rounded-full text-sm font-medium bg-gray-200 text-gray-800">
                            Status: {weekData.status}
                        </div>
                        
                        {canVerify && (
                            <button
                                onClick={handleVerify}
                                disabled={verifyWeekMutation.isLoading}
                                className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50"
                            >
                                Verify Week
                            </button>
                        )}
                        
                        {canPublish && (
                            <button
                                onClick={handlePublish}
                                disabled={publishWeekMutation.isLoading}
                                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
                            >
                                Publish Week
                            </button>
                        )}
                        
                        {canRevert && (
                            <button
                                onClick={handleRevertToDraft}
                                disabled={revertToDraftMutation.isLoading}
                                className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 disabled:opacity-50"
                            >
                                Revert to Draft
                            </button>
                        )}
                    </div>
                )}

                {/* Error Messages */}
                {(saveGridMutation.isError || verifyWeekMutation.isError || 
                  publishWeekMutation.isError || revertToDraftMutation.isError) && (
                    <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                        {saveGridMutation.error?.response?.data?.error ||
                         verifyWeekMutation.error?.response?.data?.error ||
                         publishWeekMutation.error?.response?.data?.error ||
                         revertToDraftMutation.error?.response?.data?.error ||
                         'An error occurred'}
                    </div>
                )}

                {/* Success Messages */}
                {(saveGridMutation.isSuccess || verifyWeekMutation.isSuccess || 
                  publishWeekMutation.isSuccess || revertToDraftMutation.isSuccess) && (
                    <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
                        Operation completed successfully!
                    </div>
                )}
            </div>

            {/* Week Grid */}
            {weekLoading ? (
                <div className="flex items-center justify-center h-64">
                    <div className="text-xl">Loading week data...</div>
                </div>
            ) : weekData ? (
                <WeekGrid
                    weekData={weekData}
                    departments={departments || []}
                    canEdit={canEdit}
                    onSave={handleSaveGrid}
                    isSaving={saveGridMutation.isLoading}
                />
            ) : (
                <div className="text-center py-12 text-gray-500">
                    Please select a week to view and edit
                </div>
            )}
        </div>
    );
}
