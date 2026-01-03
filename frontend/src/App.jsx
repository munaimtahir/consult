import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './router/ProtectedRoute';
import AdminRoute from './router/AdminRoute';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ConsultListPage from './pages/ConsultListPage';
import ConsultDetailPage from './pages/ConsultDetailPage';
import NewConsultPage from './pages/NewConsultPage';

// Admin pages
import AdminHomePage from './pages/admin/AdminHomePage';
import AdminUsersPage from './pages/admin/AdminUsersPage';
import AdminDepartmentsPage from './pages/admin/AdminDepartmentsPage';
import DepartmentDetailPage from './pages/admin/DepartmentDetailPage';
import DepartmentDashboardPage from './pages/admin/DepartmentDashboardPage';
import GlobalDashboardPage from './pages/admin/GlobalDashboardPage';
import DoctorAnalyticsPage from './pages/admin/DoctorAnalyticsPage';
import AdminLayout from './components/admin/AdminLayout';

// Dashboard pages
import DashboardMasterPage from './pages/admin/DashboardMasterPage';
import DashboardAnalyticsPage from './pages/admin/DashboardAnalyticsPage';

// Students pages
import StudentsProgramsPage from './pages/admin/StudentsProgramsPage';
import StudentsBatchesPage from './pages/admin/StudentsBatchesPage';
import StudentsAcademicPeriodsPage from './pages/admin/StudentsAcademicPeriodsPage';

// Faculty pages
import FacultyDepartmentsPage from './pages/admin/FacultyDepartmentsPage';

// Attendance pages
import AttendanceOverviewPage from './pages/admin/AttendanceOverviewPage';
import AttendanceInputPage from './pages/admin/AttendanceInputPage';
import AttendanceReportPage from './pages/admin/AttendanceReportPage';

// Results pages
import ResultsOverviewPage from './pages/admin/ResultsOverviewPage';
import ResultsBatchWisePage from './pages/admin/ResultsBatchWisePage';
import ResultsAcademicPeriodPage from './pages/admin/ResultsAcademicPeriodPage';
import ResultsGradePage from './pages/admin/ResultsGradePage';
import ResultsAssessmentReportPage from './pages/admin/ResultsAssessmentReportPage';

// Finance pages
import FinanceDashboardPage from './pages/admin/FinanceDashboardPage';
import FinanceFeePlansPage from './pages/admin/FinanceFeePlansPage';
import FinanceVouchersPage from './pages/admin/FinanceVouchersPage';
import FinancePaymentReportPage from './pages/admin/FinancePaymentReportPage';

// Search page
import SearchPage from './pages/admin/SearchPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

/**
 * The main application component.
 *
 * This component sets up the application's routing, providers (QueryClient
 * and Auth), and defines the overall page structure.
 *
 * @returns {React.ReactElement} The rendered application component.
 */
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />

            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Layout>
                    <DashboardPage />
                  </Layout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/adminpanel/analytics/doctors"
              element={
                <ProtectedRoute>
                  <AdminRoute requiredPermission="can_view_global_dashboard">
                    <AdminLayout>
                      <DoctorAnalyticsPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            <Route
              path="/adminpanel/departments/:id"
              element={
                <ProtectedRoute>
                  <AdminRoute requiredPermission="can_manage_departments">
                    <AdminLayout>
                      <DepartmentDetailPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            <Route
              path="/consults"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ConsultListPage />
                  </Layout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/consults/new"
              element={
                <ProtectedRoute>
                  <Layout>
                    <NewConsultPage />
                  </Layout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/consults/:id"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ConsultDetailPage />
                  </Layout>
                </ProtectedRoute>
              }
            />

            {/* Admin Routes */}
            <Route
              path="/adminpanel"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <AdminHomePage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            <Route
              path="/adminpanel/users"
              element={
                <ProtectedRoute>
                  <AdminRoute requiredPermission="can_manage_users">
                    <AdminLayout>
                      <AdminUsersPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            <Route
              path="/adminpanel/departments"
              element={
                <ProtectedRoute>
                  <AdminRoute requiredPermission="can_manage_departments">
                    <AdminLayout>
                      <AdminDepartmentsPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            <Route
              path="/adminpanel/dashboards/department"
              element={
                <ProtectedRoute>
                  <AdminRoute requiredPermission="can_view_department_dashboard">
                    <AdminLayout>
                      <DepartmentDashboardPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            <Route
              path="/adminpanel/dashboards/global"
              element={
                <ProtectedRoute>
                  <AdminRoute requiredPermission="can_view_global_dashboard">
                    <AdminLayout>
                      <GlobalDashboardPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            {/* Dashboard Routes */}
            <Route
              path="/adminpanel/dashboard/master"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <DashboardMasterPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />
            <Route
              path="/adminpanel/dashboard/analytics"
              element={
                <ProtectedRoute>
                  <AdminRoute requiredPermission="can_view_global_dashboard">
                    <AdminLayout>
                      <DashboardAnalyticsPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            {/* Students Routes */}
            <Route
              path="/adminpanel/students/programs"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <StudentsProgramsPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />
            <Route
              path="/adminpanel/students/batches"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <StudentsBatchesPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />
            <Route
              path="/adminpanel/students/academic-periods"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <StudentsAcademicPeriodsPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            {/* Faculty Routes */}
            <Route
              path="/adminpanel/faculty/departments"
              element={
                <ProtectedRoute>
                  <AdminRoute requiredPermission="can_manage_departments">
                    <AdminLayout>
                      <FacultyDepartmentsPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            {/* Attendance Routes */}
            <Route
              path="/adminpanel/attendance/overview"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <AttendanceOverviewPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />
            <Route
              path="/adminpanel/attendance/input"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <AttendanceInputPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />
            <Route
              path="/adminpanel/attendance/report"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <AttendanceReportPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            {/* Results Routes */}
            <Route
              path="/adminpanel/results/overview"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <ResultsOverviewPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />
            <Route
              path="/adminpanel/results/batch-wise"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <ResultsBatchWisePage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />
            <Route
              path="/adminpanel/results/academic-period"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <ResultsAcademicPeriodPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />
            <Route
              path="/adminpanel/results/grade"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <ResultsGradePage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />
            <Route
              path="/adminpanel/results/assessment-report"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <ResultsAssessmentReportPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            {/* Finance Routes */}
            <Route
              path="/adminpanel/finance/dashboard"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <FinanceDashboardPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />
            <Route
              path="/adminpanel/finance/fee-plans"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <FinanceFeePlansPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />
            <Route
              path="/adminpanel/finance/vouchers"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <FinanceVouchersPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />
            <Route
              path="/adminpanel/finance/payment-report"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <FinancePaymentReportPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            {/* Search Route */}
            <Route
              path="/adminpanel/search"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <AdminLayout>
                      <SearchPage />
                    </AdminLayout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
