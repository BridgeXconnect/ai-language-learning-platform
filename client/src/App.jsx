import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'react-hot-toast';

// Error Boundary
import ErrorBoundary from './components/common/ErrorBoundary';
import { FullPageLoading } from './components/common/LoadingStates';

// Auth
import { AuthProvider } from './context/auth_context';
import ProtectedRoute from './components/protected_route';

// Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import DashboardPage from './pages/DashboardPage';

// Portal Pages
import SalesPortal from './pages/sales/SalesPortal';
import CourseManagerPortal from './pages/course-manager/CourseManagerPortal';
import TrainerPortal from './pages/trainer/TrainerPortal';
import StudentPortal from './pages/student/StudentPortal';

// Components
import Layout from './components/layout_component';

// Create a client with error handling
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        // Don't retry for 4xx errors
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 2;
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      suspense: false,
      useErrorBoundary: (error) => {
        // Use error boundary for 5xx errors
        return error?.response?.status >= 500;
      },
    },
    mutations: {
      useErrorBoundary: false,
      retry: false,
    },
  },
});

// Lazy load components for better performance
const LazyLoginPage = React.lazy(() => import('./pages/auth/LoginPage'));
const LazyRegisterPage = React.lazy(() => import('./pages/auth/RegisterPage'));
const LazyDashboardPage = React.lazy(() => import('./pages/DashboardPage'));
const LazySalesPortal = React.lazy(() => import('./pages/sales/SalesPortal'));
const LazyCourseManagerPortal = React.lazy(() => import('./pages/course-manager/CourseManagerPortal'));
const LazyTrainerPortal = React.lazy(() => import('./pages/trainer/TrainerPortal'));
const LazyStudentPortal = React.lazy(() => import('./pages/student/StudentPortal'));

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <Router>
            <div className="min-h-screen bg-gray-50">
              <React.Suspense fallback={<FullPageLoading message="Loading application..." />}>
                <Routes>
                  {/* Public Routes */}
                  <Route 
                    path="/login" 
                    element={
                      <ErrorBoundary>
                        <LazyLoginPage />
                      </ErrorBoundary>
                    } 
                  />
                  <Route 
                    path="/register" 
                    element={
                      <ErrorBoundary>
                        <LazyRegisterPage />
                      </ErrorBoundary>
                    } 
                  />
                  
                  {/* Protected Routes */}
                  <Route path="/" element={
                    <ErrorBoundary>
                      <ProtectedRoute>
                        <Layout>
                          <LazyDashboardPage />
                        </Layout>
                      </ProtectedRoute>
                    </ErrorBoundary>
                  } />
                  
                  {/* Portal Routes */}
                  <Route path="/sales/*" element={
                    <ErrorBoundary>
                      <ProtectedRoute allowedRoles={['sales', 'admin']}>
                        <Layout>
                          <LazySalesPortal />
                        </Layout>
                      </ProtectedRoute>
                    </ErrorBoundary>
                  } />
                  
                  <Route path="/course-manager/*" element={
                    <ErrorBoundary>
                      <ProtectedRoute allowedRoles={['course_manager', 'admin']}>
                        <Layout>
                          <LazyCourseManagerPortal />
                        </Layout>
                      </ProtectedRoute>
                    </ErrorBoundary>
                  } />
                  
                  <Route path="/trainer/*" element={
                    <ErrorBoundary>
                      <ProtectedRoute allowedRoles={['trainer', 'admin']}>
                        <Layout>
                          <LazyTrainerPortal />
                        </Layout>
                      </ProtectedRoute>
                    </ErrorBoundary>
                  } />
                  
                  <Route path="/student/*" element={
                    <ErrorBoundary>
                      <ProtectedRoute allowedRoles={['student', 'admin']}>
                        <Layout>
                          <LazyStudentPortal />
                        </Layout>
                      </ProtectedRoute>
                    </ErrorBoundary>
                  } />
                  
                  {/* Fallback */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </React.Suspense>
            </div>
            
            {/* Global Components */}
            <Toaster 
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#FFFFFF',
                  color: '#374151',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                },
                success: {
                  duration: 3000,
                  iconTheme: {
                    primary: '#28A745',
                    secondary: '#fff',
                  },
                },
                error: {
                  duration: 5000,
                  iconTheme: {
                    primary: '#DC3545',
                    secondary: '#fff',
                  },
                },
              }}
            />
          </Router>
        </AuthProvider>
        
        {/* React Query Devtools */}
        {/* {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )} */}
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;