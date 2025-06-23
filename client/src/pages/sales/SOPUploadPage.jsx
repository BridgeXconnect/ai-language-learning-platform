import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Building, 
  Upload,
  FileText,
  CheckCircle,
  AlertCircle,
  Lightbulb,
  Zap
} from 'lucide-react';
import toast from 'react-hot-toast';
import { salesAPI, aiAPI } from '../../services/api';
import DocumentUpload from '../../components/ai/DocumentUpload';
import CourseGenerationWizard from '../../components/ai/CourseGenerationWizard';

const SOPUploadPage = () => {
  const { requestId } = useParams();
  const navigate = useNavigate();
  
  const [courseRequest, setCourseRequest] = useState(null);
  const [uploadedDocuments, setUploadedDocuments] = useState([]);
  const [isGenerationWizardOpen, setIsGenerationWizardOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchCourseRequest();
  }, [requestId]);

  const fetchCourseRequest = async () => {
    try {
      const response = await salesAPI.getCourseRequest(requestId);
      setCourseRequest(response.data);
      
      // Fetch existing documents if any
      if (response.data.sop_documents) {
        setUploadedDocuments(response.data.sop_documents);
      }
    } catch (error) {
      toast.error('Failed to load course request');
      navigate('/sales/course-requests');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDocumentsUploaded = (documents) => {
    setUploadedDocuments(documents);
  };

  const handleGenerateCourse = () => {
    if (uploadedDocuments.length === 0) {
      toast.error('Please upload at least one document before generating a course');
      return;
    }
    
    setIsGenerationWizardOpen(true);
  };

  const handleBackToRequests = () => {
    navigate('/sales/course-requests');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!courseRequest) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Course Request Not Found</h2>
          <p className="text-gray-600 mb-4">The requested course request could not be found.</p>
          <button
            onClick={handleBackToRequests}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Back to Course Requests
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={handleBackToRequests}
            className="flex items-center text-blue-600 hover:text-blue-800 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Course Requests
          </button>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Upload SOP Documents
              </h1>
              <p className="text-gray-600 mt-1">
                Upload Standard Operating Procedures to generate AI-powered course content
              </p>
            </div>
            
            <div className="hidden md:flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">Course Request ID</p>
                <p className="text-sm text-gray-600">#{requestId}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Course Request Summary */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8"
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Building className="w-6 h-6 text-blue-600" />
                  </div>
                </div>
                
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {courseRequest.company_name}
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Industry:</span>
                      <span className="ml-2 text-gray-600">{courseRequest.industry}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Cohort Size:</span>
                      <span className="ml-2 text-gray-600">{courseRequest.cohort_size} learners</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Current Level:</span>
                      <span className="ml-2 text-gray-600">{courseRequest.current_cefr}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Target Level:</span>
                      <span className="ml-2 text-gray-600">{courseRequest.target_cefr}</span>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <h4 className="font-medium text-gray-700 mb-1">Training Objectives:</h4>
                    <p className="text-gray-600 text-sm">{courseRequest.training_objectives}</p>
                  </div>
                  
                  {courseRequest.pain_points && (
                    <div className="mt-4">
                      <h4 className="font-medium text-gray-700 mb-1">Pain Points:</h4>
                      <p className="text-gray-600 text-sm">{courseRequest.pain_points}</p>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>

            {/* Document Upload Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
            >
              <div className="flex items-center space-x-3 mb-6">
                <Upload className="w-6 h-6 text-blue-600" />
                <h2 className="text-xl font-semibold text-gray-900">
                  Upload SOP Documents
                </h2>
              </div>
              
              <DocumentUpload
                onUpload={handleDocumentsUploaded}
                uploadedDocuments={uploadedDocuments}
              />
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* AI Generation CTA */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6"
            >
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Zap className="w-6 h-6 text-blue-600" />
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Ready to Generate?
                </h3>
                
                <p className="text-sm text-gray-600 mb-4">
                  Once you've uploaded your SOP documents, our AI will create a customized 
                  English course tailored to your organization's needs.
                </p>
                
                <button
                  onClick={handleGenerateCourse}
                  disabled={uploadedDocuments.length === 0}
                  className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Zap className="w-4 h-4 mr-2" />
                  Generate AI Course
                </button>
                
                {uploadedDocuments.length === 0 && (
                  <p className="text-xs text-gray-500 mt-2">
                    Upload documents to enable course generation
                  </p>
                )}
              </div>
            </motion.div>

            {/* Process Overview */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white border border-gray-200 rounded-lg p-6"
            >
              <h3 className="font-semibold text-gray-900 mb-4">How It Works</h3>
              
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-xs font-semibold text-blue-600">1</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 text-sm">Upload Documents</h4>
                    <p className="text-xs text-gray-600 mt-1">
                      Upload SOPs, training materials, and company documents
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-xs font-semibold text-blue-600">2</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 text-sm">AI Analysis</h4>
                    <p className="text-xs text-gray-600 mt-1">
                      Our AI analyzes content and extracts key learning points
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-xs font-semibold text-blue-600">3</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 text-sm">Course Generation</h4>
                    <p className="text-xs text-gray-600 mt-1">
                      Customized lessons, exercises, and assessments are created
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-3 h-3 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 text-sm">Review & Deploy</h4>
                    <p className="text-xs text-gray-600 mt-1">
                      Preview, customize, and deploy your course
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Tips */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-amber-50 border border-amber-200 rounded-lg p-6"
            >
              <div className="flex items-start space-x-3">
                <Lightbulb className="w-5 h-5 text-amber-600 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-amber-900 mb-2">Pro Tips</h3>
                  <ul className="text-sm text-amber-800 space-y-2">
                    <li>• Upload multiple documents for richer content</li>
                    <li>• Include glossaries and terminology lists</li>
                    <li>• Use clear, well-formatted documents</li>
                    <li>• Add workflow diagrams if available</li>
                  </ul>
                </div>
              </div>
            </motion.div>

            {/* Document Stats */}
            {uploadedDocuments.length > 0 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="bg-white border border-gray-200 rounded-lg p-6"
              >
                <h3 className="font-semibold text-gray-900 mb-4">Upload Summary</h3>
                
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Documents Uploaded</span>
                    <span className="font-medium text-gray-900">{uploadedDocuments.length}</span>
                  </div>
                  
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Processing Status</span>
                    <span className="font-medium text-gray-900">
                      {uploadedDocuments.filter(doc => doc.status === 'completed').length} / {uploadedDocuments.length} Complete
                    </span>
                  </div>
                  
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Total Size</span>
                    <span className="font-medium text-gray-900">
                      {(uploadedDocuments.reduce((acc, doc) => acc + doc.size, 0) / (1024 * 1024)).toFixed(1)} MB
                    </span>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>

      {/* Course Generation Wizard */}
      <CourseGenerationWizard
        isOpen={isGenerationWizardOpen}
        onClose={() => setIsGenerationWizardOpen(false)}
        initialData={courseRequest}
      />
    </div>
  );
};

export default SOPUploadPage;