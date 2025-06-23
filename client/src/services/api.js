import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const { response } = error;
    
    if (!response) {
      toast.error('Network error. Please check your connection.');
      return Promise.reject(error);
    }
    
    const { status, data } = response;
    
    switch (status) {
      case 401:
        // Unauthorized - token expired or invalid
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        if (window.location.pathname !== '/login') {
          toast.error('Session expired. Please login again.');
          window.location.href = '/login';
        }
        break;
        
      case 403:
        toast.error('Access denied. You don\'t have permission to perform this action.');
        break;
        
      case 404:
        toast.error('Resource not found.');
        break;
        
      case 422:
        // Validation errors
        if (data.errors) {
          Object.values(data.errors).forEach(error => {
            toast.error(error);
          });
        } else {
          toast.error(data.message || 'Validation error.');
        }
        break;
        
      case 429:
        toast.error('Too many requests. Please slow down.');
        break;
        
      case 500:
        toast.error('Server error. Please try again later.');
        break;
        
      default:
        toast.error(data.message || 'An unexpected error occurred.');
    }
    
    return Promise.reject(error);
  }
);

// API Methods
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  forgotPassword: (email) => api.post('/auth/forgot-password', { email }),
  resetPassword: (token, password) => api.post('/auth/reset-password', { token, password }),
  refreshToken: () => api.post('/auth/refresh'),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (userData) => api.put('/auth/profile', userData),
};

export const salesAPI = {
  // Course Requests
  getCourseRequests: (params) => api.get('/api/sales/course-requests', { params }),
  createCourseRequest: (requestData) => api.post('/api/sales/course-requests', requestData),
  getCourseRequest: (id) => api.get(`/api/sales/course-requests/${id}`),
  updateCourseRequest: (id, requestData) => api.put(`/api/sales/course-requests/${id}`, requestData),
  deleteCourseRequest: (id) => api.delete(`/api/sales/course-requests/${id}`),
  
  // SOP Upload
  uploadSOP: (requestId, file, onProgress) => {
    const formData = new FormData();
    formData.append('sop', file);
    
    return api.post(`/api/sales/course-requests/${requestId}/sop`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onProgress,
    });
  },
  
  // Client Management
  getClients: (params) => api.get('/sales/clients', { params }),
  createClient: (clientData) => api.post('/sales/clients', clientData),
  getClient: (id) => api.get(`/sales/clients/${id}`),
  updateClient: (id, clientData) => api.put(`/sales/clients/${id}`, clientData),
};

export const courseManagerAPI = {
  // Course Review
  getPendingCourses: (params) => api.get('/course-manager/pending-courses', { params }),
  getCourse: (id) => api.get(`/course-manager/courses/${id}`),
  approveCourse: (id, feedback) => api.post(`/course-manager/courses/${id}/approve`, { feedback }),
  rejectCourse: (id, reason) => api.post(`/course-manager/courses/${id}/reject`, { reason }),
  requestRevision: (id, feedback) => api.post(`/course-manager/courses/${id}/request-revision`, { feedback }),
  
  // Content Library
  getContentLibrary: (params) => api.get('/course-manager/content-library', { params }),
  getContentItem: (id) => api.get(`/course-manager/content-library/${id}`),
  updateContentItem: (id, content) => api.put(`/course-manager/content-library/${id}`, content),
  
  // User Management
  getUsers: (params) => api.get('/course-manager/users', { params }),
  createUser: (userData) => api.post('/course-manager/users', userData),
  updateUser: (id, userData) => api.put(`/course-manager/users/${id}`, userData),
  deleteUser: (id) => api.delete(`/course-manager/users/${id}`),
  
  // Analytics
  getDashboardStats: () => api.get('/course-manager/dashboard-stats'),
  getReports: (params) => api.get('/course-manager/reports', { params }),
};

export const trainerAPI = {
  // Assigned Courses
  getAssignedCourses: (params) => api.get('/trainer/assigned-courses', { params }),
  getCourseDetails: (id) => api.get(`/trainer/courses/${id}`),
  getLessonPlan: (courseId, lessonId) => api.get(`/trainer/courses/${courseId}/lessons/${lessonId}`),
  
  // Student Management
  getStudents: (params) => api.get('/trainer/students', { params }),
  getStudentProgress: (studentId) => api.get(`/trainer/students/${studentId}/progress`),
  submitStudentFeedback: (studentId, feedback) => api.post(`/trainer/students/${studentId}/feedback`, feedback),
  
  // Lesson Delivery
  markAttendance: (lessonId, attendance) => api.post(`/trainer/lessons/${lessonId}/attendance`, attendance),
  submitLessonFeedback: (lessonId, feedback) => api.post(`/trainer/lessons/${lessonId}/feedback`, feedback),
  
  // Schedule
  getSchedule: (params) => api.get('/trainer/schedule', { params }),
};

export const studentAPI = {
  // Courses
  getEnrolledCourses: () => api.get('/student/courses'),
  getCourseProgress: (courseId) => api.get(`/student/courses/${courseId}/progress`),
  getLessonContent: (courseId, lessonId) => api.get(`/student/courses/${courseId}/lessons/${lessonId}`),
  
  // Exercises & Assessments
  submitExercise: (exerciseId, answer) => api.post(`/student/exercises/${exerciseId}/submit`, { answer }),
  getExerciseResult: (submissionId) => api.get(`/student/exercise-submissions/${submissionId}`),
  submitAssessment: (assessmentId, answers) => api.post(`/student/assessments/${assessmentId}/submit`, { answers }),
  getAssessmentResult: (submissionId) => api.get(`/student/assessment-submissions/${submissionId}`),
  
  // Progress & Performance
  getProgress: () => api.get('/student/progress'),
  getPerformanceStats: () => api.get('/student/performance'),
  
  // Feedback
  submitFeedback: (targetType, targetId, feedback) => 
    api.post('/student/feedback', { targetType, targetId, feedback }),
};

export const aiAPI = {
  // Document Processing
  processDocument: (file, metadata) => {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }
    
    return api.post('/ai/process-document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  getDocumentStatus: (documentId) => api.get(`/ai/document-status/${documentId}`),
  
  // RAG System
  addToKnowledgeBase: (documentId, metadata) => 
    api.post('/ai/knowledge-base/add', { document_id: documentId, metadata }),
    
  searchKnowledgeBase: (query, filters) => 
    api.post('/ai/knowledge-base/search', { query, filters }),
    
  updateKnowledgeBase: (documentId, updates) => 
    api.put(`/ai/knowledge-base/${documentId}`, updates),
    
  deleteFromKnowledgeBase: (documentId) => 
    api.delete(`/ai/knowledge-base/${documentId}`),
    
  // Course Generation
  generateCourse: (requestData) => api.post('/ai/generate-course', requestData),
  
  generateCurriculum: (requestData) => api.post('/ai/generate-curriculum', requestData),
  
  generateLesson: (requestData) => api.post('/ai/generate-lesson', requestData),
  
  generateExercise: (requestData) => api.post('/ai/generate-exercise', requestData),
  
  generateAssessment: (requestData) => api.post('/ai/generate-assessment', requestData),
  
  // Generation Status & Results
  getGenerationStatus: (jobId) => api.get(`/ai/generation-status/${jobId}`),
  
  getGenerationResult: (jobId) => api.get(`/ai/generation-result/${jobId}`),
  
  // Content Enhancement
  enhanceContent: (contentId, requirements) => 
    api.post(`/ai/enhance-content/${contentId}`, requirements),
    
  reviewContent: (contentId, criteria) => 
    api.post(`/ai/review-content/${contentId}`, criteria),
    
  // AI Services Health
  checkAIServices: () => api.get('/ai/health'),
  
  getAIConfig: () => api.get('/ai/config'),
  
  updateAIConfig: (config) => api.put('/ai/config', config),
};

export const commonAPI = {
  // File Upload
  uploadFile: (file, type, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    
    return api.post('/common/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onProgress,
    });
  },
  
  // Notifications
  getNotifications: (params) => api.get('/common/notifications', { params }),
  markNotificationRead: (id) => api.put(`/common/notifications/${id}/read`),
  markAllNotificationsRead: () => api.put('/common/notifications/read-all'),
  
  // System Health
  getSystemHealth: () => api.get('/common/health'),
};

export default api;