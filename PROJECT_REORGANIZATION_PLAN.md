# AI Language Learning Platform - Reorganization Plan

## 🎯 Overview
This document outlines the reorganization plan for the AI Language Learning Platform to improve maintainability, consistency, and developer experience.

## 📁 Proposed Directory Structure

```
ai-language-learning-platform/
├── README.md                           # Main project documentation
├── .env.example                        # Environment template
├── .gitignore                          # Git ignore rules
├── docker-compose.yml                  # Development orchestration
├── docker-compose.prod.yml             # Production orchestration
├── 
├── 📁 apps/                           # Application layer
│   ├── 📁 frontend/                   # Single unified frontend
│   │   ├── README.md
│   │   ├── package.json
│   │   ├── vite.config.js
│   │   ├── tailwind.config.js
│   │   ├── 📁 src/
│   │   │   ├── 📁 components/         # Reusable UI components
│   │   │   ├── 📁 pages/              # Route components
│   │   │   ├── 📁 hooks/              # Custom React hooks
│   │   │   ├── 📁 services/           # API integration
│   │   │   ├── 📁 stores/             # State management
│   │   │   ├── 📁 utils/              # Helper functions
│   │   │   └── App.jsx
│   │   └── 📁 public/
│   │
│   ├── 📁 api-gateway/                # Main backend API
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   ├── 📁 app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── 📁 api/                # API routes
│   │   │   ├── 📁 core/               # Core business logic
│   │   │   ├── 📁 models/             # Database models
│   │   │   ├── 📁 services/           # Business services
│   │   │   └── 📁 utils/              # Helper utilities
│   │   └── 📁 tests/
│   │
│   └── 📁 agents/                     # AI Agent services
│       ├── README.md                  # Agent architecture overview
│       ├── 📁 orchestrator/
│       ├── 📁 course-planner/
│       ├── 📁 content-creator/
│       └── 📁 quality-assurance/
│
├── 📁 packages/                       # Shared packages/libraries
│   ├── 📁 shared-types/               # TypeScript type definitions
│   ├── 📁 shared-utils/               # Common utilities
│   └── 📁 shared-configs/             # Shared configurations
│
├── 📁 infrastructure/                  # Infrastructure as Code
│   ├── 📁 docker/                     # Docker configurations
│   ├── 📁 kubernetes/                 # K8s manifests
│   ├── 📁 terraform/                  # Infrastructure definitions
│   └── 📁 scripts/                    # Deployment scripts
│
├── 📁 docs/                           # Centralized documentation
│   ├── 📁 architecture/               # Technical architecture
│   ├── 📁 api/                        # API documentation
│   ├── 📁 product/                    # Product requirements
│   ├── 📁 development/                # Development guides
│   └── 📁 deployment/                 # Deployment guides
│
└── 📁 tools/                          # Development tools
    ├── 📁 scripts/                    # Build/deployment scripts
    ├── 📁 configs/                    # Shared configurations
    └── 📁 templates/                  # Code templates
```

## 🔄 Migration Steps

### Phase 1: Frontend Consolidation
1. **Decision**: Choose between React (Vite) or Next.js
   - **Recommendation**: Next.js for better SSR, routing, and modern React features
   - **Rationale**: Better for production, built-in optimizations

2. **Actions**:
   - Migrate best components from React app to Next.js
   - Consolidate shared utilities
   - Update build configurations

### Phase 2: Backend Restructuring
1. **Rename**: `server/` → `apps/api-gateway/`
2. **Standardize**: Use consistent naming (kebab-case for directories, snake_case for Python)
3. **Organize**: Group related functionality

### Phase 3: Agent Services Organization
1. **Track**: Add all agent services to git
2. **Standardize**: Consistent structure across all agents
3. **Document**: Add proper README files

### Phase 4: Configuration Consolidation
1. **Centralize**: Move all environment configs to root
2. **Template**: Create comprehensive .env.example
3. **Document**: Clear setup instructions

### Phase 5: Documentation Restructuring
1. **Consolidate**: Single source of truth for docs
2. **Standardize**: Consistent markdown formatting
3. **Navigation**: Clear doc hierarchy

## 🚀 Implementation Priority

### High Priority (Phase 1)
- [ ] Frontend consolidation decision
- [ ] Git tracking for untracked files
- [ ] Basic directory restructure

### Medium Priority (Phase 2)
- [ ] Backend reorganization
- [ ] Agent services standardization
- [ ] Configuration consolidation

### Low Priority (Phase 3)
- [ ] Documentation restructure
- [ ] Tool consolidation
- [ ] Infrastructure organization

## 📋 Naming Conventions

### Directory Names
- **Apps**: `kebab-case` (e.g., `api-gateway`, `content-creator`)
- **Components**: `PascalCase` (e.g., `CourseCard.jsx`)
- **Files**: `kebab-case` for config, `snake_case` for Python
- **Variables**: Language-specific conventions

### Git Branch Names
- `feature/[feature-name]`
- `bugfix/[issue-description]`
- `hotfix/[critical-fix]`
- `release/[version]`

## 🔧 Configuration Standards

### Environment Variables
```bash
# Application
APP_NAME="AI Language Learning Platform"
APP_VERSION="1.0.0"
ENVIRONMENT="development|staging|production"

# Database
DATABASE_URL="postgresql://user:pass@host:port/db"
REDIS_URL="redis://host:port/db"

# AI Services
OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""

# Agent Services
ORCHESTRATOR_URL="http://localhost:8100"
COURSE_PLANNER_URL="http://localhost:8101"
CONTENT_CREATOR_URL="http://localhost:8102"
QUALITY_ASSURANCE_URL="http://localhost:8103"
```

## 📚 Documentation Structure

### Root README.md
- Project overview and quick start
- Architecture summary
- Development setup
- Contribution guidelines

### Service-Specific READMEs
- Service purpose and responsibilities
- API documentation
- Local development setup
- Testing instructions

## 🎯 Success Metrics

### Improved Developer Experience
- ✅ Single command setup
- ✅ Clear project navigation
- ✅ Consistent code organization
- ✅ Comprehensive documentation

### Enhanced Maintainability
- ✅ Logical separation of concerns
- ✅ Consistent naming conventions
- ✅ Clear dependency management
- ✅ Standardized configuration

### Better Collaboration
- ✅ Clear contribution guidelines
- ✅ Standardized development workflow
- ✅ Comprehensive documentation
- ✅ Consistent code quality

## 📝 Next Steps

1. **Review** this plan with the team
2. **Decide** on frontend technology (React vs Next.js)
3. **Create** feature branch for reorganization
4. **Execute** phases incrementally
5. **Test** thoroughly after each phase
6. **Document** changes and update team

---

This reorganization will create a more maintainable, scalable, and developer-friendly codebase that follows modern best practices for full-stack applications. 