"use client"

import React, { useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useToast } from "@/components/ui/use-toast"
import { 
  Plus, 
  Trash2, 
  Edit, 
  Save, 
  Eye, 
  Copy, 
  Move, 
  Clock, 
  Target, 
  CheckCircle, 
  AlertCircle,
  Settings,
  BookOpen,
  FileText,
  Play
} from "lucide-react"

// Assessment types
export type QuestionType = 'multiple-choice' | 'true-false' | 'fill-blank' | 'short-answer' | 'essay' | 'matching' | 'ordering' | 'speaking' | 'listening'

export interface AssessmentQuestion {
  id: string
  type: QuestionType
  title: string
  content: string
  points: number
  timeLimit?: number
  required: boolean
  options?: string[]
  correctAnswer?: string | string[]
  feedback?: string
  difficulty: 'easy' | 'medium' | 'hard'
  tags: string[]
  metadata?: {
    speakingPrompt?: string
    listeningAudio?: string
    imageUrl?: string
    videoUrl?: string
  }
}

export interface AssessmentSettings {
  title: string
  description: string
  timeLimit: number
  attempts: number
  passingScore: number
  randomizeQuestions: boolean
  showResults: boolean
  availableFrom?: Date
  availableTo?: Date
  instructions: string
}

interface AssessmentBuilderProps {
  initialAssessment?: {
    settings: AssessmentSettings
    questions: AssessmentQuestion[]
  }
  onSave?: (assessment: { settings: AssessmentSettings; questions: AssessmentQuestion[] }) => void
  onPreview?: (assessment: { settings: AssessmentSettings; questions: AssessmentQuestion[] }) => void
  className?: string
}

const AssessmentBuilder: React.FC<AssessmentBuilderProps> = ({
  initialAssessment,
  onSave,
  onPreview,
  className = ""
}) => {
  const [settings, setSettings] = useState<AssessmentSettings>(
    initialAssessment?.settings || {
      title: "New Assessment",
      description: "",
      timeLimit: 60,
      attempts: 1,
      passingScore: 70,
      randomizeQuestions: false,
      showResults: true,
      instructions: "Read each question carefully and select the best answer."
    }
  )
  
  const [questions, setQuestions] = useState<AssessmentQuestion[]>(
    initialAssessment?.questions || []
  )
  
  const [activeQuestionId, setActiveQuestionId] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<"settings" | "questions" | "preview">("settings")
  const { toast } = useToast()

  // Question management
  const addQuestion = useCallback((type: QuestionType) => {
    const newQuestion: AssessmentQuestion = {
      id: Date.now().toString(),
      type,
      title: `Question ${questions.length + 1}`,
      content: "",
      points: 1,
      required: true,
      difficulty: 'medium',
      tags: [],
      ...(type === 'multiple-choice' && { options: ['Option 1', 'Option 2', 'Option 3', 'Option 4'] })
    }
    
    setQuestions(prev => [...prev, newQuestion])
    setActiveQuestionId(newQuestion.id)
    setActiveTab("questions")
  }, [questions.length])

  const updateQuestion = useCallback((id: string, updates: Partial<AssessmentQuestion>) => {
    setQuestions(prev => prev.map(q => q.id === id ? { ...q, ...updates } : q))
  }, [])

  const deleteQuestion = useCallback((id: string) => {
    setQuestions(prev => prev.filter(q => q.id !== id))
    if (activeQuestionId === id) {
      setActiveQuestionId(null)
    }
  }, [activeQuestionId])

  const duplicateQuestion = useCallback((id: string) => {
    const question = questions.find(q => q.id === id)
    if (question) {
      const duplicated = {
        ...question,
        id: Date.now().toString(),
        title: `${question.title} (Copy)`
      }
      setQuestions(prev => [...prev, duplicated])
    }
  }, [questions])

  const moveQuestion = useCallback((id: string, direction: 'up' | 'down') => {
    setQuestions(prev => {
      const index = prev.findIndex(q => q.id === id)
      if (index === -1) return prev
      
      const newIndex = direction === 'up' ? index - 1 : index + 1
      if (newIndex < 0 || newIndex >= prev.length) return prev
      
      const newQuestions = [...prev]
      const temp = newQuestions[index]
      newQuestions[index] = newQuestions[newIndex]
      newQuestions[newIndex] = temp
      
      return newQuestions
    })
  }, [])

  // Question option management
  const addOption = useCallback((questionId: string) => {
    const question = questions.find(q => q.id === questionId)
    if (question && question.options) {
      updateQuestion(questionId, {
        options: [...question.options, `Option ${question.options.length + 1}`]
      })
    }
  }, [questions, updateQuestion])

  const updateOption = useCallback((questionId: string, optionIndex: number, value: string) => {
    const question = questions.find(q => q.id === questionId)
    if (question && question.options) {
      const newOptions = [...question.options]
      newOptions[optionIndex] = value
      updateQuestion(questionId, { options: newOptions })
    }
  }, [questions, updateQuestion])

  const removeOption = useCallback((questionId: string, optionIndex: number) => {
    const question = questions.find(q => q.id === questionId)
    if (question && question.options && question.options.length > 2) {
      const newOptions = question.options.filter((_, index) => index !== optionIndex)
      updateQuestion(questionId, { options: newOptions })
    }
  }, [questions, updateQuestion])

  // Save and preview
  const handleSave = useCallback(() => {
    if (!settings.title.trim()) {
      toast({
        title: "Error",
        description: "Please enter a title for the assessment",
        variant: "destructive"
      })
      return
    }

    if (questions.length === 0) {
      toast({
        title: "Error",
        description: "Please add at least one question",
        variant: "destructive"
      })
      return
    }

    onSave?.({ settings, questions })
    toast({
      title: "Success",
      description: "Assessment saved successfully",
    })
  }, [settings, questions, onSave, toast])

  const handlePreview = useCallback(() => {
    onPreview?.({ settings, questions })
  }, [settings, questions, onPreview])

  // Calculate total points
  const totalPoints = questions.reduce((sum, q) => sum + q.points, 0)

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Assessment Builder</h2>
          <p className="text-muted-foreground">Create interactive assessments for your students</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handlePreview}>
            <Eye className="w-4 h-4 mr-2" />
            Preview
          </Button>
          <Button onClick={handleSave}>
            <Save className="w-4 h-4 mr-2" />
            Save Assessment
          </Button>
        </div>
      </div>

      {/* Main content */}
      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList>
          <TabsTrigger value="settings">
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </TabsTrigger>
          <TabsTrigger value="questions">
            <BookOpen className="w-4 h-4 mr-2" />
            Questions ({questions.length})
          </TabsTrigger>
          <TabsTrigger value="preview">
            <Play className="w-4 h-4 mr-2" />
            Preview
          </TabsTrigger>
        </TabsList>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Assessment Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="title">Title</Label>
                  <Input
                    id="title"
                    value={settings.title}
                    onChange={(e) => setSettings(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Enter assessment title"
                  />
                </div>
                <div>
                  <Label htmlFor="timeLimit">Time Limit (minutes)</Label>
                  <Input
                    id="timeLimit"
                    type="number"
                    value={settings.timeLimit}
                    onChange={(e) => setSettings(prev => ({ ...prev, timeLimit: parseInt(e.target.value) }))}
                    min="1"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={settings.description}
                  onChange={(e) => setSettings(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Enter assessment description"
                  rows={3}
                />
              </div>

              <div>
                <Label htmlFor="instructions">Instructions</Label>
                <Textarea
                  id="instructions"
                  value={settings.instructions}
                  onChange={(e) => setSettings(prev => ({ ...prev, instructions: e.target.value }))}
                  placeholder="Enter instructions for students"
                  rows={4}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="attempts">Max Attempts</Label>
                  <Input
                    id="attempts"
                    type="number"
                    value={settings.attempts}
                    onChange={(e) => setSettings(prev => ({ ...prev, attempts: parseInt(e.target.value) }))}
                    min="1"
                  />
                </div>
                <div>
                  <Label htmlFor="passingScore">Passing Score (%)</Label>
                  <Input
                    id="passingScore"
                    type="number"
                    value={settings.passingScore}
                    onChange={(e) => setSettings(prev => ({ ...prev, passingScore: parseInt(e.target.value) }))}
                    min="0"
                    max="100"
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="randomize"
                    checked={settings.randomizeQuestions}
                    onCheckedChange={(checked) => setSettings(prev => ({ ...prev, randomizeQuestions: checked }))}
                  />
                  <Label htmlFor="randomize">Randomize Questions</Label>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="showResults"
                  checked={settings.showResults}
                  onCheckedChange={(checked) => setSettings(prev => ({ ...prev, showResults: checked }))}
                />
                <Label htmlFor="showResults">Show Results to Students</Label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Questions Tab */}
        <TabsContent value="questions" className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h3 className="text-lg font-semibold">Questions</h3>
              <Badge variant="secondary">{questions.length} questions</Badge>
              <Badge variant="outline">{totalPoints} points total</Badge>
            </div>
            
            <Select onValueChange={(value) => addQuestion(value as QuestionType)}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Add Question" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="multiple-choice">Multiple Choice</SelectItem>
                <SelectItem value="true-false">True/False</SelectItem>
                <SelectItem value="fill-blank">Fill in the Blank</SelectItem>
                <SelectItem value="short-answer">Short Answer</SelectItem>
                <SelectItem value="essay">Essay</SelectItem>
                <SelectItem value="matching">Matching</SelectItem>
                <SelectItem value="ordering">Ordering</SelectItem>
                <SelectItem value="speaking">Speaking</SelectItem>
                <SelectItem value="listening">Listening</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {questions.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <FileText className="w-12 h-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No questions yet</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Start building your assessment by adding questions
                </p>
                <Button onClick={() => addQuestion('multiple-choice')}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Your First Question
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Question List */}
              <div className="space-y-3">
                {questions.map((question, index) => (
                  <Card 
                    key={question.id} 
                    className={`cursor-pointer transition-colors ${
                      activeQuestionId === question.id ? 'ring-2 ring-blue-500' : ''
                    }`}
                    onClick={() => setActiveQuestionId(question.id)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="outline">{index + 1}</Badge>
                            <Badge variant="secondary">{question.type}</Badge>
                            <Badge variant="outline">{question.points} pts</Badge>
                          </div>
                          <h4 className="font-medium truncate">{question.title}</h4>
                          <p className="text-sm text-muted-foreground truncate">
                            {question.content || "No content"}
                          </p>
                        </div>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => {
                              e.stopPropagation()
                              moveQuestion(question.id, 'up')
                            }}
                            disabled={index === 0}
                          >
                            <Move className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => {
                              e.stopPropagation()
                              duplicateQuestion(question.id)
                            }}
                          >
                            <Copy className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => {
                              e.stopPropagation()
                              deleteQuestion(question.id)
                            }}
                          >
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Question Editor */}
              <div>
                {activeQuestionId && (
                  <QuestionEditor
                    question={questions.find(q => q.id === activeQuestionId)!}
                    onUpdate={(updates) => updateQuestion(activeQuestionId, updates)}
                    onAddOption={() => addOption(activeQuestionId)}
                    onUpdateOption={(index, value) => updateOption(activeQuestionId, index, value)}
                    onRemoveOption={(index) => removeOption(activeQuestionId, index)}
                  />
                )}
              </div>
            </div>
          )}
        </TabsContent>

        {/* Preview Tab */}
        <TabsContent value="preview">
          <AssessmentPreview settings={settings} questions={questions} />
        </TabsContent>
      </Tabs>
    </div>
  )
}

// Question Editor Component
const QuestionEditor: React.FC<{
  question: AssessmentQuestion
  onUpdate: (updates: Partial<AssessmentQuestion>) => void
  onAddOption: () => void
  onUpdateOption: (index: number, value: string) => void
  onRemoveOption: (index: number) => void
}> = ({ question, onUpdate, onAddOption, onUpdateOption, onRemoveOption }) => {
  return (
    <Card className="sticky top-4">
      <CardHeader>
        <CardTitle>Edit Question</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="questionTitle">Question Title</Label>
          <Input
            id="questionTitle"
            value={question.title}
            onChange={(e) => onUpdate({ title: e.target.value })}
            placeholder="Enter question title"
          />
        </div>

        <div>
          <Label htmlFor="questionContent">Question Content</Label>
          <Textarea
            id="questionContent"
            value={question.content}
            onChange={(e) => onUpdate({ content: e.target.value })}
            placeholder="Enter the question text"
            rows={3}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="points">Points</Label>
            <Input
              id="points"
              type="number"
              value={question.points}
              onChange={(e) => onUpdate({ points: parseInt(e.target.value) })}
              min="0"
            />
          </div>
          <div>
            <Label htmlFor="difficulty">Difficulty</Label>
            <Select value={question.difficulty} onValueChange={(value) => onUpdate({ difficulty: value as any })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="easy">Easy</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="hard">Hard</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Multiple Choice Options */}
        {question.type === 'multiple-choice' && question.options && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <Label>Options</Label>
              <Button variant="outline" size="sm" onClick={onAddOption}>
                <Plus className="w-4 h-4 mr-1" />
                Add Option
              </Button>
            </div>
            <div className="space-y-2">
              {question.options.map((option, index) => (
                <div key={index} className="flex items-center gap-2">
                  <Input
                    value={option}
                    onChange={(e) => onUpdateOption(index, e.target.value)}
                    placeholder={`Option ${index + 1}`}
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => onRemoveOption(index)}
                    disabled={question.options!.length <= 2}
                  >
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        <div>
          <Label htmlFor="correctAnswer">Correct Answer</Label>
          {question.type === 'multiple-choice' ? (
            <Select value={question.correctAnswer as string} onValueChange={(value) => onUpdate({ correctAnswer: value })}>
              <SelectTrigger>
                <SelectValue placeholder="Select correct answer" />
              </SelectTrigger>
              <SelectContent>
                {question.options?.map((option, index) => (
                  <SelectItem key={index} value={option}>{option}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : (
            <Input
              id="correctAnswer"
              value={question.correctAnswer as string || ''}
              onChange={(e) => onUpdate({ correctAnswer: e.target.value })}
              placeholder="Enter correct answer"
            />
          )}
        </div>

        <div>
          <Label htmlFor="feedback">Feedback</Label>
          <Textarea
            id="feedback"
            value={question.feedback || ''}
            onChange={(e) => onUpdate({ feedback: e.target.value })}
            placeholder="Optional feedback for students"
            rows={2}
          />
        </div>
      </CardContent>
    </Card>
  )
}

// Assessment Preview Component
const AssessmentPreview: React.FC<{
  settings: AssessmentSettings
  questions: AssessmentQuestion[]
}> = ({ settings, questions }) => {
  const [answers, setAnswers] = useState<Record<string, string>>({})

  return (
    <Card>
      <CardHeader>
        <CardTitle>{settings.title}</CardTitle>
        <p className="text-muted-foreground">{settings.description}</p>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            {settings.timeLimit} minutes
          </span>
          <span className="flex items-center gap-1">
            <Target className="w-4 h-4" />
            {settings.passingScore}% to pass
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium mb-2">Instructions</h4>
            <p>{settings.instructions}</p>
          </div>

          {questions.map((question, index) => (
            <div key={question.id} className="p-4 border rounded-lg">
              <div className="flex items-start justify-between mb-3">
                <h4 className="font-medium">
                  {index + 1}. {question.title}
                </h4>
                <Badge variant="outline">{question.points} pts</Badge>
              </div>
              
              <p className="mb-4">{question.content}</p>
              
              {question.type === 'multiple-choice' && question.options && (
                <div className="space-y-2">
                  {question.options.map((option, optIndex) => (
                    <div key={optIndex} className="flex items-center gap-2">
                      <input
                        type="radio"
                        name={`question-${question.id}`}
                        value={option}
                        checked={answers[question.id] === option}
                        onChange={(e) => setAnswers(prev => ({ ...prev, [question.id]: e.target.value }))}
                      />
                      <label>{option}</label>
                    </div>
                  ))}
                </div>
              )}
              
              {question.type === 'short-answer' && (
                <Input
                  value={answers[question.id] || ''}
                  onChange={(e) => setAnswers(prev => ({ ...prev, [question.id]: e.target.value }))}
                  placeholder="Enter your answer"
                />
              )}
              
              {question.type === 'essay' && (
                <Textarea
                  value={answers[question.id] || ''}
                  onChange={(e) => setAnswers(prev => ({ ...prev, [question.id]: e.target.value }))}
                  placeholder="Enter your essay response"
                  rows={4}
                />
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export default AssessmentBuilder