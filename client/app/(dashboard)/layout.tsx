"use client"

import { Sidebar } from "@/components/dashboard/sidebar"
import { Header } from "@/components/dashboard/header"
import { useAuth } from "@/contexts/auth-context"
import { redirect } from "next/navigation"
import { useEffect } from "react"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { user, isLoading } = useAuth()

  useEffect(() => {
    if (!isLoading && !user) {
      redirect("/login")
    }
  }, [user, isLoading])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="flex items-center justify-center min-h-screen">
          <div className="space-y-4 text-center">
            <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-muted-foreground">Loading your dashboard...</p>
          </div>
        </div>
      </div>
    )
  }

  if (!user) {
    return null // Will redirect
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="flex h-screen overflow-hidden">
        {/* Sidebar - Hidden on mobile, shown on desktop */}
        <Sidebar className="hidden md:flex" />
        
        {/* Main Content Area */}
        <div className="flex flex-col flex-1 overflow-hidden">
          {/* Header */}
          <Header />
          
          {/* Main Content */}
          <main className="flex-1 overflow-y-auto bg-gradient-to-br from-background via-background to-muted/20">
            <div className="container mx-auto p-4 md:p-6 lg:p-8 max-w-7xl">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
