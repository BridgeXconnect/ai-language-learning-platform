"use client"

import Link from "next/link"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import {
  Menu,
  Search,
  UserCircle,
  Settings,
  LogOut,
  LayoutDashboard,
  Users,
  BookOpen,
  GraduationCap,
  Briefcase,
  Bot,
  Building,
} from "lucide-react"
import { Input } from "@/components/ui/input"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useAuth } from "@/contexts/auth-context"
import { UserRole } from "@/lib/constants"
import { SidebarNavItem } from "./sidebar-nav-item"
import { ThemeSwitcher } from "@/components/theme-switcher"

export function Header() {
  const { user, logout, hasRole } = useAuth()

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
    { href: "/settings", icon: Settings, label: "Settings", roles: Object.values(UserRole) },
  ]

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background/80 backdrop-blur-sm px-4 md:px-6">
      <nav className="hidden flex-col gap-6 text-lg font-medium md:flex md:flex-row md:items-center md:gap-5 md:text-sm lg:gap-6">
        {/* Desktop: Logo is in sidebar */}
      </nav>
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="outline" size="icon" className="shrink-0 md:hidden">
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle navigation menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="flex flex-col">
          <nav className="grid gap-2 text-lg font-medium">
            <Link href="#" className="flex items-center gap-2 text-lg font-semibold mb-4">
              <Building className="h-6 w-6 text-primary" />
              <span>CourseCreator</span>
            </Link>
            {navItems
              .filter((item) => item.roles.some((role) => hasRole(role)))
              .map((item) => (
                <SidebarNavItem key={item.href} {...item} />
              ))}
          </nav>
          <div className="mt-auto">
            <Button variant="ghost" onClick={logout} className="w-full justify-start gap-2">
              <LogOut className="h-5 w-5" />
              Logout
            </Button>
          </div>
        </SheetContent>
      </Sheet>
      <div className="flex w-full items-center gap-4 md:ml-auto md:gap-2 lg:gap-4">
        <form className="ml-auto flex-1 sm:flex-initial">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search platform..."
              className="pl-8 sm:w-[300px] md:w-[200px] lg:w-[300px]"
            />
          </div>
        </form>
        <ThemeSwitcher />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="secondary" size="icon" className="rounded-full">
              {user?.avatarUrl ? (
                <img src={user.avatarUrl || "/placeholder.svg"} alt={user.name} className="h-8 w-8 rounded-full" />
              ) : (
                <UserCircle className="h-5 w-5" />
              )}
              <span className="sr-only">Toggle user menu</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>{user?.name || "My Account"}</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => {
                /* router.push('/profile') */
              }}
            >
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => {
                /* router.push('/settings') */
              }}
            >
              Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout}>Logout</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
