"use client" // Required for hooks like useAuth, usePathname

import type React from "react"
import { Sidebar } from "@/components/dashboard/sidebar"
import { Header } from "@/components/dashboard/header"
import { useAuth } from "@/contexts/auth-context"
import { useRouter, usePathname } from "next/navigation"
import { useEffect } from "react"
import { UserRole } from "@/lib/config"

// Define allowed routes for each role
const roleRoutes: Record<UserRole, string[]> = {
  [UserRole.SALES]: ["/", "/sales", "/settings"],
  [UserRole.COURSE_MANAGER]: ["/", "/course-manager", "/content-library", "/settings"],
  [UserRole.TRAINER]: ["/", "/trainer", "/content-library", "/settings"],
  [UserRole.STUDENT]: ["/", "/student", "/settings"],
  [UserRole.ADMIN]: Object.values(UserRole)
    .map((role) => `/${role}`)
    .concat(["/", "/settings", "/content-library"]), // Admin can access all
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { user, isLoading, hasRole } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (!isLoading && !user) {
      router.replace("/login")
    } else if (!isLoading && user) {
      // Basic route protection: redirect if user tries to access a page not allowed for their role
      // This is a simplified check. More robust checking would involve checking the base path.
      const currentBaseRoute = pathname.split("/")[1] || "" // e.g. "sales" from "/sales/requests"

      let isAuthorized = false
      if (currentBaseRoute === "") {
        // Root dashboard page
        isAuthorized = true
      } else if (user.roles.includes(UserRole.ADMIN)) {
        isAuthorized = true
      } else {
        for (const role of user.roles) {
          const roleKey = role as UserRole
          if (roleRoutes[roleKey]?.some((allowedPath) => pathname.startsWith(allowedPath) && allowedPath !== "/")) {
            isAuthorized = true
            break
          } else if (roleRoutes[roleKey]?.includes(pathname)) {
            // For exact matches like "/" or "/settings"
            isAuthorized = true
            break
          }
        }
      }

      if (!isAuthorized && pathname !== "/login" && pathname !== "/register") {
        // Redirect to their primary dashboard or a generic access denied page
        if (hasRole(UserRole.SALES)) router.replace("/sales")
        else if (hasRole(UserRole.COURSE_MANAGER)) router.replace("/course-manager")
        // ... add other roles
        else router.replace("/") // Fallback to overview
      }
    }
  }, [user, isLoading, router, pathname, hasRole])

  if (isLoading || !user) {
    return (
      <div className="flex h-screen items-center justify-center">
        {/* Replace with a proper skeleton loader or spinner */}
        <p>Loading application...</p>
      </div>
    )
  }

  return (
    <div className="grid min-h-screen w-full md:grid-cols-[auto_1fr] lg:grid-cols-[auto_1fr]">
      <Sidebar />
      <div className="flex flex-col">
        <Header />
        <main className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6 bg-muted/40">{children}</main>
      </div>
    </div>
  )
}
