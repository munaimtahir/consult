import { useMemo } from 'react';
import { useTable, useSortBy } from 'react-table';

export default function DoctorAnalyticsTable({ data }) {

    const columns = useMemo(
        () => [
            {
                Header: 'Doctor',
                accessor: 'full_name',
            },
            {
                Header: 'Total Consults',
                accessor: 'total_consults',
            },
            {
                Header: 'Avg. Ack. Time (hours)',
                accessor: 'avg_acknowledgment_time',
                Cell: ({ value }) => (value ? (value / 3600).toFixed(2) : '-'),
            },
            {
                Header: 'Avg. Comp. Time (hours)',
                accessor: 'avg_completion_time',
                Cell: ({ value }) => (value ? (value / 3600).toFixed(2) : '-'),
            },
            {
                Header: 'Pending Workload',
                accessor: 'pending_workload',
            },
            {
                Header: 'Escalations Handled',
                accessor: 'escalations_handled',
            },
            {
                Header: 'Delayed Consults',
                accessor: 'delayed_consults',
            },
        ],
        []
    );

    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        rows,
        prepareRow,
    } = useTable({ columns, data }, useSortBy);

    return (
        <div className="bg-white rounded-lg shadow">
            <table {...getTableProps()} className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                    {headerGroups.map(headerGroup => (
                        <tr {...headerGroup.getHeaderGroupProps()}>
                            {headerGroup.headers.map(column => (
                                <th
                                    {...column.getHeaderProps(column.getSortByToggleProps())}
                                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                >
                                    {column.render('Header')}
                                    <span>
                                        {column.isSorted
                                            ? column.isSortedDesc
                                                ? ' 🔽'
                                                : ' 🔼'
                                            : ''}
                                    </span>
                                </th>
                            ))}
                        </tr>
                    ))}
                </thead>
                <tbody {...getTableBodyProps()} className="bg-white divide-y divide-gray-200">
                    {rows.map(row => {
                        prepareRow(row);
                        return (
                            <tr {...row.getRowProps()}>
                                {row.cells.map(cell => {
                                    return (
                                        <td
                                            {...cell.getCellProps()}
                                            className="px-6 py-4 whitespace-nowrap"
                                        >
                                            {cell.render('Cell')}
                                        </td>
                                    );
                                })}
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}
