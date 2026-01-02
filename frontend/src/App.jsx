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
import TimetableWeekEditor from './pages/TimetableWeekEditor';

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

            <Route
              path="/timetable"
              element={
                <ProtectedRoute>
                  <Layout>
                    <TimetableWeekEditor />
                  </Layout>
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
