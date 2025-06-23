import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/auth_context';
import { 
  AcademicCapIcon,
  UsersIcon,
  ChartBarIcon,
  ChatBubbleLeftIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  PencilIcon,
  DocumentTextIcon,
  CalendarDaysIcon,
  StarIcon,
  TrophyIcon,
  ArrowTrendingUpIcon,
  BellIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  PlayIcon,
  PauseIcon,
  BookOpenIcon,
  UserGroupIcon,
  PlusIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';
import { 
  Button, 
  Card, 
  CardHeader, 
  CardBody, 
  Badge, 
  SearchInput, 
  Dropdown, 
  DropdownItem,
  Progress,
  Tooltip,
  Alert,
  Tabs
} from '../common/UIComponents';
import { LoadingSpinner, EmptyState, PageLoadingSkeleton } from '../common/LoadingStates';
import api from '../../services/api';

const TrainerDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // State management
  const [dashboardStats, setDashboardStats] = useState(null);
  const [activeClasses, setActiveClasses] = useState([]);
  const [studentProgress, setStudentProgress] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Mock API calls with fallback data until backend is available
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate loading
      
      // Mock dashboard stats
      setDashboardStats({
        active_classes: 6,
        classes_change: 12,
        total_students: 156,
        students_change: 8,
        avg_progress: 78,
        progress_change: 5,
        avg_engagement: 85,
        engagement_change: 3
      });
      
      // Mock active classes
      setActiveClasses([
        {
          id: 1,
          course_title: 'Business English for TechCorp',
          company_name: 'TechCorp Inc.',
          cefr_level: 'B2',
          status: 'active',
          total_students: 24,
          completed_lessons: 12,
          total_lessons: 20,
          next_session: 'Today 2:00 PM',
          engagement_score: 92,
          progress_percentage: 60,
          next_lesson_id: 'lesson_101',
          alerts: []
        },
        {
          id: 2,
          course_title: 'Financial Communication Skills',
          company_name: 'Global Finance Ltd.',
          cefr_level: 'B1',
          status: 'active',
          total_students: 18,
          completed_lessons: 8,
          total_lessons: 15,
          next_session: 'Tomorrow 10:00 AM',
          engagement_score: 76,
          progress_percentage: 53,
          next_lesson_id: 'lesson_201',
          alerts: ['Low engagement in last session']
        },
        {
          id: 3,
          course_title: 'Healthcare Communication',
          company_name: 'MedCare Solutions',
          cefr_level: 'A2',
          status: 'active',
          total_students: 15,
          completed_lessons: 5,
          total_lessons: 12,
          next_session: 'Friday 3:00 PM',
          engagement_score: 88,
          progress_percentage: 42,
          next_lesson_id: 'lesson_301',
          alerts: []
        }
      ]);
      
      // Mock student progress
      setStudentProgress([
        {
          name: 'John Smith',
          course_title: 'Business English for TechCorp',
          progress_percentage: 85,
          last_activity: '2 hours ago'
        },
        {
          name: 'Maria Garcia',
          course_title: 'Financial Communication Skills',
          progress_percentage: 72,
          last_activity: '1 day ago'
        },
        {
          name: 'Ahmed Hassan',
          course_title: 'Healthcare Communication',
          progress_percentage: 68,
          last_activity: '3 hours ago'
        },
        {
          name: 'Lisa Chen',
          course_title: 'Business English for TechCorp',
          progress_percentage: 91,
          last_activity: '30 min ago'
        },
        {
          name: 'Carlos Rodriguez',
          course_title: 'Financial Communication Skills',
          progress_percentage: 55,
          last_activity: '5 hours ago'
        }
      ]);
      
      // Mock recent activity
      setRecentActivity([
        {
          type: 'lesson_completed',
          title: 'Lesson completed',
          description: 'John Smith completed "Presentation Skills" lesson',
          timestamp: '2 hours ago'
        },
        {
          type: 'assignment_submitted',
          title: 'Assignment submitted',
          description: 'Maria Garcia submitted final project',
          timestamp: '4 hours ago'
        },
        {
          type: 'class_started',
          title: 'Class session started',
          description: 'Business English for TechCorp - Module 3',
          timestamp: '1 day ago'
        },
        {
          type: 'feedback_given',
          title: 'Feedback provided',
          description: 'You provided feedback to Ahmed Hassan',
          timestamp: '2 days ago'
        }
      ]);
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Set empty states on error
      setDashboardStats({
        active_classes: 0,
        classes_change: 0,
        total_students: 0,
        students_change: 0,
        avg_progress: 0,
        progress_change: 0,
        avg_engagement: 0,
        engagement_change: 0
      });
      setActiveClasses([]);
      setStudentProgress([]);
      setRecentActivity([]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = async (classId, action) => {
    try {
      // Mock API call until backend is available
      console.log(`Performing ${action} on class ${classId}`);
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API delay
      
      fetchDashboardData(); // Refresh data
    } catch (error) {
      console.error(`Error performing ${action}:`, error);
    }
  };

  const getProgressColor = (progress) => {
    if (progress >= 80) return 'text-green-700 bg-green-100';
    if (progress >= 60) return 'text-amber-700 bg-amber-100';
    return 'text-red-700 bg-red-100';
  };

  const getEngagementLevel = (engagement) => {
    if (engagement >= 80) return { level: 'High', color: 'text-green-600' };
    if (engagement >= 60) return { level: 'Medium', color: 'text-amber-600' };
    return { level: 'Low', color: 'text-red-600' };
  };

  const StatCard = ({ title, value, change, icon: Icon, color = 'primary', trend = null }) => (
    <Card variant="elevated" className="hover:shadow-xl transition-all duration-300">
      <CardBody>
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="body-sm text-neutral-600 mb-1">{title}</p>
            <div className="flex items-baseline space-x-3">
              <h3 className="heading-3xl text-neutral-900">{value}</h3>
              {change !== undefined && (
                <Badge 
                  variant={change >= 0 ? 'success' : 'error'}
                  className="animate-fade-in"
                >
                  {change >= 0 ? '+' : ''}{change}%
                </Badge>
              )}
            </div>
            {trend && (
              <div className="flex items-center mt-2 animate-slide-in">
                <ArrowTrendingUpIcon className="h-4 w-4 text-success-600 mr-1" />
                <span className="body-xs text-neutral-500">{trend}</span>
              </div>
            )}
          </div>
          <div className={`p-4 rounded-xl bg-gradient-${color} shadow-lg`}>
            <Icon className="h-8 w-8 text-white" />
          </div>
        </div>
      </CardBody>
    </Card>
  );

  const ClassCard = ({ classData }) => {
    const engagementInfo = getEngagementLevel(classData.engagement_score);
    
    return (
      <Card variant="interactive" className="border-l-4 border-l-primary-500 hover:border-l-primary-600 transition-all duration-300">
        <CardBody>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-3">
                <h3 className="heading-lg text-neutral-900 line-clamp-1">
                  {classData.course_title}
                </h3>
                <Badge variant="primary" size="sm">
                  {classData.cefr_level}
                </Badge>
                <Badge 
                  variant={classData.status === 'active' ? 'success' : 'neutral'}
                  size="sm"
                >
                  {classData.status.toUpperCase()}
                </Badge>
              </div>
              
              <p className="body-sm text-neutral-600 mb-4">{classData.company_name}</p>
              
              <div className="grid grid-cols-2 gap-4 body-sm text-neutral-600 mb-4">
                <div className="flex items-center space-x-2">
                  <UsersIcon className="h-4 w-4 text-neutral-400" />
                  <span>{classData.total_students} students</span>
                </div>
                <div className="flex items-center space-x-2">
                  <ClockIcon className="h-4 w-4 text-neutral-400" />
                  <span>{classData.completed_lessons}/{classData.total_lessons} lessons</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CalendarDaysIcon className="h-4 w-4 text-neutral-400" />
                  <span>Next: {classData.next_session}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <ChartBarIcon className="h-4 w-4 text-neutral-400" />
                  <span className={engagementInfo.color}>
                    {engagementInfo.level} Engagement
                  </span>
                </div>
              </div>

              <div className="mb-4">
                <Progress 
                  value={classData.progress_percentage} 
                  showLabel={true}
                  variant="primary"
                  className="animate-fade-in"
                />
              </div>

              {classData.alerts && classData.alerts.length > 0 && (
                <Alert variant="warning" className="mb-4">
                  {classData.alerts[0]}
                </Alert>
              )}
            </div>

            <div className="flex flex-col space-y-3 ml-6">
              <Tooltip content="View and manage class details">
                <Button
                  variant="primary"
                  size="sm"
                  icon={EyeIcon}
                  onClick={() => navigate(`/trainer/class/${classData.id}`)}
                  className="w-full"
                >
                  Manage Class
                </Button>
              </Tooltip>
              
              <Tooltip content={!classData.next_lesson_id ? "No lesson available" : "Start the next lesson"}>
                <Button
                  variant="secondary"
                  size="sm"
                  icon={PlayIcon}
                  disabled={!classData.next_lesson_id}
                  onClick={() => navigate(`/trainer/lesson/${classData.next_lesson_id}`)}
                  className="w-full"
                >
                  Start Lesson
                </Button>
              </Tooltip>
              
              <Tooltip content="View class analytics and performance metrics">
                <Button
                  variant="ghost"
                  size="sm"
                  icon={ChartBarIcon}
                  onClick={() => navigate(`/trainer/analytics/${classData.id}`)}
                  className="w-full"
                >
                  Analytics
                </Button>
              </Tooltip>
            </div>
          </div>
        </CardBody>
      </Card>
    );
  };

  const StudentProgressCard = ({ student }) => (
    <div className="flex items-center space-x-4 p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex-shrink-0">
        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
          <span className="text-sm font-medium text-blue-600">
            {student.name.split(' ').map(n => n[0]).join('')}
          </span>
        </div>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">{student.name}</p>
        <p className="text-sm text-gray-500">{student.course_title}</p>
      </div>
      <div className="flex-shrink-0 text-right">
        <div className="flex items-center space-x-2">
          <div className="text-sm">
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
              getProgressColor(student.progress_percentage)
            }`}>
              {Math.round(student.progress_percentage)}%
            </span>
          </div>
          <div className="text-xs text-gray-500">
            {student.last_activity}
          </div>
        </div>
      </div>
    </div>
  );

  const ActivityItem = ({ activity }) => {
    const getActivityIcon = (type) => {
      switch (type) {
        case 'lesson_completed': return CheckCircleIcon;
        case 'assignment_submitted': return DocumentTextIcon;
        case 'class_started': return PlayIcon;
        case 'feedback_given': return ChatBubbleLeftIcon;
        default: return BellIcon;
      }
    };

    const getActivityColor = (type) => {
      switch (type) {
        case 'lesson_completed': return 'text-green-600 bg-green-100';
        case 'assignment_submitted': return 'text-blue-600 bg-blue-100';
        case 'class_started': return 'text-purple-600 bg-purple-100';
        case 'feedback_given': return 'text-amber-600 bg-amber-100';
        default: return 'text-gray-600 bg-gray-100';
      }
    };

    const Icon = getActivityIcon(activity.type);
    const colorClass = getActivityColor(activity.type);

    return (
      <div className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
        <div className={`p-2 rounded-full ${colorClass}`}>
          <Icon className="h-4 w-4" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900">
            {activity.title}
          </p>
          <p className="text-sm text-gray-600 truncate">
            {activity.description}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            {activity.timestamp}
          </p>
        </div>
      </div>
    );
  };

  const filteredClasses = activeClasses.filter(classData => {
    const matchesSearch = !searchQuery || 
      classData.course_title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      classData.company_name.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesFilter = selectedFilter === 'all' || 
      (selectedFilter === 'active' && classData.status === 'active') ||
      (selectedFilter === 'needs-attention' && classData.alerts && classData.alerts.length > 0) ||
      (selectedFilter === 'high-engagement' && classData.engagement_score >= 80);
    
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return <PageLoadingSkeleton type="dashboard" />;
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-neutral-200">
        <div className="container mx-auto py-8">
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <h1 className="heading-4xl text-gradient">Trainer Dashboard</h1>
              <p className="body-lg text-neutral-600">
                Welcome back, {user?.first_name || user?.username}. You have {activeClasses.length} active classes.
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost"
                icon={BookOpenIcon}
                onClick={() => navigate('/trainer/content-library')}
              >
                Content Library
              </Button>
              <Button 
                variant="secondary"
                icon={CalendarDaysIcon}
                onClick={() => navigate('/trainer/schedule')}
              >
                Schedule
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {dashboardStats && (
            <>
              <StatCard
                title="Active Classes"
                value={dashboardStats.active_classes}
                change={dashboardStats.classes_change}
                icon={UserGroupIcon}
                color="primary"
                trend="2 starting this week"
              />
              <StatCard
                title="Total Students"
                value={dashboardStats.total_students}
                change={dashboardStats.students_change}
                icon={UsersIcon}
                color="success"
                trend="85% attendance rate"
              />
              <StatCard
                title="Avg Progress"
                value={`${dashboardStats.avg_progress}%`}
                change={dashboardStats.progress_change}
                icon={ChartBarIcon}
                color="primary"
                trend="Above target"
              />
              <StatCard
                title="Engagement Score"
                value={`${dashboardStats.avg_engagement}%`}
                change={dashboardStats.engagement_change}
                icon={TrophyIcon}
                color="warning"
                trend="High participation"
              />
            </>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content - Active Classes */}
          <div className="lg:col-span-2">
            <Card variant="elevated">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h2 className="heading-xl text-neutral-900">
                    Active Classes ({filteredClasses.length})
                  </h2>
                  <div className="flex items-center space-x-4">
                    <SearchInput
                      placeholder="Search classes..."
                      onSearch={setSearchQuery}
                      className="w-64"
                    />
                    <Dropdown
                      trigger={
                        <Button variant="ghost" icon={FunnelIcon}>
                          Filter
                        </Button>
                      }
                    >
                      <DropdownItem onClick={() => setSelectedFilter('all')}>
                        All Classes
                      </DropdownItem>
                      <DropdownItem onClick={() => setSelectedFilter('active')}>
                        Active Only
                      </DropdownItem>
                      <DropdownItem onClick={() => setSelectedFilter('needs-attention')}>
                        Needs Attention
                      </DropdownItem>
                      <DropdownItem onClick={() => setSelectedFilter('high-engagement')}>
                        High Engagement
                      </DropdownItem>
                    </Dropdown>
                  </div>
                </div>
              </CardHeader>

              <CardBody>
                {filteredClasses.length === 0 ? (
                  <EmptyState
                    icon={AcademicCapIcon}
                    title="No classes found"
                    description="No classes match your current filters."
                    variant="card"
                  />
                ) : (
                  <div className="space-y-6">
                    {filteredClasses.map((classData) => (
                      <ClassCard key={classData.id} classData={classData} />
                    ))}
                  </div>
                )}
              </CardBody>
            </Card>
          </div>

          {/* Sidebar - Student Progress & Quick Actions */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-sm">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
              </div>
              <div className="p-6 space-y-3">
                <button 
                  onClick={() => navigate('/trainer/create-lesson')}
                  className="w-full btn btn-primary"
                >
                  <PencilIcon className="h-4 w-4" />
                  Create Custom Lesson
                </button>
                <button 
                  onClick={() => navigate('/trainer/assessment-builder')}
                  className="w-full btn btn-secondary"
                >
                  <DocumentTextIcon className="h-4 w-4" />
                  Build Assessment
                </button>
                <button 
                  onClick={() => navigate('/trainer/student-feedback')}
                  className="w-full btn btn-ghost"
                >
                  <ChatBubbleLeftIcon className="h-4 w-4" />
                  Student Feedback
                </button>
                <button 
                  onClick={() => navigate('/trainer/reports')}
                  className="w-full btn btn-ghost"
                >
                  <ChartBarIcon className="h-4 w-4" />
                  Generate Reports
                </button>
              </div>
            </div>

            {/* Student Progress Overview */}
            <div className="bg-white rounded-lg shadow-sm">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Student Progress</h3>
              </div>
              <div className="p-3">
                {studentProgress.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">No student data available</p>
                ) : (
                  <div className="space-y-3">
                    {studentProgress.slice(0, 5).map((student, index) => (
                      <StudentProgressCard key={index} student={student} />
                    ))}
                  </div>
                )}
                {studentProgress.length > 5 && (
                  <div className="mt-4 text-center">
                    <button 
                      onClick={() => navigate('/trainer/student-progress')}
                      className="text-sm text-blue-600 hover:text-blue-500"
                    >
                      View All Students →
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-lg shadow-sm">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
              </div>
              <div className="p-3">
                {recentActivity.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">No recent activity</p>
                ) : (
                  <div className="space-y-1">
                    {recentActivity.map((activity, index) => (
                      <ActivityItem key={index} activity={activity} />
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrainerDashboard;