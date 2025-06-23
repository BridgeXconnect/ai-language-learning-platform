import type React from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { LucideIcon } from "lucide-react"

interface DashboardCardProps {
  title: string
  description?: string
  icon?: LucideIcon
  value?: string | number
  footer?: React.ReactNode
  children?: React.ReactNode
  className?: string
  valueClassName?: string
  titleClassName?: string
}

export function DashboardCard({
  title,
  description,
  icon: Icon,
  value,
  footer,
  children,
  className,
  valueClassName,
  titleClassName,
}: DashboardCardProps) {
  return (
    <Card className={cn("shadow-sm hover:shadow-md transition-shadow duration-300", className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className={cn("text-lg font-semibold tracking-tight", titleClassName)}>{title}</CardTitle>
          {Icon && <Icon className="h-5 w-5 text-muted-foreground" />}
        </div>
        {description && <CardDescription className="text-sm">{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        {value && <div className={cn("text-3xl font-bold", valueClassName)}>{value}</div>}
        {children}
      </CardContent>
      {footer && <CardFooter>{footer}</CardFooter>}
    </Card>
  )
}
