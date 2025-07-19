"use client"

import React, { useState, useCallback, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Separator } from "@/components/ui/separator"
import { 
  Bot, 
  Brain, 
  Sparkles, 
  Target, 
  Zap,
  Clock,
  BarChart,
  Settings,
  Lightbulb,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Users,
  BookOpen,
  FileText,
  Play,
  Pause,
  RotateCcw,
  Save,
  Download,
  Upload,
  Share,
  Eye,
  Edit,
  Trash2,
  Plus,
  Minus,
  ChevronDown,
  ChevronUp
} from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { AssessmentQuestion, AssessmentSettings, QuestionType } from "@/components/learning/assessment-builder"

interface AIAssessmentRequest {
  topic: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  questionCount: number
  questionTypes: QuestionType[]
  learningObjectives: string[]
  targetAudience: string
  timeLimit?: number
  adaptiveMode: boolean
  cognitiveLevel: string[]
}

interface AIGeneratedAssessment {
  assessment_id: string
  questions: AssessmentQuestion[]
  metadata: {
    generation_time: number
    quality_score: number
    difficulty_distribution: Record<string, number>
    cognitive_distribution: Record<string, number>
    estimated_completion_time: number
  }
  recommendations: string[]
}

interface AIAssessmentBuilderProps {
  onAssessmentGenerated?: (assessment: AIGeneratedAssessment) => void
  onAssessmentSaved?: (assessment: { settings: AssessmentSettings; questions: AssessmentQuestion[] }) => void
  className?: string
}

export const AIAssessmentBuilder: React.FC<AIAssessmentBuilderProps> = ({
  onAssessmentGenerated,
  onAssessmentSaved,
  className = ""
}) => {
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedAssessment, setGeneratedAssessment] = useState<AIGeneratedAssessment | null>(null)
  const [activeTab, setActiveTab] = useState<"request" | "preview" | "analytics">("request")
  const { toast } = useToast()

  // AI Request Configuration
  const [aiRequest, setAiRequest] = useState<AIAssessmentRequest>({
    topic: "",
    difficulty: "intermediate",
    questionCount: 10,
    questionTypes: ["multiple-choice", "true-false", "short-answer"],
    learningObjectives: [""],
    targetAudience: "general",
    timeLimit: 60,
    adaptiveMode: false,
    cognitiveLevel: ["remember", "understand", "apply"]
  })

  // Assessment Settings
  const [assessmentSettings, setAssessmentSettings] = useState<AssessmentSettings>({
    title: "AI Generated Assessment",
    description: "",
    timeLimit: 60,
    attempts: 1,
    passingScore: 70,
    randomizeQuestions: false,
    showResults: true,
    instructions: "Read each question carefully and select the best answer."
  })

  const [generationProgress, setGenerationProgress] = useState(0)
  const [generationStage, setGenerationStage] = useState("")

  const handleGenerateAssessment = useCallback(async () => {
    if (!aiRequest.topic.trim()) {
      toast({
        title: "Error",
        description: "Please enter a topic for the assessment",
        variant: "destructive"
      })
      return
    }

    if (aiRequest.learningObjectives.filter(obj => obj.trim()).length === 0) {
      toast({
        title: "Error",
        description: "Please add at least one learning objective",
        variant: "destructive"
      })
      return
    }

    setIsGenerating(true)
    setGenerationProgress(0)
    setGenerationStage("Initializing AI generation...")

    try {
      // Simulate AI generation process with progress updates
      const stages = [
        "Analyzing topic and learning objectives...",
        "Generating question templates...",
        "Creating question content...",
        "Generating answer options and distractors...",
        "Validating content quality...",
        "Optimizing difficulty distribution...",
        "Finalizing assessment structure..."
      ]

      for (let i = 0; i < stages.length; i++) {
        setGenerationStage(stages[i])
        setGenerationProgress(((i + 1) / stages.length) * 100)
        await new Promise(resolve => setTimeout(resolve, 1000))
      }

      // Call AI service to generate assessment
      const response = await fetch('/api/ai/generate-assessment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(aiRequest),
      })

      if (!response.ok) {
        throw new Error('Failed to generate assessment')
      }

      const generatedData: AIGeneratedAssessment = await response.json()
      
      setGeneratedAssessment(generatedData)
      setActiveTab("preview")
      
      // Update assessment settings based on generated content
      setAssessmentSettings(prev => ({
        ...prev,
        title: `${aiRequest.topic} - AI Generated Assessment`,
        description: `Assessment covering ${aiRequest.learningObjectives.join(", ")}`,
        timeLimit: generatedData.metadata.estimated_completion_time,
      }))

      onAssessmentGenerated?.(generatedData)

      toast({
        title: "Success",
        description: `Assessment generated with ${generatedData.questions.length} questions`,
      })

    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate assessment. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsGenerating(false)
      setGenerationProgress(0)
      setGenerationStage("")
    }
  }, [aiRequest, onAssessmentGenerated, toast])

  const handleRegenerateQuestion = useCallback(async (questionIndex: number) => {
    if (!generatedAssessment) return

    try {
      const response = await fetch('/api/ai/regenerate-question', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          questionIndex,
          topic: aiRequest.topic,
          difficulty: aiRequest.difficulty,
          questionType: generatedAssessment.questions[questionIndex].type,
          learningObjective: generatedAssessment.questions[questionIndex].tags[0] || ""
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to regenerate question')
      }

      const newQuestion: AssessmentQuestion = await response.json()
      
      setGeneratedAssessment(prev => {
        if (!prev) return null
        const updatedQuestions = [...prev.questions]
        updatedQuestions[questionIndex] = newQuestion
        return {
          ...prev,
          questions: updatedQuestions
        }
      })

      toast({
        title: "Success",
        description: "Question regenerated successfully",
      })

    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to regenerate question. Please try again.",
        variant: "destructive"
      })
    }
  }, [generatedAssessment, aiRequest, toast])

  const handleSaveAssessment = useCallback(() => {
    if (!generatedAssessment) return

    onAssessmentSaved?.({
      settings: assessmentSettings,
      questions: generatedAssessment.questions
    })

    toast({
      title: "Success",
      description: "Assessment saved successfully",
    })
  }, [generatedAssessment, assessmentSettings, onAssessmentSaved, toast])

  const addLearningObjective = useCallback(() => {
    setAiRequest(prev => ({
      ...prev,
      learningObjectives: [...prev.learningObjectives, ""]
    }))
  }, [])

  const removeLearningObjective = useCallback((index: number) => {
    setAiRequest(prev => ({
      ...prev,
      learningObjectives: prev.learningObjectives.filter((_, i) => i !== index)
    }))
  }, [])

  const updateLearningObjective = useCallback((index: number, value: string) => {
    setAiRequest(prev => ({
      ...prev,
      learningObjectives: prev.learningObjectives.map((obj, i) => i === index ? value : obj)
    }))
  }, [])

  const toggleQuestionType = useCallback((type: QuestionType) => {
    setAiRequest(prev => ({
      ...prev,
      questionTypes: prev.questionTypes.includes(type)
        ? prev.questionTypes.filter(t => t !== type)
        : [...prev.questionTypes, type]
    }))
  }, [])

  const toggleCognitiveLevel = useCallback((level: string) => {
    setAiRequest(prev => ({
      ...prev,
      cognitiveLevel: prev.cognitiveLevel.includes(level)
        ? prev.cognitiveLevel.filter(l => l !== level)
        : [...prev.cognitiveLevel, level]
    }))
  }, [])

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Brain className="w-6 h-6 text-blue-600" />
            AI Assessment Builder
          </h2>
          <p className="text-muted-foreground">
            Generate intelligent assessments using advanced AI
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            onClick={() => setActiveTab("analytics")}
            disabled={!generatedAssessment}
          >
            <BarChart className="w-4 h-4 mr-2" />
            Analytics
          </Button>
          <Button 
            onClick={handleSaveAssessment}
            disabled={!generatedAssessment}
          >
            <Save className="w-4 h-4 mr-2" />
            Save Assessment
          </Button>
        </div>
      </div>

      {/* Generation Progress */}
      {isGenerating && (
        <Alert className="border-blue-200 bg-blue-50">
          <Bot className="h-4 w-4 text-blue-600" />
          <AlertDescription>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{generationStage}</span>
                <span className="text-sm text-muted-foreground">
                  {Math.round(generationProgress)}%
                </span>
              </div>
              <Progress value={generationProgress} className="h-2" />
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList>
          <TabsTrigger value="request">
            <Settings className="w-4 h-4 mr-2" />
            Configuration
          </TabsTrigger>
          <TabsTrigger value="preview" disabled={!generatedAssessment}>
            <Eye className="w-4 h-4 mr-2" />
            Preview
          </TabsTrigger>
          <TabsTrigger value="analytics" disabled={!generatedAssessment}>
            <BarChart className="w-4 h-4 mr-2" />
            Analytics
          </TabsTrigger>
        </TabsList>

        {/* Configuration Tab */}
        <TabsContent value="request" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Basic Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Basic Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="topic">Topic</Label>
                  <Input
                    id="topic"
                    placeholder="e.g., English Grammar, Business Communication"
                    value={aiRequest.topic}
                    onChange={(e) => setAiRequest(prev => ({ ...prev, topic: e.target.value }))}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="difficulty">Difficulty Level</Label>
                    <Select 
                      value={aiRequest.difficulty} 
                      onValueChange={(value) => setAiRequest(prev => ({ ...prev, difficulty: value as any }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="beginner">Beginner</SelectItem>
                        <SelectItem value="intermediate">Intermediate</SelectItem>
                        <SelectItem value="advanced">Advanced</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="questionCount">Number of Questions</Label>
                    <Input
                      id="questionCount"
                      type="number"
                      min="1"
                      max="50"
                      value={aiRequest.questionCount}
                      onChange={(e) => setAiRequest(prev => ({ ...prev, questionCount: parseInt(e.target.value) }))}
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="targetAudience">Target Audience</Label>
                  <Select 
                    value={aiRequest.targetAudience} 
                    onValueChange={(value) => setAiRequest(prev => ({ ...prev, targetAudience: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="general">General Learners</SelectItem>
                      <SelectItem value="business">Business Professionals</SelectItem>
                      <SelectItem value="academic">Academic Students</SelectItem>
                      <SelectItem value="children">Children</SelectItem>
                      <SelectItem value="adults">Adult Learners</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="timeLimit">Time Limit (minutes)</Label>
                  <Input
                    id="timeLimit"
                    type="number"
                    min="1"
                    value={aiRequest.timeLimit}
                    onChange={(e) => setAiRequest(prev => ({ ...prev, timeLimit: parseInt(e.target.value) }))}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Learning Objectives */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="w-5 h-5" />
                  Learning Objectives
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {aiRequest.learningObjectives.map((objective, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <Input
                      placeholder="e.g., Understand present tense usage"
                      value={objective}
                      onChange={(e) => updateLearningObjective(index, e.target.value)}
                    />
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeLearningObjective(index)}
                      disabled={aiRequest.learningObjectives.length === 1}
                    >
                      <Minus className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
                <Button variant="outline" size="sm" onClick={addLearningObjective}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Objective
                </Button>
              </CardContent>
            </Card>

            {/* Question Types */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Question Types
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: "multiple-choice", label: "Multiple Choice" },
                    { value: "true-false", label: "True/False" },
                    { value: "fill-blank", label: "Fill in the Blank" },
                    { value: "short-answer", label: "Short Answer" },
                    { value: "essay", label: "Essay" },
                    { value: "matching", label: "Matching" },
                    { value: "ordering", label: "Ordering" },
                    { value: "speaking", label: "Speaking" },
                    { value: "listening", label: "Listening" }
                  ].map((type) => (
                    <div key={type.value} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={type.value}
                        checked={aiRequest.questionTypes.includes(type.value as QuestionType)}
                        onChange={() => toggleQuestionType(type.value as QuestionType)}
                      />
                      <Label htmlFor={type.value} className="text-sm">
                        {type.label}
                      </Label>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Cognitive Levels */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="w-5 h-5" />
                  Cognitive Levels (Bloom's Taxonomy)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: "remember", label: "Remember" },
                    { value: "understand", label: "Understand" },
                    { value: "apply", label: "Apply" },
                    { value: "analyze", label: "Analyze" },
                    { value: "evaluate", label: "Evaluate" },
                    { value: "create", label: "Create" }
                  ].map((level) => (
                    <div key={level.value} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={level.value}
                        checked={aiRequest.cognitiveLevel.includes(level.value)}
                        onChange={() => toggleCognitiveLevel(level.value)}
                      />
                      <Label htmlFor={level.value} className="text-sm">
                        {level.label}
                      </Label>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="flex justify-center">
            <Button 
              onClick={handleGenerateAssessment}
              disabled={isGenerating}
              className="px-8"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Generate Assessment
                </>
              )}
            </Button>
          </div>
        </TabsContent>

        {/* Preview Tab */}
        <TabsContent value="preview" className="space-y-6">
          {generatedAssessment && (
            <>
              {/* Assessment Header */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>{assessmentSettings.title}</CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">
                        Quality Score: {Math.round(generatedAssessment.metadata.quality_score * 100)}%
                      </Badge>
                      <Badge variant="outline">
                        {generatedAssessment.questions.length} Questions
                      </Badge>
                    </div>
                  </div>
                  <p className="text-muted-foreground">
                    {assessmentSettings.description}
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {generatedAssessment.metadata.estimated_completion_time}
                      </div>
                      <div className="text-sm text-muted-foreground">Minutes</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {aiRequest.difficulty}
                      </div>
                      <div className="text-sm text-muted-foreground">Difficulty</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {Math.round(generatedAssessment.metadata.quality_score * 100)}%
                      </div>
                      <div className="text-sm text-muted-foreground">Quality</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Questions */}
              <div className="space-y-4">
                {generatedAssessment.questions.map((question, index) => (
                  <Card key={question.id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{index + 1}</Badge>
                          <Badge variant="secondary">{question.type}</Badge>
                          <Badge variant="outline">{question.difficulty}</Badge>
                          <Badge variant="outline">{question.points} pts</Badge>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRegenerateQuestion(index)}
                        >
                          <RefreshCw className="w-4 h-4 mr-2" />
                          Regenerate
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <h4 className="font-medium mb-2">{question.title}</h4>
                      <p className="mb-4">{question.content}</p>
                      
                      {question.type === 'multiple-choice' && question.options && (
                        <div className="space-y-2">
                          {question.options.map((option, optIndex) => (
                            <div key={optIndex} className="flex items-center gap-2">
                              <div className={`w-4 h-4 rounded-full border-2 ${
                                option === question.correctAnswer 
                                  ? 'bg-green-500 border-green-500' 
                                  : 'border-gray-300'
                              }`} />
                              <span className={option === question.correctAnswer ? 'font-medium' : ''}>
                                {option}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {question.feedback && (
                        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                          <p className="text-sm"><strong>Feedback:</strong> {question.feedback}</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </>
          )}
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          {generatedAssessment && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Difficulty Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(generatedAssessment.metadata.difficulty_distribution).map(([level, count]) => (
                      <div key={level} className="flex items-center justify-between">
                        <span className="capitalize">{level}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ width: `${(count / generatedAssessment.questions.length) * 100}%` }}
                            />
                          </div>
                          <span className="text-sm text-muted-foreground">{count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Cognitive Level Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(generatedAssessment.metadata.cognitive_distribution).map(([level, count]) => (
                      <div key={level} className="flex items-center justify-between">
                        <span className="capitalize">{level}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-green-600 h-2 rounded-full" 
                              style={{ width: `${(count / generatedAssessment.questions.length) * 100}%` }}
                            />
                          </div>
                          <span className="text-sm text-muted-foreground">{count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="md:col-span-2">
                <CardHeader>
                  <CardTitle>AI Recommendations</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {generatedAssessment.recommendations.map((recommendation, index) => (
                      <Alert key={index} className="border-blue-200 bg-blue-50">
                        <Lightbulb className="h-4 w-4 text-blue-600" />
                        <AlertDescription>
                          {recommendation}
                        </AlertDescription>
                      </Alert>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default AIAssessmentBuilder