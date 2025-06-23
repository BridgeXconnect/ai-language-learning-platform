import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, 
  Upload, 
  Settings, 
  BookOpen, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  ArrowRight,
  ArrowLeft
} from 'lucide-react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import toast from 'react-hot-toast';
import { aiAPI, salesAPI } from '../../services/api';
import DocumentUpload from './DocumentUpload';
import GenerationProgress from './GenerationProgress';
import CoursePreview from './CoursePreview';

const steps = [
  { id: 'request', title: 'Course Request', icon: FileText },
  { id: 'documents', title: 'Upload Documents', icon: Upload },
  { id: 'settings', title: 'AI Settings', icon: Settings },
  { id: 'generation', title: 'Generate Course', icon: BookOpen },
  { id: 'preview', title: 'Preview & Review', icon: CheckCircle }
];

const courseRequestSchema = yup.object({
  course_request_id: yup.number().required('Course request is required'),
  duration_weeks: yup.number().min(1).max(52).required('Duration is required'),
  lessons_per_week: yup.number().min(1).max(10).required('Lessons per week is required'),
  exercise_count_per_lesson: yup.number().min(1).max(20).required('Exercise count is required'),
  assessment_frequency: yup.string().oneOf(['module', 'week', 'lesson']).required(),
  difficulty_progression: yup.string().oneOf(['linear', 'adaptive', 'accelerated']).required(),
  focus_areas: yup.array().of(yup.string()).min(1).required('At least one focus area is required'),
  content_style: yup.string().oneOf(['formal', 'conversational', 'technical']).required(),
  include_cultural_context: yup.boolean(),
  target_industries: yup.array().of(yup.string()),
  custom_vocabulary: yup.string()
});

const CourseGenerationWizard = ({ isOpen, onClose, initialData = null }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [courseRequests, setCourseRequests] = useState([]);
  const [uploadedDocuments, setUploadedDocuments] = useState([]);
  const [generationJob, setGenerationJob] = useState(null);
  const [generatedCourse, setGeneratedCourse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors }
  } = useForm({
    resolver: yupResolver(courseRequestSchema),
    defaultValues: {
      duration_weeks: 8,
      lessons_per_week: 2,
      exercise_count_per_lesson: 5,
      assessment_frequency: 'module',
      difficulty_progression: 'linear',
      focus_areas: ['communication'],
      content_style: 'conversational',
      include_cultural_context: true,
      target_industries: [],
      custom_vocabulary: ''
    }
  });

  const focusAreas = [
    'communication', 'grammar', 'vocabulary', 'pronunciation', 
    'writing', 'reading', 'listening', 'speaking', 'business', 'technical'
  ];

  const industries = [
    'technology', 'finance', 'healthcare', 'manufacturing', 'retail',
    'education', 'hospitality', 'consulting', 'legal', 'media'
  ];

  useEffect(() => {
    if (isOpen) {
      fetchCourseRequests();
      if (initialData) {
        setValue('course_request_id', initialData.id);
      }
    }
  }, [isOpen, initialData]);

  const fetchCourseRequests = async () => {
    try {
      const response = await salesAPI.getCourseRequests({ status: 'submitted' });
      setCourseRequests(response.data.requests || []);
    } catch (error) {
      toast.error('Failed to fetch course requests');
    }
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleDocumentUpload = (documents) => {
    setUploadedDocuments(documents);
  };

  const handleGenerate = async (formData) => {
    setIsLoading(true);
    try {
      const response = await aiAPI.generateCourse({
        ...formData,
        uploaded_documents: uploadedDocuments.map(doc => doc.id)
      });
      
      setGenerationJob(response.data);
      handleNext(); // Move to generation progress step
      
      // Poll for completion
      pollGenerationStatus(response.data.job_id);
    } catch (error) {
      toast.error('Failed to start course generation');
      console.error('Generation error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const pollGenerationStatus = async (jobId) => {
    const interval = setInterval(async () => {
      try {
        const response = await aiAPI.getGenerationStatus(jobId);
        const status = response.data;
        
        if (status.status === 'completed') {
          clearInterval(interval);
          const resultResponse = await aiAPI.getGenerationResult(jobId);
          setGeneratedCourse(resultResponse.data);
          handleNext(); // Move to preview step
        } else if (status.status === 'failed') {
          clearInterval(interval);
          toast.error('Course generation failed');
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, 2000);

    // Cleanup after 10 minutes
    setTimeout(() => clearInterval(interval), 600000);
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Course Request
              </label>
              <select
                {...register('course_request_id')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a course request...</option>
                {courseRequests.map(request => (
                  <option key={request.id} value={request.id}>
                    {request.company_name} - {request.training_objectives}
                  </option>
                ))}
              </select>
              {errors.course_request_id && (
                <p className="text-red-500 text-sm mt-1">{errors.course_request_id.message}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Duration (weeks)
                </label>
                <input
                  type="number"
                  min="1"
                  max="52"
                  {...register('duration_weeks')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {errors.duration_weeks && (
                  <p className="text-red-500 text-sm mt-1">{errors.duration_weeks.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Lessons per week
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  {...register('lessons_per_week')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {errors.lessons_per_week && (
                  <p className="text-red-500 text-sm mt-1">{errors.lessons_per_week.message}</p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Focus Areas
              </label>
              <div className="grid grid-cols-3 gap-2">
                {focusAreas.map(area => (
                  <label key={area} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      value={area}
                      {...register('focus_areas')}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm capitalize">{area}</span>
                  </label>
                ))}
              </div>
              {errors.focus_areas && (
                <p className="text-red-500 text-sm mt-1">{errors.focus_areas.message}</p>
              )}
            </div>
          </div>
        );

      case 1:
        return (
          <DocumentUpload
            onUpload={handleDocumentUpload}
            uploadedDocuments={uploadedDocuments}
          />
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Assessment Frequency
                </label>
                <select
                  {...register('assessment_frequency')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="module">Per Module</option>
                  <option value="week">Weekly</option>
                  <option value="lesson">Per Lesson</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Difficulty Progression
                </label>
                <select
                  {...register('difficulty_progression')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="linear">Linear</option>
                  <option value="adaptive">Adaptive</option>
                  <option value="accelerated">Accelerated</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Content Style
              </label>
              <select
                {...register('content_style')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="formal">Formal</option>
                <option value="conversational">Conversational</option>
                <option value="technical">Technical</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Industries (optional)
              </label>
              <div className="grid grid-cols-3 gap-2">
                {industries.map(industry => (
                  <label key={industry} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      value={industry}
                      {...register('target_industries')}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm capitalize">{industry}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  {...register('include_cultural_context')}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm">Include cultural context</span>
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom Vocabulary (optional)
              </label>
              <textarea
                {...register('custom_vocabulary')}
                rows={4}
                placeholder="Add specific terms or vocabulary that should be included..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        );

      case 3:
        return (
          <GenerationProgress
            job={generationJob}
            onComplete={(course) => setGeneratedCourse(course)}
          />
        );

      case 4:
        return (
          <CoursePreview
            course={generatedCourse}
            onApprove={() => {
              toast.success('Course generated successfully!');
              onClose();
            }}
            onRevise={() => setCurrentStep(0)}
          />
        );

      default:
        return null;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              AI Course Generation
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          </div>

          {/* Step Indicator */}
          <div className="flex items-center justify-between mt-4">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isActive = index === currentStep;
              const isCompleted = index < currentStep;

              return (
                <div key={step.id} className="flex items-center">
                  <div
                    className={`flex items-center justify-center w-10 h-10 rounded-full ${
                      isCompleted
                        ? 'bg-green-500 text-white'
                        : isActive
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-500'
                    }`}
                  >
                    {isCompleted ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <Icon className="w-5 h-5" />
                    )}
                  </div>
                  <span
                    className={`ml-2 text-sm ${
                      isActive ? 'font-medium' : 'text-gray-500'
                    }`}
                  >
                    {step.title}
                  </span>
                  {index < steps.length - 1 && (
                    <ArrowRight className="w-4 h-4 text-gray-300 mx-4" />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-6 overflow-y-auto max-h-[60vh]">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {renderStepContent()}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-between">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Previous
          </button>

          {currentStep === 3 ? (
            <button
              onClick={handleSubmit(handleGenerate)}
              disabled={isLoading}
              className="flex items-center px-6 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Generate Course
            </button>
          ) : currentStep === steps.length - 1 ? (
            <button
              onClick={() => toast.success('Course approved!')}
              className="flex items-center px-6 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700"
            >
              <CheckCircle className="w-4 h-4 mr-2" />
              Approve Course
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
            >
              Next
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default CourseGenerationWizard;