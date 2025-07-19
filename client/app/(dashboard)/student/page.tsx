"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AIChatInterface } from "@/components/ai/ai-chat-interface"
import { ProgressTracker } from "@/components/learning/progress-tracker"
import { 
  BookOpen, 
  Play, 
  Clock, 
  Target, 
  Trophy,
  TrendingUp,
  Calendar,
  Star,
  MessageSquare,
  CheckCircle,
  AlertCircle,
  Users,
  Award,
  Zap,
  BarChart3,
  BookMarked,
  Download,
  Share2,
  Settings,
  Bell,
  Search
} from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { toast } from "@/components/ui/use-toast"
import Link from "next/link"

interface StudentDashboardData {
  profile: {
    level: number
    xp: number
    nextLevelXp: number
    streak: number
    totalTimeSpent: number
    coursesCompleted: number
    achievementsCount: number
  }
  activeCourses: Array<{
    id: string
    title: string
    description: string
    progress: number
    nextLesson: string
    instructor: string
    estimatedTime: number
    dueDate?: string
    status: 'active' | 'completed' | 'overdue'
  }>
  upcomingDeadlines: Array<{
    id: string
    title: string
    type: 'assignment' | 'quiz' | 'project' | 'discussion'
    courseTitle: string
    dueDate: string
    priority: 'high' | 'medium' | 'low'
  }>
  recentActivity: Array<{
    id: string
    type: 'lesson_completed' | 'quiz_taken' | 'assignment_submitted' | 'discussion_posted'
    title: string
    courseTitle: string
    timestamp: string
    score?: number
  }>
  recommendations: Array<{
    id: string
    type: 'course' | 'skill' | 'practice'
    title: string
    description: string
    reason: string
    difficulty: 'beginner' | 'intermediate' | 'advanced'
  }>
  progressData: any // Will be used with ProgressTracker component
}

export default function StudentPortal() {
  const { user } = useAuth()
  const [dashboardData, setDashboardData] = useState<StudentDashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [showAIChat, setShowAIChat] = useState(false)
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Mock data - replace with actual API call
      const mockData: StudentDashboardData = {
        profile: {
          level: 5,
          xp: 2450,
          nextLevelXp: 3000,
          streak: 7,
          totalTimeSpent: 2340, // minutes
          coursesCompleted: 3,
          achievementsCount: 12
        },
        activeCourses: [
          {
            id: '1',
            title: 'Advanced JavaScript Programming',
            description: 'Master modern JavaScript concepts and frameworks',
            progress: 75,
            nextLesson: 'Async/Await Patterns',
            instructor: 'Dr. Sarah Johnson',
            estimatedTime: 45,
            dueDate: '2024-01-20',
            status: 'active'
          },
          {
            id: '2',
            title: 'Data Structures & Algorithms',
            description: 'Fundamental computer science concepts',
            progress: 45,
            nextLesson: 'Binary Search Trees',
            instructor: 'Prof. Michael Chen',
            estimatedTime: 60,
            status: 'active'
          },
          {
            id: '3',
            title: 'UI/UX Design Principles',
            description: 'Create beautiful and functional user interfaces',
            progress: 90,
            nextLesson: 'Accessibility Guidelines',
            instructor: 'Emma Rodriguez',
            estimatedTime: 30,
            dueDate: '2024-01-15',
            status: 'active'
          }
        ],
        upcomingDeadlines: [
          {
            id: '1',
            title: 'Final Project Submission',
            type: 'project',
            courseTitle: 'Advanced JavaScript Programming',
            dueDate: '2024-01-20',
            priority: 'high'
          },
          {
            id: '2',
            title: 'Quiz: Tree Traversal',
            type: 'quiz',
            courseTitle: 'Data Structures & Algorithms',
            dueDate: '2024-01-18',
            priority: 'medium'
          }
        ],
        recentActivity: [
          {
            id: '1',
            type: 'lesson_completed',
            title: 'Promise Handling',
            courseTitle: 'Advanced JavaScript Programming',
            timestamp: '2024-01-10T10:30:00Z',
            score: 95
          },
          {
            id: '2',
            type: 'quiz_taken',
            title: 'Array Methods Quiz',
            courseTitle: 'Advanced JavaScript Programming',
            timestamp: '2024-01-09T14:15:00Z',
            score: 88
          }
        ],
        recommendations: [
          {
            id: '1',
            type: 'course',
            title: 'React Advanced Patterns',
            description: 'Learn advanced React patterns and best practices',
            reason: 'Based on your JavaScript progress',
            difficulty: 'advanced'
          },
          {
            id: '2',
            type: 'practice',
            title: 'Algorithm Practice Problems',
            description: 'Strengthen your problem-solving skills',
            reason: 'Complement your DS&A course',
            difficulty: 'intermediate'
          }
        ],
        progressData: {
          overall: {
            percentage: 68,
            completedItems: 34,
            totalItems: 50,
            timeSpent: 2340,
            streak: 7,
            level: 5,
            xp: 2450,
            nextLevelXp: 3000
          },
          skills: [
            {
              id: '1',
              name: 'JavaScript',
              category: 'Programming',
              level: 4,
              progress: 75,
              maxLevel: 5,
              prerequisites: [],
              unlocked: true,
              mastery: 'advanced'
            },
            {
              id: '2',
              name: 'Data Structures',
              category: 'Computer Science',
              level: 2,
              progress: 45,
              maxLevel: 5,
              prerequisites: ['JavaScript'],
              unlocked: true,
              mastery: 'intermediate'
            }
          ],
          modules: [
            {
              id: '1',
              title: 'Advanced JavaScript Programming',
              description: 'Master modern JavaScript concepts',
              progress: 75,
              status: 'in_progress',
              estimatedTime: 480,
              completedTime: 360,
              lessons: []
            }
          ],
          achievements: [
            {
              id: '1',
              title: 'First Steps',
              description: 'Complete your first lesson',
              icon: '🎯',
              category: 'completion',
              earned: true,
              earnedAt: new Date('2024-01-01')
            },
            {
              id: '2',
              title: 'Speed Learner',
              description: 'Complete 10 lessons in one day',
              icon: '⚡',
              category: 'streak',
              earned: false,
              progress: 7,
              target: 10
            }
          ],
          timeline: [
            {
              id: '1',
              type: 'lesson_completed',
              title: 'Promise Handling',
              description: 'Completed with 95% score',
              timestamp: new Date('2024-01-10T10:30:00Z'),
              points: 100
            }
          ]
        }
      }
      
      setDashboardData(mockData)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load dashboard data",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleCourseClick = (courseId: string) => {
    setSelectedCourse(courseId)
    // Navigate to course or open course details
  }

  const handleContinueLearning = (courseId: string) => {
    // Navigate to next lesson
    window.location.href = `/student/courses/${courseId}/continue`
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  const profile = dashboardData?.profile || {
    level: 1,
    xp: 0,
    nextLevelXp: 1000,
    streak: 0,
    totalTimeSpent: 0,
    coursesCompleted: 0,
    achievementsCount: 0
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Learning Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {user?.first_name || user?.username}! Continue your learning journey.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline"
            onClick={() => setShowAIChat(true)}
          >
            <MessageSquare className="w-4 h-4 mr-2" />
            AI Tutor
          </Button>
          <Button asChild>
            <Link href="/student/courses">
              <BookOpen className="w-4 h-4 mr-2" />
              Browse Courses
            </Link>
          </Button>
        </div>
      </div>

      {/* Profile Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Level</CardTitle>
            <Star className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{profile.level}</div>
            <div className="space-y-1">
              <Progress value={(profile.xp / profile.nextLevelXp) * 100} className="h-2" />
              <p className="text-xs text-muted-foreground">
                {profile.xp}/{profile.nextLevelXp} XP
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Streak</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{profile.streak}</div>
            <p className="text-xs text-muted-foreground">
              days in a row
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Time Spent</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Math.floor(profile.totalTimeSpent / 60)}h</div>
            <p className="text-xs text-muted-foreground">
              {profile.totalTimeSpent % 60}m total learning time
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Achievements</CardTitle>
            <Trophy className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{profile.achievementsCount}</div>
            <p className="text-xs text-muted-foreground">
              badges earned
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="courses">My Courses</TabsTrigger>
          <TabsTrigger value="progress">Progress</TabsTrigger>
          <TabsTrigger value="achievements">Achievements</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Active Courses */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5" />
                  Continue Learning
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {dashboardData?.activeCourses?.slice(0, 3).map((course) => (
                  <div key={course.id} className="p-3 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{course.title}</h4>
                      <Badge variant={course.status === 'overdue' ? 'destructive' : 'default'}>
                        {course.progress}%
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      Next: {course.nextLesson}
                    </p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        <span>{course.estimatedTime}min</span>
                      </div>
                      <Button size="sm" onClick={() => handleContinueLearning(course.id)}>
                        <Play className="w-3 h-3 mr-1" />
                        Continue
                      </Button>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Upcoming Deadlines */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Upcoming Deadlines
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {dashboardData?.upcomingDeadlines?.slice(0, 3).map((deadline) => (
                  <div key={deadline.id} className="flex items-center justify-between p-3 rounded-lg border">
                    <div className="flex-1">
                      <h4 className="font-medium">{deadline.title}</h4>
                      <p className="text-sm text-muted-foreground">{deadline.courseTitle}</p>
                      <p className="text-xs text-muted-foreground">
                        Due: {new Date(deadline.dueDate).toLocaleDateString()}
                      </p>
                    </div>
                    <Badge variant={deadline.priority === 'high' ? 'destructive' : 'default'}>
                      {deadline.priority}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* AI Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Recommended for You
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 md:grid-cols-2">
                {dashboardData?.recommendations?.map((rec) => (
                  <div key={rec.id} className="p-3 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{rec.title}</h4>
                      <Badge variant="outline">{rec.difficulty}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{rec.description}</p>
                    <p className="text-xs text-blue-600 mb-2">💡 {rec.reason}</p>
                    <Button variant="outline" size="sm">
                      Learn More
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="courses" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {dashboardData?.activeCourses?.map((course) => (
              <Card key={course.id}>
                <CardHeader>
                  <CardTitle className="text-lg">{course.title}</CardTitle>
                  <CardDescription>{course.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between text-sm">
                      <span>Progress</span>
                      <span>{course.progress}%</span>
                    </div>
                    <Progress value={course.progress} className="h-2" />
                    
                    <div className="space-y-2 text-sm text-muted-foreground">
                      <div className="flex items-center gap-2">
                        <Users className="h-3 w-3" />
                        <span>Instructor: {course.instructor}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="h-3 w-3" />
                        <span>Next lesson: {course.estimatedTime}min</span>
                      </div>
                      {course.dueDate && (
                        <div className="flex items-center gap-2">
                          <Calendar className="h-3 w-3" />
                          <span>Due: {new Date(course.dueDate).toLocaleDateString()}</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        className="flex-1"
                        onClick={() => handleContinueLearning(course.id)}
                      >
                        <Play className="w-3 h-3 mr-1" />
                        Continue
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleCourseClick(course.id)}
                      >
                        View Details
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="progress" className="space-y-4">
          {dashboardData?.progressData && (
            <ProgressTracker 
              variant="linear"
              data={dashboardData.progressData}
              onModuleClick={handleCourseClick}
              showAchievements={false}
              showTimeline={false}
            />
          )}
        </TabsContent>

        <TabsContent value="achievements" className="space-y-4">
          {dashboardData?.progressData && (
            <ProgressTracker 
              variant="skill-tree"
              data={dashboardData.progressData}
              onModuleClick={handleCourseClick}
              showAchievements={true}
              showTimeline={true}
            />
          )}
        </TabsContent>
      </Tabs>

      {/* AI Chat Interface */}
      {showAIChat && (
        <AIChatInterface
          variant="overlay"
          context="student-learning"
          contextData={dashboardData}
          onClose={() => setShowAIChat(false)}
        />
      )}
    </div>
  )
}