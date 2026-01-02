import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { getDefaulters, getCollectionReport } from '../../api/finance';

export default function FinanceDashboardPage() {
  const { data: defaulters, isLoading: defaultersLoading } = useQuery({
    queryKey: ['finance', 'defaulters'],
    queryFn: () => getDefaulters().then(res => res.data),
  });

  const { data: collection, isLoading: collectionLoading } = useQuery({
    queryKey: ['finance', 'collection'],
    queryFn: () => getCollectionReport().then(res => res.data),
  });

  if (defaultersLoading || collectionLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  const totalOutstanding = defaulters?.reduce((sum, d) => sum + parseFloat(d.total_outstanding || 0), 0) || 0;
  const totalCollection = parseFloat(collection?.total_collection || 0);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Finance Dashboard</h1>
          <p className="text-gray-600 mt-2">Financial overview and quick actions</p>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Outstanding</h3>
            <p className="text-3xl font-bold text-red-600">{totalOutstanding.toLocaleString()} PKR</p>
            <p className="text-sm text-gray-500 mt-2">{defaulters?.length || 0} defaulters</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Collected</h3>
            <p className="text-3xl font-bold text-green-600">{totalCollection.toLocaleString()} PKR</p>
            <p className="text-sm text-gray-500 mt-2">{collection?.total_count || 0} payments</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Defaulters</h3>
            <p className="text-3xl font-bold text-orange-600">{defaulters?.length || 0}</p>
            <p className="text-sm text-gray-500 mt-2">Students with outstanding dues</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              to="/finance/vouchers/generate"
              className="px-4 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-center"
            >
              Generate Vouchers
            </Link>
            <Link
              to="/finance/payments/new"
              className="px-4 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 text-center"
            >
              Record Payment
            </Link>
            <Link
              to="/finance/defaulters"
              className="px-4 py-3 bg-orange-600 text-white rounded-md hover:bg-orange-700 text-center"
            >
              View Defaulters
            </Link>
          </div>
        </div>

        {/* Recent Defaulters */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Defaulters</h2>
          {defaulters && defaulters.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Program</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Outstanding</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {defaulters.slice(0, 10).map((defaulter) => (
                    <tr key={defaulter.student_id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{defaulter.student_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{defaulter.student_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{defaulter.program || 'N/A'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-red-600">
                        {parseFloat(defaulter.total_outstanding).toLocaleString()} PKR
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <Link
                          to={`/finance/students/${defaulter.student_id}/summary`}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          View Details
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500">No defaulters found</p>
          )}
        </div>
      </div>
    </div>
  );
}
