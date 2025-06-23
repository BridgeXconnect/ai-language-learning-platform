# Product Requirements Document (PRD): Dynamic English Course Creator App

## 1. Introduction

### 1.1 Executive Summary

The Dynamic English Course Creator App is an innovative platform designed to transform Wall Street English Thailand's approach to delivering tailored English language training for corporate clients. Moving beyond a fixed curriculum, this AI-powered solution will streamline and automate the creation of highly customized, job-specific English courses. By leveraging advanced AI to integrate client-provided Standard Operating Procedures (SOPs) and adapt content to specific CEFR proficiency levels, the platform will enable rapid course development, enhance learning effectiveness, and significantly expand Wall Street English's marketable product offerings.

### 1.2 Purpose

This Product Requirements Document (PRD) outlines the detailed functional and non-functional requirements for the Dynamic English Course Creator App. It serves as the definitive guide for all stakeholders involved in the product's development, ensuring a shared understanding of its objectives, features, and overall scope.

### 1.3 Scope

The initial scope of this product includes the development of:

- A **Sales Portal** for submitting client training requests and SOPs
- A **Course Generation Engine** utilizing AI/NLP for dynamic curriculum and content creation
- A **Course Manager Dashboard** for oversight, approval, and content/user management
- A **Trainer Portal** for lesson delivery and feedback
- A **Student Portal** for interactive learning and progress tracking

## 2. Problem Statement

Currently, the process of creating customized English language courses for corporate clients is heavily manual, time-consuming, and resource-intensive. This often involves bespoke curriculum design and content creation for each client, limiting the scalability and efficiency of Wall Street English Thailand's corporate training division. The lack of automation restricts the ability to rapidly respond to market demand, adapt to diverse client needs, or efficiently integrate client-specific technical language and Standard Operating Procedures (SOPs) into the curriculum.

**Key Problems:**
- **High operational costs** associated with manual course development
- **Limited scalability** for custom training solutions
- **Slower time-to-market** for new corporate training programs
- **Inconsistent quality** in customized course content due to manual processes
- **Reduced competitive advantage** in a dynamic corporate training market

## 3. Goals & Objectives

### 3.1 Primary Goals

**Goal 1: Enhance Scalability & Efficiency**
- Reduce average time for custom course creation from request to ready-for-delivery by 70% within 12 months post-launch
- Increase volume of custom courses delivered to corporate clients by 50% within the first year

**Goal 2: Drive Customization & Relevance**
- Ensure AI-generated custom course content seamlessly integrates client-specific SOPs with high fidelity
- Achieve 85% Course Manager approval rate for AI-generated course outlines without significant manual revisions within 6 months

**Goal 3: Improve Learning Outcomes & Engagement**
- Maintain or exceed current student completion rates for custom courses (target: 80% completion within 3 months of course start)
- Increase average student engagement scores by 15% compared to existing digital content

**Goal 4: Expand Product Offering & Market Position**
- Establish a new "SOP-integrated" English training solutions product line within 9 months
- Position Wall Street English Thailand as a leader in innovative, AI-powered corporate language training solutions within 18 months

## 4. Target Audience & User Personas

### 4.1 Sales Team (Portal User)
- **Primary Interaction:** Initiating course creation requests, inputting client requirements, uploading SOPs
- **Needs:** Intuitive form-based interface, clear guidance on required inputs, confirmation of submission

### 4.2 Course Manager / Administrator (Dashboard User)
- **Primary Interaction:** Reviewing and approving AI-generated curricula, managing trainers, monitoring student progress
- **Needs:** Comprehensive dashboard views, detailed review tools, clear approval workflows, robust reporting

### 4.3 Trainers (Portal User)
- **Primary Interaction:** Accessing lesson plans, delivering lessons, tracking student attendance, providing feedback
- **Needs:** Organized access to pedagogical resources, clear lesson delivery instructions, efficient feedback tools

### 4.4 Students (Portal User)
- **Primary Interaction:** Accessing course content, completing interactive exercises, participating in assessments
- **Needs:** Engaging learning interface, diverse interactive activities, clear progress visualization, personalized learning paths

## 5. Core Features

### 5.1 Sales Portal Features

#### 5.1.1 Client & Training Needs Request Form
- **Client Information Input:** Company details, industry, size, primary contact
- **Training Cohort Profile:** Participant count, current/target CEFR levels, roles/departments
- **Training Objectives & Pain Points:** Specific learning goals and current challenges
- **SOP & Document Upload:** Secure mechanism for uploading client SOPs, glossaries, handbooks
- **Content Customization Preferences:** Preferred scenarios, key terminology, tone/formality
- **Course Structure Preferences:** Total length, lessons per module, delivery method, scheduling

#### 5.1.2 Request Submission & Confirmation
- **Submit Button:** Finalize and send request to Course Manager
- **Submission Confirmation:** In-app and email confirmation
- **Email Notifications:** Automated notifications to relevant stakeholders

#### 5.1.3 Request Tracking & Status View
- **"My Requests" List:** Dashboard view of all submitted requests
- **Status Indicators:** Clear labels for request lifecycle stages
- **Basic Details View:** Access to initial input details

### 5.2 Course Generation Engine Features

#### 5.2.1 AI-Powered Curriculum Design & Structuring
- **Input Processing:** Ingests client objectives, CEFR levels, course length, delivery preferences
- **CEFR-Aligned Curriculum Generation:** Creates logical learning progression based on WSE 80-lesson foundation
- **Modular Course Outline:** Generates structured course with modules, lessons, and objectives
- **Complexity Scaling:** Adjusts curriculum complexity based on CEFR level progression

#### 5.2.2 SOP-Integrated & Contextual Content Generation
- **SOP Knowledge Retrieval (RAG):** Utilizes parsed SOP data via Retrieval-Augmented Generation
- **LLM-Driven Content Creation:** Generates dialogues, scenarios, reading passages, grammar explanations
- **CEFR-Adaptive Language:** Ensures content aligns with specified CEFR level complexity
- **Industry-Specific Contextualization:** Integrates SOP-specific jargon and processes

#### 5.2.3 Dynamic Exercise & Assessment Creation
- **Exercise Generation:** Creates diverse exercise types linked to lesson content and CEFR level
- **Quiz Generation:** Produces end-of-lesson comprehension checks
- **Assessment Generation:** Designs comprehensive module/course evaluations
- **Answer Key Generation:** Creates detailed answer keys and grading rubrics

#### 5.2.4 Multi-Format Content Packaging
- **Trainer Lesson Plans:** Detailed documents with objectives, activities, timings, teaching notes
- **Presentation Slides:** Downloadable slide decks for lesson delivery
- **Student Materials:** Printable/digital worksheets and handouts
- **Digital Content Bundling:** Organized packages for portal upload

### 5.3 Course Manager Dashboard Features

#### 5.3.1 Dashboard Overview & KPIs
- **Course Creation Funnel:** Displays counts by status (Awaiting Review, Under Development, Approved)
- **Content Performance:** AI approval rates, revision needs, most edited sections
- **User Activity Metrics:** Active students/trainers, new enrollments
- **System Health:** SOP processing and content generation indicators

#### 5.3.2 Course Review & Approval Workflow
- **Review Queue:** List of courses awaiting review
- **Detailed Curriculum View:** Hierarchical display of course structure and content
- **AI Confidence Display:** Shows confidence scores and flagged anomalies
- **Approval Actions:** Approve & Publish, Request Revision, Edit Directly, Decline

#### 5.3.3 Content Library Management
- **WSE Core Course Management:** Interface to view and update foundational content
- **SOP Repository:** Searchable repository of client documents with version control
- **Reusable Content Snippets:** Library of approved content for reuse
- **Content Tagging:** Metadata management for efficient AI retrieval

### 5.4 Trainer Portal Features

#### 5.4.1 Dashboard Overview
- **Upcoming Lessons:** Clear list of scheduled lessons
- **Assigned Courses:** Overview of current course assignments
- **Attendance Tracking:** Quick access to mark student attendance

#### 5.4.2 Course & Lesson Materials Access
- **Lesson Plan View:** Step-by-step lesson plans with timings and activities
- **Presentation Slides:** Access to downloadable slide decks
- **Student Materials:** Worksheets and handouts for distribution
- **Multimedia Resources:** Audio/video content for lessons

#### 5.4.3 Student Management
- **Course-Specific Rosters:** Lists of enrolled students
- **Progress Tracking:** Individual student progress and performance
- **Feedback Tools:** Structured forms for lesson and student feedback

### 5.5 Student Portal Features

#### 5.5.1 Dashboard Overview
- **Current Course Highlight:** Prominent display of active course
- **Progress Visualization:** Overall and module-level completion tracking
- **Next Activity:** Clear call-to-action for next learning step

#### 5.5.2 Interactive Learning Experience
- **Lesson Content Access:** Structured, navigable lesson materials
- **Multimedia Integration:** Embedded audio/video for listening practice
- **Interactive Exercises:** Diverse exercise types with immediate feedback
- **Assessment Tools:** Formal evaluations with automated and manual grading

#### 5.5.3 Progress & Performance Tracking
- **Skill Mastery Visualization:** Progress across language skills
- **Score History:** Review of quiz and assessment results
- **Time Tracking:** Monitor learning time and activity

## 6. Non-Functional Requirements (NFRs)

### 6.1 Performance & Scalability
- **Course Generation Speed:** Complete single-module course generation within 30 minutes
- **Concurrent Users:** Support 1,000 concurrent students and 100 concurrent trainers
- **Page Load Times:** All portal pages load within 3 seconds
- **Database Responsiveness:** Common queries complete within 500 milliseconds
- **Horizontal Scalability:** Architecture designed to scale 2x within 2 years

### 6.2 Security
- **Data Encryption:** All sensitive data encrypted at rest and in transit (TLS 1.2+)
- **Access Control:** Robust Role-Based Access Control (RBAC)
- **Authentication:** Secure authentication with multi-factor authentication capabilities
- **SOP Confidentiality:** Strict measures to prevent unauthorized access to client SOPs
- **Vulnerability Management:** Regular security audits and dependency updates

### 6.3 Usability & User Experience
- **Intuitive Interface:** User-friendly interfaces with clear navigation
- **Consistency:** Consistent look, feel, and interaction patterns across portals
- **Error Handling:** Clear, actionable error messages
- **Responsiveness:** Fully responsive design across devices
- **Accessibility:** WCAG 2.1 AA compliance

### 6.4 Reliability & Availability
- **Uptime:** Minimum 99.9% uptime (excluding planned maintenance)
- **Data Backup:** Automated daily backups with 24-hour RPO and 4-hour RTO
- **Fault Tolerance:** Graceful degradation and automatic recovery mechanisms
- **AI Model Stability:** Highly stable AI models with minimal unexpected outputs

## 7. Out of Scope (For Initial Version)

To maintain focus and deliver a robust MVP, the following functionalities are explicitly out of scope:

- **Direct Student-to-Student Communication:** No in-app messaging beyond structured peer review
- **Native Mobile Applications:** Responsive web applications only, no dedicated iOS/Android apps
- **Advanced Gamification Systems:** Basic gamification only (points, badges, basic leaderboards)
- **External LMS Integration:** Standalone platform operation, no third-party LMS integration
- **Real-time Video Conferencing:** Assumes use of external tools (Zoom, Teams) for live sessions
- **Automated Content Translation:** English-only content generation and SOP processing
- **Comprehensive CRM Integration:** Basic request submission only, no deep CRM integration

## 8. Future Considerations & Roadmap

### Phase 2 Enhancements (6-12 months post-MVP)
- **Advanced AI Personalization:** Real-time adaptive learning paths based on individual performance
- **Multi-Language Support:** Expansion to other language pairs (Thai-English, Japanese-English)
- **Enhanced Gamification:** Narrative-driven progress, collaborative challenges, advanced rewards
- **Native Mobile Applications:** Dedicated iOS and Android applications

### Phase 3 Innovations (12-24 months post-MVP)
- **Deep WSE System Integration:** Integration with existing CRM, HR, and internal platforms
- **AI-Powered Content Recommendations:** Proactive learning resource suggestions
- **Automated Trainer Matching:** AI-driven trainer-course-student matching
- **Advanced Analytics & Reporting:** Predictive analytics for learning outcomes

## 9. Success Metrics

### 9.1 Operational Metrics
- **Course Generation Time:** Reduction from current manual process by 70%
- **Course Approval Rate:** 85% approval rate without significant revisions
- **System Uptime:** Maintain 99.9% availability
- **User Adoption Rate:** 90% user adoption across all user roles within 6 months

### 9.2 Business Metrics
- **Revenue Growth:** 50% increase in custom course revenue within 12 months
- **Client Satisfaction:** 90% client satisfaction rating for AI-generated courses
- **Market Position:** Recognition as leading AI-powered corporate language training provider
- **Operational Cost Reduction:** 40% reduction in course development operational costs

### 9.3 Learning Effectiveness Metrics
- **Student Completion Rate:** Maintain or exceed 80% course completion rate
- **Learning Outcomes:** Demonstrate measurable CEFR level progression
- **Engagement Metrics:** 15% increase in time spent on platform and exercise completion rates
- **Content Quality:** Consistent positive feedback on content relevance and applicability

## 10. Key Assumptions & Constraints

### 10.1 Assumptions
- **LLM API Availability:** Consistent access to stable, cost-effective LLM APIs (GPT-4, Claude, Gemini)
- **SOP Parsability:** Client SOPs generally in parseable digital formats (PDF, DOCX, TXT)
- **WSE Course Data Quality:** Existing 80-lesson course sufficiently structured for AI foundation
- **Client SOP Sharing:** Corporate clients willing to share confidential SOPs for customization
- **Trainer Adoption:** Trainers adaptable to AI-generated content and new portal tools
- **Infrastructure Scalability:** Cloud infrastructure can provide necessary compute and storage resources

### 10.2 Constraints
- **Budget:** Development and operational costs within agreed-upon budget parameters
- **Timeline:** MVP delivery within target launch timeline
- **Technology Familiarity:** Initial choices influenced by organizational expertise for rapid development
- **Data Compliance:** Adherence to PDPA (Thailand), GDPR (international clients), and other relevant regulations
- **Security Requirements:** Compliance with Wall Street English internal security policies and industry standards

## 11. Risk Assessment

### 11.1 Technical Risks
- **AI Model Performance:** Risk of inconsistent or low-quality content generation
- **Scalability Challenges:** Potential performance issues under high load
- **Integration Complexity:** Difficulties integrating multiple AI services and databases
- **Data Processing Issues:** Challenges in parsing diverse SOP formats

### 11.2 Business Risks
- **Market Acceptance:** Potential resistance to AI-generated educational content
- **Competitive Response:** Competitors developing similar AI-powered solutions
- **Client Data Security:** Risks associated with handling sensitive corporate SOPs
- **Regulatory Changes:** Evolving AI and data privacy regulations

### 11.3 Mitigation Strategies
- **Technical:** Comprehensive testing, gradual rollout, backup systems, regular model evaluation
- **Business:** Pilot programs, strong security measures, continuous market monitoring, legal compliance reviews
- **Operational:** Training programs, change management, stakeholder engagement, feedback loops

---

**Document Version:** 1.0  
**Last Updated:** December 2024  
**Owner:** Product Team  
**Stakeholders:** Engineering, Design, Sales, Course Management, Executive Leadership