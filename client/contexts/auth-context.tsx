"use client"

import React, { createContext, useContext, useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { authApi, testConnection } from "@/lib/api"
import { User } from "@/lib/types"
import { AUTH_TOKEN_KEY, REFRESH_TOKEN_KEY, UserRole } from "@/lib/config"
import { useToast } from "@/hooks/use-toast"

interface AuthContextType {
  user: User | null
  roles: UserRole[]
  isLoading: boolean
  login: (credentials: { email: string; password: string }) => Promise<void>
  register: (details: Record<string, string>) => Promise<void>
  logout: () => void
  hasRole: (role: UserRole) => boolean
  fetchWithAuth: (url: string, options?: RequestInit) => Promise<Response>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  const { toast } = useToast()

  // Check for existing auth on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Only check if we have a token
        const token = localStorage.getItem(AUTH_TOKEN_KEY)
        if (token) {
          const userData = await authApi.getProfile()
          setUser(userData)
        }
      } catch (error) {
        console.log("Auth check failed, user needs to login")
        // Clear any invalid tokens
        localStorage.removeItem(AUTH_TOKEN_KEY)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
      } finally {
        setIsLoading(false)
      }
    }

    // Add a small delay to prevent flash
    const timer = setTimeout(checkAuth, 100)
    return () => clearTimeout(timer)
  }, [])

  const login = async (credentials: { email: string; password: string }) => {
    console.log("🚀 Auth context login initiated")
    setIsLoading(true)
    
    try {
      console.log("📡 Attempting login API call...")
      const response = await authApi.login(credentials)
      console.log("✅ API login successful, user:", response.user)
      setUser(response.user)
      
      // Redirect based on user role
      const userRoles = response.user.roles
      console.log("👤 User roles:", userRoles)
      
      if (userRoles.includes(UserRole.SALES)) {
        console.log("🏢 Redirecting to sales portal")
        router.push("/sales")
      } else if (userRoles.includes(UserRole.COURSE_MANAGER)) {
        console.log("📚 Redirecting to course manager portal")
        router.push("/course-manager")
      } else if (userRoles.includes(UserRole.TRAINER)) {
        console.log("👨‍🏫 Redirecting to trainer portal")
        router.push("/trainer")
      } else if (userRoles.includes(UserRole.STUDENT)) {
        console.log("🎓 Redirecting to student portal")
        router.push("/student")
      } else {
        console.log("🏠 Redirecting to home")
        router.push("/")
      }
    } catch (error: any) {
      console.error("❌ Auth context login failed:", error)
      toast({
        variant: "destructive",
        title: "Login failed",
        description: error.message || "Please check your credentials and try again",
      })
      throw error
    } finally {
      console.log("🔄 Resetting loading state...")
      setIsLoading(false)
    }
  }

  const register = async (details: Record<string, string>) => {
    setIsLoading(true)
    try {
      await authApi.register(details)
      toast({
        title: "Registration successful",
        description: "You can now log in with your credentials",
      })
      router.push("/login")
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Registration failed",
        description: error.message || "Please check your details and try again",
      })
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      // Continue with logout even if API fails
    }
    
    setUser(null)
    router.push("/login")
  }

  const hasRole = (role: UserRole): boolean => {
    return user?.roles.includes(role) || false
  }

  const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
    const token = localStorage.getItem(AUTH_TOKEN_KEY)
    
    const headers = {
      ...options.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    }
    
    return fetch(url, { ...options, headers })
  }

  // Compute roles from user
  const roles = user?.roles || []

  return (
    <AuthContext.Provider
      value={{
        user,
        roles,
        isLoading,
        login,
        register,
        logout,
        hasRole,
        fetchWithAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  
  return context
}
