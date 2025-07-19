# User Management Service Architecture

## Overview
The User Management Service handles all user-related operations including authentication, authorization, and profile management across all portals of the Dynamic English Course Creator App.

## Core Features
- User registration and authentication
- Role-based access control (RBAC)
- Profile management
- Password management and recovery
- Session handling
- Multi-factor authentication (MFA)

## Technologies
- Node.js/TypeScript
- PostgreSQL
- AWS Cognito
- JWT for session management
- Redis for session caching

## Data Model
```sql
-- Core user table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User roles and permissions
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE role_permissions (
    role_id INTEGER REFERENCES roles(id),
    permission_id INTEGER REFERENCES permissions(id),
    PRIMARY KEY (role_id, permission_id)
);
```

## API Endpoints
```typescript
// Authentication
POST /auth/register
POST /auth/login
POST /auth/logout
POST /auth/refresh-token
POST /auth/forgot-password
POST /auth/reset-password

// Profile Management
GET /users/profile
PUT /users/profile
PUT /users/password

// Role Management (Admin only)
GET /roles
POST /roles
PUT /roles/:id
DELETE /roles/:id
```

## Security Measures
- Password hashing with bcrypt
- JWT token rotation
- Rate limiting on auth endpoints
- IP-based blocking
- Audit logging for sensitive operations

## Integration Points
- AWS Cognito for identity management
- Email service for notifications
- Audit logging service
- All portal services for authentication

## Monitoring & Alerts
- Failed login attempts
- Password reset requests
- User creation rate
- Session token usage
- API endpoint latency 