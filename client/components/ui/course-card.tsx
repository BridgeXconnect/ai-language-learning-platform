/**
 * Course Card Component
 * Consistent course representation across all portals
 * Features: Multiple variants, progress tracking, accessibility, interactive states
 */

"use client"

import React, { useState } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/enhanced-button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/enhanced-card'
import { Progress } from '@/components/ui/progress'
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'
import { 
  Clock, 
  Users, 
  Star, 
  BookOpen, 
  Play, 
  Pause,
  CheckCircle,
  Lock,
  Calendar,
  Award,
  TrendingUp,
  BarChart,
  Eye,
  Heart,
  Share2,
  Download,
  MoreHorizontal,
  Target,
  Zap,
  Brain,
  type LucideIcon
} from 'lucide-react'

const courseCardVariants = cva(
  [
    'group transition-all duration-200',
    'focus-within:ring-2 focus-within:ring-primary/20',
  ],
  {
    variants: {
      variant: {
        grid: [
          'w-full max-w-sm',
        ],
        list: [
          'w-full flex',
        ],
        compact: [
          'w-full max-w-xs',
        ],
        detailed: [
          'w-full max-w-2xl',
        ],
      },
      state: {
        available: 'cursor-pointer hover:shadow-lg hover:-translate-y-1',
        enrolled: 'cursor-pointer hover:shadow-lg hover:-translate-y-1',
        'in-progress': 'cursor-pointer hover:shadow-lg hover:-translate-y-1',
        completed: 'cursor-pointer hover:shadow-lg hover:-translate-y-1',
        locked: 'cursor-not-allowed opacity-60',
      },
      priority: {
        normal: '',
        featured: 'ring-2 ring-primary/20 bg-primary/5',
        urgent: 'ring-2 ring-orange-200 bg-orange-50',
        recommended: 'ring-2 ring-green-200 bg-green-50',
      },
    },
    defaultVariants: {
      variant: 'grid',
      state: 'available',
      priority: 'normal',
    },
  }
)

export interface CourseInstructor {
  id: string
  name: string
  avatar?: string
  title?: string
  rating?: number
}

export interface CourseStats {
  enrollments: number
  completionRate: number
  rating: number
  reviews: number
  duration: number // in minutes
  lessons: number
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  lastUpdated: Date
}

export interface CourseProgress {
  completedLessons: number
  totalLessons: number
  timeSpent: number // in minutes
  lastAccessed: Date
  nextLesson?: string
  completionPercentage: number
}

export interface CourseMetadata {
  tags: string[]
  category: string
  language: string
  prerequisites?: string[]
  learningOutcomes: string[]
  certificate: boolean
  aiGenerated: boolean
  qualityScore?: number
}

export interface CourseCardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof courseCardVariants> {
  // Core course data
  id: string
  title: string
  description: string
  thumbnail?: string
  instructor: CourseInstructor
  stats: CourseStats
  metadata: CourseMetadata
  
  // Progress and state
  progress?: CourseProgress
  isEnrolled?: boolean
  isFavorite?: boolean
  isNew?: boolean
  
  // Pricing
  price?: number
  originalPrice?: number
  isFree?: boolean
  
  // Actions
  onEnroll?: () => void
  onContinue?: () => void
  onView?: () => void
  onFavorite?: () => void
  onShare?: () => void
  onDownload?: () => void
  onMoreActions?: () => void
  
  // Display options
  showProgress?: boolean
  showStats?: boolean
  showInstructor?: boolean
  showActions?: boolean
  showTags?: boolean
  showPreview?: boolean
  
  // Accessibility
  ariaLabel?: string
}

const CourseCard = React.forwardRef<HTMLDivElement, CourseCardProps>(
  ({
    className,
    variant,
    state,
    priority,
    id,
    title,
    description,
    thumbnail,
    instructor,
    stats,
    metadata,
    progress,
    isEnrolled = false,
    isFavorite = false,
    isNew = false,
    price,
    originalPrice,
    isFree = false,
    onEnroll,
    onContinue,
    onView,
    onFavorite,
    onShare,
    onDownload,
    onMoreActions,
    showProgress = true,
    showStats = true,
    showInstructor = true,
    showActions = true,
    showTags = true,
    showPreview = false,
    ariaLabel,
    ...props
  }, ref) => {
    const [isHovered, setIsHovered] = useState(false)
    const [imageLoaded, setImageLoaded] = useState(false)
    
    const getDifficultyColor = (difficulty: string) => {
      switch (difficulty) {
        case 'beginner': return 'text-green-600 bg-green-50'
        case 'intermediate': return 'text-yellow-600 bg-yellow-50'
        case 'advanced': return 'text-red-600 bg-red-50'
        default: return 'text-gray-600 bg-gray-50'
      }
    }
    
    const getDifficultyIcon = (difficulty: string) => {
      switch (difficulty) {
        case 'beginner': return Target
        case 'intermediate': return TrendingUp
        case 'advanced': return Brain
        default: return BookOpen
      }
    }
    
    const getStateIcon = () => {
      switch (state) {
        case 'completed': return CheckCircle
        case 'in-progress': return Play
        case 'locked': return Lock
        default: return BookOpen
      }
    }
    
    const formatDuration = (minutes: number) => {
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      if (hours > 0) {
        return `${hours}h ${mins}m`
      }
      return `${mins}m`
    }
    
    const formatPrice = (price: number) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
      }).format(price)
    }
    
    const handleCardClick = () => {
      if (state === 'locked') return
      
      if (isEnrolled && progress) {
        onContinue?.()
      } else if (isEnrolled) {
        onView?.()
      } else {
        onView?.()
      }
    }
    
    const handlePrimaryAction = (e: React.MouseEvent) => {
      e.stopPropagation()
      
      if (isEnrolled && progress) {
        onContinue?.()
      } else if (isEnrolled) {
        onView?.()
      } else {
        onEnroll?.()
      }
    }
    
    const getPrimaryActionLabel = () => {
      if (isEnrolled && progress) {
        return progress.completionPercentage === 100 ? 'Review' : 'Continue'
      } else if (isEnrolled) {
        return 'Start Learning'
      } else {
        return isFree ? 'Enroll Free' : 'Enroll Now'
      }
    }
    
    const StateIcon = getStateIcon()
    const DifficultyIcon = getDifficultyIcon(stats.difficulty)
    
    // List variant layout
    if (variant === 'list') {
      return (
        <Card
          ref={ref}
          className={cn(courseCardVariants({ variant, state, priority }), className)}
          onClick={handleCardClick}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          role="button"
          tabIndex={state === 'locked' ? -1 : 0}
          aria-label={ariaLabel || `Course: ${title}`}
          {...props}
        >
          <div className="flex gap-4 p-4">
            {/* Thumbnail */}
            <div className="flex-shrink-0 w-24 h-16 rounded-lg overflow-hidden bg-gray-100 relative">
              {thumbnail && (
                <img
                  src={thumbnail}
                  alt={title}
                  className={cn(
                    "w-full h-full object-cover transition-opacity duration-300",
                    imageLoaded ? "opacity-100" : "opacity-0"
                  )}
                  onLoad={() => setImageLoaded(true)}
                />
              )}
              {!imageLoaded && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <BookOpen className="h-8 w-8 text-gray-400" />
                </div>
              )}
              
              {/* State indicator */}
              <div className="absolute top-1 right-1">
                <StateIcon className="h-4 w-4 text-white drop-shadow-lg" />
              </div>
            </div>
            
            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-sm truncate">{title}</h3>
                  <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                    {description}
                  </p>
                  
                  {/* Stats */}
                  <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {formatDuration(stats.duration)}
                    </div>
                    <div className="flex items-center gap-1">
                      <Users className="h-3 w-3" />
                      {stats.enrollments}
                    </div>
                    <div className="flex items-center gap-1">
                      <Star className="h-3 w-3" />
                      {stats.rating}
                    </div>
                  </div>
                </div>
                
                {/* Actions */}
                <div className="flex items-center gap-2 ml-4">
                  <Button
                    size="sm"
                    variant={isEnrolled ? "outline" : "default"}
                    onClick={handlePrimaryAction}
                    disabled={state === 'locked'}
                  >
                    {getPrimaryActionLabel()}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )
    }
    
    // Grid variant layout (default)
    return (
      <Card
        ref={ref}
        className={cn(courseCardVariants({ variant, state, priority }), className)}
        onClick={handleCardClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        role="button"
        tabIndex={state === 'locked' ? -1 : 0}
        aria-label={ariaLabel || `Course: ${title}`}
        {...props}
      >
        {/* Thumbnail */}
        <div className="relative aspect-video rounded-t-lg overflow-hidden bg-gray-100">
          {thumbnail && (
            <img
              src={thumbnail}
              alt={title}
              className={cn(
                "w-full h-full object-cover transition-all duration-300",
                imageLoaded ? "opacity-100" : "opacity-0",
                isHovered && "scale-105"
              )}
              onLoad={() => setImageLoaded(true)}
            />
          )}
          {!imageLoaded && (
            <div className="absolute inset-0 flex items-center justify-center">
              <BookOpen className="h-12 w-12 text-gray-400" />
            </div>
          )}
          
          {/* Overlay badges */}
          <div className="absolute top-2 left-2 flex flex-col gap-1">
            {isNew && (
              <Badge className="bg-green-500 text-white text-xs">New</Badge>
            )}
            {metadata.aiGenerated && (
              <Badge className="bg-purple-500 text-white text-xs">
                <Zap className="h-3 w-3 mr-1" />
                AI Generated
              </Badge>
            )}
            {priority === 'featured' && (
              <Badge className="bg-orange-500 text-white text-xs">Featured</Badge>
            )}
          </div>
          
          {/* State indicator */}
          <div className="absolute top-2 right-2">
            <StateIcon className="h-5 w-5 text-white drop-shadow-lg" />
          </div>
          
          {/* Price badge */}
          {!isFree && price && (
            <div className="absolute bottom-2 right-2">
              <Badge className="bg-white text-black text-xs font-semibold">
                {originalPrice && (
                  <span className="line-through text-gray-500 mr-1">
                    {formatPrice(originalPrice)}
                  </span>
                )}
                {formatPrice(price)}
              </Badge>
            </div>
          )}
          
          {/* Hover actions */}
          {showActions && isHovered && (
            <div className="absolute inset-0 bg-black/50 flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <Button
                size="sm"
                variant="secondary"
                onClick={(e) => {
                  e.stopPropagation()
                  onView?.()
                }}
              >
                <Eye className="h-4 w-4 mr-2" />
                Preview
              </Button>
              <Button
                size="sm"
                onClick={handlePrimaryAction}
                disabled={state === 'locked'}
              >
                {getPrimaryActionLabel()}
              </Button>
            </div>
          )}
        </div>
        
        <CardContent className="p-4">
          {/* Header */}
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-sm line-clamp-2 group-hover:text-primary transition-colors">
                {title}
              </h3>
              
              {/* Instructor */}
              {showInstructor && (
                <div className="flex items-center gap-2 mt-1">
                  <Avatar className="h-4 w-4">
                    <AvatarImage src={instructor.avatar} alt={instructor.name} />
                    <AvatarFallback className="text-xs">
                      {instructor.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <span className="text-xs text-muted-foreground truncate">
                    {instructor.name}
                  </span>
                </div>
              )}
            </div>
            
            {/* Quick actions */}
            <div className="flex items-center gap-1 ml-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  onFavorite?.()
                }}
                className="opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <Heart className={cn(
                  "h-4 w-4",
                  isFavorite ? "fill-red-500 text-red-500" : "text-gray-400"
                )} />
              </Button>
              
              {onMoreActions && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    onMoreActions()
                  }}
                  className="opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
          
          {/* Description */}
          <p className="text-xs text-muted-foreground line-clamp-2 mb-3">
            {description}
          </p>
          
          {/* Progress */}
          {showProgress && progress && (
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-muted-foreground">Progress</span>
                <span className="text-xs font-medium">
                  {progress.completionPercentage}%
                </span>
              </div>
              <Progress value={progress.completionPercentage} className="h-2" />
              <div className="flex items-center justify-between mt-1 text-xs text-muted-foreground">
                <span>{progress.completedLessons} of {progress.totalLessons} lessons</span>
                <span>{formatDuration(progress.timeSpent)} watched</span>
              </div>
            </div>
          )}
          
          {/* Tags */}
          {showTags && metadata.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-3">
              {metadata.tags.slice(0, 3).map((tag, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {metadata.tags.length > 3 && (
                <Badge variant="outline" className="text-xs">
                  +{metadata.tags.length - 3} more
                </Badge>
              )}
            </div>
          )}
          
          {/* Stats */}
          {showStats && (
            <div className="flex items-center justify-between text-xs text-muted-foreground mb-3">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {formatDuration(stats.duration)}
                </div>
                <div className="flex items-center gap-1">
                  <BookOpen className="h-3 w-3" />
                  {stats.lessons}
                </div>
                <div className="flex items-center gap-1">
                  <Star className="h-3 w-3" />
                  {stats.rating}
                </div>
              </div>
              
              <div className="flex items-center gap-1">
                <Badge 
                  variant="outline" 
                  className={cn("text-xs", getDifficultyColor(stats.difficulty))}
                >
                  <DifficultyIcon className="h-3 w-3 mr-1" />
                  {stats.difficulty}
                </Badge>
              </div>
            </div>
          )}
          
          {/* Actions */}
          {showActions && (
            <div className="flex items-center gap-2">
              <Button
                className="flex-1"
                size="sm"
                variant={isEnrolled ? "outline" : "default"}
                onClick={handlePrimaryAction}
                disabled={state === 'locked'}
              >
                {getPrimaryActionLabel()}
              </Button>
              
              {onShare && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    onShare()
                  }}
                >
                  <Share2 className="h-4 w-4" />
                </Button>
              )}
            </div>
          )}
          
          {/* Quality indicator for AI generated courses */}
          {metadata.aiGenerated && metadata.qualityScore && (
            <div className="mt-2 flex items-center gap-1">
              <BarChart className="h-3 w-3 text-purple-500" />
              <span className="text-xs text-purple-600">
                AI Quality Score: {metadata.qualityScore}%
              </span>
            </div>
          )}
        </CardContent>
      </Card>
    )
  }
)

CourseCard.displayName = 'CourseCard'

export { CourseCard, courseCardVariants }