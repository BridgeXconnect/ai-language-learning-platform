# Trainer Service Architecture

## Overview
The Trainer Service manages all trainer-specific functionalities, including lesson delivery, student progress monitoring, and feedback management in the Dynamic English Course Creator App.

## Core Features
- Course material access
- Student roster management
- Attendance tracking
- Student performance monitoring
- Feedback facilitation
- Manual grading support
- Lesson scheduling

## Technologies
- Node.js/Express.js
- PostgreSQL
- Redis (caching)
- WebSocket (real-time updates)

## Data Models
```sql
-- Trainer Assignments
CREATE TABLE trainer_assignments (
    id SERIAL PRIMARY KEY,
    trainer_id INTEGER REFERENCES users(id),
    course_id INTEGER REFERENCES courses(id),
    assignment_notes TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Attendance Records
CREATE TABLE attendance_records (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER REFERENCES lessons(id),
    student_id INTEGER REFERENCES users(id),
    trainer_id INTEGER REFERENCES users(id),
    present BOOLEAN,
    notes TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trainer Feedback
CREATE TABLE trainer_feedback (
    id SERIAL PRIMARY KEY,
    trainer_id INTEGER REFERENCES users(id),
    student_id INTEGER REFERENCES users(id),
    lesson_id INTEGER REFERENCES lessons(id),
    feedback_text TEXT,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    skill_ratings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints
### Dashboard & Overview
- GET `/api/trainer/dashboard-stats`
- GET `/api/trainer/assigned-courses`
- GET `/api/trainer/schedule`

### Course & Lesson Management
- GET `/api/trainer/courses/:id`
- GET `/api/trainer/courses/:id/lessons/:lessonId`
- POST `/api/trainer/lessons/:id/attendance`
- POST `/api/trainer/lessons/:id/feedback`

### Student Management
- GET `/api/trainer/students`
- GET `/api/trainer/students/:id/progress`
- POST `/api/trainer/students/:id/feedback`

### Reporting
- GET `/api/trainer/reports/student-progress`

## Performance Metrics
- Dashboard load time: < 2 seconds
- Attendance marking: < 500ms
- Feedback submission: < 1 second
- Report generation: < 5 seconds 