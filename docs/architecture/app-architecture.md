# Dynamic English Course Creator App Architecture Document

## 1. Introduction / Preamble

This document outlines the overall project architecture for the Dynamic English Course Creator App, encompassing backend systems, shared services, and core infrastructure concerns. Its primary goal is to serve as the guiding architectural blueprint for development, ensuring consistency, scalability, security, and alignment with the product requirements.

## 2. Technical Summary

The Dynamic English Course Creator App adopts a **microservices-oriented architecture** deployed on **Amazon Web Services (AWS)**, enabling robust scalability, independent deployment, and domain-driven development for its distinct functional areas (Sales, Course Generation, Course Management, Training, and Student Learning). The core innovation lies in its **AI-powered Course Generation Engine**, which leverages advanced Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) techniques, coupled with a **vector database** for efficient contextual content creation from client SOPs.

## 3. High-Level Overview

### 3.1 Architectural Style

The application utilizes a **Microservices Architecture** with the following benefits:

- **Scalability:** Individual services can be scaled independently based on specific load and performance requirements
- **Resilience:** Failure in one service is less likely to affect the entire system
- **Maintainability & Modularity:** Smaller, focused services are easier to understand, develop, and maintain
- **Technology Diversity:** Allows selection of optimal technology stack for each service's specific needs
- **Independent Deployment:** Services can be deployed and updated independently

#### Key Services (Logical Grouping):

- **User Management Service:** Authentication, authorization, and user profiles across all portals
- **Sales Service:** Client requests, SOP uploads, and tracking
- **Course Generation Service:** Core AI engine for curriculum and content creation
- **Course Management Service:** Course lifecycle management, approvals, content library
- **Learning Service:** Student Portal functionality, progress tracking, content delivery
- **Trainer Service:** Trainer-specific functionalities like lesson delivery and feedback
- **Notification Service:** Email, in-app, and other alert management

### 3.2 Repository Structure

A **Polyrepo (Multi-Repository) approach** will be adopted, with each core microservice and frontend application residing in its own dedicated Git repository.

### 3.3 Primary Data Flow

1. **Sales Portal Submission:** Sales representative submits client request and uploads SOPs
2. **Request Ingestion:** Sales Service validates inputs, stores metadata, publishes "Order Course Creation" event
3. **SOP Processing:** Course Generation Service processes SOPs through OCR/text extraction, parsing, embedding generation, and vector database storage
4. **Curriculum Generation:** AI engine generates course outline using RAG against SOPs and LLM APIs
5. **Content Generation:** Detailed lesson content creation (dialogues, exercises, assessments) adapted to CEFR levels
6. **Content Packaging & Storage:** Generated content packaged and stored for Course Manager review
7. **Course Review:** Course Manager reviews, provides feedback, and approves content
8. **Trainer Assignment & Delivery:** Assignment to trainers and lesson delivery via Trainer Portal
9. **Student Learning:** Students access interactive content via Student Portal
10. **Feedback & Analytics:** Continuous feedback loop for system improvement

## 4. Definitive Tech Stack Selections

### 4.1 Cloud Provider
**Amazon Web Services (AWS)**
- Comprehensive AI/ML services (SageMaker, Lambda, Rekognition)
- Robust infrastructure for scalability (EC2, ECS, EKS)
- Strong security posture and industry adoption

### 4.2 Core Backend Services
- **Languages:** Python 3.x (AI/ML components), TypeScript/Node.js (APIs and web services)
- **Frameworks:** 
  - Python: FastAPI (high-performance APIs), Flask/Django (general-purpose services)
  - Node.js: Express.js or NestJS (API construction)

### 4.3 Frontend Development
- **Framework:** React.js (component-based architecture, large community support)
- **Language:** TypeScript (type safety and improved maintainability)

### 4.4 Databases
- **Relational Database:** PostgreSQL (AWS RDS PostgreSQL) for transactional data, user management, metadata
- **Vector Database:** Milvus or Pinecone (AWS OpenSearch Service with vector engine) for SOP embeddings and RAG
- **Document Database:** MongoDB (AWS DocumentDB) for generated course content

### 4.5 AI/ML & NLP Components
- **Large Language Models:** OpenAI GPT-4, Anthropic Claude 3, Google Gemini APIs
- **Local NLP Libraries:** spaCy, NLTK, Hugging Face Transformers for SOP pre-processing
- **Embeddings:** OpenAI Embeddings, Hugging Face Sentence Transformers, Cohere Embeddings

### 4.6 Containerization & Orchestration
- **Container Runtime:** Docker
- **Orchestration:** Kubernetes (AWS EKS) for robust, scalable, manageable microservices deployment

### 4.7 Message Queue/Event Bus
- **Technology:** Apache Kafka (AWS MSK) or RabbitMQ (AWS MQ) for asynchronous communication and event-driven architecture

### 4.8 Caching
- **Technology:** Redis (AWS ElastiCache for Redis) for high-performance in-memory data storage

### 4.9 Content Delivery Network
- **Technology:** AWS CloudFront for global content delivery of static assets

### 4.10 Monitoring & Logging
- **Logging:** AWS CloudWatch Logs with ELK Stack (Elasticsearch, Logstash, Kibana) or Datadog/Splunk
- **Monitoring:** AWS CloudWatch Metrics, Prometheus & Grafana for service-level metrics

### 4.11 Authentication & Authorization
- **Technology:** OAuth 2.0 and OpenID Connect via AWS Cognito or similar Identity as a Service (IDaaS) provider

## 5. Major System Components

### 5.1 API Gateway / Load Balancer
- **Responsibilities:** Single entry point for client requests, request routing, load balancing, SSL termination, authentication/authorization enforcement, rate limiting
- **Technologies:** AWS API Gateway, AWS Application Load Balancer (ALB)

### 5.2 User Management Service
- **Responsibilities:** User registration, authentication, authorization (RBAC), profile management, password management
- **Technologies:** Node.js/TypeScript, PostgreSQL, AWS Cognito

### 5.3 Sales Service
- **Responsibilities:** Client course request lifecycle management, SOP handling and storage, request status management
- **Technologies:** Python/FastAPI or Node.js/NestJS, PostgreSQL, AWS S3

### 5.4 Data Ingestion & SOP Processing Service
- **Responsibilities:** Document parsing, text pre-processing, knowledge extraction, embedding generation, vector database indexing
- **Technologies:** Python, spaCy/NLTK/Hugging Face Transformers, LLM APIs, Vector Database, AWS S3

### 5.5 Course Generation Engine (CGE) Service
- **Responsibilities:** AI-powered curriculum design, content generation, exercise/assessment creation, SOP integration via RAG, content packaging
- **Technologies:** Python, LLM APIs (OpenAI, Anthropic, Google), MongoDB/AWS DocumentDB

### 5.6 Course Management Service
- **Responsibilities:** Course review and approval workflow, content library management, trainer/student assignment, version control, reporting & analytics
- **Technologies:** Node.js/NestJS or Python/FastAPI, PostgreSQL, MongoDB

### 5.7 Learning Service (Student Portal Backend)
- **Responsibilities:** Course content serving, student progress tracking, interactive exercise management, assessment handling, feedback collection
- **Technologies:** Node.js/Express.js, MongoDB, PostgreSQL, Redis

### 5.8 Trainer Service (Trainer Portal Backend)
- **Responsibilities:** Course material access, student roster management, attendance tracking, feedback facilitation, manual grading support
- **Technologies:** Node.js/Express.js, MongoDB, PostgreSQL

### 5.9 Notification Service
- **Responsibilities:** Email notifications, in-app notifications, SMS integration, event-driven notification triggers
- **Technologies:** Node.js/TypeScript, AWS SNS/SES, Kafka/RabbitMQ

## 6. High-Level Data Models

### 6.1 Core Entities

#### User
- **Attributes:** UserID, Username, Email, Role, FirstName, LastName, Status
- **Storage:** PostgreSQL (User Management Service)

#### Course Request
- **Attributes:** RequestID, SalesUserID, CompanyName, Industry, TrainingObjectives, CEFRLevels, Status, Timestamps
- **Storage:** PostgreSQL (Sales Service)

#### SOP Document
- **Attributes:** SOPID, RequestID, FileName, StoragePath, ProcessingStatus, VectorIndexID
- **Storage:** PostgreSQL (metadata), AWS S3 (files), Vector Database (embeddings)

#### Course
- **Attributes:** CourseID, RequestID, Title, Description, TotalModules, TotalLessons, ApprovalStatus, Timestamps
- **Storage:** PostgreSQL (metadata), MongoDB (content)

#### Module & Lesson
- **Attributes:** ModuleID/LessonID, CourseID, Name, Objectives, Order, CEFRLevel, ContentPath
- **Storage:** MongoDB (as part of Course structure)

#### Student Progress
- **Attributes:** ProgressID, StudentID, CourseID, LessonID, CompletionStatus, Scores, Timestamps
- **Storage:** PostgreSQL (Learning Service)

## 7. Security Architecture

### 7.1 Authentication & Authorization
- **User Authentication:** Centralized via AWS Cognito with MFA support
- **Service-to-Service Authorization:** JWT tokens for microservice communication
- **Role-Based Access Control:** Granular permissions based on user roles

### 7.2 Network Security
- **Virtual Private Cloud (VPC):** All resources within private VPC
- **Subnets:** Private subnets for applications, public subnets for load balancers only
- **Security Groups:** Strict traffic control between components
- **Web Application Firewall (WAF):** AWS WAF for common exploit protection

### 7.3 Data Encryption
- **Encryption in Transit:** TLS 1.2+ for all communications
- **Encryption at Rest:** AWS KMS for databases and storage

### 7.4 SOP Data Protection
- **Dedicated S3 buckets** with restricted access
- **Strict IAM policies** for SOP data access
- **Audit logging** of all SOP access
- **Data retention policies** per client agreements

## 8. Scalability & Resilience

### 8.1 Horizontal Scaling
- **Microservices:** Independent scaling based on demand
- **Kubernetes:** Automatic scaling of service pods
- **Stateless Services:** Easy scaling and load balancing

### 8.2 Load Balancing
- **AWS Application Load Balancer:** Traffic distribution across service instances

### 8.3 Database Scaling
- **PostgreSQL:** AWS RDS Multi-AZ deployments and Read Replicas
- **MongoDB:** Replica sets and sharding for horizontal scaling
- **Vector Database:** High availability and horizontal scaling configurations

### 8.4 Caching Strategy
- **Redis:** Session management, content caching, rate limiting

### 8.5 High Availability
- **Multi-AZ Deployment:** Components across multiple Availability Zones
- **Automated Backups:** Daily backups with defined RPO/RTO
- **Fault Tolerance:** Circuit breakers, retries with exponential backoff

## 9. Monitoring & Logging Strategy

### 9.1 Centralized Logging
- **AWS CloudWatch Logs** for initial ingestion
- **ELK Stack** for advanced analytics and visualization
- **Structured Logging:** JSON format for easier parsing

### 9.2 Metrics Collection
- **Application Metrics:** KPIs like request rates, response times, error rates
- **System Health Metrics:** CPU, memory, disk I/O, network traffic
- **Business Metrics:** Course generation success rates, user engagement
- **Tools:** AWS CloudWatch Metrics, Prometheus, Grafana

### 9.3 Distributed Tracing
- **AWS X-Ray** or OpenTelemetry for request tracking across microservices

### 9.4 Alerting
- **AWS CloudWatch Alarms** or Prometheus Alertmanager
- **Notification Channels:** Email, Slack, PagerDuty

## 10. Deployment Strategy

### 10.1 Containerization
- **Docker containers** for all microservices and applications

### 10.2 Orchestration
- **Kubernetes (AWS EKS)** for automated deployment, scaling, and management

### 10.3 CI/CD Pipeline
- **AWS CodePipeline/CodeBuild** or GitHub Actions
- **Workflow:** Code commit → automated tests → Docker image build → Kubernetes deployment

### 10.4 Deployment Environments
- **Development:** Active coding and feature development
- **Staging:** Pre-production environment for integration testing
- **Production:** Live environment serving end-users

### 10.5 Deployment Patterns
- **Blue/Green Deployment** or **Canary Releases** for major updates
- **Rolling Updates** for minor changes

## 11. Future Considerations

### 11.1 Architectural Assumptions
- **AWS Service Stability:** Consistent availability and performance
- **LLM Provider Reliability:** Stable API access and consistent pricing
- **Vector Database Performance:** Sufficient performance for anticipated SOP volume
- **Team Skillset:** Acquisition of necessary technical skills

### 11.2 Architectural Constraints
- **Primary Cloud Provider:** AWS as mandated platform
- **Budget Constraints:** Defined limits for infrastructure and API costs
- **Compliance Requirements:** PDPA, GDPR adherence for data handling
- **Time-to-Market:** Aggressive MVP timeline favoring managed services
- **Security Standards:** Wall Street English internal security policies

### 11.3 Scalability Roadmap
- **Phase 1 (MVP):** Support 1,000 concurrent users, 100 courses
- **Phase 2 (6-12 months):** Scale to 5,000 concurrent users, 500 courses
- **Phase 3 (12-24 months):** Scale to 10,000+ concurrent users, 1,000+ courses

---

**Document Version:** 1.0  
**Last Updated:** December 2024  
**Owner:** Architecture Team  
**Reviewers:** Engineering Leadership, DevOps Team, Security Team