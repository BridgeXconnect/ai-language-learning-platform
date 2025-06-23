import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BookOpen, 
  Play, 
  Edit, 
  CheckCircle, 
  RotateCcw,
  Clock,
  Users,
  Target,
  ChevronDown,
  ChevronRight,
  FileText,
  PenTool,
  BarChart
} from 'lucide-react';
import toast from 'react-hot-toast';

const CoursePreview = ({ course, onApprove, onRevise }) => {
  const [expandedModules, setExpandedModules] = useState({});
  const [selectedTab, setSelectedTab] = useState('overview');

  if (!course) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="text-gray-600 mt-2">Loading course preview...</p>
      </div>
    );
  }

  const toggleModule = (moduleId) => {
    setExpandedModules(prev => ({
      ...prev,
      [moduleId]: !prev[moduleId]
    }));
  };

  const tabs = [
    { id: 'overview', name: 'Overview', icon: BookOpen },
    { id: 'curriculum', name: 'Curriculum', icon: FileText },
    { id: 'exercises', name: 'Exercises', icon: PenTool },
    { id: 'assessments', name: 'Assessments', icon: BarChart }
  ];

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Course Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          {course.title || 'AI-Generated English Course'}
        </h3>
        <p className="text-gray-700 mb-4">
          {course.description || 'A customized English learning course generated from your requirements and documents.'}
        </p>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-2">
              <Clock className="w-6 h-6 text-blue-600" />
            </div>
            <p className="text-sm font-medium text-gray-900">{course.duration_weeks || 8} Weeks</p>
            <p className="text-xs text-gray-600">Duration</p>
          </div>
          
          <div className="text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mb-2">
              <BookOpen className="w-6 h-6 text-green-600" />
            </div>
            <p className="text-sm font-medium text-gray-900">{course.modules?.length || 0} Modules</p>
            <p className="text-xs text-gray-600">Learning Modules</p>
          </div>
          
          <div className="text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mb-2">
              <Target className="w-6 h-6 text-purple-600" />
            </div>
            <p className="text-sm font-medium text-gray-900">{course.cefr_level || 'B1'}</p>
            <p className="text-xs text-gray-600">CEFR Level</p>
          </div>
          
          <div className="text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-orange-100 rounded-lg mb-2">
              <Users className="w-6 h-6 text-orange-600" />
            </div>
            <p className="text-sm font-medium text-gray-900">
              {course.total_lessons || course.modules?.reduce((acc, mod) => acc + (mod.lessons?.length || 0), 0) || 0}
            </p>
            <p className="text-xs text-gray-600">Total Lessons</p>
          </div>
        </div>
      </div>

      {/* Learning Objectives */}
      {course.learning_objectives && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h4 className="font-semibold text-gray-900 mb-3">Learning Objectives</h4>
          <ul className="space-y-2">
            {course.learning_objectives.map((objective, index) => (
              <li key={index} className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                <span className="text-gray-700">{objective}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Course Features */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h4 className="font-semibold text-gray-900 mb-3">Course Features</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
            <span className="text-gray-700">Industry-specific vocabulary</span>
          </div>
          <div className="flex items-center">
            <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
            <span className="text-gray-700">Interactive exercises</span>
          </div>
          <div className="flex items-center">
            <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
            <span className="text-gray-700">Progressive assessments</span>
          </div>
          <div className="flex items-center">
            <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
            <span className="text-gray-700">Contextual learning</span>
          </div>
          <div className="flex items-center">
            <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
            <span className="text-gray-700">Real-world scenarios</span>
          </div>
          <div className="flex items-center">
            <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
            <span className="text-gray-700">Performance tracking</span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCurriculum = () => (
    <div className="space-y-4">
      {course.modules?.map((module, moduleIndex) => (
        <div key={module.id || moduleIndex} className="border border-gray-200 rounded-lg">
          <button
            onClick={() => toggleModule(module.id || moduleIndex)}
            className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50"
          >
            <div className="flex items-center">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                <span className="text-sm font-semibold text-blue-600">
                  {moduleIndex + 1}
                </span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">{module.title}</h4>
                <p className="text-sm text-gray-600">{module.description}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-500">
                {module.lessons?.length || 0} lessons
              </span>
              {expandedModules[module.id || moduleIndex] ? (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronRight className="w-5 h-5 text-gray-400" />
              )}
            </div>
          </button>

          <AnimatePresence>
            {expandedModules[module.id || moduleIndex] && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="border-t border-gray-100"
              >
                <div className="p-4 space-y-3">
                  {module.lessons?.map((lesson, lessonIndex) => (
                    <div key={lesson.id || lessonIndex} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                      <Play className="w-4 h-4 text-blue-500" />
                      <div className="flex-1">
                        <h5 className="font-medium text-gray-900">{lesson.title}</h5>
                        <p className="text-sm text-gray-600">{lesson.description}</p>
                        <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                          <span>{lesson.duration_minutes || 45} minutes</span>
                          <span>{lesson.exercises?.length || 0} exercises</span>
                        </div>
                      </div>
                      <button className="text-blue-600 hover:text-blue-800">
                        <Edit className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ))}
    </div>
  );

  const renderExercises = () => (
    <div className="space-y-4">
      {course.sample_exercises?.map((exercise, index) => (
        <div key={index} className="border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-gray-900">{exercise.title}</h4>
            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
              {exercise.type}
            </span>
          </div>
          <p className="text-gray-700 mb-3">{exercise.instructions}</p>
          
          {exercise.options && (
            <div className="space-y-2">
              {exercise.options.map((option, optionIndex) => (
                <div key={optionIndex} className="flex items-center space-x-2">
                  <div className="w-4 h-4 border border-gray-300 rounded"></div>
                  <span className="text-gray-700">{option}</span>
                </div>
              ))}
            </div>
          )}
          
          {exercise.sample_answer && (
            <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm font-medium text-green-800">Sample Answer:</p>
              <p className="text-sm text-green-700 mt-1">{exercise.sample_answer}</p>
            </div>
          )}
        </div>
      )) || (
        <div className="text-center py-8 text-gray-500">
          <PenTool className="w-12 h-12 mx-auto mb-4" />
          <p>Sample exercises will be available after generation is complete.</p>
        </div>
      )}
    </div>
  );

  const renderAssessments = () => (
    <div className="space-y-4">
      {course.assessments?.map((assessment, index) => (
        <div key={index} className="border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-gray-900">{assessment.title}</h4>
            <div className="flex items-center space-x-2">
              <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                {assessment.type}
              </span>
              <span className="text-sm text-gray-500">
                {assessment.duration} minutes
              </span>
            </div>
          </div>
          <p className="text-gray-700 mb-3">{assessment.description}</p>
          
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-900">Questions:</span>
              <span className="ml-2 text-gray-600">{assessment.question_count}</span>
            </div>
            <div>
              <span className="font-medium text-gray-900">Passing Score:</span>
              <span className="ml-2 text-gray-600">{assessment.passing_score}%</span>
            </div>
            <div>
              <span className="font-medium text-gray-900">Attempts:</span>
              <span className="ml-2 text-gray-600">{assessment.max_attempts}</span>
            </div>
          </div>
        </div>
      )) || (
        <div className="text-center py-8 text-gray-500">
          <BarChart className="w-12 h-12 mx-auto mb-4" />
          <p>Assessment details will be available after generation is complete.</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setSelectedTab(tab.id)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  selectedTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={selectedTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.2 }}
        >
          {selectedTab === 'overview' && renderOverview()}
          {selectedTab === 'curriculum' && renderCurriculum()}
          {selectedTab === 'exercises' && renderExercises()}
          {selectedTab === 'assessments' && renderAssessments()}
        </motion.div>
      </AnimatePresence>

      {/* Action Buttons */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-200">
        <button
          onClick={onRevise}
          className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Request Revision
        </button>

        <div className="flex space-x-3">
          <button
            onClick={() => toast.success('Course saved as draft')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Save as Draft
          </button>
          
          <button
            onClick={onApprove}
            className="flex items-center px-6 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700"
          >
            <CheckCircle className="w-4 h-4 mr-2" />
            Approve & Deploy
          </button>
        </div>
      </div>
    </div>
  );
};

export default CoursePreview;