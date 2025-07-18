# Contributing Guide

Welcome! This monorepo uses a modular, feature-based structure for scalability and maintainability. Please follow these guidelines:

## Structure
- Apps live in `/apps` (client, server, agents)
- Shared code lives in `/packages` (types, utils, agent infra, UI)
- Docs in `/docs`, tests in `/tests`, scripts in `/scripts`

## Code Style
- Use strict TypeScript (no `as any`)
- Colocate unit tests and feature docs
- Use feature/domain folders, not just technical layering

## Review Process
- All PRs must pass lint, type-check, and tests
- Add/refresh README.md in new folders
- Reference architecture docs in code when relevant

## Onboarding
- See `/docs/onboarding.md` for setup instructions
- Ask for help in the team chat if stuck 