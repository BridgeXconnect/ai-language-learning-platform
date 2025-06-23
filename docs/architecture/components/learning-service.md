# Learning Service Architecture

## Overview
The Learning Service manages the student learning experience, including content delivery, progress tracking, and interactive exercise handling in the Dynamic English Course Creator App.

## Core Features
- Course content delivery
- Interactive exercise management
- Progress tracking
- Assessment handling
- Student feedback collection
- Performance analytics

## Technologies
- Node.js/Express.js
- MongoDB (content storage)
- PostgreSQL (student data)
- Redis (caching)
- WebSocket (real-time features)

## Data Models
```sql
-- Student Progress
CREATE TABLE student_progress (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id),
    course_id INTEGER REFERENCES courses(id),
    lesson_id INTEGER REFERENCES lessons(id),
    completion_status VARCHAR(20),
    score INTEGER,
    time_spent_seconds INTEGER,
    last_accessed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exercise Submissions
CREATE TABLE exercise_submissions (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id),
    exercise_id INTEGER REFERENCES exercises(id),
    answers JSONB,
    score INTEGER,
    feedback TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints
### Student Dashboard
- GET `/api/student/dashboard-stats`
- GET `/api/student/courses`
- GET `/api/student/courses/:id/progress`

### Content Access
- GET `/api/student/courses/:id/lessons/:lessonId`
- GET `/api/student/exercises/:id`
- POST `/api/student/exercises/:id/submit`

### Progress & Analytics
- GET `/api/student/performance`
- GET `/api/student/progress`
- POST `/api/student/feedback`

## Performance Metrics
- Content load time: < 2 seconds
- Exercise submission processing: < 1 second
- Progress tracking latency: < 500ms
- Analytics calculation time: < 3 seconds 