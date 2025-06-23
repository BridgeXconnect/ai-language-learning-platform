import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/auth_context';
import { 
  BuildingOfficeIcon, 
  UserGroupIcon, 
  DocumentTextIcon,
  SparklesIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowRightIcon,
  ArrowLeftIcon,
  CloudArrowUpIcon,
  XMarkIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import api from '../../services/api';

const NewCourseRequestWizard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // Wizard state
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  
  // Form data with smart defaults
  const [formData, setFormData] = useState({
    // Company Information
    company_name: '',
    industry: '',
    contact_person: '',
    contact_email: user?.email || '',
    contact_phone: '',
    
    // Training Details
    cohort_size: 10,
    current_cefr: 'B1',
    target_cefr: 'B2',
    training_objectives: '',
    pain_points: '',
    specific_requirements: '',
    
    // Course Preferences
    course_length_hours: 40,
    lessons_per_module: 4,
    delivery_method: 'blended',
    preferred_schedule: '',
    priority: 'normal',
    internal_notes: ''
  });

  // File upload state
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);

  const steps = [
    { 
      id: 1, 
      title: 'Company Info', 
      subtitle: 'Tell us about your client',
      icon: BuildingOfficeIcon,
      color: 'blue'
    },
    { 
      id: 2, 
      title: 'Training Needs', 
      subtitle: 'Define learning objectives',
      icon: UserGroupIcon,
      color: 'purple'
    },
    { 
      id: 3, 
      title: 'Documents', 
      subtitle: 'Upload SOPs & materials',
      icon: DocumentTextIcon,
      color: 'green'
    },
    { 
      id: 4, 
      title: 'Review & Submit', 
      subtitle: 'Confirm and send request',
      icon: SparklesIcon,
      color: 'amber'
    }
  ];

  const industries = [
    'Technology', 'Finance', 'Healthcare', 'Manufacturing', 'Retail',
    'Education', 'Government', 'Energy', 'Transportation', 'Hospitality'
  ];

  const cefrLevels = [
    { value: 'A1', label: 'A1 - Beginner', description: 'Basic words and phrases' },
    { value: 'A2', label: 'A2 - Elementary', description: 'Simple conversations' },
    { value: 'B1', label: 'B1 - Intermediate', description: 'Work and travel topics' },
    { value: 'B2', label: 'B2 - Upper Intermediate', description: 'Complex discussions' },
    { value: 'C1', label: 'C1 - Advanced', description: 'Professional fluency' },
    { value: 'C2', label: 'C2 - Proficiency', description: 'Near-native level' }
  ];

  const deliveryMethods = [
    { value: 'in_person', label: 'In-Person', description: 'Traditional classroom setting' },
    { value: 'virtual', label: 'Virtual', description: 'Online video sessions' },
    { value: 'blended', label: 'Blended', description: 'Mix of online and in-person' }
  ];

  // Smart validation with helpful messages
  const validateStep = (step) => {
    const errors = {};
    
    switch (step) {
      case 1:
        if (!formData.company_name.trim()) {
          errors.company_name = 'Company name is required';
        }
        if (!formData.contact_person.trim()) {
          errors.contact_person = 'Contact person is required';
        }
        if (!formData.contact_email.trim()) {
          errors.contact_email = 'Contact email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.contact_email)) {
          errors.contact_email = 'Please enter a valid email address';
        }
        break;
        
      case 2:
        if (!formData.training_objectives.trim()) {
          errors.training_objectives = 'Please describe the training objectives';
        } else if (formData.training_objectives.trim().length < 20) {
          errors.training_objectives = 'Please provide more detail about the objectives';
        }
        if (formData.cohort_size < 1 || formData.cohort_size > 1000) {
          errors.cohort_size = 'Cohort size must be between 1 and 1000';
        }
        break;
        
      case 3:
        if (uploadedFiles.length === 0) {
          errors.files = 'Please upload at least one SOP document';
        }
        break;
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear validation error when user starts typing
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, steps.length));
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  // File upload handling
  const handleFileUpload = (files) => {
    const validFiles = Array.from(files).filter(file => {
      const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
      return validTypes.includes(file.type) && file.size <= 50 * 1024 * 1024; // 50MB limit
    });

    setUploadedFiles(prev => [...prev, ...validFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'ready',
      progress: 0
    }))]);
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  // Drag and drop handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files);
    }
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;
    
    setIsSubmitting(true);
    try {
      // Submit the request
      const response = await api.post('/api/sales/course-requests', formData);
      
      // Upload files if any
      if (uploadedFiles.length > 0) {
        const requestId = response.data.id;
        const formData = new FormData();
        
        for (const fileItem of uploadedFiles) {
          formData.append('files', fileItem.file);
        }
        
        await api.post(`/api/sales/course-requests/${requestId}/sop`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      }
      
      // Show success and redirect
      navigate('/sales/requests', { 
        state: { 
          message: 'Course request submitted successfully! You\'ll receive updates as we process your request.',
          type: 'success'
        }
      });
      
    } catch (error) {
      console.error('Error submitting request:', error);
      setValidationErrors({ submit: 'Failed to submit request. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Dynamic progress calculation
  const getProgress = () => {
    let progress = 0;
    const stepWeight = 25;
    
    // Step 1 completion
    if (formData.company_name && formData.contact_person && formData.contact_email) {
      progress += stepWeight;
    }
    
    // Step 2 completion
    if (formData.training_objectives && formData.cohort_size) {
      progress += stepWeight;
    }
    
    // Step 3 completion
    if (uploadedFiles.length > 0) {
      progress += stepWeight;
    }
    
    // Current step partial progress
    if (currentStep <= 3) {
      progress += ((currentStep - 1) * stepWeight) / 4;
    } else {
      progress = 100;
    }
    
    return Math.min(progress, 100);
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6 animate-fade-in">
            <div className="text-center mb-8">
              <BuildingOfficeIcon className="h-12 w-12 text-blue-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Company Information</h2>
              <p className="text-gray-600">Let's start with basic information about your client</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="form-label">Company Name *</label>
                <input
                  type="text"
                  name="company_name"
                  value={formData.company_name}
                  onChange={handleInputChange}
                  className={`form-input ${validationErrors.company_name ? 'form-input-error' : ''}`}
                  placeholder="e.g., TechCorp International"
                />
                {validationErrors.company_name && (
                  <p className="form-error">{validationErrors.company_name}</p>
                )}
              </div>

              <div>
                <label className="form-label">Industry</label>
                <select
                  name="industry"
                  value={formData.industry}
                  onChange={handleInputChange}
                  className="form-input"
                >
                  <option value="">Select industry...</option>
                  {industries.map(industry => (
                    <option key={industry} value={industry}>{industry}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="form-label">Contact Person *</label>
                <input
                  type="text"
                  name="contact_person"
                  value={formData.contact_person}
                  onChange={handleInputChange}
                  className={`form-input ${validationErrors.contact_person ? 'form-input-error' : ''}`}
                  placeholder="Full name of main contact"
                />
                {validationErrors.contact_person && (
                  <p className="form-error">{validationErrors.contact_person}</p>
                )}
              </div>

              <div>
                <label className="form-label">Contact Email *</label>
                <input
                  type="email"
                  name="contact_email"
                  value={formData.contact_email}
                  onChange={handleInputChange}
                  className={`form-input ${validationErrors.contact_email ? 'form-input-error' : ''}`}
                  placeholder="contact@company.com"
                />
                {validationErrors.contact_email && (
                  <p className="form-error">{validationErrors.contact_email}</p>
                )}
              </div>

              <div className="md:col-span-2">
                <label className="form-label">Contact Phone</label>
                <input
                  type="tel"
                  name="contact_phone"
                  value={formData.contact_phone}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="+1 (555) 123-4567"
                />
                <p className="form-help">Optional: Include country code for international clients</p>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6 animate-fade-in">
            <div className="text-center mb-8">
              <UserGroupIcon className="h-12 w-12 text-purple-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Training Requirements</h2>
              <p className="text-gray-600">Define the learning objectives and group details</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-gray-50 p-4 rounded-lg">
                <label className="form-label">Cohort Size *</label>
                <input
                  type="number"
                  name="cohort_size"
                  value={formData.cohort_size}
                  onChange={handleInputChange}
                  min="1"
                  max="1000"
                  className={`form-input ${validationErrors.cohort_size ? 'form-input-error' : ''}`}
                />
                {validationErrors.cohort_size && (
                  <p className="form-error">{validationErrors.cohort_size}</p>
                )}
                <p className="form-help">Number of students in the group</p>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <label className="form-label">Current CEFR Level</label>
                <select
                  name="current_cefr"
                  value={formData.current_cefr}
                  onChange={handleInputChange}
                  className="form-input"
                >
                  {cefrLevels.map(level => (
                    <option key={level.value} value={level.value}>
                      {level.label}
                    </option>
                  ))}
                </select>
                <p className="form-help">{cefrLevels.find(l => l.value === formData.current_cefr)?.description}</p>
              </div>

              <div className="bg-green-50 p-4 rounded-lg">
                <label className="form-label">Target CEFR Level</label>
                <select
                  name="target_cefr"
                  value={formData.target_cefr}
                  onChange={handleInputChange}
                  className="form-input"
                >
                  {cefrLevels.map(level => (
                    <option key={level.value} value={level.value}>
                      {level.label}
                    </option>
                  ))}
                </select>
                <p className="form-help">{cefrLevels.find(l => l.value === formData.target_cefr)?.description}</p>
              </div>
            </div>

            <div>
              <label className="form-label">Training Objectives *</label>
              <textarea
                name="training_objectives"
                value={formData.training_objectives}
                onChange={handleInputChange}
                rows={4}
                className={`form-input ${validationErrors.training_objectives ? 'form-input-error' : ''}`}
                placeholder="Describe the specific learning goals and outcomes you want to achieve. What should students be able to do after completing this course?"
              />
              {validationErrors.training_objectives && (
                <p className="form-error">{validationErrors.training_objectives}</p>
              )}
              <div className="flex justify-between">
                <p className="form-help">Be specific about skills, scenarios, and outcomes</p>
                <span className="text-xs text-gray-400">{formData.training_objectives.length}/500</span>
              </div>
            </div>

            <div>
              <label className="form-label">Current Pain Points</label>
              <textarea
                name="pain_points"
                value={formData.pain_points}
                onChange={handleInputChange}
                rows={3}
                className="form-input"
                placeholder="What are the main English language challenges the team currently faces? (e.g., presentations, client meetings, technical documentation)"
              />
              <p className="form-help">This helps us focus on the most relevant scenarios</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="form-label">Course Length (Hours)</label>
                <select
                  name="course_length_hours"
                  value={formData.course_length_hours}
                  onChange={handleInputChange}
                  className="form-input"
                >
                  <option value={20}>20 hours (Intensive)</option>
                  <option value={40}>40 hours (Standard)</option>
                  <option value={60}>60 hours (Comprehensive)</option>
                  <option value={80}>80 hours (Extended)</option>
                </select>
              </div>

              <div>
                <label className="form-label">Delivery Method</label>
                <div className="space-y-3">
                  {deliveryMethods.map(method => (
                    <label key={method.value} className="flex items-start space-x-3">
                      <input
                        type="radio"
                        name="delivery_method"
                        value={method.value}
                        checked={formData.delivery_method === method.value}
                        onChange={handleInputChange}
                        className="mt-1"
                      />
                      <div>
                        <div className="font-medium text-gray-900">{method.label}</div>
                        <div className="text-sm text-gray-500">{method.description}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6 animate-fade-in">
            <div className="text-center mb-8">
              <DocumentTextIcon className="h-12 w-12 text-green-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Documents</h2>
              <p className="text-gray-600">Share SOPs and materials to customize the course content</p>
            </div>

            {/* File Upload Zone */}
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive 
                  ? 'border-blue-400 bg-blue-50' 
                  : validationErrors.files 
                    ? 'border-red-300 bg-red-50' 
                    : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <CloudArrowUpIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <div className="space-y-2">
                <p className="text-lg font-medium text-gray-900">
                  Drop your files here, or{' '}
                  <label className="text-blue-600 hover:text-blue-500 cursor-pointer">
                    browse
                    <input
                      type="file"
                      multiple
                      accept=".pdf,.doc,.docx,.txt"
                      onChange={(e) => handleFileUpload(e.target.files)}
                      className="hidden"
                    />
                  </label>
                </p>
                <p className="text-sm text-gray-500">
                  PDF, Word, or text files up to 50MB each
                </p>
              </div>
            </div>

            {validationErrors.files && (
              <div className="flex items-center space-x-2 text-red-600 text-sm">
                <ExclamationTriangleIcon className="h-4 w-4" />
                <span>{validationErrors.files}</span>
              </div>
            )}

            {/* Uploaded Files List */}
            {uploadedFiles.length > 0 && (
              <div className="space-y-3">
                <h3 className="font-medium text-gray-900">Uploaded Documents</h3>
                {uploadedFiles.map((fileItem) => (
                  <div key={fileItem.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <DocumentTextIcon className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{fileItem.file.name}</p>
                        <p className="text-xs text-gray-500">
                          {(fileItem.file.size / 1024 / 1024).toFixed(1)} MB
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(fileItem.id)}
                      className="p-1 text-gray-400 hover:text-red-500"
                    >
                      <XMarkIcon className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Upload Tips */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <InformationCircleIcon className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-blue-900">Tips for better course customization:</h4>
                  <ul className="mt-2 text-sm text-blue-700 space-y-1">
                    <li>• Include company-specific procedures and workflows</li>
                    <li>• Upload glossaries with technical terms and jargon</li>
                    <li>• Share sample communications (emails, reports, presentations)</li>
                    <li>• Include organizational charts if relevant to communication flows</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6 animate-fade-in">
            <div className="text-center mb-8">
              <SparklesIcon className="h-12 w-12 text-amber-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Review & Submit</h2>
              <p className="text-gray-600">Review your request and submit for processing</p>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="card">
                <div className="card-header">
                  <h3 className="font-semibold text-gray-900">Company Details</h3>
                </div>
                <div className="card-body space-y-2">
                  <p><span className="font-medium">Company:</span> {formData.company_name}</p>
                  <p><span className="font-medium">Industry:</span> {formData.industry || 'Not specified'}</p>
                  <p><span className="font-medium">Contact:</span> {formData.contact_person}</p>
                  <p><span className="font-medium">Email:</span> {formData.contact_email}</p>
                </div>
              </div>

              <div className="card">
                <div className="card-header">
                  <h3 className="font-semibold text-gray-900">Training Details</h3>
                </div>
                <div className="card-body space-y-2">
                  <p><span className="font-medium">Cohort Size:</span> {formData.cohort_size} students</p>
                  <p><span className="font-medium">CEFR Level:</span> {formData.current_cefr} → {formData.target_cefr}</p>
                  <p><span className="font-medium">Duration:</span> {formData.course_length_hours} hours</p>
                  <p><span className="font-medium">Delivery:</span> {deliveryMethods.find(m => m.value === formData.delivery_method)?.label}</p>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h3 className="font-semibold text-gray-900">Training Objectives</h3>
              </div>
              <div className="card-body">
                <p className="text-gray-700">{formData.training_objectives}</p>
              </div>
            </div>

            {uploadedFiles.length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h3 className="font-semibold text-gray-900">Uploaded Documents</h3>
                </div>
                <div className="card-body">
                  <ul className="space-y-2">
                    {uploadedFiles.map((fileItem) => (
                      <li key={fileItem.id} className="flex items-center space-x-2">
                        <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                        <span className="text-sm">{fileItem.file.name}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Internal Notes */}
            <div>
              <label className="form-label">Internal Notes (Optional)</label>
              <textarea
                name="internal_notes"
                value={formData.internal_notes}
                onChange={handleInputChange}
                rows={3}
                className="form-input"
                placeholder="Add any internal notes or special considerations for the course manager..."
              />
              <p className="form-help">These notes are only visible to the internal team</p>
            </div>

            {validationErrors.submit && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 text-red-700">
                  <ExclamationTriangleIcon className="h-5 w-5" />
                  <span>{validationErrors.submit}</span>
                </div>
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Progress Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-gray-900">New Course Request</h1>
            <span className="text-sm text-gray-500">Step {currentStep} of {steps.length}</span>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${getProgress()}%` }}
            ></div>
          </div>
          
          {/* Step Indicators */}
          <div className="flex justify-between">
            {steps.map((step) => {
              const Icon = step.icon;
              const isActive = currentStep === step.id;
              const isCompleted = currentStep > step.id;
              
              return (
                <div key={step.id} className="flex flex-col items-center">
                  <div className={`
                    w-10 h-10 rounded-full flex items-center justify-center mb-2 transition-colors
                    ${isCompleted ? 'bg-green-600 text-white' : 
                      isActive ? 'bg-blue-600 text-white' : 
                      'bg-gray-200 text-gray-400'}
                  `}>
                    {isCompleted ? (
                      <CheckCircleIcon className="h-5 w-5" />
                    ) : (
                      <Icon className="h-5 w-5" />
                    )}
                  </div>
                  <div className="text-center">
                    <p className={`text-sm font-medium ${isActive || isCompleted ? 'text-gray-900' : 'text-gray-500'}`}>
                      {step.title}
                    </p>
                    <p className="text-xs text-gray-400 hidden sm:block">
                      {step.subtitle}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          {renderStepContent()}
          
          {/* Navigation Buttons */}
          <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
            <button
              onClick={handlePrevious}
              disabled={currentStep === 1}
              className="btn btn-ghost disabled:opacity-50"
            >
              <ArrowLeftIcon className="h-4 w-4" />
              Previous
            </button>
            
            <div className="flex space-x-3">
              {currentStep < steps.length ? (
                <button
                  onClick={handleNext}
                  className="btn btn-primary"
                >
                  Next Step
                  <ArrowRightIcon className="h-4 w-4" />
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                  className="btn btn-success btn-lg"
                >
                  {isSubmitting ? (
                    <>
                      <div className="loading-spinner" />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="h-5 w-5" />
                      Submit Request
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewCourseRequestWizard; 