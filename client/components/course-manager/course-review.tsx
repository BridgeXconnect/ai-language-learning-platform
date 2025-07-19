"use client"
import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/enhanced-card"
import { Button } from "@/components/ui/enhanced-button"
import { StatusBadge } from "@/components/ui/status-badge"
import { Textarea } from "@/components/ui/textarea"
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  FileText,
  Users,
  Clock,
  Target,
  BarChart3,
  Edit3,
  Eye,
  Download,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  Star,
  BookOpen,
  PlayCircle,
  Award
} from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"

interface CourseStructure {
  id: string
  title: string
  description: string
  modules: Module[]
  totalLessons: number
  estimatedDuration: string
  cefrLevel: string
  objectives: string[]
}

interface Module {
  id: string
  title: string
  description: string
  lessons: Lesson[]
  estimatedDuration: string
}

interface Lesson {
  id: string
  title: string
  type: 'presentation' | 'exercise' | 'activity' | 'assessment'
  duration: string
  exercises: Exercise[]
  materials: string[]
}

interface Exercise {
  id: string
  type: 'multiple_choice' | 'fill_blank' | 'role_play' | 'writing' | 'listening'
  question: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  points: number
}

interface QualityMetrics {
  overallScore: number
  linguisticAccuracy: number
  pedagogicalEffectiveness: number
  cefrAlignment: number
  culturalSensitivity: number
  businessRelevance: number
  contentQuality: number
  exerciseVariety: number
}

interface AIConfidence {
  contentGeneration: number
  structuralCoherence: number
  vocabularySelection: number
  grammarComplexity: number
  scenarioRelevance: number
}

interface CourseReviewData {
  courseId: string
  structure: CourseStructure
  qualityMetrics: QualityMetrics
  aiConfidence: AIConfidence
  generatedAt: string
  reviewStatus: 'draft' | 'under_review' | 'approved' | 'rejected' | 'completed'
  reviewer?: string
  reviewNotes?: string
  companyContext: {
    name: string
    industry: string
    sopFiles: string[]
    requirements: string
  }
}

interface CourseReviewProps {
  courseId: string
  onReviewComplete?: (courseId: string, decision: string, notes?: string) => void
  onEdit?: (courseId: string) => void
}

export function CourseReview({ courseId, onReviewComplete, onEdit }: CourseReviewProps) {
  const [courseData, setCourseData] = useState<CourseReviewData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [reviewNotes, setReviewNotes] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [selectedModule, setSelectedModule] = useState<string | null>(null)
  const [selectedLesson, setSelectedLesson] = useState<string | null>(null)
  const { fetchWithAuth } = useAuth()

  useEffect(() => {
    const loadCourseData = async () => {
      try {
        const response = await fetchWithAuth(`/api/courses/${courseId}/review`)
        if (response.ok) {
          const data = await response.json()
          setCourseData(data)
        } else {
          // Mock data for development
          setCourseData({
            courseId,
            structure: {
              id: courseId,
              title: "Advanced Business Communication for Tech Professionals",
              description: "Comprehensive English training focused on technical communication, client presentations, and cross-cultural business interactions.",
              totalLessons: 24,
              estimatedDuration: "8 weeks",
              cefrLevel: "B2",
              objectives: [
                "Master technical vocabulary and terminology",
                "Deliver effective client presentations",
                "Navigate cross-cultural business communications",
                "Write professional technical documentation",
                "Conduct successful virtual meetings"
              ],
              modules: [
                {
                  id: "mod1",
                  title: "Technical Communication Fundamentals",
                  description: "Core concepts and vocabulary for technical discussions",
                  estimatedDuration: "2 weeks",
                  lessons: [
                    {
                      id: "lesson1",
                      title: "Technical Vocabulary Mastery",
                      type: "presentation",
                      duration: "45 min",
                      exercises: [
                        {
                          id: "ex1",
                          type: "multiple_choice",
                          question: "What is the most appropriate term for...",
                          difficulty: "intermediate",
                          points: 10
                        }
                      ],
                      materials: ["Technical_Glossary.pdf", "Industry_Terms.pptx"]
                    },
                    {
                      id: "lesson2",
                      title: "Explaining Complex Concepts",
                      type: "activity",
                      duration: "60 min",
                      exercises: [
                        {
                          id: "ex2",
                          type: "role_play",
                          question: "Explain your product to a non-technical client",
                          difficulty: "advanced",
                          points: 15
                        }
                      ],
                      materials: ["Explanation_Framework.pdf"]
                    }
                  ]
                },
                {
                  id: "mod2",
                  title: "Client Presentation Skills",
                  description: "Advanced presentation techniques for client-facing scenarios",
                  estimatedDuration: "3 weeks",
                  lessons: [
                    {
                      id: "lesson3",
                      title: "Structuring Technical Presentations",
                      type: "presentation",
                      duration: "50 min",
                      exercises: [],
                      materials: ["Presentation_Template.pptx"]
                    }
                  ]
                }
              ]
            },
            qualityMetrics: {
              overallScore: 91.3,
              linguisticAccuracy: 94.5,
              pedagogicalEffectiveness: 89.2,
              cefrAlignment: 92.8,
              culturalSensitivity: 88.7,
              businessRelevance: 95.1,
              contentQuality: 90.4,
              exerciseVariety: 87.9
            },
            aiConfidence: {
              contentGeneration: 92.4,
              structuralCoherence: 89.7,
              vocabularySelection: 94.1,
              grammarComplexity: 88.3,
              scenarioRelevance: 91.6
            },
            generatedAt: "2025-01-15T14:30:00Z",
            reviewStatus: "draft",
            companyContext: {
              name: "TechCorp Solutions",
              industry: "Technology",
              sopFiles: ["Communication_Guidelines.pdf", "Client_Interaction_SOP.docx"],
              requirements: "Focus on technical communication and client presentations"
            }
          })
        }
      } catch (error) {
        console.error('Failed to load course data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    loadCourseData()
  }, [courseId])

  const handleReviewAction = async (action: 'approve' | 'reject' | 'revision') => {
    setIsSubmitting(true)
    try {
      const response = await fetchWithAuth(`/api/courses/${courseId}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action,
          notes: reviewNotes
        })
      })

      if (response.ok) {
        onReviewComplete?.(courseId, action, reviewNotes)
      }
    } catch (error) {
      console.error('Failed to submit review:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const getQualityColor = (score: number) => {
    if (score >= 90) return "text-green-600 bg-green-50"
    if (score >= 80) return "text-yellow-600 bg-yellow-50"
    return "text-red-600 bg-red-50"
  }

  const getQualityIcon = (score: number) => {
    if (score >= 90) return <CheckCircle className="h-4 w-4" />
    if (score >= 80) return <AlertTriangle className="h-4 w-4" />
    return <XCircle className="h-4 w-4" />
  }

  if (isLoading) {
    return (
      <Card variant="elevated">
        <CardContent spacing="lg" className="animate-pulse">
          <div className="space-y-4">
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="grid grid-cols-3 gap-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-20 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!courseData) {
    return (
      <Card variant="elevated">
        <CardContent spacing="md" className="text-center py-8">
          <p className="text-muted-foreground">Failed to load course data</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card variant="elevated">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <CardTitle className="text-2xl">{courseData.structure.title}</CardTitle>
              <p className="text-muted-foreground max-w-3xl">{courseData.structure.description}</p>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span className="flex items-center gap-1">
                  <BookOpen className="h-4 w-4" />
                  {courseData.structure.totalLessons} lessons
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  {courseData.structure.estimatedDuration}
                </span>
                <span className="flex items-center gap-1">
                  <Award className="h-4 w-4" />
                  CEFR {courseData.structure.cefrLevel}
                </span>
              </div>
            </div>
            <StatusBadge status={courseData.reviewStatus} showTooltip />
          </div>
        </CardHeader>
      </Card>

      {/* Quality Metrics Overview */}
      <Card variant="elevated">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Quality Assessment
          </CardTitle>
        </CardHeader>
        <CardContent spacing="md">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {Object.entries(courseData.qualityMetrics).map(([metric, score]) => (
              <div key={metric} className={`p-3 rounded-lg border ${getQualityColor(score)}`}>
                <div className="flex items-center justify-between mb-1">
                  {getQualityIcon(score)}
                  <span className="font-bold text-lg">{score.toFixed(1)}%</span>
                </div>
                <p className="text-xs font-medium capitalize">
                  {metric.replace(/([A-Z])/g, ' $1').trim()}
                </p>
              </div>
            ))}
          </div>
          
          {/* Overall Score */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-semibold text-lg">Overall Quality Score</h4>
                <p className="text-sm text-muted-foreground">Composite score across all metrics</p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-blue-600">
                  {courseData.qualityMetrics.overallScore.toFixed(1)}%
                </div>
                <div className="text-sm text-muted-foreground">Excellent Quality</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Course Structure Review */}
      <Card variant="elevated">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Course Structure
          </CardTitle>
        </CardHeader>
        <CardContent spacing="md">
          <Tabs defaultValue="structure" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="structure">Structure</TabsTrigger>
              <TabsTrigger value="objectives">Objectives</TabsTrigger>
              <TabsTrigger value="materials">Materials</TabsTrigger>
            </TabsList>
            
            <TabsContent value="structure" className="space-y-4 mt-4">
              {courseData.structure.modules.map((module) => (
                <div key={module.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-lg">{module.title}</h4>
                    <Badge variant="outline">{module.estimatedDuration}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{module.description}</p>
                  
                  <div className="space-y-2">
                    {module.lessons.map((lesson) => (
                      <div key={lesson.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <div className="flex items-center gap-2">
                          <PlayCircle className="h-4 w-4 text-blue-600" />
                          <span className="font-medium text-sm">{lesson.title}</span>
                          <Badge variant="secondary" className="text-xs">{lesson.type}</Badge>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <span>{lesson.duration}</span>
                          <span>•</span>
                          <span>{lesson.exercises.length} exercises</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </TabsContent>
            
            <TabsContent value="objectives" className="space-y-3 mt-4">
              {courseData.structure.objectives.map((objective, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                  <Target className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <p className="text-sm">{objective}</p>
                </div>
              ))}
            </TabsContent>
            
            <TabsContent value="materials" className="mt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {courseData.companyContext.sopFiles.map((file, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 border rounded-lg">
                    <FileText className="h-5 w-5 text-blue-600" />
                    <div className="flex-1">
                      <p className="font-medium text-sm">{file}</p>
                      <p className="text-xs text-muted-foreground">Source material</p>
                    </div>
                    <Button size="xs" variant="ghost">
                      <Download className="h-3 w-3" />
                    </Button>
                  </div>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* AI Confidence Metrics */}
      <Card variant="elevated">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Star className="h-5 w-5" />
            AI Confidence Levels
          </CardTitle>
        </CardHeader>
        <CardContent spacing="md">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(courseData.aiConfidence).map(([metric, confidence]) => (
              <div key={metric} className="p-3 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium capitalize">
                    {metric.replace(/([A-Z])/g, ' $1').trim()}
                  </span>
                  <span className="text-sm font-bold">{confidence.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      confidence >= 90 ? 'bg-green-500' :
                      confidence >= 80 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${confidence}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Review Actions */}
      <Card variant="elevated">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Review Decision
          </CardTitle>
        </CardHeader>
        <CardContent spacing="md">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Review Notes</label>
              <Textarea
                placeholder="Add your review comments, suggestions, or concerns..."
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                rows={4}
              />
            </div>
            
            <div className="flex flex-wrap gap-3">
              <Button
                variant="success"
                onClick={() => handleReviewAction('approve')}
                loading={isSubmitting}
                className="flex items-center gap-2"
              >
                <ThumbsUp className="h-4 w-4" />
                Approve Course
              </Button>
              
              <Button
                variant="warning"
                onClick={() => handleReviewAction('revision')}
                loading={isSubmitting}
                className="flex items-center gap-2"
              >
                <Edit3 className="h-4 w-4" />
                Request Revision
              </Button>
              
              <Button
                variant="destructive"
                onClick={() => handleReviewAction('reject')}
                loading={isSubmitting}
                className="flex items-center gap-2"
              >
                <ThumbsDown className="h-4 w-4" />
                Reject Course
              </Button>
              
              {onEdit && (
                <Button
                  variant="outline"
                  onClick={() => onEdit(courseId)}
                  className="flex items-center gap-2"
                >
                  <Edit3 className="h-4 w-4" />
                  Edit Course
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}