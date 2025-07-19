"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import type { LucideIcon } from "lucide-react"

interface SidebarNavItemProps {
  href: string
  icon: LucideIcon
  label: string
  isCollapsed?: boolean
}

export function SidebarNavItem({ href, icon: Icon, label, isCollapsed }: SidebarNavItemProps) {
  const pathname = usePathname()
  const isActive = pathname === href || (href !== "/" && pathname.startsWith(href))

  return (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary hover:bg-muted",
        isActive && "bg-primary/10 text-primary font-medium",
        isCollapsed && "justify-center",
      )}
    >
      <Icon className={cn("h-5 w-5", isCollapsed && "h-6 w-6")} />
      {!isCollapsed && <span className="truncate">{label}</span>}
      {isCollapsed && <span className="sr-only">{label}</span>}
    </Link>
  )
}
