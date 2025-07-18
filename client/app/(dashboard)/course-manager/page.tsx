"use client"
import { useState, useEffect } from "react"
import { CourseManagerRequest } from "@/lib/types"
import { Button } from "@/components/ui/enhanced-button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/enhanced-card"
import { StatusBadge, ProgressBadge } from "@/components/ui/status-badge"
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertCircle, 
  Play, 
  FileText, 
  Download, 
  Eye,
  Users,
  Calendar,
  Target,
  BarChart3,
  Filter,
  Search,
  MoreHorizontal,
  ExternalLink,
  Sparkles,
  TrendingUp,
  Activity
} from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { WorkflowStatusTracker, AgentHealthMonitor, SystemStatusIndicator, CourseCreationFunnel, HistoricalPerformance, QualityControlPipeline } from "@/components/course-manager"
import { format, formatDistanceToNow } from "date-fns"

// Enhanced mock data with more realistic details
const mockCourseRequests = [
  {
    id: 1,
    company_name: "TechCorp Solutions",
    industry: "Technology",
    status: "submitted",
    priority: "high",
    submitted_by: "Alice Johnson",
    submitted_at: "2025-01-11T10:30:00Z",
    training_goals: "Improve technical communication and client presentations for our global development team",
    current_english_level: "B1",
    target_english_level: "B2",
    participant_count: 25,
    duration_weeks: 8,
    estimated_budget: 15000,
    urgency: "high",
    sop_files: [
      { name: "TechCorp_Communication_Guidelines.pdf", size: "2.3 MB", type: "guidelines" },
      { name: "Client_Interaction_SOP.docx", size: "1.1 MB", type: "procedures" },
      { name: "Technical_Presentation_Standards.pdf", size: "800 KB", type: "standards" }
    ],
    notes: "Focus on technical vocabulary and presentation skills for client-facing roles."
  },
  {
    id: 2,
    company_name: "Global Manufacturing Inc",
    industry: "Manufacturing",
    status: "under_review",
    priority: "medium",
    submitted_by: "Bob Smith",
    submitted_at: "2025-01-10T14:15:00Z",
    training_goals: "Safety communication and team coordination across multiple shifts",
    current_english_level: "A2",
    target_english_level: "B1",
    participant_count: 40,
    duration_weeks: 12,
    estimated_budget: 22000,
    urgency: "medium",
    sop_files: [
      { name: "Safety_Protocols.pdf", size: "4.2 MB", type: "safety" },
      { name: "Team_Communication_Standards.pdf", size: "1.8 MB", type: "communication" },
      { name: "Equipment_Operation_Manual.pdf", size: "3.5 MB", type: "operations" }
    ],
    notes: "Emphasis on safety-critical communication and shift handover procedures."
  },
  {
    id: 3,
    company_name: "Financial Services Co",
    industry: "Finance",
    status: "generation_in_progress",
    priority: "high",
    submitted_by: "Carol Davis",
    submitted_at: "2025-01-09T09:45:00Z",
    training_goals: "Client advisory and regulatory compliance communication",
    current_english_level: "B1",
    target_english_level: "B2",
    participant_count: 15,
    duration_weeks: 6,
    estimated_budget: 12000,
    urgency: "high",
    workflow_id: "mock_workflow_3_1736675820",
    generation_progress: 75,
    sop_files: [
      { name: "Compliance_Communication.pdf", size: "3.1 MB", type: "compliance" },
      { name: "Client_Advisory_Guidelines.docx", size: "2.0 MB", type: "guidelines" }
    ],
    notes: "Focus on regulatory language and client-facing communication in financial contexts."
  },
  {
    id: 4,
    company_name: "Healthcare Innovation Labs",
    industry: "Healthcare",
    status: "approved",
    priority: "high",
    submitted_by: "Dr. Sarah Chen",
    submitted_at: "2025-01-08T16:20:00Z",
    training_goals: "Medical communication and patient interaction skills",
    current_english_level: "B2",
    target_english_level: "C1",
    participant_count: 20,
    duration_weeks: 10,
    estimated_budget: 18000,
    urgency: "high",
    course_id: "course_healthcare_001",
    quality_score: 92,
    sop_files: [
      { name: "Patient_Communication_Protocol.pdf", size: "2.8 MB", type: "medical" },
      { name: "Medical_Terminology_Standards.pdf", size: "4.1 MB", type: "terminology" }
    ],
    notes: "High-precision medical English with emphasis on patient safety communication."
  }
]

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'high': return 'text-red-600 bg-red-50 border-red-200'
    case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    case 'low': return 'text-green-600 bg-green-50 border-green-200'
    default: return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

export default function CourseManagerPage() {
  const [courseRequests, setCourseRequests] = useState<CourseManagerRequest[]>(mockCourseRequests)
  const [selectedRequest, setSelectedRequest] = useState<CourseManagerRequest | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [filterStatus, setFilterStatus] = useState("all")
  const [agentHealthData, setAgentHealthData] = useState<any>(null)
  const [showHealthMonitor, setShowHealthMonitor] = useState(false)
  const [activeWorkflows, setActiveWorkflows] = useState<Record<string, any>>({})
  const { user, fetchWithAuth } = useAuth()

  // Filter and search logic
  const filteredRequests = courseRequests.filter(request => {
    const matchesSearch = request.company_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         request.industry.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         request.submitted_by.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterStatus === "all" || request.status === filterStatus
    return matchesSearch && matchesFilter
  })

  const handleApprove = async (requestId: number) => {
    setIsProcessing(true)
    try {
      const response = await fetchWithAuth(`/api/agents/generate-course-with-agents?course_request_id=${requestId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const result = await response.json()
        
        // Update request with workflow information
        const foundRequest = courseRequests.find(req => req.id === requestId)
        if (!foundRequest) return
        
        const updatedRequest = {
          ...foundRequest,
          status: result.course_generated ? 'approved' : 'generation_in_progress',
          workflow_id: result.workflow_id,
          generation_method: result.method
        }
        
        setCourseRequests(prev => 
          prev.map(req => 
            req.id === requestId ? updatedRequest : req
          )
        )
        
        // Track active workflow
        if (result.workflow_id && !result.course_generated) {
          setActiveWorkflows(prev => ({
            ...prev,
            [result.workflow_id]: {
              workflow_id: result.workflow_id,
              course_request_id: requestId,
              company_name: updatedRequest?.company_name || 'Unknown',
              status: result.status || 'in_progress',
              method: result.method
            }
          }))
        }
        
        // If using real agents, implement more sophisticated progress tracking
        if (result.method === 'real_agent_workflow' && !result.course_generated) {
          // Start polling for real workflow progress
          startWorkflowProgressTracking(requestId, result.workflow_id)
        } else if (result.method === 'mock_generation') {
          // Simulate realistic progress for mock generation
          simulateMockProgress(requestId, result)
        } else if (result.course_generated) {
          // Course is already completed
          setCourseRequests(prev => 
            prev.map(req => 
              req.id === requestId 
                ? { 
                    ...req, 
                    status: 'approved',
                    quality_score: result.quality_score,
                    course_id: `course_${req.company_name.toLowerCase().replace(/\s+/g, '_')}_${Date.now()}`
                  }
                : req
            )
          )
        }
      } else {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }
    } catch (error) {
      console.error('Error approving request:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  const startWorkflowProgressTracking = async (requestId: number, workflowId: string) => {
    let attempts = 0
    const maxAttempts = 60 // 5 minutes max
    
    const checkProgress = async () => {
      try {
        const response = await fetchWithAuth(`/api/agents/workflow/${workflowId}`)
        
        if (response.ok) {
          const workflowData = await response.json()
          const workflow = workflowData.workflow
          
          // Update progress based on workflow status
          let progress = 0
          switch (workflow.status) {
            case 'pending':
              progress = 10
              break
            case 'planning':
              progress = 25
              break
            case 'content_creation':
              progress = 60
              break
            case 'quality_review':
              progress = 85
              break
            case 'completed':
              progress = 100
              break
            case 'failed':
              progress = 0
              break
          }
          
          setCourseRequests(prev => 
            prev.map(req => 
              req.id === requestId 
                ? { 
                    ...req, 
                    generation_progress: progress,
                    workflow_status: workflow.status,
                    status: workflow.status === 'completed' ? 'approved' : 
                            workflow.status === 'failed' ? 'rejected' : 'generation_in_progress'
                  }
                : req
            )
          )
          
          // If completed or failed, stop tracking
          if (workflow.status === 'completed' || workflow.status === 'failed') {
            if (workflow.status === 'completed') {
              setCourseRequests(prev => 
                prev.map(req => 
                  req.id === requestId 
                    ? { 
                        ...req, 
                        quality_score: workflow.quality_score,
                        course_id: `course_${req.company_name.toLowerCase().replace(/\s+/g, '_')}_${Date.now()}`
                      }
                    : req
                )
              )
            }
            return
          }
          
          // Continue polling if still in progress
          if (attempts < maxAttempts) {
            attempts++
            setTimeout(checkProgress, 5000) // Check every 5 seconds
          }
        }
      } catch (error) {
        console.error('Error checking workflow progress:', error)
        // Fallback to mock progress on error
        simulateMockProgress(requestId, { quality_score: 85 })
      }
    }
    
    // Start checking progress
    checkProgress()
  }

  const simulateMockProgress = (requestId: number, result: any) => {
    let progress = 0
    const progressInterval = setInterval(() => {
      progress += Math.random() * 15 + 10 // Variable progress increments
      setCourseRequests(prev => 
        prev.map(req => 
          req.id === requestId 
            ? { ...req, generation_progress: Math.min(progress, 100) }
            : req
        )
      )
      
      if (progress >= 100) {
        clearInterval(progressInterval)
        setCourseRequests(prev => 
          prev.map(req => 
            req.id === requestId 
              ? { 
                  ...req, 
                  status: 'approved', 
                  generation_progress: undefined,
                  quality_score: result.quality_score || Math.floor(Math.random() * 15) + 85,
                  course_id: `course_${req.company_name.toLowerCase().replace(/\s+/g, '_')}_${Date.now()}`
                }
              : req
          )
        )
      }
    }, 800)
  }

  // Load agent health data on component mount
  useEffect(() => {
    const loadAgentHealth = async () => {
      try {
        const response = await fetchWithAuth('/api/agents/health/summary')
        if (response.ok) {
          const data = await response.json()
          setAgentHealthData(data)
        }
      } catch (error) {
        console.error('Failed to load agent health data:', error)
      }
    }

    loadAgentHealth()
    
    // Refresh health data every 30 seconds
    const healthInterval = setInterval(loadAgentHealth, 30000)
    
    return () => clearInterval(healthInterval)
  }, [])

  // Handle workflow completion callback
  const handleWorkflowComplete = (workflowId: string, result: any) => {
    // Update course request status
    setCourseRequests(prev => 
      prev.map(req => 
        req.workflow_id === workflowId 
          ? { 
              ...req, 
              status: 'approved',
              quality_score: result.quality_score,
              course_id: `course_${req.company_name.toLowerCase().replace(/\s+/g, '_')}_${Date.now()}`
            }
          : req
      )
    )
    
    // Remove from active workflows
    setActiveWorkflows(prev => {
      const updated = { ...prev }
      delete updated[workflowId]
      return updated
    })
  }

  // Handle workflow error callback
  const handleWorkflowError = (workflowId: string, error: any) => {
    // Update course request status
    setCourseRequests(prev => 
      prev.map(req => 
        req.workflow_id === workflowId 
          ? { ...req, status: 'rejected' }
          : req
      )
    )
    
    // Remove from active workflows
    setActiveWorkflows(prev => {
      const updated = { ...prev }
      delete updated[workflowId]
      return updated
    })
  }

  const handleReject = (requestId: number) => {
    setCourseRequests(prev => 
      prev.map(req => 
        req.id === requestId 
          ? { ...req, status: 'rejected' }
          : req
      )
    )
  }

  const pendingRequests = filteredRequests.filter(req => 
    ['submitted', 'under_review'].includes(req.status)
  )
  
  const inProgressRequests = filteredRequests.filter(req => 
    req.status === 'generation_in_progress'
  )
  
  const completedRequests = filteredRequests.filter(req => 
    ['approved', 'rejected'].includes(req.status)
  )

  // Calculate dashboard metrics
  const totalBudget = courseRequests.reduce((sum, req) => sum + (req.estimated_budget || 0), 0)
  const totalParticipants = courseRequests.reduce((sum, req) => sum + req.participant_count, 0)
  const avgQualityScore = completedRequests.filter(req => req.quality_score).reduce((sum, req, _, arr) => 
    sum + (req.quality_score || 0) / arr.length, 0
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30">
      <div className="space-y-8 p-8">
        {/* Header Section */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="space-y-2">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
              Course Manager Dashboard
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl">
              Review, approve, and monitor AI-powered course generation requests from sales teams
            </p>
          </div>
          
          {/* Quick Actions */}
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm">
              <BarChart3 className="h-4 w-4 mr-2" />
              Analytics
            </Button>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export Report
            </Button>
          </div>
        </div>

        {/* System Status Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <SystemStatusIndicator 
              autoRefresh={true}
              refreshInterval={30000}
              showDetails={true}
              onStatusChange={(status) => setAgentHealthData(status)}
            />
          </div>
          <div className="space-y-4">
            <div className="text-right">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setShowHealthMonitor(!showHealthMonitor)}
              >
                <Activity className="h-4 w-4 mr-2" />
                {showHealthMonitor ? 'Hide' : 'Show'} Agent Details
              </Button>
            </div>
          </div>
        </div>

        {/* Agent Health Monitor */}
        {showHealthMonitor && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AgentHealthMonitor 
              autoRefresh={true}
              refreshInterval={30000}
              onHealthChange={(health) => setAgentHealthData(health)}
            />
            <CourseCreationFunnel />
          </div>
          
        )}
        <HistoricalPerformance />
        <QualityControlPipeline />

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card variant="elevated" className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0">
            <CardContent spacing="md">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm font-medium">Pending Review</p>
                  <p className="text-3xl font-bold">{pendingRequests.length}</p>
                  {agentHealthData?.system_status && (
                    <p className="text-xs text-blue-200 mt-1">
                      System: {agentHealthData.system_status}
                    </p>
                  )}
                </div>
                <div className="p-3 bg-white/20 rounded-full">
                  <Clock className="h-6 w-6" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card variant="elevated" className="bg-gradient-to-br from-amber-500 to-orange-500 text-white border-0">
            <CardContent spacing="md">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-amber-100 text-sm font-medium">In Progress</p>
                  <p className="text-3xl font-bold">{inProgressRequests.length}</p>
                  {agentHealthData?.active_workflows_count !== undefined && (
                    <p className="text-xs text-amber-200 mt-1">
                      Active: {agentHealthData.active_workflows_count}
                    </p>
                  )}
                </div>
                <div className="p-3 bg-white/20 rounded-full">
                  <Sparkles className="h-6 w-6" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card variant="elevated" className="bg-gradient-to-br from-green-500 to-emerald-500 text-white border-0">
            <CardContent spacing="md">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100 text-sm font-medium">Total Learners</p>
                  <p className="text-3xl font-bold">{totalParticipants.toLocaleString()}</p>
                  {agentHealthData?.metrics?.healthy_agents !== undefined && (
                    <p className="text-xs text-green-200 mt-1">
                      Agents: {agentHealthData.metrics.healthy_agents}/{agentHealthData.metrics.total_agents}
                    </p>
                  )}
                </div>
                <div className="p-3 bg-white/20 rounded-full">
                  <Users className="h-6 w-6" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card variant="elevated" className="bg-gradient-to-br from-purple-500 to-indigo-500 text-white border-0">
            <CardContent spacing="md">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100 text-sm font-medium">Avg Quality</p>
                  <p className="text-3xl font-bold">{avgQualityScore ? Math.round(avgQualityScore) : '--'}%</p>
                  {agentHealthData?.workflow_metrics && (
                    <p className="text-xs text-purple-200 mt-1">
                      Success: {agentHealthData.workflow_metrics.total_completed}/{agentHealthData.workflow_metrics.total_started}
                    </p>
                  )}
                </div>
                <div className="p-3 bg-white/20 rounded-full">
                  <TrendingUp className="h-6 w-6" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search and Filter Controls */}
        <Card variant="elevated">
          <CardContent spacing="md">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search by company, industry, or sales rep..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline">
                    <Filter className="h-4 w-4 mr-2" />
                    Filter: {filterStatus === "all" ? "All Status" : filterStatus.replace('_', ' ')}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => setFilterStatus("all")}>All Status</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterStatus("submitted")}>Submitted</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterStatus("under_review")}>Under Review</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterStatus("generation_in_progress")}>In Progress</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterStatus("approved")}>Approved</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </CardContent>
        </Card>

        {/* Main Content Tabs */}
        <Tabs defaultValue="pending" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-auto lg:grid-cols-3">
            <TabsTrigger value="pending" className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Pending ({pendingRequests.length})
            </TabsTrigger>
            <TabsTrigger value="in-progress" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              In Progress ({inProgressRequests.length})
            </TabsTrigger>
            <TabsTrigger value="completed" className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              Completed ({completedRequests.length})
            </TabsTrigger>
          </TabsList>

          {/* Pending Requests Tab */}
          <TabsContent value="pending" className="space-y-6">
            {pendingRequests.length === 0 ? (
              <Card variant="interactive" className="py-16">
                <CardContent className="text-center">
                  <CheckCircle className="h-16 w-16 mx-auto text-green-500 mb-6" />
                  <h3 className="text-2xl font-semibold mb-3">All caught up!</h3>
                  <p className="text-muted-foreground text-lg max-w-md mx-auto">
                    No pending course requests to review. Great work staying on top of things!
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6">
                {pendingRequests.map((request) => (
                  <Card key={request.id} variant="interactive" className="overflow-hidden">
                    <CardHeader spacing="lg">
                      <div className="flex items-start justify-between">
                        <div className="space-y-3">
                          <div className="flex items-center gap-3">
                            <CardTitle level={2} className="text-2xl">{request.company_name}</CardTitle>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getPriorityColor(request.priority)}`}>
                              {request.priority} priority
                            </span>
                          </div>
                          <CardDescription size="md" className="max-w-2xl">
                            <span className="font-medium">{request.industry}</span> • 
                            Submitted by <span className="font-medium">{request.submitted_by}</span> • 
                            {formatDistanceToNow(new Date(request.submitted_at), { addSuffix: true })}
                          </CardDescription>
                        </div>
                        <StatusBadge status={request.status as any} showTooltip />
                      </div>
                    </CardHeader>

                    <CardContent spacing="lg">
                      {/* Key Metrics Row */}
                      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 text-sm font-medium text-gray-600">
                            <Target className="h-4 w-4" />
                            Training Goals
                          </div>
                          <p className="text-sm text-gray-800 leading-relaxed">{request.training_goals}</p>
                        </div>
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 text-sm font-medium text-gray-600">
                            <BarChart3 className="h-4 w-4" />
                            English Level
                          </div>
                          <p className="text-sm font-semibold">
                            {request.current_english_level} → {request.target_english_level}
                          </p>
                        </div>
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 text-sm font-medium text-gray-600">
                            <Users className="h-4 w-4" />
                            Participants
                          </div>
                          <p className="text-sm font-semibold">{request.participant_count} learners</p>
                        </div>
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 text-sm font-medium text-gray-600">
                            <Calendar className="h-4 w-4" />
                            Duration
                          </div>
                          <p className="text-sm font-semibold">{request.duration_weeks} weeks</p>
                        </div>
                      </div>

                      {/* SOP Files */}
                      <div className="mb-6">
                        <h4 className="text-sm font-semibold text-gray-700 mb-3">
                          SOP Documents ({request.sop_files.length})
                        </h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                          {request.sop_files.map((file, idx) => (
                            <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border">
                              <FileText className="h-5 w-5 text-blue-600 flex-shrink-0" />
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
                                <p className="text-xs text-gray-500">{file.size} • {file.type}</p>
                              </div>
                              <Button size="xs" variant="ghost">
                                <Download className="h-3 w-3" />
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Notes */}
                      {request.notes && (
                        <div className="mb-6">
                          <h4 className="text-sm font-semibold text-gray-700 mb-2">Additional Notes</h4>
                          <p className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg border border-blue-200">
                            {request.notes}
                          </p>
                        </div>
                      )}

                      {/* Action Buttons */}
                      <div className="flex flex-wrap gap-3 pt-4 border-t">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button variant="outline" onClick={() => setSelectedRequest(request)}>
                              <Eye className="h-4 w-4 mr-2" />
                              Review Details
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                            <DialogHeader>
                              <DialogTitle className="text-2xl">Course Request Review</DialogTitle>
                              <DialogDescription className="text-base">
                                Complete details for {request.company_name} course request
                              </DialogDescription>
                            </DialogHeader>
                            {selectedRequest && (
                              <div className="space-y-6 py-4">
                                {/* Detailed content would go here */}
                                <div className="grid grid-cols-2 gap-6">
                                  <div>
                                    <h4 className="font-semibold mb-2">Company Information</h4>
                                    <div className="space-y-2 text-sm">
                                      <p><span className="font-medium">Company:</span> {selectedRequest.company_name}</p>
                                      <p><span className="font-medium">Industry:</span> {selectedRequest.industry}</p>
                                      <p><span className="font-medium">Budget:</span> ${selectedRequest.estimated_budget?.toLocaleString()}</p>
                                    </div>
                                  </div>
                                  <div>
                                    <h4 className="font-semibold mb-2">Training Details</h4>
                                    <div className="space-y-2 text-sm">
                                      <p><span className="font-medium">Participants:</span> {selectedRequest.participant_count}</p>
                                      <p><span className="font-medium">Duration:</span> {selectedRequest.duration_weeks} weeks</p>
                                      <p><span className="font-medium">Level:</span> {selectedRequest.current_english_level} → {selectedRequest.target_english_level}</p>
                                    </div>
                                  </div>
                                </div>
                                <div>
                                  <h4 className="font-semibold mb-2">Training Goals</h4>
                                  <p className="text-sm text-gray-600">{selectedRequest.training_goals}</p>
                                </div>
                              </div>
                            )}
                          </DialogContent>
                        </Dialog>
                        
                        <Button 
                          variant="success"
                          onClick={() => handleApprove(request.id)}
                          loading={isProcessing}
                        >
                          <CheckCircle className="h-4 w-4 mr-2" />
                          Approve & Generate Course
                        </Button>
                        
                        <Button 
                          variant="destructive" 
                          onClick={() => handleReject(request.id)}
                          disabled={isProcessing}
                        >
                          <XCircle className="h-4 w-4 mr-2" />
                          Reject Request
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* In Progress Tab */}
          <TabsContent value="in-progress" className="space-y-6">
            {inProgressRequests.map((request) => (
              <div key={request.id} className="space-y-4">
                <Card variant="elevated" className="overflow-hidden">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-xl">{request.company_name}</CardTitle>
                        <CardDescription>AI course generation in progress...</CardDescription>
                      </div>
                      <StatusBadge status="generation_in_progress" pulse />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <ProgressBadge 
                        progress={request.generation_progress || 0}
                        status="generation_in_progress"
                        showPercentage={true}
                      />
                      {request.workflow_id && (
                        <div className="text-xs text-muted-foreground font-mono bg-gray-50 p-2 rounded">
                          Workflow ID: {request.workflow_id}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
                
                {/* Real-time Workflow Tracker */}
                {request.workflow_id && (
                  <WorkflowStatusTracker
                    workflowId={request.workflow_id}
                    courseRequestId={request.id}
                    companyName={request.company_name}
                    onWorkflowComplete={(result) => handleWorkflowComplete(request.workflow_id!, result)}
                    onWorkflowError={(error) => handleWorkflowError(request.workflow_id!, error)}
                  />
                )}
              </div>
            ))}
            
            {/* Active Workflows from other sources */}
            {Object.values(activeWorkflows).map((workflow) => (
              <WorkflowStatusTracker
                key={workflow.workflow_id}
                workflowId={workflow.workflow_id}
                courseRequestId={workflow.course_request_id}
                companyName={workflow.company_name}
                onWorkflowComplete={(result) => handleWorkflowComplete(workflow.workflow_id, result)}
                onWorkflowError={(error) => handleWorkflowError(workflow.workflow_id, error)}
              />
            ))}
          </TabsContent>

          {/* Completed Tab */}
          <TabsContent value="completed" className="space-y-6">
            {completedRequests.map((request) => (
              <Card key={request.id} variant="elevated">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-xl">{request.company_name}</CardTitle>
                      <CardDescription>
                        Completed {formatDistanceToNow(new Date(request.submitted_at), { addSuffix: true })}
                        {request.quality_score && (
                          <span className="ml-2 font-semibold text-green-600">
                            • Quality Score: {request.quality_score}%
                          </span>
                        )}
                      </CardDescription>
                    </div>
                    <StatusBadge status={request.status as any} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-3">
                    {request.status === 'approved' && (
                      <>
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-2" />
                          View Course
                        </Button>
                        <Button variant="outline" size="sm">
                          <Download className="h-4 w-4 mr-2" />
                          Download Materials
                        </Button>
                        <Button variant="outline" size="sm">
                          <ExternalLink className="h-4 w-4 mr-2" />
                          Assign Trainer
                        </Button>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}