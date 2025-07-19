# V0 Integration Task

## Overview
This task integrates V0's AI-powered component generation with the BMAD development workflow, enabling real-time UI component creation and live preview capabilities.

## Task Inputs
- User story file path or story content
- User role (sales, course-manager, trainer, student)
- Component type (page, component, layout)
- Custom prompt modifications (optional)

## Prerequisites
- V0 API credentials configured in environment
- Next.js frontend with V0 integration services
- Active user story with UI requirements

## Execution Steps

### Step 1: Story Analysis
1. Read the user story content
2. Extract UI requirements from acceptance criteria
3. Identify user role and component context
4. Generate V0-optimized prompt from story requirements

### Step 2: Component Generation
1. Call V0 API with generated prompt
2. Include project context (design system, existing components)
3. Specify framework (Next.js) and styling (Tailwind + shadcn/ui)
4. Monitor generation status via WebSocket

### Step 3: Live Preview
1. Create preview session with V0
2. Display component in responsive preview panel
3. Enable real-time updates and hot reload
4. Allow device-specific preview (mobile, tablet, desktop)

### Step 4: Iteration and Refinement
1. Collect feedback on generated component
2. Update prompt based on requirements
3. Regenerate component with improvements
4. Compare versions and select best option

### Step 5: Testing and Validation
1. Validate component against story acceptance criteria
2. Test responsive behavior across devices
3. Verify accessibility compliance
4. Check integration with existing codebase

### Step 6: Deployment
1. Backup existing files if overwriting
2. Deploy component to target location
3. Update imports and dependencies
4. Run automated tests to ensure integration
5. Update story status to reflect completion

## Output Artifacts
- Generated React component with TypeScript
- Live preview URL for stakeholder review
- Component documentation and usage examples
- Updated story file with dev agent records

## Quality Gates
- Component meets all acceptance criteria
- Responsive design works on all target devices
- Accessibility standards (WCAG 2.1 AA) compliance
- Code passes linting and type checking
- Integration tests pass

## Error Handling
- V0 API failures: Fallback to manual component creation
- Generation timeouts: Retry with simplified prompt
- Preview issues: Provide code-only view
- Deployment conflicts: Create backup and resolve manually

## Success Criteria
- Functional component deployed and integrated
- Live preview accessible for stakeholder review
- All acceptance criteria validated
- Story marked as complete with dev agent records updated

## Integration with BMAD Workflow
- SM agent creates story → Dev agent uses V0 integration → Preview shared → Approval → Deployment
- Real-time collaboration between stakeholders via live preview
- Faster iteration cycles with immediate visual feedback
- Reduced development time for UI components

## Best Practices
- Use story content as primary source of requirements
- Leverage project context for consistent design
- Test components in isolation before integration
- Maintain component library organization
- Document V0 generation decisions in story files