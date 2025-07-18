"use client"

import React, { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useToast } from "@/components/ui/use-toast"
import { Loader2, Send, Bot, User, BookOpen, Target, Lightbulb, MessageCircle, ThumbsUp, ThumbsDown, Copy, RotateCcw, Volume2 } from "lucide-react"

interface ChatMessage {
  id: string
  content: string
  sender: 'user' | 'ai'
  timestamp: Date
  type?: 'text' | 'exercise' | 'assessment' | 'feedback'
  metadata?: {
    exercise?: ExerciseData
    assessment?: AssessmentData
    feedback?: FeedbackData
  }
}

interface ExerciseData {
  id: string
  title: string
  instructions: string
  type: 'multiple-choice' | 'fill-blank' | 'speaking' | 'writing'
  options?: string[]
  correctAnswer?: string
  userAnswer?: string
  isCorrect?: boolean
}

interface AssessmentData {
  id: string
  title: string
  questions: ExerciseData[]
  score?: number
  totalScore?: number
  feedback?: string
}

interface FeedbackData {
  level: 'beginner' | 'intermediate' | 'advanced'
  strengths: string[]
  improvements: string[]
  suggestions: string[]
}

interface LearningContext {
  courseId?: string
  lessonId?: string
  studentLevel?: string
  focusAreas?: string[]
  learningGoals?: string[]
}

interface AIChatInterfaceProps {
  context?: LearningContext
  onExerciseComplete?: (exercise: ExerciseData) => void
  onAssessmentComplete?: (assessment: AssessmentData) => void
  className?: string
}

const AIChatInterface: React.FC<AIChatInterfaceProps> = ({
  context,
  onExerciseComplete,
  onAssessmentComplete,
  className = ""
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const { toast } = useToast()

  // Initialize chat with welcome message
  useEffect(() => {
    const welcomeMessage: ChatMessage = {
      id: 'welcome',
      content: `Hello! I'm your AI learning assistant. I'm here to help you learn and practice. ${context?.courseId ? `We're working on ${context.courseId}.` : ''} How can I help you today?`,
      sender: 'ai',
      timestamp: new Date(),
      type: 'text'
    }
    setMessages([welcomeMessage])
  }, [context])

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: input,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    }

    setMessages(prev => [...prev, userMessage])
    setInput("")
    setIsLoading(true)
    setIsTyping(true)

    try {
      // Simulate AI response (replace with actual API call)
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const aiResponse = await generateAIResponse(input, context)
      
      setMessages(prev => [...prev, aiResponse])
      
      // Handle special message types
      if (aiResponse.type === 'exercise' && aiResponse.metadata?.exercise) {
        onExerciseComplete?.(aiResponse.metadata.exercise)
      } else if (aiResponse.type === 'assessment' && aiResponse.metadata?.assessment) {
        onAssessmentComplete?.(aiResponse.metadata.assessment)
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to get AI response. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
      setIsTyping(false)
    }
  }

  const generateAIResponse = async (userInput: string, context?: LearningContext): Promise<ChatMessage> => {
    // This is a mock implementation - replace with actual AI API call
    const responses = [
      "Great question! Let me help you understand this concept better.",
      "That's a good point. Let me provide some examples to illustrate this.",
      "I can see you're working on this topic. Here's a practice exercise for you.",
      "Let me create a quick assessment to check your understanding.",
    ]

    const randomResponse = responses[Math.floor(Math.random() * responses.length)]
    
    // Sometimes generate an exercise
    if (Math.random() > 0.7) {
      return {
        id: Date.now().toString(),
        content: "Here's a practice exercise for you:",
        sender: 'ai',
        timestamp: new Date(),
        type: 'exercise',
        metadata: {
          exercise: {
            id: Date.now().toString(),
            title: "Practice Exercise",
            instructions: "Choose the correct answer:",
            type: 'multiple-choice',
            options: ["Option A", "Option B", "Option C", "Option D"],
            correctAnswer: "Option A"
          }
        }
      }
    }

    return {
      id: Date.now().toString(),
      content: randomResponse,
      sender: 'ai',
      timestamp: new Date(),
      type: 'text'
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleExerciseAnswer = (exerciseId: string, answer: string) => {
    // Handle exercise answer submission
    setMessages(prev => prev.map(msg => {
      if (msg.id === exerciseId && msg.metadata?.exercise) {
        return {
          ...msg,
          metadata: {
            ...msg.metadata,
            exercise: {
              ...msg.metadata.exercise,
              userAnswer: answer,
              isCorrect: answer === msg.metadata.exercise.correctAnswer
            }
          }
        }
      }
      return msg
    }))

    // Add feedback message
    const feedbackMessage: ChatMessage = {
      id: Date.now().toString(),
      content: answer === "Option A" ? "Correct! Well done!" : "That's not quite right. The correct answer is Option A.",
      sender: 'ai',
      timestamp: new Date(),
      type: 'feedback'
    }
    setMessages(prev => [...prev, feedbackMessage])
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: "Copied!",
      description: "Message copied to clipboard",
    })
  }

  const regenerateResponse = (messageId: string) => {
    // Implement regenerate functionality
    toast({
      title: "Regenerating...",
      description: "Generating a new response",
    })
  }

  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      speechSynthesis.speak(utterance)
    }
  }

  return (
    <TooltipProvider>
      <Card className={`flex flex-col h-full ${className}`}>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-blue-600" />
            AI Learning Assistant
            {context?.courseId && (
              <Badge variant="secondary" className="ml-2">
                {context.courseId}
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        
        <CardContent className="flex-1 flex flex-col p-0">
          <ScrollArea 
            ref={scrollAreaRef}
            className="flex-1 p-4 max-h-[500px]"
          >
            <div className="space-y-4">
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] ${message.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'} rounded-lg p-3`}>
                    <div className="flex items-start gap-2">
                      {message.sender === 'ai' ? (
                        <Bot className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      ) : (
                        <User className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      )}
                      <div className="flex-1">
                        <p className="text-sm">{message.content}</p>
                        
                        {/* Render exercise */}
                        {message.type === 'exercise' && message.metadata?.exercise && (
                          <div className="mt-3 p-3 bg-white rounded border">
                            <h4 className="font-medium text-gray-900 mb-2">
                              {message.metadata.exercise.title}
                            </h4>
                            <p className="text-sm text-gray-600 mb-3">
                              {message.metadata.exercise.instructions}
                            </p>
                            
                            {message.metadata.exercise.type === 'multiple-choice' && (
                              <div className="space-y-2">
                                {message.metadata.exercise.options?.map((option, index) => (
                                  <Button
                                    key={index}
                                    variant={message.metadata?.exercise?.userAnswer === option ? "default" : "outline"}
                                    size="sm"
                                    className="w-full justify-start"
                                    onClick={() => handleExerciseAnswer(message.id, option)}
                                    disabled={!!message.metadata?.exercise?.userAnswer}
                                  >
                                    {option}
                                  </Button>
                                ))}
                              </div>
                            )}
                            
                            {message.metadata.exercise.userAnswer && (
                              <div className={`mt-3 p-2 rounded ${message.metadata.exercise.isCorrect ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                <p className="text-sm font-medium">
                                  {message.metadata.exercise.isCorrect ? '✓ Correct!' : '✗ Incorrect'}
                                </p>
                              </div>
                            )}
                          </div>
                        )}
                        
                        <div className="flex items-center gap-2 mt-2">
                          <span className="text-xs opacity-70">
                            {message.timestamp.toLocaleTimeString()}
                          </span>
                          
                          {message.sender === 'ai' && (
                            <div className="flex items-center gap-1">
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-6 w-6 opacity-50 hover:opacity-100"
                                    onClick={() => copyToClipboard(message.content)}
                                  >
                                    <Copy className="w-3 h-3" />
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent>Copy message</TooltipContent>
                              </Tooltip>
                              
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-6 w-6 opacity-50 hover:opacity-100"
                                    onClick={() => speakText(message.content)}
                                  >
                                    <Volume2 className="w-3 h-3" />
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent>Speak message</TooltipContent>
                              </Tooltip>
                              
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-6 w-6 opacity-50 hover:opacity-100"
                                    onClick={() => regenerateResponse(message.id)}
                                  >
                                    <RotateCcw className="w-3 h-3" />
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent>Regenerate response</TooltipContent>
                              </Tooltip>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-900 rounded-lg p-3">
                    <div className="flex items-center gap-2">
                      <Bot className="w-4 h-4" />
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
          
          <Separator />
          
          <div className="p-4">
            <div className="flex gap-2">
              <Input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about the lesson..."
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                onClick={handleSendMessage}
                disabled={!input.trim() || isLoading}
                size="icon"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
            
            {/* Quick action buttons */}
            <div className="flex gap-2 mt-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setInput("Can you give me a practice exercise?")}
              >
                <Target className="w-4 h-4 mr-1" />
                Practice
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setInput("Can you explain this concept?")}
              >
                <Lightbulb className="w-4 h-4 mr-1" />
                Explain
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setInput("How am I doing with this lesson?")}
              >
                <BookOpen className="w-4 h-4 mr-1" />
                Progress
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </TooltipProvider>
  )
}

export default AIChatInterface