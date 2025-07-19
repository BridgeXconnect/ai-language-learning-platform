"use client"

import React, { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { 
  Trophy, 
  Target, 
  TrendingUp, 
  Clock, 
  BookOpen, 
  CheckCircle, 
  Star, 
  Award,
  Calendar,
  BarChart3,
  PieChart,
  Activity,
  Zap,
  Brain,
  Users,
  Medal,
  Crown,
  Lock,
  Play
} from "lucide-react"

// Types
export interface SkillNode {
  id: string
  name: string
  description: string
  level: number
  maxLevel: number
  progress: number
  isUnlocked: boolean
  isCompleted: boolean
  prerequisites: string[]
  rewards: string[]
  category: string
  icon: React.ReactNode
  position: { x: number; y: number }
}

export interface LearningProgress {
  userId: string
  courseId: string
  overallProgress: number
  completedLessons: number
  totalLessons: number
  skillsUnlocked: number
  achievementsEarned: number
  streakDays: number
  timeSpent: number
  lastActive: Date
  level: number
  experiencePoints: number
  nextLevelXP: number
}

export interface Achievement {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  category: 'progress' | 'skill' | 'time' | 'social'
  isUnlocked: boolean
  unlockedAt?: Date
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
  points: number
}

export interface StudySession {
  id: string
  date: Date
  duration: number
  lessonsCompleted: number
  exercisesCompleted: number
  accuracy: number
  xpGained: number
}

interface ProgressTrackingProps {
  progress: LearningProgress
  skills: SkillNode[]
  achievements: Achievement[]
  studySessions: StudySession[]
  onSkillClick?: (skill: SkillNode) => void
  onAchievementClick?: (achievement: Achievement) => void
  className?: string
}

const ProgressTracking: React.FC<ProgressTrackingProps> = ({
  progress,
  skills,
  achievements,
  studySessions,
  onSkillClick,
  onAchievementClick,
  className = ""
}) => {
  const [selectedTimeRange, setSelectedTimeRange] = useState<'week' | 'month' | 'year'>('week')
  const [hoveredSkill, setHoveredSkill] = useState<string | null>(null)

  // Calculate statistics
  const completedSkills = skills.filter(skill => skill.isCompleted).length
  const unlockedAchievements = achievements.filter(a => a.isUnlocked).length
  const averageAccuracy = studySessions.reduce((sum, s) => sum + s.accuracy, 0) / studySessions.length || 0
  const totalStudyTime = studySessions.reduce((sum, s) => sum + s.duration, 0)

  // Get recent sessions based on time range
  const getRecentSessions = (range: 'week' | 'month' | 'year') => {
    const now = new Date()
    const daysBack = range === 'week' ? 7 : range === 'month' ? 30 : 365
    const cutoff = new Date(now.getTime() - daysBack * 24 * 60 * 60 * 1000)
    return studySessions.filter(s => s.date >= cutoff)
  }

  const recentSessions = getRecentSessions(selectedTimeRange)

  return (
    <TooltipProvider>
      <div className={`space-y-6 ${className}`}>
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Overall Progress</CardTitle>
              <Trophy className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{progress.overallProgress}%</div>
              <Progress value={progress.overallProgress} className="mt-2" />
              <p className="text-xs text-muted-foreground mt-1">
                {progress.completedLessons} of {progress.totalLessons} lessons
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Skills Mastered</CardTitle>
              <Target className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{completedSkills}</div>
              <p className="text-xs text-muted-foreground">
                {skills.length - completedSkills} skills remaining
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Study Streak</CardTitle>
              <Zap className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{progress.streakDays}</div>
              <p className="text-xs text-muted-foreground">days in a row</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Level</CardTitle>
              <Crown className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{progress.level}</div>
              <Progress 
                value={(progress.experiencePoints / progress.nextLevelXP) * 100} 
                className="mt-2" 
              />
              <p className="text-xs text-muted-foreground mt-1">
                {progress.experiencePoints} / {progress.nextLevelXP} XP
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="skills" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="skills">
              <Brain className="w-4 h-4 mr-2" />
              Skills Tree
            </TabsTrigger>
            <TabsTrigger value="achievements">
              <Award className="w-4 h-4 mr-2" />
              Achievements
            </TabsTrigger>
            <TabsTrigger value="analytics">
              <BarChart3 className="w-4 h-4 mr-2" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="activity">
              <Activity className="w-4 h-4 mr-2" />
              Activity
            </TabsTrigger>
          </TabsList>

          {/* Skills Tree Tab */}
          <TabsContent value="skills" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="w-5 h-5" />
                  Skills Tree
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Master skills to unlock new learning paths
                </p>
              </CardHeader>
              <CardContent>
                <SkillTree 
                  skills={skills} 
                  onSkillClick={onSkillClick}
                  hoveredSkill={hoveredSkill}
                  onSkillHover={setHoveredSkill}
                />
              </CardContent>
            </Card>
          </TabsContent>

          {/* Achievements Tab */}
          <TabsContent value="achievements" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="w-5 h-5" />
                  Achievements
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  {unlockedAchievements} of {achievements.length} unlocked
                </p>
              </CardHeader>
              <CardContent>
                <AchievementGrid 
                  achievements={achievements}
                  onAchievementClick={onAchievementClick}
                />
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-sm font-medium">Time Range:</span>
              <div className="flex gap-1">
                {(['week', 'month', 'year'] as const).map((range) => (
                  <Button
                    key={range}
                    variant={selectedTimeRange === range ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedTimeRange(range)}
                  >
                    {range.charAt(0).toUpperCase() + range.slice(1)}
                  </Button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Study Statistics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-sm">Total Study Time</span>
                      <span className="text-sm font-medium">
                        {Math.round(totalStudyTime / 60)}h {totalStudyTime % 60}m
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Average Accuracy</span>
                      <span className="text-sm font-medium">{averageAccuracy.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Sessions Completed</span>
                      <span className="text-sm font-medium">{recentSessions.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">XP Gained</span>
                      <span className="text-sm font-medium">
                        {recentSessions.reduce((sum, s) => sum + s.xpGained, 0)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Performance Trends</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {recentSessions.slice(0, 5).map((session, index) => (
                      <div key={session.id} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full" />
                          <span className="text-sm">
                            {session.date.toLocaleDateString()}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary">{session.duration}m</Badge>
                          <Badge variant="outline">{session.accuracy}%</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Activity Tab */}
          <TabsContent value="activity" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ActivityFeed sessions={recentSessions} achievements={achievements} />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </TooltipProvider>
  )
}

// Skills Tree Component
const SkillTree: React.FC<{
  skills: SkillNode[]
  onSkillClick?: (skill: SkillNode) => void
  hoveredSkill: string | null
  onSkillHover: (skillId: string | null) => void
}> = ({ skills, onSkillClick, hoveredSkill, onSkillHover }) => {
  return (
    <div className="relative min-h-[400px] p-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg">
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {skills.map((skill) => (
          <Tooltip key={skill.id}>
            <TooltipTrigger asChild>
              <div
                className={`relative p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  skill.isCompleted
                    ? 'bg-green-50 border-green-200 text-green-800'
                    : skill.isUnlocked
                    ? 'bg-white border-blue-200 hover:border-blue-300'
                    : 'bg-gray-50 border-gray-200 opacity-60 cursor-not-allowed'
                } ${hoveredSkill === skill.id ? 'scale-105 shadow-lg' : ''}`}
                onClick={() => skill.isUnlocked && onSkillClick?.(skill)}
                onMouseEnter={() => onSkillHover(skill.id)}
                onMouseLeave={() => onSkillHover(null)}
              >
                <div className="flex items-center gap-2 mb-2">
                  {skill.isCompleted ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : skill.isUnlocked ? (
                    skill.icon
                  ) : (
                    <Lock className="w-5 h-5 text-gray-400" />
                  )}
                  <span className="font-medium text-sm">{skill.name}</span>
                </div>
                
                <div className="text-xs text-muted-foreground mb-2">
                  Level {skill.level} / {skill.maxLevel}
                </div>
                
                <Progress value={skill.progress} className="h-2" />
                
                {skill.isCompleted && (
                  <div className="absolute -top-2 -right-2">
                    <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                  </div>
                )}
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <div className="max-w-xs">
                <p className="font-medium">{skill.name}</p>
                <p className="text-sm text-muted-foreground">{skill.description}</p>
                {skill.prerequisites.length > 0 && (
                  <p className="text-xs mt-1">
                    Prerequisites: {skill.prerequisites.join(', ')}
                  </p>
                )}
                {skill.rewards.length > 0 && (
                  <p className="text-xs mt-1">
                    Rewards: {skill.rewards.join(', ')}
                  </p>
                )}
              </div>
            </TooltipContent>
          </Tooltip>
        ))}
      </div>
    </div>
  )
}

// Achievement Grid Component
const AchievementGrid: React.FC<{
  achievements: Achievement[]
  onAchievementClick?: (achievement: Achievement) => void
}> = ({ achievements, onAchievementClick }) => {
  const getRarityColor = (rarity: Achievement['rarity']) => {
    switch (rarity) {
      case 'common': return 'border-gray-300 bg-gray-50'
      case 'rare': return 'border-blue-300 bg-blue-50'
      case 'epic': return 'border-purple-300 bg-purple-50'
      case 'legendary': return 'border-yellow-300 bg-yellow-50'
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {achievements.map((achievement) => (
        <Tooltip key={achievement.id}>
          <TooltipTrigger asChild>
            <div
              className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                achievement.isUnlocked
                  ? getRarityColor(achievement.rarity)
                  : 'bg-gray-50 border-gray-200 opacity-60'
              } hover:scale-105`}
              onClick={() => onAchievementClick?.(achievement)}
            >
              <div className="flex items-center gap-2 mb-2">
                {achievement.isUnlocked ? (
                  achievement.icon
                ) : (
                  <Lock className="w-5 h-5 text-gray-400" />
                )}
                <span className="font-medium text-sm">{achievement.title}</span>
              </div>
              
              <p className="text-xs text-muted-foreground mb-2">
                {achievement.description}
              </p>
              
              <div className="flex items-center justify-between">
                <Badge variant="secondary" className="text-xs">
                  {achievement.rarity}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {achievement.points} XP
                </span>
              </div>
              
              {achievement.isUnlocked && achievement.unlockedAt && (
                <p className="text-xs text-muted-foreground mt-1">
                  Unlocked {achievement.unlockedAt.toLocaleDateString()}
                </p>
              )}
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <div className="max-w-xs">
              <p className="font-medium">{achievement.title}</p>
              <p className="text-sm text-muted-foreground">{achievement.description}</p>
              <p className="text-xs mt-1">Category: {achievement.category}</p>
              <p className="text-xs">Rarity: {achievement.rarity}</p>
            </div>
          </TooltipContent>
        </Tooltip>
      ))}
    </div>
  )
}

// Activity Feed Component
const ActivityFeed: React.FC<{
  sessions: StudySession[]
  achievements: Achievement[]
}> = ({ sessions, achievements }) => {
  const recentAchievements = achievements
    .filter(a => a.isUnlocked && a.unlockedAt)
    .sort((a, b) => (b.unlockedAt!.getTime() - a.unlockedAt!.getTime()))
    .slice(0, 5)

  const combinedActivity = [
    ...sessions.map(s => ({ type: 'session' as const, data: s, date: s.date })),
    ...recentAchievements.map(a => ({ type: 'achievement' as const, data: a, date: a.unlockedAt! }))
  ].sort((a, b) => b.date.getTime() - a.date.getTime()).slice(0, 10)

  return (
    <div className="space-y-4">
      {combinedActivity.map((activity, index) => (
        <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
          {activity.type === 'session' ? (
            <>
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <Play className="w-4 h-4 text-blue-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">Study Session Completed</p>
                <p className="text-xs text-muted-foreground">
                  {activity.data.duration} minutes • {activity.data.accuracy}% accuracy
                </p>
              </div>
              <div className="text-xs text-muted-foreground">
                {activity.date.toLocaleDateString()}
              </div>
            </>
          ) : (
            <>
              <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                <Award className="w-4 h-4 text-yellow-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">Achievement Unlocked</p>
                <p className="text-xs text-muted-foreground">
                  {activity.data.title}
                </p>
              </div>
              <div className="text-xs text-muted-foreground">
                {activity.date.toLocaleDateString()}
              </div>
            </>
          )}
        </div>
      ))}
    </div>
  )
}

export default ProgressTracking