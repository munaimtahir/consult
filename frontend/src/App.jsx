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
import DepartmentDashboardPage from './pages/admin/DepartmentDashboardPage';
import GlobalDashboardPage from './pages/admin/GlobalDashboardPage';

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

            {/* <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Layout>
                    <DashboardPage />
                  </Layout>
                </ProtectedRoute>
              }
            /> */}

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
              path="/admin"
              element={
                <ProtectedRoute>
                  <AdminRoute>
                    <Layout>
                      <AdminHomePage />
                    </Layout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            <Route
              path="/admin/users"
              element={
                <ProtectedRoute>
                  <AdminRoute requiredPermission="can_manage_users">
                    <Layout>
                      <AdminUsersPage />
                    </Layout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            <Route
              path="/admin/departments"
              element={
                <ProtectedRoute>
                  <AdminRoute requiredPermission="can_manage_departments">
                    <Layout>
                      <AdminDepartmentsPage />
                    </Layout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            <Route
              path="/admin/dashboards/department"
              element={
                <ProtectedRoute>
                  <AdminRoute requiredPermission="can_view_department_dashboard">
                    <Layout>
                      <DepartmentDashboardPage />
                    </Layout>
                  </AdminRoute>
                </ProtectedRoute>
              }
            />

            <Route
              path="/admin/dashboards/global"
              element={
                <ProtectedRoute>
                  <AdminRoute requiredPermission="can_view_global_dashboard">
                    <Layout>
                      <GlobalDashboardPage />
                    </Layout>
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
