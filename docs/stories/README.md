# User Stories Directory

This directory contains user stories generated from the PRD epics following the BMAD method v4 workflow.

## Story Status Workflow

Stories progress through the following statuses:
- **Draft** → **Approved** → **InProgress** → **Done**

## File Naming Convention

Stories are named following the pattern: `story-{epic}.{story}-{title}.md`

Examples:
- `story-1.1-client-information-capture.md`
- `story-2.1-ai-powered-curriculum-design.md`
- `story-3.1-dashboard-overview-kpis.md`

## Story Template

Each story file should follow this structure:

```markdown
# Story {Epic}.{Number}: {Title}

**Status:** Draft | Approved | InProgress | Done

## User Story
**As a** {user type}  
**I want** {functionality}  
**So that** {business value}

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Notes
{Any technical implementation details}

## Definition of Done
- [ ] Feature implemented and tested
- [ ] Code review completed
- [ ] Documentation updated
- [ ] User acceptance testing passed

## Notes
{Any additional notes or comments}
```

## Development Workflow

1. **Story Creation**: SM agent generates stories from epics
2. **Story Review**: Review and update status to "Approved"
3. **Development**: Dev agent implements story, status becomes "InProgress"
4. **Completion**: Mark as "Done" when all acceptance criteria met

Only work on one story at a time in sequential order within each epic.