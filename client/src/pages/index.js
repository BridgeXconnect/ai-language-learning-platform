// client/src/components/layout/Navbar.jsx
import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/auth_context';
import { 
  UserIcon, 
  BellIcon, 
  ChevronDownIcon,
  BookOpenIcon,
  DocumentTextIcon,
  AcademicCapIcon,
  PresentationChartBarIcon
} from '@heroicons/react/24/outline';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getNavigationItems = () => {
    if (!user) return [];

    const baseItems = [
      { name: 'Dashboard', href: '/dashboard', icon: PresentationChartBarIcon }
    ];

    switch (user.role) {
      case 'sales':
        return [
          ...baseItems,
          { name: 'New Request', href: '/sales/new-request', icon: DocumentTextIcon },
          { name: 'My Requests', href: '/sales/requests', icon: DocumentTextIcon }
        ];
      case 'course_manager':
        return [
          ...baseItems,
          { name: 'Course Reviews', href: '/course-manager/reviews', icon: AcademicCapIcon },
          { name: 'Content Library', href: '/course-manager/library', icon: BookOpenIcon },
          { name: 'User Management', href: '/course-manager/users', icon: UserIcon }
        ];
      case 'trainer':
        return [
          ...baseItems,
          { name: 'My Courses', href: '/trainer/courses', icon: AcademicCapIcon },
          { name: 'Students', href: '/trainer/students', icon: UserIcon },
          { name: 'Schedule', href: '/trainer/schedule', icon: DocumentTextIcon }
        ];
      case 'student':
        return [
          ...baseItems,
          { name: 'My Courses', href: '/student/courses', icon: BookOpenIcon },
          { name: 'Progress', href: '/student/progress', icon: AcademicCapIcon }
        ];
      default:
        return baseItems;
    }
  };

  const navigationItems = getNavigationItems();

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link to="/dashboard" className="text-xl font-bold text-blue-600">
                AI Language Learning
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`${
                      isActive
                        ? 'border-blue-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>
          <div className="flex items-center">
            <button className="p-2 text-gray-400 hover:text-gray-500">
              <BellIcon className="h-6 w-6" />
            </button>
            <div className="ml-3 relative">
              <div className="flex items-center text-sm">
                <UserIcon className="h-8 w-8 text-gray-400 mr-2" />
                <span className="text-gray-700">{user?.username}</span>
                <button
                  onClick={handleLogout}
                  className="ml-4 bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

// client/src/components/layout/Layout.jsx
import React from 'react';
import Navbar from './Navbar';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;

// client/src/components/common/LoadingSpinner.jsx
import React from 'react';

const LoadingSpinner = ({ size = 'medium', text = 'Loading...' }) => {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-8 w-8',
    large: 'h-12 w-12'
  };

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className={`animate-spin rounded-full border-2 border-gray-300 border-t-blue-600 ${sizeClasses[size]}`}></div>
      {text && <p className="mt-2 text-sm text-gray-600">{text}</p>}
    </div>
  );
};

export default LoadingSpinner;

// client/src/components/common/StatusBadge.jsx
import React from 'react';

const StatusBadge = ({ status, size = 'medium' }) => {
  const getStatusStyles = (status) => {
    const statusMap = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      generating: 'bg-blue-100 text-blue-800',
      needs_revision: 'bg-orange-100 text-orange-800',
      completed: 'bg-green-100 text-green-800',
      in_progress: 'bg-blue-100 text-blue-800'
    };
    return statusMap[status] || 'bg-gray-100 text-gray-800';
  };

  const sizeClasses = {
    small: 'px-2 py-1 text-xs',
    medium: 'px-3 py-1 text-sm',
    large: 'px-4 py-2 text-base'
  };

  return (
    <span className={`inline-flex items-center font-medium rounded-full ${getStatusStyles(status)} ${sizeClasses[size]}`}>
      {status.replace('_', ' ').toUpperCase()}
    </span>
  );
};

export default StatusBadge;

// client/src/pages/sales/NewRequestPage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/auth_context';
import api from '../../services/api';
import Layout from '../../components/layout/Layout';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const NewRequestPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  
  const [formData, setFormData] = useState({
    // Client Information
    companyName: '',
    industry: '',
    contactName: '',
    contactEmail: '',
    contactPhone: '',
    
    // Training Details
    courseTitle: '',
    cohortSize: '',
    currentCefr: 'A1',
    targetCefr: 'A2',
    trainingObjectives: '',
    painPoints: '',
    
    // Course Structure
    courseLengthHours: '',
    lessonsPerWeek: '',
    deliveryMethod: 'in_person',
    
    // SOPs
    sopFiles: []
  });

  const [errors, setErrors] = useState({});

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    setFormData(prev => ({
      ...prev,
      sopFiles: [...prev.sopFiles, ...files]
    }));
  };

  const removeFile = (index) => {
    setFormData(prev => ({
      ...prev,
      sopFiles: prev.sopFiles.filter((_, i) => i !== index)
    }));
  };

  const validateStep = (step) => {
    const newErrors = {};
    
    if (step === 1) {
      if (!formData.companyName) newErrors.companyName = 'Company name is required';
      if (!formData.contactName) newErrors.contactName = 'Contact name is required';
      if (!formData.contactEmail) newErrors.contactEmail = 'Contact email is required';
      if (formData.contactEmail && !/\S+@\S+\.\S+/.test(formData.contactEmail)) {
        newErrors.contactEmail = 'Invalid email format';
      }
    } else if (step === 2) {
      if (!formData.courseTitle) newErrors.courseTitle = 'Course title is required';
      if (!formData.cohortSize) newErrors.cohortSize = 'Cohort size is required';
      if (!formData.trainingObjectives) newErrors.trainingObjectives = 'Training objectives are required';
    } else if (step === 3) {
      if (!formData.courseLengthHours) newErrors.courseLengthHours = 'Course length is required';
      if (!formData.lessonsPerWeek) newErrors.lessonsPerWeek = 'Lessons per week is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => prev - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateStep(currentStep)) return;
    
    setLoading(true);
    
    try {
      // Create FormData for file upload
      const submitData = new FormData();
      
      // Add text fields
      Object.keys(formData).forEach(key => {
        if (key !== 'sopFiles') {
          submitData.append(key, formData[key]);
        }
      });
      
      // Add files
      formData.sopFiles.forEach(file => {
        submitData.append('sopFiles', file);
      });
      
      const response = await api.post('/sales/course-request', submitData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      if (response.data.success) {
        navigate('/sales/requests', { 
          state: { message: 'Course request submitted successfully!' }
        });
      }
    } catch (error) {
      console.error('Error submitting request:', error);
      setErrors({ submit: 'Failed to submit request. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900">Client Information</h3>
            
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Company Name *
                </label>
                <input
                  type="text"
                  name="companyName"
                  value={formData.companyName}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
                {errors.companyName && <p className="mt-1 text-sm text-red-600">{errors.companyName}</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Industry
                </label>
                <input
                  type="text"
                  name="industry"
                  value={formData.industry}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Contact Name *
                </label>
                <input
                  type="text"
                  name="contactName"
                  value={formData.contactName}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
                {errors.contactName && <p className="mt-1 text-sm text-red-600">{errors.contactName}</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Contact Email *
                </label>
                <input
                  type="email"
                  name="contactEmail"
                  value={formData.contactEmail}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
                {errors.contactEmail && <p className="mt-1 text-sm text-red-600">{errors.contactEmail}</p>}
              </div>
              
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700">
                  Contact Phone
                </label>
                <input
                  type="tel"
                  name="contactPhone"
                  value={formData.contactPhone}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        );
        
      case 2:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900">Training Requirements</h3>
            
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700">
                  Course Title *
                </label>
                <input
                  type="text"
                  name="courseTitle"
                  value={formData.courseTitle}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
                {errors.courseTitle && <p className="mt-1 text-sm text-red-600">{errors.courseTitle}</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Cohort Size *
                </label>
                <input
                  type="number"
                  name="cohortSize"
                  value={formData.cohortSize}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
                {errors.cohortSize && <p className="mt-1 text-sm text-red-600">{errors.cohortSize}</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Current CEFR Level
                </label>
                <select
                  name="currentCefr"
                  value={formData.currentCefr}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="A1">A1 - Beginner</option>
                  <option value="A2">A2 - Elementary</option>
                  <option value="B1">B1 - Intermediate</option>
                  <option value="B2">B2 - Upper Intermediate</option>
                  <option value="C1">C1 - Advanced</option>
                  <option value="C2">C2 - Proficient</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Target CEFR Level
                </label>
                <select
                  name="targetCefr"
                  value={formData.targetCefr}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="A1">A1 - Beginner</option>
                  <option value="A2">A2 - Elementary</option>
                  <option value="B1">B1 - Intermediate</option>
                  <option value="B2">B2 - Upper Intermediate</option>
                  <option value="C1">C1 - Advanced</option>
                  <option value="C2">C2 - Proficient</option>
                </select>
              </div>
              
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700">
                  Training Objectives *
                </label>
                <textarea
                  name="trainingObjectives"
                  rows={4}
                  value={formData.trainingObjectives}
                  onChange={handleInputChange}
                  placeholder="Describe the specific learning goals and outcomes..."
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
                {errors.trainingObjectives && <p className="mt-1 text-sm text-red-600">{errors.trainingObjectives}</p>}
              </div>
              
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700">
                  Current Pain Points & Challenges
                </label>
                <textarea
                  name="painPoints"
                  rows={3}
                  value={formData.painPoints}
                  onChange={handleInputChange}
                  placeholder="Describe current English language challenges..."
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        );
        
      case 3:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900">Course Structure</h3>
            
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Course Length (Hours) *
                </label>
                <input
                  type="number"
                  name="courseLengthHours"
                  value={formData.courseLengthHours}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
                {errors.courseLengthHours && <p className="mt-1 text-sm text-red-600">{errors.courseLengthHours}</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Lessons Per Week *
                </label>
                <input
                  type="number"
                  name="lessonsPerWeek"
                  value={formData.lessonsPerWeek}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
                {errors.lessonsPerWeek && <p className="mt-1 text-sm text-red-600">{errors.lessonsPerWeek}</p>}
              </div>
              
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700">
                  Delivery Method
                </label>
                <select
                  name="deliveryMethod"
                  value={formData.deliveryMethod}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="in_person">In Person</option>
                  <option value="virtual">Virtual</option>
                  <option value="blended">Blended</option>
                </select>
              </div>
            </div>
          </div>
        );
        
      case 4:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900">Upload SOP Documents</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Standard Operating Procedures & Supporting Documents
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                <div className="space-y-1 text-center">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      strokeWidth={2}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <div className="flex text-sm text-gray-600">
                    <label className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                      <span>Upload files</span>
                      <input
                        type="file"
                        multiple
                        onChange={handleFileUpload}
                        accept=".pdf,.docx,.doc,.txt,.xlsx,.xls"
                        className="sr-only"
                      />
                    </label>
                    <p className="pl-1">or drag and drop</p>
                  </div>
                  <p className="text-xs text-gray-500">
                    PDF, DOC, DOCX, TXT, XLS, XLSX up to 50MB each
                  </p>
                </div>
              </div>
            </div>
            
            {formData.sopFiles.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Uploaded Files:</h4>
                <ul className="space-y-2">
                  {formData.sopFiles.map((file, index) => (
                    <li key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <span className="text-sm text-gray-600">{file.name}</span>
                      <button
                        type="button"
                        onClick={() => removeFile(index)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Remove
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );
        
      default:
        return null;
    }
  };

  return (
    <Layout>
      <div className="max-w-3xl mx-auto">
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">New Course Request</h1>
            
            {/* Progress Bar */}
            <div className="mt-4">
              <div className="flex items-center">
                {[1, 2, 3, 4].map((step) => (
                  <div key={step} className="flex items-center">
                    <div
                      className={`flex items-center justify-center w-8 h-8 rounded-full ${
                        currentStep >= step
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-300 text-gray-600'
                      }`}
                    >
                      {step}
                    </div>
                    {step < 4 && (
                      <div
                        className={`flex-1 h-0.5 mx-2 ${
                          currentStep > step ? 'bg-blue-600' : 'bg-gray-300'
                        }`}
                      />
                    )}
                  </div>
                ))}
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-2">
                <span>Client Info</span>
                <span>Training</span>
                <span>Structure</span>
                <span>Documents</span>
              </div>
            </div>
          </div>
          
          <form onSubmit={handleSubmit} className="px-6 py-6">
            {renderStepContent()}
            
            {errors.submit && (
              <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600">{errors.submit}</p>
              </div>
            )}
            
            <div className="mt-8 flex justify-between">
              <button
                type="button"
                onClick={prevStep}
                disabled={currentStep === 1}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              
              {currentStep < 4 ? (
                <button
                  type="button"
                  onClick={nextStep}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
                >
                  Next
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 disabled:opacity-50"
                >
                  {loading ? <LoadingSpinner size="small" text="" /> : 'Submit Request'}
                </button>
              )}
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
};

export default NewRequestPage;

// client/src/pages/sales/RequestsListPage.jsx
import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import api from '../../services/api';
import Layout from '../../components/layout/Layout';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import StatusBadge from '../../components/common/StatusBadge';
import { PlusIcon, EyeIcon } from '@heroicons/react/24/outline';

const RequestsListPage = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const location = useLocation();

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      const response = await api.get('/sales/requests');
      setRequests(response.data.requests || []);
    } catch (error) {
      console.error('Error fetching requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredRequests = requests.filter(request => {
    if (filter === 'all') return true;
    return request.status === filter;
  });

  const getStatusCount = (status) => {
    return requests.filter(r => r.status === status).length;
  };

  if (loading) {
    return (
      <Layout>
        <LoadingSpinner text="Loading your requests..." />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">My Course Requests</h1>
          <Link
            to="/sales/new-request"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            New Request
          </Link>
        </div>

        {/* Success Message */}
        {location.state?.message && (
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <p className="text-sm text-green-600">{location.state.message}</p>
          </div>
        )}

        {/* Filter Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'all', label: 'All Requests', count: requests.length },
              { key: 'pending', label: 'Pending', count: getStatusCount('pending') },
              { key: 'generating', label: 'Generating', count: getStatusCount('generating') },
              { key: 'approved', label: 'Approved', count: getStatusCount('approved') },
              { key: 'rejected', label: 'Rejected', count: getStatusCount('rejected') }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setFilter(tab.key)}
                className={`${
                  filter === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
              >
                {tab.label}
                {tab.count > 0 && (
                  <span className="ml-2 bg-gray-100 text-gray-900 py-0.5 px-2.5 rounded-full text-xs">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Requests List */}
        {filteredRequests.length === 0 ? (
          <div className="text-center py-12">
            <h3 className="mt-2 text-sm font-medium text-gray-900">No requests found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {filter === 'all' 
                ? "You haven't submitted any course requests yet." 
                : `No requests with status "${filter}".`
              }
            </p>
            <div className="mt-6">
              <Link
                to="/sales/new-request"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Create your first request
              </Link>
            </div>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {filteredRequests.map((request) => (
                <li key={request.id}>
                  <div className="px-6 py-4 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h3 className="text-lg font-medium text-gray-900">
                            {request.company_name}
                          </h3>
                          <StatusBadge status={request.status} />
                        </div>
                        <div className="mt-2 text-sm text-gray-600">
                          <p><strong>Course:</strong> {request.course_title || 'Not specified'}</p>
                          <p><strong>CEFR Level:</strong> {request.current_cefr} → {request.target_cefr}</p>
                          <p><strong>Cohort Size:</strong> {request.cohort_size} participants</p>
                          <p><strong>Submitted:</strong> {new Date(request.created_at).toLocaleDateString()}</p>
                        </div>
                        {request.training_objectives && (
                          <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                            {request.training_objectives}
                          </p>
                        )}
                      </div>
                      <div className="ml-4 flex-shrink-0">
                        <Link
                          to={`/sales/requests/${request.id}`}
                          className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                        >
                          <EyeIcon className="h-4 w-4 mr-2" />
                          View
                        </Link>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default RequestsListPage;

// client/src/pages/course-manager/ReviewsPage.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import Layout from '../../components/layout/Layout';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import StatusBadge from '../../components/common/StatusBadge';
import { 
  EyeIcon, 
  CheckIcon, 
  XMarkIcon, 
  PencilIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

const ReviewsPage = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('pending_review');

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await api.get('/course-manager/courses');
      setCourses(response.data.courses || []);
    } catch (error) {
      console.error('Error fetching courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = async (courseId, action) => {
    try {
      await api.post(`/course-manager/courses/${courseId}/review`, { action });
      fetchCourses(); // Refresh the list
    } catch (error) {
      console.error('Error processing action:', error);
    }
  };

  const filteredCourses = courses.filter(course => {
    if (filter === 'all') return true;
    return course.status === filter;
  });

  const getStatusCount = (status) => {
    return courses.filter(c => c.status === status).length;
  };

  if (loading) {
    return (
      <Layout>
        <LoadingSpinner text="Loading courses for review..." />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Course Reviews</h1>
          <div className="text-sm text-gray-500">
            {getStatusCount('pending_review')} courses awaiting review
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'pending_review', label: 'Pending Review', count: getStatusCount('pending_review') },
              { key: 'approved', label: 'Approved', count: getStatusCount('approved') },
              { key: 'needs_revision', label: 'Needs Revision', count: getStatusCount('needs_revision') },
              { key: 'generating', label: 'Generating', count: getStatusCount('generating') },
              { key: 'all', label: 'All Courses', count: courses.length }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setFilter(tab.key)}
                className={`${
                  filter === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
              >
                {tab.label}
                {tab.count > 0 && (
                  <span className="ml-2 bg-gray-100 text-gray-900 py-0.5 px-2.5 rounded-full text-xs">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Courses List */}
        {filteredCourses.length === 0 ? (
          <div className="text-center py-12">
            <ClockIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No courses found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {filter === 'pending_review' 
                ? "No courses are currently awaiting review." 
                : `No courses with status "${filter}".`
              }
            </p>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {filteredCourses.map((course) => (
                <li key={course.id}>
                  <div className="px-6 py-4 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h3 className="text-lg font-medium text-gray-900">
                            {course.title}
                          </h3>
                          <StatusBadge status={course.status} />
                        </div>
                        <div className="mt-2 text-sm text-gray-600">
                          <p><strong>Company:</strong> {course.company_name}</p>
                          <p><strong>CEFR Level:</strong> {course.cefr_level}</p>
                          <p><strong>Modules:</strong> {course.modules_count || 0}</p>
                          <p><strong>Generated:</strong> {new Date(course.generated_at || course.created_at).toLocaleDateString()}</p>
                        </div>
                        {course.description && (
                          <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                            {course.description}
                          </p>
                        )}
                      </div>
                      <div className="ml-4 flex-shrink-0 space-x-2">
                        <Link
                          to={`/course-manager/courses/${course.id}`}
                          className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                        >
                          <EyeIcon className="h-4 w-4 mr-2" />
                          Review
                        </Link>
                        
                        {course.status === 'pending_review' && (
                          <>
                            <button
                              onClick={() => handleQuickAction(course.id, 'approve')}
                              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                            >
                              <CheckIcon className="h-4 w-4 mr-2" />
                              Approve
                            </button>
                            <button
                              onClick={() => handleQuickAction(course.id, 'request_revision')}
                              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700"
                            >
                              <PencilIcon className="h-4 w-4 mr-2" />
                              Revise
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default ReviewsPage;

// client/src/pages/student/CoursesPage.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import Layout from '../../components/layout/Layout';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  BookOpenIcon, 
  PlayIcon, 
  CheckIcon,
  ClockIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';

const CoursesPage = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await api.get('/student/courses');
      setCourses(response.data.courses || []);
    } catch (error) {
      console.error('Error fetching courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const getProgressColor = (progress) => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 50) return 'bg-blue-500';
    if (progress >= 20) return 'bg-yellow-500';
    return 'bg-gray-300';
  };

  if (loading) {
    return (
      <Layout>
        <LoadingSpinner text="Loading your courses..." />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">My Courses</h1>
          <div className="text-sm text-gray-500">
            {courses.filter(c => c.progress < 100).length} courses in progress
          </div>
        </div>

        {/* Courses Grid */}
        {courses.length === 0 ? (
          <div className="text-center py-12">
            <BookOpenIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No courses assigned</h3>
            <p className="mt-1 text-sm text-gray-500">
              You don't have any courses assigned yet. Please contact your trainer or administrator.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {courses.map((course) => (
              <div key={course.id} className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
                <div className="p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <BookOpenIcon className="h-8 w-8 text-blue-600" />
                    </div>
                    <div className="ml-4 flex-1">
                      <h3 className="text-lg font-medium text-gray-900 line-clamp-2">
                        {course.title}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {course.cefr_level} Level
                      </p>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                      <span>Progress</span>
                      <span>{Math.round(course.progress || 0)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(course.progress || 0)}`}
                        style={{ width: `${course.progress || 0}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
                    <div className="flex items-center">
                      <ClockIcon className="h-4 w-4 mr-1" />
                      <span>{course.completed_lessons || 0}/{course.total_lessons || 0} lessons</span>
                    </div>
                    {course.last_accessed && (
                      <span>Last: {new Date(course.last_accessed).toLocaleDateString()}</span>
                    )}
                  </div>
                  
                  {course.description && (
                    <p className="mt-3 text-sm text-gray-600 line-clamp-3">
                      {course.description}
                    </p>
                  )}
                  
                  <div className="mt-6">
                    {course.progress < 100 ? (
                      <Link
                        to={`/student/courses/${course.id}/learn`}
                        className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                      >
                        <PlayIcon className="h-4 w-4 mr-2" />
                        {course.progress > 0 ? 'Continue Learning' : 'Start Course'}
                      </Link>
                    ) : (
                      <div className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-gray-50">
                        <CheckIcon className="h-4 w-4 mr-2 text-green-600" />
                        Completed
                      </div>
                    )}
                  </div>
                  
                  <div className="mt-2">
                    <Link
                      to={`/student/courses/${course.id}`}
                      className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                    >
                      View Details
                      <ChevronRightIcon className="h-4 w-4 ml-2" />
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default CoursesPage;

// client/src/services/courseService.js
import api from './api';

export const courseService = {
  // Sales endpoints
  submitCourseRequest: async (formData) => {
    const response = await api.post('/sales/course-request', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  getSalesRequests: async () => {
    const response = await api.get('/sales/requests');
    return response.data;
  },

  getSalesRequest: async (id) => {
    const response = await api.get(`/sales/requests/${id}`);
    return response.data;
  },

  // Course Manager endpoints
  getCourses: async () => {
    const response = await api.get('/course-manager/courses');
    return response.data;
  },

  getCourse: async (id) => {
    const response = await api.get(`/course-manager/courses/${id}`);
    return response.data;
  },

  reviewCourse: async (id, action, feedback = null) => {
    const response = await api.post(`/course-manager/courses/${id}/review`, {
      action,
      feedback
    });
    return response.data;
  },

  // Student endpoints
  getStudentCourses: async () => {
    const response = await api.get('/student/courses');
    return response.data;
  },

  getStudentCourse: async (id) => {
    const response = await api.get(`/student/courses/${id}`);
    return response.data;
  },

  getLesson: async (courseId, lessonId) => {
    const response = await api.get(`/student/courses/${courseId}/lessons/${lessonId}`);
    return response.data;
  },

  submitExercise: async (lessonId, exerciseId, answer) => {
    const response = await api.post(`/student/lessons/${lessonId}/exercises/${exerciseId}`, {
      answer
    });
    return response.data;
  },

  // Trainer endpoints
  getTrainerCourses: async () => {
    const response = await api.get('/trainer/courses');
    return response.data;
  },

  getTrainerStudents: async () => {
    const response = await api.get('/trainer/students');
    return response.data;
  },

  submitFeedback: async (studentId, lessonId, feedback) => {
    const response = await api.post('/trainer/feedback', {
      student_id: studentId,
      lesson_id: lessonId,
      feedback
    });
    return response.data;
  },

  // AI endpoints
  generateCourse: async (requestId) => {
    const response = await api.post('/ai/generate-course', {
      request_id: requestId
    });
    return response.data;
  },

  processSOP: async (filePath, requestId) => {
    const response = await api.post('/ai/process-sop', {
      file_path: filePath,
      request_id: requestId
    });
    return response.data;
  }
};

export default courseService;
