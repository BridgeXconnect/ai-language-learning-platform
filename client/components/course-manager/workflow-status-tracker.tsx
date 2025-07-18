"use client"

import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/enhanced-card'
import { ProgressBadge, StatusBadge } from '@/components/ui/status-badge'
import { Button } from '@/components/ui/enhanced-button'
import { 
  Play, 
  Pause, 
  Square, 
  RefreshCw, 
  AlertTriangle, 
  CheckCircle,
  Clock,
  Activity,
  Zap,
  Brain,
  FileCheck,
  ExternalLink,
  Download
} from 'lucide-react'
import { useAuth } from '@/contexts/auth-context'
import { format } from 'date-fns'

interface WorkflowStage {
  id: string
  name: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped'
  startTime?: string
  endTime?: string
  duration?: number
  icon: React.ComponentType<{ className?: string }>
  details?: Record<string, any>
  errorMessage?: string
}

interface WorkflowData {
  workflow_id: string
  status: 'pending' | 'planning' | 'content_creation' | 'quality_review' | 'completed' | 'failed' | 'cancelled'
  course_request_id: number
  company_name: string
  start_time: string
  completion_time?: string
  current_stage?: string
  progress_percentage: number
  stages: WorkflowStage[]
  agent_health: Record<string, boolean>
  final_course?: any
  quality_score?: number
  errors?: Array<{ stage: string; error: string; timestamp: string }>
}

interface WorkflowStatusTrackerProps {
  workflowId: string
  courseRequestId: number
  companyName: string
  onWorkflowComplete?: (result: any) => void
  onWorkflowError?: (error: any) => void
}

export function WorkflowStatusTracker({
  workflowId,
  courseRequestId,
  companyName,
  onWorkflowComplete,
  onWorkflowError
}: WorkflowStatusTrackerProps) {
  const [workflowData, setWorkflowData] = useState<WorkflowData | null>(null)
  const [isPolling, setIsPolling] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const pollingRef = useRef<NodeJS.Timeout | null>(null)
  const { fetchWithAuth } = useAuth()

  // Initialize workflow data structure
  const initializeWorkflowData = (initialStatus: string = 'pending'): WorkflowData => {
    return {
      workflow_id: workflowId,
      status: initialStatus as any,
      course_request_id: courseRequestId,
      company_name: companyName,
      start_time: new Date().toISOString(),
      progress_percentage: 0,
      agent_health: {},
      stages: [
        {
          id: 'planning',
          name: 'Course Planning',
          description: 'AI agent analyzing requirements and creating curriculum structure',
          status: 'pending',
          icon: Brain
        },
        {
          id: 'content_creation',
          name: 'Content Creation',
          description: 'Generating lessons, exercises, and learning materials',
          status: 'pending',
          icon: Zap
        },
        {
          id: 'quality_review',
          name: 'Quality Assurance',
          description: 'Reviewing content quality and educational effectiveness',
          status: 'pending',
          icon: FileCheck
        }
      ]
    }
  }

  // Fetch workflow status from API
  const fetchWorkflowStatus = async () => {
    try {
      const response = await fetchWithAuth(`/api/agents/workflow/${workflowId}`)
      
      if (response.ok) {
        const data = await response.json()
        
        if (data.workflow) {
          const updatedWorkflow = mapApiDataToWorkflow(data.workflow)
          setWorkflowData(updatedWorkflow)
          setLastUpdate(new Date().toISOString())
          setError(null)
          
          // Check if workflow is complete
          if (updatedWorkflow.status === 'completed') {
            setIsPolling(false)
            onWorkflowComplete?.(updatedWorkflow)
          } else if (updatedWorkflow.status === 'failed') {
            setIsPolling(false)
            onWorkflowError?.(updatedWorkflow.errors?.[0] || { error: 'Workflow failed' })
          }
        }
      } else if (response.status === 404) {
        // Workflow not found, might still be initializing
        if (!workflowData) {
          setWorkflowData(initializeWorkflowData())
        }
      } else {
        throw new Error(`API error: ${response.status}`)
      }
    } catch (err) {
      console.error('Error fetching workflow status:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch workflow status')
      
      // Initialize default data if no workflow data exists
      if (!workflowData) {
        setWorkflowData(initializeWorkflowData())
      }
    }
  }

  // Map API response to our workflow data structure
  const mapApiDataToWorkflow = (apiData: any): WorkflowData => {
    const stages = workflowData?.stages || initializeWorkflowData().stages
    
    // Update stage statuses based on current workflow status
    const updatedStages = stages.map(stage => {
      let stageStatus: 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped' = 'pending'
      
      if (apiData.status === 'completed') {
        stageStatus = 'completed'
      } else if (apiData.status === 'failed') {
        if (apiData.failed_stage === stage.id) {
          stageStatus = 'failed'
        } else {
          stageStatus = stage.status // Keep previous status
        }
      } else if (apiData.current_stage === stage.id || apiData.status === stage.id) {
        stageStatus = 'in_progress'
      } else if (shouldStageBeCompleted(stage.id, apiData.status)) {
        stageStatus = 'completed'
      }
      
      return {
        ...stage,
        status: stageStatus,
        startTime: stage.startTime || (stageStatus === 'in_progress' ? new Date().toISOString() : undefined),
        endTime: stageStatus === 'completed' ? new Date().toISOString() : undefined,
        details: apiData[`${stage.id}_result`] || stage.details,
        errorMessage: apiData.failed_stage === stage.id ? apiData.error_message : undefined
      }
    })
    
    // Calculate progress percentage
    const completedStages = updatedStages.filter(s => s.status === 'completed').length
    const totalStages = updatedStages.length
    let progressPercentage = (completedStages / totalStages) * 100
    
    // Add partial progress for in-progress stage
    const inProgressStage = updatedStages.find(s => s.status === 'in_progress')
    if (inProgressStage) {
      progressPercentage += (100 / totalStages) * 0.5 // Add 50% of stage progress
    }
    
    return {
      workflow_id: workflowId,
      status: apiData.status,
      course_request_id: courseRequestId,
      company_name: companyName,
      start_time: apiData.start_time || workflowData?.start_time || new Date().toISOString(),
      completion_time: apiData.completion_time,
      current_stage: apiData.current_stage,
      progress_percentage: Math.min(progressPercentage, 100),
      stages: updatedStages,
      agent_health: apiData.agent_health || {},
      final_course: apiData.final_course,
      quality_score: apiData.quality_score,
      errors: apiData.errors || []
    }
  }

  // Determine if a stage should be marked as completed based on current workflow status
  const shouldStageBeCompleted = (stageId: string, currentStatus: string): boolean => {
    const stageOrder = ['planning', 'content_creation', 'quality_review']
    const currentIndex = stageOrder.indexOf(currentStatus)
    const stageIndex = stageOrder.indexOf(stageId)
    
    return stageIndex < currentIndex
  }

  // Map workflow status to StatusBadge status
  const mapWorkflowStatusToBadge = (status: string): keyof typeof import("../ui/status-badge").statusConfig => {
    switch (status) {
      case 'pending':
        return 'submitted';
      case 'planning':
        return 'under_review';
      case 'content_creation':
        return 'generation_in_progress';
      case 'quality_review':
        return 'under_review';
      case 'completed':
        return 'completed';
      case 'failed':
        return 'error';
      case 'cancelled':
        return 'paused';
      default:
        return 'draft';
    }
  }

  // Start polling for workflow updates
  useEffect(() => {
    if (isPolling) {
      // Initial fetch
      fetchWorkflowStatus()
      
      // Set up polling interval
      pollingRef.current = setInterval(fetchWorkflowStatus, 3000) // Poll every 3 seconds
      
      return () => {
        if (pollingRef.current) {
          clearInterval(pollingRef.current)
        }
      }
    }
  }, [isPolling, workflowId])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
      }
    }
  }, [])

  const handleTogglePolling = () => {
    setIsPolling(!isPolling)
  }

  const handleRefresh = () => {
    fetchWorkflowStatus()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600'
      case 'failed': return 'text-red-600'
      case 'in_progress': return 'text-blue-600'
      case 'pending': return 'text-gray-400'
      default: return 'text-gray-400'
    }
  }

  const getStageIcon = (stage: WorkflowStage) => {
    const IconComponent = stage.icon
    const className = `h-6 w-6 ${getStatusColor(stage.status)}`
    
    return <IconComponent className={className} />
  }

  if (!workflowData) {
    return (
      <Card variant="elevated">
        <CardContent spacing="md">
          <div className="flex items-center justify-center p-8">
            <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
            <span className="ml-3 text-lg">Loading workflow status...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card variant="elevated" className="w-full">
      <CardHeader spacing="lg">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle level={2} className="text-xl">
              AI Course Generation Workflow
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              {companyName} • Workflow ID: {workflowId.slice(-8)}
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <StatusBadge 
              status={mapWorkflowStatusToBadge(workflowData.status)} 
              pulse={mapWorkflowStatusToBadge(workflowData.status) === 'generation_in_progress'}
            />
            <Button
              variant="outline"
              size="sm"
              onClick={handleTogglePolling}
              className="ml-2"
            >
              {isPolling ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent spacing="lg">
        {/* Overall Progress */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Overall Progress</span>
            <span className="text-sm text-muted-foreground">
              {Math.round(workflowData.progress_percentage)}%
            </span>
          </div>
          <ProgressBadge 
            progress={workflowData.progress_percentage}
            status={mapWorkflowStatusToBadge(workflowData.status)}
            showPercentage={false}
          />
        </div>

        {/* Workflow Stages */}
        <div className="space-y-4">
          {workflowData.stages.map((stage, index) => (
            <div key={stage.id} className="flex items-start space-x-4">
              <div className="flex-shrink-0 mt-1">
                {getStageIcon(stage)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h4 className={`text-sm font-semibold ${getStatusColor(stage.status)}`}>
                    {stage.name}
                  </h4>
                  <div className="flex items-center gap-2">
                    {stage.status === 'in_progress' && (
                      <Activity className="h-4 w-4 text-blue-500 animate-pulse" />
                    )}
                    {stage.status === 'completed' && (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    )}
                    {stage.status === 'failed' && (
                      <AlertTriangle className="h-4 w-4 text-red-500" />
                    )}
                  </div>
                </div>
                
                <p className="text-xs text-muted-foreground mt-1">
                  {stage.description}
                </p>
                
                {/* Stage timing info */}
                {stage.startTime && (
                  <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                    {stage.status === 'in_progress' && (
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        Started {format(new Date(stage.startTime), 'HH:mm:ss')}
                      </div>
                    )}
                    {stage.endTime && stage.startTime && (
                      <div className="flex items-center gap-1">
                        <CheckCircle className="h-3 w-3" />
                        Completed in {Math.round((new Date(stage.endTime).getTime() - new Date(stage.startTime).getTime()) / 1000)}s
                      </div>
                    )}
                  </div>
                )}
                
                {/* Error message */}
                {stage.errorMessage && (
                  <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                    <AlertTriangle className="h-3 w-3 inline mr-1" />
                    {stage.errorMessage}
                  </div>
                )}
                
                {/* Stage details */}
                {stage.details && stage.status === 'completed' && (
                  <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded text-xs">
                    <CheckCircle className="h-3 w-3 inline mr-1 text-green-600" />
                    <span className="text-green-700">
                      Stage completed successfully
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Final Results */}
        {workflowData.status === 'completed' && workflowData.final_course && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-semibold text-green-800">
                Course Generation Complete!
              </h4>
              {workflowData.quality_score && (
                <span className="text-sm font-semibold text-green-600">
                  Quality Score: {workflowData.quality_score}%
                </span>
              )}
            </div>
            
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <ExternalLink className="h-4 w-4 mr-2" />
                View Course
              </Button>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Download Materials
              </Button>
            </div>
          </div>
        )}

        {/* Error Summary */}
        {workflowData.errors && workflowData.errors.length > 0 && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <h4 className="text-sm font-semibold text-red-800 mb-2">
              Workflow Errors
            </h4>
            <div className="space-y-2">
              {workflowData.errors.map((error, index) => (
                <div key={index} className="text-xs text-red-700">
                  <span className="font-medium">{error.stage}:</span> {error.error}
                  <span className="text-red-500 ml-2">
                    {format(new Date(error.timestamp), 'HH:mm:ss')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Status Footer */}
        <div className="mt-6 pt-4 border-t flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-4">
            <span>Started: {format(new Date(workflowData.start_time), 'MMM dd, HH:mm:ss')}</span>
            {workflowData.completion_time && (
              <span>Completed: {format(new Date(workflowData.completion_time), 'HH:mm:ss')}</span>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            {lastUpdate && (
              <span>Last updated: {format(new Date(lastUpdate), 'HH:mm:ss')}</span>
            )}
            {isPolling && (
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Live</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}