"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"
import { 
  Save, 
  Bot, 
  Plus, 
  Trash2, 
  Edit3, 
  Eye, 
  Play, 
  Upload,
  FileText,
  Video,
  Image,
  Link as LinkIcon,
  ChevronDown,
  ChevronUp,
  GripVertical,
  Sparkles,
  BookOpen,
  Users,
  Clock,
  Target,
  CheckCircle,
  AlertCircle,
  Loader2,
  MessageSquare,
  Settings,
  Download,
  Share2
} from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { toast } from "@/components/ui/use-toast"
import { useRouter } from "next/navigation"
import { courseManagerService } from "@/lib/api-services"
// import { CourseCreatorAIAssistant } from "@/components/trainer/course-creator-ai-assistant"
// import { CurriculumBuilder } from "@/components/trainer/curriculum-builder"
// import { ContentEditor } from "@/components/trainer/content-editor"
// import { AssessmentDesigner } from "@/components/trainer/assessment-designer"

interface CourseData {
  id?: string
  title: string
  description: string
  level: string
  duration: string
  objectives: string[]
  prerequisites: string[]
  category: string
  tags: string[]
  status: 'draft' | 'published' | 'archived'
  curriculum: LessonModule[]
  settings: {
    allowAIAssistance: boolean
    enableCollaboration: boolean
    autoSave: boolean
    previewMode: boolean
  }
}

interface LessonModule {
  id: string
  title: string
  description: string
  type: 'lesson' | 'assessment' | 'activity'
  duration: number
  order: number
  content: {
    text?: string
    media?: MediaItem[]
    exercises?: Exercise[]
  }
  aiGenerated: boolean
  status: 'draft' | 'complete' | 'review'
}

interface MediaItem {
  id: string
  type: 'image' | 'video' | 'audio' | 'document'
  url: string
  name: string
  description?: string
}

interface Exercise {
  id: string
  type: 'multiple_choice' | 'essay' | 'fill_blank' | 'matching'
  question: string
  options?: string[]
  answer: string
  explanation?: string
}

export default function CourseCreator() {
  const router = useRouter()
  const [course, setCourse] = useState<CourseData>({
    title: "",
    description: "",
    level: "beginner",
    duration: "",
    objectives: [],
    prerequisites: [],
    category: "",
    tags: [],
    status: "draft",
    curriculum: [],
    settings: {
      allowAIAssistance: true,
      enableCollaboration: false,
      autoSave: true,
      previewMode: false
    }
  })
  
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [aiAssistantOpen, setAiAssistantOpen] = useState(false)
  const [selectedModule, setSelectedModule] = useState<LessonModule | null>(null)
  const [activeTab, setActiveTab] = useState("overview")

  // Auto-save functionality
  useEffect(() => {
    if (course.settings.autoSave && course.title) {
      const timer = setTimeout(() => {
        handleSave(true) // Silent save
      }, 5000)
      return () => clearTimeout(timer)
    }
  }, [course])

  const handleSave = async (silent = false) => {
    setIsSaving(true)
    try {
      // Here you would call your API to save the course
      await new Promise(resolve => setTimeout(resolve, 1000)) // Mock save
      
      if (!silent) {
        toast({
          title: "Success",
          description: "Course saved successfully"
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save course",
        variant: "destructive"
      })
    } finally {
      setIsSaving(false)
    }
  }

  const handlePublish = async () => {
    setIsLoading(true)
    try {
      // Validation
      if (!course.title || !course.description || course.curriculum.length === 0) {
        toast({
          title: "Validation Error",
          description: "Please complete all required fields and add at least one lesson",
          variant: "destructive"
        })
        return
      }

      // Here you would call your API to publish the course
      await new Promise(resolve => setTimeout(resolve, 2000)) // Mock publish
      
      setCourse(prev => ({ ...prev, status: 'published' }))
      toast({
        title: "Success",
        description: "Course published successfully!"
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to publish course",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const addObjective = () => {
    setCourse(prev => ({
      ...prev,
      objectives: [...prev.objectives, ""]
    }))
  }

  const updateObjective = (index: number, value: string) => {
    setCourse(prev => ({
      ...prev,
      objectives: prev.objectives.map((obj, i) => i === index ? value : obj)
    }))
  }

  const removeObjective = (index: number) => {
    setCourse(prev => ({
      ...prev,
      objectives: prev.objectives.filter((_, i) => i !== index)
    }))
  }

  const addNewModule = () => {
    const newModule: LessonModule = {
      id: Date.now().toString(),
      title: "New Lesson",
      description: "",
      type: "lesson",
      duration: 30,
      order: course.curriculum.length + 1,
      content: {},
      aiGenerated: false,
      status: "draft"
    }
    setCourse(prev => ({
      ...prev,
      curriculum: [...prev.curriculum, newModule]
    }))
  }

  const updateModule = (moduleId: string, updates: Partial<LessonModule>) => {
    setCourse(prev => ({
      ...prev,
      curriculum: prev.curriculum.map(module => 
        module.id === moduleId ? { ...module, ...updates } : module
      )
    }))
  }

  const deleteModule = (moduleId: string) => {
    setCourse(prev => ({
      ...prev,
      curriculum: prev.curriculum.filter(module => module.id !== moduleId)
    }))
  }

  const generateAIContent = async (moduleId: string) => {
    const module = course.curriculum.find(m => m.id === moduleId)
    if (!module) return

    try {
      // Here you would call your AI content generation API
      await new Promise(resolve => setTimeout(resolve, 2000)) // Mock AI generation
      
      updateModule(moduleId, {
        content: {
          text: `AI-generated content for ${module.title}. This is a comprehensive lesson covering the key concepts...`,
          exercises: [
            {
              id: Date.now().toString(),
              type: "multiple_choice",
              question: "What is the main concept covered in this lesson?",
              options: ["Option A", "Option B", "Option C", "Option D"],
              answer: "Option A",
              explanation: "This is the correct answer because..."
            }
          ]
        },
        aiGenerated: true,
        status: "complete"
      })

      toast({
        title: "Success",
        description: "AI content generated successfully!"
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate AI content",
        variant: "destructive"
      })
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Course Creator</h1>
          <p className="text-muted-foreground">
            Create engaging courses with AI assistance
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={course.status === 'published' ? 'default' : 'secondary'}>
            {course.status}
          </Badge>
          <Button 
            variant="outline" 
            onClick={() => setAiAssistantOpen(true)}
            disabled={!course.settings.allowAIAssistance}
          >
            <Bot className="w-4 h-4 mr-2" />
            AI Assistant
          </Button>
          <Button 
            variant="outline" 
            onClick={() => handleSave()}
            disabled={isSaving}
          >
            {isSaving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
            Save
          </Button>
          <Button onClick={handlePublish} disabled={isLoading}>
            {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Share2 className="w-4 h-4 mr-2" />}
            Publish
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="curriculum">Curriculum</TabsTrigger>
          <TabsTrigger value="content">Content</TabsTrigger>
          <TabsTrigger value="assessments">Assessments</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Basic Information */}
            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="title">Course Title</Label>
                  <Input
                    id="title"
                    placeholder="Enter course title"
                    value={course.title}
                    onChange={(e) => setCourse(prev => ({ ...prev, title: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    placeholder="Describe your course"
                    value={course.description}
                    onChange={(e) => setCourse(prev => ({ ...prev, description: e.target.value }))}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="level">Level</Label>
                    <Select value={course.level} onValueChange={(value) => setCourse(prev => ({ ...prev, level: value }))}>
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
                    <Label htmlFor="duration">Duration</Label>
                    <Input
                      id="duration"
                      placeholder="e.g., 4 weeks"
                      value={course.duration}
                      onChange={(e) => setCourse(prev => ({ ...prev, duration: e.target.value }))}
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="category">Category</Label>
                  <Select value={course.category} onValueChange={(value) => setCourse(prev => ({ ...prev, category: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="technology">Technology</SelectItem>
                      <SelectItem value="business">Business</SelectItem>
                      <SelectItem value="language">Language</SelectItem>
                      <SelectItem value="creative">Creative</SelectItem>
                      <SelectItem value="science">Science</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Learning Objectives */}
            <Card>
              <CardHeader>
                <CardTitle>Learning Objectives</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {course.objectives.map((objective, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <Input
                      placeholder="Enter learning objective"
                      value={objective}
                      onChange={(e) => updateObjective(index, e.target.value)}
                    />
                    <Button 
                      variant="outline" 
                      size="icon"
                      onClick={() => removeObjective(index)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
                <Button variant="outline" onClick={addObjective}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Objective
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="curriculum" className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Course Curriculum</h2>
            <Button onClick={addNewModule}>
              <Plus className="w-4 h-4 mr-2" />
              Add Lesson
            </Button>
          </div>

          <div className="space-y-4">
            {course.curriculum.map((module, index) => (
              <Card key={module.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        <GripVertical className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm font-medium">Lesson {index + 1}</span>
                      </div>
                      <Badge variant={module.aiGenerated ? 'default' : 'secondary'}>
                        {module.aiGenerated ? 'AI Generated' : 'Manual'}
                      </Badge>
                      <Badge variant={module.status === 'complete' ? 'default' : 'secondary'}>
                        {module.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => generateAIContent(module.id)}
                      >
                        <Sparkles className="w-4 h-4 mr-2" />
                        Generate AI Content
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedModule(module)}
                      >
                        <Edit3 className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => deleteModule(module.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <Input
                      placeholder="Lesson title"
                      value={module.title}
                      onChange={(e) => updateModule(module.id, { title: e.target.value })}
                    />
                    <Textarea
                      placeholder="Lesson description"
                      value={module.description}
                      onChange={(e) => updateModule(module.id, { description: e.target.value })}
                    />
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 w-3" />
                        <span>{module.duration} minutes</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <FileText className="w-3 w-3" />
                        <span>{module.type}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {course.curriculum.length === 0 && (
            <Card className="p-8 text-center">
              <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No lessons yet</h3>
              <p className="text-muted-foreground mb-4">
                Start building your course curriculum by adding lessons
              </p>
              <Button onClick={addNewModule}>
                <Plus className="w-4 h-4 mr-2" />
                Add Your First Lesson
              </Button>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="content" className="space-y-6">
          {/* <ContentEditor 
            modules={course.curriculum}
            onUpdateModule={updateModule}
            selectedModule={selectedModule}
            onSelectModule={setSelectedModule}
          /> */}
          <div className="p-4 border rounded-lg">
            <p className="text-muted-foreground">Content Editor component will be implemented here</p>
          </div>
        </TabsContent>

        <TabsContent value="assessments" className="space-y-6">
          {/* <AssessmentDesigner 
            modules={course.curriculum}
            onUpdateModule={updateModule}
          /> */}
          <div className="p-4 border rounded-lg">
            <p className="text-muted-foreground">Assessment Designer component will be implemented here</p>
          </div>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Course Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="ai-assistance">AI Assistance</Label>
                  <p className="text-sm text-muted-foreground">
                    Enable AI-powered content generation and suggestions
                  </p>
                </div>
                <Switch
                  id="ai-assistance"
                  checked={course.settings.allowAIAssistance}
                  onCheckedChange={(checked) => 
                    setCourse(prev => ({
                      ...prev,
                      settings: { ...prev.settings, allowAIAssistance: checked }
                    }))
                  }
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="collaboration">Collaboration</Label>
                  <p className="text-sm text-muted-foreground">
                    Allow other trainers to collaborate on this course
                  </p>
                </div>
                <Switch
                  id="collaboration"
                  checked={course.settings.enableCollaboration}
                  onCheckedChange={(checked) => 
                    setCourse(prev => ({
                      ...prev,
                      settings: { ...prev.settings, enableCollaboration: checked }
                    }))
                  }
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="auto-save">Auto Save</Label>
                  <p className="text-sm text-muted-foreground">
                    Automatically save changes every 5 seconds
                  </p>
                </div>
                <Switch
                  id="auto-save"
                  checked={course.settings.autoSave}
                  onCheckedChange={(checked) => 
                    setCourse(prev => ({
                      ...prev,
                      settings: { ...prev.settings, autoSave: checked }
                    }))
                  }
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* AI Assistant Dialog */}
      <Dialog open={aiAssistantOpen} onOpenChange={setAiAssistantOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>AI Course Assistant</DialogTitle>
          </DialogHeader>
          {/* <CourseCreatorAIAssistant 
            course={course}
            onSuggestionApply={(suggestion) => {
              // Apply AI suggestion to course
              toast({
                title: "Applied",
                description: "AI suggestion applied to your course"
              })
            }}
          /> */}
          <div className="p-4 border rounded-lg">
            <p className="text-muted-foreground">AI Assistant component will be implemented here</p>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}