# Migration Plan: Senior-Level Monorepo Structure

This document tracks the migration to a scalable, maintainable monorepo structure.

## Steps
- [ ] Create `/packages` and subfolders for shared code
- [ ] Move shared types, utils, and agent logic into packages
- [ ] Update imports in apps/agents to use new packages
- [ ] Colocate unit tests and feature docs
- [ ] Add/refresh README.md in all major folders
- [ ] Update CI/CD to lint, type-check, and test all packages/apps

## Notes
- No code is deleted; all moves are non-destructive
- Reference this file in PRs related to migration
- See `/docs/architecture/` for rationale and diagrams 