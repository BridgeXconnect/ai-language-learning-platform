# V0 Sales Portal Complete Implementation

Create a **comprehensive Sales Portal** for the AI Language Learning Platform with all pages, components, and functionality needed for sales team workflow management.

## 🎯 Sales Portal Overview

Build a **complete sales management interface** that handles the entire sales lifecycle from initial client contact through course request submission and tracking. The portal should feel professional, goal-oriented, and optimized for sales productivity.

## 📋 Complete Page Structure & Wireframes

### 1. **Sales Dashboard** (`/sales/dashboard`)

**Layout Structure:**
- Header with welcome message and quick actions
- 4-card KPI metrics grid (Active Requests, Conversion Rate, Revenue, Pipeline)
- Charts section with pipeline funnel and monthly trends
- Recent activity feed
- Quick action buttons for common tasks

**Key Components:**
- MetricCards with trend indicators and animations
- PipelineFunnelChart showing conversion stages
- MonthlyTrendsChart with interactive data points
- ActivityFeed with real-time updates
- QuickActionButtons for new requests and follow-ups

### 2. **Course Requests List** (`/sales/requests`)

**Layout Structure:**
- Page header with title and "New Request" button
- Advanced filters bar (Status, Priority, Date range)
- Global search functionality
- Comprehensive data table with sorting and actions
- Server-side pagination

**Table Columns:**
- Company Name + Contact Person (with avatar)
- Status Badge (Draft, Submitted, Processing, Completed)
- Priority Indicator (Low, Normal, High, Urgent)
- CEFR Levels (Current → Target with arrow)
- Cohort Size with user icon
- Created Date with relative time
- Actions Menu (View, Edit, Upload SOPs, Delete)

### 3. **New Course Request Wizard** (`/sales/requests/new`)

**Multi-Step Process:**
1. **Client Information**
   - Company Name*, Industry
   - Contact Person*, Contact Email*
   - Contact Phone, Company Size

2. **Training Requirements**
   - Cohort Size*, Current CEFR Level*
   - Target CEFR Level*, Training Objectives*
   - Pain Points, Specific Requirements

3. **Course Preferences**
   - Course Length Hours, Lessons per Module
   - Delivery Method, Preferred Schedule
   - Budget Range, Timeline Expectations

4. **Review & Submit**
   - Summary of all entered data
   - Save as Draft or Submit options

### 4. **Request Details Page** (`/sales/requests/:id`)

**Tabbed Interface:**
- **Overview Tab**: Client info, training requirements, course preferences
- **SOPs Tab**: File upload zone and document management
- **Communications Tab**: Email threads and client feedback
- **Timeline Tab**: Activity history and status changes

### 5. **SOP Upload Page** (`/sales/requests/:id/documents`)

**Features:**
- Multi-file drag-drop upload zone
- File type validation (PDF, DOCX, TXT)
- Upload progress indicators
- Processing status tracking
- File preview and download options
- Error handling with retry functionality

### 6. **Client Communication Hub** (`/sales/requests/:id/communications`)

**Components:**
- Rich text email composer
- Email thread viewer
- Client feedback collection forms
- Internal notes section
- Meeting scheduling widget
- Document sharing interface

### 7. **Sales Analytics Dashboard** (`/sales/analytics`)

**Analytics Features:**
- Flexible date range picker
- Key performance indicators
- Conversion funnel visualization
- Team leaderboard
- Exportable reports section

## 🎨 Design Specifications

### Color Theme
```css
/* Sales Portal Colors */
--sales-primary: #2563eb;      /* Professional blue */
--sales-success: #10b981;      /* Success green */
--sales-warning: #f59e0b;      /* Attention amber */
--sales-accent: #8b5cf6;       /* Premium purple */

/* Status Colors */
--status-draft: #6b7280;       /* Gray */
--status-submitted: #3b82f6;   /* Blue */
--status-processing: #f59e0b;  /* Amber */
--status-completed: #10b981;   /* Green */
--status-rejected: #ef4444;    /* Red */
```

### Component Examples

#### Dashboard Metric Card
```jsx
<Card className="metric-card hover:shadow-lg transition-shadow">
  <CardHeader className="flex items-center justify-between pb-2">
    <div className="flex items-center space-x-2">
      <div className="p-2 bg-blue-100 rounded-lg">
        <UsersIcon className="w-5 h-5 text-blue-600" />
      </div>
      <h3 className="font-medium text-gray-700">Active Requests</h3>
    </div>
  </CardHeader>
  
  <CardContent>
    <div className="text-2xl font-bold text-gray-900">47</div>
    <div className="flex items-center space-x-1 mt-1">
      <TrendingUpIcon className="w-4 h-4 text-green-500" />
      <span className="text-sm font-medium text-green-600">+12%</span>
      <span className="text-sm text-gray-500">vs last month</span>
    </div>
  </CardContent>
</Card>
```

#### Advanced Data Table
```jsx
<div className="sales-data-table">
  <div className="flex items-center justify-between mb-4">
    <h2 className="text-xl font-semibold">Course Requests</h2>
    <Button className="bg-blue-600 hover:bg-blue-700">
      <PlusIcon className="w-4 h-4 mr-2" />
      New Request
    </Button>
  </div>
  
  <div className="filters-bar flex space-x-4 mb-4">
    <Input placeholder="Search requests..." className="max-w-sm" />
    <Select>
      <SelectTrigger className="w-32">
        <SelectValue placeholder="Status" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="all">All Status</SelectItem>
        <SelectItem value="draft">Draft</SelectItem>
        <SelectItem value="submitted">Submitted</SelectItem>
      </SelectContent>
    </Select>
  </div>
  
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead>Company</TableHead>
        <TableHead>Status</TableHead>
        <TableHead>Priority</TableHead>
        <TableHead>CEFR Level</TableHead>
        <TableHead>Cohort Size</TableHead>
        <TableHead>Created</TableHead>
        <TableHead>Actions</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      {/* Table rows with interactive elements */}
    </TableBody>
  </Table>
</div>
```

#### Multi-Step Wizard
```jsx
<div className="request-wizard max-w-4xl mx-auto">
  <div className="steps-indicator mb-8">
    <div className="flex items-center justify-between">
      {steps.map((step, index) => (
        <div key={index} className={`step ${index <= currentStep ? 'active' : ''}`}>
          <div className="step-circle">{index + 1}</div>
          <div className="step-label">{step.label}</div>
        </div>
      ))}
    </div>
  </div>
  
  <Card className="wizard-content">
    <CardContent className="p-6">
      {/* Step content with smooth transitions */}
    </CardContent>
    
    <CardFooter className="flex justify-between">
      <Button variant="outline" disabled={currentStep === 0}>
        Previous
      </Button>
      <div className="flex space-x-2">
        <Button variant="outline">Save Draft</Button>
        <Button>
          {currentStep === steps.length - 1 ? 'Submit' : 'Next'}
        </Button>
      </div>
    </CardFooter>
  </Card>
</div>
```

## 🔌 API Integration

### Required Endpoints
```typescript
// Course Requests CRUD
GET    /api/v1/sales/course-requests
POST   /api/v1/sales/course-requests
GET    /api/v1/sales/course-requests/:id
PUT    /api/v1/sales/course-requests/:id
DELETE /api/v1/sales/course-requests/:id

// SOP Document Management
POST   /api/v1/sales/course-requests/:id/sop
GET    /api/v1/sales/course-requests/:id/sop
DELETE /api/v1/sales/course-requests/:id/sop/:sopId

// Dashboard & Analytics
GET    /api/v1/sales/dashboard-stats
GET    /api/v1/sales/analytics

// Communications
POST   /api/v1/sales/course-requests/:id/feedback
GET    /api/v1/sales/course-requests/:id/feedback
```

### State Management
```typescript
interface SalesState {
  requests: CourseRequest[]
  currentRequest: CourseRequest | null
  dashboardStats: DashboardStats
  filters: RequestFilters
  loading: boolean
  error: string | null
}

// Use React Query for data fetching
const useRequests = (filters) => useQuery(['requests', filters], () => fetchRequests(filters))
const useCreateRequest = () => useMutation(createRequest)
```

### Form Validation
```typescript
// Use Zod for form validation
const requestSchema = z.object({
  company_name: z.string().min(2).max(200),
  contact_person: z.string().min(2).max(200),
  contact_email: z.string().email(),
  cohort_size: z.number().min(1).max(1000),
  current_cefr: z.enum(['A1', 'A2', 'B1', 'B2', 'C1', 'C2']),
  target_cefr: z.enum(['A1', 'A2', 'B1', 'B2', 'C1', 'C2'])
})
```

## 🎯 Key Features to Implement

### Interactive Elements
- Hover effects on cards and table rows
- Smooth transitions between wizard steps
- Real-time search and filtering
- Drag-and-drop file uploads
- Progress indicators for uploads
- Toast notifications for actions

### Responsive Design
- Mobile-friendly navigation
- Responsive data tables
- Touch-friendly interactions
- Adaptive layouts for different screen sizes

### Accessibility
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Focus indicators

### Performance
- Lazy loading for large datasets
- Optimistic updates for better UX
- Debounced search inputs
- Efficient re-rendering

---

**Generate a complete, production-ready Sales Portal** with all the pages, components, and functionality specified above. Focus on creating an intuitive, efficient interface that enables sales teams to manage their entire workflow seamlessly. Include proper TypeScript types, error handling, loading states, and modern UI patterns with Shadcn/ui components and Tailwind CSS styling. 