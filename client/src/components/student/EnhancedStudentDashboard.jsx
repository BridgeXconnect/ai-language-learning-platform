import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/auth_context';
import { 
  BookOpenIcon,
  PlayIcon,
  PauseIcon,
  ChartBarIcon,
  TrophyIcon,
  FireIcon,
  ClockIcon,
  CheckCircleIcon,
  StarIcon,
  ArrowRightIcon,
  CalendarDaysIcon,
  ChatBubbleLeftIcon,
  AcademicCapIcon,
  RocketLaunchIcon,
  LightBulbIcon,
  HeartIcon,
  BoltIcon
} from '@heroicons/react/24/outline';
import api from '../../services/api';

const EnhancedStudentDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // State management
  const [studentData, setStudentData] = useState(null);
  const [currentCourse, setCurrentCourse] = useState(null);
  const [progress, setProgress] = useState(null);
  const [achievements, setAchievements] = useState([]);
  const [weeklyGoals, setWeeklyGoals] = useState(null);
  const [loading, setLoading] = useState(true);
  const [streakCount, setStreakCount] = useState(0);

  useEffect(() => {
    fetchStudentData();
  }, []);

  const fetchStudentData = async () => {
    try {
      setLoading(true);
      
      // Mock student data until backend is available
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockStudentData = {
        id: 1,
        name: 'Alex Thompson',
        email: 'alex.thompson@techcorp.com',
        company: 'TechCorp Inc.',
        level: 'B2',
        joined_date: '2024-01-15'
      };
      
      const mockCurrentCourse = {
        id: 1,
        title: 'Business English for Technology Professionals',
        description: 'A comprehensive course designed for technology professionals to improve their business English communication skills.',
        cefr_level: 'B2',
        overall_progress: 67,
        completed_lessons: 12,
        total_lessons: 18,
        estimated_completion: 8,
        next_lesson: {
          id: 'lesson_13',
          title: 'Advanced Technical Presentations',
          duration: 25,
          type: 'video'
        }
      };
      
      const mockProgress = {
        lessons_this_week: 4,
        weekly_target: 5,
        completed_lessons: 12,
        total_lessons: 18,
        speaking_minutes: 45,
        speaking_target: 60,
        streak_days: 7,
        total_study_hours: 28,
        vocabulary_count: 156,
        average_score: 85,
        completion_rate: 92,
        recent_activities: [
          {
            title: 'Completed Lesson',
            description: 'Technical Vocabulary Essentials',
            timestamp: '2 hours ago',
            score: 88
          },
          {
            title: 'Exercise Completed',
            description: 'Email Communication Practice',
            timestamp: '1 day ago',
            score: 92
          },
          {
            title: 'Assessment Passed',
            description: 'Module 2 Final Assessment',
            timestamp: '3 days ago',
            score: 85
          }
        ]
      };
      
      const mockAchievements = [
        {
          id: 1,
          title: 'Week Warrior',
          description: 'Complete 5 lessons in one week',
          type: 'streak',
          unlocked: true,
          progress: 5,
          target: 5
        },
        {
          id: 2,
          title: 'Quick Learner',
          description: 'Score 90% or higher on 3 assessments',
          type: 'score',
          unlocked: false,
          progress: 2,
          target: 3
        },
        {
          id: 3,
          title: 'Vocabulary Master',
          description: 'Learn 100 new words',
          type: 'lessons',
          unlocked: true,
          progress: 156,
          target: 100
        },
        {
          id: 4,
          title: 'Speed Demon',
          description: 'Complete a lesson in under 15 minutes',
          type: 'speed',
          unlocked: false,
          progress: 0,
          target: 1
        }
      ];
      
      const mockWeeklyGoals = {
        goals: [
          {
            title: 'Complete 5 Lessons',
            progress: 4,
            target: 5,
            completed: false,
            description: 'Finish 5 lessons this week to stay on track'
          },
          {
            title: '60 Minutes Speaking Practice',
            progress: 45,
            target: 60,
            completed: false,
            description: 'Practice speaking to improve fluency'
          },
          {
            title: 'Learn 20 New Words',
            progress: 20,
            target: 20,
            completed: true,
            description: 'Expand your technical vocabulary'
          }
        ]
      };
      
      setStudentData(mockStudentData);
      setCurrentCourse(mockCurrentCourse);
      setProgress(mockProgress);
      setAchievements(mockAchievements);
      setWeeklyGoals(mockWeeklyGoals);
      setStreakCount(mockProgress.streak_days || 7);
      
    } catch (error) {
      console.error('Error fetching student data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContinueLearning = () => {
    if (currentCourse?.next_lesson) {
      navigate(`/student/lesson/${currentCourse.next_lesson.id}`);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    const name = user?.first_name || 'there';
    
    if (hour < 12) return `Good morning, ${name}!`;
    if (hour < 17) return `Good afternoon, ${name}!`;
    return `Good evening, ${name}!`;
  };

  const getMotivationalMessage = () => {
    const messages = [
      "You're making great progress! Keep it up! 🚀",
      "Every lesson brings you closer to fluency! 📚",
      "Consistency is key - you're building a great habit! 🔥",
      "Your dedication is inspiring! Keep learning! ⭐",
      "Small steps every day lead to big results! 💪"
    ];
    return messages[Math.floor(Math.random() * messages.length)];
  };

  const ProgressCard = ({ title, current, total, color = 'blue', icon: Icon }) => {
    const percentage = total > 0 ? (current / total) * 100 : 0;
    
    return (
      <div className="card">
        <div className="card-body">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Icon className={`h-5 w-5 text-${color}-600`} />
              <h3 className="font-medium text-gray-900">{title}</h3>
            </div>
            <span className="text-sm text-gray-500">{current}/{total}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
            <motion.div 
              className={`${color === 'blue' ? 'bg-blue-600' : `bg-${color}-500`} h-2 rounded-full`}
              initial={{ width: 0 }}
              animate={{ width: `${percentage}%` }}
              transition={{ duration: 0.8, ease: "easeOut", delay: 0.5 }}
            ></motion.div>
          </div>
          <p className="text-xs text-gray-500">{Math.round(percentage)}% complete</p>
        </div>
      </div>
    );
  };

  const AchievementBadge = ({ achievement }) => {
    const getAchievementIcon = (type) => {
      switch (type) {
        case 'streak': return FireIcon;
        case 'lessons': return BookOpenIcon;
        case 'score': return TrophyIcon;
        case 'speed': return BoltIcon;
        default: return StarIcon;
      }
    };

    const Icon = getAchievementIcon(achievement.type);
    
    return (
      <div className={`flex items-center space-x-3 p-3 rounded-lg border-2 ${
        achievement.unlocked 
          ? 'border-yellow-200 bg-yellow-50' 
          : 'border-gray-200 bg-gray-50'
      }`}>
        <div className={`p-2 rounded-full ${
          achievement.unlocked 
            ? 'bg-yellow-100 text-yellow-600' 
            : 'bg-gray-100 text-gray-400'
        }`}>
          <Icon className="h-5 w-5" />
        </div>
        <div className="flex-1">
          <h4 className={`font-medium ${
            achievement.unlocked ? 'text-gray-900' : 'text-gray-500'
          }`}>
            {achievement.title}
          </h4>
          <p className="text-sm text-gray-500">{achievement.description}</p>
          {achievement.progress && (
            <div className="mt-1">
              <div className="w-full bg-gray-200 rounded-full h-1">
                <div 
                  className="bg-yellow-500 h-1 rounded-full transition-all duration-300"
                  style={{ width: `${(achievement.progress / achievement.target) * 100}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
        {achievement.unlocked && (
          <CheckCircleIcon className="h-5 w-5 text-green-600" />
        )}
      </div>
    );
  };

  const WeeklyGoalCard = ({ goal }) => (
    <div className="card">
      <div className="card-body">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-medium text-gray-900">{goal.title}</h3>
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
            goal.completed 
              ? 'bg-green-100 text-green-700' 
              : 'bg-blue-100 text-blue-700'
          }`}>
            {goal.completed ? 'Complete!' : `${goal.progress}/${goal.target}`}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
          <div 
            className={`h-2 rounded-full transition-all duration-500 ${
              goal.completed ? 'bg-green-600' : 'bg-blue-600'
            }`}
            style={{ width: `${Math.min((goal.progress / goal.target) * 100, 100)}%` }}
          ></div>
        </div>
        <p className="text-sm text-gray-600">{goal.description}</p>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4" />
          <p className="text-gray-600">Loading your learning dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Welcome Header */}
      <motion.div 
        className="bg-gradient-to-r from-brand-500 to-brand-600 text-white"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <h1 className="text-3xl font-bold mb-2">{getGreeting()}</h1>
              <p className="text-blue-100 text-lg">{getMotivationalMessage()}</p>
            </motion.div>
            <motion.div 
              className="text-center"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <div className="flex items-center justify-center space-x-2 mb-1">
                <FireIcon className="h-6 w-6 text-orange-300" />
                <span className="text-2xl font-bold">{streakCount}</span>
              </div>
              <p className="text-sm text-blue-100">Day Streak</p>
            </motion.div>
          </div>
        </div>
      </motion.div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Quick Actions */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <motion.button 
            onClick={handleContinueLearning}
            className="card hover:shadow-lg transition-all cursor-pointer group"
            whileHover={{ y: -4, boxShadow: "0 10px 25px 0 rgba(0, 0, 0, 0.1)" }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.7 }}
          >
            <div className="card-body text-center">
              <motion.div 
                className="bg-green-100 rounded-full p-3 w-12 h-12 mx-auto mb-3 group-hover:bg-green-200 transition-colors"
                whileHover={{ scale: 1.1 }}
                transition={{ duration: 0.2 }}
              >
                <PlayIcon className="h-6 w-6 text-green-600" />
              </motion.div>
              <h3 className="font-semibold text-gray-900">Continue Learning</h3>
              <p className="text-sm text-gray-600 mt-1">
                {currentCourse?.next_lesson ? currentCourse.next_lesson.title : 'No active lesson'}
              </p>
            </div>
          </motion.button>

          <motion.button 
            onClick={() => navigate('/student/practice')}
            className="card hover:shadow-lg transition-all cursor-pointer group"
            whileHover={{ y: -4, boxShadow: "0 10px 25px 0 rgba(0, 0, 0, 0.1)" }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.8 }}
          >
            <div className="card-body text-center">
              <motion.div 
                className="bg-purple-100 rounded-full p-3 w-12 h-12 mx-auto mb-3 group-hover:bg-purple-200 transition-colors"
                whileHover={{ scale: 1.1 }}
                transition={{ duration: 0.2 }}
              >
                <LightBulbIcon className="h-6 w-6 text-purple-600" />
              </motion.div>
              <h3 className="font-semibold text-gray-900">Practice</h3>
              <p className="text-sm text-gray-600 mt-1">Review and reinforce</p>
            </div>
          </motion.button>

          <motion.button 
            onClick={() => navigate('/student/progress')}
            className="card hover:shadow-lg transition-all cursor-pointer group"
            whileHover={{ y: -4, boxShadow: "0 10px 25px 0 rgba(0, 0, 0, 0.1)" }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.9 }}
          >
            <div className="card-body text-center">
              <motion.div 
                className="bg-blue-100 rounded-full p-3 w-12 h-12 mx-auto mb-3 group-hover:bg-blue-200 transition-colors"
                whileHover={{ scale: 1.1 }}
                transition={{ duration: 0.2 }}
              >
                <ChartBarIcon className="h-6 w-6 text-blue-600" />
              </motion.div>
              <h3 className="font-semibold text-gray-900">Progress</h3>
              <p className="text-sm text-gray-600 mt-1">See your stats</p>
            </div>
          </motion.button>

          <motion.button 
            onClick={() => navigate('/student/community')}
            className="card hover:shadow-lg transition-all cursor-pointer group"
            whileHover={{ y: -4, boxShadow: "0 10px 25px 0 rgba(0, 0, 0, 0.1)" }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 1.0 }}
          >
            <div className="card-body text-center">
              <motion.div 
                className="bg-amber-100 rounded-full p-3 w-12 h-12 mx-auto mb-3 group-hover:bg-amber-200 transition-colors"
                whileHover={{ scale: 1.1 }}
                transition={{ duration: 0.2 }}
              >
                <ChatBubbleLeftIcon className="h-6 w-6 text-amber-600" />
              </motion.div>
              <h3 className="font-semibold text-gray-900">Community</h3>
              <p className="text-sm text-gray-600 mt-1">Connect & discuss</p>
            </div>
          </motion.button>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content - Current Course & Progress */}
          <div className="lg:col-span-2 space-y-6">
            {/* Current Course */}
            {currentCourse && (
              <div className="card">
                <div className="card-body">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900 mb-2">
                        {currentCourse.title}
                      </h2>
                      <p className="text-gray-600">{currentCourse.description}</p>
                    </div>
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-700">
                      {currentCourse.cefr_level}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <div className="text-2xl font-bold text-gray-900">
                        {currentCourse.completed_lessons}
                      </div>
                      <div className="text-sm text-gray-600">Lessons Completed</div>
                    </div>
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <div className="text-2xl font-bold text-gray-900">
                        {Math.round(currentCourse.overall_progress)}%
                      </div>
                      <div className="text-sm text-gray-600">Course Progress</div>
                    </div>
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <div className="text-2xl font-bold text-gray-900">
                        {currentCourse.estimated_completion}
                      </div>
                      <div className="text-sm text-gray-600">Days to Complete</div>
                    </div>
                  </div>

                  <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                    <motion.div 
                      className="bg-blue-600 h-3 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${currentCourse.overall_progress}%` }}
                      transition={{ duration: 1, ease: "easeOut", delay: 1.2 }}
                    ></motion.div>
                  </div>

                  {currentCourse.next_lesson && (
                    <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                      <div>
                        <h3 className="font-medium text-blue-900">Up Next:</h3>
                        <p className="text-blue-700">{currentCourse.next_lesson.title}</p>
                        <p className="text-sm text-blue-600 mt-1">
                          Estimated time: {currentCourse.next_lesson.duration} minutes
                        </p>
                      </div>
                      <button 
                        onClick={handleContinueLearning}
                        className="btn btn-primary"
                      >
                        <PlayIcon className="h-4 w-4" />
                        Start Lesson
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Weekly Goals */}
            {weeklyGoals && (
              <div className="card">
                <div className="card-header">
                  <h2 className="text-xl font-semibold text-gray-900">This Week's Goals</h2>
                  <p className="text-gray-600">Stay on track with your learning objectives</p>
                </div>
                <div className="card-body">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {weeklyGoals.goals?.map((goal, index) => (
                      <WeeklyGoalCard key={index} goal={goal} />
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Recent Activity */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
              </div>
              <div className="card-body">
                {progress?.recent_activities?.length === 0 ? (
                  <div className="text-center py-8">
                    <BookOpenIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Start learning to see your activity here!</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {progress?.recent_activities?.map((activity, index) => (
                      <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                        <div className="bg-blue-100 rounded-full p-2">
                          <BookOpenIcon className="h-4 w-4 text-blue-600" />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{activity.title}</p>
                          <p className="text-sm text-gray-600">{activity.description}</p>
                          <p className="text-xs text-gray-400 mt-1">{activity.timestamp}</p>
                        </div>
                        {activity.score && (
                          <div className="text-center">
                            <div className="text-lg font-bold text-green-600">{activity.score}%</div>
                            <div className="text-xs text-gray-500">Score</div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar - Progress & Achievements */}
          <div className="space-y-6">
            {/* Progress Overview */}
            {progress && (
              <div className="space-y-4">
                <ProgressCard
                  title="Lessons This Week"
                  current={progress.lessons_this_week}
                  total={progress.weekly_target}
                  color="green"
                  icon={BookOpenIcon}
                />
                <ProgressCard
                  title="Course Progress"
                  current={progress.completed_lessons}
                  total={progress.total_lessons}
                  color="blue"
                  icon={AcademicCapIcon}
                />
                <ProgressCard
                  title="Speaking Practice"
                  current={progress.speaking_minutes}
                  total={progress.speaking_target}
                  color="purple"
                  icon={ChatBubbleLeftIcon}
                />
              </div>
            )}

            {/* Achievements */}
            <div className="card">
              <div className="card-header">
                <div className="flex items-center space-x-2">
                  <TrophyIcon className="h-5 w-5 text-yellow-600" />
                  <h3 className="font-semibold text-gray-900">Achievements</h3>
                </div>
              </div>
              <div className="card-body">
                <div className="space-y-3">
                  {achievements?.slice(0, 3).map((achievement, index) => (
                    <AchievementBadge key={index} achievement={achievement} />
                  ))}
                </div>
                {achievements?.length > 3 && (
                  <button 
                    onClick={() => navigate('/student/achievements')}
                    className="w-full mt-4 btn btn-ghost"
                  >
                    View All Achievements
                    <ArrowRightIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>

            {/* Study Streak */}
            <div className="card">
              <div className="card-body text-center">
                <div className="bg-orange-100 rounded-full p-4 w-16 h-16 mx-auto mb-4">
                  <FireIcon className="h-8 w-8 text-orange-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-1">{streakCount} Days</h3>
                <p className="text-gray-600 mb-4">Current Study Streak</p>
                <div className="bg-gray-100 rounded-full h-2 mb-2">
                  <div 
                    className="bg-orange-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min((streakCount / 30) * 100, 100)}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-500">
                  {30 - streakCount > 0 ? `${30 - streakCount} days to next milestone` : 'Streak Master! 🔥'}
                </p>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="card">
              <div className="card-header">
                <h3 className="font-semibold text-gray-900">Quick Stats</h3>
              </div>
              <div className="card-body space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Study Time</span>
                  <span className="font-medium">{progress?.total_study_hours || 0}h</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Vocabulary Learned</span>
                  <span className="font-medium">{progress?.vocabulary_count || 0} words</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Average Score</span>
                  <span className="font-medium">{progress?.average_score || 0}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Completion Rate</span>
                  <span className="font-medium">{progress?.completion_rate || 0}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedStudentDashboard; 