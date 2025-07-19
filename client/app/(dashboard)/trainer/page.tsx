"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { 
  BookOpen, 
  Users, 
  Calendar, 
  Clock, 
  TrendingUp, 
  Plus,
  Play,
  Pause,
  CheckCircle,
  AlertCircle,
  PlusCircle,
  Star,
  MessageSquare,
  Target,
  Award,
  Edit3,
  Eye,
  BarChart3
} from "lucide-react"
import { trainerService } from "@/lib/api-services"
import { useAuth } from "@/contexts/auth-context"
import { toast } from "@/components/ui/use-toast"
import Link from "next/link"

interface TrainerDashboardData {
  stats: {
    totalCourses: number
    activeCourses: number
    totalStudents: number
    completedCourses: number
    pendingReviews: number
    averageRating: number
  }
  upcomingLessons: Array<{
    id: string
    title: string
    courseTitle: string
    scheduledAt: string
    studentCount: number
    status: 'scheduled' | 'in_progress' | 'completed'
  }>
  recentCourses: Array<{
    id: string
    title: string
    description: string
    progress: number
    studentCount: number
    lastUpdated: string
    status: 'draft' | 'published' | 'archived'
  }>
  notifications: Array<{
    id: string
    type: 'feedback' | 'assignment' | 'system'
    message: string
    timestamp: string
    read: boolean
  }>
}

export default function TrainerPortal() {
  const { user } = useAuth()
  const [dashboardData, setDashboardData] = useState<TrainerDashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const data = await trainerService.getDashboard()
      setDashboardData(data)
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  const stats = dashboardData?.stats || {
    totalCourses: 0,
    activeCourses: 0,
    totalStudents: 0,
    completedCourses: 0,
    pendingReviews: 0,
    averageRating: 0
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Trainer Portal</h1>
          <p className="text-muted-foreground">
            Welcome back, {user?.first_name || user?.username}! Manage your courses and students.
          </p>
        </div>
        <div className="flex gap-2">
          <Button asChild>
            <Link href="/trainer/course-creator">
              <PlusCircle className="w-4 h-4 mr-2" />
              Create Course
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/trainer/content-library">
              <BookOpen className="w-4 h-4 mr-2" />
              Content Library
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Courses</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalCourses}</div>
            <p className="text-xs text-muted-foreground">
              {stats.activeCourses} active courses
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Students</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalStudents}</div>
            <p className="text-xs text-muted-foreground">
              Across all courses
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Reviews</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pendingReviews}</div>
            <p className="text-xs text-muted-foreground">
              Assignments to review
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Rating</CardTitle>
            <Star className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.averageRating.toFixed(1)}</div>
            <p className="text-xs text-muted-foreground">
              Student feedback
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="courses">My Courses</TabsTrigger>
          <TabsTrigger value="lessons">Upcoming Lessons</TabsTrigger>
          <TabsTrigger value="students">Student Progress</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Upcoming Lessons */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Upcoming Lessons
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {dashboardData?.upcomingLessons?.slice(0, 3).map((lesson) => (
                  <div key={lesson.id} className="flex items-center justify-between p-3 rounded-lg border">
                    <div className="flex-1">
                      <h4 className="font-medium">{lesson.title}</h4>
                      <p className="text-sm text-muted-foreground">{lesson.courseTitle}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Clock className="h-3 w-3 text-muted-foreground" />
                        <span className="text-xs text-muted-foreground">
                          {new Date(lesson.scheduledAt).toLocaleDateString()}
                        </span>
                        <Users className="h-3 w-3 text-muted-foreground ml-2" />
                        <span className="text-xs text-muted-foreground">
                          {lesson.studentCount} students
                        </span>
                      </div>
                    </div>
                    <Badge variant={lesson.status === 'scheduled' ? 'default' : 'secondary'}>
                      {lesson.status}
                    </Badge>
                  </div>
                ))}
                {(!dashboardData?.upcomingLessons || dashboardData.upcomingLessons.length === 0) && (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No upcoming lessons scheduled
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {dashboardData?.notifications?.slice(0, 3).map((notification) => (
                  <div key={notification.id} className="flex items-start gap-3 p-3 rounded-lg border">
                    <div className="flex-1">
                      <p className="text-sm">{notification.message}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(notification.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                    {!notification.read && (
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    )}
                  </div>
                ))}
                {(!dashboardData?.notifications || dashboardData.notifications.length === 0) && (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No recent activity
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="courses" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">My Courses</h2>
            <Button asChild>
              <Link href="/trainer/course-creator">
                <Plus className="w-4 h-4 mr-2" />
                Create New Course
              </Link>
            </Button>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {dashboardData?.recentCourses?.map((course) => (
              <Card key={course.id} className="relative">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <Badge variant={course.status === 'published' ? 'default' : 'secondary'}>
                      {course.status}
                    </Badge>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="sm" asChild>
                        <Link href={`/trainer/courses/${course.id}`}>
                          <Eye className="h-4 w-4" />
                        </Link>
                      </Button>
                      <Button variant="ghost" size="sm" asChild>
                        <Link href={`/trainer/course-creator/${course.id}`}>
                          <Edit3 className="h-4 w-4" />
                        </Link>
                      </Button>
                    </div>
                  </div>
                  <CardTitle className="text-lg">{course.title}</CardTitle>
                  <CardDescription>{course.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span>Progress</span>
                      <span>{course.progress}%</span>
                    </div>
                    <Progress value={course.progress} className="h-2" />
                    
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Users className="h-3 w-3" />
                        <span>{course.studentCount} students</span>
                      </div>
                      <span>Updated {new Date(course.lastUpdated).toLocaleDateString()}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {(!dashboardData?.recentCourses || dashboardData.recentCourses.length === 0) && (
            <Card className="p-8 text-center">
              <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No courses yet</h3>
              <p className="text-muted-foreground mb-4">
                Start creating your first course to engage with students
              </p>
              <Button asChild>
                <Link href="/trainer/course-creator">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Course
                </Link>
              </Button>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="lessons" className="space-y-4">
          <h2 className="text-xl font-semibold">Upcoming Lessons</h2>
          
          <div className="space-y-4">
            {dashboardData?.upcomingLessons?.map((lesson) => (
              <Card key={lesson.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{lesson.title}</CardTitle>
                      <CardDescription>{lesson.courseTitle}</CardDescription>
                    </div>
                    <Badge variant={lesson.status === 'scheduled' ? 'default' : 'secondary'}>
                      {lesson.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        <span>{new Date(lesson.scheduledAt).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        <span>{new Date(lesson.scheduledAt).toLocaleTimeString()}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Users className="h-3 w-3" />
                        <span>{lesson.studentCount} students</span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        View Details
                      </Button>
                      {lesson.status === 'scheduled' && (
                        <Button size="sm">
                          <Play className="w-4 h-4 mr-2" />
                          Start Lesson
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="students" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Student Progress</h2>
            <Button variant="outline" asChild>
              <Link href="/trainer/analytics">
                <BarChart3 className="w-4 h-4 mr-2" />
                View Analytics
              </Link>
            </Button>
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle>Progress Overview</CardTitle>
              <CardDescription>
                Track your students' performance across all courses
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <TrendingUp className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Student Analytics</h3>
                <p className="text-muted-foreground mb-4">
                  Detailed student progress tracking coming soon
                </p>
                <Button variant="outline" asChild>
                  <Link href="/trainer/students">
                    View All Students
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}