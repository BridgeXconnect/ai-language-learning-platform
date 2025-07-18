"use client"

import React, { createContext, useContext, useCallback, useState } from 'react'
import { X, CheckCircle, AlertCircle, AlertTriangle, Info, Loader } from 'lucide-react'
import { cn } from '@/lib/utils'

export type ToastType = 'success' | 'error' | 'warning' | 'info' | 'loading'

export interface Toast {
  id: string
  type: ToastType
  title: string
  description?: string
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
  onDismiss?: () => void
}

interface ToastContextType {
  toasts: Toast[]
  showToast: (toast: Omit<Toast, 'id'>) => string
  dismissToast: (id: string) => void
  dismissAll: () => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const showToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9)
    const newToast: Toast = { ...toast, id }
    
    setToasts(prev => [...prev, newToast])

    // Auto dismiss after duration (default 5s, never for loading)
    if (toast.type !== 'loading') {
      const duration = toast.duration ?? 5000
      if (duration > 0) {
        setTimeout(() => {
          dismissToast(id)
        }, duration)
      }
    }

    return id
  }, [])

  const dismissToast = useCallback((id: string) => {
    setToasts(prev => {
      const toast = prev.find(t => t.id === id)
      if (toast?.onDismiss) {
        toast.onDismiss()
      }
      return prev.filter(t => t.id !== id)
    })
  }, [])

  const dismissAll = useCallback(() => {
    setToasts([])
  }, [])

  return (
    <ToastContext.Provider value={{ toasts, showToast, dismissToast, dismissAll }}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  )
}

export function useNotificationToast() {
  const context = useContext(ToastContext)
  if (context === undefined) {
    throw new Error('useNotificationToast must be used within a ToastProvider')
  }
  return context
}

function ToastContainer() {
  const { toasts } = useNotificationToast()

  if (toasts.length === 0) return null

  return (
    <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2 max-w-sm w-full">
      {toasts.map(toast => (
        <ToastItem key={toast.id} toast={toast} />
      ))}
    </div>
  )
}

function ToastItem({ toast }: { toast: Toast }) {
  const { dismissToast } = useNotificationToast()

  const getIcon = () => {
    switch (toast.type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-600" />
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />
      case 'info':
        return <Info className="h-5 w-5 text-blue-600" />
      case 'loading':
        return <Loader className="h-5 w-5 text-blue-600 animate-spin" />
      default:
        return <Info className="h-5 w-5 text-gray-600" />
    }
  }

  const getBorderColor = () => {
    switch (toast.type) {
      case 'success':
        return 'border-l-green-500'
      case 'error':
        return 'border-l-red-500'
      case 'warning':
        return 'border-l-yellow-500'
      case 'info':
        return 'border-l-blue-500'
      case 'loading':
        return 'border-l-blue-500'
      default:
        return 'border-l-gray-500'
    }
  }

  return (
    <div
      className={cn(
        "relative bg-white border-l-4 rounded-lg shadow-lg p-4 transition-all duration-300 transform",
        "animate-in slide-in-from-right-full",
        getBorderColor()
      )}
      role="alert"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          {getIcon()}
        </div>
        
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-gray-900 text-sm">
            {toast.title}
          </h4>
          {toast.description && (
            <p className="text-sm text-gray-600 mt-1">
              {toast.description}
            </p>
          )}
          {toast.action && (
            <button
              onClick={toast.action.onClick}
              className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-500 transition-colors"
            >
              {toast.action.label}
            </button>
          )}
        </div>

        {toast.type !== 'loading' && (
          <button
            onClick={() => dismissToast(toast.id)}
            className="flex-shrink-0 p-1 rounded-full hover:bg-gray-100 transition-colors"
            aria-label="Dismiss notification"
          >
            <X className="h-4 w-4 text-gray-400" />
          </button>
        )}
      </div>
    </div>
  )
}

// Convenience hooks for different toast types
export function useToastHelpers() {
  const { showToast, dismissToast } = useNotificationToast()

  return {
    success: (title: string, description?: string, options?: Partial<Toast>) =>
      showToast({ type: 'success', title, description, ...options }),
    
    error: (title: string, description?: string, options?: Partial<Toast>) =>
      showToast({ type: 'error', title, description, duration: 0, ...options }),
    
    warning: (title: string, description?: string, options?: Partial<Toast>) =>
      showToast({ type: 'warning', title, description, ...options }),
    
    info: (title: string, description?: string, options?: Partial<Toast>) =>
      showToast({ type: 'info', title, description, ...options }),
    
    loading: (title: string, description?: string) => {
      const id = showToast({ type: 'loading', title, description })
      return {
        id,
        dismiss: () => dismissToast(id),
        update: (newTitle: string, newDescription?: string, newType: ToastType = 'success') => {
          dismissToast(id)
          return showToast({ type: newType, title: newTitle, description: newDescription })
        }
      }
    },

    showToast,
    dismissToast
  }
}