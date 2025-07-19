# V0 Prompt: AI Language Learning Platform

Create a modern, comprehensive AI-powered English language learning platform with role-based dashboards and AI course generation capabilities.

## 🎯 Platform Overview

Build a **Dynamic English Course Creator** - an enterprise SaaS platform that uses AI to generate customized English courses from company SOPs (Standard Operating Procedures). The platform serves 4 user roles with distinct workflows and interfaces.

## 👥 User Roles & Core Workflows

### 1. **Sales Team** - Course Request Management
- Create new course requests with client details
- Upload SOP documents (PDF, DOCX, TXT)
- Track request status and client communications
- Dashboard with pipeline metrics and conversion rates

### 2. **Course Managers** - AI Course Generation & Approval
- Review submitted course requests
- Trigger AI course generation from uploaded SOPs
- Approve/reject generated courses
- Monitor AI generation progress with real-time updates
- Content library management

### 3. **Trainers** - Course Delivery
- View assigned courses and lesson plans
- Access detailed teaching materials
- Track student progress and engagement
- Provide feedback on course effectiveness

### 4. **Students** - Learning Experience
- Interactive course dashboard with progress tracking
- Lesson player with video, exercises, and assessments
- Achievement system and learning streaks
- Performance analytics and recommendations

## 🚀 Key Features to Implement

### Authentication & Navigation
- Modern login/register forms with role-based redirects
- Sidebar navigation that adapts to user role
- User profile management with role indicators
- Secure logout with session management

### Sales Portal Features
```typescript
// Key components needed:
- NewCourseRequestWizard (multi-step form)
- SOPUploadPage with drag-drop file handling
- SalesRequestsDashboard with filtering
- ClientFeedbackForm
- SalesPipelineMetrics
```

### Course Manager Portal Features
```typescript
// Key components needed:
- CourseGenerationWizard (AI-powered)
- GenerationProgressTracker (real-time WebSocket updates)
- CourseApprovalInterface
- ContentLibraryBrowser
- ManagerDashboardStats
```

### Trainer Portal Features
```typescript
// Key components needed:
- TrainerDashboard with assigned courses
- LessonPlanViewer with teaching notes
- StudentProgressTracker
- CourseDeliveryTools
- TrainerFeedbackForms
```

### Student Portal Features
```typescript
// Key components needed:
- EnhancedStudentDashboard with progress rings
- InteractiveLessonPlayer (video + exercises)
- AchievementsBadgeSystem
- LearningStreakTracker
- PerformanceAnalytics
```

## 🎨 UI/UX Requirements

### Design System
- **Colors**: Professional blue/indigo primary, success green, warning amber
- **Typography**: Clean, modern fonts (Inter/Poppins)
- **Components**: Shadcn/ui style with Tailwind CSS
- **Icons**: Heroicons or Lucide React
- **Layout**: Clean, spacious, mobile-responsive

### Modern UI Patterns
- Loading states with skeleton screens
- Toast notifications for user feedback
- Modal dialogs for confirmations
- Progress indicators for multi-step processes
- Real-time updates with WebSocket connections
- Drag-and-drop file uploads
- Advanced data tables with sorting/filtering

## 🔌 Backend Integration Patterns

### API Configuration
```typescript
// Base configuration
const API_BASE_URL = 'http://localhost:8000/api/v1'
const WS_URL = 'ws://localhost:8000/ws'

// Authentication headers
const authHeaders = {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
  'Content-Type': 'application/json'
}
```

### Key API Endpoints to Connect

#### Authentication
```typescript
POST /auth/login
POST /auth/register  
POST /auth/refresh
GET /auth/profile
```

#### Sales Endpoints
```typescript
GET /sales/course-requests
POST /sales/course-requests
PUT /sales/course-requests/{id}
POST /sales/course-requests/{id}/sop (file upload)
GET /sales/dashboard-stats
```

#### Course Management
```typescript
GET /courses/
POST /courses/
PUT /courses/{id}
GET /courses/{id}/modules
POST /ai/generate-course
GET /ai/generation-status/{id}
```

#### AI & Document Processing
```typescript
POST /ai/process-document
POST /ai/generate-content
GET /ai/indexed-sources
POST /ai/search-content
```

### WebSocket Integration
```typescript
// Real-time updates for course generation
const wsConnection = new WebSocket(`${WS_URL}/generation-updates`)
wsConnection.onmessage = (event) => {
  const update = JSON.parse(event.data)
  // Update progress bars, status indicators
}
```

## 📱 Specific Component Requirements

### 1. Course Generation Wizard
```typescript
interface CourseGenerationWizard {
  steps: [
    'Upload SOPs',
    'Configure Parameters', 
    'Review & Generate',
    'Monitor Progress'
  ]
  features: [
    'Multi-file drag-drop upload',
    'CEFR level selection (A1-C2)',
    'Course duration settings',
    'Real-time generation progress',
    'Error handling & retry logic'
  ]
}
```

### 2. Interactive Dashboard Cards
```typescript
interface DashboardCard {
  variants: ['metric', 'chart', 'progress', 'activity']
  animations: 'smooth hover effects'
  responsive: true
  darkMode: 'supported'
}
```

### 3. Advanced Data Tables
```typescript
interface DataTable {
  features: [
    'Server-side pagination',
    'Column sorting',
    'Global search',
    'Row selection',
    'Export functionality',
    'Responsive stacking on mobile'
  ]
}
```

### 4. File Upload Components
```typescript
interface FileUpload {
  types: ['drag-drop', 'click-to-browse']
  formats: ['PDF', 'DOCX', 'TXT', 'XLSX']
  maxSize: '50MB'
  preview: 'show file details & processing status'
  progress: 'upload & processing progress bars'
}
```

## 🎯 State Management

Use React hooks and context for:
- Authentication state
- User role and permissions
- WebSocket connections
- Loading states
- Error handling
- Real-time notifications

```typescript
// Example auth context structure
interface AuthContext {
  user: User | null
  roles: string[]
  login: (credentials) => Promise<void>
  logout: () => void
  hasRole: (role: string) => boolean
}
```

## 🚦 Error Handling & Loading States

Implement comprehensive error boundaries and loading states:
- Network error recovery
- Token refresh logic
- Graceful degradation
- Loading skeletons
- Progress indicators
- User-friendly error messages

## 📊 Data Visualization

Include charts and metrics using libraries like Recharts:
- Sales pipeline funnel charts
- Course completion rates
- Student progress tracking
- Performance analytics
- Generation success metrics

## 🎨 Modern UI Elements

- Glassmorphism effects for hero sections
- Subtle animations and micro-interactions
- Progressive disclosure for complex forms
- Contextual help and tooltips
- Keyboard navigation support
- Accessibility (WCAG 2.1 AA compliance)

## 🔄 Real-time Features

Implement WebSocket connections for:
- Course generation progress updates
- Live notifications
- Collaborative editing indicators
- System status updates
- Chat/messaging features

---

**Generate a complete, production-ready React application** with TypeScript, Tailwind CSS, and all the components needed for this comprehensive AI language learning platform. Focus on creating an intuitive, modern interface that handles the complex workflows while maintaining excellent user experience across all user roles. 