/**
 * Status Badge Component
 * Professional status indicators with consistent styling
 */

import React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
import { 
  Clock, 
  AlertCircle, 
  CheckCircle, 
  XCircle, 
  Play, 
  Pause,
  RefreshCw,
  FileText,
  Eye,
  type LucideIcon
} from 'lucide-react'

const statusBadgeVariants = cva(
  [
    'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full',
    'text-xs font-medium transition-all duration-200',
    'border',
  ],
  {
    variants: {
      variant: {
        pending: [
          'bg-yellow-50 text-yellow-800 border-yellow-200',
          'dark:bg-yellow-900/20 dark:text-yellow-300 dark:border-yellow-800',
        ],
        'in-progress': [
          'bg-blue-50 text-blue-800 border-blue-200',
          'dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-800',
        ],
        review: [
          'bg-purple-50 text-purple-800 border-purple-200',
          'dark:bg-purple-900/20 dark:text-purple-300 dark:border-purple-800',
        ],
        approved: [
          'bg-green-50 text-green-800 border-green-200',
          'dark:bg-green-900/20 dark:text-green-300 dark:border-green-800',
        ],
        completed: [
          'bg-emerald-50 text-emerald-800 border-emerald-200',
          'dark:bg-emerald-900/20 dark:text-emerald-300 dark:border-emerald-800',
        ],
        rejected: [
          'bg-red-50 text-red-800 border-red-200',
          'dark:bg-red-900/20 dark:text-red-300 dark:border-red-800',
        ],
        draft: [
          'bg-gray-50 text-gray-800 border-gray-200',
          'dark:bg-gray-900/20 dark:text-gray-300 dark:border-gray-800',
        ],
        paused: [
          'bg-orange-50 text-orange-800 border-orange-200',
          'dark:bg-orange-900/20 dark:text-orange-300 dark:border-orange-800',
        ],
      },
      size: {
        sm: 'px-2 py-0.5 text-xs',
        md: 'px-2.5 py-1 text-xs',
        lg: 'px-3 py-1.5 text-sm',
      },
      animated: {
        true: '',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'pending',
      size: 'md',
      animated: false,
    },
  }
)

const statusConfig = {
  // Course request statuses
  submitted: {
    variant: 'pending' as const,
    icon: Clock,
    label: 'Awaiting Review',
    description: 'Request submitted and waiting for review',
    animated: false,
  },
  under_review: {
    variant: 'review' as const,
    icon: Eye,
    label: 'Under Review',
    description: 'Being reviewed by course manager',
    animated: false,
  },
  generation_in_progress: {
    variant: 'in-progress' as const,
    icon: RefreshCw,
    label: 'Generating Course',
    description: 'AI agents are creating course content',
    animated: true,
  },
  approved: {
    variant: 'approved' as const,
    icon: CheckCircle,
    label: 'Approved',
    description: 'Course approved and ready for delivery',
    animated: false,
  },
  completed: {
    variant: 'completed' as const,
    icon: CheckCircle,
    label: 'Completed',
    description: 'Course generation completed successfully',
    animated: false,
  },
  rejected: {
    variant: 'rejected' as const,
    icon: XCircle,
    label: 'Rejected',
    description: 'Request rejected during review',
    animated: false,
  },
  draft: {
    variant: 'draft' as const,
    icon: FileText,
    label: 'Draft',
    description: 'Request saved as draft',
    animated: false,
  },
  paused: {
    variant: 'paused' as const,
    icon: Pause,
    label: 'Paused',
    description: 'Generation paused',
    animated: false,
  },
  
  // Generic statuses
  active: {
    variant: 'approved' as const,
    icon: Play,
    label: 'Active',
    description: 'Currently active',
    animated: false,
  },
  inactive: {
    variant: 'draft' as const,
    icon: Pause,
    label: 'Inactive',
    description: 'Currently inactive',
    animated: false,
  },
  error: {
    variant: 'rejected' as const,
    icon: AlertCircle,
    label: 'Error',
    description: 'An error occurred',
    animated: false,
  },
} as const

export interface StatusBadgeProps
  extends Omit<React.HTMLAttributes<HTMLSpanElement>, 'children'>,
    VariantProps<typeof statusBadgeVariants> {
  status: keyof typeof statusConfig | string
  showIcon?: boolean
  showTooltip?: boolean
  customLabel?: string
  pulse?: boolean
}

const StatusBadge = React.forwardRef<HTMLSpanElement, StatusBadgeProps>(
  ({ 
    className, 
    status, 
    size, 
    showIcon = true, 
    showTooltip = false,
    customLabel,
    pulse = false,
    ...props 
  }, ref) => {
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft
    const IconComponent = config.icon
    const isAnimated = config.animated || pulse
    
    const badge = (
      <span
        ref={ref}
        className={cn(
          statusBadgeVariants({ 
            variant: config.variant, 
            size, 
            animated: isAnimated 
          }),
          className
        )}
        {...props}
      >
        {showIcon && (
          <IconComponent 
            className={cn(
              'flex-shrink-0',
              size === 'sm' ? 'h-3 w-3' : size === 'lg' ? 'h-4 w-4' : 'h-3.5 w-3.5',
              isAnimated && 'animate-spin'
            )} 
          />
        )}
        <span className="truncate">
          {customLabel || config.label}
        </span>
      </span>
    )
    
    if (showTooltip) {
      return (
        <div className="group relative inline-block">
          {badge}
          <div className="invisible group-hover:visible absolute z-10 w-48 p-2 mt-2 text-xs bg-gray-900 text-white rounded-md shadow-lg -translate-x-1/2 left-1/2">
            <div className="font-medium">{config.label}</div>
            <div className="text-gray-300 mt-0.5">{config.description}</div>
            <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-gray-900 rotate-45"></div>
          </div>
        </div>
      )
    }
    
    return badge
  }
)
StatusBadge.displayName = 'StatusBadge'

// Progress badge for showing completion percentage
export interface ProgressBadgeProps extends StatusBadgeProps {
  progress: number
  showPercentage?: boolean
}

const ProgressBadge = React.forwardRef<HTMLSpanElement, ProgressBadgeProps>(
  ({ 
    progress, 
    showPercentage = true, 
    status = 'generation_in_progress',
    ...props 
  }, ref) => {
    const clampedProgress = Math.max(0, Math.min(100, progress))
    
    return (
      <div className="flex items-center gap-2">
        <StatusBadge
          ref={ref}
          status={status}
          customLabel={showPercentage ? `${clampedProgress}%` : undefined}
          {...props}
        />
        <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className="h-full bg-current transition-all duration-300 ease-out"
            style={{ width: `${clampedProgress}%` }}
          />
        </div>
      </div>
    )
  }
)
ProgressBadge.displayName = 'ProgressBadge'

// Export all status types for TypeScript
export type StatusType = keyof typeof statusConfig

export { StatusBadge, ProgressBadge, statusConfig }