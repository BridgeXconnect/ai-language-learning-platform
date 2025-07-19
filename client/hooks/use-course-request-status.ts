"use client"

import { useEffect, useState, useCallback } from 'react'
import { WebSocketService } from '@/lib/websocket'
import { useAuth } from '@/contexts/auth-context'
import { useToastHelpers } from '@/components/ui/notification-toast'

export interface CourseRequestStatus {
  id: number
  status: string
  progress?: number
  message?: string
  updated_at: string
  generated_course_id?: number
}

export interface StatusUpdate {
  event: 'status_change' | 'progress_update' | 'generation_complete' | 'error'
  request_id: number
  data: CourseRequestStatus
}

interface UseCourseRequestStatusOptions {
  requestId?: number
  autoConnect?: boolean
  onStatusChange?: (status: CourseRequestStatus) => void
  onError?: (error: any) => void
}

export function useCourseRequestStatus({
  requestId,
  autoConnect = true,
  onStatusChange,
  onError
}: UseCourseRequestStatusOptions = {}) {
  const [status, setStatus] = useState<CourseRequestStatus | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const [wsService, setWsService] = useState<WebSocketService | null>(null)
  
  const { user } = useAuth()
  const { info, warning, error: showError } = useToastHelpers()

  const connect = useCallback((targetRequestId: number) => {
    if (!user || wsService?.isConnected()) return

    try {
      const service = new WebSocketService(`/ws/course-requests/${targetRequestId}`, {
        autoReconnect: true,
        reconnectInterval: 3000,
        maxReconnectAttempts: 5
      })

      // Connection handlers
      service.onConnect(() => {
        setIsConnected(true)
        setConnectionError(null)
        console.log(`🔗 Connected to course request #${targetRequestId} status updates`)
      })

      service.onDisconnect(() => {
        setIsConnected(false)
        console.log(`🔌 Disconnected from course request #${targetRequestId} status updates`)
      })

      service.onError((error) => {
        const errorMessage = 'Real-time updates connection failed'
        setConnectionError(errorMessage)
        console.error('WebSocket error:', error)
        
        if (onError) {
          onError(error)
        } else {
          warning('Connection issue', 'Real-time updates may be delayed')
        }
      })

      // Status update handlers
      service.on('status_change', (update: StatusUpdate) => {
        console.log('📡 Status update received:', update)
        setStatus(update.data)
        
        if (onStatusChange) {
          onStatusChange(update.data)
        }
        
        // Show notification for important status changes
        if (update.data.status === 'approved') {
          info('Course Approved', 'Your course request has been approved!')
        } else if (update.data.status === 'completed') {
          info('Course Ready', 'Your course has been generated and is ready for delivery!')
        } else if (update.data.status === 'rejected') {
          showError('Request Rejected', update.data.message || 'Your course request was rejected')
        }
      })

      service.on('progress_update', (update: StatusUpdate) => {
        console.log('📈 Progress update received:', update)
        setStatus(prev => prev ? { ...prev, progress: update.data.progress } : update.data)
        
        if (onStatusChange) {
          onStatusChange(update.data)
        }
      })

      service.on('generation_complete', (update: StatusUpdate) => {
        console.log('✅ Generation complete:', update)
        setStatus(update.data)
        
        if (onStatusChange) {
          onStatusChange(update.data)
        }
        
        info(
          'Course Generation Complete',
          `Your course is ready! Course ID: ${update.data.generated_course_id}`,
          {
            duration: 0, // Don't auto-dismiss
            action: {
              label: 'View Course',
              onClick: () => {
                window.open(`/course-manager/courses/${update.data.generated_course_id}`, '_blank')
              }
            }
          }
        )
      })

      service.on('error', (update: StatusUpdate) => {
        console.error('❌ Status error received:', update)
        setStatus(update.data)
        
        if (onStatusChange) {
          onStatusChange(update.data)
        }
        
        showError(
          'Processing Error',
          update.data.message || 'An error occurred while processing your request'
        )
      })

      service.connect()
      setWsService(service)
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setConnectionError('Failed to establish real-time connection')
      
      if (onError) {
        onError(error)
      }
    }
  }, [user, wsService, onStatusChange, onError, info, warning, showError])

  const disconnect = useCallback(() => {
    if (wsService) {
      wsService.disconnect()
      setWsService(null)
      setIsConnected(false)
      setStatus(null)
    }
  }, [wsService])

  const reconnect = useCallback(() => {
    if (requestId) {
      disconnect()
      setTimeout(() => connect(requestId), 1000)
    }
  }, [requestId, disconnect, connect])

  // Auto-connect when requestId is provided
  useEffect(() => {
    if (autoConnect && requestId && user) {
      connect(requestId)
    }

    return () => {
      if (wsService) {
        wsService.disconnect()
      }
    }
  }, [requestId, autoConnect, user, connect])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsService) {
        wsService.disconnect()
      }
    }
  }, [wsService])

  return {
    status,
    isConnected,
    connectionError,
    connect,
    disconnect,
    reconnect,
    
    // Convenience methods
    isProcessing: status?.status === 'generation_in_progress',
    isCompleted: status?.status === 'completed',
    isApproved: status?.status === 'approved',
    isRejected: status?.status === 'rejected',
    progress: status?.progress || 0
  }
}

// Hook for tracking multiple course requests
export function useMultipleCourseRequestStatus(requestIds: number[]) {
  const [statuses, setStatuses] = useState<Record<number, CourseRequestStatus>>({})
  const [connections, setConnections] = useState<Record<number, WebSocketService>>({})
  
  const { user } = useAuth()
  const { info, warning, error: showError } = useToastHelpers()

  const connectToRequest = useCallback((requestId: number) => {
    setConnections(prev => {
      // Check if already connected
      if (!user || prev[requestId]?.isConnected()) return prev

      try {
        const service = new WebSocketService(`/ws/course-requests/${requestId}`, {
          autoReconnect: true,
          reconnectInterval: 3000,
          maxReconnectAttempts: 3
        })

        service.onConnect(() => {
          console.log(`🔗 Connected to course request #${requestId}`)
        })

        service.on('status_change', (update: StatusUpdate) => {
          setStatuses(prev => ({
            ...prev,
            [requestId]: update.data
          }))

          // Show notifications for important changes
          if (update.data.status === 'completed') {
            info(`Course #${requestId} Ready`, 'Course generation completed!')
          }
        })

        service.on('progress_update', (update: StatusUpdate) => {
          setStatuses(prev => ({
            ...prev,
            [requestId]: { ...prev[requestId], ...update.data }
          }))
        })

        service.connect()
        
        return {
          ...prev,
          [requestId]: service
        }
        
      } catch (error) {
        console.error(`Failed to connect to request #${requestId}:`, error)
        return prev
      }
    })
  }, [user, info])

  const disconnectFromRequest = useCallback((requestId: number) => {
    setConnections(prev => {
      const connection = prev[requestId]
      if (connection) {
        connection.disconnect()
        const { [requestId]: removed, ...rest } = prev
        return rest
      }
      return prev
    })
  }, [])

  const disconnectAll = useCallback(() => {
    setConnections(prev => {
      Object.values(prev).forEach(connection => {
        connection.disconnect()
      })
      return {}
    })
    setStatuses({})
  }, [])

  // Connect to all requests
  useEffect(() => {
    if (user && requestIds.length > 0) {
      requestIds.forEach(connectToRequest)
    }

    return () => {
      // Disconnect all connections on cleanup
      setConnections(prev => {
        Object.values(prev).forEach(connection => {
          connection.disconnect()
        })
        return {}
      })
      setStatuses({})
    }
  }, [requestIds, user, connectToRequest])

  return {
    statuses,
    connectToRequest,
    disconnectFromRequest,
    disconnectAll,
    getStatus: (requestId: number) => statuses[requestId] || null,
    isConnected: (requestId: number) => connections[requestId]?.isConnected() || false
  }
}