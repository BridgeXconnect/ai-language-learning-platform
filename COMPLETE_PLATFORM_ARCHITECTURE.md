# 🏗️ Complete AI Language Learning Platform Architecture

**Architect**: Winston (BMAD Architect)  
**Date**: Current  
**Status**: Comprehensive System Design  

---

## 🎯 **Architecture Overview**

### **Mission Statement**
Transform the existing foundation into a fully functional AI Language Learning Platform with real authentication, AI integrations, course creation, assessment systems, and user analytics.

### **Current State Analysis**
- ✅ **Strong Foundation**: Next.js + FastAPI, well-structured codebase
- ✅ **Testing Infrastructure**: Comprehensive test suite with Pydantic factories
- ❌ **Missing Core**: Real authentication, AI integrations, database with data
- ❌ **Missing Features**: Course content, assessment engine, user management

---

## 🏗️ **System Architecture Design**

### **1. Database Schema Architecture**

#### **Core Tables Design**
```sql
-- Users & Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Roles & Permissions
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255)
);

CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Courses & Content
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    cefr_level VARCHAR(10) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    version INTEGER DEFAULT 1,
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    ai_generated BOOLEAN DEFAULT FALSE,
    generation_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Course Modules
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    sequence_number INTEGER NOT NULL,
    duration_hours INTEGER DEFAULT 4,
    learning_objectives JSONB,
    vocabulary_themes JSONB,
    grammar_focus JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Course Lessons
CREATE TABLE lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id UUID REFERENCES modules(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content JSONB NOT NULL,
    sequence_number INTEGER NOT NULL,
    duration_minutes INTEGER,
    lesson_type VARCHAR(50) DEFAULT 'interactive',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Assessments
CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    assessment_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    scoring_config JSONB,
    time_limit_minutes INTEGER,
    is_final BOOLEAN DEFAULT FALSE,
    pass_threshold INTEGER DEFAULT 70,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Progress & Analytics
CREATE TABLE user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    time_spent_minutes INTEGER DEFAULT 0,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Assessment Results
CREATE TABLE assessment_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
    score DECIMAL(5,2),
    answers JSONB,
    time_taken_minutes INTEGER,
    passed BOOLEAN,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI Chat Sessions
CREATE TABLE ai_chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id),
    session_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **Indexes for Performance**
```sql
-- Performance indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_courses_status ON courses(status);
CREATE INDEX idx_courses_created_by ON courses(created_by);
CREATE INDEX idx_modules_course_id ON modules(course_id);
CREATE INDEX idx_lessons_module_id ON lessons(module_id);
CREATE INDEX idx_user_progress_user_course ON user_progress(user_id, course_id);
CREATE INDEX idx_assessment_results_user ON assessment_results(user_id);
```

### **2. API Architecture Design**

#### **RESTful API Structure**
```
/api/v1/
├── auth/
│   ├── POST /register
│   ├── POST /login
│   ├── POST /logout
│   ├── POST /refresh
│   └── GET /profile
├── courses/
│   ├── GET /
│   ├── POST /
│   ├── GET /{id}
│   ├── PUT /{id}
│   ├── DELETE /{id}
│   ├── POST /{id}/generate-ai
│   └── GET /{id}/modules
├── modules/
│   ├── GET /
│   ├── POST /
│   ├── GET /{id}
│   ├── PUT /{id}
│   └── DELETE /{id}
├── lessons/
│   ├── GET /
│   ├── POST /
│   ├── GET /{id}
│   ├── PUT /{id}
│   └── DELETE /{id}
├── assessments/
│   ├── GET /
│   ├── POST /
│   ├── GET /{id}
│   ├── POST /{id}/submit
│   └── GET /{id}/results
├── progress/
│   ├── GET /user/{user_id}
│   ├── POST /update
│   └── GET /analytics
├── ai/
│   ├── POST /chat
│   ├── POST /generate-content
│   ├── POST /create-assessment
│   └── POST /analyze-progress
└── admin/
    ├── GET /users
    ├── GET /courses
    ├── POST /approve-course
    └── GET /analytics
```

#### **API Response Standards**
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

### **3. Authentication System Architecture**

#### **JWT-Based Authentication Flow**
```python
# Authentication Service Architecture
class AuthenticationService:
    def __init__(self):
        self.jwt_secret = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    async def register_user(self, user_data: UserRegistration):
        # 1. Validate user data
        # 2. Hash password
        # 3. Create user record
        # 4. Send verification email
        # 5. Return user info (no token)
    
    async def login_user(self, credentials: UserLogin):
        # 1. Verify credentials
        # 2. Generate access & refresh tokens
        # 3. Store refresh token hash
        # 4. Return tokens + user info
    
    async def refresh_token(self, refresh_token: str):
        # 1. Validate refresh token
        # 2. Generate new access token
        # 3. Return new access token
    
    async def verify_token(self, token: str):
        # 1. Decode and verify JWT
        # 2. Check user exists and is active
        # 3. Return user info
```

#### **Security Implementation**
```python
# Security Middleware
class SecurityMiddleware:
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.cors_handler = CORSMiddleware()
    
    async def authenticate_request(self, request: Request):
        # 1. Extract token from header
        # 2. Verify token
        # 3. Add user to request state
        # 4. Check permissions
    
    async def rate_limit_check(self, request: Request):
        # 1. Check rate limits
        # 2. Block if exceeded
        # 3. Update counters
```

### **4. AI Integration Architecture**

#### **AI Service Orchestration**
```python
# AI Service Manager
class AIServiceManager:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.nlp_service = AdvancedNLPService()
        self.recommendation_engine = AIRecommendationEngine()
    
    async def generate_course_content(self, topic: str, level: str):
        # 1. Use OpenAI for content generation
        # 2. Use NLP service for analysis
        # 3. Structure content into modules/lessons
        # 4. Return structured course data
    
    async def create_assessment(self, content: str, difficulty: str):
        # 1. Use Anthropic for question generation
        # 2. Validate questions with NLP
        # 3. Generate answer explanations
        # 4. Return assessment structure
    
    async def provide_tutoring(self, user_message: str, context: dict):
        # 1. Use Anthropic for conversational AI
        # 2. Include learning context
        # 3. Provide personalized responses
        # 4. Track conversation for analytics
```

#### **AI API Integration Patterns**
```python
# OpenAI Integration
class OpenAIIntegration:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_course_outline(self, topic: str, level: str):
        prompt = f"""
        Create a comprehensive course outline for {topic} at {level} level.
        Include:
        - Module structure
        - Learning objectives
        - Key vocabulary themes
        - Grammar focus areas
        """
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return self.parse_course_outline(response.choices[0].message.content)
    
    async def generate_lesson_content(self, module: str, objectives: list):
        # Generate interactive lesson content
        pass

# Anthropic Integration
class AnthropicIntegration:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def create_assessment_questions(self, content: str, count: int = 10):
        prompt = f"""
        Create {count} assessment questions based on this content:
        {content}
        
        Include multiple choice questions with explanations.
        """
        response = await self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        return self.parse_assessment_questions(response.content[0].text)
```

### **5. Frontend Architecture**

#### **Component Architecture**
```
src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── AuthProvider.tsx
│   ├── courses/
│   │   ├── CourseCard.tsx
│   │   ├── CourseCreator.tsx
│   │   ├── ModuleViewer.tsx
│   │   └── LessonPlayer.tsx
│   ├── assessment/
│   │   ├── AssessmentBuilder.tsx
│   │   ├── QuizPlayer.tsx
│   │   └── ResultsViewer.tsx
│   ├── ai/
│   │   ├── AIChatInterface.tsx
│   │   ├── ContentGenerator.tsx
│   │   └── TutorInterface.tsx
│   ├── dashboard/
│   │   ├── UserDashboard.tsx
│   │   ├── ProgressTracker.tsx
│   │   └── AnalyticsView.tsx
│   └── shared/
│       ├── Navigation.tsx
│       ├── LoadingSpinner.tsx
│       └── ErrorBoundary.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useCourses.ts
│   ├── useAI.ts
│   └── useProgress.ts
├── services/
│   ├── api.ts
│   ├── auth.ts
│   └── ai.ts
└── utils/
    ├── constants.ts
    ├── helpers.ts
    └── types.ts
```

#### **State Management**
```typescript
// Zustand Store Architecture
interface AppState {
  // Auth State
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Course State
  courses: Course[];
  currentCourse: Course | null;
  userProgress: UserProgress[];
  
  // AI State
  aiChatHistory: ChatMessage[];
  isAIGenerating: boolean;
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  fetchCourses: () => Promise<void>;
  updateProgress: (progress: UserProgress) => Promise<void>;
  sendAIMessage: (message: string) => Promise<void>;
}

const useAppStore = create<AppState>((set, get) => ({
  // State
  user: null,
  isAuthenticated: false,
  isLoading: false,
  courses: [],
  currentCourse: null,
  userProgress: [],
  aiChatHistory: [],
  isAIGenerating: false,
  
  // Actions
  login: async (credentials) => {
    set({ isLoading: true });
    try {
      const response = await authService.login(credentials);
      set({ 
        user: response.user, 
        isAuthenticated: true, 
        isLoading: false 
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },
  
  // ... other actions
}));
```

### **6. Deployment Architecture**

#### **Production Infrastructure**
```yaml
# Docker Compose Production
version: '3.8'
services:
  # Backend API
  api:
    build: ./server
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - postgres
      - redis
  
  # Frontend
  frontend:
    build: ./client
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=${API_URL}
  
  # Database
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
      - frontend

volumes:
  postgres_data:
  redis_data:
```

#### **Environment Configuration**
```bash
# Production Environment Variables
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=your-super-secret-jwt-key
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
CORS_ORIGINS=https://yourdomain.com
ENVIRONMENT=production
```

---

## 🚀 **Implementation Roadmap**

### **Phase 1: Foundation (Days 1-2)**
1. **Database Setup**
   - Create PostgreSQL database
   - Run migration scripts
   - Set up indexes and constraints
   - Seed initial data

2. **Authentication System**
   - Implement JWT authentication
   - Create user registration/login
   - Add password hashing
   - Set up role-based permissions

3. **Basic API Structure**
   - Set up FastAPI with middleware
   - Create authentication routes
   - Add error handling
   - Implement rate limiting

### **Phase 2: Core Features (Days 3-5)**
1. **AI Integration**
   - Connect OpenAI API
   - Connect Anthropic API
   - Implement AI service manager
   - Add error handling and fallbacks

2. **Course Management**
   - Create course CRUD operations
   - Implement module/lesson structure
   - Add AI-powered content generation
   - Create course approval workflow

3. **Frontend Authentication**
   - Build login/register forms
   - Implement auth context
   - Add protected routes
   - Create user dashboard

### **Phase 3: Learning Features (Days 6-8)**
1. **Assessment System**
   - Build assessment creation
   - Implement quiz player
   - Add automated grading
   - Create results tracking

2. **Progress Tracking**
   - Implement user progress
   - Add learning analytics
   - Create progress dashboard
   - Build achievement system

3. **AI Tutoring**
   - Create AI chat interface
   - Implement conversation history
   - Add personalized responses
   - Build tutoring analytics

### **Phase 4: Polish & Testing (Days 9-10)**
1. **Integration Testing**
   - Test complete user flows
   - Validate AI integrations
   - Performance testing
   - Security testing

2. **Deployment**
   - Set up production environment
   - Configure monitoring
   - Deploy to production
   - Final validation

---

## 🔒 **Security Architecture**

### **Authentication Security**
- JWT tokens with short expiration
- Refresh token rotation
- Password hashing with bcrypt
- Rate limiting on auth endpoints
- CORS configuration

### **Data Security**
- Row Level Security (RLS) policies
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection

### **API Security**
- API key management
- Request signing
- Rate limiting
- Request logging
- Error handling without data leakage

---

## 📊 **Monitoring & Analytics**

### **Application Monitoring**
```python
# Monitoring Service
class MonitoringService:
    def __init__(self):
        self.metrics = {}
        self.logger = logging.getLogger(__name__)
    
    async def track_user_action(self, user_id: str, action: str, metadata: dict):
        # Track user actions for analytics
        pass
    
    async def monitor_ai_performance(self, service: str, response_time: float, success: bool):
        # Monitor AI service performance
        pass
    
    async def track_course_completion(self, user_id: str, course_id: str, score: float):
        # Track learning outcomes
        pass
```

### **Analytics Dashboard**
- User engagement metrics
- Course completion rates
- AI service performance
- Learning outcome analysis
- System health monitoring

---

## 🎯 **Success Metrics**

### **Technical Metrics**
- API response time < 200ms
- 99.9% uptime
- Zero security vulnerabilities
- < 1% error rate

### **Business Metrics**
- User registration completion > 80%
- Course completion rate > 60%
- AI response satisfaction > 4.5/5
- User retention > 70%

---

## 🚀 **Next Steps**

1. **Immediate Actions**
   - Set up PostgreSQL database
   - Configure environment variables
   - Implement authentication system
   - Connect AI APIs

2. **Development Workflow**
   - Use BMAD agents for implementation
   - Follow test-driven development
   - Implement continuous integration
   - Regular security reviews

3. **Deployment Strategy**
   - Staging environment testing
   - Gradual rollout
   - Monitoring and alerting
   - Backup and recovery

---

**Architecture Status**: ✅ **Complete**  
**Ready for Implementation**: ✅ **Yes**  
**BMAD Agent Coordination**: ✅ **Planned**  

**Next**: Activate Developer (James) to begin implementation following this architecture. 