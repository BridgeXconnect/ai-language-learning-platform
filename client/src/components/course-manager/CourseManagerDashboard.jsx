import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/auth_context';
import { 
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  PencilIcon,
  UsersIcon,
  BookOpenIcon,
  ChartBarIcon,
  CalendarDaysIcon,
  DocumentTextIcon,
  SparklesIcon,
  XCircleIcon,
  ArrowTrendingUpIcon,
  BellIcon,
  FunnelIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';

const CourseManagerDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // State management
  const [dashboardStats, setDashboardStats] = useState(null);
  const [pendingCourses, setPendingCourses] = useState([]);
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
      
      // Mock data instead of API calls
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate loading
      
      setDashboardStats({
        total_pending: 8,
        urgent_priority: 3,
        high_confidence: 5,
        processing_time_avg: 2.4
      });
      
      setPendingCourses([
        {
          id: 1,
          company_name: 'TechCorp Inc.',
          cefr_level: 'B2',
          cohort_size: 45,
          estimated_hours: 40,
          daysSinceCreated: 5,
          sop_count: 3,
          training_objectives: 'Improve business communication and technical vocabulary for software developers',
          ai_confidence: 85,
          priority: 'high'
        },
        {
          id: 2,
          company_name: 'Global Finance Ltd.',
          cefr_level: 'B1',
          cohort_size: 32,
          estimated_hours: 30,
          daysSinceCreated: 2,
          sop_count: 2,
          training_objectives: 'Financial terminology and client communication skills',
          ai_confidence: 92,
          priority: 'urgent'
        },
        {
          id: 3,
          company_name: 'MedCare Solutions',
          cefr_level: 'A2',
          cohort_size: 28,
          estimated_hours: 25,
          daysSinceCreated: 8,
          sop_count: 4,
          training_objectives: 'Healthcare communication and patient interaction protocols',
          ai_confidence: 78,
          priority: 'normal'
        }
      ]);
      
      setRecentActivity([
        {
          id: 1,
          type: 'course_generated',
          message: 'New course generated for TechCorp Inc.',
          timestamp: '2 hours ago'
        },
        {
          id: 2,
          type: 'course_approved',
          message: 'Course approved for Global Finance Ltd.',
          timestamp: '4 hours ago'
        },
        {
          id: 3,
          type: 'sop_processed',
          message: 'SOP documents processed for MedCare Solutions',
          timestamp: '1 day ago'
        }
      ]);
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = async (courseId, action) => {
    try {
      // Mock quick action
      console.log(`Performing ${action} on course ${courseId}`);
      fetchDashboardData(); // Refresh data
    } catch (error) {
      console.error(`Error performing ${action}:`, error);
    }
  };

  const getUrgencyLevel = (createdDays, priority) => {
    if (priority === 'urgent' || createdDays > 7) return 'high';
    if (priority === 'high' || createdDays > 3) return 'medium';
    return 'low';
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'high': return 'text-red-700 bg-red-100 border-red-200';
      case 'medium': return 'text-amber-700 bg-amber-100 border-amber-200';
      default: return 'text-green-700 bg-green-100 border-green-200';
    }
  };

  const StatCard = ({ title, value, change, icon: Icon, color = 'blue', trend = null }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <div className="flex items-baseline space-x-2">
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            {change !== undefined && (
              <span className={`text-sm font-medium ${
                change >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {change >= 0 ? '+' : ''}{change}%
              </span>
            )}
          </div>
          {trend && (
            <div className="flex items-center mt-1">
              <ArrowTrendingUpIcon className="h-3 w-3 text-green-500 mr-1" />
              <span className="text-xs text-gray-500">{trend}</span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-lg bg-${color}-100`}>
          <Icon className={`h-6 w-6 text-${color}-600`} />
        </div>
      </div>
    </div>
  );

  const CourseCard = ({ course }) => {
    const urgency = getUrgencyLevel(course.daysSinceCreated, course.priority);
    const urgencyStyle = getUrgencyColor(urgency);
    
    return (
      <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 border-l-4 ${urgency === 'high' ? 'border-l-red-500' : urgency === 'medium' ? 'border-l-amber-500' : 'border-l-green-500'}`}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <h3 className="text-lg font-semibold text-gray-900">
                {course.company_name}
              </h3>
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${urgencyStyle}`}>
                {urgency.toUpperCase()}
              </span>
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                {course.cefr_level}
              </span>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 mb-3">
              <div className="flex items-center space-x-1">
                <UsersIcon className="h-4 w-4" />
                <span>{course.cohort_size} students</span>
              </div>
              <div className="flex items-center space-x-1">
                <ClockIcon className="h-4 w-4" />
                <span>{course.estimated_hours}h course</span>
              </div>
              <div className="flex items-center space-x-1">
                <CalendarDaysIcon className="h-4 w-4" />
                <span>{course.daysSinceCreated} days ago</span>
              </div>
              <div className="flex items-center space-x-1">
                <DocumentTextIcon className="h-4 w-4" />
                <span>{course.sop_count} documents</span>
              </div>
            </div>

            <p className="text-sm text-gray-700 mb-3">
              {course.training_objectives}
            </p>

            {course.ai_confidence && (
              <div className="mb-3">
                <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                  <span>AI Generation Confidence</span>
                  <span>{course.ai_confidence}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1">
                  <div 
                    className={`h-1 rounded-full ${
                      course.ai_confidence >= 80 ? 'bg-green-500' : 
                      course.ai_confidence >= 60 ? 'bg-amber-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${course.ai_confidence}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>

          <div className="flex flex-col space-y-2 ml-4">
            <button
              onClick={() => console.log(`Review course ${course.id}`)}
              className="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
            >
              <EyeIcon className="h-4 w-4 mr-1" />
              Review
            </button>
            
            {course.ai_confidence >= 80 && (
              <button
                onClick={() => handleQuickAction(course.id, 'quick-approve')}
                className="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 transition-colors"
              >
                <CheckCircleIcon className="h-4 w-4 mr-1" />
                Quick Approve
              </button>
            )}
            
            <button
              onClick={() => console.log(`Edit course ${course.id}`)}
              className="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 transition-colors"
            >
              <PencilIcon className="h-4 w-4 mr-1" />
              Edit
            </button>
          </div>
        </div>
      </div>
    );
  };

  const ActivityItem = ({ activity }) => {
    const getActivityIcon = (type) => {
      switch (type) {
        case 'course_generated': return SparklesIcon;
        case 'course_approved': return CheckCircleIcon;
        case 'sop_processed': return DocumentTextIcon;
        default: return BellIcon;
      }
    };

    const getActivityColor = (type) => {
      switch (type) {
        case 'course_generated': return 'text-blue-600 bg-blue-100';
        case 'course_approved': return 'text-green-600 bg-green-100';
        case 'sop_processed': return 'text-amber-600 bg-amber-100';
        default: return 'text-gray-600 bg-gray-100';
      }
    };

    const Icon = getActivityIcon(activity.type);
    const colorClass = getActivityColor(activity.type);

    return (
      <div className="flex items-start space-x-3 py-3">
        <div className={`p-2 rounded-lg ${colorClass}`}>
          <Icon className="h-4 w-4" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-900">{activity.message}</p>
          <p className="text-xs text-gray-500">{activity.timestamp}</p>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const filteredCourses = pendingCourses.filter(course => {
    if (selectedFilter === 'urgent') return course.priority === 'urgent';
    if (selectedFilter === 'high-confidence') return course.ai_confidence >= 80;
    if (selectedFilter === 'needs-attention') return course.daysSinceCreated > 3;
    return true;
  });

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Course Manager Dashboard</h1>
            <p className="mt-2 text-gray-600">
              Welcome back, {user?.name || 'Course Manager'}! Review and approve AI-generated courses.
            </p>
          </div>
          <button className="mt-4 sm:mt-0 inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <SparklesIcon className="w-5 h-5 mr-2" />
            Generate New Course
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Courses Pending Review"
            value={dashboardStats?.total_pending || 0}
            change={12}
            icon={ClockIcon}
            color="blue"
            trend="vs last week"
          />
          <StatCard
            title="Urgent Priority"
            value={dashboardStats?.urgent_priority || 0}
            change={-8}
            icon={ExclamationTriangleIcon}
            color="red"
            trend="reduction this week"
          />
          <StatCard
            title="High Confidence"
            value={dashboardStats?.high_confidence || 0}
            change={25}
            icon={CheckCircleIcon}
            color="green"
            trend="AI success rate"
          />
          <StatCard
            title="Avg. Processing Time"
            value={`${dashboardStats?.processing_time_avg || 0}d`}
            change={-15}
            icon={ChartBarIcon}
            color="purple"
            trend="improvement"
          />
        </div>

        {/* Smart Filters */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
            <div className="flex items-center space-x-4">
              <FunnelIcon className="h-5 w-5 text-gray-400" />
              <div className="flex space-x-2">
                {[
                  { id: 'all', label: 'All Courses', count: pendingCourses.length },
                  { id: 'urgent', label: 'Urgent Priority', count: pendingCourses.filter(c => c.priority === 'urgent').length },
                  { id: 'high-confidence', label: 'High Confidence', count: pendingCourses.filter(c => c.ai_confidence >= 80).length },
                  { id: 'needs-attention', label: 'Needs Attention', count: pendingCourses.filter(c => c.daysSinceCreated > 3).length }
                ].map(filter => (
                  <button
                    key={filter.id}
                    onClick={() => setSelectedFilter(filter.id)}
                    className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      selectedFilter === filter.id
                        ? 'bg-blue-100 text-blue-700 border border-blue-200'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    {filter.label} ({filter.count})
                  </button>
                ))}
              </div>
            </div>
            
            <div className="relative">
              <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search courses..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Pending Courses */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  Pending Course Reviews ({filteredCourses.length})
                </h2>
              </div>
              <div className="p-6">
                <div className="space-y-6">
                  {filteredCourses.map((course) => (
                    <CourseCard key={course.id} course={course} />
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Activity Feed */}
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
              </div>
              <div className="p-6">
                <div className="space-y-1">
                  {recentActivity.map((activity) => (
                    <ActivityItem key={activity.id} activity={activity} />
                  ))}
                </div>
              </div>
            </div>

            {/* System Status */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">System Status</h3>
              </div>
              <div className="p-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">AI Generation</span>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                      Operational
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Document Processing</span>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                      Operational
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Database</span>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                      Healthy
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseManagerDashboard; 