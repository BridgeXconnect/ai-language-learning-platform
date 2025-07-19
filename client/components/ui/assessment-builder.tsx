/**
 * Assessment Builder Component
 * Interactive assessment creation with AI assistance
 * Features: Multiple question types, AI generation, accessibility, validation
 */

"use client"

import React, { useState, useCallback, useRef } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/enhanced-button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/enhanced-card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { 
  Plus, 
  Minus, 
  Eye, 
  Edit3, 
  Save, 
  Trash2, 
  Copy, 
  Move, 
  Settings, 
  Wand2,
  Brain,
  CheckCircle,
  Circle,
  Square,
  Type,
  FileText,
  Code,
  Image,
  Clock,
  Target,
  TrendingUp,
  AlertCircle,
  HelpCircle,
  ChevronUp,
  ChevronDown,
  GripVertical,
  Shuffle,
  RotateCcw
} from 'lucide-react'

const assessmentBuilderVariants = cva(
  [
    'w-full h-full flex flex-col bg-background',
  ],
  {
    variants: {
      variant: {
        default: 'border rounded-lg',
        fullscreen: 'border-none rounded-none',
        embedded: 'border-none',
      },
      state: {
        draft: 'border-gray-200',
        preview: 'border-blue-200 bg-blue-50/50',
        published: 'border-green-200 bg-green-50/50',
        archived: 'border-gray-300 bg-gray-50/50',
      },
    },
    defaultVariants: {
      variant: 'default',
      state: 'draft',
    },
  }
)

export type QuestionType = 'multiple_choice' | 'single_choice' | 'true_false' | 'short_answer' | 'long_answer' | 'matching' | 'ordering' | 'fill_blanks' | 'code' | 'practical'

// Question type configurations - moved outside component for reuse
const questionTypes = {
  multiple_choice: {
    label: 'Multiple Choice',
    icon: CheckCircle,
    description: 'Select one or more correct answers',
    supportsOptions: true,
    defaultOptions: 4,
  },
  single_choice: {
    label: 'Single Choice',
    icon: Circle,
    description: 'Select exactly one correct answer',
    supportsOptions: true,
    defaultOptions: 4,
  },
  true_false: {
    label: 'True/False',
    icon: Square,
    description: 'Simple true or false question',
    supportsOptions: true,
    defaultOptions: 2,
  },
  short_answer: {
    label: 'Short Answer',
    icon: Type,
    description: 'Brief text response',
    supportsOptions: false,
    defaultOptions: 0,
  },
  long_answer: {
    label: 'Long Answer',
    icon: FileText,
    description: 'Extended text response',
    supportsOptions: false,
    defaultOptions: 0,
  },
  matching: {
    label: 'Matching',
    icon: Shuffle,
    description: 'Match items from two lists',
    supportsOptions: true,
    defaultOptions: 4,
  },
  ordering: {
    label: 'Ordering',
    icon: GripVertical,
    description: 'Put items in correct order',
    supportsOptions: true,
    defaultOptions: 4,
  },
  fill_blanks: {
    label: 'Fill Blanks',
    icon: Square,
    description: 'Fill in missing words',
    supportsOptions: false,
    defaultOptions: 0,
  },
  code: {
    label: 'Code',
    icon: Code,
    description: 'Programming code response',
    supportsOptions: false,
    defaultOptions: 0,
  },
  practical: {
    label: 'Practical',
    icon: Target,
    description: 'Hands-on demonstration',
    supportsOptions: false,
    defaultOptions: 0,
  },
}

export interface QuestionOption {
  id: string
  text: string
  isCorrect: boolean
  explanation?: string
  order?: number
}

export interface Question {
  id: string
  type: QuestionType
  title: string
  content: string
  options: QuestionOption[]
  correctAnswer?: string
  explanation?: string
  hints?: string[]
  points: number
  timeLimit?: number
  difficulty: 'easy' | 'medium' | 'hard'
  tags: string[]
  metadata: {
    aiGenerated?: boolean
    bloomsLevel?: 'remember' | 'understand' | 'apply' | 'analyze' | 'evaluate' | 'create'
    learningObjective?: string
    prerequisites?: string[]
  }
  validation?: {
    required: boolean
    caseSensitive?: boolean
    exactMatch?: boolean
    allowPartialCredit?: boolean
  }
}

export interface Assessment {
  id: string
  title: string
  description: string
  instructions: string
  questions: Question[]
  settings: {
    timeLimit?: number
    shuffleQuestions: boolean
    shuffleOptions: boolean
    showResults: boolean
    allowRetries: boolean
    maxRetries?: number
    passingScore: number
    showCorrectAnswers: boolean
    showExplanations: boolean
    randomizeFromPool: boolean
    questionsPerAttempt?: number
  }
  metadata: {
    category: string
    tags: string[]
    difficulty: 'beginner' | 'intermediate' | 'advanced'
    estimatedTime: number
    totalPoints: number
    createdAt: Date
    updatedAt: Date
    version: number
    status: 'draft' | 'review' | 'published' | 'archived'
  }
}

export interface AssessmentBuilderProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof assessmentBuilderVariants> {
  // Core props
  assessment: Assessment
  onAssessmentChange: (assessment: Assessment) => void
  onSave: (assessment: Assessment) => void
  onPreview: (assessment: Assessment) => void
  onPublish: (assessment: Assessment) => void
  
  // AI assistance
  onAIGenerate?: (prompt: string, questionType: QuestionType) => Promise<Question>
  onAIEnhance?: (question: Question) => Promise<Question>
  onAISuggest?: (context: string) => Promise<string[]>
  
  // Validation
  onValidate?: (assessment: Assessment) => Promise<string[]>
  
  // Display options
  showAIFeatures?: boolean
  showPreview?: boolean
  showAdvancedOptions?: boolean
  
  // Accessibility
  ariaLabel?: string
}

const AssessmentBuilder = React.forwardRef<HTMLDivElement, AssessmentBuilderProps>(
  ({
    className,
    variant,
    state,
    assessment,
    onAssessmentChange,
    onSave,
    onPreview,
    onPublish,
    onAIGenerate,
    onAIEnhance,
    onAISuggest,
    onValidate,
    showAIFeatures = true,
    showPreview = true,
    showAdvancedOptions = true,
    ariaLabel = "Assessment Builder",
    ...props
  }, ref) => {
    const [activeTab, setActiveTab] = useState<string>('questions')
    const [selectedQuestion, setSelectedQuestion] = useState<string | null>(null)
    const [isGenerating, setIsGenerating] = useState(false)
    const [aiPrompt, setAiPrompt] = useState('')
    const [validationErrors, setValidationErrors] = useState<string[]>([])
    const [isDragging, setIsDragging] = useState(false)
    
    const dragItemRef = useRef<number | null>(null)
    const dragOverItemRef = useRef<number | null>(null)
    
    // Update assessment helper
    const updateAssessment = useCallback((updates: Partial<Assessment>) => {
      const updatedAssessment = {
        ...assessment,
        ...updates,
        metadata: {
          ...assessment.metadata,
          ...updates.metadata,
          updatedAt: new Date(),
        },
      }
      onAssessmentChange(updatedAssessment)
    }, [assessment, onAssessmentChange])
    
    // Question management
    const addQuestion = useCallback((type: QuestionType) => {
      const newQuestion: Question = {
        id: `q_${Date.now()}`,
        type,
        title: '',
        content: '',
        options: questionTypes[type].supportsOptions 
          ? Array.from({ length: questionTypes[type].defaultOptions }, (_, i) => ({
              id: `opt_${Date.now()}_${i}`,
              text: '',
              isCorrect: i === 0,
              order: i,
            }))
          : [],
        points: 1,
        difficulty: 'medium',
        tags: [],
        metadata: {
          aiGenerated: false,
        },
        validation: {
          required: true,
        },
      }
      
      updateAssessment({
        questions: [...assessment.questions, newQuestion],
        metadata: {
          ...assessment.metadata,
          totalPoints: assessment.metadata.totalPoints + 1,
        },
      })
      
      setSelectedQuestion(newQuestion.id)
    }, [assessment, updateAssessment])
    
    const updateQuestion = useCallback((questionId: string, updates: Partial<Question>) => {
      const updatedQuestions = assessment.questions.map(q => 
        q.id === questionId ? { ...q, ...updates } : q
      )
      
      const totalPoints = updatedQuestions.reduce((sum, q) => sum + q.points, 0)
      
      updateAssessment({
        questions: updatedQuestions,
        metadata: {
          ...assessment.metadata,
          totalPoints,
        },
      })
    }, [assessment, updateAssessment])
    
    const removeQuestion = useCallback((questionId: string) => {
      const updatedQuestions = assessment.questions.filter(q => q.id !== questionId)
      const totalPoints = updatedQuestions.reduce((sum, q) => sum + q.points, 0)
      
      updateAssessment({
        questions: updatedQuestions,
        metadata: {
          ...assessment.metadata,
          totalPoints,
        },
      })
      
      if (selectedQuestion === questionId) {
        setSelectedQuestion(null)
      }
    }, [assessment, updateAssessment, selectedQuestion])
    
    const duplicateQuestion = useCallback((questionId: string) => {
      const questionToDuplicate = assessment.questions.find(q => q.id === questionId)
      if (!questionToDuplicate) return
      
      const duplicatedQuestion: Question = {
        ...questionToDuplicate,
        id: `q_${Date.now()}`,
        title: `${questionToDuplicate.title} (Copy)`,
        options: questionToDuplicate.options.map(opt => ({
          ...opt,
          id: `opt_${Date.now()}_${opt.order}`,
        })),
      }
      
      updateAssessment({
        questions: [...assessment.questions, duplicatedQuestion],
        metadata: {
          ...assessment.metadata,
          totalPoints: assessment.metadata.totalPoints + duplicatedQuestion.points,
        },
      })
    }, [assessment, updateAssessment])
    
    // AI-powered question generation
    const generateAIQuestion = useCallback(async (type: QuestionType) => {
      if (!onAIGenerate) return
      
      setIsGenerating(true)
      try {
        const generatedQuestion = await onAIGenerate(aiPrompt, type)
        updateAssessment({
          questions: [...assessment.questions, generatedQuestion],
          metadata: {
            ...assessment.metadata,
            totalPoints: assessment.metadata.totalPoints + generatedQuestion.points,
          },
        })
        setSelectedQuestion(generatedQuestion.id)
        setAiPrompt('')
      } catch (error) {
        console.error('Failed to generate AI question:', error)
      } finally {
        setIsGenerating(false)
      }
    }, [aiPrompt, assessment, updateAssessment, onAIGenerate])
    
    // Question option management
    const addOption = useCallback((questionId: string) => {
      const question = assessment.questions.find(q => q.id === questionId)
      if (!question) return
      
      const newOption: QuestionOption = {
        id: `opt_${Date.now()}`,
        text: '',
        isCorrect: false,
        order: question.options.length,
      }
      
      updateQuestion(questionId, {
        options: [...question.options, newOption],
      })
    }, [assessment, updateQuestion])
    
    const updateOption = useCallback((questionId: string, optionId: string, updates: Partial<QuestionOption>) => {
      const question = assessment.questions.find(q => q.id === questionId)
      if (!question) return
      
      const updatedOptions = question.options.map(opt => 
        opt.id === optionId ? { ...opt, ...updates } : opt
      )
      
      updateQuestion(questionId, { options: updatedOptions })
    }, [assessment, updateQuestion])
    
    const removeOption = useCallback((questionId: string, optionId: string) => {
      const question = assessment.questions.find(q => q.id === questionId)
      if (!question || question.options.length <= 2) return
      
      const updatedOptions = question.options
        .filter(opt => opt.id !== optionId)
        .map((opt, index) => ({ ...opt, order: index }))
      
      updateQuestion(questionId, { options: updatedOptions })
    }, [assessment, updateQuestion])
    
    // Validation
    const validateAssessment = useCallback(async () => {
      const errors: string[] = []
      
      if (!assessment.title.trim()) {
        errors.push('Assessment title is required')
      }
      
      if (assessment.questions.length === 0) {
        errors.push('At least one question is required')
      }
      
      assessment.questions.forEach((question, index) => {
        if (!question.title.trim()) {
          errors.push(`Question ${index + 1} title is required`)
        }
        
        if (!question.content.trim()) {
          errors.push(`Question ${index + 1} content is required`)
        }
        
        if (questionTypes[question.type].supportsOptions && question.options.length === 0) {
          errors.push(`Question ${index + 1} requires at least one option`)
        }
        
        if (questionTypes[question.type].supportsOptions && !question.options.some(opt => opt.isCorrect)) {
          errors.push(`Question ${index + 1} must have at least one correct answer`)
        }
      })
      
      if (onValidate) {
        const customErrors = await onValidate(assessment)
        errors.push(...customErrors)
      }
      
      setValidationErrors(errors)
      return errors.length === 0
    }, [assessment, onValidate])
    
    // Handle save
    const handleSave = useCallback(async () => {
      const isValid = await validateAssessment()
      if (isValid) {
        onSave(assessment)
      }
    }, [assessment, onSave, validateAssessment])
    
    // Handle preview
    const handlePreview = useCallback(async () => {
      const isValid = await validateAssessment()
      if (isValid) {
        onPreview(assessment)
      }
    }, [assessment, onPreview, validateAssessment])
    
    // Handle publish
    const handlePublish = useCallback(async () => {
      const isValid = await validateAssessment()
      if (isValid) {
        onPublish(assessment)
      }
    }, [assessment, onPublish, validateAssessment])
    
    // Drag and drop for question reordering
    const handleDragStart = useCallback((index: number) => {
      dragItemRef.current = index
      setIsDragging(true)
    }, [])
    
    const handleDragEnter = useCallback((index: number) => {
      dragOverItemRef.current = index
    }, [])
    
    const handleDragEnd = useCallback(() => {
      if (dragItemRef.current === null || dragOverItemRef.current === null) return
      
      const draggedItem = assessment.questions[dragItemRef.current]
      const newQuestions = [...assessment.questions]
      
      newQuestions.splice(dragItemRef.current, 1)
      newQuestions.splice(dragOverItemRef.current, 0, draggedItem)
      
      updateAssessment({ questions: newQuestions })
      
      dragItemRef.current = null
      dragOverItemRef.current = null
      setIsDragging(false)
    }, [assessment, updateAssessment])
    
    const selectedQuestionData = assessment.questions.find(q => q.id === selectedQuestion)
    
    return (
      <div
        ref={ref}
        className={cn(assessmentBuilderVariants({ variant, state }), className)}
        role="region"
        aria-label={ariaLabel}
        {...props}
      >
        {/* Header */}
        <div className="flex-shrink-0 p-4 border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div>
                <h2 className="text-lg font-semibold">{assessment.title || 'Untitled Assessment'}</h2>
                <p className="text-sm text-muted-foreground">
                  {assessment.questions.length} questions • {assessment.metadata.totalPoints} points
                </p>
              </div>
              
              <Badge variant={state === 'published' ? 'default' : 'secondary'}>
                {assessment.metadata.status}
              </Badge>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleSave}
                disabled={validationErrors.length > 0}
              >
                <Save className="h-4 w-4 mr-2" />
                Save
              </Button>
              
              {showPreview && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handlePreview}
                  disabled={validationErrors.length > 0}
                >
                  <Eye className="h-4 w-4 mr-2" />
                  Preview
                </Button>
              )}
              
              <Button
                onClick={handlePublish}
                disabled={validationErrors.length > 0 || assessment.metadata.status === 'published'}
              >
                Publish
              </Button>
            </div>
          </div>
          
          {/* Validation errors */}
          {validationErrors.length > 0 && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <h4 className="text-sm font-medium text-red-800">Validation Errors</h4>
              </div>
              <ul className="text-sm text-red-700 space-y-1">
                {validationErrors.map((error, index) => (
                  <li key={index}>• {error}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
        
        {/* Main content */}
        <div className="flex-1 overflow-hidden">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="questions">Questions</TabsTrigger>
              <TabsTrigger value="settings">Settings</TabsTrigger>
              <TabsTrigger value="metadata">Metadata</TabsTrigger>
            </TabsList>
            
            <div className="flex-1 overflow-hidden">
              <TabsContent value="questions" className="h-full m-0">
                <div className="h-full flex">
                  {/* Question list */}
                  <div className="w-1/3 border-r bg-gray-50">
                    <div className="p-4 border-b bg-white">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-medium">Questions</h3>
                        <Badge variant="secondary">
                          {assessment.questions.length}
                        </Badge>
                      </div>
                      
                      {/* AI generation */}
                      {showAIFeatures && (
                        <div className="space-y-2 mb-4">
                          <Textarea
                            value={aiPrompt}
                            onChange={(e) => setAiPrompt(e.target.value)}
                            placeholder="Describe the question you want to generate..."
                            className="min-h-[60px]"
                          />
                          <div className="flex flex-wrap gap-1">
                            {Object.entries(questionTypes).map(([type, config]) => (
                              <Button
                                key={type}
                                variant="outline"
                                size="sm"
                                onClick={() => generateAIQuestion(type as QuestionType)}
                                disabled={!aiPrompt.trim() || isGenerating}
                                className="text-xs"
                              >
                                <config.icon className="h-3 w-3 mr-1" />
                                {config.label}
                              </Button>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {/* Manual question addition */}
                      <div className="flex flex-wrap gap-1">
                        {Object.entries(questionTypes).map(([type, config]) => (
                          <Button
                            key={type}
                            variant="outline"
                            size="sm"
                            onClick={() => addQuestion(type as QuestionType)}
                            className="text-xs"
                          >
                            <Plus className="h-3 w-3 mr-1" />
                            {config.label}
                          </Button>
                        ))}
                      </div>
                    </div>
                    
                    {/* Question list */}
                    <ScrollArea className="h-[calc(100%-200px)]">
                      <div className="p-2 space-y-2">
                        {assessment.questions.map((question, index) => {
                          const QuestionIcon = questionTypes[question.type].icon
                          return (
                            <Card
                              key={question.id}
                              className={cn(
                                "cursor-pointer transition-all duration-200",
                                selectedQuestion === question.id 
                                  ? "ring-2 ring-primary bg-primary/5" 
                                  : "hover:bg-accent/50"
                              )}
                              onClick={() => setSelectedQuestion(question.id)}
                              draggable
                              onDragStart={() => handleDragStart(index)}
                              onDragEnter={() => handleDragEnter(index)}
                              onDragEnd={handleDragEnd}
                            >
                              <CardContent className="p-3">
                                <div className="flex items-start gap-3">
                                  <GripVertical className="h-4 w-4 text-gray-400 mt-1 cursor-move" />
                                  
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                      <QuestionIcon className="h-4 w-4 text-gray-600" />
                                      <span className="text-xs font-medium text-gray-600">
                                        Question {index + 1}
                                      </span>
                                      <Badge variant="outline" className="text-xs">
                                        {question.points}pt
                                      </Badge>
                                    </div>
                                    
                                    <h4 className="text-sm font-medium truncate">
                                      {question.title || 'Untitled Question'}
                                    </h4>
                                    
                                    <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                                      {question.content}
                                    </p>
                                    
                                    <div className="flex items-center gap-2 mt-2">
                                      <Badge variant="secondary" className="text-xs">
                                        {question.difficulty}
                                      </Badge>
                                      {question.metadata.aiGenerated && (
                                        <Badge variant="outline" className="text-xs">
                                          <Brain className="h-3 w-3 mr-1" />
                                          AI
                                        </Badge>
                                      )}
                                    </div>
                                  </div>
                                  
                                  <div className="flex flex-col gap-1">
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={(e) => {
                                        e.stopPropagation()
                                        duplicateQuestion(question.id)
                                      }}
                                    >
                                      <Copy className="h-3 w-3" />
                                    </Button>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={(e) => {
                                        e.stopPropagation()
                                        removeQuestion(question.id)
                                      }}
                                    >
                                      <Trash2 className="h-3 w-3" />
                                    </Button>
                                  </div>
                                </div>
                              </CardContent>
                            </Card>
                          )
                        })}
                      </div>
                    </ScrollArea>
                  </div>
                  
                  {/* Question editor */}
                  <div className="flex-1 overflow-hidden">
                    {selectedQuestionData ? (
                      <QuestionEditor
                        question={selectedQuestionData}
                        onUpdate={(updates) => updateQuestion(selectedQuestionData.id, updates)}
                        onAddOption={() => addOption(selectedQuestionData.id)}
                        onUpdateOption={(optionId, updates) => updateOption(selectedQuestionData.id, optionId, updates)}
                        onRemoveOption={(optionId) => removeOption(selectedQuestionData.id, optionId)}
                        onAIEnhance={onAIEnhance}
                        showAIFeatures={showAIFeatures}
                        showAdvancedOptions={showAdvancedOptions}
                      />
                    ) : (
                      <div className="h-full flex items-center justify-center">
                        <div className="text-center">
                          <HelpCircle className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                          <h3 className="text-lg font-medium text-gray-600 mb-2">
                            No Question Selected
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            Select a question from the list to start editing
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="settings" className="h-full m-0">
                <AssessmentSettings
                  assessment={assessment}
                  onUpdate={updateAssessment}
                />
              </TabsContent>
              
              <TabsContent value="metadata" className="h-full m-0">
                <AssessmentMetadata
                  assessment={assessment}
                  onUpdate={updateAssessment}
                />
              </TabsContent>
            </div>
          </Tabs>
        </div>
      </div>
    )
  }
)

// Question Editor Component
interface QuestionEditorProps {
  question: Question
  onUpdate: (updates: Partial<Question>) => void
  onAddOption: () => void
  onUpdateOption: (optionId: string, updates: Partial<QuestionOption>) => void
  onRemoveOption: (optionId: string) => void
  onAIEnhance?: (question: Question) => Promise<Question>
  showAIFeatures: boolean
  showAdvancedOptions: boolean
}

function QuestionEditor({
  question,
  onUpdate,
  onAddOption,
  onUpdateOption,
  onRemoveOption,
  onAIEnhance,
  showAIFeatures,
  showAdvancedOptions,
}: QuestionEditorProps) {
  const [isEnhancing, setIsEnhancing] = useState(false)
  const questionConfig = questionTypes[question.type]
  
  const handleAIEnhance = async () => {
    if (!onAIEnhance) return
    
    setIsEnhancing(true)
    try {
      const enhancedQuestion = await onAIEnhance(question)
      onUpdate(enhancedQuestion)
    } catch (error) {
      console.error('Failed to enhance question:', error)
    } finally {
      setIsEnhancing(false)
    }
  }
  
  return (
    <ScrollArea className="h-full">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <questionConfig.icon className="h-5 w-5 text-gray-600" />
            <h3 className="text-lg font-semibold">Edit Question</h3>
            <Badge variant="outline">{questionConfig.label}</Badge>
          </div>
          
          {showAIFeatures && onAIEnhance && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleAIEnhance}
              disabled={isEnhancing}
            >
              <Wand2 className="h-4 w-4 mr-2" />
              {isEnhancing ? 'Enhancing...' : 'AI Enhance'}
            </Button>
          )}
        </div>
        
        {/* Basic fields */}
        <div className="space-y-4">
          <div>
            <Label htmlFor="question-title">Question Title</Label>
            <Input
              id="question-title"
              value={question.title}
              onChange={(e) => onUpdate({ title: e.target.value })}
              placeholder="Enter question title..."
            />
          </div>
          
          <div>
            <Label htmlFor="question-content">Question Content</Label>
            <Textarea
              id="question-content"
              value={question.content}
              onChange={(e) => onUpdate({ content: e.target.value })}
              placeholder="Enter question content..."
              className="min-h-[100px]"
            />
          </div>
        </div>
        
        {/* Options */}
        {questionConfig.supportsOptions && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <Label>Answer Options</Label>
              <Button
                variant="outline"
                size="sm"
                onClick={onAddOption}
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Option
              </Button>
            </div>
            
            <div className="space-y-3">
              {question.options.map((option, index) => (
                <div key={option.id} className="flex items-center gap-3 p-3 border rounded-lg">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium w-6">
                      {String.fromCharCode(65 + index)}
                    </span>
                    <Switch
                      checked={option.isCorrect}
                      onCheckedChange={(checked) => onUpdateOption(option.id, { isCorrect: checked })}
                    />
                    <Label className="text-xs text-muted-foreground">
                      Correct
                    </Label>
                  </div>
                  
                  <Input
                    value={option.text}
                    onChange={(e) => onUpdateOption(option.id, { text: e.target.value })}
                    placeholder={`Option ${String.fromCharCode(65 + index)}`}
                    className="flex-1"
                  />
                  
                  {question.options.length > 2 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onRemoveOption(option.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Question settings */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="question-points">Points</Label>
            <Input
              id="question-points"
              type="number"
              min="0"
              value={question.points}
              onChange={(e) => onUpdate({ points: parseInt(e.target.value) || 0 })}
            />
          </div>
          
          <div>
            <Label htmlFor="question-difficulty">Difficulty</Label>
            <Select
              value={question.difficulty}
              onValueChange={(value) => onUpdate({ difficulty: value as Question['difficulty'] })}
            >
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
        
        {/* Advanced options */}
        {showAdvancedOptions && (
          <div className="space-y-4">
            <Separator />
            <h4 className="font-medium">Advanced Options</h4>
            
            <div>
              <Label htmlFor="question-explanation">Explanation</Label>
              <Textarea
                id="question-explanation"
                value={question.explanation || ''}
                onChange={(e) => onUpdate({ explanation: e.target.value })}
                placeholder="Provide explanation for the correct answer..."
              />
            </div>
            
            <div>
              <Label htmlFor="question-time-limit">Time Limit (seconds)</Label>
              <Input
                id="question-time-limit"
                type="number"
                min="0"
                value={question.timeLimit || ''}
                onChange={(e) => onUpdate({ timeLimit: parseInt(e.target.value) || undefined })}
                placeholder="Leave empty for no time limit"
              />
            </div>
            
            <div>
              <Label htmlFor="question-tags">Tags</Label>
              <Input
                id="question-tags"
                value={question.tags.join(', ')}
                onChange={(e) => onUpdate({ tags: e.target.value.split(',').map(t => t.trim()).filter(Boolean) })}
                placeholder="Enter tags separated by commas"
              />
            </div>
          </div>
        )}
      </div>
    </ScrollArea>
  )
}

// Assessment Settings Component
interface AssessmentSettingsProps {
  assessment: Assessment
  onUpdate: (updates: Partial<Assessment>) => void
}

function AssessmentSettings({ assessment, onUpdate }: AssessmentSettingsProps) {
  const updateSettings = (updates: Partial<Assessment['settings']>) => {
    onUpdate({
      settings: {
        ...assessment.settings,
        ...updates,
      },
    })
  }
  
  return (
    <ScrollArea className="h-full">
      <div className="p-6 space-y-6">
        <div>
          <h3 className="text-lg font-semibold mb-4">Assessment Settings</h3>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="assessment-time-limit">Time Limit (minutes)</Label>
              <Input
                id="assessment-time-limit"
                type="number"
                min="0"
                value={assessment.settings.timeLimit || ''}
                onChange={(e) => updateSettings({ timeLimit: parseInt(e.target.value) || undefined })}
                placeholder="Leave empty for no time limit"
              />
            </div>
            
            <div>
              <Label htmlFor="passing-score">Passing Score (%)</Label>
              <Input
                id="passing-score"
                type="number"
                min="0"
                max="100"
                value={assessment.settings.passingScore}
                onChange={(e) => updateSettings({ passingScore: parseInt(e.target.value) || 0 })}
              />
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="shuffle-questions">Shuffle Questions</Label>
                <Switch
                  id="shuffle-questions"
                  checked={assessment.settings.shuffleQuestions}
                  onCheckedChange={(checked) => updateSettings({ shuffleQuestions: checked })}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="shuffle-options">Shuffle Options</Label>
                <Switch
                  id="shuffle-options"
                  checked={assessment.settings.shuffleOptions}
                  onCheckedChange={(checked) => updateSettings({ shuffleOptions: checked })}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="show-results">Show Results</Label>
                <Switch
                  id="show-results"
                  checked={assessment.settings.showResults}
                  onCheckedChange={(checked) => updateSettings({ showResults: checked })}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="allow-retries">Allow Retries</Label>
                <Switch
                  id="allow-retries"
                  checked={assessment.settings.allowRetries}
                  onCheckedChange={(checked) => updateSettings({ allowRetries: checked })}
                />
              </div>
              
              {assessment.settings.allowRetries && (
                <div>
                  <Label htmlFor="max-retries">Maximum Retries</Label>
                  <Input
                    id="max-retries"
                    type="number"
                    min="1"
                    value={assessment.settings.maxRetries || ''}
                    onChange={(e) => updateSettings({ maxRetries: parseInt(e.target.value) || undefined })}
                    placeholder="Leave empty for unlimited"
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </ScrollArea>
  )
}

// Assessment Metadata Component
interface AssessmentMetadataProps {
  assessment: Assessment
  onUpdate: (updates: Partial<Assessment>) => void
}

function AssessmentMetadata({ assessment, onUpdate }: AssessmentMetadataProps) {
  const updateMetadata = (updates: Partial<Assessment['metadata']>) => {
    onUpdate({
      metadata: {
        ...assessment.metadata,
        ...updates,
      },
    })
  }
  
  return (
    <ScrollArea className="h-full">
      <div className="p-6 space-y-6">
        <div>
          <h3 className="text-lg font-semibold mb-4">Assessment Metadata</h3>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="assessment-title">Title</Label>
              <Input
                id="assessment-title"
                value={assessment.title}
                onChange={(e) => onUpdate({ title: e.target.value })}
                placeholder="Enter assessment title..."
              />
            </div>
            
            <div>
              <Label htmlFor="assessment-description">Description</Label>
              <Textarea
                id="assessment-description"
                value={assessment.description}
                onChange={(e) => onUpdate({ description: e.target.value })}
                placeholder="Enter assessment description..."
              />
            </div>
            
            <div>
              <Label htmlFor="assessment-instructions">Instructions</Label>
              <Textarea
                id="assessment-instructions"
                value={assessment.instructions}
                onChange={(e) => onUpdate({ instructions: e.target.value })}
                placeholder="Enter instructions for students..."
              />
            </div>
            
            <div>
              <Label htmlFor="assessment-category">Category</Label>
              <Input
                id="assessment-category"
                value={assessment.metadata.category}
                onChange={(e) => updateMetadata({ category: e.target.value })}
                placeholder="Enter category..."
              />
            </div>
            
            <div>
              <Label htmlFor="assessment-tags">Tags</Label>
              <Input
                id="assessment-tags"
                value={assessment.metadata.tags.join(', ')}
                onChange={(e) => updateMetadata({ tags: e.target.value.split(',').map(t => t.trim()).filter(Boolean) })}
                placeholder="Enter tags separated by commas"
              />
            </div>
            
            <div>
              <Label htmlFor="assessment-difficulty">Difficulty</Label>
              <Select
                value={assessment.metadata.difficulty}
                onValueChange={(value) => updateMetadata({ difficulty: value as Assessment['metadata']['difficulty'] })}
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
              <Label htmlFor="estimated-time">Estimated Time (minutes)</Label>
              <Input
                id="estimated-time"
                type="number"
                min="0"
                value={assessment.metadata.estimatedTime}
                onChange={(e) => updateMetadata({ estimatedTime: parseInt(e.target.value) || 0 })}
              />
            </div>
          </div>
        </div>
      </div>
    </ScrollArea>
  )
}

AssessmentBuilder.displayName = 'AssessmentBuilder'

export { AssessmentBuilder, assessmentBuilderVariants }