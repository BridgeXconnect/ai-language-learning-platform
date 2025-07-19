# Architecture Document: Dynamic English Course Creator App

*This is the master architecture file that links to all sharded components following BMAD method v4 structure.*

## Document Structure

### Core Architecture Components
- [Overview](architecture/overview.md) - High-level architecture and data flow
- [Technology Stack](architecture/tech-stack.md) - Chosen technologies and rationale
- [System Components](architecture/system-components.md) - Major services and responsibilities
- [Data Models](architecture/data-models.md) - Core entities and relationships
- [Security Architecture](architecture/security-architecture.md) - Authentication, authorization, and data protection
- [Scalability & Resilience](architecture/scalability-resilience.md) - Scaling and high availability strategies
- [Monitoring & Logging](architecture/monitoring-logging.md) - Observability and alerting
- [Deployment Strategy](architecture/deployment-strategy.md) - CI/CD and deployment patterns
- [Future Considerations](architecture/future-considerations.md) - Assumptions, constraints, and roadmap

### Development Standards
- [Coding Standards](architecture/coding-standards.md) - Code quality and style guidelines
- [Source Tree Structure](architecture/source-tree.md) - Project organization and file purposes

### Legacy Component Documentation
The `architecture/components/` directory contains detailed documentation for individual microservices:
- [API Gateway](architecture/components/api-gateway.md)
- [Course Generation Engine](architecture/components/course-generation-engine.md)
- [Course Management](architecture/components/course-management.md)
- [Frontend](architecture/components/frontend.md)
- [Learning Service](architecture/components/learning-service.md)
- [Sales Service](architecture/components/sales-service.md)
- [Trainer Service](architecture/components/trainer-service.md)
- [User Management](architecture/components/user-management.md)
- [Vector Database](architecture/components/vector-db.md)

## Architecture Principles

### Microservices Architecture
- **Scalability**: Independent scaling based on service demand
- **Resilience**: Failure isolation and graceful degradation
- **Maintainability**: Smaller, focused services for easier development
- **Technology Diversity**: Optimal tech stack per service needs

### AI-First Design
- **Course Generation Engine**: Core innovation using LLMs and RAG
- **SOP Integration**: Vector database for contextual content creation
- **Quality Assurance**: AI confidence scoring and human review workflow

### Cloud-Native Approach
- **AWS Foundation**: Leveraging managed services for rapid development
- **Containerization**: Docker and Kubernetes for deployment
- **Event-Driven**: Asynchronous communication between services

## Development Context

This architecture supports:
- **BMAD Method v4**: Agent-driven development with clear documentation structure
- **Rapid Prototyping**: Monolithic development for MVP
- **Production Scaling**: Microservices architecture for enterprise deployment
- **Quality Assurance**: Comprehensive testing and monitoring strategies

## Usage Notes

For development teams:
1. **Dev Agents**: Always load coding standards, tech stack, and source tree docs
2. **Architecture Reviews**: Reference component docs for service boundaries
3. **Implementation**: Follow coding standards and deployment strategies
4. **Monitoring**: Implement logging and metrics as specified

---

**Document Version:** 1.0  
**Last Updated:** December 2024  
**Structure:** BMAD Method v4 Sharded  
**Owner:** Architecture Team