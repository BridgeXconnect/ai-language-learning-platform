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
  Bell,
  Sparkles,
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
import { UserRole } from "packages/shared/constants"
import { SidebarNavItem } from "./sidebar-nav-item"
import { ThemeSwitcher } from "@/components/theme-switcher"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

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

  const getUserInitials = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
    }
    if (user?.first_name) {
      return user.first_name[0].toUpperCase()
    }
    if (user?.username) {
      return user.username[0].toUpperCase()
    }
    return "U"
  }

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background/95 backdrop-blur-md px-4 md:px-6 shadow-sm">
      {/* Mobile Navigation */}
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="outline" size="icon" className="shrink-0 md:hidden hover:bg-primary/5 transition-colors">
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle navigation menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="flex flex-col bg-background/95 backdrop-blur-md">
          <nav className="grid gap-2 text-lg font-medium">
            <Link href="#" className="flex items-center gap-2 text-lg font-semibold mb-6 p-2 rounded-lg hover:bg-primary/5 transition-colors">
              <div className="p-2 rounded-lg gradient-primary">
                <Building className="h-6 w-6 text-primary-foreground" />
              </div>
              <span className="bg-gradient-to-r from-primary to-[hsl(var(--ai-purple))] bg-clip-text text-transparent">
                CourseCreator
              </span>
            </Link>
            {navItems
              .filter((item) => item.roles.some((role) => hasRole(role)))
              .map((item) => (
                <SidebarNavItem key={item.href} {...item} />
              ))}
          </nav>
          <div className="mt-auto">
            <Button variant="ghost" onClick={logout} className="w-full justify-start gap-2 hover:bg-destructive/10 hover:text-destructive transition-colors">
              <LogOut className="h-5 w-5" />
              Logout
            </Button>
          </div>
        </SheetContent>
      </Sheet>

      {/* Desktop Navigation */}
      <nav className="hidden flex-col gap-6 text-lg font-medium md:flex md:flex-row md:items-center md:gap-5 md:text-sm lg:gap-6">
        {/* Logo placeholder for desktop */}
      </nav>

      {/* Search and Actions */}
      <div className="flex w-full items-center gap-4 md:ml-auto md:gap-2 lg:gap-4">
        {/* Enhanced Search */}
        <form className="ml-auto flex-1 sm:flex-initial">
          <div className="relative group">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within:text-primary" />
            <Input
              type="search"
              placeholder="Search courses, students, analytics..."
              className="pl-10 pr-4 sm:w-[300px] md:w-[200px] lg:w-[300px] transition-all duration-200 focus:w-[350px] focus:ring-2 focus:ring-primary/20"
            />
          </div>
        </form>

        {/* Notifications */}
        <Button variant="ghost" size="icon" className="relative hover:bg-primary/5 transition-colors">
          <Bell className="h-5 w-5" />
          <Badge className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs bg-destructive">
            3
          </Badge>
          <span className="sr-only">Notifications</span>
        </Button>

        {/* Theme Switcher */}
        <ThemeSwitcher />

        {/* AI Status Indicator */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-full bg-[hsl(var(--ai-purple))]/10 border border-[hsl(var(--ai-purple))]/20">
          <div className="w-2 h-2 rounded-full bg-[hsl(var(--ai-purple))] animate-pulse-slow" />
          <span className="text-xs font-medium text-[hsl(var(--ai-purple))]">AI Active</span>
        </div>

        {/* User Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="rounded-full hover:bg-primary/5 transition-all duration-200 hover:scale-105">
              <Avatar className="h-8 w-8">
                <AvatarImage src={user?.avatarUrl} alt={user?.first_name || user?.username || "User"} />
                <AvatarFallback className="bg-gradient-to-br from-primary to-[hsl(var(--ai-purple))] text-primary-foreground font-semibold">
                  {getUserInitials()}
                </AvatarFallback>
              </Avatar>
              <span className="sr-only">Toggle user menu</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56 bg-background/95 backdrop-blur-md border-border/50">
            <DropdownMenuLabel className="font-semibold">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">
                  {user?.first_name || user?.username || "User"}
                </p>
                <p className="text-xs leading-none text-muted-foreground">
                  {user?.email}
                </p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="cursor-pointer hover:bg-primary/5 transition-colors">
              <UserCircle className="mr-2 h-4 w-4" />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem className="cursor-pointer hover:bg-primary/5 transition-colors">
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem 
              onClick={logout} 
              className="cursor-pointer hover:bg-destructive/10 hover:text-destructive transition-colors"
            >
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
