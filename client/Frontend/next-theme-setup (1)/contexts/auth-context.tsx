"use client"

import React, { createContext, useContext, useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { authApi } from "@/lib/api"
import { User } from "@/lib/types"
import { UserRole } from "@/lib/config"
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
        const userData = await authApi.getProfile()
        setUser(userData)
      } catch (error) {
        // Silent fail on initial load
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = async (credentials: { email: string; password: string }) => {
    setIsLoading(true)
    try {
      const response = await authApi.login(credentials)
      setUser(response.user)
      
      // Redirect based on user role
      if (response.user.roles.includes(UserRole.SALES)) {
        router.push("/sales")
      } else if (response.user.roles.includes(UserRole.COURSE_MANAGER)) {
        router.push("/course-manager")
      } else if (response.user.roles.includes(UserRole.TRAINER)) {
        router.push("/trainer")
      } else if (response.user.roles.includes(UserRole.STUDENT)) {
        router.push("/student")
      } else {
        router.push("/")
      }
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Login failed",
        description: error.message || "Please check your credentials and try again",
      })
      throw error
    } finally {
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
    const token = localStorage.getItem("auth_token")
    
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
