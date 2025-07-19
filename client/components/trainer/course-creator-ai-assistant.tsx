"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Bot,
  Send,
  Sparkles,
  BookOpen,
  Users,
  Target,
  Clock,
  CheckCircle,
  Lightbulb,
  Zap,
  MessageSquare,
  Loader2,
  ThumbsUp,
  ThumbsDown,
  Copy,
  RefreshCw
} from "lucide-react"
import { toast } from "@/components/ui/use-toast"

interface CourseCreatorAIAssistantProps {
  course: {
    title: string
    description: string
    level: string
    category: string
    objectives: string[]
    curriculum: any[]
  }
  onSuggestionApply: (suggestion: AISuggestion) => void
}

interface AISuggestion {
  id: string
  type: 'content' | 'structure' | 'assessment' | 'improvement'
  title: string
  description: string
  content: string
  confidence: number
  category: string
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  suggestions?: AISuggestion[]
}

export function CourseCreatorAIAssistant({ course, onSuggestionApply }: CourseCreatorAIAssistantProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [activeSuggestions, setActiveSuggestions] = useState<AISuggestion[]>([])

  // Initialize with welcome message
  useEffect(() => {
    const welcomeMessage: ChatMessage = {
      id: "welcome",
      role: "assistant",
      content: `Hello! I'm your AI Course Assistant. I can help you create engaging content, suggest improvements, and optimize your course structure. What would you like to work on today?`,
      timestamp: new Date(),
      suggestions: generateInitialSuggestions()
    }
    setMessages([welcomeMessage])
    setActiveSuggestions(generateInitialSuggestions())
  }, [])

  const generateInitialSuggestions = (): AISuggestion[] => {
    const suggestions: AISuggestion[] = []

    // Content suggestions based on course data
    if (course.title && course.description) {
      suggestions.push({
        id: "content-outline",
        type: "structure",
        title: "Generate Course Outline",
        description: "Create a detailed course outline based on your title and description",
        content: `Based on "${course.title}", I can create a comprehensive outline with modules, lessons, and key topics.`,
        confidence: 0.9,
        category: "structure"
      })
    }

    if (course.objectives.length > 0) {
      suggestions.push({
        id: "assessment-plan",
        type: "assessment",
        title: "Create Assessment Plan",
        description: "Generate assessments aligned with your learning objectives",
        content: "I'll create quizzes, assignments, and projects that measure achievement of your learning objectives.",
        confidence: 0.85,
        category: "assessment"
      })
    }

    if (course.curriculum.length === 0) {
      suggestions.push({
        id: "first-lesson",
        type: "content",
        title: "Create First Lesson",
        description: "Generate engaging content for your first lesson",
        content: "Let me help you create a compelling first lesson that hooks your students and sets clear expectations.",
        confidence: 0.8,
        category: "content"
      })
    }

    return suggestions
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage("")
    setIsLoading(true)

    try {
      // Simulate AI response
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const aiResponse = generateAIResponse(inputMessage)
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: aiResponse.content,
        timestamp: new Date(),
        suggestions: aiResponse.suggestions
      }

      setMessages(prev => [...prev, assistantMessage])
      setActiveSuggestions(aiResponse.suggestions)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to get AI response",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const generateAIResponse = (userInput: string): { content: string; suggestions: AISuggestion[] } => {
    const input = userInput.toLowerCase()
    
    // Content generation requests
    if (input.includes("content") || input.includes("lesson") || input.includes("material")) {
      return {
        content: "I can help you create engaging lesson content! Based on your course structure, I can generate interactive materials, examples, and activities that align with your learning objectives.",
        suggestions: [
          {
            id: "lesson-content",
            type: "content",
            title: "Generate Lesson Content",
            description: "Create comprehensive lesson materials with examples",
            content: "I'll create detailed lesson content including introduction, main concepts, examples, and summary for your specified topic.",
            confidence: 0.9,
            category: "content"
          },
          {
            id: "interactive-activities",
            type: "content",
            title: "Add Interactive Activities",
            description: "Create hands-on exercises and activities",
            content: "Let me design interactive activities that reinforce learning and keep students engaged.",
            confidence: 0.85,
            category: "content"
          }
        ]
      }
    }

    // Assessment requests
    if (input.includes("quiz") || input.includes("test") || input.includes("assessment")) {
      return {
        content: "I can create various types of assessments to measure student progress! I'll design questions that align with your learning objectives and provide immediate feedback.",
        suggestions: [
          {
            id: "quiz-generator",
            type: "assessment",
            title: "Generate Quiz Questions",
            description: "Create multiple-choice and short-answer questions",
            content: "I'll generate a variety of quiz questions at different difficulty levels to test student understanding.",
            confidence: 0.9,
            category: "assessment"
          },
          {
            id: "project-assignment",
            type: "assessment",
            title: "Design Project Assignment",
            description: "Create practical project assignments",
            content: "Let me design a project assignment that allows students to apply their knowledge in a real-world context.",
            confidence: 0.8,
            category: "assessment"
          }
        ]
      }
    }

    // Improvement suggestions
    if (input.includes("improve") || input.includes("better") || input.includes("enhance")) {
      return {
        content: "I can analyze your course and suggest improvements! I'll review your content structure, engagement levels, and learning outcomes to recommend enhancements.",
        suggestions: [
          {
            id: "engagement-boost",
            type: "improvement",
            title: "Boost Student Engagement",
            description: "Add interactive elements and gamification",
            content: "I'll suggest ways to make your course more engaging through interactive elements, gamification, and multimedia.",
            confidence: 0.85,
            category: "improvement"
          },
          {
            id: "accessibility-check",
            type: "improvement",
            title: "Improve Accessibility",
            description: "Make your course accessible to all learners",
            content: "Let me review your course for accessibility improvements and suggest inclusive design elements.",
            confidence: 0.8,
            category: "improvement"
          }
        ]
      }
    }

    // Default response
    return {
      content: "I'm here to help with your course creation! I can assist with content generation, assessment design, course structure optimization, and engagement improvements. What specific area would you like to focus on?",
      suggestions: [
        {
          id: "general-help",
          type: "content",
          title: "Course Structure Review",
          description: "Analyze and improve your course structure",
          content: "I'll review your course structure and suggest improvements for better learning flow and outcomes.",
          confidence: 0.8,
          category: "structure"
        }
      ]
    }
  }

  const handleApplySuggestion = (suggestion: AISuggestion) => {
    onSuggestionApply(suggestion)
    toast({
      title: "Applied",
      description: `Applied suggestion: ${suggestion.title}`,
    })
  }

  const handleRegenerateResponse = async (messageId: string) => {
    const messageIndex = messages.findIndex(m => m.id === messageId)
    if (messageIndex === -1) return

    setIsLoading(true)
    try {
      // Simulate regeneration
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const newResponse = generateAIResponse("regenerate")
      const updatedMessages = [...messages]
      updatedMessages[messageIndex] = {
        ...updatedMessages[messageIndex],
        content: newResponse.content,
        suggestions: newResponse.suggestions
      }
      
      setMessages(updatedMessages)
      setActiveSuggestions(newResponse.suggestions)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to regenerate response",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
      {/* Chat Interface */}
      <div className="lg:col-span-2 flex flex-col">
        <Card className="flex-1 flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              AI Course Assistant
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col">
            <ScrollArea className="flex-1 pr-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-3 ${
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted'
                      }`}
                    >
                      <div className="flex items-start gap-2">
                        {message.role === 'assistant' && (
                          <Bot className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        )}
                        <div className="flex-1">
                          <p className="text-sm">{message.content}</p>
                          {message.role === 'assistant' && (
                            <div className="flex items-center gap-2 mt-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleRegenerateResponse(message.id)}
                              >
                                <RefreshCw className="h-3 w-3" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => navigator.clipboard.writeText(message.content)}
                              >
                                <Copy className="h-3 w-3" />
                              </Button>
                              <Button variant="ghost" size="sm">
                                <ThumbsUp className="h-3 w-3" />
                              </Button>
                              <Button variant="ghost" size="sm">
                                <ThumbsDown className="h-3 w-3" />
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-muted rounded-lg p-3 max-w-[80%]">
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-sm">AI is thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>
            
            <div className="mt-4 flex gap-2">
              <Input
                placeholder="Ask me anything about your course..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                disabled={isLoading}
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Suggestions Panel */}
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              AI Suggestions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {activeSuggestions.map((suggestion) => (
                <div key={suggestion.id} className="border rounded-lg p-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-sm">{suggestion.title}</h4>
                        <Badge variant="secondary" className="text-xs">
                          {Math.round(suggestion.confidence * 100)}%
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mb-2">
                        {suggestion.description}
                      </p>
                      <p className="text-xs">{suggestion.content}</p>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    className="w-full mt-2"
                    onClick={() => handleApplySuggestion(suggestion)}
                  >
                    Apply Suggestion
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => setInputMessage("Generate content for my next lesson")}
              >
                <BookOpen className="h-4 w-4 mr-2" />
                Generate Lesson Content
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => setInputMessage("Create assessment questions")}
              >
                <Target className="h-4 w-4 mr-2" />
                Create Assessment
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => setInputMessage("Improve student engagement")}
              >
                <Users className="h-4 w-4 mr-2" />
                Boost Engagement
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => setInputMessage("Review my course structure")}
              >
                <CheckCircle className="h-4 w-4 mr-2" />
                Review Structure
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}