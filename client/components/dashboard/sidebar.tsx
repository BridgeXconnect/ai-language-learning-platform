"use client"

import Link from "next/link"
import {
  LayoutDashboard,
  Users,
  BookOpen,
  GraduationCap,
  Briefcase,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Building,
  Bot,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/contexts/auth-context"
import { UserRole } from "packages/shared/constants"
import { SidebarNavItem } from "./sidebar-nav-item"
import { useState } from "react"
import { cn } from "@/lib/utils"
import { ThemeSwitcher } from "@/components/theme-switcher" // Assuming you have this

export function Sidebar() {
  const { user, hasRole, logout } = useAuth()
  const [isCollapsed, setIsCollapsed] = useState(false)

  const navItems = [
    { href: "/", icon: LayoutDashboard, label: "Overview", roles: Object.values(UserRole) },
    { href: "/sales", icon: Briefcase, label: "Sales Portal", roles: [UserRole.SALES, UserRole.ADMIN] },
    {
      href: "/course-manager",
      icon: Bot,
      label: "Course Management",
      roles: [UserRole.COURSE_MANAGER, UserRole.ADMIN],
    },
    { href: "/trainer", icon: Users, label: "Trainer Portal", roles: [UserRole.TRAINER, UserRole.ADMIN] },
    { href: "/student", icon: GraduationCap, label: "My Learning", roles: [UserRole.STUDENT] },
    {
      href: "/content-library",
      icon: BookOpen,
      label: "Content Library",
      roles: [UserRole.COURSE_MANAGER, UserRole.TRAINER, UserRole.ADMIN],
    },
  ]

  const bottomNavItems = [{ href: "/settings", icon: Settings, label: "Settings", roles: Object.values(UserRole) }]

  if (!user) return null

  return (
    <div
      className={cn(
        "hidden border-r bg-card md:flex flex-col transition-all duration-300 ease-in-out",
        isCollapsed ? "w-20" : "w-64",
      )}
    >
      <div className="flex h-16 items-center border-b px-4 lg:px-6 shrink-0">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <Building className="h-6 w-6 text-primary" />
          {!isCollapsed && <span className="">CourseCreator</span>}
        </Link>
      </div>
      <nav className="flex-1 overflow-y-auto p-2 space-y-1">
        {navItems
          .filter((item) => item.roles.some((role) => hasRole(role)))
          .map((item) => (
            <SidebarNavItem key={item.href} {...item} isCollapsed={isCollapsed} />
          ))}
      </nav>
      <div className="mt-auto p-2 space-y-1 border-t">
        {bottomNavItems
          .filter((item) => item.roles.some((role) => hasRole(role)))
          .map((item) => (
            <SidebarNavItem key={item.href} {...item} isCollapsed={isCollapsed} />
          ))}
        <div className={cn("px-3 py-2", isCollapsed && "flex justify-center")}>
          <ThemeSwitcher />
        </div>
        <Button
          variant="ghost"
          onClick={logout}
          className={cn("w-full justify-start gap-3", isCollapsed && "justify-center")}
        >
          <LogOut className={cn("h-5 w-5", isCollapsed && "h-6 w-6")} />
          {!isCollapsed && <span>Logout</span>}
          {isCollapsed && <span className="sr-only">Logout</span>}
        </Button>
      </div>
      <Button
        variant="ghost"
        size="icon"
        className="absolute -right-4 top-16 rounded-full border bg-card hover:bg-muted"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        <span className="sr-only">Toggle sidebar</span>
      </Button>
    </div>
  )
}
