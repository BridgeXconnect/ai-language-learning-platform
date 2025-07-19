# Coding Standards

## General Principles

### Code Quality
- **Readability First:** Code should be self-documenting and easy to understand
- **Consistency:** Follow established patterns and conventions throughout the codebase
- **Simplicity:** Prefer simple solutions over complex ones (KISS principle)
- **DRY Principle:** Don't Repeat Yourself - extract common functionality
- **SOLID Principles:** Follow Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion

### Documentation
- **API Documentation:** All APIs must be documented using OpenAPI/Swagger
- **Code Comments:** Complex business logic requires inline comments
- **README Files:** Each service requires comprehensive README with setup instructions
- **Architecture Decision Records (ADRs):** Document significant architectural decisions

## Backend Standards

### Python Standards
- **Style Guide:** Follow PEP 8 with line length of 88 characters (Black formatter)
- **Type Hints:** Use type hints for all function signatures and class attributes
- **Docstrings:** Use Google-style docstrings for all functions and classes
- **Error Handling:** Use specific exception types and meaningful error messages
- **Testing:** Minimum 80% code coverage with pytest

```python
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def process_sop_document(
    document_path: str,
    client_id: int,
    processing_options: Optional[dict] = None
) -> dict:
    """Process an SOP document for course generation.
    
    Args:
        document_path: Path to the SOP document file
        client_id: Unique identifier for the client
        processing_options: Optional configuration for processing
        
    Returns:
        Dictionary containing processing results and metadata
        
    Raises:
        DocumentProcessingError: If document cannot be processed
        ValidationError: If inputs are invalid
    """
    # Implementation here
    pass
```

### Node.js/TypeScript Standards
- **Style Guide:** Use Prettier with ESLint configuration
- **Type Safety:** Strict TypeScript configuration with no implicit any
- **Error Handling:** Use Result pattern or proper Error classes
- **Async/Await:** Prefer async/await over Promises chains
- **Testing:** Use Jest with minimum 80% coverage

```typescript
interface CourseRequest {
  clientId: number;
  companyName: string;
  trainingObjectives: string[];
  cefrLevels: CEFRLevel[];
  sopDocuments: SOPDocument[];
}

class CourseGenerationService {
  async generateCourse(request: CourseRequest): Promise<Course> {
    try {
      // Validate input
      this.validateRequest(request);
      
      // Process SOPs
      const sopData = await this.processSopDocuments(request.sopDocuments);
      
      // Generate curriculum
      const curriculum = await this.generateCurriculum(request, sopData);
      
      return curriculum;
    } catch (error) {
      logger.error('Course generation failed', { error, requestId: request.id });
      throw new CourseGenerationError('Failed to generate course', error);
    }
  }
}
```

## Frontend Standards

### React/TypeScript Standards
- **Component Structure:** Use functional components with hooks
- **Props Interface:** Define TypeScript interfaces for all component props
- **State Management:** Use React Query for server state, Context for local state
- **Styling:** Use CSS Modules or styled-components with consistent naming
- **Testing:** React Testing Library with minimum 70% coverage

```tsx
interface CourseCardProps {
  course: Course;
  onSelect: (courseId: string) => void;
  className?: string;
}

export const CourseCard: React.FC<CourseCardProps> = ({
  course,
  onSelect,
  className
}) => {
  const handleClick = useCallback(() => {
    onSelect(course.id);
  }, [course.id, onSelect]);

  return (
    <div className={`course-card ${className}`} onClick={handleClick}>
      <h3>{course.title}</h3>
      <p>{course.description}</p>
      <div className="course-meta">
        <span>Modules: {course.moduleCount}</span>
        <span>CEFR: {course.cefrLevel}</span>
      </div>
    </div>
  );
};
```

## Database Standards

### SQL Standards
- **Naming:** Use snake_case for tables and columns
- **Indexes:** Create appropriate indexes for query performance
- **Migrations:** All schema changes via versioned migrations
- **Constraints:** Use foreign keys and check constraints appropriately

```sql
-- Good table design
CREATE TABLE course_requests (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    company_name VARCHAR(255) NOT NULL,
    training_objectives TEXT[],
    cefr_levels VARCHAR(2)[] CHECK (
        array_length(cefr_levels, 1) > 0
    ),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_course_requests_client_id ON course_requests(client_id);
CREATE INDEX idx_course_requests_status ON course_requests(status);
```

## API Standards

### RESTful API Design
- **HTTP Methods:** Use appropriate HTTP methods (GET, POST, PUT, DELETE)
- **Status Codes:** Return appropriate HTTP status codes
- **Response Format:** Consistent JSON response structure
- **Versioning:** API versioning via URL path (/api/v1/)
- **Rate Limiting:** Implement rate limiting on all public endpoints

```json
{
  "success": true,
  "data": {
    "course": {
      "id": "course_123",
      "title": "Business English for Healthcare",
      "status": "approved",
      "modules": []
    }
  },
  "meta": {
    "timestamp": "2024-12-20T10:30:00Z",
    "version": "1.0"
  }
}
```

## Security Standards

### Authentication & Authorization
- **JWT Tokens:** Use short-lived access tokens with refresh tokens
- **Password Security:** Bcrypt with minimum 12 rounds for hashing
- **Input Validation:** Validate and sanitize all user inputs
- **SQL Injection:** Use parameterized queries only
- **XSS Protection:** Implement Content Security Policy headers

### Environment Variables
- **Secrets Management:** Never commit secrets to version control
- **Environment Files:** Use .env files for local development
- **Production Secrets:** Use AWS Secrets Manager or similar for production

## Testing Standards

### Unit Testing
- **Coverage:** Minimum 80% code coverage for backend, 70% for frontend
- **Test Structure:** Arrange, Act, Assert pattern
- **Naming:** Descriptive test names that explain the scenario
- **Mocking:** Mock external dependencies and APIs

### Integration Testing
- **Database Tests:** Use test database with transactions rollback
- **API Tests:** Test complete request/response cycles
- **E2E Tests:** Critical user flows must have end-to-end tests

## Git Standards

### Commit Messages
```
type(scope): description

[optional body]

[optional footer]
```

Types: feat, fix, docs, style, refactor, test, chore

Example:
```
feat(course-generation): add SOP processing pipeline

Implement document parsing and embedding generation
for SOP documents with support for PDF and DOCX formats.

Closes #123
```

### Branch Strategy
- **Main Branch:** `main` - production-ready code
- **Feature Branches:** `feature/ticket-description`
- **Hotfix Branches:** `hotfix/issue-description`
- **Pull Requests:** Required for all changes to main branch

## Performance Standards

### Backend Performance
- **Response Times:** API endpoints must respond within 500ms for 95th percentile
- **Database Queries:** No N+1 queries, use proper indexing
- **Caching:** Implement caching for frequently accessed data
- **Memory Usage:** Monitor and optimize memory consumption

### Frontend Performance
- **Bundle Size:** Keep JavaScript bundles under 250KB gzipped
- **Loading Times:** Initial page load under 3 seconds
- **Code Splitting:** Implement route-based code splitting
- **Image Optimization:** Use WebP format and appropriate sizing

## Error Handling

### Logging Standards
- **Structured Logging:** Use JSON format for all logs
- **Log Levels:** Appropriate use of DEBUG, INFO, WARN, ERROR
- **Sensitive Data:** Never log passwords or sensitive information
- **Context:** Include relevant context (user ID, request ID, etc.)

```python
import structlog

logger = structlog.get_logger()

def process_request(request_id: str, user_id: str):
    logger.info(
        "Processing course generation request",
        request_id=request_id,
        user_id=user_id,
        action="course_generation_start"
    )
```

## Code Review Standards

### Review Checklist
- [ ] Code follows established style guidelines
- [ ] All tests pass and coverage meets requirements
- [ ] Security considerations have been addressed
- [ ] Performance implications have been considered
- [ ] Documentation has been updated if necessary
- [ ] Error handling is appropriate
- [ ] Logging provides sufficient debugging information