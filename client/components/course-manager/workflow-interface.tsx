"use client"
import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/enhanced-card"
import { Button } from "@/components/ui/enhanced-button"
import { StatusBadge, ProgressBadge } from "@/components/ui/status-badge"
import { 
  Play,
  Pause,
  Square,
  RotateCcw,
  Settings,
  Zap,
  AlertTriangle,
  CheckCircle,
  Clock,
  Users,
  BarChart3,
  Activity,
  GitBranch,
  Cpu,
  RefreshCw,
  ExternalLink,
  Download,
  Eye,
  Edit3,
  Filter,
  Search
} from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { Input } from "@/components/ui/input"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { format, formatDistanceToNow } from "date-fns"

interface WorkflowStep {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
  startTime?: string
  endTime?: string
  duration?: number
  agent: string
  errorMessage?: string
  retryCount: number
  maxRetries: number
  output?: any
}

interface WorkflowInstance {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused' | 'cancelled'
  progress: number
  startTime: string
  endTime?: string
  estimatedCompletion?: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  type: 'course_generation' | 'content_review' | 'sop_processing' | 'quality_assessment'
  courseRequestId?: string
  companyName: string
  steps: WorkflowStep[]
  metadata: {
    totalSteps: number
    completedSteps: number
    failedSteps: number
    estimatedDuration: string
    resourceUsage: {
      cpu: number
      memory: number
      storage: number
    }
  }
  configuration: {
    parallelExecution: boolean
    autoRetry: boolean
    qualityThreshold: number
    timeoutMinutes: number
  }
}

interface WorkflowTemplate {
  id: string
  name: string
  description: string
  type: string
  steps: string[]
  defaultConfig: any
  usageCount: number
  successRate: number
}

interface WorkflowInterfaceProps {
  autoRefresh?: boolean
  refreshInterval?: number
}

export function WorkflowInterface({ autoRefresh = true, refreshInterval = 5000 }: WorkflowInterfaceProps) {
  const [workflows, setWorkflows] = useState<WorkflowInstance[]>([])
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [filterStatus, setFilterStatus] = useState("all")
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowInstance | null>(null)
  const [showConfigDialog, setShowConfigDialog] = useState(false)
  const [interventionNotes, setInterventionNotes] = useState("")
  const { fetchWithAuth } = useAuth()

  const loadWorkflows = async () => {
    try {
      const response = await fetchWithAuth('/api/workflows/active')
      if (response.ok) {
        const data = await response.json()
        setWorkflows(data)
      } else {
        // Mock data for development
        const mockWorkflows: WorkflowInstance[] = [
          {
            id: "wf_1",
            name: "TechCorp Course Generation",
            status: "running",
            progress: 65,
            startTime: "2025-01-15T14:30:00Z",
            estimatedCompletion: "2025-01-15T15:45:00Z",
            priority: "high",
            type: "course_generation",
            courseRequestId: "req_123",
            companyName: "TechCorp Solutions",
            steps: [
              {
                id: "step_1",
                name: "SOP Analysis",
                status: "completed",
                startTime: "2025-01-15T14:30:00Z",
                endTime: "2025-01-15T14:35:00Z",
                duration: 300,
                agent: "Course Planner",
                retryCount: 0,
                maxRetries: 3
              },
              {
                id: "step_2",
                name: "Curriculum Structure",
                status: "completed",
                startTime: "2025-01-15T14:35:00Z",
                endTime: "2025-01-15T14:42:00Z",
                duration: 420,
                agent: "Course Planner",
                retryCount: 0,
                maxRetries: 3
              },
              {
                id: "step_3",
                name: "Content Generation",
                status: "running",
                startTime: "2025-01-15T14:42:00Z",
                agent: "Content Creator",
                retryCount: 0,
                maxRetries: 3
              },
              {
                id: "step_4",
                name: "Quality Review",
                status: "pending",
                agent: "Quality Assurance",
                retryCount: 0,
                maxRetries: 3
              }
            ],
            metadata: {
              totalSteps: 4,
              completedSteps: 2,
              failedSteps: 0,
              estimatedDuration: "75 minutes",
              resourceUsage: {
                cpu: 45,
                memory: 62,
                storage: 23
              }
            },
            configuration: {
              parallelExecution: false,
              autoRetry: true,
              qualityThreshold: 0.8,
              timeoutMinutes: 120
            }
          },
          {
            id: "wf_2",
            name: "Manufacturing Safety Training",
            status: "completed",
            progress: 100,
            startTime: "2025-01-15T13:15:00Z",
            endTime: "2025-01-15T14:20:00Z",
            priority: "medium",
            type: "course_generation",
            courseRequestId: "req_124",
            companyName: "Global Manufacturing Inc",
            steps: [
              {
                id: "step_1",
                name: "SOP Analysis",
                status: "completed",
                startTime: "2025-01-15T13:15:00Z",
                endTime: "2025-01-15T13:22:00Z",
                duration: 420,
                agent: "Course Planner",
                retryCount: 0,
                maxRetries: 3
              },
              {
                id: "step_2",
                name: "Curriculum Structure",
                status: "completed",
                startTime: "2025-01-15T13:22:00Z",
                endTime: "2025-01-15T13:35:00Z",
                duration: 780,
                agent: "Course Planner",
                retryCount: 1,
                maxRetries: 3
              },
              {
                id: "step_3",
                name: "Content Generation",
                status: "completed",
                startTime: "2025-01-15T13:35:00Z",
                endTime: "2025-01-15T14:05:00Z",
                duration: 1800,
                agent: "Content Creator",
                retryCount: 0,
                maxRetries: 3
              },
              {
                id: "step_4",
                name: "Quality Review",
                status: "completed",
                startTime: "2025-01-15T14:05:00Z",
                endTime: "2025-01-15T14:20:00Z",
                duration: 900,
                agent: "Quality Assurance",
                retryCount: 0,
                maxRetries: 3
              }
            ],
            metadata: {
              totalSteps: 4,
              completedSteps: 4,
              failedSteps: 0,
              estimatedDuration: "65 minutes",
              resourceUsage: {
                cpu: 0,
                memory: 0,
                storage: 45
              }
            },
            configuration: {
              parallelExecution: false,
              autoRetry: true,
              qualityThreshold: 0.85,
              timeoutMinutes: 90
            }
          },
          {
            id: "wf_3",
            name: "Finance Communication Training",
            status: "failed",
            progress: 25,
            startTime: "2025-01-15T12:00:00Z",
            endTime: "2025-01-15T12:30:00Z",
            priority: "high",
            type: "course_generation",
            courseRequestId: "req_125",
            companyName: "Financial Services Co",
            steps: [
              {
                id: "step_1",
                name: "SOP Analysis",
                status: "completed",
                startTime: "2025-01-15T12:00:00Z",
                endTime: "2025-01-15T12:08:00Z",
                duration: 480,
                agent: "Course Planner",
                retryCount: 0,
                maxRetries: 3
              },
              {
                id: "step_2",
                name: "Curriculum Structure",
                status: "failed",
                startTime: "2025-01-15T12:08:00Z",
                endTime: "2025-01-15T12:30:00Z",
                agent: "Course Planner",
                retryCount: 3,
                maxRetries: 3,
                errorMessage: "Failed to parse SOP compliance requirements"
              },
              {
                id: "step_3",
                name: "Content Generation",
                status: "skipped",
                agent: "Content Creator",
                retryCount: 0,
                maxRetries: 3
              },
              {
                id: "step_4",
                name: "Quality Review",
                status: "skipped",
                agent: "Quality Assurance",
                retryCount: 0,
                maxRetries: 3
              }
            ],
            metadata: {
              totalSteps: 4,
              completedSteps: 1,
              failedSteps: 1,
              estimatedDuration: "70 minutes",
              resourceUsage: {
                cpu: 0,
                memory: 0,
                storage: 12
              }
            },
            configuration: {
              parallelExecution: false,
              autoRetry: true,
              qualityThreshold: 0.9,
              timeoutMinutes: 100
            }
          }
        ]
        setWorkflows(mockWorkflows)
      }
    } catch (error) {
      console.error('Failed to load workflows:', error)
    }
  }

  const loadTemplates = async () => {
    try {
      const response = await fetchWithAuth('/api/workflows/templates')
      if (response.ok) {
        const data = await response.json()
        setTemplates(data)
      } else {
        // Mock templates
        const mockTemplates: WorkflowTemplate[] = [
          {
            id: "template_1",
            name: "Standard Course Generation",
            description: "Default workflow for generating business English courses",
            type: "course_generation",
            steps: ["SOP Analysis", "Curriculum Structure", "Content Generation", "Quality Review"],
            defaultConfig: {
              parallelExecution: false,
              autoRetry: true,
              qualityThreshold: 0.8,
              timeoutMinutes: 120
            },
            usageCount: 45,
            successRate: 94.2
          },
          {
            id: "template_2",
            name: "Technical Communication Fast Track",
            description: "Accelerated workflow for technical communication courses",
            type: "course_generation",
            steps: ["SOP Analysis", "Content Generation", "Quality Review"],
            defaultConfig: {
              parallelExecution: true,
              autoRetry: true,
              qualityThreshold: 0.75,
              timeoutMinutes: 60
            },
            usageCount: 23,
            successRate: 89.7
          }
        ]
        setTemplates(mockTemplates)
      }
    } catch (error) {
      console.error('Failed to load templates:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    const loadData = async () => {
      await Promise.all([loadWorkflows(), loadTemplates()])
    }

    loadData()

    if (autoRefresh) {
      const interval = setInterval(loadWorkflows, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [autoRefresh, refreshInterval])

  const handleWorkflowAction = async (workflowId: string, action: 'pause' | 'resume' | 'cancel' | 'retry') => {
    try {
      const response = await fetchWithAuth(`/api/workflows/${workflowId}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes: interventionNotes })
      })

      if (response.ok) {
        await loadWorkflows()
        setInterventionNotes("")
      }
    } catch (error) {
      console.error(`Failed to ${action} workflow:`, error)
    }
  }

  const handleStepRetry = async (workflowId: string, stepId: string) => {
    try {
      const response = await fetchWithAuth(`/api/workflows/${workflowId}/steps/${stepId}/retry`, {
        method: 'POST'
      })

      if (response.ok) {
        await loadWorkflows()
      }
    } catch (error) {
      console.error('Failed to retry step:', error)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-red-700 bg-red-100'
      case 'high': return 'text-orange-700 bg-orange-100'
      case 'medium': return 'text-yellow-700 bg-yellow-100'
      case 'low': return 'text-green-700 bg-green-100'
      default: return 'text-gray-700 bg-gray-100'
    }
  }

  const filteredWorkflows = workflows.filter(workflow => {
    const matchesSearch = workflow.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         workflow.companyName.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterStatus === "all" || workflow.status === filterStatus
    return matchesSearch && matchesFilter
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        {[...Array(3)].map((_, i) => (
          <Card key={i} variant="elevated" className="animate-pulse">
            <CardContent spacing="md">
              <div className="h-24 bg-gray-200 rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Workflow Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card variant="elevated">
          <CardContent spacing="md">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Activity className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Active</p>
                <p className="text-2xl font-bold">
                  {workflows.filter(w => w.status === 'running').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="elevated">
          <CardContent spacing="md">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Completed</p>
                <p className="text-2xl font-bold">
                  {workflows.filter(w => w.status === 'completed').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="elevated">
          <CardContent spacing="md">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Failed</p>
                <p className="text-2xl font-bold">
                  {workflows.filter(w => w.status === 'failed').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="elevated">
          <CardContent spacing="md">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <BarChart3 className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Avg Success</p>
                <p className="text-2xl font-bold">
                  {workflows.length > 0 
                    ? Math.round((workflows.filter(w => w.status === 'completed').length / workflows.length) * 100)
                    : 0}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card variant="elevated">
        <CardContent spacing="md">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search workflows by name or company..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <div className="flex gap-2">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    Status: {filterStatus === "all" ? "All" : filterStatus}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => setFilterStatus("all")}>All Status</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterStatus("running")}>Running</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterStatus("completed")}>Completed</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterStatus("failed")}>Failed</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterStatus("paused")}>Paused</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              <Button variant="outline" size="sm" onClick={loadWorkflows}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Workflow List */}
      <div className="space-y-4">
        {filteredWorkflows.map((workflow) => (
          <Card key={workflow.id} variant="interactive" className="overflow-hidden">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <CardTitle className="text-xl">{workflow.name}</CardTitle>
                    <Badge className={getPriorityColor(workflow.priority)}>
                      {workflow.priority}
                    </Badge>
                    <StatusBadge status={workflow.status} showTooltip />
                  </div>
                  <p className="text-muted-foreground">
                    {workflow.companyName} • Started {formatDistanceToNow(new Date(workflow.startTime), { addSuffix: true })}
                    {workflow.estimatedCompletion && workflow.status === 'running' && (
                      <span> • Est. completion {formatDistanceToNow(new Date(workflow.estimatedCompletion), { addSuffix: true })}</span>
                    )}
                  </p>
                </div>
                
                <div className="flex items-center gap-2">
                  {workflow.status === 'running' && (
                    <Button size="sm" variant="outline" onClick={() => handleWorkflowAction(workflow.id, 'pause')}>
                      <Pause className="h-4 w-4" />
                    </Button>
                  )}
                  {workflow.status === 'paused' && (
                    <Button size="sm" variant="outline" onClick={() => handleWorkflowAction(workflow.id, 'resume')}>
                      <Play className="h-4 w-4" />
                    </Button>
                  )}
                  {workflow.status === 'failed' && (
                    <Button size="sm" variant="outline" onClick={() => handleWorkflowAction(workflow.id, 'retry')}>
                      <RotateCcw className="h-4 w-4" />
                    </Button>
                  )}
                  
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button size="sm" variant="outline" onClick={() => setSelectedWorkflow(workflow)}>
                        <Eye className="h-4 w-4" />
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                      <DialogHeader>
                        <DialogTitle>Workflow Details: {workflow.name}</DialogTitle>
                      </DialogHeader>
                      {selectedWorkflow && (
                        <WorkflowDetailView workflow={selectedWorkflow} onStepRetry={handleStepRetry} />
                      )}
                    </DialogContent>
                  </Dialog>
                </div>
              </div>
            </CardHeader>

            <CardContent spacing="md">
              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Progress</span>
                  <span className="text-sm text-muted-foreground">{workflow.progress}%</span>
                </div>
                <ProgressBadge 
                  progress={workflow.progress}
                  status={workflow.status}
                  showPercentage={false}
                />
              </div>

              {/* Steps Overview */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {workflow.steps.map((step, index) => (
                  <div key={step.id} className={`p-3 rounded-lg border ${getStatusColor(step.status)}`}>
                    <div className="flex items-center justify-between mb-1">
                      {getStatusIcon(step.status)}
                      <span className="text-xs font-medium">Step {index + 1}</span>
                    </div>
                    <p className="text-sm font-medium">{step.name}</p>
                    <p className="text-xs text-muted-foreground">{step.agent}</p>
                    {step.duration && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {Math.round(step.duration / 60)}m {step.duration % 60}s
                      </p>
                    )}
                    {step.errorMessage && (
                      <p className="text-xs text-red-600 mt-1 truncate" title={step.errorMessage}>
                        {step.errorMessage}
                      </p>
                    )}
                  </div>
                ))}
              </div>

              {/* Resource Usage */}
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-medium mb-2">Resource Usage</h4>
                <div className="grid grid-cols-3 gap-4 text-xs">
                  <div>
                    <div className="flex items-center justify-between">
                      <span>CPU</span>
                      <span>{workflow.metadata.resourceUsage.cpu}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                      <div 
                        className="bg-blue-600 h-1 rounded-full transition-all duration-300"
                        style={{ width: `${workflow.metadata.resourceUsage.cpu}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center justify-between">
                      <span>Memory</span>
                      <span>{workflow.metadata.resourceUsage.memory}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                      <div 
                        className="bg-green-600 h-1 rounded-full transition-all duration-300"
                        style={{ width: `${workflow.metadata.resourceUsage.memory}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center justify-between">
                      <span>Storage</span>
                      <span>{workflow.metadata.resourceUsage.storage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                      <div 
                        className="bg-purple-600 h-1 rounded-full transition-all duration-300"
                        style={{ width: `${workflow.metadata.resourceUsage.storage}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {filteredWorkflows.length === 0 && (
        <Card variant="elevated">
          <CardContent spacing="lg" className="text-center py-16">
            <Activity className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">No workflows found</h3>
            <p className="text-muted-foreground">
              No workflows match your current filters. Try adjusting your search criteria.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// Utility functions for status handling
const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed': return 'text-green-600 bg-green-50'
    case 'running': return 'text-blue-600 bg-blue-50'
    case 'failed': return 'text-red-600 bg-red-50'
    case 'pending': return 'text-gray-600 bg-gray-50'
    case 'paused': return 'text-yellow-600 bg-yellow-50'
    case 'cancelled': return 'text-gray-600 bg-gray-50'
    case 'skipped': return 'text-gray-400 bg-gray-50'
    default: return 'text-gray-600 bg-gray-50'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed': return <CheckCircle className="h-4 w-4" />
    case 'running': return <Activity className="h-4 w-4 animate-spin" />
    case 'failed': return <AlertTriangle className="h-4 w-4" />
    case 'pending': return <Clock className="h-4 w-4" />
    case 'paused': return <Pause className="h-4 w-4" />
    case 'cancelled': return <Square className="h-4 w-4" />
    default: return <Clock className="h-4 w-4" />
  }
}

// Detailed workflow view component
function WorkflowDetailView({ 
  workflow, 
  onStepRetry 
}: { 
  workflow: WorkflowInstance
  onStepRetry: (workflowId: string, stepId: string) => void
}) {
  return (
    <div className="space-y-6 py-4">
      <Tabs defaultValue="steps" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="steps">Steps</TabsTrigger>
          <TabsTrigger value="config">Configuration</TabsTrigger>
          <TabsTrigger value="resources">Resources</TabsTrigger>
        </TabsList>
        
        <TabsContent value="steps" className="space-y-4 mt-4">
          {workflow.steps.map((step, index) => (
            <div key={step.id} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-full ${getStatusColor(step.status)}`}>
                    {getStatusIcon(step.status)}
                  </div>
                  <div>
                    <h4 className="font-semibold">Step {index + 1}: {step.name}</h4>
                    <p className="text-sm text-muted-foreground">Agent: {step.agent}</p>
                  </div>
                </div>
                {step.status === 'failed' && step.retryCount < step.maxRetries && (
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => onStepRetry(workflow.id, step.id)}
                  >
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Retry ({step.retryCount}/{step.maxRetries})
                  </Button>
                )}
              </div>
              
              {step.startTime && (
                <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
                  <div>
                    <span className="font-medium">Started:</span> {format(new Date(step.startTime), 'HH:mm:ss')}
                  </div>
                  {step.endTime && (
                    <div>
                      <span className="font-medium">Completed:</span> {format(new Date(step.endTime), 'HH:mm:ss')}
                    </div>
                  )}
                  {step.duration && (
                    <div>
                      <span className="font-medium">Duration:</span> {Math.round(step.duration / 60)}m {step.duration % 60}s
                    </div>
                  )}
                </div>
              )}
              
              {step.errorMessage && (
                <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-700 font-medium">Error:</p>
                  <p className="text-sm text-red-600">{step.errorMessage}</p>
                </div>
              )}
            </div>
          ))}
        </TabsContent>
        
        <TabsContent value="config" className="mt-4">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 border rounded-lg">
                <h4 className="font-medium mb-2">Execution Mode</h4>
                <p className="text-sm text-muted-foreground">
                  {workflow.configuration.parallelExecution ? 'Parallel' : 'Sequential'}
                </p>
              </div>
              <div className="p-3 border rounded-lg">
                <h4 className="font-medium mb-2">Auto Retry</h4>
                <p className="text-sm text-muted-foreground">
                  {workflow.configuration.autoRetry ? 'Enabled' : 'Disabled'}
                </p>
              </div>
              <div className="p-3 border rounded-lg">
                <h4 className="font-medium mb-2">Quality Threshold</h4>
                <p className="text-sm text-muted-foreground">
                  {(workflow.configuration.qualityThreshold * 100).toFixed(0)}%
                </p>
              </div>
              <div className="p-3 border rounded-lg">
                <h4 className="font-medium mb-2">Timeout</h4>
                <p className="text-sm text-muted-foreground">
                  {workflow.configuration.timeoutMinutes} minutes
                </p>
              </div>
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="resources" className="mt-4">
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(workflow.metadata.resourceUsage).map(([resource, usage]) => (
                <div key={resource} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium capitalize">{resource}</h4>
                    <span className="text-2xl font-bold">{usage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        usage > 80 ? 'bg-red-500' : usage > 60 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${usage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}