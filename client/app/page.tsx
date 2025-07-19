"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"
import { ThemeToggle } from "@/components/theme-toggle"
import { Building } from "lucide-react"

export default function HomePage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  // Consolidated useEffect to handle all navigation logic
  useEffect(() => {
    if (isLoading) {
      // Still loading, don't do anything yet
      return
    }

    if (!user) {
      // Not authenticated, redirect to login
      router.push("/login")
      return
    }

    // User is authenticated, check for role-based redirects
    if (user.roles.length > 0) {
      const roles = user.roles
      if (roles.includes("admin")) {
        // Admin can access all portals, stay on dashboard
        return
      } else if (roles.includes("sales")) {
        router.push("/sales")
      } else if (roles.includes("course_manager")) {
        router.push("/course-manager")
      } else if (roles.includes("trainer")) {
        router.push("/trainer")
      } else if (roles.includes("student")) {
        router.push("/student")
      }
    }
  }, [user, isLoading, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Building className="h-12 w-12 text-primary animate-pulse" />
          <div className="text-lg font-medium">Loading...</div>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Building className="h-12 w-12 text-primary" />
          <div className="text-lg font-medium">Redirecting to login...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex flex-col items-center gap-6">
          <div className="flex items-center gap-3 text-3xl font-bold text-primary">
            <Building className="h-10 w-10" />
            <span>AI Language Learning Platform</span>
          </div>
          <div className="text-center">
            <p className="text-xl text-muted-foreground mb-2">
              Welcome back, {user.first_name || user.username}!
            </p>
            <p className="text-sm text-muted-foreground mb-6">
              You are logged in with roles: {user.roles.join(", ")}
            </p>
            
            {user.roles.includes("admin") && (
              <div className="grid grid-cols-2 gap-4 mt-8">
                <button
                  onClick={() => router.push("/sales")}
                  className="flex flex-col items-center gap-2 p-6 border rounded-lg hover:bg-accent transition-colors"
                >
                  <Building className="h-8 w-8 text-blue-500" />
                  <span className="font-medium">Sales Portal</span>
                  <span className="text-sm text-muted-foreground">Manage course requests</span>
                </button>
                
                <button
                  onClick={() => router.push("/course-manager")}
                  className="flex flex-col items-center gap-2 p-6 border rounded-lg hover:bg-accent transition-colors"
                >
                  <Building className="h-8 w-8 text-green-500" />
                  <span className="font-medium">Course Manager</span>
                  <span className="text-sm text-muted-foreground">Create & manage courses</span>
                </button>
                
                <button
                  onClick={() => router.push("/trainer")}
                  className="flex flex-col items-center gap-2 p-6 border rounded-lg hover:bg-accent transition-colors"
                >
                  <Building className="h-8 w-8 text-purple-500" />
                  <span className="font-medium">Trainer Portal</span>
                  <span className="text-sm text-muted-foreground">Deliver courses & feedback</span>
                </button>
                
                <button
                  onClick={() => router.push("/student")}
                  className="flex flex-col items-center gap-2 p-6 border rounded-lg hover:bg-accent transition-colors"
                >
                  <Building className="h-8 w-8 text-orange-500" />
                  <span className="font-medium">Student Portal</span>
                  <span className="text-sm text-muted-foreground">Take courses & track progress</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
