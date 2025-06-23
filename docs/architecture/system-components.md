# Major System Components

## API Gateway / Load Balancer
- **Responsibilities:** Single entry point for client requests, request routing, load balancing, SSL termination, authentication/authorization enforcement, rate limiting
- **Technologies:** AWS API Gateway, AWS Application Load Balancer (ALB)

## User Management Service
- **Responsibilities:** User registration, authentication, authorization (RBAC), profile management, password management
- **Technologies:** Node.js/TypeScript, PostgreSQL, AWS Cognito

## Sales Service
- **Responsibilities:** Client course request lifecycle management, SOP handling and storage, request status management
- **Technologies:** Python/FastAPI or Node.js/NestJS, PostgreSQL, AWS S3

## Data Ingestion & SOP Processing Service
- **Responsibilities:** Document parsing, text pre-processing, knowledge extraction, embedding generation, vector database indexing
- **Technologies:** Python, spaCy/NLTK/Hugging Face Transformers, LLM APIs, Vector Database, AWS S3

## Course Generation Engine (CGE) Service
- **Responsibilities:** AI-powered curriculum design, content generation, exercise/assessment creation, SOP integration via RAG, content packaging
- **Technologies:** Python, LLM APIs (OpenAI, Anthropic, Google), MongoDB/AWS DocumentDB

## Course Management Service
- **Responsibilities:** Course review and approval workflow, content library management, trainer/student assignment, version control, reporting & analytics
- **Technologies:** Node.js/NestJS or Python/FastAPI, PostgreSQL, MongoDB

## Learning Service (Student Portal Backend)
- **Responsibilities:** Course content serving, student progress tracking, interactive exercise management, assessment handling, feedback collection
- **Technologies:** Node.js/Express.js, MongoDB, PostgreSQL, Redis

## Trainer Service (Trainer Portal Backend)
- **Responsibilities:** Course material access, student roster management, attendance tracking, feedback facilitation, manual grading support
- **Technologies:** Node.js/Express.js, MongoDB, PostgreSQL

## Notification Service
- **Responsibilities:** Email notifications, in-app notifications, SMS integration, event-driven notification triggers
- **Technologies:** Node.js/TypeScript, AWS SNS/SES, Kafka/RabbitMQ