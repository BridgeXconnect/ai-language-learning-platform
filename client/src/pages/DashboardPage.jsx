import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/auth_context';
import { FullPageLoading } from '../components/common/LoadingStates';

const DashboardPage = () => {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && user) {
      // Redirect users to their role-specific portal
      const roleRedirects = {
        'course_manager': '/course-manager',
        'sales': '/sales',
        'trainer': '/trainer',
        'student': '/student',
        'admin': '/course-manager' // Default admin to course manager view
      };

      const primaryRole = user.roles?.[0] || user.role;
      const redirectPath = roleRedirects[primaryRole] || '/course-manager';
      
      navigate(redirectPath, { replace: true });
    }
  }, [user, loading, navigate]);

  if (loading) {
    return <FullPageLoading message="Loading dashboard..." />;
  }

  // This should not be reached, but just in case
  return <FullPageLoading message="Redirecting to your dashboard..." />;
};

export default DashboardPage;