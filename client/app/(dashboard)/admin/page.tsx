"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { DataTable } from "@/components/shared/data-table"
import { 
  Users, 
  BookOpen, 
  TrendingUp, 
  Activity,
  Settings,
  Shield,
  Database,
  BarChart3,
  UserPlus,
  UserMinus,
  AlertTriangle,
  CheckCircle,
  Clock,
  Server,
  Monitor,
  Globe,
  Zap,
  HardDrive,
  Cpu,
  Wifi,
  Download,
  Upload,
  RefreshCw,
  Search,
  Filter,
  MoreHorizontal,
  Edit,
  Trash2,
  Eye,
  Key,
  Mail,
  Bell,
  Calendar,
  FileText,
  Archive,
  Star,
  Target,
  Award
} from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { toast } from "@/components/ui/use-toast"

interface AdminDashboardData {
  systemStats: {
    totalUsers: number
    activeUsers: number
    totalCourses: number
    activeCourses: number
    totalLessons: number
    completionRate: number
    averageRating: number
    systemUptime: number
  }
  userMetrics: {
    newUsersToday: number
    newUsersThisWeek: number
    newUsersThisMonth: number
    activeUsersToday: number
    usersByRole: {
      students: number
      trainers: number
      courseManagers: number
      sales: number
      admins: number
    }
  }
  courseMetrics: {
    coursesCreatedToday: number
    coursesCreatedThisWeek: number
    coursesCreatedThisMonth: number
    averageCompletionTime: number
    topPerformingCourses: Array<{
      id: string
      title: string
      completionRate: number
      averageRating: number
      enrolledStudents: number
    }>
  }
  systemHealth: {
    serverStatus: 'healthy' | 'warning' | 'critical'
    databaseStatus: 'healthy' | 'warning' | 'critical'
    apiResponseTime: number
    memoryUsage: number
    cpuUsage: number
    diskUsage: number
    activeConnections: number
  }
  recentActivity: Array<{
    id: string
    type: 'user_registered' | 'course_created' | 'lesson_completed' | 'system_alert'
    description: string
    timestamp: string
    severity: 'info' | 'warning' | 'error'
    userId?: string
    userName?: string
  }>
  users: Array<{
    id: string
    username: string
    email: string
    firstName: string
    lastName: string
    role: string
    status: 'active' | 'inactive' | 'suspended'
    lastLogin: string
    coursesCompleted: number
    totalTimeSpent: number
    createdAt: string
  }>
  courses: Array<{
    id: string
    title: string
    instructor: string
    status: 'draft' | 'published' | 'archived'
    enrolledStudents: number
    completionRate: number
    averageRating: number
    createdAt: string
    lastUpdated: string
  }>
}

export default function AdminPortal() {
  const { user } = useAuth()
  const [dashboardData, setDashboardData] = useState<AdminDashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState("overview")

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Mock data - replace with actual API call
      const mockData: AdminDashboardData = {
        systemStats: {
          totalUsers: 1247,
          activeUsers: 856,
          totalCourses: 89,
          activeCourses: 67,
          totalLessons: 1340,
          completionRate: 73.5,
          averageRating: 4.2,
          systemUptime: 99.8
        },
        userMetrics: {
          newUsersToday: 23,
          newUsersThisWeek: 156,
          newUsersThisMonth: 634,
          activeUsersToday: 342,
          usersByRole: {
            students: 1089,
            trainers: 78,
            courseManagers: 45,
            sales: 23,
            admins: 12
          }
        },
        courseMetrics: {
          coursesCreatedToday: 3,
          coursesCreatedThisWeek: 12,
          coursesCreatedThisMonth: 45,
          averageCompletionTime: 2.5,
          topPerformingCourses: [
            {
              id: '1',
              title: 'Introduction to Programming',
              completionRate: 89,
              averageRating: 4.7,
              enrolledStudents: 234
            },
            {
              id: '2',
              title: 'Data Science Fundamentals',
              completionRate: 82,
              averageRating: 4.5,
              enrolledStudents: 178
            }
          ]
        },
        systemHealth: {
          serverStatus: 'healthy',
          databaseStatus: 'healthy',
          apiResponseTime: 145,
          memoryUsage: 68,
          cpuUsage: 23,
          diskUsage: 45,
          activeConnections: 1247
        },
        recentActivity: [
          {
            id: '1',
            type: 'user_registered',
            description: 'New user John Doe registered',
            timestamp: '2024-01-10T10:30:00Z',
            severity: 'info',
            userId: '1',
            userName: 'John Doe'
          },
          {
            id: '2',
            type: 'course_created',
            description: 'Course "Advanced React" created by Jane Smith',
            timestamp: '2024-01-10T09:15:00Z',
            severity: 'info',
            userId: '2',
            userName: 'Jane Smith'
          }
        ],
        users: [
          {
            id: '1',
            username: 'john.doe',
            email: 'john.doe@example.com',
            firstName: 'John',
            lastName: 'Doe',
            role: 'student',
            status: 'active',
            lastLogin: '2024-01-10T08:30:00Z',
            coursesCompleted: 3,
            totalTimeSpent: 1440,
            createdAt: '2024-01-01T00:00:00Z'
          }
        ],
        courses: [
          {
            id: '1',
            title: 'Introduction to Programming',
            instructor: 'Dr. Sarah Johnson',
            status: 'published',
            enrolledStudents: 234,
            completionRate: 89,
            averageRating: 4.7,
            createdAt: '2024-01-01T00:00:00Z',
            lastUpdated: '2024-01-09T12:00:00Z'
          }
        ]
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

  const handleUserAction = (userId: string, action: string) => {
    // Handle user actions (suspend, activate, delete, etc.)
    toast({
      title: "Action Completed",
      description: `User ${action} successfully`
    })
  }

  const handleCourseAction = (courseId: string, action: string) => {
    // Handle course actions (publish, archive, delete, etc.)
    toast({
      title: "Action Completed",
      description: `Course ${action} successfully`
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  const systemStats = dashboardData?.systemStats || {
    totalUsers: 0,
    activeUsers: 0,
    totalCourses: 0,
    activeCourses: 0,
    totalLessons: 0,
    completionRate: 0,
    averageRating: 0,
    systemUptime: 0
  }
  
  const userMetrics = dashboardData?.userMetrics || {
    newUsersToday: 0,
    newUsersThisWeek: 0,
    newUsersThisMonth: 0,
    activeUsersToday: 0,
    usersByRole: {
      students: 0,
      trainers: 0,
      courseManagers: 0,
      sales: 0,
      admins: 0
    }
  }
  
  const courseMetrics = dashboardData?.courseMetrics || {
    coursesCreatedToday: 0,
    coursesCreatedThisWeek: 0,
    coursesCreatedThisMonth: 0,
    averageCompletionTime: 0,
    topPerformingCourses: []
  }
  
  const systemHealth = dashboardData?.systemHealth || {
    serverStatus: 'healthy' as const,
    databaseStatus: 'healthy' as const,
    apiResponseTime: 0,
    memoryUsage: 0,
    cpuUsage: 0,
    diskUsage: 0,
    activeConnections: 0
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Admin Portal</h1>
          <p className="text-muted-foreground">
            System administration and platform management
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export Data
          </Button>
          <Button variant="outline">
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </Button>
          <Button>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* System Health Alert */}
      {systemHealth.serverStatus !== 'healthy' && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-500" />
              <span className="font-medium">System Health Warning</span>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Server status: {systemHealth.serverStatus} | Database status: {systemHealth.databaseStatus}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats.totalUsers}</div>
            <p className="text-xs text-muted-foreground">
              {systemStats.activeUsers} active users
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Courses</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats.totalCourses}</div>
            <p className="text-xs text-muted-foreground">
              {systemStats.activeCourses} published courses
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completion Rate</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats.completionRate}%</div>
            <p className="text-xs text-muted-foreground">
              Average across all courses
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Uptime</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats.systemUptime}%</div>
            <p className="text-xs text-muted-foreground">
              Last 30 days
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="courses">Courses</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* User Growth */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  User Growth
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Today</span>
                    <Badge variant="secondary">+{userMetrics.newUsersToday}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">This Week</span>
                    <Badge variant="secondary">+{userMetrics.newUsersThisWeek}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">This Month</span>
                    <Badge variant="secondary">+{userMetrics.newUsersThisMonth}</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Course Performance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Top Performing Courses
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {courseMetrics.topPerformingCourses.map((course) => (
                    <div key={course.id} className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-medium">{course.title}</p>
                        <p className="text-xs text-muted-foreground">
                          {course.enrolledStudents} students
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{course.completionRate}%</Badge>
                        <div className="flex items-center gap-1">
                          <Star className="h-3 w-3 text-yellow-500" />
                          <span className="text-xs">{course.averageRating}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* System Health */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Monitor className="h-5 w-5" />
                System Health
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">CPU Usage</span>
                    <span className="text-sm font-medium">{systemHealth.cpuUsage}%</span>
                  </div>
                  <Progress value={systemHealth.cpuUsage} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Memory</span>
                    <span className="text-sm font-medium">{systemHealth.memoryUsage}%</span>
                  </div>
                  <Progress value={systemHealth.memoryUsage} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Disk Usage</span>
                    <span className="text-sm font-medium">{systemHealth.diskUsage}%</span>
                  </div>
                  <Progress value={systemHealth.diskUsage} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">API Response</span>
                    <span className="text-sm font-medium">{systemHealth.apiResponseTime}ms</span>
                  </div>
                  <Progress value={systemHealth.apiResponseTime / 10} className="h-2" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Recent Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {dashboardData?.recentActivity?.map((activity) => (
                  <div key={activity.id} className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      activity.severity === 'error' ? 'bg-red-500' : 
                      activity.severity === 'warning' ? 'bg-yellow-500' : 
                      'bg-green-500'
                    }`} />
                    <div className="flex-1">
                      <p className="text-sm">{activity.description}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(activity.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="users" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">User Management</h2>
            <div className="flex items-center gap-2">
              <Button variant="outline">
                <Download className="w-4 h-4 mr-2" />
                Export Users
              </Button>
              <Button>
                <UserPlus className="w-4 h-4 mr-2" />
                Add User
              </Button>
            </div>
          </div>

          {/* User Statistics */}
          <div className="grid gap-4 md:grid-cols-5">
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold">{userMetrics.usersByRole.students}</div>
                  <p className="text-sm text-muted-foreground">Students</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold">{userMetrics.usersByRole.trainers}</div>
                  <p className="text-sm text-muted-foreground">Trainers</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold">{userMetrics.usersByRole.courseManagers}</div>
                  <p className="text-sm text-muted-foreground">Course Managers</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold">{userMetrics.usersByRole.sales}</div>
                  <p className="text-sm text-muted-foreground">Sales</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold">{userMetrics.usersByRole.admins}</div>
                  <p className="text-sm text-muted-foreground">Admins</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Users Table */}
          <Card>
            <CardHeader>
              <CardTitle>All Users</CardTitle>
              <CardDescription>
                Manage platform users and their permissions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">User Management Table</h3>
                <p className="text-muted-foreground mb-4">
                  Advanced user management table will be implemented here
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="courses" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Course Management</h2>
            <div className="flex items-center gap-2">
              <Button variant="outline">
                <Download className="w-4 h-4 mr-2" />
                Export Courses
              </Button>
              <Button>
                <BookOpen className="w-4 h-4 mr-2" />
                Add Course
              </Button>
            </div>
          </div>

          {/* Course Statistics */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold">{courseMetrics.coursesCreatedToday}</div>
                  <p className="text-sm text-muted-foreground">Created Today</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold">{courseMetrics.coursesCreatedThisWeek}</div>
                  <p className="text-sm text-muted-foreground">Created This Week</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold">{courseMetrics.averageCompletionTime}h</div>
                  <p className="text-sm text-muted-foreground">Average Completion</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Courses Table */}
          <Card>
            <CardHeader>
              <CardTitle>All Courses</CardTitle>
              <CardDescription>
                Manage platform courses and their content
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Course Management Table</h3>
                <p className="text-muted-foreground mb-4">
                  Advanced course management table will be implemented here
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="text-center py-8">
            <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Analytics Dashboard</h3>
            <p className="text-muted-foreground mb-4">
              Advanced analytics and reporting features will be implemented here
            </p>
          </div>
        </TabsContent>

        <TabsContent value="system" className="space-y-4">
          <div className="text-center py-8">
            <Server className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">System Management</h3>
            <p className="text-muted-foreground mb-4">
              System configuration and management tools will be implemented here
            </p>
          </div>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <div className="text-center py-8">
            <Settings className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Platform Settings</h3>
            <p className="text-muted-foreground mb-4">
              Platform configuration and settings will be implemented here
            </p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}