"use client"

import React, { useState, useEffect, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  Brain, 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Target, 
  Clock,
  Users,
  Award,
  AlertTriangle,
  CheckCircle,
  Circle,
  ArrowUp,
  ArrowDown,
  Zap,
  Eye,
  BookOpen,
  MessageSquare,
  Calendar,
  Filter,
  Download,
  RefreshCw,
  Lightbulb,
  PieChart,
  LineChart,
  Activity,
  Star,
  Trophy,
  Flame
} from "lucide-react"

interface LearningAnalytics {
  student_id: number
  overall_progress: number
  learning_velocity: number
  engagement_score: number
  difficulty_adaptation: {
    current_level: string
    recommended_level: string
    confidence: number
  }
  performance_trends: {
    accuracy_trend: number[]
    response_time_trend: number[]
    engagement_trend: number[]
  }
  learning_patterns: {
    optimal_study_time: string
    preferred_content_type: string
    learning_style: string
    attention_span: number
  }
  skill_assessment: {
    skills: Array<{
      skill: string
      proficiency: number
      growth_rate: number
      last_practiced: string
    }>
  }
  recommendations: Array<{
    type: string
    message: string
    priority: string
    action: string
  }>
  achievements: Array<{
    id: string
    title: string
    description: string
    earned_date: string
    category: string
  }>
  study_streak: {
    current: number
    longest: number
    last_activity: string
  }
}

interface AILearningAnalyticsProps {
  studentId: number
  timeRange: "week" | "month" | "quarter" | "year"
  onRecommendationApply?: (recommendation: any) => void
  className?: string
}

export const AILearningAnalytics: React.FC<AILearningAnalyticsProps> = ({
  studentId,
  timeRange = "month",
  onRecommendationApply,
  className = ""
}) => {
  const [analytics, setAnalytics] = useState<LearningAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedMetric, setSelectedMetric] = useState("overall")
  const [activeTab, setActiveTab] = useState("overview")

  // Mock data for demonstration
  const mockAnalytics: LearningAnalytics = useMemo(() => ({
    student_id: studentId,
    overall_progress: 75,
    learning_velocity: 1.2,
    engagement_score: 85,
    difficulty_adaptation: {
      current_level: "intermediate",
      recommended_level: "intermediate",
      confidence: 0.82
    },
    performance_trends: {
      accuracy_trend: [65, 70, 75, 78, 80, 82, 85],
      response_time_trend: [45, 42, 38, 35, 32, 30, 28],
      engagement_trend: [70, 75, 80, 85, 83, 87, 90]
    },
    learning_patterns: {
      optimal_study_time: "morning",
      preferred_content_type: "interactive",
      learning_style: "visual",
      attention_span: 25
    },
    skill_assessment: {
      skills: [
        { skill: "Grammar", proficiency: 82, growth_rate: 0.15, last_practiced: "2 hours ago" },
        { skill: "Vocabulary", proficiency: 76, growth_rate: 0.12, last_practiced: "1 day ago" },
        { skill: "Pronunciation", proficiency: 68, growth_rate: 0.08, last_practiced: "3 days ago" },
        { skill: "Listening", proficiency: 79, growth_rate: 0.11, last_practiced: "1 hour ago" },
        { skill: "Speaking", proficiency: 71, growth_rate: 0.09, last_practiced: "2 days ago" },
        { skill: "Reading", proficiency: 88, growth_rate: 0.06, last_practiced: "5 hours ago" },
        { skill: "Writing", proficiency: 74, growth_rate: 0.13, last_practiced: "1 day ago" }
      ]
    },
    recommendations: [
      {
        type: "difficulty_adjustment",
        message: "Consider increasing difficulty for Grammar exercises to maintain challenge",
        priority: "medium",
        action: "adjust_difficulty"
      },
      {
        type: "study_schedule",
        message: "Schedule Pronunciation practice sessions during your optimal morning hours",
        priority: "high",
        action: "schedule_practice"
      },
      {
        type: "content_type",
        message: "Add more visual learning materials based on your learning style preference",
        priority: "medium",
        action: "add_visual_content"
      }
    ],
    achievements: [
      {
        id: "streak_7",
        title: "Week Warrior",
        description: "Completed 7 consecutive days of study",
        earned_date: "2024-01-15",
        category: "consistency"
      },
      {
        id: "grammar_master",
        title: "Grammar Master",
        description: "Achieved 85% accuracy in grammar exercises",
        earned_date: "2024-01-14",
        category: "skill"
      },
      {
        id: "speed_demon",
        title: "Speed Demon",
        description: "Improved response time by 50%",
        earned_date: "2024-01-13",
        category: "performance"
      }
    ],
    study_streak: {
      current: 12,
      longest: 23,
      last_activity: "2 hours ago"
    }
  }), [studentId])

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true)
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000))
        setAnalytics(mockAnalytics)
      } catch (error) {
        console.error("Failed to fetch analytics:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
  }, [studentId, timeRange, mockAnalytics])

  const getProgressColor = (value: number) => {
    if (value >= 80) return "text-green-600"
    if (value >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const getProgressBg = (value: number) => {
    if (value >= 80) return "bg-green-100"
    if (value >= 60) return "bg-yellow-100"
    return "bg-red-100"
  }

  const getTrendIcon = (value: number) => {
    if (value > 0) return <TrendingUp className="w-4 h-4 text-green-600" />
    if (value < 0) return <TrendingDown className="w-4 h-4 text-red-600" />
    return <Circle className="w-4 h-4 text-gray-600" />
  }

  const handleApplyRecommendation = (recommendation: any) => {
    onRecommendationApply?.(recommendation)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (!analytics) {
    return (
      <Alert className="border-red-200 bg-red-50">
        <AlertTriangle className="h-4 w-4 text-red-600" />
        <AlertDescription>
          Failed to load learning analytics. Please try again.
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Brain className="w-6 h-6 text-blue-600" />
            AI Learning Analytics
          </h2>
          <p className="text-muted-foreground">
            Intelligent insights into your learning progress and patterns
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={selectedMetric} onValueChange={setSelectedMetric}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="overall">Overall</SelectItem>
              <SelectItem value="skills">Skills</SelectItem>
              <SelectItem value="engagement">Engagement</SelectItem>
              <SelectItem value="performance">Performance</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Overall Progress</p>
                <p className={`text-2xl font-bold ${getProgressColor(analytics.overall_progress)}`}>
                  {analytics.overall_progress}%
                </p>
              </div>
              <div className={`p-2 rounded-full ${getProgressBg(analytics.overall_progress)}`}>
                <Target className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <Progress value={analytics.overall_progress} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Learning Velocity</p>
                <p className="text-2xl font-bold text-blue-600">
                  {analytics.learning_velocity}x
                </p>
              </div>
              <div className="p-2 rounded-full bg-blue-100">
                <Zap className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="flex items-center mt-2">
              {getTrendIcon(analytics.learning_velocity - 1)}
              <span className="text-sm text-muted-foreground ml-1">vs last period</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Engagement Score</p>
                <p className={`text-2xl font-bold ${getProgressColor(analytics.engagement_score)}`}>
                  {analytics.engagement_score}%
                </p>
              </div>
              <div className={`p-2 rounded-full ${getProgressBg(analytics.engagement_score)}`}>
                <Activity className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <Progress value={analytics.engagement_score} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Study Streak</p>
                <p className="text-2xl font-bold text-orange-600">
                  {analytics.study_streak.current} days
                </p>
              </div>
              <div className="p-2 rounded-full bg-orange-100">
                <Flame className="w-6 h-6 text-orange-600" />
              </div>
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              Best: {analytics.study_streak.longest} days
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">
            <Eye className="w-4 h-4 mr-2" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="skills">
            <BookOpen className="w-4 h-4 mr-2" />
            Skills Analysis
          </TabsTrigger>
          <TabsTrigger value="recommendations">
            <Lightbulb className="w-4 h-4 mr-2" />
            AI Recommendations
          </TabsTrigger>
          <TabsTrigger value="achievements">
            <Trophy className="w-4 h-4 mr-2" />
            Achievements
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Performance Trends */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LineChart className="w-5 h-5" />
                  Performance Trends
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Accuracy</span>
                      <span className="text-sm text-muted-foreground">
                        {analytics.performance_trends.accuracy_trend.slice(-1)[0]}%
                      </span>
                    </div>
                    <div className="h-20 bg-gray-50 rounded-lg flex items-end justify-between p-2">
                      {analytics.performance_trends.accuracy_trend.map((value, index) => (
                        <div
                          key={index}
                          className="bg-blue-600 rounded-t"
                          style={{ height: `${value}%`, width: '10px' }}
                        />
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Response Time (s)</span>
                      <span className="text-sm text-muted-foreground">
                        {analytics.performance_trends.response_time_trend.slice(-1)[0]}s
                      </span>
                    </div>
                    <div className="h-20 bg-gray-50 rounded-lg flex items-end justify-between p-2">
                      {analytics.performance_trends.response_time_trend.map((value, index) => (
                        <div
                          key={index}
                          className="bg-green-600 rounded-t"
                          style={{ height: `${(60 - value) / 60 * 100}%`, width: '10px' }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Learning Patterns */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="w-5 h-5" />
                  Learning Patterns
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Optimal Study Time</span>
                    <Badge variant="secondary">{analytics.learning_patterns.optimal_study_time}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Preferred Content</span>
                    <Badge variant="secondary">{analytics.learning_patterns.preferred_content_type}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Learning Style</span>
                    <Badge variant="secondary">{analytics.learning_patterns.learning_style}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Attention Span</span>
                    <Badge variant="secondary">{analytics.learning_patterns.attention_span} min</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Difficulty Adaptation */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Adaptive Difficulty System
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {analytics.difficulty_adaptation.current_level}
                    </div>
                    <div className="text-sm text-muted-foreground">Current Level</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {analytics.difficulty_adaptation.recommended_level}
                    </div>
                    <div className="text-sm text-muted-foreground">Recommended</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {Math.round(analytics.difficulty_adaptation.confidence * 100)}%
                    </div>
                    <div className="text-sm text-muted-foreground">Confidence</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Skills Analysis Tab */}
        <TabsContent value="skills" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analytics.skill_assessment.skills.map((skill, index) => (
              <Card key={index}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{skill.skill}</CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge variant={skill.proficiency >= 80 ? "default" : skill.proficiency >= 60 ? "secondary" : "destructive"}>
                        {skill.proficiency}%
                      </Badge>
                      {getTrendIcon(skill.growth_rate)}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium">Proficiency</span>
                        <span className="text-sm text-muted-foreground">{skill.proficiency}%</span>
                      </div>
                      <Progress value={skill.proficiency} />
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium">Growth Rate</span>
                        <span className="text-sm text-muted-foreground">
                          {skill.growth_rate > 0 ? '+' : ''}{(skill.growth_rate * 100).toFixed(1)}%
                        </span>
                      </div>
                      <Progress value={Math.abs(skill.growth_rate) * 100} />
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Last Practiced</span>
                      <span className="text-sm text-muted-foreground">{skill.last_practiced}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Recommendations Tab */}
        <TabsContent value="recommendations" className="space-y-6">
          <div className="space-y-4">
            {analytics.recommendations.map((rec, index) => (
              <Alert key={index} className={`border-blue-200 bg-blue-50 ${rec.priority === 'high' ? 'border-orange-200 bg-orange-50' : ''}`}>
                <Lightbulb className={`h-4 w-4 ${rec.priority === 'high' ? 'text-orange-600' : 'text-blue-600'}`} />
                <AlertDescription>
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium">{rec.message}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge variant={rec.priority === 'high' ? 'destructive' : 'secondary'}>
                          {rec.priority} priority
                        </Badge>
                        <Badge variant="outline">{rec.type}</Badge>
                      </div>
                    </div>
                    <Button
                      size="sm"
                      onClick={() => handleApplyRecommendation(rec)}
                      className="ml-4"
                    >
                      Apply
                    </Button>
                  </div>
                </AlertDescription>
              </Alert>
            ))}
          </div>
        </TabsContent>

        {/* Achievements Tab */}
        <TabsContent value="achievements" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analytics.achievements.map((achievement, index) => (
              <Card key={index}>
                <CardContent className="p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="p-2 rounded-full bg-yellow-100">
                      <Award className="w-6 h-6 text-yellow-600" />
                    </div>
                    <div>
                      <h4 className="font-medium">{achievement.title}</h4>
                      <p className="text-sm text-muted-foreground">{achievement.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <Badge variant="outline">{achievement.category}</Badge>
                    <span className="text-sm text-muted-foreground">
                      {new Date(achievement.earned_date).toLocaleDateString()}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default AILearningAnalytics