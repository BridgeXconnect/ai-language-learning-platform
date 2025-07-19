"use client"

import { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import { 
  Send, 
  Bot, 
  User, 
  Loader2, 
  MessageSquare,
  Sparkles,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Minimize2,
  Maximize2,
  X,
  Settings,
  BookOpen,
  Lightbulb,
  Target,
  Code,
  FileText,
  CheckCircle,
  AlertCircle
} from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { toast } from "@/components/ui/use-toast"

export interface ChatMessage {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  context?: any
  suggestions?: string[]
  actions?: ChatAction[]
}

export interface ChatAction {
  id: string
  label: string
  type: 'apply' | 'copy' | 'regenerate' | 'expand'
  data?: any
}

export interface AIChatInterfaceProps {
  variant?: 'compact' | 'expanded' | 'overlay' | 'sidebar'
  context?: 'course-creation' | 'student-learning' | 'assessment' | 'general'
  contextData?: any
  onSuggestionApply?: (suggestion: any) => void
  onClose?: () => void
  className?: string
}

export function AIChatInterface({ 
  variant = 'expanded',
  context = 'general',
  contextData,
  onSuggestionApply,
  onClose,
  className = ""
}: AIChatInterfaceProps) {
  const { user } = useAuth()
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'system',
      content: `Hi ${user?.first_name || 'there'}! I'm your AI assistant. I can help you with ${getContextDescription(context)}.`,
      timestamp: new Date(),
      suggestions: getInitialSuggestions(context)
    }
  ])
  const [inputMessage, setInputMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage("")
    setIsLoading(true)

    try {
      // Mock AI response - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const aiResponse = await generateAIResponse(inputMessage, context, contextData)
      
      setMessages(prev => [...prev, aiResponse])
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to get AI response. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion)
    inputRef.current?.focus()
  }

  const handleActionClick = (action: ChatAction) => {
    switch (action.type) {
      case 'apply':
        onSuggestionApply?.(action.data)
        toast({
          title: "Applied",
          description: "AI suggestion has been applied to your work."
        })
        break
      case 'copy':
        navigator.clipboard.writeText(action.data)
        toast({
          title: "Copied",
          description: "Content copied to clipboard."
        })
        break
      case 'regenerate':
        // Regenerate the response
        break
      case 'expand':
        // Expand the response
        break
    }
  }

  const getContainerClasses = () => {
    const base = "flex flex-col bg-background border rounded-lg"
    
    switch (variant) {
      case 'compact':
        return `${base} h-80 w-80`
      case 'expanded':
        return `${base} h-96 w-full max-w-4xl`
      case 'overlay':
        return `${base} fixed bottom-4 right-4 h-96 w-80 z-50 shadow-lg`
      case 'sidebar':
        return `${base} h-full w-80`
      default:
        return base
    }
  }

  if (isMinimized && variant === 'overlay') {
    return (
      <Button
        className="fixed bottom-4 right-4 z-50 h-12 w-12 rounded-full shadow-lg"
        onClick={() => setIsMinimized(false)}
      >
        <MessageSquare className="h-6 w-6" />
      </Button>
    )
  }

  return (
    <div className={`${getContainerClasses()} ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-2">
          <Avatar className="h-8 w-8">
            <AvatarFallback>
              <Bot className="h-4 w-4" />
            </AvatarFallback>
          </Avatar>
          <div>
            <h3 className="font-semibold">AI Assistant</h3>
            <p className="text-xs text-muted-foreground">
              {getContextDescription(context)}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {variant === 'overlay' && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMinimized(true)}
            >
              <Minimize2 className="h-4 w-4" />
            </Button>
          )}
          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Messages */}
      <ScrollArea ref={scrollAreaRef} className="flex-1 p-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              {message.type !== 'user' && (
                <Avatar className="h-8 w-8">
                  <AvatarFallback>
                    <Bot className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
              )}
              
              <div className={`max-w-[80%] ${message.type === 'user' ? 'order-1' : ''}`}>
                <div className={`p-3 rounded-lg ${
                  message.type === 'user' 
                    ? 'bg-primary text-primary-foreground ml-auto' 
                    : message.type === 'system'
                    ? 'bg-muted'
                    : 'bg-muted'
                }`}>
                  <p className="text-sm">{message.content}</p>
                </div>
                
                {/* Suggestions */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="mt-2 space-y-2">
                    <p className="text-xs text-muted-foreground">Quick suggestions:</p>
                    <div className="flex flex-wrap gap-1">
                      {message.suggestions.map((suggestion, index) => (
                        <Button
                          key={index}
                          variant="outline"
                          size="sm"
                          className="text-xs"
                          onClick={() => handleSuggestionClick(suggestion)}
                        >
                          {suggestion}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                {message.actions && message.actions.length > 0 && (
                  <div className="mt-2 flex items-center gap-1">
                    {message.actions.map((action) => (
                      <Button
                        key={action.id}
                        variant="ghost"
                        size="sm"
                        onClick={() => handleActionClick(action)}
                        className="text-xs"
                      >
                        {action.type === 'apply' && <CheckCircle className="h-3 w-3 mr-1" />}
                        {action.type === 'copy' && <Copy className="h-3 w-3 mr-1" />}
                        {action.type === 'regenerate' && <RefreshCw className="h-3 w-3 mr-1" />}
                        {action.label}
                      </Button>
                    ))}
                  </div>
                )}
                
                <p className="text-xs text-muted-foreground mt-1">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
              
              {message.type === 'user' && (
                <Avatar className="h-8 w-8">
                  <AvatarFallback>
                    <User className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
              )}
            </div>
          ))}
          
          {isLoading && (
            <div className="flex gap-3">
              <Avatar className="h-8 w-8">
                <AvatarFallback>
                  <Bot className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
              <div className="bg-muted p-3 rounded-lg">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            placeholder="Ask me anything..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            disabled={isLoading}
          />
          <Button onClick={handleSendMessage} disabled={isLoading || !inputMessage.trim()} aria-label="Send message">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}

function getContextDescription(context: string): string {
  switch (context) {
    case 'course-creation':
      return 'Course creation & curriculum design'
    case 'student-learning':
      return 'Learning assistance & progress tracking'
    case 'assessment':
      return 'Assessment design & evaluation'
    default:
      return 'General assistance'
  }
}

function getInitialSuggestions(context: string): string[] {
  switch (context) {
    case 'course-creation':
      return [
        "Help me create a course outline",
        "Suggest learning objectives",
        "Generate assessment questions",
        "Create lesson content"
      ]
    case 'student-learning':
      return [
        "Explain this concept",
        "Give me practice questions",
        "Check my understanding",
        "Show my progress"
      ]
    case 'assessment':
      return [
        "Create multiple choice questions",
        "Design a rubric",
        "Suggest assessment methods",
        "Generate feedback"
      ]
    default:
      return [
        "How can I help you today?",
        "What would you like to know?",
        "Get started with AI assistance"
      ]
  }
}

async function generateAIResponse(message: string, context: string, contextData?: any): Promise<ChatMessage> {
  // Mock AI response generation - replace with actual API call
  const responses = {
    'course-creation': [
      "I can help you create comprehensive course content. Based on your input, I suggest structuring your course into modules with clear learning objectives.",
      "For effective course design, consider starting with a needs assessment and learning outcomes. Would you like me to generate a course outline?",
      "I can assist with curriculum development using pedagogical best practices. What specific area would you like to focus on?"
    ],
    'student-learning': [
      "I'm here to help you learn effectively. Let me break down this concept into manageable parts.",
      "Based on your progress, I recommend focusing on these areas for improvement.",
      "Great question! Let me provide you with a detailed explanation and some practice exercises."
    ],
    'assessment': [
      "I can help you create various types of assessments. What learning objectives are you trying to evaluate?",
      "For effective assessment design, consider using a mix of formative and summative evaluations.",
      "I can generate questions that align with your course objectives. What topic should we focus on?"
    ],
    'general': [
      "I'm here to help! What specific task would you like assistance with?",
      "I can provide guidance on various topics. Could you be more specific about what you need?",
      "Let me help you with that. What would you like to know more about?"
    ]
  }

  const contextResponses = responses[context as keyof typeof responses] || responses.general
  const randomResponse = contextResponses[Math.floor(Math.random() * contextResponses.length)]

  return {
    id: Date.now().toString(),
    type: 'assistant',
    content: randomResponse,
    timestamp: new Date(),
    actions: [
      {
        id: 'apply',
        label: 'Apply',
        type: 'apply',
        data: { suggestion: randomResponse }
      },
      {
        id: 'copy',
        label: 'Copy',
        type: 'copy',
        data: randomResponse
      },
      {
        id: 'regenerate',
        label: 'Regenerate',
        type: 'regenerate'
      }
    ]
  }
}