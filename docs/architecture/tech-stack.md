# Technology Stack

## Cloud Provider
**Amazon Web Services (AWS)**
- Comprehensive AI/ML services (SageMaker, Lambda, Rekognition)
- Robust infrastructure for scalability (EC2, ECS, EKS)
- Strong security posture and industry adoption

## Core Backend Services
- **Languages:** Python 3.x (AI/ML components), TypeScript/Node.js (APIs and web services)
- **Frameworks:** 
  - Python: FastAPI (high-performance APIs), Flask/Django (general-purpose services)
  - Node.js: Express.js or NestJS (API construction)

## Frontend Development
- **Framework:** React.js (component-based architecture, large community support)
- **Language:** TypeScript (type safety and improved maintainability)

## Databases
- **Relational Database:** PostgreSQL (AWS RDS PostgreSQL) for transactional data, user management, metadata
- **Vector Database:** Milvus or Pinecone (AWS OpenSearch Service with vector engine) for SOP embeddings and RAG
- **Document Database:** MongoDB (AWS DocumentDB) for generated course content

## AI/ML & NLP Components
- **Large Language Models:** OpenAI GPT-4, Anthropic Claude 3, Google Gemini APIs
- **Local NLP Libraries:** spaCy, NLTK, Hugging Face Transformers for SOP pre-processing
- **Embeddings:** OpenAI Embeddings, Hugging Face Sentence Transformers, Cohere Embeddings

## Containerization & Orchestration
- **Container Runtime:** Docker
- **Orchestration:** Kubernetes (AWS EKS) for robust, scalable, manageable microservices deployment

## Message Queue/Event Bus
- **Technology:** Apache Kafka (AWS MSK) or RabbitMQ (AWS MQ) for asynchronous communication and event-driven architecture

## Caching
- **Technology:** Redis (AWS ElastiCache for Redis) for high-performance in-memory data storage

## Content Delivery Network
- **Technology:** AWS CloudFront for global content delivery of static assets

## Monitoring & Logging
- **Logging:** AWS CloudWatch Logs with ELK Stack (Elasticsearch, Logstash, Kibana) or Datadog/Splunk
- **Monitoring:** AWS CloudWatch Metrics, Prometheus & Grafana for service-level metrics

## Authentication & Authorization
- **Technology:** OAuth 2.0 and OpenID Connect via AWS Cognito or similar Identity as a Service (IDaaS) provider