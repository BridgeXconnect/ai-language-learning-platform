import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/auth_context';
import LoadingSpinner from './loading_spinner';

const ProtectedRoute = ({ children, allowedRoles = null, requireAuth = true }) => {
  const { user, isAuthenticated, isInitializing } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (isInitializing) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // If authentication is required but user is not authenticated
  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If specific roles are required, check if user has the required role
  if (allowedRoles && user) {
    const hasRequiredRole = allowedRoles.includes(user.role) || user.role === 'admin';
    
    if (!hasRequiredRole) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="max-w-md mx-auto">
              <div className="bg-white rounded-lg shadow-soft p-8">
                <div className="w-16 h-16 mx-auto mb-4 bg-error-100 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-error-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Access Denied</h3>
                <p className="text-gray-600 mb-4">
                  You don't have permission to access this page. 
                  {allowedRoles && (
                    <span className="block mt-2 text-sm">
                      Required roles: {allowedRoles.join(', ')}
                    </span>
                  )}
                </p>
                <button
                  onClick={() => window.history.back()}
                  className="btn-secondary"
                >
                  Go Back
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }
  }

  // User is authenticated and has required permissions
  return children;
};

export default ProtectedRoute;