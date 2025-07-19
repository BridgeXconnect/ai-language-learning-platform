"use client"

import React, { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { 
  Route, 
  MapPin, 
  Target, 
  BookOpen, 
  Clock, 
  TrendingUp, 
  Star, 
  CheckCircle, 
  Circle, 
  AlertCircle,
  Brain,
  Lightbulb,
  Compass,
  ArrowRight,
  Play,
  Pause,
  RotateCcw,
  Settings,
  Filter,
  ChevronDown,
  ChevronUp,
  Users,
  Calendar,
  Award
} from "lucide-react"

// Types
export interface LearningObjective {
  id: string
  title: string
  description: string
  category: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  estimatedTime: number
  prerequisites: string[]
  skills: string[]
  isCompleted: boolean
  progress: number
  priority: 'high' | 'medium' | 'low'
}

export interface LearningPath {
  id: string
  title: string
  description: string
  objectives: LearningObjective[]
  totalTime: number
  completedTime: number
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  category: string
  tags: string[]
  isRecommended: boolean
  adaptationReason?: string
  customized: boolean
}

export interface StudentProfile {
  id: string
  name: string
  level: string
  strengths: string[]
  weaknesses: string[]
  learningStyle: 'visual' | 'auditory' | 'kinesthetic' | 'reading'
  preferredPace: 'slow' | 'medium' | 'fast'
  availableTime: number
  goals: string[]
  previousProgress: Record<string, number>
}

export interface PathRecommendation {
  id: string
  pathId: string
  reason: string
  confidence: number
  expectedOutcome: string
  estimatedCompletion: Date
  adaptations: string[]
}

interface AdaptiveLearningPathProps {
  studentProfile: StudentProfile
  availablePaths: LearningPath[]
  currentPath?: LearningPath
  recommendations: PathRecommendation[]
  onPathSelect?: (path: LearningPath) => void
  onObjectiveStart?: (objective: LearningObjective) => void
  onPathCustomize?: (path: LearningPath, customizations: any) => void
  className?: string
}

const AdaptiveLearningPath: React.FC<AdaptiveLearningPathProps> = ({
  studentProfile,
  availablePaths,
  currentPath,
  recommendations,
  onPathSelect,
  onObjectiveStart,
  onPathCustomize,
  className = ""
}) => {
  const [selectedPath, setSelectedPath] = useState<LearningPath | null>(currentPath || null)
  const [viewMode, setViewMode] = useState<'overview' | 'detailed' | 'timeline'>('overview')
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [filterDifficulty, setFilterDifficulty] = useState<string>('all')
  const [expandedObjectives, setExpandedObjectives] = useState<Set<string>>(new Set())

  // Filter paths based on selected filters
  const filteredPaths = availablePaths.filter(path => {
    const matchesCategory = filterCategory === 'all' || path.category === filterCategory
    const matchesDifficulty = filterDifficulty === 'all' || path.difficulty === filterDifficulty
    return matchesCategory && matchesDifficulty
  })

  const toggleObjectiveExpansion = (objectiveId: string) => {
    setExpandedObjectives(prev => {
      const newSet = new Set(prev)
      if (newSet.has(objectiveId)) {
        newSet.delete(objectiveId)
      } else {
        newSet.add(objectiveId)
      }
      return newSet
    })
  }

  const getNextObjective = (path: LearningPath) => {
    return path.objectives.find(obj => !obj.isCompleted)
  }

  const getPathProgress = (path: LearningPath) => {
    const completed = path.objectives.filter(obj => obj.isCompleted).length
    return (completed / path.objectives.length) * 100
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800'
      case 'intermediate': return 'bg-yellow-100 text-yellow-800'
      case 'advanced': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <TooltipProvider>
      <div className={`space-y-6 ${className}`}>
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <Compass className="w-6 h-6" />
              Adaptive Learning Path
            </h2>
            <p className="text-muted-foreground">
              Personalized learning journey for {studentProfile.name}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Select value={viewMode} onValueChange={(value) => setViewMode(value as any)}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="overview">Overview</SelectItem>
                <SelectItem value="detailed">Detailed</SelectItem>
                <SelectItem value="timeline">Timeline</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="sm">
              <Settings className="w-4 h-4 mr-2" />
              Customize
            </Button>
          </div>
        </div>

        {/* Student Profile Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              Student Profile
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <p className="text-sm font-medium">Level</p>
                <Badge variant="secondary">{studentProfile.level}</Badge>
              </div>
              <div>
                <p className="text-sm font-medium">Learning Style</p>
                <Badge variant="outline">{studentProfile.learningStyle}</Badge>
              </div>
              <div>
                <p className="text-sm font-medium">Preferred Pace</p>
                <Badge variant="outline">{studentProfile.preferredPace}</Badge>
              </div>
              <div>
                <p className="text-sm font-medium">Available Time</p>
                <Badge variant="outline">{studentProfile.availableTime}h/week</Badge>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium mb-2">Strengths</p>
                <div className="flex flex-wrap gap-1">
                  {studentProfile.strengths.map((strength, index) => (
                    <Badge key={index} variant="default" className="text-xs">
                      {strength}
                    </Badge>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-sm font-medium mb-2">Areas for Improvement</p>
                <div className="flex flex-wrap gap-1">
                  {studentProfile.weaknesses.map((weakness, index) => (
                    <Badge key={index} variant="destructive" className="text-xs">
                      {weakness}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* AI Recommendations */}
        {recommendations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5" />
                AI Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recommendations.slice(0, 3).map((rec) => (
                  <Alert key={rec.id} className="border-blue-200 bg-blue-50">
                    <Lightbulb className="h-4 w-4 text-blue-600" />
                    <AlertDescription>
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium">{rec.reason}</p>
                          <p className="text-sm text-muted-foreground mt-1">
                            {rec.expectedOutcome}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            Confidence: {rec.confidence}% | Expected completion: {rec.estimatedCompletion.toLocaleDateString()}
                          </p>
                        </div>
                        <Button
                          size="sm"
                          onClick={() => {
                            const path = availablePaths.find(p => p.id === rec.pathId)
                            if (path) onPathSelect?.(path)
                          }}
                        >
                          Try This Path
                        </Button>
                      </div>
                    </AlertDescription>
                  </Alert>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Path Selection */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Route className="w-5 h-5" />
                  Available Paths
                </CardTitle>
                <div className="flex items-center gap-2 text-sm">
                  <Filter className="w-4 h-4" />
                  <Select value={filterCategory} onValueChange={setFilterCategory}>
                    <SelectTrigger className="w-24 h-8">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All</SelectItem>
                      <SelectItem value="language">Language</SelectItem>
                      <SelectItem value="grammar">Grammar</SelectItem>
                      <SelectItem value="vocabulary">Vocabulary</SelectItem>
                      <SelectItem value="speaking">Speaking</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={filterDifficulty} onValueChange={setFilterDifficulty}>
                    <SelectTrigger className="w-24 h-8">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All</SelectItem>
                      <SelectItem value="beginner">Beginner</SelectItem>
                      <SelectItem value="intermediate">Intermediate</SelectItem>
                      <SelectItem value="advanced">Advanced</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="max-h-96 overflow-y-auto">
                  {filteredPaths.map((path) => (
                    <div
                      key={path.id}
                      className={`p-4 border-b cursor-pointer hover:bg-gray-50 transition-colors ${
                        selectedPath?.id === path.id ? 'bg-blue-50 border-blue-200' : ''
                      }`}
                      onClick={() => setSelectedPath(path)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium text-sm">{path.title}</h4>
                          {path.isRecommended && (
                            <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                          )}
                        </div>
                        <Badge className={getDifficultyColor(path.difficulty)}>
                          {path.difficulty}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mb-2">
                        {path.description}
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">
                          {path.objectives.length} objectives
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {Math.round(path.totalTime)}h
                        </span>
                      </div>
                      <Progress value={getPathProgress(path)} className="mt-2 h-1" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Path Details */}
          <div className="lg:col-span-2">
            {selectedPath ? (
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                      <MapPin className="w-5 h-5" />
                      {selectedPath.title}
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge className={getDifficultyColor(selectedPath.difficulty)}>
                        {selectedPath.difficulty}
                      </Badge>
                      {selectedPath.isRecommended && (
                        <Badge variant="secondary">Recommended</Badge>
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {selectedPath.description}
                  </p>
                  {selectedPath.adaptationReason && (
                    <Alert className="mt-3 border-green-200 bg-green-50">
                      <Brain className="h-4 w-4 text-green-600" />
                      <AlertDescription className="text-sm">
                        <span className="font-medium">Adapted for you:</span> {selectedPath.adaptationReason}
                      </AlertDescription>
                    </Alert>
                  )}
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {selectedPath.objectives.filter(o => o.isCompleted).length}
                      </div>
                      <div className="text-sm text-muted-foreground">Completed</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {Math.round(getPathProgress(selectedPath))}%
                      </div>
                      <div className="text-sm text-muted-foreground">Progress</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {Math.round(selectedPath.totalTime - selectedPath.completedTime)}h
                      </div>
                      <div className="text-sm text-muted-foreground">Remaining</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 mb-4">
                    <Button
                      onClick={() => onPathSelect?.(selectedPath)}
                      className="flex items-center gap-2"
                    >
                      <Play className="w-4 h-4" />
                      {selectedPath === currentPath ? 'Continue Path' : 'Start Path'}
                    </Button>
                    <Button variant="outline" onClick={() => onPathCustomize?.(selectedPath, {})}>
                      <Settings className="w-4 h-4 mr-2" />
                      Customize
                    </Button>
                  </div>

                  <div className="space-y-3">
                    <h4 className="font-medium flex items-center gap-2">
                      <Target className="w-4 h-4" />
                      Learning Objectives
                    </h4>
                    {selectedPath.objectives.map((objective, index) => (
                      <div key={objective.id} className="border rounded-lg p-3">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3 flex-1">
                            <div className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-sm font-medium">
                              {index + 1}
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <h5 className="font-medium">{objective.title}</h5>
                                <Badge className={getPriorityColor(objective.priority)}>
                                  {objective.priority}
                                </Badge>
                                {objective.isCompleted && (
                                  <CheckCircle className="w-4 h-4 text-green-600" />
                                )}
                              </div>
                              <p className="text-sm text-muted-foreground mb-2">
                                {objective.description}
                              </p>
                              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                <span className="flex items-center gap-1">
                                  <Clock className="w-3 h-3" />
                                  {objective.estimatedTime}h
                                </span>
                                <span className="flex items-center gap-1">
                                  <BookOpen className="w-3 h-3" />
                                  {objective.category}
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => toggleObjectiveExpansion(objective.id)}
                            >
                              {expandedObjectives.has(objective.id) ? (
                                <ChevronUp className="w-4 h-4" />
                              ) : (
                                <ChevronDown className="w-4 h-4" />
                              )}
                            </Button>
                            {!objective.isCompleted && (
                              <Button
                                size="sm"
                                onClick={() => onObjectiveStart?.(objective)}
                              >
                                Start
                              </Button>
                            )}
                          </div>
                        </div>
                        
                        {!objective.isCompleted && (
                          <div className="mt-2">
                            <Progress value={objective.progress} className="h-2" />
                            <p className="text-xs text-muted-foreground mt-1">
                              {Math.round(objective.progress)}% complete
                            </p>
                          </div>
                        )}

                        {expandedObjectives.has(objective.id) && (
                          <div className="mt-3 pt-3 border-t">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <p className="text-sm font-medium mb-1">Prerequisites</p>
                                <div className="flex flex-wrap gap-1">
                                  {objective.prerequisites.map((prereq, i) => (
                                    <Badge key={i} variant="outline" className="text-xs">
                                      {prereq}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                              <div>
                                <p className="text-sm font-medium mb-1">Skills Developed</p>
                                <div className="flex flex-wrap gap-1">
                                  {objective.skills.map((skill, i) => (
                                    <Badge key={i} variant="secondary" className="text-xs">
                                      {skill}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <Compass className="w-12 h-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Choose Your Learning Path</h3>
                  <p className="text-muted-foreground text-center">
                    Select a learning path from the left to see detailed objectives and get started
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </TooltipProvider>
  )
}

export default AdaptiveLearningPath