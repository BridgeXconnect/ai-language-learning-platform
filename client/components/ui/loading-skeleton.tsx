import { cn } from "@/lib/utils"

interface SkeletonProps {
  className?: string
  width?: string | number
  height?: string | number
  rounded?: "none" | "sm" | "md" | "lg" | "full"
}

export function Skeleton({ 
  className, 
  width, 
  height, 
  rounded = "md" 
}: SkeletonProps) {
  const getRoundedClass = () => {
    switch (rounded) {
      case "none": return ""
      case "sm": return "rounded-sm"
      case "md": return "rounded-md"
      case "lg": return "rounded-lg"
      case "full": return "rounded-full"
      default: return "rounded-md"
    }
  }

  return (
    <div
      className={cn(
        "animate-pulse bg-muted",
        getRoundedClass(),
        className
      )}
      style={{
        width: width,
        height: height,
      }}
    />
  )
}

// Predefined skeleton components
export function CardSkeleton() {
  return (
    <div className="space-y-3">
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-4 w-1/2" />
      <Skeleton className="h-8 w-1/3" />
    </div>
  )
}

export function DashboardCardSkeleton() {
  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-5 w-24" />
        <Skeleton className="h-8 w-8 rounded-full" />
      </div>
      <Skeleton className="h-4 w-32" />
      <Skeleton className="h-8 w-16" />
    </div>
  )
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex gap-4">
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-16" />
        <Skeleton className="h-4 w-20" />
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-16" />
          <Skeleton className="h-4 w-20" />
        </div>
      ))}
    </div>
  )
}

export function ChartSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-5 w-32" />
        <Skeleton className="h-4 w-24" />
      </div>
      <div className="space-y-2">
        {Array.from({ length: 7 }).map((_, i) => (
          <div key={i} className="flex items-center gap-3">
            <Skeleton className="h-4 w-12" />
            <Skeleton className="h-4 flex-1" />
            <Skeleton className="h-4 w-16" />
          </div>
        ))}
      </div>
    </div>
  )
}

export function AvatarSkeleton() {
  return <Skeleton className="h-10 w-10 rounded-full" />
}

export function ButtonSkeleton() {
  return <Skeleton className="h-10 w-24" />
}

export function InputSkeleton() {
  return <Skeleton className="h-10 w-full" />
}

export function ListSkeleton({ items = 3 }: { items?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <Skeleton className="h-8 w-8 rounded-full" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  )
} 