"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/enhanced-card'
import { Button } from '@/components/ui/enhanced-button'
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  RefreshCw, 
  Zap,
  Brain,
  FileCheck,
  Settings,
  Wifi,
  WifiOff
} from 'lucide-react'
import { useAuth } from '@/contexts/auth-context'
import { format } from 'date-fns'

interface AgentStatus {
  agent: string
  healthy: boolean
  response_time_ms?: number
  status?: string
  error?: string
  checked_at: string
  capabilities?: {
    agent_name?: string
    version?: string
    features?: string[]
  }
  metrics?: {
    requests_processed?: number
    average_response_time?: number
    error_rate?: number
  }
}

interface AgentHealthData {
  agents_enabled: boolean
  orchestrator_available: boolean
  agent_health: Record<string, AgentStatus>
  system_status: 'operational' | 'degraded' | 'offline'
  checked_at: string
  error?: string
}

interface AgentHealthMonitorProps {
  autoRefresh?: boolean
  refreshInterval?: number
  onHealthChange?: (health: AgentHealthData) => void
}

export function AgentHealthMonitor({ 
  autoRefresh = true, 
  refreshInterval = 30000, // 30 seconds
  onHealthChange 
}: AgentHealthMonitorProps) {
  const [healthData, setHealthData] = useState<AgentHealthData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const { fetchWithAuth } = useAuth()

  const agentInfo = {
    orchestrator: {
      name: 'Orchestrator',
      description: 'Coordinates workflow between agents',
      icon: Settings,
      color: 'text-purple-600'
    },
    course_planner: {
      name: 'Course Planner',
      description: 'Analyzes requirements and creates curriculum',
      icon: Brain,
      color: 'text-blue-600'
    },
    content_creator: {
      name: 'Content Creator',
      description: 'Generates lessons and exercises',
      icon: Zap,
      color: 'text-yellow-600'
    },
    quality_assurance: {
      name: 'Quality Assurance',
      description: 'Reviews and improves content quality',
      icon: FileCheck,
      color: 'text-green-600'
    }
  }

  const fetchAgentHealth = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetchWithAuth('/api/agents/status')
      
      if (response.ok) {
        const data = await response.json()
        setHealthData(data)
        setLastRefresh(new Date().toISOString())
        onHealthChange?.(data)
      } else {
        throw new Error(`Failed to fetch agent status: ${response.status}`)
      }
    } catch (err) {
      console.error('Error fetching agent health:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch agent health')
      
      // Set offline status if fetch fails
      setHealthData({
        agents_enabled: false,
        orchestrator_available: false,
        agent_health: {},
        system_status: 'offline',
        checked_at: new Date().toISOString(),
        error: err instanceof Error ? err.message : 'Connection failed'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const testAgentSystem = async () => {
    setIsLoading(true)
    
    try {
      const response = await fetchWithAuth('/api/agents/test', {
        method: 'POST'
      })
      
      if (response.ok) {
        const data = await response.json()
        console.log('Agent system test results:', data)
        
        // Refresh health after test
        await fetchAgentHealth()
      } else {
        throw new Error(`Agent system test failed: ${response.status}`)
      }
    } catch (err) {
      console.error('Error testing agent system:', err)
      setError(err instanceof Error ? err.message : 'Agent system test failed')
    } finally {
      setIsLoading(false)
    }
  }

  // Auto-refresh functionality
  useEffect(() => {
    if (autoRefresh) {
      // Initial fetch
      fetchAgentHealth()
      
      // Set up interval
      const interval = setInterval(fetchAgentHealth, refreshInterval)
      
      return () => clearInterval(interval)
    } else {
      // Fetch once if auto-refresh is disabled
      fetchAgentHealth()
    }
  }, [autoRefresh, refreshInterval])

  const getSystemStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return 'text-green-600 bg-green-50 border-green-200'
      case 'degraded': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'offline': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getAgentStatusIcon = (agent: AgentStatus) => {
    if (agent.healthy) {
      return <CheckCircle className="h-5 w-5 text-green-500" />
    } else {
      return <AlertTriangle className="h-5 w-5 text-red-500" />
    }
  }

  const getResponseTimeColor = (responseTime?: number) => {
    if (!responseTime) return 'text-gray-500'
    if (responseTime < 1000) return 'text-green-600'
    if (responseTime < 3000) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (isLoading && !healthData) {
    return (
      <Card variant="elevated">
        <CardContent spacing="md">
          <div className="flex items-center justify-center p-8">
            <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
            <span className="ml-3 text-lg">Checking agent health...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!healthData) {
    return (
      <Card variant="elevated">
        <CardContent spacing="md">
          <div className="text-center p-8">
            <WifiOff className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-700 mb-2">
              Unable to Connect
            </h3>
            <p className="text-gray-500 mb-4">
              Cannot reach the agent monitoring system
            </p>
            <Button onClick={fetchAgentHealth} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry Connection
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  const healthyAgents = Object.values(healthData.agent_health).filter(agent => agent.healthy).length
  const totalAgents = Object.values(healthData.agent_health).length

  return (
    <Card variant="elevated" className="w-full">
      <CardHeader spacing="lg">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle level={2} className="text-xl flex items-center gap-2">
              <Activity className="h-6 w-6" />
              Agent Health Monitor
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Real-time status of AI agent system
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchAgentHealth}
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={testAgentSystem}
              disabled={isLoading || !healthData.agents_enabled}
            >
              Test System
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent spacing="lg">
        {/* System Status Overview */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold">System Status</h4>
            <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getSystemStatusColor(healthData.system_status)}`}>
              {healthData.system_status.charAt(0).toUpperCase() + healthData.system_status.slice(1)}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {healthyAgents}/{totalAgents}
              </div>
              <div className="text-sm text-muted-foreground">Agents Online</div>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center gap-2">
                {healthData.agents_enabled ? (
                  <Wifi className="h-5 w-5 text-green-500" />
                ) : (
                  <WifiOff className="h-5 w-5 text-red-500" />
                )}
                <span className="text-sm font-medium">
                  {healthData.agents_enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
              <div className="text-sm text-muted-foreground">Multi-Agent System</div>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center gap-2">
                {healthData.orchestrator_available ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : (
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                )}
                <span className="text-sm font-medium">
                  {healthData.orchestrator_available ? 'Available' : 'Unavailable'}
                </span>
              </div>
              <div className="text-sm text-muted-foreground">Orchestrator</div>
            </div>
          </div>
        </div>

        {/* Individual Agent Status */}
        <div className="space-y-4">
          <h4 className="text-lg font-semibold">Agent Status</h4>
          
          {Object.entries(healthData.agent_health).map(([agentKey, agent]) => {
            const agentConfig = agentInfo[agentKey as keyof typeof agentInfo]
            if (!agentConfig) return null
            
            const IconComponent = agentConfig.icon
            
            return (
              <div key={agentKey} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <IconComponent className={`h-6 w-6 ${agentConfig.color}`} />
                    <div>
                      <h5 className="font-semibold">{agentConfig.name}</h5>
                      <p className="text-sm text-muted-foreground">
                        {agentConfig.description}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {getAgentStatusIcon(agent)}
                    <span className={`text-sm font-medium ${agent.healthy ? 'text-green-600' : 'text-red-600'}`}>
                      {agent.healthy ? 'Healthy' : 'Unhealthy'}
                    </span>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Status:</span>
                    <div className="font-medium">
                      {agent.status || (agent.healthy ? 'Online' : 'Offline')}
                    </div>
                  </div>
                  
                  {agent.response_time_ms && (
                    <div>
                      <span className="text-muted-foreground">Response:</span>
                      <div className={`font-medium ${getResponseTimeColor(agent.response_time_ms)}`}>
                        {agent.response_time_ms}ms
                      </div>
                    </div>
                  )}
                  
                  <div>
                    <span className="text-muted-foreground">Last Check:</span>
                    <div className="font-medium">
                      {format(new Date(agent.checked_at), 'HH:mm:ss')}
                    </div>
                  </div>
                  
                  {agent.capabilities?.version && (
                    <div>
                      <span className="text-muted-foreground">Version:</span>
                      <div className="font-medium">
                        {agent.capabilities.version}
                      </div>
                    </div>
                  )}
                </div>
                
                {agent.error && (
                  <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                    <AlertTriangle className="h-4 w-4 inline mr-1" />
                    {agent.error}
                  </div>
                )}
                
                {agent.capabilities?.features && agent.capabilities.features.length > 0 && (
                  <div className="mt-3">
                    <span className="text-sm text-muted-foreground">Features:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {agent.capabilities.features.map((feature, index) => (
                        <span key={index} className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )
          })}
          
          {Object.keys(healthData.agent_health).length === 0 && (
            <div className="text-center py-8">
              <Settings className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-700 mb-2">
                No Agent Data Available
              </h3>
              <p className="text-gray-500 mb-4">
                {healthData.agents_enabled 
                  ? "Agent health data is not available at the moment."
                  : "The multi-agent system is currently disabled."
                }
              </p>
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2 text-red-800">
              <AlertTriangle className="h-4 w-4" />
              <span className="font-semibold">Connection Error</span>
            </div>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        )}

        {/* Footer */}
        <div className="mt-6 pt-4 border-t flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-4">
            {lastRefresh && (
              <span>Last updated: {format(new Date(lastRefresh), 'HH:mm:ss')}</span>
            )}
            {autoRefresh && (
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <span>Auto-refresh every {refreshInterval / 1000}s</span>
              </div>
            )}
          </div>
          
          <div>
            System checked at: {format(new Date(healthData.checked_at), 'MMM dd, HH:mm:ss')}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}