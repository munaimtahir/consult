import { useAuth } from '../hooks/useAuth';
import { useDashboardStats } from '../hooks/useConsults';
import { Link } from 'react-router-dom';

/**
 * Renders the main dashboard page.
 *
 * This component displays a welcome message and a summary of consult
 * statistics for the current user, categorized by department, assigned to
 * the user, and requested by the user. It also provides quick links to
 * filtered views of the consults list.
 *
 * @returns {React.ReactElement} The rendered dashboard page component.
 */
export default function DashboardPage() {
    const { user } = useAuth();
    const { data: stats, isLoading } = useDashboardStats();

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-xl">Loading...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                    <p className="text-gray-600 mt-2">
                        Welcome back, {user?.first_name || user?.email}
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    {/* My Department Stats */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">My Department</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Pending</span>
                                <span className="font-bold text-yellow-600">
                                    {stats?.my_department?.pending || 0}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">In Progress</span>
                                <span className="font-bold text-blue-600">
                                    {stats?.my_department?.in_progress || 0}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Overdue</span>
                                <span className="font-bold text-red-600">
                                    {stats?.my_department?.overdue || 0}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Assigned to Me */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Assigned to Me</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Pending</span>
                                <span className="font-bold text-yellow-600">
                                    {stats?.assigned_to_me?.pending || 0}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">In Progress</span>
                                <span className="font-bold text-blue-600">
                                    {stats?.assigned_to_me?.in_progress || 0}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Overdue</span>
                                <span className="font-bold text-red-600">
                                    {stats?.assigned_to_me?.overdue || 0}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* My Requests */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">My Requests</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Pending</span>
                                <span className="font-bold text-yellow-600">
                                    {stats?.my_requests?.pending || 0}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">In Progress</span>
                                <span className="font-bold text-blue-600">
                                    {stats?.my_requests?.in_progress || 0}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Completed</span>
                                <span className="font-bold text-green-600">
                                    {stats?.my_requests?.completed || 0}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <Link
                            to="/consults?view=my_department"
                            className="p-4 border-2 border-blue-200 rounded-lg hover:border-blue-400 transition-colors text-center"
                        >
                            <div className="text-blue-600 font-semibold">View Department Consults</div>
                        </Link>
                        <Link
                            to="/consults?view=assigned_to_me"
                            className="p-4 border-2 border-green-200 rounded-lg hover:border-green-400 transition-colors text-center"
                        >
                            <div className="text-green-600 font-semibold">View My Consults</div>
                        </Link>
                        <Link
                            to="/consults?view=my_requests"
                            className="p-4 border-2 border-purple-200 rounded-lg hover:border-purple-400 transition-colors text-center"
                        >
                            <div className="text-purple-600 font-semibold">View My Requests</div>
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
