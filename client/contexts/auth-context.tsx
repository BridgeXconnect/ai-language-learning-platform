/**
 * Production-Ready Authentication Context
 * Secure session management with proper error handling
 */

"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { authService, healthService } from "@/lib/api-services";
import { apiClient } from "@/lib/api-client";
import { tokenManager, TokenPair } from "@/lib/token-manager";
import { User, isValidUser } from "@/lib/types";
import { UserRole } from "@/lib/config";
import { shouldEnableDebugLogs } from "@/lib/env";
import {
  AppError,
  createAuthError,
  createNetworkError,
  ErrorLogger,
  setupGlobalErrorHandler,
} from "@/lib/errors";
import { useToast } from "@/hooks/use-toast";

export interface AuthContextType {
  // State
  user: User | null;
  roles: UserRole[];
  isLoading: boolean;
  isAuthenticated: boolean;
  
  // Actions
  login: (credentials: { email: string; password: string }) => Promise<void>;
  register: (userData: {
    email: string;
    password: string;
    username: string;
    first_name?: string;
    last_name?: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  
  // Utilities
  hasRole: (role: UserRole) => boolean;
  hasAnyRole: (roles: UserRole[]) => boolean;
  checkPermission: (permission: string) => boolean;
  
  // Legacy compatibility (temporary)
  fetchWithAuth: (url: string, options?: RequestInit) => Promise<Response>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [initializationError, setInitializationError] = useState<string | null>(null);
  
  const router = useRouter();
  const { toast } = useToast();

  // Setup global error handling
  useEffect(() => {
    setupGlobalErrorHandler();
  }, []);

  // Initialize authentication state
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = useCallback(async () => {
    try {
      setIsLoading(true);
      setInitializationError(null);

      if (shouldEnableDebugLogs) {
        console.log('🔍 Initializing authentication...');
      }

      // Check backend connectivity with fallback validation
      const isHealthy = await healthService.validateConnectivity();
      if (!isHealthy) {
        const healthDetails = await healthService.getHealthDetails();
        setInitializationError(
          `Backend service is not available at ${healthDetails.url}. Please ensure the backend server is running.`
        );
        if (shouldEnableDebugLogs) {
          console.warn('⚠️ Backend connectivity validation failed:', healthDetails);
        }
        return;
      }

      // Check if we have valid tokens
      if (!tokenManager.hasTokens()) {
        if (shouldEnableDebugLogs) {
          console.log('📭 No existing tokens found');
        }
        return;
      }

      // Validate access token
      const validation = tokenManager.validateAccessToken();
      if (!validation.isValid) {
        if (shouldEnableDebugLogs) {
          console.log('🔄 Access token invalid, attempting refresh...');
        }
        
        try {
          await authService.refreshTokens();
          if (shouldEnableDebugLogs) {
            console.log('✅ Tokens refreshed successfully');
          }
        } catch (error) {
          if (shouldEnableDebugLogs) {
            console.log('❌ Token refresh failed, clearing tokens');
          }
          tokenManager.clearTokens();
          return;
        }
      }

      // Fetch user profile
      try {
        const userData = await authService.getProfile();
        
        if (isValidUser(userData)) {
          setUser(userData);
          if (shouldEnableDebugLogs) {
            console.log('✅ User authenticated successfully:', {
              id: userData.id,
              username: userData.username,
              roles: userData.roles,
            });
          }
        } else {
          throw createAuthError('Invalid user data received from server');
        }
      } catch (error) {
        if (shouldEnableDebugLogs) {
          console.log('❌ Profile fetch failed:', error);
        }
        
        if (error instanceof AppError && error.statusCode === 401) {
          // Token is invalid, clear it
          tokenManager.clearTokens();
        } else {
          // Other errors might be temporary
          ErrorLogger.log(error instanceof AppError ? error : createNetworkError(String(error)));
        }
      }
    } catch (error) {
      const authError = createAuthError(`Authentication initialization failed: ${error}`);
      ErrorLogger.log(authError);
      setInitializationError(authError.userMessage);
    } finally {
      setIsLoading(false);
      if (shouldEnableDebugLogs) {
        console.log('🏁 Authentication initialization completed');
      }
    }
  }, []);

  const login = useCallback(async (credentials: { email: string; password: string }) => {
    try {
      setIsLoading(true);
      
      if (shouldEnableDebugLogs) {
        console.log('🔐 Starting login process...');
      }

      const { user: userData } = await authService.login(credentials);
      
      if (!isValidUser(userData)) {
        throw createAuthError('Invalid user data received from login');
      }

      setUser(userData);
      
      if (shouldEnableDebugLogs) {
        console.log('✅ Login successful:', {
          id: userData.id,
          username: userData.username,
          roles: userData.roles,
        });
      }

      // Navigate based on user role
      redirectAfterLogin(userData.roles);
      
      toast({
        title: "Login successful",
        description: `Welcome back, ${userData.username}!`,
      });
    } catch (error) {
      const authError = error instanceof AppError 
        ? error 
        : createAuthError(`Login failed: ${error}`);
      
      ErrorLogger.log(authError);
      
      toast({
        variant: "destructive",
        title: "Login failed",
        description: authError.userMessage,
      });
      
      throw authError;
    } finally {
      setIsLoading(false);
    }
  }, [router, toast]);

  const register = useCallback(async (userData: {
    email: string;
    password: string;
    username: string;
    first_name?: string;
    last_name?: string;
  }) => {
    try {
      setIsLoading(true);
      
      if (shouldEnableDebugLogs) {
        console.log('📝 Starting registration process...');
      }

      await authService.register(userData);
      
      toast({
        title: "Registration successful",
        description: "You can now log in with your credentials.",
      });
      
      router.push("/login");
    } catch (error) {
      const authError = error instanceof AppError 
        ? error 
        : createAuthError(`Registration failed: ${error}`);
      
      ErrorLogger.log(authError);
      
      toast({
        variant: "destructive",
        title: "Registration failed",
        description: authError.userMessage,
      });
      
      throw authError;
    } finally {
      setIsLoading(false);
    }
  }, [router, toast]);

  const logout = useCallback(async () => {
    try {
      if (shouldEnableDebugLogs) {
        console.log('🚪 Starting logout process...');
      }

      await authService.logout();
      setUser(null);
      
      toast({
        title: "Logged out",
        description: "You have been successfully logged out.",
      });
      
      router.push("/login");
    } catch (error) {
      // Even if logout API fails, clear local state
      setUser(null);
      tokenManager.clearTokens();
      
      if (shouldEnableDebugLogs) {
        console.warn('⚠️ Logout API failed, but local state cleared:', error);
      }
      
      router.push("/login");
    }
  }, [router, toast]);

  const refreshUser = useCallback(async () => {
    try {
      if (!tokenManager.hasTokens()) {
        setUser(null);
        return;
      }

      const userData = await authService.getProfile();
      
      if (isValidUser(userData)) {
        setUser(userData);
        if (shouldEnableDebugLogs) {
          console.log('🔄 User data refreshed');
        }
      } else {
        throw createAuthError('Invalid user data received');
      }
    } catch (error) {
      if (error instanceof AppError && error.statusCode === 401) {
        // Authentication failed, clear state
        setUser(null);
        tokenManager.clearTokens();
      } else {
        ErrorLogger.log(error instanceof AppError ? error : createNetworkError(String(error)));
      }
    }
  }, []);

  const hasRole = useCallback((role: UserRole): boolean => {
    return user?.roles.includes(role) || false;
  }, [user]);

  const hasAnyRole = useCallback((roles: UserRole[]): boolean => {
    return roles.some(role => hasRole(role));
  }, [hasRole]);

  const checkPermission = useCallback((permission: string): boolean => {
    // Implement permission checking logic here
    // For now, just check if user is authenticated
    return !!user;
  }, [user]);

  const redirectAfterLogin = (userRoles: string[]) => {
    const roles = userRoles.map(role => role.toLowerCase());
    
    if (roles.includes('sales')) {
      router.push('/sales');
    } else if (roles.includes('course_manager')) {
      router.push('/course-manager');
    } else if (roles.includes('trainer')) {
      router.push('/trainer');
    } else if (roles.includes('student')) {
      router.push('/student');
    } else if (roles.includes('admin')) {
      router.push('/admin');
    } else {
      router.push('/');
    }
  };

  // Legacy compatibility method - temporary until all components migrated
  const fetchWithAuth = useCallback(async (url: string, options?: RequestInit): Promise<Response> => {
    const token = tokenManager.getAccessToken();
    return fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options?.headers,
      },
    });
  }, []);

  const contextValue: AuthContextType = {
    // State
    user,
    roles: (user?.roles || []) as UserRole[],
    isLoading,
    isAuthenticated: !!user,
    
    // Actions
    login,
    register,
    logout,
    refreshUser,
    
    // Utilities
    hasRole,
    hasAnyRole,
    checkPermission,
    
    // Legacy compatibility (temporary)
    fetchWithAuth,
  };

  // Show initialization error if backend is not available
  if (initializationError && !isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
              <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Service Unavailable</h3>
            <p className="mt-1 text-sm text-gray-500">{initializationError}</p>
            <div className="mt-6">
              <button
                type="button"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                onClick={() => window.location.reload()}
              >
                Retry Connection
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  
  return context;
}