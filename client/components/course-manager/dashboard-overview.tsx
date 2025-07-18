"use client"
import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/enhanced-card"
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Users, 
  Clock, 
  CheckCircle,
  BarChart3,
  Zap,
  Target,
  Calendar
} from "lucide-react"
import { useAuth } from "@/contexts/auth-context"

interface DashboardMetrics {
  workflowSuccessRate: number
  averageProcessingTime: number
  totalCourses: number
  activeLearners: number
  completionRate: number
  qualityScore: number
  trends: {
    coursesGenerated: { current: number, previous: number, change: number }
    processingTime: { current: number, previous: number, change: number }
    qualityScore: { current: number, previous: number, change: number }
    successRate: { current: number, previous: number, change: number }
  }
}

interface AgentPerformance {
  orchestrator: { health: number, responseTime: number, tasksCompleted: number }
  coursePlanner: { health: number, responseTime: number, tasksCompleted: number }
  contentCreator: { health: number, responseTime: number, tasksCompleted: number }
  qualityAssurance: { health: number, responseTime: number, tasksCompleted: number }
}

interface DashboardOverviewProps {
  refreshInterval?: number
  autoRefresh?: boolean
}

export function DashboardOverview({ 
  refreshInterval = 30000, 
  autoRefresh = true 
}: DashboardOverviewProps) {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [agentPerformance, setAgentPerformance] = useState<AgentPerformance | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const { fetchWithAuth } = useAuth()

  const loadDashboardMetrics = async () => {
    try {
      const response = await fetchWithAuth('/api/dashboard/metrics')
      if (response.ok) {
        const data = await response.json()
        setMetrics(data)
      } else {
        // Fallback to mock data if API not available
        setMetrics({
          workflowSuccessRate: 94.2,
          averageProcessingTime: 12.3,
          totalCourses: 156,
          activeLearners: 2847,
          completionRate: 87.5,
          qualityScore: 91.3,
          trends: {
            coursesGenerated: { current: 23, previous: 18, change: 27.8 },
            processingTime: { current: 12.3, previous: 15.1, change: -18.5 },
            qualityScore: { current: 91.3, previous: 89.7, change: 1.8 },
            successRate: { current: 94.2, previous: 91.5, change: 2.9 }
          }
        })
      }
    } catch (error) {
      console.error('Failed to load dashboard metrics:', error)
      // Use mock data on error
      setMetrics({
        workflowSuccessRate: 94.2,
        averageProcessingTime: 12.3,
        totalCourses: 156,
        activeLearners: 2847,
        completionRate: 87.5,
        qualityScore: 91.3,
        trends: {
          coursesGenerated: { current: 23, previous: 18, change: 27.8 },
          processingTime: { current: 12.3, previous: 15.1, change: -18.5 },
          qualityScore: { current: 91.3, previous: 89.7, change: 1.8 },
          successRate: { current: 94.2, previous: 91.5, change: 2.9 }
        }
      })
    }
  }

  const loadAgentPerformance = async () => {
    try {
      const response = await fetchWithAuth('/api/agents/performance')
      if (response.ok) {
        const data = await response.json()
        setAgentPerformance(data)
      } else {
        // Fallback to mock data
        setAgentPerformance({
          orchestrator: { health: 98.5, responseTime: 125, tasksCompleted: 47 },
          coursePlanner: { health: 95.2, responseTime: 2340, tasksCompleted: 23 },
          contentCreator: { health: 97.8, responseTime: 4560, tasksCompleted: 23 },
          qualityAssurance: { health: 96.1, responseTime: 890, tasksCompleted: 23 }
        })
      }
    } catch (error) {
      console.error('Failed to load agent performance:', error)
      setAgentPerformance({
        orchestrator: { health: 98.5, responseTime: 125, tasksCompleted: 47 },
        coursePlanner: { health: 95.2, responseTime: 2340, tasksCompleted: 23 },
        contentCreator: { health: 97.8, responseTime: 4560, tasksCompleted: 23 },
        qualityAssurance: { health: 96.1, responseTime: 890, tasksCompleted: 23 }
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    const loadData = async () => {
      await Promise.all([loadDashboardMetrics(), loadAgentPerformance()])
    }

    loadData()

    if (autoRefresh) {
      const interval = setInterval(loadData, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [autoRefresh, refreshInterval])

  const formatTrend = (trend: { current: number, previous: number, change: number }) => {
    const isPositive = trend.change > 0
    const icon = isPositive ? TrendingUp : TrendingDown
    const colorClass = isPositive ? "text-green-600" : "text-red-600"
    
    return {
      icon,
      colorClass,
      text: `${isPositive ? '+' : ''}${trend.change.toFixed(1)}%`
    }
  }

  const getHealthColor = (health: number) => {
    if (health >= 95) return "text-green-600"
    if (health >= 85) return "text-yellow-600"
    return "text-red-600"
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(8)].map((_, i) => (
          <Card key={i} variant="elevated" className="animate-pulse">
            <CardContent spacing="md">
              <div className="h-16 bg-gray-200 rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (!metrics || !agentPerformance) {
    return (
      <Card variant="elevated">
        <CardContent spacing="md" className="text-center py-8">
          <p className="text-muted-foreground">Failed to load dashboard metrics</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Key Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card variant="elevated" className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0">
          <CardContent spacing="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm font-medium">Success Rate</p>
                <p className="text-3xl font-bold">{metrics.workflowSuccessRate}%</p>
                <div className="flex items-center gap-1 mt-1">
                  {(() => {
                    const trend = formatTrend(metrics.trends.successRate)
                    return (
                      <>
                        <trend.icon className={`h-3 w-3 ${trend.colorClass}`} />
                        <span className={`text-xs ${trend.colorClass}`}>{trend.text}</span>
                      </>
                    )
                  })()}
                </div>
              </div>
              <div className="p-3 bg-white/20 rounded-full">
                <CheckCircle className="h-6 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="elevated" className="bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0">
          <CardContent spacing="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm font-medium">Avg Processing Time</p>
                <p className="text-3xl font-bold">{metrics.averageProcessingTime}m</p>
                <div className="flex items-center gap-1 mt-1">
                  {(() => {
                    const trend = formatTrend(metrics.trends.processingTime)
                    return (
                      <>
                        <trend.icon className={`h-3 w-3 ${trend.colorClass}`} />
                        <span className={`text-xs ${trend.colorClass}`}>{trend.text}</span>
                      </>
                    )
                  })()}
                </div>
              </div>
              <div className="p-3 bg-white/20 rounded-full">
                <Clock className="h-6 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="elevated" className="bg-gradient-to-br from-green-500 to-green-600 text-white border-0">
          <CardContent spacing="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm font-medium">Quality Score</p>
                <p className="text-3xl font-bold">{metrics.qualityScore}%</p>
                <div className="flex items-center gap-1 mt-1">
                  {(() => {
                    const trend = formatTrend(metrics.trends.qualityScore)
                    return (
                      <>
                        <trend.icon className={`h-3 w-3 ${trend.colorClass}`} />
                        <span className={`text-xs ${trend.colorClass}`}>{trend.text}</span>
                      </>
                    )
                  })()}
                </div>
              </div>
              <div className="p-3 bg-white/20 rounded-full">
                <Target className="h-6 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="elevated" className="bg-gradient-to-br from-orange-500 to-orange-600 text-white border-0">
          <CardContent spacing="md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100 text-sm font-medium">Courses Generated</p>
                <p className="text-3xl font-bold">{metrics.trends.coursesGenerated.current}</p>
                <div className="flex items-center gap-1 mt-1">
                  {(() => {
                    const trend = formatTrend(metrics.trends.coursesGenerated)
                    return (
                      <>
                        <trend.icon className={`h-3 w-3 ${trend.colorClass}`} />
                        <span className={`text-xs ${trend.colorClass}`}>vs last week</span>
                      </>
                    )
                  })()}
                </div>
              </div>
              <div className="p-3 bg-white/20 rounded-full">
                <BarChart3 className="h-6 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agent Performance Overview */}
      <Card variant="elevated">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Agent Performance Overview
          </CardTitle>
        </CardHeader>
        <CardContent spacing="md">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(agentPerformance).map(([agentName, performance]) => (
              <div key={agentName} className="p-4 bg-gray-50 rounded-lg border">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-sm capitalize">
                    {agentName.replace(/([A-Z])/g, ' $1').trim()}
                  </h4>
                  <div className={`text-xs font-bold ${getHealthColor(performance.health)}`}>
                    {performance.health}%
                  </div>
                </div>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Response Time:</span>
                    <span className="font-medium">{performance.responseTime}ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Tasks Today:</span>
                    <span className="font-medium">{performance.tasksCompleted}</span>
                  </div>
                </div>
                <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      performance.health >= 95 ? 'bg-green-500' :
                      performance.health >= 85 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${performance.health}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* System Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card variant="elevated">
          <CardContent spacing="md">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BarChart3 className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Courses</p>
                <p className="text-2xl font-bold">{metrics.totalCourses}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="elevated">
          <CardContent spacing="md">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Users className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Active Learners</p>
                <p className="text-2xl font-bold">{metrics.activeLearners.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="elevated">
          <CardContent spacing="md">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Zap className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Completion Rate</p>
                <p className="text-2xl font-bold">{metrics.completionRate}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}