# High-Level Data Models

## Core Entities

### User
- **Attributes:** UserID, Username, Email, Role, FirstName, LastName, Status
- **Storage:** PostgreSQL (User Management Service)

### Course Request
- **Attributes:** RequestID, SalesUserID, CompanyName, Industry, TrainingObjectives, CEFRLevels, Status, Timestamps
- **Storage:** PostgreSQL (Sales Service)

### SOP Document
- **Attributes:** SOPID, RequestID, FileName, StoragePath, ProcessingStatus, VectorIndexID
- **Storage:** PostgreSQL (metadata), AWS S3 (files), Vector Database (embeddings)

### Course
- **Attributes:** CourseID, RequestID, Title, Description, TotalModules, TotalLessons, ApprovalStatus, Timestamps
- **Storage:** PostgreSQL (metadata), MongoDB (content)

### Module & Lesson
- **Attributes:** ModuleID/LessonID, CourseID, Name, Objectives, Order, CEFRLevel, ContentPath
- **Storage:** MongoDB (as part of Course structure)

### Student Progress
- **Attributes:** ProgressID, StudentID, CourseID, LessonID, CompletionStatus, Scores, Timestamps
- **Storage:** PostgreSQL (Learning Service)