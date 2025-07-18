# Naming Conventions Guide

This document outlines the standardized naming conventions for the AI Language Learning Platform.

## Overview

Consistent naming conventions improve code readability, maintainability, and developer experience. This project uses different conventions based on the technology and context.

## File and Directory Naming

### Python Files
- **Convention**: `snake_case`
- **Examples**: 
  - ✅ `auth_service.py`
  - ✅ `course_generation.py`
  - ❌ `authService.py`
  - ❌ `course-generation.py`

### TypeScript/JavaScript Files
- **Convention**: `kebab-case` (preferred) or `camelCase`
- **Examples**:
  - ✅ `auth-service.ts`
  - ✅ `course-request-wizard.tsx`
  - ✅ `useAuth.ts` (hooks)
  - ❌ `AuthService.ts`
  - ❌ `course_request_wizard.tsx`

### React Components
- **Convention**: `kebab-case` for files, `PascalCase` for components
- **Examples**:
  - ✅ File: `course-request-wizard.tsx`, Component: `CourseRequestWizard`
  - ✅ File: `auth-context.tsx`, Component: `AuthProvider`
  - ❌ File: `CourseRequestWizard.tsx`

### Directories
- **General**: `kebab-case`
- **Python Packages**: `snake_case` (with `__init__.py`)
- **Examples**:
  - ✅ `course-manager/`
  - ✅ `auth_service/` (Python package)
  - ✅ `ai-services/`
  - ❌ `courseManager/`
  - ❌ `AI_Services/`

## Code Naming

### Python
- **Variables**: `snake_case`
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

```python
# ✅ Good
class UserService:
    MAX_RETRY_ATTEMPTS = 3
    
    def __init__(self):
        self._connection = None
    
    def create_user(self, user_data: dict) -> User:
        return User(**user_data)

# ❌ Bad  
class userService:
    maxRetryAttempts = 3
    
    def createUser(self, userData: dict) -> User:
        return User(**userData)
```

### TypeScript/JavaScript
- **Variables**: `camelCase`
- **Functions**: `camelCase`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Types/Interfaces**: `PascalCase`
- **Enums**: `PascalCase`

```typescript
// ✅ Good
interface UserData {
  firstName: string;
  lastName: string;
}

class AuthService {
  private readonly MAX_RETRY_ATTEMPTS = 3;
  
  async authenticateUser(userData: UserData): Promise<User> {
    return this.processUser(userData);
  }
}

// ❌ Bad
interface user_data {
  first_name: string;
  last_name: string;
}

class auth_service {
  private readonly max_retry_attempts = 3;
  
  async authenticate_user(user_data: user_data): Promise<User> {
    return this.process_user(user_data);
  }
}
```

## Database Naming

### Tables
- **Convention**: `snake_case`
- **Examples**: `users`, `course_requests`, `lesson_content`

### Columns
- **Convention**: `snake_case`
- **Examples**: `user_id`, `created_at`, `first_name`

### Indexes
- **Convention**: `idx_{table}_{columns}`
- **Examples**: `idx_users_email`, `idx_course_requests_status`

## API Naming

### Endpoints
- **Convention**: `kebab-case` with clear resource hierarchy
- **Examples**:
  - ✅ `/api/course-requests`
  - ✅ `/api/users/{id}/courses`
  - ✅ `/api/auth/login`
  - ❌ `/api/courseRequests`
  - ❌ `/api/users/{id}/getCourses`

### JSON Fields
- **Convention**: `camelCase` for frontend APIs, `snake_case` for internal APIs
- **Examples**:
  ```json
  {
    "userId": 123,
    "firstName": "John",
    "createdAt": "2023-01-01T00:00:00Z"
  }
  ```

## Environment Variables

### Convention
- **Format**: `UPPER_SNAKE_CASE`
- **Grouping**: Use prefixes for related variables

### Examples
```bash
# ✅ Good
DATABASE_URL=postgresql://...
DATABASE_POOL_SIZE=10
JWT_SECRET_KEY=...
JWT_EXPIRE_MINUTES=30
OPENAI_API_KEY=...
SMTP_HOST=...
SMTP_PORT=587

# ❌ Bad
databaseUrl=postgresql://...
DatabasePoolSize=10
jwt-secret-key=...
openai_api_key=...
```

## Configuration Files

### File Names
- **Convention**: `kebab-case` with descriptive names
- **Examples**:
  - ✅ `next.config.mjs`
  - ✅ `tailwind.config.ts`
  - ✅ `docker-compose.yml`
  - ❌ `nextConfig.mjs`
  - ❌ `tailwind_config.ts`

## Git Branches

### Convention
- **Format**: `{type}/{short-description}`
- **Types**: `feature`, `fix`, `refactor`, `docs`, `test`

### Examples
```bash
# ✅ Good
feature/user-authentication
fix/course-generation-bug
refactor/domain-structure
docs/api-documentation

# ❌ Bad
userAuthentication
courseGenerationBugFix
Domain_Structure_Refactor
```

## Commit Messages

### Convention
- **Format**: `{type}: {description}`
- **Types**: `feat`, `fix`, `refactor`, `docs`, `test`, `style`, `chore`

### Examples
```bash
# ✅ Good
feat: add user authentication system
fix: resolve course generation timeout
refactor: reorganize backend domain structure
docs: update API documentation

# ❌ Bad
Added user authentication
Fixed bug
Refactoring
Updated docs
```

## Enforcement

Use the naming convention checker:

```bash
# Check current naming conventions
python3 scripts/enforce-naming-conventions.py

# View detailed report
cat refactoring-reports/naming-conventions-report.json
```

## Migration Guide

When renaming files or directories:

1. **Backup**: Always backup before renaming
2. **Update Imports**: Update all import statements
3. **Update Documentation**: Update any documentation references
4. **Test**: Verify functionality after changes
5. **Commit**: Commit changes with descriptive message

## Exceptions

Some exceptions to these rules are acceptable:

- **Third-party dependencies**: Keep original naming
- **Generated files**: Follow generator conventions
- **Legacy systems**: Gradual migration is acceptable
- **Industry standards**: Follow established patterns (e.g., `README.md`)

## Tools

- **Python**: Use `pylint` and `black` for formatting
- **TypeScript**: Use `eslint` and `prettier` for formatting
- **Naming Checker**: Use provided script for validation
