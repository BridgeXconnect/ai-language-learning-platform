# Epic 1: Sales Portal Development

## Epic Overview
Develop a comprehensive Sales Portal that enables sales representatives to efficiently submit client training requests, upload SOPs, and track request status throughout the course creation process.

## Business Value
- Streamlines client onboarding process
- Reduces manual data entry and errors
- Provides transparency into request status
- Enables efficient SOP collection and management

## User Stories

### Story 1.1: Client Information Capture
**As a** sales representative  
**I want to** input comprehensive client information including company details, industry, and contact information  
**So that** the course generation system has all necessary context for customization  

**Acceptance Criteria:**
- [ ] Form includes fields for company name, industry, size, primary contact
- [ ] Input validation ensures required fields are completed
- [ ] Data is stored securely and associated with the request

### Story 1.2: Training Needs Assessment
**As a** sales representative  
**I want to** specify training cohort profiles and objectives  
**So that** the AI can generate appropriately targeted course content  

**Acceptance Criteria:**
- [ ] Capture participant count and CEFR levels (current/target)
- [ ] Record specific training objectives and pain points
- [ ] Allow specification of roles/departments involved

### Story 1.3: SOP Document Upload
**As a** sales representative  
**I want to** securely upload client SOPs and related documents  
**So that** the course content can be customized with client-specific procedures  

**Acceptance Criteria:**
- [ ] Support multiple file formats (PDF, DOCX, TXT)
- [ ] Implement secure file storage and access controls
- [ ] Provide upload progress and confirmation feedback

### Story 1.4: Request Submission and Tracking
**As a** sales representative  
**I want to** submit completed requests and track their status  
**So that** I can provide updates to clients and manage my pipeline  

**Acceptance Criteria:**
- [ ] Submit button finalizes and sends request to Course Manager
- [ ] Email confirmation sent to relevant stakeholders
- [ ] Dashboard view shows all submitted requests with status indicators

## Technical Requirements
- Secure file upload and storage system
- Form validation and data sanitization
- Integration with notification system
- Database design for request tracking

## Definition of Done
- [ ] All user stories completed and tested
- [ ] Security requirements met for SOP handling
- [ ] Integration with Course Manager workflow established
- [ ] User acceptance testing passed
- [ ] Documentation updated