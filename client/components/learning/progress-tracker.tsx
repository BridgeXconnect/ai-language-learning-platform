"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { 
  CheckCircle, 
  Circle, 
  Lock, 
  Star, 
  Trophy, 
  TrendingUp,
  Clock,
  Target,
  BookOpen,
  Award,
  Zap,
  Calendar,
  BarChart3,
  PlayCircle,
  Pause,
  RotateCcw
} from "lucide-react"

export interface ProgressData {
  overall: {
    percentage: number
    completedItems: number
    totalItems: number
    timeSpent: number
    streak: number
    level: number
    xp: number
    nextLevelXp: number
  }
  skills: SkillProgress[]
  modules: ModuleProgress[]
  achievements: Achievement[]
  timeline: TimelineEvent[]
}

export interface SkillProgress {
  id: string
  name: string
  category: string
  level: number
  progress: number
  maxLevel: number
  prerequisites: string[]
  unlocked: boolean
  mastery: 'beginner' | 'intermediate' | 'advanced' | 'expert'
}

export interface ModuleProgress {
  id: string
  title: string
  description: string
  progress: number
  status: 'locked' | 'available' | 'in_progress' | 'completed'
  estimatedTime: number
  completedTime?: number
  lessons: LessonProgress[]
}

export interface LessonProgress {
  id: string
  title: string
  type: 'video' | 'reading' | 'quiz' | 'assignment' | 'interactive'
  status: 'locked' | 'available' | 'in_progress' | 'completed'
  progress: number
  score?: number
  timeSpent?: number
}

export interface Achievement {
  id: string
  title: string
  description: string
  icon: string
  category: 'completion' | 'streak' | 'mastery' | 'social' | 'time'
  earned: boolean
  earnedAt?: Date
  progress?: number
  target?: number
}

export interface TimelineEvent {
  id: string
  type: 'lesson_completed' | 'module_completed' | 'achievement_earned' | 'streak_milestone'
  title: string
  description: string
  timestamp: Date
  points?: number
}

export interface ProgressTrackerProps {
  variant?: 'linear' | 'circular' | 'skill-tree' | 'timeline'
  data: ProgressData
  onModuleClick?: (moduleId: string) => void
  onLessonClick?: (lessonId: string) => void
  showAchievements?: boolean
  showTimeline?: boolean
  className?: string
}

export function ProgressTracker({ 
  variant = 'linear',
  data,
  onModuleClick,
  onLessonClick,
  showAchievements = true,
  showTimeline = true,
  className = ""
}: ProgressTrackerProps) {
  const [selectedModule, setSelectedModule] = useState<string | null>(null)
  const [showDetails, setShowDetails] = useState(false)

  const handleModuleClick = (moduleId: string) => {
    setSelectedModule(moduleId)
    onModuleClick?.(moduleId)
  }

  const renderLinearProgress = () => (
    <div className="space-y-6">
      {/* Overall Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Overall Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Course Completion</span>
              <span className="text-sm font-bold">{data.overall.percentage}%</span>
            </div>
            <Progress value={data.overall.percentage} className="h-3" />
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span>{data.overall.completedItems}/{data.overall.totalItems} completed</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-blue-500" />
                <span>{Math.floor(data.overall.timeSpent / 60)}h {data.overall.timeSpent % 60}m spent</span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-orange-500" />
                <span>{data.overall.streak} day streak</span>
              </div>
              <div className="flex items-center gap-2">
                <Star className="h-4 w-4 text-yellow-500" />
                <span>Level {data.overall.level}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Modules */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            Course Modules
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.modules.map((module, index) => (
              <div 
                key={module.id}
                className={`p-4 rounded-lg border transition-colors cursor-pointer ${
                  selectedModule === module.id ? 'border-primary bg-primary/5' : 'hover:bg-muted/50'
                }`}
                onClick={() => handleModuleClick(module.id)}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground text-sm font-bold">
                      {index + 1}
                    </div>
                    <div>
                      <h4 className="font-medium">{module.title}</h4>
                      <p className="text-sm text-muted-foreground">{module.description}</p>
                    </div>
                  </div>
                  <Badge variant={getModuleStatusVariant(module.status)}>
                    {module.status.replace('_', ' ')}
                  </Badge>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Progress</span>
                    <span>{module.progress}%</span>
                  </div>
                  <Progress value={module.progress} className="h-2" />
                  
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{module.lessons.length} lessons</span>
                    <span>Est. {module.estimatedTime}min</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderCircularProgress = () => (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {data.modules.map((module) => (
        <Card key={module.id} className="relative">
          <CardHeader className="text-center">
            <div className="mx-auto w-20 h-20 relative">
              <svg className="w-20 h-20 transform -rotate-90">
                <circle
                  cx="40"
                  cy="40"
                  r="36"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="none"
                  className="text-muted-foreground/20"
                />
                <circle
                  cx="40"
                  cy="40"
                  r="36"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${2 * Math.PI * 36}`}
                  strokeDashoffset={`${2 * Math.PI * 36 * (1 - module.progress / 100)}`}
                  className="text-primary transition-all duration-300"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-lg font-bold">{module.progress}%</span>
              </div>
            </div>
            <CardTitle className="text-lg">{module.title}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Badge variant={getModuleStatusVariant(module.status)} className="w-full justify-center">
                {module.status.replace('_', ' ')}
              </Badge>
              <p className="text-sm text-muted-foreground text-center">
                {module.lessons.filter(l => l.status === 'completed').length} of {module.lessons.length} lessons
              </p>
              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => handleModuleClick(module.id)}
              >
                {module.status === 'completed' ? 'Review' : 'Continue'}
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )

  const renderSkillTree = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Skill Progression
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {data.skills.map((skill) => (
            <div key={skill.id} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <h4 className="font-medium">{skill.name}</h4>
                  <Badge variant="outline">{skill.category}</Badge>
                  <Badge variant={skill.unlocked ? 'default' : 'secondary'}>
                    {skill.mastery}
                  </Badge>
                </div>
                <span className="text-sm font-medium">
                  Level {skill.level}/{skill.maxLevel}
                </span>
              </div>
              <Progress value={skill.progress} className="h-2" />
              {!skill.unlocked && (
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <Lock className="h-3 w-3" />
                  <span>Requires: {skill.prerequisites.join(', ')}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )

  const renderTimeline = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calendar className="h-5 w-5" />
          Learning Timeline
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {data.timeline.map((event) => (
            <div key={event.id} className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                {getTimelineIcon(event.type)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">{event.title}</h4>
                  <span className="text-sm text-muted-foreground">
                    {event.timestamp.toLocaleDateString()}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">{event.description}</p>
                {event.points && (
                  <Badge variant="secondary" className="mt-1">
                    +{event.points} XP
                  </Badge>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )

  const renderAchievements = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Trophy className="h-5 w-5" />
          Achievements
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {data.achievements.map((achievement) => (
            <div 
              key={achievement.id}
              className={`p-3 rounded-lg border text-center transition-colors ${
                achievement.earned ? 'border-yellow-500 bg-yellow-50' : 'border-muted bg-muted/50'
              }`}
            >
              <div className="text-2xl mb-2">{achievement.icon}</div>
              <h4 className="font-medium text-sm">{achievement.title}</h4>
              <p className="text-xs text-muted-foreground mt-1">{achievement.description}</p>
              {achievement.earned && achievement.earnedAt && (
                <p className="text-xs text-yellow-600 mt-1">
                  Earned {achievement.earnedAt.toLocaleDateString()}
                </p>
              )}
              {!achievement.earned && achievement.progress && achievement.target && (
                <div className="mt-2">
                  <Progress 
                    value={(achievement.progress / achievement.target) * 100} 
                    className="h-1"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    {achievement.progress}/{achievement.target}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className={`space-y-6 ${className}`}>
      {variant === 'linear' && renderLinearProgress()}
      {variant === 'circular' && renderCircularProgress()}
      {variant === 'skill-tree' && renderSkillTree()}
      {variant === 'timeline' && renderTimeline()}
      
      {showAchievements && renderAchievements()}
      {showTimeline && variant !== 'timeline' && renderTimeline()}
    </div>
  )
}

function getModuleStatusVariant(status: string): "default" | "secondary" | "destructive" | "outline" {
  switch (status) {
    case 'completed':
      return 'default'
    case 'in_progress':
      return 'secondary'
    case 'locked':
      return 'outline'
    default:
      return 'outline'
  }
}

function getTimelineIcon(type: string) {
  switch (type) {
    case 'lesson_completed':
      return <CheckCircle className="h-4 w-4 text-white" />
    case 'module_completed':
      return <BookOpen className="h-4 w-4 text-white" />
    case 'achievement_earned':
      return <Trophy className="h-4 w-4 text-white" />
    case 'streak_milestone':
      return <Zap className="h-4 w-4 text-white" />
    default:
      return <Circle className="h-4 w-4 text-white" />
  }
}