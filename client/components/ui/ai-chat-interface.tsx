/**
 * AI Chat Interface Component
 * Consistent AI interaction component across all portals
 * Features: Multiple variants, accessibility, typing indicators, error handling
 */

"use client"

import React, { useState, useRef, useEffect, useCallback } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/enhanced-button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/enhanced-card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Textarea } from '@/components/ui/textarea'
import { 
  Bot, 
  User, 
  Send, 
  Loader2, 
  AlertCircle, 
  Maximize2, 
  Minimize2, 
  X,
  RefreshCw,
  MessageSquare,
  Brain,
  Sparkles,
  HelpCircle,
  Lightbulb,
  Settings,
  Volume2,
  VolumeX,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown
} from 'lucide-react'

const chatVariants = cva(
  [
    'flex flex-col bg-background border rounded-lg transition-all duration-300',
    'focus-within:ring-2 focus-within:ring-primary/20',
  ],
  {
    variants: {
      variant: {
        compact: [
          'h-64 max-w-sm',
        ],
        expanded: [
          'h-96 max-w-2xl',
        ],
        overlay: [
          'fixed bottom-4 right-4 h-80 w-80 z-50 shadow-2xl',
        ],
        sidebar: [
          'h-full w-full max-w-md',
        ],
        fullscreen: [
          'h-screen w-full max-w-none rounded-none',
        ],
      },
      theme: {
        default: 'border-border',
        blue: 'border-blue-200 bg-blue-50/50',
        purple: 'border-purple-200 bg-purple-50/50',
        green: 'border-green-200 bg-green-50/50',
      },
    },
    defaultVariants: {
      variant: 'compact',
      theme: 'default',
    },
  }
)

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  isTyping?: boolean
  isError?: boolean
  metadata?: {
    confidence?: number
    sources?: string[]
    suggestions?: string[]
    actionType?: 'course_planning' | 'content_creation' | 'assessment' | 'help'
  }
}

export interface AIChatInterfaceProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof chatVariants> {
  // Core props
  messages: ChatMessage[]
  onSendMessage: (message: string) => void
  onMessageAction?: (messageId: string, action: string) => void
  
  // State props
  isLoading?: boolean
  isTyping?: boolean
  isOffline?: boolean
  isError?: boolean
  
  // UI props
  title?: string
  subtitle?: string
  placeholder?: string
  showHeader?: boolean
  showFooter?: boolean
  showSuggestions?: boolean
  showVoiceInput?: boolean
  showActions?: boolean
  
  // Behavior props
  autoFocus?: boolean
  maxMessages?: number
  persistMessages?: boolean
  
  // Callbacks
  onToggleSize?: () => void
  onClose?: () => void
  onClear?: () => void
  onExport?: () => void
  onSettings?: () => void
  
  // Accessibility
  ariaLabel?: string
  ariaDescribedBy?: string
}

const AIChatInterface = React.forwardRef<HTMLDivElement, AIChatInterfaceProps>(
  ({ 
    className,
    variant,
    theme,
    messages = [],
    onSendMessage,
    onMessageAction,
    isLoading = false,
    isTyping = false,
    isOffline = false,
    isError = false,
    title = "AI Assistant",
    subtitle,
    placeholder = "Type your message...",
    showHeader = true,
    showFooter = true,
    showSuggestions = true,
    showVoiceInput = false,
    showActions = true,
    autoFocus = false,
    maxMessages = 100,
    persistMessages = false,
    onToggleSize,
    onClose,
    onClear,
    onExport,
    onSettings,
    ariaLabel = "AI Chat Interface",
    ariaDescribedBy,
    ...props 
  }, ref) => {
    const [input, setInput] = useState('')
    const [isExpanded, setIsExpanded] = useState(false)
    const [isSpeaking, setIsSpeaking] = useState(false)
    const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null)
    const [suggestions] = useState([
      "Help me plan a course",
      "Create an assessment",
      "Generate content ideas",
      "Explain a concept"
    ])
    
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLTextAreaElement>(null)
    const scrollAreaRef = useRef<HTMLDivElement>(null)
    
    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])
    
    // Auto-focus input when requested
    useEffect(() => {
      if (autoFocus && inputRef.current) {
        inputRef.current.focus()
      }
    }, [autoFocus])
    
    const handleSubmit = useCallback((e: React.FormEvent) => {
      e.preventDefault()
      if (!input.trim() || isLoading) return
      
      onSendMessage(input.trim())
      setInput('')
    }, [input, isLoading, onSendMessage])
    
    const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSubmit(e)
      }
    }, [handleSubmit])
    
    const handleSuggestionClick = useCallback((suggestion: string) => {
      setInput(suggestion)
      inputRef.current?.focus()
    }, [])
    
    const handleToggleExpanded = useCallback(() => {
      setIsExpanded(!isExpanded)
      onToggleSize?.()
    }, [isExpanded, onToggleSize])
    
    const handleCopyMessage = useCallback(async (messageId: string, content: string) => {
      try {
        await navigator.clipboard.writeText(content)
        setCopiedMessageId(messageId)
        setTimeout(() => setCopiedMessageId(null), 2000)
      } catch (err) {
        console.error('Failed to copy message:', err)
      }
    }, [])
    
    const handleVoiceToggle = useCallback(() => {
      setIsSpeaking(!isSpeaking)
      // Voice synthesis logic would go here
    }, [isSpeaking])
    
    const getMessageIcon = (role: string) => {
      switch (role) {
        case 'assistant':
          return <Bot className="h-4 w-4 text-blue-600" />
        case 'system':
          return <Settings className="h-4 w-4 text-gray-600" />
        default:
          return <User className="h-4 w-4 text-gray-600" />
      }
    }
    
    const getMessageBadge = (message: ChatMessage) => {
      if (message.isError) {
        return <Badge variant="destructive" className="text-xs">Error</Badge>
      }
      if (message.metadata?.confidence && message.metadata.confidence < 0.7) {
        return <Badge variant="secondary" className="text-xs">Low Confidence</Badge>
      }
      if (message.metadata?.actionType) {
        const actionLabels = {
          course_planning: 'Course Planning',
          content_creation: 'Content Creation',
          assessment: 'Assessment',
          help: 'Help'
        }
        return <Badge variant="outline" className="text-xs">{actionLabels[message.metadata.actionType]}</Badge>
      }
      return null
    }
    
    const currentVariant = isExpanded ? 'expanded' : variant
    
    return (
      <div
        ref={ref}
        className={cn(chatVariants({ variant: currentVariant, theme }), className)}
        role="region"
        aria-label={ariaLabel}
        aria-describedby={ariaDescribedBy}
        {...props}
      >
        {/* Header */}
        {showHeader && (
          <CardHeader className="flex-shrink-0 pb-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-blue-600" />
                  <div>
                    <CardTitle className="text-sm font-semibold">{title}</CardTitle>
                    {subtitle && (
                      <p className="text-xs text-muted-foreground">{subtitle}</p>
                    )}
                  </div>
                </div>
                
                {/* Status indicators */}
                <div className="flex items-center gap-1">
                  {isOffline && (
                    <Badge variant="destructive" className="text-xs">Offline</Badge>
                  )}
                  {isError && (
                    <Badge variant="destructive" className="text-xs">Error</Badge>
                  )}
                  {isTyping && (
                    <Badge variant="secondary" className="text-xs">
                      <Loader2 className="h-3 w-3 animate-spin mr-1" />
                      Typing...
                    </Badge>
                  )}
                </div>
              </div>
              
              {/* Header actions */}
              <div className="flex items-center gap-1">
                {showVoiceInput && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleVoiceToggle}
                    aria-label={isSpeaking ? "Disable voice" : "Enable voice"}
                  >
                    {isSpeaking ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                  </Button>
                )}
                
                {variant === 'compact' && onToggleSize && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleToggleExpanded}
                    aria-label={isExpanded ? "Minimize chat" : "Expand chat"}
                  >
                    {isExpanded ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                  </Button>
                )}
                
                {onSettings && (
                  <Button variant="ghost" size="sm" onClick={onSettings} aria-label="Chat settings">
                    <Settings className="h-4 w-4" />
                  </Button>
                )}
                
                {onClose && (
                  <Button variant="ghost" size="sm" onClick={onClose} aria-label="Close chat">
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
        )}
        
        {/* Messages */}
        <CardContent className="flex-1 overflow-hidden p-4">
          <ScrollArea ref={scrollAreaRef} className="h-full">
            <div className="space-y-4">
              {messages.length === 0 ? (
                <div className="text-center py-8">
                  <MessageSquare className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-sm text-muted-foreground">
                    Start a conversation with your AI assistant
                  </p>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={cn(
                      "flex gap-3 group",
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    )}
                  >
                    {message.role !== 'user' && (
                      <div className="flex-shrink-0 mt-1">
                        {getMessageIcon(message.role)}
                      </div>
                    )}
                    
                    <div className={cn(
                      "max-w-[80%] space-y-2",
                      message.role === 'user' ? 'items-end' : 'items-start'
                    )}>
                      {/* Message bubble */}
                      <div className={cn(
                        "px-4 py-2 rounded-lg text-sm",
                        message.role === 'user' 
                          ? "bg-primary text-primary-foreground" 
                          : message.isError
                            ? "bg-destructive/10 text-destructive border border-destructive/20"
                            : "bg-muted",
                        message.isTyping && "animate-pulse"
                      )}>
                        {message.isTyping ? (
                          <div className="flex items-center gap-2">
                            <Loader2 className="h-3 w-3 animate-spin" />
                            <span>Thinking...</span>
                          </div>
                        ) : (
                          <p className="whitespace-pre-wrap">{message.content}</p>
                        )}
                      </div>
                      
                      {/* Message metadata */}
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>{message.timestamp.toLocaleTimeString()}</span>
                        {getMessageBadge(message)}
                        
                        {/* Message actions */}
                        {showActions && !message.isTyping && (
                          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleCopyMessage(message.id, message.content)}
                              aria-label="Copy message"
                            >
                              {copiedMessageId === message.id ? (
                                <Check className="h-3 w-3" />
                              ) : (
                                <Copy className="h-3 w-3" />
                              )}
                            </Button>
                            
                            {message.role === 'assistant' && onMessageAction && (
                              <>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => onMessageAction(message.id, 'like')}
                                  aria-label="Like message"
                                >
                                  <ThumbsUp className="h-3 w-3" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => onMessageAction(message.id, 'dislike')}
                                  aria-label="Dislike message"
                                >
                                  <ThumbsDown className="h-3 w-3" />
                                </Button>
                              </>
                            )}
                          </div>
                        )}
                      </div>
                      
                      {/* Suggestions from AI */}
                      {message.metadata?.suggestions && message.metadata.suggestions.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {message.metadata.suggestions.map((suggestion, index) => (
                            <Button
                              key={index}
                              variant="outline"
                              size="sm"
                              onClick={() => handleSuggestionClick(suggestion)}
                              className="text-xs h-6"
                            >
                              <Lightbulb className="h-3 w-3 mr-1" />
                              {suggestion}
                            </Button>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    {message.role === 'user' && (
                      <div className="flex-shrink-0 mt-1">
                        {getMessageIcon(message.role)}
                      </div>
                    )}
                  </div>
                ))
              )}
              
              {/* Typing indicator */}
              {isTyping && (
                <div className="flex gap-3">
                  <div className="flex-shrink-0 mt-1">
                    <Bot className="h-4 w-4 text-blue-600" />
                  </div>
                  <div className="bg-muted px-4 py-2 rounded-lg">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>
        </CardContent>
        
        {/* Quick suggestions */}
        {showSuggestions && messages.length === 0 && (
          <div className="px-4 pb-2">
            <div className="flex flex-wrap gap-1">
              {suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="text-xs h-6"
                >
                  <Sparkles className="h-3 w-3 mr-1" />
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        )}
        
        {/* Input area */}
        {showFooter && (
          <div className="flex-shrink-0 p-4 border-t">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <div className="flex-1">
                <Textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={isOffline ? "Chat is offline" : placeholder}
                  disabled={isLoading || isOffline}
                  className="min-h-[40px] max-h-[120px] resize-none"
                  aria-label="Type your message"
                />
              </div>
              <Button
                type="submit"
                disabled={!input.trim() || isLoading || isOffline}
                aria-label="Send message"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </form>
            
            {/* Footer actions */}
            <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
              <div className="flex items-center gap-2">
                <span>Press Enter to send, Shift+Enter for new line</span>
                {isError && (
                  <Button variant="ghost" size="sm" onClick={() => location.reload()}>
                    <RefreshCw className="h-3 w-3 mr-1" />
                    Retry
                  </Button>
                )}
              </div>
              
              <div className="flex items-center gap-1">
                {onClear && messages.length > 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={onClear}
                    className="text-xs h-6"
                  >
                    Clear
                  </Button>
                )}
                {onExport && messages.length > 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={onExport}
                    className="text-xs h-6"
                  >
                    Export
                  </Button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }
)

AIChatInterface.displayName = 'AIChatInterface'

export { AIChatInterface, chatVariants }