# Architecture Overview

## Introduction / Preamble

This document outlines the overall project architecture for the Dynamic English Course Creator App, encompassing backend systems, shared services, and core infrastructure concerns. Its primary goal is to serve as the guiding architectural blueprint for development, ensuring consistency, scalability, security, and alignment with the product requirements.

## Technical Summary

The Dynamic English Course Creator App adopts a **microservices-oriented architecture** deployed on **Amazon Web Services (AWS)**, enabling robust scalability, independent deployment, and domain-driven development for its distinct functional areas (Sales, Course Generation, Course Management, Training, and Student Learning). The core innovation lies in its **AI-powered Course Generation Engine**, which leverages advanced Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) techniques, coupled with a **vector database** for efficient contextual content creation from client SOPs.

## High-Level Overview

### Architectural Style

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

### Repository Structure

A **Polyrepo (Multi-Repository) approach** will be adopted, with each core microservice and frontend application residing in its own dedicated Git repository.

### Primary Data Flow

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