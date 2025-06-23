import React, { createContext, useState, useEffect, useContext } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const queryClient = useQueryClient();

  // Check if user is logged in on app start
  useEffect(() => {
    const initializeAuth = () => {
      const storedUser = localStorage.getItem('user');
      
      if (storedUser) {
        try {
          setUser(JSON.parse(storedUser));
        } catch (error) {
          // Invalid stored user data, clear storage
          localStorage.removeItem('user');
        }
      }
      
      setIsInitializing(false);
    };

    initializeAuth();
  }, []);

  // Simplified login for demo
  const loginMutation = {
    mutate: async (credentials) => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const userData = {
        id: '1',
        email: credentials.email,
        name: credentials.email.split('@')[0],
        role: 'course_manager'
      };
      
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      toast.success(`Welcome back, ${userData.name}!`);
    },
    isPending: false
  };

  // Simplified mutations for demo
  const registerMutation = {
    mutate: async () => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('Registration successful! Please log in with your credentials.');
    },
    isPending: false
  };

  const logoutMutation = {
    mutate: () => {
      localStorage.removeItem('user');
      setUser(null);
      queryClient.clear();
      toast.success('Logged out successfully');
    },
    isPending: false
  };

  const updateProfileMutation = {
    mutate: async (userData) => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      const updatedUser = { ...user, ...userData };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
      toast.success('Profile updated successfully');
    },
    isPending: false
  };

  const forgotPasswordMutation = {
    mutate: async () => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('Password reset instructions sent to your email');
    },
    isPending: false
  };

  const resetPasswordMutation = {
    mutate: async () => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('Password reset successfully. Please log in with your new password.');
    },
    isPending: false
  };

  // Helper functions
  const login = async (credentials) => {
    try {
      await loginMutation.mutateAsync(credentials);
      return true;
    } catch (error) {
      return false;
    }
  };

  const register = async (userData) => {
    try {
      await registerMutation.mutateAsync(userData);
      return true;
    } catch (error) {
      return false;
    }
  };

  const logout = () => {
    logoutMutation.mutate();
  };

  const updateProfile = async (userData) => {
    try {
      await updateProfileMutation.mutateAsync(userData);
      return true;
    } catch (error) {
      return false;
    }
  };

  const forgotPassword = async (email) => {
    try {
      await forgotPasswordMutation.mutateAsync(email);
      return true;
    } catch (error) {
      return false;
    }
  };

  const resetPassword = async (token, password) => {
    try {
      await resetPasswordMutation.mutateAsync({ token, password });
      return true;
    } catch (error) {
      return false;
    }
  };

  // Check if user has specific role
  const hasRole = (role) => {
    if (!user) return false;
    if (user.role === 'admin') return true; // Admin has access to everything
    return user.role === role;
  };

  // Check if user has any of the specified roles
  const hasAnyRole = (roles) => {
    if (!user) return false;
    if (user.role === 'admin') return true;
    return roles.includes(user.role);
  };

  // Check if user is authenticated
  const isAuthenticated = !!user;

  // Loading states
  const isLoggingIn = loginMutation.isPending;
  const isRegistering = registerMutation.isPending;
  const isLoggingOut = logoutMutation.isPending;
  const isUpdatingProfile = updateProfileMutation.isPending;

  const value = {
    // User state
    user,
    isAuthenticated,
    isInitializing,
    
    // Actions
    login,
    register,
    logout,
    updateProfile,
    forgotPassword,
    resetPassword,
    
    // Utilities
    hasRole,
    hasAnyRole,
    
    // Loading states
    isLoggingIn,
    isRegistering,
    isLoggingOut,
    isUpdatingProfile,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};