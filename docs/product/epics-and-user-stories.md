# Dynamic English Course Creator App: Epics & Initial User Stories

## High-Level Epics (Top-Level Project Components)

These Epics represent major, distinct features or modules of the application, aligning with our key user roles and core system functionalities.

## Epic 1: User & Authentication Management

**Goal:** Establish a secure and robust system for user registration, login, and profile management across all portals.

**Related Portals:** All (Sales, Course Manager, Trainer, Student)

### User Stories

#### User Story 1.1: Secure User Login
**As a** registered user of any portal (Sales, CM, Trainer, Student)  
**I want to** securely log in with my credentials  
**So that** I can access my designated portal and its functionalities

**Acceptance Criteria:**
- The system presents a login screen with fields for username/email and password
- The system validates credentials against registered users
- Upon successful login, I am redirected to my role-specific dashboard
- Upon failed login, an appropriate error message is displayed without revealing specific credential issues
- Password is encrypted both in transit and at rest
- The system handles concurrent login attempts securely

#### User Story 1.2: Password Reset Functionality
**As a** user who has forgotten my password  
**I want to** be able to reset it securely  
**So that** I can regain access to my account without administrative intervention

**Acceptance Criteria:**
- The login screen includes a "Forgot Password?" link
- Clicking the link prompts me to enter my registered email address
- Upon submitting a valid email, the system sends a secure password reset link to that email
- The password reset link has a defined expiry time
- The reset process guides me to set a new password, enforcing strong password policies
- An email notification confirms the password change after successful reset

#### User Story 1.3: User Registration (Admin/Sales Assisted)
**As an** Administrator or Sales Representative  
**I want to** register new users (Course Managers, Trainers, Students) for the platform  
**So that** they can access their respective portals

**Acceptance Criteria:**
- The system provides an interface for authorized users to input new user details
- The system assigns the correct role to the new user upon registration
- Upon successful registration, the new user receives an automated welcome email with login instructions
- The system ensures that each email address is unique for user registration
- Admin/Sales can specify if the user needs to set their own password on first login

#### User Story 1.4: View & Update User Profile
**As a** logged-in user  
**I want to** view and update my basic profile information  
**So that** my account details are accurate and up-to-date

**Acceptance Criteria:**
- I can access a "My Profile" section from within my portal
- The profile section displays my current name, email, and other relevant details
- I can edit my name and contact details (if applicable)
- The system validates updated information (e.g., email format)
- Upon saving changes, a confirmation message is displayed

---

## Epic 2: Sales Portal - Client & Request Management

**Goal:** Enable Sales Representatives to efficiently submit client requirements and SOPs for new course generation requests.

**Related Portals:** Sales Portal, Data Ingestion Service

### User Stories

#### User Story 2.1: Submit New Course Request - Basic Client Info
**As a** Sales Representative  
**I want to** submit basic client information for a new course request  
**So that** the request can be initiated and tracked from the start

**Acceptance Criteria:**
- The system allows me to enter Client Name, Company Name, Industry, Primary Contact Name, Email, and Phone Number
- Client Name, Company Name, Primary Contact Name, and Email are marked as required fields
- The system validates the email format
- Upon successful submission of this step, the system generates a unique Request ID
- I can save the request as a draft at this stage

#### User Story 2.2: Specify Training Needs
**As a** Sales Representative  
**I want to** define the specific training needs and objectives for a new course  
**So that** the AI has clear instructions for content generation

**Acceptance Criteria:**
- The system allows me to specify Course Title, Target CEFR Level (initial and desired), Number of Participants, Training Objectives (free text), and Specific Pain Points/Challenges (free text)
- Target CEFR Level is a dropdown with options A1-C2
- Training Objectives and Specific Pain Points/Challenges fields support multi-line text input
- I can navigate back to edit client info from this step
- I can save the request as a draft at this stage

#### User Story 2.3: Upload Supporting SOP Documents
**As a** Sales Representative  
**I want to** upload relevant SOP documents for a course request  
**So that** the AI can generate highly contextual and industry-specific content

**Acceptance Criteria:**
- The system provides a clear interface for uploading files (e.g., drag-and-drop or browse)
- The system accepts common document formats (.pdf, .docx, .xlsx, .txt)
- The system displays the file name and upload progress
- I can remove an uploaded file before finalizing the request
- Uploaded SOPs are securely stored in the designated S3 bucket
- I can save the request as a draft at this stage

#### User Story 2.4: Review and Finalize Course Request
**As a** Sales Representative  
**I want to** review all submitted details before finalizing a course request  
**So that** I can ensure accuracy and completeness

**Acceptance Criteria:**
- The system displays a summary of all information entered across previous steps in a read-only format
- I can easily navigate back to individual sections for editing
- A confirmation checkbox is present, indicating agreement to submit the request
- Upon clicking "Submit," the request status changes to "Submitted" and the Course Manager is notified
- The system provides a confirmation message with the Request ID

---

## Epic 3: AI-Powered Course Generation & Content Ingestion

**Goal:** Develop the core AI engine and associated services to process SOPs, generate CEFR-aligned course content, and structure it for effective learning.

**Related Services:** Data Ingestion Service, Content Generation Engine (CGE), Vector Database, LLM Integrations

### User Stories

#### User Story 3.1: Ingest & Pre-process SOP Documents
**As the** system  
**I want to** automatically ingest and pre-process uploaded SOP documents  
**So that** their content can be prepared for AI analysis and contextualization

**Acceptance Criteria:**
- Upon a Sales Representative submitting a request with SOPs, the system initiates an automated ingestion process
- The system can extract text content from accepted document formats using OCR/parsing
- The system performs basic text cleaning (removing extraneous characters, standardizing encoding)
- Pre-processed text is stored securely in intermediate storage
- The system indicates the status of SOP processing
- Error handling is in place for corrupted or unreadable files

#### User Story 3.2: Generate Vector Embeddings for SOPs
**As the** Content Generation Engine  
**I want to** generate vector embeddings from the pre-processed SOP text  
**So that** the content can be efficiently retrieved for RAG-powered course generation

**Acceptance Criteria:**
- For each pre-processed SOP document, the system breaks the text into manageable chunks
- Each chunk is converted into a numerical vector embedding using a pre-trained embedding model
- Vector embeddings, along with their corresponding text chunks and metadata, are stored in the Vector Database
- The system maintains an index for efficient similarity search

#### User Story 3.3: AI-Generate CEFR-Aligned Lesson Content
**As the** Content Generation Engine  
**I want to** use LLMs and RAG to generate CEFR-aligned English lesson content based on client needs and SOP context  
**So that** customized and pedagogically sound course material is created

**Acceptance Criteria:**
- The system initiates content generation upon approval of a course request
- The Content Generation Engine queries the Vector Database to retrieve relevant SOP chunks
- LLMs are prompted to generate diverse lesson content types referencing the retrieved SOP content
- Generated content adheres to the specified target CEFR level in terms of vocabulary, grammar complexity, and sentence structure
- The system generates multiple variations or sufficient content to meet the requested course length
- The system stores the generated content with metadata in MongoDB

#### User Story 3.4: Structure Generated Content into Course Modules
**As the** Content Generation Engine  
**I want to** logically structure the AI-generated content into modules and lessons  
**So that** it forms a coherent and navigable course for students and trainers

**Acceptance Criteria:**
- The system groups related content segments into logical lessons
- Lessons are further grouped into modules, respecting a natural learning progression
- Each lesson and module is assigned a unique ID and descriptive title
- The structured course content is stored in MongoDB, linked to the original Course Request ID
- The system provides a clear content hierarchy (Course → Module → Lesson → Content Segment Type)

---

## Epic 4: Course Management & Content Curation

**Goal:** Provide Course Managers with robust tools to review, edit, approve, and manage the library of generated course content.

**Related Portals:** Course Manager Portal

### User Stories

#### User Story 4.1: Review AI-Generated Course Draft
**As a** Course Manager  
**I want to** review the initial draft of an AI-generated course, module by module and lesson by lesson  
**So that** I can assess its quality, alignment with objectives, and pedagogical soundness

**Acceptance Criteria:**
- I can access a list of course drafts awaiting my review in the Course Manager Portal dashboard
- Clicking a course opens a dedicated review interface displaying the course structure hierarchically
- I can navigate through individual lessons within the course, viewing all content types
- The system highlights any flagged areas or confidence scores from the AI generation process
- I can save my review progress for a draft and return to it later

#### User Story 4.2: Provide Inline Feedback and Request AI Revisions
**As a** Course Manager  
**I want to** provide specific inline feedback on AI-generated content and request targeted AI revisions  
**So that** I can refine the course content efficiently without manual re-writing

**Acceptance Criteria:**
- Within the lesson review interface, I can select specific text segments to add comments
- I can mark a segment with a "Request AI Revision" flag and provide detailed instructions
- The system records my feedback and associates it with the specific content segment and course version
- My feedback is stored and visible for subsequent review cycles

#### User Story 4.3: Approve or Reject a Course Draft
**As a** Course Manager  
**I want to** formally approve a course draft or send it back for major revisions/rejection  
**So that** the course's status is clearly communicated and tracked

**Acceptance Criteria:**
- After reviewing a course, I have clear options to "Approve Course" or "Request Major Revision/Reject"
- If "Approve Course" is selected, the course status changes to "Approved," making it available for assignment
- If "Request Major Revision/Reject" is selected, I am prompted to provide overall feedback and justification
- The system prevents approval if critical feedback points or pending revisions remain

#### User Story 4.4: Manage Approved Content Library
**As a** Course Manager  
**I want to** search, view, and organize approved course modules and lessons within a central content library  
**So that** I can easily find and reuse content for future course assignments or custom curricula

**Acceptance Criteria:**
- I can access a "Content Library" section in the portal
- The library displays approved content with clear titles and metadata (CEFR level, topic, source course)
- I can search content by keywords and filter by CEFR level, content type, and topic
- I can view the full content of any approved lesson or module from the library

---

## Epic 5: Student Learning Experience

**Goal:** Create an engaging, intuitive, and effective online learning environment for students to access courses, complete lessons, receive adaptive feedback, and track their progress.

**Related Portals:** Student Portal

### User Stories

#### User Story 5.1: Access Assigned Courses and Resume Learning
**As a** student  
**I want to** easily see my assigned courses and resume my learning from where I left off  
**So that** I can quickly continue my educational progress

**Acceptance Criteria:**
- Upon logging in, my dashboard prominently displays my currently assigned course(s)
- Each course card shows the course title, my current progress percentage, and the next lesson to complete
- A clear "Resume Course" or "Start Lesson" button takes me directly to the relevant part of the course
- I can view a list of all courses I'm enrolled in, even if not active

#### User Story 5.2: Engage with Interactive Lesson Content
**As a** student  
**I want to** interact with various types of lesson content (dialogues, readings, grammar explanations, vocabulary)  
**So that** I can effectively learn new English concepts and skills

**Acceptance Criteria:**
- The lesson player displays different content segments clearly (text, audio, images)
- For dialogues, I can play audio for individual lines or the entire dialogue
- For vocabulary, I can see new words with definitions and example sentences
- For grammar, explanations are clear and accompanied by illustrative examples
- I can navigate between sections within a lesson easily

#### User Story 5.3: Complete Interactive Exercises & Receive Instant Feedback
**As a** student  
**I want to** complete interactive exercises and receive instant, AI-powered adaptive feedback on my answers  
**So that** I can immediately understand my mistakes and reinforce my learning

**Acceptance Criteria:**
- The system presents various exercise formats clearly
- After submitting an answer, I receive immediate feedback (correct/incorrect)
- For incorrect answers, the system provides a concise explanation of the error
- I can optionally view more detailed explanations within the feedback
- I can attempt the exercise again or move to the next section
- The system tracks my score for each exercise

#### User Story 5.4: Practice Speaking & Writing with AI Feedback
**As a** student  
**I want to** practice my speaking and writing skills within lessons and receive AI-generated feedback  
**So that** I can improve my productive English skills

**Acceptance Criteria:**
- For speaking exercises, I can record my voice and play it back
- The system provides AI feedback on pronunciation and fluency
- For writing exercises, I can type my response
- The system provides AI feedback on grammar, spelling, and sentence structure for written responses
- The feedback system offers adaptive guidance based on my performance

#### User Story 5.5: View My Learning Progress
**As a** student  
**I want to** view my overall learning progress and performance metrics  
**So that** I can track my achievements, identify areas for improvement, and stay motivated

**Acceptance Criteria:**
- I can access a "My Progress" section from the main navigation
- This section displays my overall course completion progress
- It shows my performance breakdown by skill (Listening, Speaking, Reading, Writing) or by content type
- I can see a history of completed lessons and exercise scores

---

## Epic 6: Trainer Portal - Lesson Delivery & Student Support

**Goal:** Equip trainers with the necessary tools to efficiently deliver lessons, monitor student progress, and provide targeted, human-centric feedback.

**Related Portals:** Trainer Portal

### User Stories

#### User Story 6.1: Access & Prepare Assigned Course Lessons
**As a** Trainer  
**I want to** access and review the specific lessons assigned to my students  
**So that** I can prepare for classes and understand the AI-generated content

**Acceptance Criteria:**
- My dashboard displays a list of courses and students assigned to me
- I can click on an assigned course to view its modules and lessons
- I can view the full content of any lesson, including all materials and solutions
- The system allows me to "mark as reviewed" for my preparation
- I can add personal teaching notes to a lesson, visible only to me

#### User Story 6.2: Monitor Individual Student Progress
**As a** Trainer  
**I want to** view the overall progress and performance details of each student assigned to me  
**So that** I can understand their strengths, weaknesses, and areas needing support

**Acceptance Criteria:**
- I can access a list of my assigned students from the dashboard
- Clicking a student's name opens their individual profile with course progress overview
- The student's profile displays performance metrics (average exercise scores, assessment scores)
- I can see a log of the student's completed lessons and exercises

#### User Story 6.3: Provide Qualitative Feedback on Student Performance
**As a** Trainer  
**I want to** provide qualitative, personalized feedback on a student's speaking or writing submissions  
**So that** I can guide their learning beyond automated AI feedback

**Acceptance Criteria:**
- From a student's profile or exercise submission, I can access a feedback interface
- I can input free-form text comments
- For speaking submissions, I can listen to the student's recorded audio and provide feedback
- For writing submissions, I can view their written text and provide comments
- I can optionally assign qualitative ratings for specific skills
- My feedback is saved and visible to the student in their portal

---

## Epic 7: Reporting & Analytics

**Goal:** Provide relevant stakeholders with actionable data and dashboards related to platform usage, student progress, course performance, and sales metrics.

**Related Portals:** Admin Portal (primary), Sales Portal, Course Manager Portal, Trainer Portal

### User Stories

#### User Story 7.1: View Overall Platform Health Dashboard (Admin)
**As an** Administrator  
**I want to** view a dashboard summarizing key platform health metrics  
**So that** I can monitor the overall operational status and identify potential issues

**Acceptance Criteria:**
- The dashboard displays metrics such as total registered users, active users, number of courses generated, lessons completed, and system uptime
- Metrics are presented visually (charts, graphs) for quick understanding
- Data can be filtered by time range (last 24 hours, 7 days, 30 days)
- The dashboard is accessible only to users with administrative privileges

#### User Story 7.2: Track Sales Request Funnel (Sales)
**As a** Sales Representative  
**I want to** view a report on the status of my submitted course requests  
**So that** I can track their progress through the generation and approval pipeline

**Acceptance Criteria:**
- A dedicated section in the Sales Portal displays a funnel view of my requests by status
- I can see the number of requests in each status
- I can click on a status to view a list of associated requests
- Data can be filtered by client, date submitted, or specific request ID

#### User Story 7.3: Monitor Course Performance & Usage (Course Manager)
**As a** Course Manager  
**I want to** view reports on the performance and usage of approved courses  
**So that** I can assess their effectiveness and identify areas for content improvement

**Acceptance Criteria:**
- I can access a "Course Performance" report showing metrics like total student enrollments per course, average completion rate, and average scores
- The report allows me to filter by course, CEFR level, or student cohort
- The system can highlight lessons or exercises where students consistently struggle

#### User Story 7.4: Review Student Progress & Engagement Metrics (Trainer)
**As a** Trainer  
**I want to** view consolidated reports on the progress and engagement of my assigned students  
**So that** I can prepare for sessions and provide targeted support

**Acceptance Criteria:**
- A dashboard in the Trainer Portal displays key student metrics: overall progress, average exercise scores, and recent activity timestamps
- I can view a summary for all my students or drill down into individual student reports
- The report highlights students who are falling behind or show low engagement

---

**Document Version:** 1.0  
**Last Updated:** December 2024  
**Owner:** Product Team  
**Stakeholders:** Engineering, QA, UX/UI Design