import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './router/ProtectedRoute';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ConsultListPage from './pages/ConsultListPage';
import ConsultDetailPage from './pages/ConsultDetailPage';
import NewConsultPage from './pages/NewConsultPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

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

            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
