# V0 Course Manager Portal Complete Implementation

Create a **comprehensive Course Manager Portal** for the AI Language Learning Platform with all pages, components, and functionality needed for AI-powered course generation, approval workflows, and content management.

## 🎯 Course Manager Portal Overview

Build a **sophisticated AI-powered course management interface** that handles course generation from SOPs, approval workflows, content library management, and real-time AI generation monitoring. The portal should feel intelligent, powerful, and optimized for content management professionals.

## 📋 Complete Page Structure & Wireframes

### 1. **Course Manager Dashboard** (`/course-manager/dashboard`)

**Layout Structure:**
- Header with AI status indicators and quick actions
- 4-card KPI metrics grid (Pending Approvals, Generated Courses, AI Processing, Content Library)
- AI Generation Queue with real-time status updates
- Recent activities and system notifications
- Quick action buttons for common tasks

**Key Components:**
- AIStatusIndicator showing service health
- GenerationQueueWidget with live progress
- ApprovalWorkflowCards with priority indicators
- ContentLibraryStats with usage metrics
- SystemNotifications with real-time updates

### 2. **Pending Approvals** (`/course-manager/approvals`)

**Layout Structure:**
- Filter bar (Status, Priority, Date range, CEFR level)
- Advanced search with AI-powered suggestions
- Card-based layout showing course previews
- Bulk approval actions
- Detailed approval workflow tracking

**Card Components:**
- Course preview with generated content summary
- Client information and requirements
- AI generation confidence scores
- Approval status and reviewer comments
- Quick action buttons (Approve, Reject, Request Revision)

### 3. **AI Course Generation Hub** (`/course-manager/generate`)

**Layout Structure:**
- Course request selection interface
- AI generation configuration panel
- Real-time generation progress monitor
- Generated content preview
- Quality assessment tools

**Generation Process:**
1. **Request Selection**
   - Available course requests grid
   - SOP document preview
   - Client requirements summary

2. **AI Configuration**
   - Model selection (GPT-4, Claude, etc.)
   - Generation parameters (temperature, creativity)
   - Course structure preferences
   - Quality thresholds

3. **Generation Monitoring**
   - Real-time progress tracking
   - Stage-by-stage status updates
   - Error handling and retry options
   - Performance metrics

4. **Content Review**
   - Generated course preview
   - Quality scores and assessments
   - Content validation tools
   - Approval/rejection interface

### 4. **Course Details & Approval** (`/course-manager/courses/:id`)

**Tabbed Interface:**
- **Overview Tab**: Course summary, client info, generation details
- **Content Tab**: Full course content with editing capabilities
- **Quality Tab**: AI assessment scores and validation results
- **History Tab**: Generation history and approval workflow
- **Comments Tab**: Reviewer feedback and collaboration

**Approval Workflow:**
- Detailed content review interface
- Quality scoring system
- Feedback and revision request tools
- Approval/rejection with comments
- Version history tracking

### 5. **Content Library Management** (`/course-manager/library`)

**Features:**
- Searchable content repository
- AI-indexed document management
- Content categorization and tagging
- Usage analytics and insights
- Bulk operations and organization

**Library Components:**
- Document upload and processing
- AI-powered content analysis
- Semantic search capabilities
- Content recommendation engine
- Usage tracking and analytics

### 6. **AI Generation Analytics** (`/course-manager/analytics`)

**Analytics Features:**
- Generation success rates and metrics
- AI model performance comparisons
- Content quality trend analysis
- Processing time analytics
- Cost and usage optimization insights

### 7. **System Configuration** (`/course-manager/settings`)

**Configuration Options:**
- AI model settings and preferences
- Quality thresholds and validation rules
- Approval workflow customization
- Notification preferences
- Integration settings

## 🎨 Design Specifications

### Color Theme
```css
/* Course Manager Portal Colors */
--manager-primary: #8b5cf6;       /* Intelligent purple */
--manager-secondary: #3b82f6;     /* Professional blue */
--manager-success: #10b981;       /* Success green */
--manager-warning: #f59e0b;       /* Attention amber */
--manager-ai: #6366f1;            /* AI accent indigo */

/* AI Status Colors */
--ai-processing: #3b82f6;         /* Blue */
--ai-success: #10b981;            /* Green */
--ai-error: #ef4444;              /* Red */
--ai-pending: #f59e0b;            /* Amber */

/* Quality Scores */
--quality-excellent: #10b981;     /* Green */
--quality-good: #84cc16;          /* Lime */
--quality-fair: #f59e0b;          /* Amber */
--quality-poor: #ef4444;          /* Red */
```

### Component Examples

#### AI Status Dashboard Card
```jsx
<Card className="ai-status-card border-purple-200 hover:shadow-xl transition-all">
  <CardHeader className="flex items-center justify-between pb-3">
    <div className="flex items-center space-x-3">
      <div className="p-2 bg-purple-100 rounded-lg">
        <CpuChipIcon className="w-6 h-6 text-purple-600" />
      </div>
      <div>
        <h3 className="font-semibold text-gray-900">AI Generation Status</h3>
        <p className="text-sm text-gray-500">Real-time processing monitor</p>
      </div>
    </div>
    <div className="flex items-center space-x-2">
      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
      <span className="text-sm font-medium text-green-600">Online</span>
    </div>
  </CardHeader>
  
  <CardContent>
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-600">Active Generations</span>
        <span className="font-semibold">3</span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-600">Queue Length</span>
        <span className="font-semibold">7</span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-600">Avg. Processing Time</span>
        <span className="font-semibold">4.2 min</span>
      </div>
    </div>
    
    <div className="mt-4 pt-4 border-t">
      <div className="flex items-center space-x-2">
        <div className="flex-1 bg-gray-200 rounded-full h-2">
          <div className="bg-purple-600 h-2 rounded-full" style={{width: '75%'}}></div>
        </div>
        <span className="text-xs text-gray-500">75% capacity</span>
      </div>
    </div>
  </CardContent>
</Card>
```

#### Course Approval Card
```jsx
<Card className="approval-card group hover:shadow-lg transition-all border-l-4 border-l-blue-500">
  <CardHeader className="pb-3">
    <div className="flex items-start justify-between">
      <div className="flex items-center space-x-3">
        <Avatar className="w-10 h-10">
          <BuildingOfficeIcon className="w-5 h-5" />
        </Avatar>
        <div>
          <h3 className="font-semibold text-gray-900">Acme Corporation Training</h3>
          <p className="text-sm text-gray-500">B1 → B2 Business English</p>
        </div>
      </div>
      <div className="flex items-center space-x-2">
        <PriorityBadge priority="high" />
        <StatusBadge status="pending_approval" />
      </div>
    </div>
  </CardHeader>
  
  <CardContent className="space-y-4">
    <div className="grid grid-cols-2 gap-4 text-sm">
      <div>
        <span className="text-gray-500">Cohort Size:</span>
        <span className="ml-2 font-medium">25 students</span>
      </div>
      <div>
        <span className="text-gray-500">Duration:</span>
        <span className="ml-2 font-medium">8 weeks</span>
      </div>
      <div>
        <span className="text-gray-500">Generated:</span>
        <span className="ml-2 font-medium">2 hours ago</span>
      </div>
      <div>
        <span className="text-gray-500">Quality Score:</span>
        <span className="ml-2 font-medium text-green-600">92%</span>
      </div>
    </div>
    
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-600">Content Modules</span>
        <span className="font-medium">8/8 generated</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-1.5">
        <div className="bg-green-500 h-1.5 rounded-full w-full"></div>
      </div>
    </div>
    
    <div className="flex items-center space-x-2 pt-2">
      <Button size="sm" className="flex-1">
        <EyeIcon className="w-4 h-4 mr-2" />
        Review
      </Button>
      <Button size="sm" variant="outline" className="flex-1">
        <CheckIcon className="w-4 h-4 mr-2" />
        Quick Approve
      </Button>
    </div>
  </CardContent>
</Card>
```

#### AI Generation Progress Monitor
```jsx
<Card className="generation-monitor">
  <CardHeader>
    <div className="flex items-center justify-between">
      <h3 className="font-semibold">Course Generation in Progress</h3>
      <div className="flex items-center space-x-2">
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
        <span className="text-sm text-blue-600">Processing</span>
      </div>
    </div>
  </CardHeader>
  
  <CardContent className="space-y-4">
    <div className="space-y-3">
      {generationStages.map((stage, index) => (
        <div key={index} className="flex items-center space-x-3">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            stage.status === 'completed' ? 'bg-green-100 text-green-600' :
            stage.status === 'processing' ? 'bg-blue-100 text-blue-600' :
            'bg-gray-100 text-gray-400'
          }`}>
            {stage.status === 'completed' ? (
              <CheckIcon className="w-4 h-4" />
            ) : stage.status === 'processing' ? (
              <div className="w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <span className="text-xs">{index + 1}</span>
            )}
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{stage.name}</span>
              <span className="text-xs text-gray-500">{stage.duration}</span>
            </div>
            {stage.status === 'processing' && (
              <div className="mt-1 w-full bg-gray-200 rounded-full h-1">
                <div 
                  className="bg-blue-500 h-1 rounded-full transition-all duration-300"
                  style={{width: `${stage.progress}%`}}
                ></div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
    
    <div className="pt-3 border-t">
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-600">Overall Progress</span>
        <span className="font-medium">67% complete</span>
      </div>
      <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full" style={{width: '67%'}}></div>
      </div>
      <p className="text-xs text-gray-500 mt-2">Estimated completion: 3 minutes</p>
    </div>
  </CardContent>
</Card>
```

#### Content Library Browser
```jsx
<div className="content-library">
  <div className="flex items-center justify-between mb-6">
    <h2 className="text-2xl font-bold">Content Library</h2>
    <div className="flex items-center space-x-3">
      <Button variant="outline">
        <UploadIcon className="w-4 h-4 mr-2" />
        Upload Content
      </Button>
      <Button>
        <PlusIcon className="w-4 h-4 mr-2" />
        New Collection
      </Button>
    </div>
  </div>
  
  <div className="flex space-x-6">
    <div className="w-64 space-y-4">
      <div>
        <h3 className="font-medium mb-2">Categories</h3>
        <div className="space-y-1">
          {categories.map(category => (
            <button
              key={category.id}
              className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 text-sm"
            >
              <div className="flex items-center justify-between">
                <span>{category.name}</span>
                <span className="text-gray-400">{category.count}</span>
              </div>
            </button>
          ))}
        </div>
      </div>
      
      <div>
        <h3 className="font-medium mb-2">Content Types</h3>
        <div className="space-y-2">
          {contentTypes.map(type => (
            <label key={type.id} className="flex items-center space-x-2">
              <input type="checkbox" className="rounded" />
              <span className="text-sm">{type.name}</span>
              <span className="text-xs text-gray-400">({type.count})</span>
            </label>
          ))}
        </div>
      </div>
    </div>
    
    <div className="flex-1">
      <div className="mb-4">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <Input
              placeholder="Search content with AI..."
              className="pl-10"
            />
          </div>
          <Select>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="recent">Most Recent</SelectItem>
              <SelectItem value="popular">Most Used</SelectItem>
              <SelectItem value="quality">Highest Quality</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {contentItems.map(item => (
          <Card key={item.id} className="group hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-gray-100 rounded-lg">
                  <DocumentTextIcon className="w-5 h-5 text-gray-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium truncate">{item.title}</h4>
                  <p className="text-sm text-gray-500 line-clamp-2">{item.description}</p>
                  <div className="flex items-center space-x-4 mt-2 text-xs text-gray-400">
                    <span>{item.type}</span>
                    <span>{item.size}</span>
                    <span>{item.usage} uses</span>
                  </div>
                </div>
              </div>
              
              <div className="mt-3 flex items-center justify-between">
                <QualityScore score={item.qualityScore} />
                <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button size="sm" variant="ghost">
                    <EyeIcon className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  </div>
</div>
```

## 🔌 API Integration

### Required Endpoints
```typescript
// Course Management
GET    /api/v1/courses/pending-approval
POST   /api/v1/courses/:id/approve
POST   /api/v1/courses/:id/reject
GET    /api/v1/courses/:id/details

// AI Generation
POST   /api/v1/ai/generate-course
GET    /api/v1/ai/generation-status/:jobId
GET    /api/v1/ai/service-status
POST   /api/v1/ai/regenerate-component

// Content Library
GET    /api/v1/content-library/items
POST   /api/v1/content-library/upload
GET    /api/v1/content-library/search
DELETE /api/v1/content-library/:id

// Analytics
GET    /api/v1/course-manager/dashboard-stats
GET    /api/v1/course-manager/analytics
GET    /api/v1/ai/performance-metrics

// WebSocket for real-time updates
WS     /ws/generation-updates
WS     /ws/approval-notifications
```

### State Management
```typescript
interface CourseManagerState {
  pendingApprovals: Course[]
  generationQueue: GenerationJob[]
  contentLibrary: ContentItem[]
  aiStatus: AIServiceStatus
  dashboardStats: ManagerDashboardStats
  loading: boolean
  error: string | null
}

// React Query hooks
const usePendingApprovals = () => useQuery(['pending-approvals'], fetchPendingApprovals)
const useGenerationStatus = (jobId) => useQuery(['generation', jobId], () => fetchGenerationStatus(jobId))
const useContentLibrary = (filters) => useQuery(['content-library', filters], () => fetchContentLibrary(filters))
```

### WebSocket Integration
```typescript
const useGenerationUpdates = (jobId) => {
  const [status, setStatus] = useState(null)
  
  useEffect(() => {
    const ws = new WebSocket(`/ws/generation-updates/${jobId}`)
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data)
      setStatus(update)
    }
    
    return () => ws.close()
  }, [jobId])
  
  return status
}
```

## 🎯 Key Features to Implement

### AI-Powered Features
- Real-time generation progress monitoring
- AI quality assessment and scoring
- Intelligent content recommendations
- Automated quality validation
- Smart search and filtering

### Approval Workflow
- Multi-stage approval process
- Collaborative review tools
- Version control and history
- Bulk approval operations
- Automated notifications

### Content Management
- AI-indexed content library
- Semantic search capabilities
- Content categorization and tagging
- Usage analytics and insights
- Bulk operations and organization

### Real-time Features
- Live generation progress updates
- Instant approval notifications
- Real-time collaboration
- System status monitoring
- Performance metrics tracking

### Advanced UI Patterns
- Drag-and-drop content organization
- Advanced filtering and search
- Interactive data visualizations
- Progressive disclosure
- Contextual help and guidance

---

**Generate a complete, production-ready Course Manager Portal** with all the pages, components, and functionality specified above. Focus on creating an intelligent, powerful interface that enables course managers to efficiently handle AI-powered course generation, approval workflows, and content management. Include proper TypeScript types, real-time updates, error handling, and sophisticated UI patterns with Shadcn/ui components and Tailwind CSS styling. 