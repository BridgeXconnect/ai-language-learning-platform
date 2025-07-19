# Frontend Integration Plan - BMAD Method

## Current State Assessment

We have two frontend implementations:
1. **Original React frontend**: Built with Vite, React Router, and React Query
2. **New Next.js frontend**: Generated with v0.dev, using shadcn/ui components and Next.js App Router

The backend is a FastAPI application with:
- JWT authentication
- Role-based access control
- REST API endpoints
- WebSocket support for real-time features
- File upload handling

## Integration Strategy

We'll use the BMAD (Brownfield, Modular, Agile, Design-first) method to integrate the new Next.js frontend with the existing backend:

### 1. Authentication & Context Migration

- Adapt the Next.js `AuthContext` to work with the existing JWT authentication system
- Ensure proper token storage, refresh, and role-based access control
- Implement API service layer for backend communication

### 2. API Integration Layer

- Create API service modules for each domain (auth, sales, course-manager, trainer, student)
- Implement WebSocket service for real-time features
- Set up file upload utilities compatible with the backend

### 3. Component-by-Component Migration

Implement each portal in phases:
1. **Authentication Portal**: Login/Register flows
2. **Sales Portal**: Course requests, SOP uploads, dashboard
3. **Course Manager Portal**: AI generation, content management
4. **Trainer Portal**: Lesson management, feedback
5. **Student Portal**: Learning interface, progress tracking

### 4. Testing & Optimization

- End-to-end testing for each user journey
- Performance optimization
- Error handling improvements

## Implementation Plan

### Phase 1: Project Setup & Authentication (Week 1)

1. Set up Next.js project structure
   - Organize components by domain
   - Configure environment variables
   - Set up API service layer

2. Implement authentication
   - Adapt AuthContext to work with existing JWT system
   - Create login/register flows
   - Implement protected routes and role-based access

### Phase 2: Sales Portal Integration (Week 2)

1. Connect Sales dashboard to backend APIs
2. Implement course request wizard with file uploads
3. Connect data tables to backend pagination and filtering

### Phase 3: Course Manager Portal Integration (Week 3)

1. Implement course generation wizard
2. Connect WebSocket for real-time generation updates
3. Build course management interfaces

### Phase 4: Trainer & Student Portal Integration (Week 4)

1. Implement trainer dashboard and lesson management
2. Build student learning interface
3. Connect progress tracking and analytics

### Phase 5: Testing & Deployment (Week 5)

1. End-to-end testing for all user journeys
2. Performance optimization
3. Deployment configuration
4. Documentation

## Technical Decisions

1. **API Integration Approach**: Create a service layer that adapts the Next.js frontend to the existing API contracts
2. **Authentication Strategy**: Use Next.js middleware for protected routes, with JWT stored in HTTP-only cookies
3. **State Management**: Use React Context for global state, SWR or React Query for server state
4. **Styling**: Use Tailwind CSS with shadcn/ui components
5. **Deployment**: Configure Docker for production deployment

## Risks & Mitigations

1. **Authentication Mismatch**: 
   - Risk: JWT implementation differences between Next.js and existing system
   - Mitigation: Create comprehensive auth adapter layer

2. **API Contract Changes**: 
   - Risk: Frontend expectations vs. actual API responses
   - Mitigation: Create type-safe API client with proper error handling

3. **Performance Issues**: 
   - Risk: New UI components may have performance implications
   - Mitigation: Implement proper loading states, pagination, and caching

4. **WebSocket Integration**: 
   - Risk: Complexity in real-time feature implementation
   - Mitigation: Create reusable WebSocket hooks with reconnection logic

## Next Steps

1. Set up the Next.js project structure
2. Implement the authentication integration
3. Create the API service layer
4. Begin component-by-component integration 