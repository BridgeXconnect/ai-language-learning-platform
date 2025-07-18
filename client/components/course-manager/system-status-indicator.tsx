"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/enhanced-card'
import { Button } from '@/components/ui/enhanced-button'
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  WifiOff,
  Wifi,
  Clock,
  Zap,
  TrendingUp,
  TrendingDown,
  Minus,
  ExternalLink,
  RefreshCw
} from 'lucide-react'
import { useAuth } from '@/contexts/auth-context'
import { format } from 'date-fns'

interface SystemStatusData {
  agents_enabled: boolean
  orchestrator_available: boolean
  agent_health: Record<string, any>
  system_status: 'operational' | 'degraded' | 'offline'
  metrics: {
    healthy_agents: number
    total_agents: number
    health_percentage: number
    average_response_time_ms: number
  }
  workflow_metrics: {
    total_started: number
    total_completed: number
    total_failed: number
  }
  active_workflows_count: number
  checked_at: string
}

interface SystemStatusIndicatorProps {
  autoRefresh?: boolean
  refreshInterval?: number
  showDetails?: boolean
  onStatusChange?: (status: SystemStatusData) => void
}

export function SystemStatusIndicator({ 
  autoRefresh = true, 
  refreshInterval = 30000,
  showDetails = true,
  onStatusChange 
}: SystemStatusIndicatorProps) {
  const [statusData, setStatusData] = useState<SystemStatusData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const { fetchWithAuth } = useAuth()

  const fetchSystemStatus = async () => {
    try {
      setError(null)
      const response = await fetchWithAuth('/api/agents/status')
      
      if (response.ok) {
        const data = await response.json()
        setStatusData(data)
        setLastUpdate(new Date().toISOString())
        onStatusChange?.(data)
      } else {
        throw new Error(`Failed to fetch status: ${response.status}`)
      }
    } catch (err) {
      console.error('Error fetching system status:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch system status')
      
      // Set offline status
      setStatusData({
        agents_enabled: false,
        orchestrator_available: false,
        agent_health: {},
        system_status: 'offline',
        metrics: { healthy_agents: 0, total_agents: 0, health_percentage: 0, average_response_time_ms: 0 },
        workflow_metrics: { total_started: 0, total_completed: 0, total_failed: 0 },
        active_workflows_count: 0,
        checked_at: new Date().toISOString()
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Auto-refresh functionality
  useEffect(() => {
    if (autoRefresh) {
      fetchSystemStatus()
      const interval = setInterval(fetchSystemStatus, refreshInterval)
      return () => clearInterval(interval)
    } else {
      fetchSystemStatus()
    }
  }, [autoRefresh, refreshInterval])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return 'text-green-600 bg-green-50 border-green-200'
      case 'degraded': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'offline': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getStatusIcon = (status: string, size: string = 'h-5 w-5') => {
    switch (status) {
      case 'operational':
        return <CheckCircle className={`${size} text-green-500`} />
      case 'degraded':
        return <AlertTriangle className={`${size} text-yellow-500`} />
      case 'offline':
        return <WifiOff className={`${size} text-red-500`} />
      default:
        return <Activity className={`${size} text-gray-500`} />
    }
  }

  const getResponseTimeIcon = (responseTime: number) => {
    if (responseTime < 1000) return <TrendingUp className="h-4 w-4 text-green-500" />
    if (responseTime < 3000) return <Minus className="h-4 w-4 text-yellow-500" />
    return <TrendingDown className="h-4 w-4 text-red-500" />
  }

  const calculateSuccessRate = () => {
    if (!statusData?.workflow_metrics) return 0
    const { total_started, total_completed } = statusData.workflow_metrics
    return total_started > 0 ? Math.round((total_completed / total_started) * 100) : 0
  }

  if (isLoading && !statusData) {
    return (
      <Card variant="elevated" className="animate-pulse">
        <CardContent spacing="md">
          <div className="flex items-center space-x-3">
            <div className="w-5 h-5 bg-gray-300 rounded-full"></div>
            <div className="h-4 bg-gray-300 rounded w-32"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!statusData) {
    return (
      <Card variant="elevated">
        <CardContent spacing="md">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <WifiOff className="h-5 w-5 text-red-500" />
              <span className="text-sm font-medium text-red-600">System Status Unavailable</span>
            </div>
            <Button variant="outline" size="xs" onClick={fetchSystemStatus}>
              <RefreshCw className="h-3 w-3" />
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card variant="elevated" className="w-full">
      <CardHeader spacing="sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {getStatusIcon(statusData.system_status)}
            <CardTitle level={3} className="text-lg">
              System Status
            </CardTitle>
            <div className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(statusData.system_status)}`}>
              {statusData.system_status.charAt(0).toUpperCase() + statusData.system_status.slice(1)}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {statusData.agents_enabled ? (
              <Wifi className="h-4 w-4 text-green-500" aria-label="Multi-agent system enabled" />
            ) : (
              <WifiOff className="h-4 w-4 text-gray-400" aria-label="Multi-agent system disabled" />
            )}
            <Button variant="ghost" size="xs" onClick={fetchSystemStatus} disabled={isLoading}>
              <RefreshCw className={`h-3 w-3 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
            {/* Last Updated Timestamp */}
            {lastUpdate && (
              <span className="ml-2 text-xs text-gray-500" title={lastUpdate}>
                Last updated: {format(new Date(lastUpdate), 'yyyy-MM-dd HH:mm:ss')}
              </span>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent spacing="md">
        {/* Error Message */}
        {error && (
          <div className="mb-2 p-2 bg-red-50 border border-red-200 text-red-700 rounded text-xs">
            Error: {error}
          </div>
        )}
        {/* Main Status Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          {/* Agent Health */}
          <div className="text-center">
            <div className="flex items-center justify-center space-x-1 mb-1">
              <Activity className="h-4 w-4 text-blue-500" />
              <span className="text-sm font-semibold text-blue-600">
                {statusData.metrics.healthy_agents}/{statusData.metrics.total_agents}
              </span>
            </div>
            <div className="text-xs text-gray-500">Agents Healthy</div>
            <div className="mt-1">
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <div 
                  className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
                  style={{ width: `${statusData.metrics.health_percentage}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Response Time */}
          <div className="text-center">
            <div className="flex items-center justify-center space-x-1 mb-1">
              {getResponseTimeIcon(statusData.metrics.average_response_time_ms)}
              <span className="text-sm font-semibold">
                {Math.round(statusData.metrics.average_response_time_ms)}ms
              </span>
            </div>
            <div className="text-xs text-gray-500">Avg Response</div>
          </div>

          {/* Active Workflows */}
          <div className="text-center">
            <div className="flex items-center justify-center space-x-1 mb-1">
              <Zap className="h-4 w-4 text-purple-500" />
              <span className="text-sm font-semibold text-purple-600">
                {statusData.active_workflows_count}
              </span>
            </div>
            <div className="text-xs text-gray-500">Active Workflows</div>
          </div>

          {/* Success Rate */}
          <div className="text-center">
            <div className="flex items-center justify-center space-x-1 mb-1">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <span className="text-sm font-semibold text-green-600">
                {calculateSuccessRate()}%
              </span>
            </div>
            <div className="text-xs text-gray-500">Success Rate</div>
          </div>
        </div>

        {/* Detailed Information */}
        {showDetails && (
          <div className="space-y-3">
            {/* Agent Status Details */}
            {statusData.agents_enabled && Object.keys(statusData.agent_health).length > 0 && (
              <div className="border-t pt-3">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Agent Details</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {Object.entries(statusData.agent_health).map(([agentName, health]) => (
                    <div key={agentName} className="flex items-center justify-between p-2 bg-gray-50 rounded text-xs">
                      <div className="flex items-center space-x-2">
                        {health.healthy ? (
                          <CheckCircle className="h-3 w-3 text-green-500" />
                        ) : (
                          <AlertTriangle className="h-3 w-3 text-red-500" />
                        )}
                        <span className="font-medium capitalize">
                          {agentName.replace('_', ' ')}
                        </span>
                      </div>
                      {health.response_time_ms && (
                        <span className="text-gray-500">
                          {Math.round(health.response_time_ms)}ms
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Workflow Metrics */}
            {statusData.workflow_metrics && (
              <div className="border-t pt-3">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Workflow Statistics</h4>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-lg font-bold text-blue-600">
                      {statusData.workflow_metrics.total_started}
                    </div>
                    <div className="text-xs text-gray-500">Started</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-green-600">
                      {statusData.workflow_metrics.total_completed}
                    </div>
                    <div className="text-xs text-gray-500">Completed</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-red-600">
                      {statusData.workflow_metrics.total_failed}
                    </div>
                    <div className="text-xs text-gray-500">Failed</div>
                  </div>
                </div>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="border-t pt-3">
                <div className="flex items-center space-x-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                  <AlertTriangle className="h-4 w-4" />
                  <span>{error}</span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="mt-4 pt-3 border-t flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-1">
            <Clock className="h-3 w-3" />
            <span>
              {lastUpdate ? format(new Date(lastUpdate), 'HH:mm:ss') : 'Never'}
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            {autoRefresh && (
              <div className="flex items-center space-x-1">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
                <span>Live</span>
              </div>
            )}
            
            <Button variant="ghost" size="xs">
              <ExternalLink className="h-3 w-3 mr-1" />
              Details
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}