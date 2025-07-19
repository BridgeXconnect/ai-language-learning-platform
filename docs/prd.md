# Product Requirements Document (PRD): Dynamic English Course Creator App

*This is the master PRD file that links to all sharded components following BMAD method v4 structure.*

## Document Structure

### Core PRD Components
- [Introduction](prd/introduction.md) - Executive summary, purpose, and scope
- [Problem Statement](prd/problem-statement.md) - Current challenges and pain points
- [Goals & Objectives](prd/goals-and-objectives.md) - Primary goals and success metrics
- [Target Audience](prd/target-audience.md) - User personas and needs
- [Core Features](prd/core-features.md) - Detailed feature specifications
- [Non-Functional Requirements](prd/non-functional-requirements.md) - Performance, security, and usability requirements
- [Scope and Constraints](prd/scope-and-constraints.md) - What's in/out of scope and key constraints
- [Success Metrics](prd/success-metrics.md) - Operational, business, and learning effectiveness metrics
- [Future Roadmap](prd/future-roadmap.md) - Phase 2 and 3 enhancements
- [Risk Assessment](prd/risk-assessment.md) - Technical and business risks with mitigation strategies

### Epic Specifications
- [Epic 1: Sales Portal](prd/epic-1-sales-portal.md) - Client request submission and SOP upload
- [Epic 2: Course Generation Engine](prd/epic-2-course-generation-engine.md) - AI-powered content creation
- [Epic 3: Course Manager Dashboard](prd/epic-3-course-manager-dashboard.md) - Review, approval, and management
- [Epic 4: Trainer Portal](prd/epic-4-trainer-portal.md) - Lesson delivery and student management
- [Epic 5: Student Portal](prd/epic-5-student-portal.md) - Interactive learning experience

## Usage Notes

This sharded structure is designed for:
- **BMAD Method v4 Compliance**: Enables efficient agent-driven development
- **Manageable Development**: Each component can be worked on independently
- **Clear Dependencies**: Logical flow from requirements to implementation
- **Story Generation**: SM agents can create detailed user stories from epics

## Development Workflow

1. **Planning Phase**: Review all PRD components for context
2. **Story Creation**: Use epics to generate detailed user stories in `docs/stories/`
3. **Implementation**: Develop features following story-driven approach
4. **Validation**: Ensure implementation meets acceptance criteria

For the complete development workflow, see the [BMAD Knowledge Base](.bmad-core/data/bmad-kb.md).

---

**Document Version:** 1.0  
**Last Updated:** December 2024  
**Structure:** BMAD Method v4 Sharded  
**Owner:** Product Team