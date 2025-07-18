"use client"

import React from 'react'
import { cn } from '@/lib/utils'
import { StatusBadge, ProgressBadge } from '@/components/ui/status-badge'
import { useCourseRequestStatus } from '@/hooks/use-course-request-status'
import { 
  Wifi, 
  WifiOff, 
  RefreshCw, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Eye,
  Play,
  Pause
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface CourseRequestStatusProps {
  requestId: number
  className?: string
  showProgress?: boolean
  showConnection?: boolean
  compact?: boolean
}

// Map statusInfo.type to allowed ProgressBadge/StatusBadge statuses
const mapStatusTypeToBadge = (type: string): any => {
  switch (type) {
    case 'pending':
      return 'submitted';
    default:
      return type;
  }
}

export function CourseRequestStatus({
  requestId,
  className,
  showProgress = true,
  showConnection = true,
  compact = false
}: CourseRequestStatusProps) {
  const {
    status,
    isConnected,
    connectionError,
    reconnect,
    isProcessing,
    isCompleted,
    isApproved,
    isRejected,
    progress
  } = useCourseRequestStatus({ requestId })

  const getStatusInfo = () => {
    if (!status) {
      return {
        type: 'pending' as const,
        label: 'Loading...',
        description: 'Fetching status information'
      }
    }

    switch (status.status) {
      case 'submitted':
        return {
          type: 'submitted' as const,
          label: 'Submitted',
          description: 'Awaiting review by course manager'
        }
      case 'under_review':
        return {
          type: 'under_review' as const,
          label: 'Under Review',
          description: 'Being reviewed by our team'
        }
      case 'approved':
        return {
          type: 'approved' as const,
          label: 'Approved',
          description: 'Approved and queued for generation'
        }
      case 'generation_in_progress':
        return {
          type: 'generation_in_progress' as const,
          label: 'Generating',
          description: 'AI agents are creating your course'
        }
      case 'completed':
        return {
          type: 'completed' as const,
          label: 'Completed',
          description: 'Course ready for delivery'
        }
      case 'rejected':
        return {
          type: 'rejected' as const,
          label: 'Rejected',
          description: status.message || 'Request rejected during review'
        }
      default:
        return {
          type: 'pending' as const,
          label: status.status,
          description: status.message || 'Status unknown'
        }
    }
  }

  const statusInfo = getStatusInfo()
  const lastUpdated = status?.updated_at ? new Date(status.updated_at) : null

  if (compact) {
    return (
      <div className={cn("flex items-center gap-2", className)}>
        {showProgress && isProcessing ? (
          <ProgressBadge
            status={mapStatusTypeToBadge(statusInfo.type)}
            progress={progress}
            showPercentage={true}
            size="sm"
          />
        ) : (
          <StatusBadge
            status={mapStatusTypeToBadge(statusInfo.type)}
            size="sm"
            showTooltip={true}
          />
        )}
        
        {showConnection && (
          <div className="flex items-center gap-1">
            {isConnected ? (
              <Wifi className="h-3 w-3 text-green-500" />
            ) : (
              <WifiOff className="h-3 w-3 text-gray-400" />
            )}
          </div>
        )}
      </div>
    )
  }

  return (
    <Card className={cn("", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Request Status</CardTitle>
          {showConnection && (
            <div className="flex items-center gap-2">
              {isConnected ? (
                <div className="flex items-center gap-1 text-sm text-green-600">
                  <Wifi className="h-4 w-4" />
                  <span>Live</span>
                </div>
              ) : (
                <div className="flex items-center gap-1">
                  <WifiOff className="h-4 w-4 text-gray-400" />
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={reconnect}
                    className="text-xs h-6 px-2"
                  >
                    <RefreshCw className="h-3 w-3 mr-1" />
                    Reconnect
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
        <CardDescription>
          Course Request #{requestId}
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Status Badge */}
        <div className="flex items-center gap-3">
          {showProgress && isProcessing ? (
            <ProgressBadge
              status={mapStatusTypeToBadge(statusInfo.type)}
              progress={progress}
              showPercentage={true}
            />
          ) : (
            <StatusBadge
              status={mapStatusTypeToBadge(statusInfo.type)}
              showIcon={true}
              pulse={isProcessing}
            />
          )}
          <div className="flex-1">
            <div className="font-medium">{statusInfo.label}</div>
            <div className="text-sm text-muted-foreground">
              {statusInfo.description}
            </div>
          </div>
        </div>

        {/* Progress Bar for Generation */}
        {isProcessing && showProgress && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Generation Progress</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Status Message */}
        {status?.message && (
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-700">
              {status.message}
            </div>
          </div>
        )}

        {/* Last Updated */}
        {lastUpdated && (
          <div className="text-xs text-muted-foreground flex items-center gap-1">
            <Clock className="h-3 w-3" />
            Last updated: {lastUpdated.toLocaleString()}
          </div>
        )}

        {/* Connection Error */}
        {connectionError && (
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center gap-2 text-yellow-800">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{connectionError}</span>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        {isCompleted && status?.generated_course_id && (
          <Button
            onClick={() => window.open(`/course-manager/courses/${status.generated_course_id}`, '_blank')}
            className="w-full"
          >
            <Eye className="h-4 w-4 mr-2" />
            View Generated Course
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

// Mini status component for use in lists
export function MiniCourseRequestStatus({
  requestId,
  className
}: {
  requestId: number
  className?: string
}) {
  return (
    <CourseRequestStatus
      requestId={requestId}
      className={className}
      compact={true}
      showConnection={false}
    />
  )
}

// Status timeline component
export function CourseRequestTimeline({
  requestId,
  className
}: {
  requestId: number
  className?: string
}) {
  const { status } = useCourseRequestStatus({ requestId })

  const timelineSteps = [
    { status: 'submitted', label: 'Submitted', icon: CheckCircle },
    { status: 'under_review', label: 'Under Review', icon: Eye },
    { status: 'approved', label: 'Approved', icon: CheckCircle },
    { status: 'generation_in_progress', label: 'Generating', icon: Play },
    { status: 'completed', label: 'Completed', icon: CheckCircle }
  ]

  const currentStatusIndex = timelineSteps.findIndex(step => step.status === status?.status)
  
  return (
    <div className={cn("space-y-2", className)}>
      {timelineSteps.map((step, index) => {
        const Icon = step.icon
        const isActive = index === currentStatusIndex
        const isCompleted = index < currentStatusIndex
        const isPending = index > currentStatusIndex
        
        return (
          <div
            key={step.status}
            className={cn(
              "flex items-center gap-3 p-2 rounded-lg transition-colors",
              isActive && "bg-blue-50 border border-blue-200",
              isCompleted && "text-green-600",
              isPending && "text-gray-400"
            )}
          >
            <Icon className={cn(
              "h-4 w-4",
              isActive && "text-blue-600",
              isCompleted && "text-green-600",
              isPending && "text-gray-400"
            )} />
            <span className="text-sm font-medium">{step.label}</span>
            {isActive && (
              <RefreshCw className="h-3 w-3 animate-spin text-blue-600 ml-auto" />
            )}
          </div>
        )
      })}
    </div>
  )
}