import { useState, useEffect } from 'react';

/**
 * WeekGrid Component
 * 
 * Displays and allows editing of the weekly timetable grid.
 * Landscape layout: rows (slots) × columns (days).
 */
export default function WeekGrid({ weekData, departments, canEdit, onSave, isSaving }) {
    const [rows, setRows] = useState([]);
    const [cells, setCells] = useState([]);
    const [hasChanges, setHasChanges] = useState(false);

    // Initialize data from weekData
    useEffect(() => {
        if (weekData) {
            // Sort rows by row_index
            const sortedRows = [...weekData.slot_rows].sort((a, b) => a.row_index - b.row_index);
            setRows(sortedRows);
            
            // Sort cells by day_of_week and row_index
            const sortedCells = [...weekData.cells].sort((a, b) => {
                if (a.day_of_week !== b.day_of_week) {
                    return a.day_of_week - b.day_of_week;
                }
                const aRowIndex = typeof a.slot_row === 'object' ? a.slot_row.row_index : a.slot_row;
                const bRowIndex = typeof b.slot_row === 'object' ? b.slot_row.row_index : b.slot_row;
                return aRowIndex - bRowIndex;
            });
            setCells(sortedCells);
            setHasChanges(false);
        }
    }, [weekData]);

    const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

    const handleRowTimeChange = (rowId, field, value) => {
        if (!canEdit) return;
        
        setRows(rows.map(row => 
            row.id === rowId ? { ...row, [field]: value || null } : row
        ));
        setHasChanges(true);
    };

    const handleCellChange = (cellId, field, value) => {
        if (!canEdit) return;
        
        setCells(cells.map(cell => 
            cell.id === cellId ? { ...cell, [field]: value } : cell
        ));
        setHasChanges(true);
    };

    const handleSave = () => {
        if (!hasChanges || !onSave) return;
        
        // Prepare rows data
        const rowsData = rows.map(row => ({
            id: row.id,
            start_time: row.start_time || null,
            end_time: row.end_time || null,
        }));

        // Prepare cells data
        const cellsData = cells.map(cell => ({
            id: cell.id,
            department_id: cell.department?.id || cell.department_id || null,
            topic: cell.topic || '',
            faculty_name: cell.faculty_name || '',
            status: cell.status || 'SCHEDULED',
        }));

        onSave(rowsData, cellsData);
        setHasChanges(false);
    };

    // Get cell for a specific row and day
    const getCell = (rowId, dayOfWeek) => {
        return cells.find(cell => {
            const cellRowId = typeof cell.slot_row === 'object' ? cell.slot_row.id : cell.slot_row;
            return cellRowId === rowId && cell.day_of_week === dayOfWeek;
        });
    };

    if (!weekData || rows.length === 0) {
        return <div className="text-center py-8 text-gray-500">No data available</div>;
    }

    return (
        <div className="overflow-x-auto">
            <div className="mb-4 flex justify-between items-center">
                <h2 className="text-xl font-semibold">
                    Week: {new Date(weekData.week_start_date).toLocaleDateString()} - {new Date(weekData.week_end_date).toLocaleDateString()}
                </h2>
                {canEdit && (
                    <button
                        onClick={handleSave}
                        disabled={!hasChanges || isSaving}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isSaving ? 'Saving...' : hasChanges ? 'Save Changes' : 'No Changes'}
                    </button>
                )}
            </div>

            <div className="bg-white border border-gray-300 rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">
                                Slot / Time
                            </th>
                            {dayNames.map((day, index) => (
                                <th key={index} className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    {day}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {rows.map((row) => (
                            <tr key={row.id} className="hover:bg-gray-50">
                                {/* Row header with time inputs */}
                                <td className="px-4 py-3 whitespace-nowrap bg-gray-50">
                                    <div className="space-y-2">
                                        <div className="text-sm font-medium text-gray-900">
                                            Slot {row.row_index}
                                        </div>
                                        {canEdit ? (
                                            <div className="space-y-1">
                                                <input
                                                    type="time"
                                                    value={row.start_time || ''}
                                                    onChange={(e) => handleRowTimeChange(row.id, 'start_time', e.target.value)}
                                                    className="w-full px-2 py-1 text-xs border border-gray-300 rounded"
                                                />
                                                <input
                                                    type="time"
                                                    value={row.end_time || ''}
                                                    onChange={(e) => handleRowTimeChange(row.id, 'end_time', e.target.value)}
                                                    className="w-full px-2 py-1 text-xs border border-gray-300 rounded"
                                                />
                                            </div>
                                        ) : (
                                            <div className="text-xs text-gray-600">
                                                {row.start_time && row.end_time ? (
                                                    <>
                                                        {row.start_time} - {row.end_time}
                                                    </>
                                                ) : (
                                                    'No time set'
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </td>

                                {/* Cells for each day */}
                                {dayNames.map((day, dayIndex) => {
                                    const cell = getCell(row.id, dayIndex);
                                    if (!cell) return <td key={dayIndex} className="px-4 py-3"></td>;

                                    return (
                                        <td key={dayIndex} className="px-4 py-3 border-l border-gray-200">
                                            <div className="space-y-2 min-h-[120px]">
                                                {/* Department Dropdown */}
                                                {canEdit ? (
                                                    <select
                                                        value={cell.department?.id || cell.department_id || ''}
                                                        onChange={(e) => handleCellChange(cell.id, 'department_id', e.target.value ? parseInt(e.target.value) : null)}
                                                        className="w-full px-2 py-1 text-xs border border-gray-300 rounded"
                                                    >
                                                        <option value="">-- Select Department --</option>
                                                        {departments.map((dept) => (
                                                            <option key={dept.id} value={dept.id}>
                                                                {dept.name}
                                                            </option>
                                                        ))}
                                                    </select>
                                                ) : (
                                                    <div className="text-xs font-medium text-gray-700">
                                                        {cell.department?.name || 'No Department'}
                                                    </div>
                                                )}

                                                {/* Topic Input */}
                                                {canEdit ? (
                                                    <input
                                                        type="text"
                                                        placeholder="Topic"
                                                        value={cell.topic || ''}
                                                        onChange={(e) => handleCellChange(cell.id, 'topic', e.target.value)}
                                                        className="w-full px-2 py-1 text-xs border border-gray-300 rounded"
                                                    />
                                                ) : (
                                                    cell.topic && (
                                                        <div className="text-xs text-gray-600">
                                                            <strong>Topic:</strong> {cell.topic}
                                                        </div>
                                                    )
                                                )}

                                                {/* Faculty Name Input */}
                                                {canEdit ? (
                                                    <input
                                                        type="text"
                                                        placeholder="Faculty Name"
                                                        value={cell.faculty_name || ''}
                                                        onChange={(e) => handleCellChange(cell.id, 'faculty_name', e.target.value)}
                                                        className="w-full px-2 py-1 text-xs border border-gray-300 rounded"
                                                    />
                                                ) : (
                                                    cell.faculty_name && (
                                                        <div className="text-xs text-gray-600">
                                                            <strong>Faculty:</strong> {cell.faculty_name}
                                                        </div>
                                                    )
                                                )}

                                                {/* Status Badge */}
                                                {cell.status === 'CANCELLED' && (
                                                    <div className="text-xs text-red-600 font-medium">
                                                        Cancelled
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                    );
                                })}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {hasChanges && canEdit && (
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded text-yellow-800 text-sm">
                    You have unsaved changes. Click "Save Changes" to save.
                </div>
            )}
        </div>
    );
}
