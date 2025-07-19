# AI Language Learning Platform - Development Standards

## Overview

This document establishes comprehensive development standards for the AI Language Learning Platform, ensuring consistent code quality, maintainable architecture, and reliable deployment processes across all development teams and AI agents.

## Code Quality Standards

### General Principles

#### Core Values
- **Readability First**: Code should be self-documenting and easily understood by team members
- **Consistency**: Follow established patterns and conventions throughout the codebase
- **Simplicity**: Prefer simple, clear solutions over complex ones (KISS principle)
- **DRY Principle**: Don't Repeat Yourself - extract common functionality into reusable modules
- **SOLID Principles**: Follow Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion

#### Code Organization
- **Modular Architecture**: Organize code into logical modules with clear boundaries
- **Separation of Concerns**: Separate business logic, data access, and presentation layers
- **Dependency Management**: Use dependency injection and avoid tight coupling
- **Configuration Management**: Externalize configuration and use environment-specific settings

### Backend Development Standards

#### Python/FastAPI Standards
- **Style Guide**: Follow PEP 8 with line length of 88 characters (Black formatter)
- **Type Hints**: Use type hints for all function signatures and class attributes
- **Docstrings**: Use Google-style docstrings for all functions and classes
- **Error Handling**: Use specific exception types and meaningful error messages
- **Testing**: Minimum 80% code coverage with pytest

```python
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class CourseRequest(BaseModel):
    """Represents a client course generation request."""
    
    client_id: int = Field(..., description="Unique client identifier")
    company_name: str = Field(..., min_length=1, max_length=255)
    training_objectives: List[str] = Field(..., min_items=1)
    cefr_levels: List[str] = Field(..., description="Target CEFR levels")
    sop_documents: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

async def process_course_request(
    request: CourseRequest,
    ai_service: AIService,
    processing_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process a course generation request using AI services.
    
    Args:
        request: The course generation request
        ai_service: AI service instance for content generation
        processing_options: Optional configuration for processing
        
    Returns:
        Dictionary containing processing results and metadata
        
    Raises:
        CourseGenerationError: If course generation fails
        ValidationError: If request validation fails
    """
    try:
        # Validate request
        await validate_course_request(request)
        
        # Process SOPs
        sop_data = await process_sop_documents(request.sop_documents)
        
        # Generate course content
        course_content = await ai_service.generate_course(
            request=request,
            sop_context=sop_data,
            options=processing_options
        )
        
        logger.info(
            "Course generation completed successfully",
            extra={
                "client_id": request.client_id,
                "company_name": request.company_name,
                "module_count": len(course_content.modules)
            }
        )
        
        return {
            "success": True,
            "course_content": course_content,
            "processing_time": course_content.generation_time,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
    except Exception as e:
        logger.error(
            "Course generation failed",
            extra={
                "client_id": request.client_id,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        raise CourseGenerationError(f"Failed to generate course: {str(e)}") from e
```

#### Database Standards
- **Naming**: Use snake_case for tables and columns
- **Indexes**: Create appropriate indexes for query performance
- **Migrations**: All schema changes via versioned migrations using Alembic
- **Constraints**: Use foreign keys and check constraints appropriately
- **Transactions**: Use database transactions for data consistency

```sql
-- Example table design with proper constraints and indexes
CREATE TABLE course_requests (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    training_objectives TEXT[] NOT NULL CHECK (array_length(training_objectives, 1) > 0),
    cefr_levels VARCHAR(2)[] NOT NULL CHECK (
        array_length(cefr_levels, 1) > 0 AND
        cefr_levels <@ ARRAY['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    ),
    status VARCHAR(50) DEFAULT 'pending' CHECK (
        status IN ('pending', 'processing', 'completed', 'approved', 'rejected')
    ),
    sop_documents TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    
    CONSTRAINT valid_cefr_levels CHECK (
        array_length(cefr_levels, 1) <= 6
    )
);

-- Performance indexes
CREATE INDEX idx_course_requests_client_id ON course_requests(client_id);
CREATE INDEX idx_course_requests_status ON course_requests(status);
CREATE INDEX idx_course_requests_created_at ON course_requests(created_at);
CREATE INDEX idx_course_requests_company_name ON course_requests USING gin(company_name gin_trgm_ops);

-- Trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_course_requests_updated_at
    BEFORE UPDATE ON course_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Frontend Development Standards

#### React/TypeScript Standards
- **Component Structure**: Use functional components with hooks
- **Props Interface**: Define TypeScript interfaces for all component props
- **State Management**: Use React Query for server state, Zustand for client state
- **Styling**: Use Tailwind CSS with consistent component patterns
- **Testing**: React Testing Library with minimum 70% coverage

```typescript
interface CourseCardProps {
  course: Course;
  onSelect: (courseId: string) => void;
  onEdit?: (courseId: string) => void;
  className?: string;
  showActions?: boolean;
}

export const CourseCard: React.FC<CourseCardProps> = ({
  course,
  onSelect,
  onEdit,
  className = "",
  showActions = true
}) => {
  const [isLoading, setIsLoading] = React.useState(false);
  
  const handleSelect = React.useCallback(async () => {
    setIsLoading(true);
    try {
      await onSelect(course.id);
    } catch (error) {
      console.error('Failed to select course:', error);
    } finally {
      setIsLoading(false);
    }
  }, [course.id, onSelect]);

  const handleEdit = React.useCallback(() => {
    if (onEdit) {
      onEdit(course.id);
    }
  }, [course.id, onEdit]);

  return (
    <div className={`
      bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow
      ${className}
    `}>
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-semibold text-gray-900 line-clamp-2">
          {course.title}
        </h3>
        {showActions && (
          <div className="flex space-x-2">
            <button
              onClick={handleEdit}
              className="text-blue-600 hover:text-blue-800 text-sm"
              disabled={isLoading}
            >
              Edit
            </button>
          </div>
        )}
      </div>
      
      <p className="text-gray-600 mb-4 line-clamp-3">
        {course.description}
      </p>
      
      <div className="flex justify-between items-center">
        <div className="flex space-x-4 text-sm text-gray-500">
          <span>Modules: {course.moduleCount}</span>
          <span>CEFR: {course.cefrLevel}</span>
          <span>Duration: {course.estimatedHours}h</span>
        </div>
        
        <button
          onClick={handleSelect}
          disabled={isLoading}
          className={`
            px-4 py-2 text-sm font-medium rounded-md
            ${isLoading 
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
              : 'bg-blue-600 text-white hover:bg-blue-700'
            }
          `}
        >
          {isLoading ? 'Loading...' : 'Select Course'}
        </button>
      </div>
    </div>
  );
};
```

### API Development Standards

#### RESTful API Design
- **HTTP Methods**: Use appropriate HTTP methods (GET, POST, PUT, PATCH, DELETE)
- **Status Codes**: Return appropriate HTTP status codes
- **Response Format**: Consistent JSON response structure
- **Versioning**: API versioning via URL path (/api/v1/)
- **Rate Limiting**: Implement rate limiting on all public endpoints

```json
{
  "success": true,
  "data": {
    "course": {
      "id": "course_123",
      "title": "Business English for Healthcare",
      "status": "approved",
      "modules": [],
      "metadata": {
        "cefr_level": "B2",
        "estimated_hours": 40,
        "created_at": "2024-12-20T10:30:00Z",
        "updated_at": "2024-12-20T10:30:00Z"
      }
    }
  },
  "meta": {
    "timestamp": "2024-12-20T10:30:00Z",
    "version": "1.0",
    "request_id": "req_abc123"
  }
}
```

## Review Processes

### Code Review Standards

#### Pre-Review Checklist
- [ ] All tests pass locally
- [ ] Code follows established style guidelines
- [ ] Documentation has been updated
- [ ] Security considerations have been addressed
- [ ] Performance implications have been considered

#### Review Criteria
- **Functionality**: Code works as intended and meets requirements
- **Security**: No security vulnerabilities or data exposure risks
- **Performance**: Efficient algorithms and database queries
- **Maintainability**: Clear, readable code with appropriate comments
- **Testing**: Adequate test coverage and edge case handling

#### Review Process
1. **Automated Checks**: CI/CD pipeline runs automated tests and linting
2. **Peer Review**: At least one team member reviews the code
3. **Architecture Review**: Complex changes reviewed by senior developers
4. **Security Review**: Security-sensitive changes reviewed by security team
5. **Final Approval**: Team lead or designated reviewer approves merge

### Pull Request Guidelines

#### PR Template
```markdown
## Description
Brief description of changes made

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] Security implications considered

## Related Issues
Closes #123
```

#### Branch Strategy
- **Main Branch**: `main` - production-ready code
- **Feature Branches**: `feature/TICKET-short-description`
- **Hotfix Branches**: `hotfix/TICKET-issue-description`
- **Release Branches**: `release/v1.2.0`

## Testing Requirements

### Testing Strategy

#### Test Pyramid
- **Unit Tests**: 80% coverage for business logic
- **Integration Tests**: API endpoints and database interactions
- **End-to-End Tests**: Critical user workflows
- **Load Tests**: Performance under expected load

#### Test Categories
- **Functional Tests**: Verify feature behavior
- **Security Tests**: Vulnerability scanning and penetration testing
- **Performance Tests**: Load, stress, and scalability testing
- **Usability Tests**: User experience and accessibility testing

### Unit Testing Standards

#### Python Testing (pytest)
```python
import pytest
from unittest.mock import Mock, patch
from app.services.course_generation import CourseGenerationService
from app.models.course import Course
from app.exceptions import CourseGenerationError

class TestCourseGenerationService:
    """Test suite for CourseGenerationService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_ai_service = Mock()
        self.service = CourseGenerationService(ai_service=self.mock_ai_service)
    
    @pytest.mark.asyncio
    async def test_generate_course_success(self):
        """Test successful course generation."""
        # Arrange
        request = CourseRequest(
            client_id=1,
            company_name="Test Corp",
            training_objectives=["Improve communication"],
            cefr_levels=["B1", "B2"]
        )
        
        expected_course = Course(
            id="course_123",
            title="Business English for Test Corp",
            modules=[]
        )
        
        self.mock_ai_service.generate_course.return_value = expected_course
        
        # Act
        result = await self.service.generate_course(request)
        
        # Assert
        assert result.success is True
        assert result.course_content.id == "course_123"
        self.mock_ai_service.generate_course.assert_called_once_with(
            request=request,
            sop_context=None,
            options=None
        )
    
    @pytest.mark.asyncio
    async def test_generate_course_validation_error(self):
        """Test course generation with invalid request."""
        # Arrange
        invalid_request = CourseRequest(
            client_id=1,
            company_name="",  # Invalid empty name
            training_objectives=[],  # Invalid empty objectives
            cefr_levels=["B1"]
        )
        
        # Act & Assert
        with pytest.raises(ValidationError):
            await self.service.generate_course(invalid_request)
    
    @pytest.mark.asyncio
    async def test_generate_course_ai_service_error(self):
        """Test course generation when AI service fails."""
        # Arrange
        request = CourseRequest(
            client_id=1,
            company_name="Test Corp",
            training_objectives=["Improve communication"],
            cefr_levels=["B1"]
        )
        
        self.mock_ai_service.generate_course.side_effect = Exception("AI service unavailable")
        
        # Act & Assert
        with pytest.raises(CourseGenerationError) as exc_info:
            await self.service.generate_course(request)
        
        assert "Failed to generate course" in str(exc_info.value)
```

#### Frontend Testing (Jest + React Testing Library)
```typescript
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CourseCard } from './CourseCard';
import { Course } from '../types/course';

const mockCourse: Course = {
  id: 'course_123',
  title: 'Business English for Healthcare',
  description: 'Comprehensive course for healthcare professionals',
  moduleCount: 5,
  cefrLevel: 'B2',
  estimatedHours: 40,
  status: 'approved'
};

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });
  
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('CourseCard', () => {
  const mockOnSelect = jest.fn();
  const mockOnEdit = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders course information correctly', () => {
    renderWithQueryClient(
      <CourseCard
        course={mockCourse}
        onSelect={mockOnSelect}
        onEdit={mockOnEdit}
      />
    );

    expect(screen.getByText('Business English for Healthcare')).toBeInTheDocument();
    expect(screen.getByText(/Comprehensive course for healthcare/)).toBeInTheDocument();
    expect(screen.getByText('Modules: 5')).toBeInTheDocument();
    expect(screen.getByText('CEFR: B2')).toBeInTheDocument();
    expect(screen.getByText('Duration: 40h')).toBeInTheDocument();
  });

  test('calls onSelect when select button is clicked', async () => {
    renderWithQueryClient(
      <CourseCard
        course={mockCourse}
        onSelect={mockOnSelect}
      />
    );

    const selectButton = screen.getByText('Select Course');
    fireEvent.click(selectButton);

    await waitFor(() => {
      expect(mockOnSelect).toHaveBeenCalledWith('course_123');
    });
  });

  test('shows loading state when select is in progress', async () => {
    const slowOnSelect = jest.fn(() => 
      new Promise(resolve => setTimeout(resolve, 100))
    );

    renderWithQueryClient(
      <CourseCard
        course={mockCourse}
        onSelect={slowOnSelect}
      />
    );

    const selectButton = screen.getByText('Select Course');
    fireEvent.click(selectButton);

    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(selectButton).toBeDisabled();

    await waitFor(() => {
      expect(screen.getByText('Select Course')).toBeInTheDocument();
    });
  });

  test('does not show edit button when onEdit is not provided', () => {
    renderWithQueryClient(
      <CourseCard
        course={mockCourse}
        onSelect={mockOnSelect}
      />
    );

    expect(screen.queryByText('Edit')).not.toBeInTheDocument();
  });

  test('hides actions when showActions is false', () => {
    renderWithQueryClient(
      <CourseCard
        course={mockCourse}
        onSelect={mockOnSelect}
        onEdit={mockOnEdit}
        showActions={false}
      />
    );

    expect(screen.queryByText('Edit')).not.toBeInTheDocument();
  });
});
```

## Documentation Standards

### Code Documentation

#### Inline Comments
- **Purpose**: Explain complex business logic and non-obvious code
- **Style**: Clear, concise explanations of why, not what
- **Frequency**: Comment complex algorithms, business rules, and edge cases

#### API Documentation
- **OpenAPI/Swagger**: All REST endpoints must be documented
- **Request/Response Examples**: Include realistic examples
- **Error Codes**: Document all possible error responses
- **Authentication**: Clearly specify authentication requirements

#### README Files
- **Service README**: Each service requires comprehensive setup instructions
- **Project README**: High-level overview and quick start guide
- **Deployment README**: Deployment and configuration instructions

### Architecture Documentation

#### Architecture Decision Records (ADRs)
- **Format**: Use standard ADR template
- **Storage**: Version control with code
- **Updates**: Keep current with implementation changes

#### System Documentation
- **Component Diagrams**: Visual representation of system architecture
- **Data Flow Diagrams**: Show how data moves through the system
- **Integration Guides**: How to integrate with external systems

### User Documentation

#### User Guides
- **Role-based Guides**: Separate guides for each user role
- **Step-by-step Instructions**: Clear, actionable instructions
- **Screenshots**: Visual aids for complex workflows

#### Training Materials
- **Video Tutorials**: Screen recordings for complex features
- **Interactive Demos**: Hands-on learning experiences
- **FAQ**: Common questions and troubleshooting

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Next Review**: Quarterly  
**Document Owner**: BMAD Architect Agent