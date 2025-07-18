"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { 
  DragDropContext, 
  Droppable, 
  Draggable,
  DropResult 
} from "@hello-pangea/dnd"
import {
  Plus,
  Trash2,
  Edit3,
  GripVertical,
  Clock,
  BookOpen,
  CheckCircle,
  FileText,
  Video,
  HeadphonesIcon,
  Image,
  Target,
  Users,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Copy,
  Eye,
  Settings
} from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { toast } from "@/components/ui/use-toast"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"

interface CurriculumBuilderProps {
  modules: LessonModule[]
  onUpdateModules: (modules: LessonModule[]) => void
  onSelectModule: (module: LessonModule) => void
  selectedModule?: LessonModule | null
}

interface LessonModule {
  id: string
  title: string
  description: string
  type: 'lesson' | 'assessment' | 'activity' | 'video' | 'reading'
  duration: number
  order: number
  content: {
    text?: string
    media?: MediaItem[]
    exercises?: Exercise[]
    objectives?: string[]
    prerequisites?: string[]
  }
  aiGenerated: boolean
  status: 'draft' | 'complete' | 'review' | 'published'
  isExpanded?: boolean
  settings: {
    isRequired: boolean
    allowSkip: boolean
    retakeAllowed: boolean
    passingScore?: number
  }
}

interface MediaItem {
  id: string
  type: 'image' | 'video' | 'audio' | 'document'
  url: string
  name: string
  description?: string
  duration?: number
}

interface Exercise {
  id: string
  type: 'multiple_choice' | 'essay' | 'fill_blank' | 'matching' | 'code'
  question: string
  options?: string[]
  answer: string
  explanation?: string
  points: number
}

const MODULE_TYPES = [
  { value: 'lesson', label: 'Lesson', icon: BookOpen, color: 'bg-blue-500' },
  { value: 'assessment', label: 'Assessment', icon: Target, color: 'bg-green-500' },
  { value: 'activity', label: 'Activity', icon: Users, color: 'bg-purple-500' },
  { value: 'video', label: 'Video', icon: Video, color: 'bg-red-500' },
  { value: 'reading', label: 'Reading', icon: FileText, color: 'bg-orange-500' }
]

const STATUS_COLORS = {
  draft: 'bg-gray-500',
  complete: 'bg-green-500',
  review: 'bg-yellow-500',
  published: 'bg-blue-500'
}

export function CurriculumBuilder({ 
  modules, 
  onUpdateModules, 
  onSelectModule,
  selectedModule 
}: CurriculumBuilderProps) {
  const [editingModule, setEditingModule] = useState<LessonModule | null>(null)
  const [showAddModule, setShowAddModule] = useState(false)
  const [newModule, setNewModule] = useState<Partial<LessonModule>>({
    title: '',
    description: '',
    type: 'lesson',
    duration: 30,
    settings: {
      isRequired: true,
      allowSkip: false,
      retakeAllowed: true
    }
  })

  const handleDragEnd = (result: DropResult) => {
    if (!result.destination) return

    const items = Array.from(modules)
    const [reorderedItem] = items.splice(result.source.index, 1)
    items.splice(result.destination.index, 0, reorderedItem)

    // Update order values
    const updatedItems = items.map((item, index) => ({
      ...item,
      order: index + 1
    }))

    onUpdateModules(updatedItems)
  }

  const addModule = () => {
    const module: LessonModule = {
      id: Date.now().toString(),
      title: newModule.title || 'New Module',
      description: newModule.description || '',
      type: newModule.type as any || 'lesson',
      duration: newModule.duration || 30,
      order: modules.length + 1,
      content: {
        objectives: [],
        prerequisites: []
      },
      aiGenerated: false,
      status: 'draft',
      isExpanded: false,
      settings: newModule.settings || {
        isRequired: true,
        allowSkip: false,
        retakeAllowed: true
      }
    }

    onUpdateModules([...modules, module])
    setNewModule({
      title: '',
      description: '',
      type: 'lesson',
      duration: 30,
      settings: {
        isRequired: true,
        allowSkip: false,
        retakeAllowed: true
      }
    })
    setShowAddModule(false)
    toast({
      title: "Module Added",
      description: "New module has been added to your curriculum"
    })
  }

  const updateModule = (moduleId: string, updates: Partial<LessonModule>) => {
    const updatedModules = modules.map(module => 
      module.id === moduleId ? { ...module, ...updates } : module
    )
    onUpdateModules(updatedModules)
  }

  const deleteModule = (moduleId: string) => {
    const updatedModules = modules.filter(module => module.id !== moduleId)
    onUpdateModules(updatedModules)
    toast({
      title: "Module Deleted",
      description: "Module has been removed from your curriculum"
    })
  }

  const duplicateModule = (module: LessonModule) => {
    const duplicatedModule: LessonModule = {
      ...module,
      id: Date.now().toString(),
      title: `${module.title} (Copy)`,
      order: modules.length + 1,
      status: 'draft'
    }
    onUpdateModules([...modules, duplicatedModule])
    toast({
      title: "Module Duplicated",
      description: "Module has been duplicated successfully"
    })
  }

  const toggleModuleExpanded = (moduleId: string) => {
    updateModule(moduleId, { isExpanded: !modules.find(m => m.id === moduleId)?.isExpanded })
  }

  const generateAIContent = async (moduleId: string) => {
    // Mock AI content generation
    const module = modules.find(m => m.id === moduleId)
    if (!module) return

    try {
      // Simulate AI generation
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const aiContent = {
        text: `AI-generated content for ${module.title}. This comprehensive lesson covers the fundamental concepts and provides practical examples to help students understand the material effectively.`,
        objectives: [
          `Understand the core concepts of ${module.title}`,
          `Apply learned principles in practical scenarios`,
          `Demonstrate mastery through exercises and assessments`
        ],
        exercises: [
          {
            id: Date.now().toString(),
            type: 'multiple_choice' as const,
            question: `What is the main focus of this ${module.title} lesson?`,
            options: ['Option A', 'Option B', 'Option C', 'Option D'],
            answer: 'Option A',
            explanation: 'This is the correct answer because...',
            points: 10
          }
        ]
      }

      updateModule(moduleId, {
        content: { ...module.content, ...aiContent },
        aiGenerated: true,
        status: 'complete'
      })

      toast({
        title: "AI Content Generated",
        description: "Content has been generated successfully"
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate AI content",
        variant: "destructive"
      })
    }
  }

  const getModuleIcon = (type: string) => {
    const moduleType = MODULE_TYPES.find(t => t.value === type)
    return moduleType?.icon || BookOpen
  }

  const getModuleColor = (type: string) => {
    const moduleType = MODULE_TYPES.find(t => t.value === type)
    return moduleType?.color || 'bg-gray-500'
  }

  const getTotalDuration = () => {
    return modules.reduce((total, module) => total + module.duration, 0)
  }

  const getModuleStats = () => {
    const total = modules.length
    const completed = modules.filter(m => m.status === 'complete').length
    const drafts = modules.filter(m => m.status === 'draft').length
    const reviews = modules.filter(m => m.status === 'review').length
    
    return { total, completed, drafts, reviews }
  }

  const stats = getModuleStats()

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Modules</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
              <BookOpen className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Completed</p>
                <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">In Review</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.reviews}</p>
              </div>
              <Eye className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Duration</p>
                <p className="text-2xl font-bold">{getTotalDuration()}m</p>
              </div>
              <Clock className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Course Curriculum</h2>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setShowAddModule(true)}
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Module
          </Button>
          <Button
            variant="outline"
            onClick={() => {
              // Generate AI curriculum outline
              toast({
                title: "AI Generation",
                description: "Generating curriculum outline with AI assistance"
              })
            }}
          >
            <Sparkles className="w-4 h-4 mr-2" />
            AI Outline
          </Button>
        </div>
      </div>

      {/* Curriculum List */}
      <DragDropContext onDragEnd={handleDragEnd}>
        <Droppable droppableId="curriculum">
          {(provided) => (
            <div {...provided.droppableProps} ref={provided.innerRef} className="space-y-4">
              {modules.map((module, index) => {
                const Icon = getModuleIcon(module.type)
                return (
                  <Draggable key={module.id} draggableId={module.id} index={index}>
                    {(provided, snapshot) => (
                      <Card
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        className={`transition-all ${
                          snapshot.isDragging ? 'shadow-lg' : ''
                        } ${selectedModule?.id === module.id ? 'ring-2 ring-primary' : ''}`}
                      >
                        <CardHeader className="pb-3">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div {...provided.dragHandleProps}>
                                <GripVertical className="h-4 w-4 text-muted-foreground cursor-grab" />
                              </div>
                              <div className={`p-2 rounded-lg ${getModuleColor(module.type)}`}>
                                <Icon className="h-4 w-4 text-white" />
                              </div>
                              <div>
                                <div className="flex items-center gap-2">
                                  <span className="text-sm font-medium">Module {index + 1}</span>
                                  <Badge variant="secondary" className="text-xs">
                                    {module.type}
                                  </Badge>
                                  <Badge 
                                    variant="secondary" 
                                    className={`text-xs text-white ${STATUS_COLORS[module.status]}`}
                                  >
                                    {module.status}
                                  </Badge>
                                  {module.aiGenerated && (
                                    <Badge variant="outline" className="text-xs">
                                      <Sparkles className="h-3 w-3 mr-1" />
                                      AI
                                    </Badge>
                                  )}
                                </div>
                                <h3 className="font-semibold">{module.title}</h3>
                                <p className="text-sm text-muted-foreground">{module.description}</p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <div className="text-right text-sm text-muted-foreground">
                                <div className="flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  <span>{module.duration}m</span>
                                </div>
                                {module.settings.isRequired && (
                                  <div className="flex items-center gap-1 text-red-500">
                                    <Target className="h-3 w-3" />
                                    <span>Required</span>
                                  </div>
                                )}
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => toggleModuleExpanded(module.id)}
                              >
                                {module.isExpanded ? (
                                  <ChevronUp className="h-4 w-4" />
                                ) : (
                                  <ChevronDown className="h-4 w-4" />
                                )}
                              </Button>
                            </div>
                          </div>
                        </CardHeader>

                        <Collapsible open={module.isExpanded}>
                          <CollapsibleContent>
                            <CardContent className="pt-0">
                              <Separator className="mb-4" />
                              
                              <div className="space-y-4">
                                {/* Module Content Preview */}
                                <div>
                                  <h4 className="font-medium mb-2">Content Preview</h4>
                                  <div className="bg-muted rounded-lg p-3 text-sm">
                                    {module.content.text ? (
                                      <p className="line-clamp-3">{module.content.text}</p>
                                    ) : (
                                      <p className="text-muted-foreground italic">No content yet</p>
                                    )}
                                  </div>
                                </div>

                                {/* Learning Objectives */}
                                {module.content.objectives && module.content.objectives.length > 0 && (
                                  <div>
                                    <h4 className="font-medium mb-2">Learning Objectives</h4>
                                    <ul className="space-y-1">
                                      {module.content.objectives.map((objective, i) => (
                                        <li key={i} className="text-sm flex items-center gap-2">
                                          <Target className="h-3 w-3 text-green-500" />
                                          {objective}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}

                                {/* Exercises */}
                                {module.content.exercises && module.content.exercises.length > 0 && (
                                  <div>
                                    <h4 className="font-medium mb-2">Exercises</h4>
                                    <div className="space-y-2">
                                      {module.content.exercises.map((exercise, i) => (
                                        <div key={i} className="bg-muted rounded-lg p-3">
                                          <div className="flex items-center justify-between">
                                            <p className="text-sm font-medium">{exercise.question}</p>
                                            <Badge variant="secondary" className="text-xs">
                                              {exercise.points} pts
                                            </Badge>
                                          </div>
                                          <p className="text-xs text-muted-foreground mt-1">
                                            Type: {exercise.type}
                                          </p>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Actions */}
                                <div className="flex items-center justify-between pt-2">
                                  <div className="flex gap-2">
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      onClick={() => onSelectModule(module)}
                                    >
                                      <Edit3 className="h-3 w-3 mr-2" />
                                      Edit
                                    </Button>
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      onClick={() => duplicateModule(module)}
                                    >
                                      <Copy className="h-3 w-3 mr-2" />
                                      Duplicate
                                    </Button>
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      onClick={() => generateAIContent(module.id)}
                                    >
                                      <Sparkles className="h-3 w-3 mr-2" />
                                      Generate AI Content
                                    </Button>
                                  </div>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => deleteModule(module.id)}
                                  >
                                    <Trash2 className="h-3 w-3 text-red-500" />
                                  </Button>
                                </div>
                              </div>
                            </CardContent>
                          </CollapsibleContent>
                        </Collapsible>
                      </Card>
                    )}
                  </Draggable>
                )
              })}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>

      {/* Empty State */}
      {modules.length === 0 && (
        <Card className="p-8 text-center">
          <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">No modules yet</h3>
          <p className="text-muted-foreground mb-4">
            Start building your curriculum by adding your first module
          </p>
          <Button onClick={() => setShowAddModule(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Your First Module
          </Button>
        </Card>
      )}

      {/* Add Module Dialog */}
      <Dialog open={showAddModule} onOpenChange={setShowAddModule}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Add New Module</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="module-title">Module Title</Label>
              <Input
                id="module-title"
                placeholder="Enter module title"
                value={newModule.title}
                onChange={(e) => setNewModule(prev => ({ ...prev, title: e.target.value }))}
              />
            </div>
            
            <div>
              <Label htmlFor="module-description">Description</Label>
              <Textarea
                id="module-description"
                placeholder="Describe what this module covers"
                value={newModule.description}
                onChange={(e) => setNewModule(prev => ({ ...prev, description: e.target.value }))}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="module-type">Module Type</Label>
                <Select 
                  value={newModule.type} 
                  onValueChange={(value) => setNewModule(prev => ({ ...prev, type: value as any }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {MODULE_TYPES.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        <div className="flex items-center gap-2">
                          <type.icon className="h-4 w-4" />
                          {type.label}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="module-duration">Duration (minutes)</Label>
                <Input
                  id="module-duration"
                  type="number"
                  value={newModule.duration}
                  onChange={(e) => setNewModule(prev => ({ ...prev, duration: parseInt(e.target.value) }))}
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2">
              <Button variant="outline" onClick={() => setShowAddModule(false)}>
                Cancel
              </Button>
              <Button onClick={addModule} disabled={!newModule.title}>
                Add Module
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}