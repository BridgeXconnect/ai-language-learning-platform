import type React from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { LucideIcon } from "lucide-react"
import { Badge } from "@/components/ui/badge"

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
  style?: React.CSSProperties
  trend?: {
    value: number
    isPositive: boolean
    label: string
  }
  variant?: "default" | "success" | "warning" | "ai" | "gradient"
  size?: "sm" | "md" | "lg"
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
  style,
  trend,
  variant = "default",
  size = "md",
}: DashboardCardProps) {
  const getVariantStyles = () => {
    switch (variant) {
      case "success":
        return "border-success/20 bg-gradient-to-br from-success/5 to-success/10 hover:from-success/10 hover:to-success/15"
      case "warning":
        return "border-warning/20 bg-gradient-to-br from-warning/5 to-warning/10 hover:from-warning/10 hover:to-warning/15"
      case "ai":
        return "border-[hsl(var(--ai-purple))]/20 bg-gradient-to-br from-[hsl(var(--ai-purple))]/5 to-[hsl(var(--ai-teal))]/10 hover:from-[hsl(var(--ai-purple))]/10 hover:to-[hsl(var(--ai-teal))]/15"
      case "gradient":
        return "gradient-card border-primary/20"
      default:
        return "border-border/50 bg-gradient-to-br from-card to-card/80 hover:from-card hover:to-card/90"
    }
  }

  const getIconColor = () => {
    switch (variant) {
      case "success":
        return "text-success"
      case "warning":
        return "text-warning"
      case "ai":
        return "text-[hsl(var(--ai-purple))]"
      default:
        return "text-primary"
    }
  }

  const getSizeStyles = () => {
    switch (size) {
      case "sm":
        return "p-4"
      case "lg":
        return "p-6"
      default:
        return "p-5"
    }
  }

  return (
    <Card 
      className={cn(
        "card-hover card-glow group relative overflow-hidden transition-all duration-300",
        getVariantStyles(),
        getSizeStyles(),
        className
      )}
      style={style}
    >
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      
      <CardHeader className="pb-3 relative z-10">
        <div className="flex items-center justify-between">
          <CardTitle className={cn(
            "text-lg font-semibold tracking-tight transition-colors duration-200",
            titleClassName
          )}>
            {title}
          </CardTitle>
          {Icon && (
            <div className={cn(
              "p-2 rounded-lg bg-background/50 backdrop-blur-sm transition-all duration-300 group-hover:scale-110",
              getIconColor()
            )}>
              <Icon className="h-5 w-5" />
            </div>
          )}
        </div>
        {description && (
          <CardDescription className="text-sm opacity-80 transition-opacity duration-200 group-hover:opacity-100">
            {description}
          </CardDescription>
        )}
      </CardHeader>
      
      <CardContent className="relative z-10">
        {value && (
          <div className="space-y-2">
            <div className={cn(
              "text-3xl font-bold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent transition-all duration-300 group-hover:scale-105",
              valueClassName
            )}>
              {value}
            </div>
            {trend && (
              <div className="flex items-center gap-2">
                <Badge 
                  variant={trend.isPositive ? "default" : "secondary"}
                  className={cn(
                    "text-xs",
                    trend.isPositive 
                      ? "bg-success/10 text-success border-success/20" 
                      : "bg-destructive/10 text-destructive border-destructive/20"
                  )}
                >
                  {trend.isPositive ? "↗" : "↘"} {Math.abs(trend.value)}%
                </Badge>
                <span className="text-xs text-muted-foreground">{trend.label}</span>
              </div>
            )}
          </div>
        )}
        {children}
      </CardContent>
      
      {footer && (
        <CardFooter className="relative z-10 pt-0">
          {footer}
        </CardFooter>
      )}
    </Card>
  )
}
