# Course Management Service Architecture

## Overview
The Course Management Service handles the lifecycle of courses from creation through approval, including version control, content management, and integration with the Course Generation Engine.

## Core Features
- Course lifecycle management
- Review and approval workflows
- Version control for course content
- Content organization and structuring
- Integration with Course Generation Engine
- Quality assurance workflows

## Technologies
- Python/FastAPI
- PostgreSQL
- MongoDB (course content)
- Redis (caching)
- AWS S3 (file storage)

## Data Models
```sql
-- Course definitions
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    cefr_level VARCHAR(10) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    version INTEGER DEFAULT 1,
    created_by INTEGER REFERENCES users(id),
    approved_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Course modules
CREATE TABLE modules (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    sequence_number INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Course lessons
CREATE TABLE lessons (
    id SERIAL PRIMARY KEY,
    module_id INTEGER REFERENCES modules(id),
    title VARCHAR(255) NOT NULL,
    content_id VARCHAR(100), -- References MongoDB content
    sequence_number INTEGER NOT NULL,
    duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Review records
CREATE TABLE course_reviews (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id),
    reviewer_id INTEGER REFERENCES users(id),
    status VARCHAR(50) NOT NULL,
    feedback TEXT,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## MongoDB Schema (Course Content)
```javascript
{
  _id: ObjectId,
  lesson_id: Number,
  content: {
    objectives: [String],
    materials: [{
      type: String,
      content: String,
      metadata: Object
    }],
    exercises: [{
      type: String,
      instructions: String,
      content: Object,
      answers: Object
    }],
    assessments: [{
      type: String,
      questions: Array,
      answers: Object,
      scoring: Object
    }]
  },
  version: Number,
  created_at: Date,
  updated_at: Date
}
```

## API Endpoints
### Course Management
- GET `/api/courses` - List all courses
- POST `/api/courses` - Create new course
- GET `/api/courses/:id` - Get course details
- PUT `/api/courses/:id` - Update course
- DELETE `/api/courses/:id` - Delete course

### Content Management
- GET `/api/courses/:id/modules` - List modules
- POST `/api/courses/:id/modules` - Add module
- GET `/api/modules/:id/lessons` - List lessons
- POST `/api/modules/:id/lessons` - Add lesson
- PUT `/api/lessons/:id/content` - Update lesson content

### Review Workflow
- POST `/api/courses/:id/submit` - Submit for review
- POST `/api/courses/:id/review` - Review course
- POST `/api/courses/:id/approve` - Approve course
- POST `/api/courses/:id/reject` - Reject course

## Integration Points
- Course Generation Engine (content creation)
- User Management Service (authentication)
- Learning Service (content delivery)
- Trainer Service (course access)
- Sales Service (course requests)

## Performance Metrics
- Course creation time: < 5 minutes
- Content update latency: < 2 seconds
- Review process time: < 24 hours
- API response time: < 500ms

## Monitoring & Alerts
- Course creation success rate
- Review pipeline metrics
- Content update success rate
- API endpoint performance
- Error rates and types 