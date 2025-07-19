import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await api.get('/dashboard');
        setMessage(response.data.message);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        setMessage('Failed to load dashboard content.');
        // Handle token expiry or invalid token
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          logout(); // Log out if token is invalid/expired
          navigate('/login');
        }
      }
    };
    fetchDashboardData();
  }, [logout, navigate]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) {
    return <div>Redirecting...</div>; // Should be handled by ProtectedRoute
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-2xl text-center">
      <h2 className="text-3xl font-bold mb-4 text-gray-800">Welcome, {user.username}!</h2>
      <p className="text-gray-700 text-lg mb-6">{message}</p>
      <button
        onClick={handleLogout}
        className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
      >
        Logout
      </button>
    </div>
  );
}

export default DashboardPage;