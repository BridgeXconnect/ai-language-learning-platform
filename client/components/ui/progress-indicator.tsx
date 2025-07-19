"use client"

import React from 'react'
import { cn } from '@/lib/utils'
import { Loader, CheckCircle, AlertCircle } from 'lucide-react'

export interface ProgressStep {
  id: string
  label: string
  description?: string
  status: 'pending' | 'active' | 'completed' | 'error'
}

interface ProgressIndicatorProps {
  steps: ProgressStep[]
  currentStepId?: string
  className?: string
  orientation?: 'horizontal' | 'vertical'
  showLabels?: boolean
  showDescriptions?: boolean
}

export function ProgressIndicator({
  steps,
  currentStepId,
  className,
  orientation = 'horizontal',
  showLabels = true,
  showDescriptions = false
}: ProgressIndicatorProps) {
  const currentIndex = currentStepId ? steps.findIndex(step => step.id === currentStepId) : -1

  const getStepIcon = (step: ProgressStep, index: number) => {
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-600" />
      case 'active':
        return <Loader className="h-5 w-5 text-blue-600 animate-spin" />
      default:
        return (
          <div className={cn(
            "h-5 w-5 rounded-full border-2 flex items-center justify-center text-xs font-semibold",
            step.status === 'pending' ? "border-gray-300 text-gray-400" : "border-blue-600 text-blue-600"
          )}>
            {index + 1}
          </div>
        )
    }
  }

  const getStepClasses = (step: ProgressStep) => {
    const baseClasses = "transition-all duration-200"
    switch (step.status) {
      case 'completed':
        return cn(baseClasses, "text-green-600")
      case 'error':
        return cn(baseClasses, "text-red-600")
      case 'active':
        return cn(baseClasses, "text-blue-600 font-medium")
      default:
        return cn(baseClasses, "text-gray-500")
    }
  }

  const getConnectorClasses = (fromStep: ProgressStep, toStep: ProgressStep) => {
    if (fromStep.status === 'completed') {
      return "bg-green-600"
    } else if (fromStep.status === 'active' || fromStep.status === 'error') {
      return "bg-blue-600"
    }
    return "bg-gray-300"
  }

  if (orientation === 'vertical') {
    return (
      <div className={cn("flex flex-col space-y-4", className)}>
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-start space-x-3">
            <div className="flex flex-col items-center">
              {getStepIcon(step, index)}
              {index < steps.length - 1 && (
                <div className={cn(
                  "w-0.5 h-8 mt-2",
                  getConnectorClasses(step, steps[index + 1])
                )} />
              )}
            </div>
            {(showLabels || showDescriptions) && (
              <div className="flex-1 min-w-0">
                {showLabels && (
                  <h4 className={cn("text-sm", getStepClasses(step))}>
                    {step.label}
                  </h4>
                )}
                {showDescriptions && step.description && (
                  <p className="text-xs text-gray-500 mt-0.5">
                    {step.description}
                  </p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    )
  }

  // Horizontal orientation
  return (
    <div className={cn("flex items-center justify-between", className)}>
      {steps.map((step, index) => (
        <React.Fragment key={step.id}>
          <div className="flex flex-col items-center space-y-2">
            {getStepIcon(step, index)}
            {(showLabels || showDescriptions) && (
              <div className="text-center">
                {showLabels && (
                  <div className={cn("text-xs", getStepClasses(step))}>
                    {step.label}
                  </div>
                )}
                {showDescriptions && step.description && (
                  <div className="text-xs text-gray-500 mt-0.5">
                    {step.description}
                  </div>
                )}
              </div>
            )}
          </div>
          {index < steps.length - 1 && (
            <div className={cn(
              "flex-1 h-0.5 mx-2",
              getConnectorClasses(step, steps[index + 1])
            )} />
          )}
        </React.Fragment>
      ))}
    </div>
  )
}

// Simple loading spinner component
export function LoadingSpinner({ 
  size = 'md',
  className 
}: { 
  size?: 'sm' | 'md' | 'lg'
  className?: string 
}) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  }

  return (
    <Loader className={cn(
      'animate-spin text-blue-600',
      sizeClasses[size],
      className
    )} />
  )
}

// Loading overlay component
export function LoadingOverlay({ 
  message = "Loading...",
  description,
  className 
}: { 
  message?: string
  description?: string
  className?: string 
}) {
  return (
    <div className={cn(
      "absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50",
      className
    )}>
      <div className="text-center space-y-3">
        <LoadingSpinner size="lg" />
        <div>
          <div className="font-medium text-gray-900">{message}</div>
          {description && (
            <div className="text-sm text-gray-600 mt-1">{description}</div>
          )}
        </div>
      </div>
    </div>
  )
}