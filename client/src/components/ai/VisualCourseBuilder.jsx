import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/auth_context';
import { 
  PlusIcon,
  TrashIcon,
  PencilIcon,
  EyeIcon,
  ArrowsUpDownIcon,
  DocumentDuplicateIcon,
  SparklesIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  UsersIcon,
  BookOpenIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  ArrowLeftIcon,
  ArrowRightIcon,
  PlayIcon,
  CheckIcon,
  ShareIcon
} from '@heroicons/react/24/outline';
import api from '../../services/api';

const VisualCourseBuilder = () => {
  const { courseId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // Course state
  const [course, setCourse] = useState(null);
  const [modules, setModules] = useState([]);
  const [selectedModule, setSelectedModule] = useState(null);
  const [selectedLesson, setSelectedLesson] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Builder state
  const [previewMode, setPreviewMode] = useState(false);
  const [showAIAssistant, setShowAIAssistant] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [qualityScore, setQualityScore] = useState(null);
  
  // Modal state
  const [showModuleModal, setShowModuleModal] = useState(false);
  const [showLessonModal, setShowLessonModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  useEffect(() => {
    fetchCourseData();
  }, [courseId]);

  const fetchCourseData = async () => {
    try {
      setLoading(true);
      
      // Mock course data until backend is available
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockCourse = {
        id: courseId,
        title: 'Business English for Technology Professionals',
        company_name: 'TechCorp Inc.',
        cefr_level: 'B2',
        cohort_size: 45,
        description: 'A comprehensive course designed for technology professionals to improve their business English communication skills.',
        training_objectives: 'Enhance technical vocabulary, improve presentation skills, and develop effective written communication for the tech industry.'
      };
      
      const mockModules = [
        {
          id: 1,
          title: 'Technical Communication Fundamentals',
          description: 'Learn the basics of technical communication in English',
          estimated_duration: 120,
          lessons: [
            { id: 1, title: 'Technical Vocabulary Essentials', duration: 30, type: 'video' },
            { id: 2, title: 'Writing Technical Documentation', duration: 45, type: 'interactive' },
            { id: 3, title: 'Email Communication in Tech', duration: 25, type: 'exercise' },
            { id: 4, title: 'Assessment - Module 1', duration: 20, type: 'assessment' }
          ]
        },
        {
          id: 2,
          title: 'Presentation Skills for Developers',
          description: 'Master the art of presenting technical concepts to diverse audiences',
          estimated_duration: 180,
          lessons: [
            { id: 5, title: 'Structuring Technical Presentations', duration: 40, type: 'video' },
            { id: 6, title: 'Visual Aids and Code Examples', duration: 35, type: 'interactive' },
            { id: 7, title: 'Handling Q&A Sessions', duration: 30, type: 'video' },
            { id: 8, title: 'Practice Presentation', duration: 60, type: 'project' },
            { id: 9, title: 'Assessment - Module 2', duration: 15, type: 'assessment' }
          ]
        },
        {
          id: 3,
          title: 'Cross-Cultural Communication',
          description: 'Navigate cultural differences in global tech teams',
          estimated_duration: 90,
          lessons: [
            { id: 10, title: 'Cultural Awareness in Tech', duration: 25, type: 'video' },
            { id: 11, title: 'Remote Team Communication', duration: 30, type: 'interactive' },
            { id: 12, title: 'Conflict Resolution', duration: 20, type: 'scenario' },
            { id: 13, title: 'Final Assessment', duration: 15, type: 'assessment' }
          ]
        }
      ];
      
      const mockQualityScore = {
        overall_score: 87,
        content_quality: 92,
        structure_score: 85,
        engagement_score: 81,
        cefr_alignment: 89,
        feedback: [
          'Excellent technical vocabulary coverage',
          'Well-structured progression from basics to advanced',
          'Could benefit from more interactive elements',
          'Strong alignment with B2 CEFR level'
        ]
      };
      
      setCourse(mockCourse);
      setModules(mockModules);
      setQualityScore(mockQualityScore);
      
    } catch (error) {
      console.error('Error fetching course data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateContent = async (type, targetId) => {
    try {
      setSaving(true);
      console.log(`Generating ${type} content for target ${targetId}`);
      
      // Mock AI content generation
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate AI processing
      
      // In a real app, this would generate new content via AI
      // For now, we'll just refresh the data
      await fetchCourseData();
      
      // Show success message
      console.log(`Successfully generated ${type} content`);
      
    } catch (error) {
      console.error('Error generating content:', error);
    } finally {
      setSaving(false);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'text-green-600 bg-green-100';
    if (confidence >= 60) return 'text-amber-600 bg-amber-100';
    return 'text-red-600 bg-red-100';
  };

  const QualityIndicator = ({ score, label }) => (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <span className="text-sm font-medium text-gray-700">{label}</span>
      <div className="flex items-center space-x-2">
        <div className="w-16 bg-gray-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full ${
              score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-amber-500' : 'bg-red-500'
            }`}
            style={{ width: `${score}%` }}
          ></div>
        </div>
        <span className="text-sm font-bold text-gray-900">{score}%</span>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4" />
          <p className="text-gray-600">Loading course builder...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/course-manager')}
                className="btn btn-ghost"
              >
                <ArrowLeftIcon className="h-5 w-5" />
                Back to Dashboard
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{course?.title}</h1>
                <p className="text-gray-600">{course?.company_name} • {course?.cefr_level}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setPreviewMode(!previewMode)}
                className="btn btn-ghost"
              >
                <EyeIcon className="h-5 w-5" />
                {previewMode ? 'Edit Mode' : 'Preview'}
              </button>
              
              <button
                onClick={() => setShowAIAssistant(!showAIAssistant)}
                className="btn btn-secondary"
              >
                <SparklesIcon className="h-5 w-5" />
                AI Assistant
              </button>
              
              <button
                onClick={() => setSaving(true)}
                disabled={saving}
                className="btn btn-primary"
              >
                {saving ? (
                  <>
                    <div className="loading-spinner" />
                    Saving...
                  </>
                ) : (
                  <>
                    <CheckIcon className="h-5 w-5" />
                    Save Course
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Builder Area */}
          <div className="lg:col-span-3">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Course Structure</h2>
              <button
                className="btn btn-primary"
              >
                <PlusIcon className="h-4 w-4" />
                Add Module
              </button>
            </div>

            {modules.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg border-2 border-dashed border-gray-300">
                <BookOpenIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No modules yet</h3>
                <p className="text-gray-600 mb-4">Start building your course by adding the first module</p>
                <button 
                  className="btn btn-primary"
                  onClick={() => setShowModuleModal(true)}
                >
                  <PlusIcon className="h-4 w-4" />
                  Add First Module
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                {modules.map((module, moduleIndex) => (
                  <div key={module.id} className="card border-l-4 border-l-blue-500">
                    <div className="card-header flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="font-semibold text-gray-900 text-lg">{module.title}</h3>
                          <span className="badge badge-primary">Module {moduleIndex + 1}</span>
                          <span className="badge badge-neutral">
                            {module.lessons?.length || 0} lessons
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{module.description}</p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span className="flex items-center space-x-1">
                            <ClockIcon className="h-3 w-3" />
                            <span>{module.estimated_duration} min</span>
                          </span>
                          <span className="flex items-center space-x-1">
                            <UsersIcon className="h-3 w-3" />
                            <span>All students</span>
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          className="btn btn-ghost btn-sm"
                          onClick={() => {
                            setSelectedModule(module);
                            setEditingItem(module);
                            setShowModuleModal(true);
                          }}
                        >
                          <PencilIcon className="h-4 w-4" />
                          Edit
                        </button>
                        <button className="btn btn-ghost btn-sm text-red-600">
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                    
                    {/* Lessons List */}
                    {module.lessons && module.lessons.length > 0 && (
                      <div className="card-body pt-0">
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <h4 className="text-sm font-medium text-gray-700">Lessons</h4>
                            <button 
                              className="btn btn-ghost btn-sm"
                              onClick={() => {
                                setSelectedModule(module);
                                setShowLessonModal(true);
                              }}
                            >
                              <PlusIcon className="h-3 w-3" />
                              Add Lesson
                            </button>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {module.lessons.map((lesson, lessonIndex) => (
                              <div 
                                key={lesson.id} 
                                className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group cursor-pointer"
                                onClick={() => {
                                  setSelectedLesson(lesson);
                                  setEditingItem(lesson);
                                  setShowLessonModal(true);
                                }}
                              >
                                <div className={`p-2 rounded-full text-xs font-medium ${
                                  lesson.type === 'video' ? 'bg-blue-100 text-blue-600' :
                                  lesson.type === 'interactive' ? 'bg-green-100 text-green-600' :
                                  lesson.type === 'exercise' ? 'bg-purple-100 text-purple-600' :
                                  lesson.type === 'assessment' ? 'bg-orange-100 text-orange-600' :
                                  'bg-gray-100 text-gray-600'
                                }`}>
                                  {lessonIndex + 1}
                                </div>
                                <div className="flex-1 min-w-0">
                                  <p className="text-sm font-medium text-gray-900 truncate">{lesson.title}</p>
                                  <div className="flex items-center space-x-3 text-xs text-gray-500">
                                    <span>{lesson.duration} min</span>
                                    <span className="capitalize">{lesson.type}</span>
                                  </div>
                                </div>
                                <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                                  <ArrowsUpDownIcon className="h-4 w-4 text-gray-400" />
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                
                {/* Add Module Button */}
                <div className="text-center py-6">
                  <button 
                    className="btn btn-secondary"
                    onClick={() => setShowModuleModal(true)}
                  >
                    <PlusIcon className="h-4 w-4" />
                    Add Another Module
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Course Overview */}
            <div className="card">
              <div className="card-header">
                <h3 className="font-semibold text-gray-900">Course Overview</h3>
              </div>
              <div className="card-body space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Modules</span>
                  <span className="font-medium">{modules.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Lessons</span>
                  <span className="font-medium">
                    {modules.reduce((total, module) => total + (module.lessons?.length || 0), 0)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Est. Duration</span>
                  <span className="font-medium">
                    {modules.reduce((total, module) => total + (module.estimated_duration || 0), 0)} min
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Target Students</span>
                  <span className="font-medium">{course?.cohort_size}</span>
                </div>
              </div>
            </div>

            {/* Quality Assessment */}
            {qualityScore && (
              <div className="card">
                <div className="card-header">
                  <h3 className="font-semibold text-gray-900">Quality Assessment</h3>
                </div>
                <div className="card-body space-y-3">
                  <QualityIndicator score={qualityScore.content_quality} label="Content Quality" />
                  <QualityIndicator score={qualityScore.structure_score} label="Structure" />
                  <QualityIndicator score={qualityScore.engagement_score} label="Engagement" />
                  <QualityIndicator score={qualityScore.cefr_alignment} label="CEFR Alignment" />
                  
                  <div className="pt-3 border-t border-gray-200">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-gray-900">Overall Score</span>
                      <span className={`text-lg font-bold ${
                        qualityScore.overall_score >= 80 ? 'text-green-600' : 
                        qualityScore.overall_score >= 60 ? 'text-amber-600' : 'text-red-600'
                      }`}>
                        {qualityScore.overall_score}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* AI Assistant */}
            {showAIAssistant && (
              <div className="card">
                <div className="card-header">
                  <h3 className="font-semibold text-gray-900">AI Assistant</h3>
                </div>
                <div className="card-body space-y-3">
                  <button
                    onClick={() => handleGenerateContent('module', null)}
                    className="w-full btn btn-ghost"
                  >
                    <SparklesIcon className="h-4 w-4" />
                    Suggest New Module
                  </button>
                  
                  <button
                    onClick={() => handleGenerateContent('lesson', selectedModule?.id)}
                    className="w-full btn btn-ghost"
                    disabled={!selectedModule}
                  >
                    <SparklesIcon className="h-4 w-4" />
                    Generate Lesson Content
                  </button>
                  
                  <button
                    onClick={() => handleGenerateContent('exercise', selectedLesson?.id)}
                    className="w-full btn btn-ghost"
                    disabled={!selectedLesson}
                  >
                    <SparklesIcon className="h-4 w-4" />
                    Create Exercises
                  </button>
                  
                  <button
                    onClick={() => handleGenerateContent('assessment', course?.id)}
                    className="w-full btn btn-ghost"
                  >
                    <SparklesIcon className="h-4 w-4" />
                    Generate Assessment
                  </button>
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="card">
              <div className="card-header">
                <h3 className="font-semibold text-gray-900">Quick Actions</h3>
              </div>
              <div className="card-body space-y-3">
                <button
                  onClick={() => navigate(`/course-manager/preview/${courseId}`)}
                  className="w-full btn btn-ghost"
                >
                  <PlayIcon className="h-4 w-4" />
                  Preview Course
                </button>
                
                <button
                  onClick={() => navigate(`/course-manager/export/${courseId}`)}
                  className="w-full btn btn-ghost"
                >
                  <ShareIcon className="h-4 w-4" />
                  Export Course
                </button>
                
                <button
                  onClick={() => navigate(`/course-manager/settings/${courseId}`)}
                  className="w-full btn btn-ghost"
                >
                  <Cog6ToothIcon className="h-4 w-4" />
                  Course Settings
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VisualCourseBuilder; 