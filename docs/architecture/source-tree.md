# Source Tree Structure

## Project Overview

The AI Language Learning Platform follows a monorepo structure with clear separation between client-side and server-side applications, along with comprehensive documentation and deployment configurations.

## Root Directory Structure

```
AI Language Learning Platform/
├── .bmad-core/                 # BMAD method v4 framework
│   ├── agents/                 # AI agent definitions
│   ├── agent-teams/           # Team configurations
│   ├── workflows/             # Development workflows
│   ├── tasks/                 # Reusable tasks
│   ├── templates/             # Document templates
│   ├── checklists/            # Quality assurance checklists
│   └── data/                  # Knowledge base and preferences
├── client/                    # Frontend applications
├── server/                    # Backend services
├── docs/                      # Project documentation
├── deployment/                # Deployment configurations
├── docker-compose.yml         # Local development setup
├── docker-compose.prod.yml    # Production setup
└── start-dev.sh              # Development startup script
```

## Client Directory Structure

```
client/
├── Frontend/
│   └── next-theme-setup (1)/  # Next.js application with theming
│       ├── app/               # Next.js App Router structure
│       │   ├── (auth)/        # Authentication routes
│       │   ├── (dashboard)/   # Dashboard routes
│       │   └── api/           # API routes
│       ├── components/        # React components
│       │   ├── auth/          # Authentication components
│       │   ├── dashboard/     # Dashboard components
│       │   ├── shared/        # Shared components
│       │   ├── theme-*        # Theme-related components
│       │   └── ui/            # UI library components
│       ├── contexts/          # React contexts
│       ├── hooks/             # Custom React hooks
│       ├── lib/               # Utility libraries
│       ├── public/            # Static assets
│       └── styles/            # Global styles
├── src/                       # Legacy React application
│   ├── components/            # React components by feature
│   │   ├── ai/                # AI-related components
│   │   ├── common/            # Common/shared components
│   │   ├── course-manager/    # Course management components
│   │   ├── sales/             # Sales portal components
│   │   ├── student/           # Student portal components
│   │   └── trainer/           # Trainer portal components
│   ├── context/               # React contexts
│   ├── pages/                 # Page components
│   │   ├── auth/              # Authentication pages
│   │   ├── course-manager/    # Course manager pages
│   │   ├── sales/             # Sales portal pages
│   │   ├── student/           # Student portal pages
│   │   └── trainer/           # Trainer portal pages
│   ├── services/              # API and external services
│   └── styles/                # CSS and styling
├── public/                    # Static assets
├── package.json               # Dependencies and scripts
├── vite.config.js            # Vite configuration
└── tailwind.config.js        # Tailwind CSS configuration
```

## Server Directory Structure

```
server/
├── app/                       # Main application code
│   ├── __init__.py           # App initialization
│   ├── main.py               # FastAPI application entry point
│   ├── config.py             # Configuration management
│   ├── database.py           # Database connection and setup
│   ├── middleware/           # Custom middleware
│   │   └── auth_middleware.py
│   ├── models/               # Database models
│   │   ├── course.py         # Course-related models
│   │   ├── sales.py          # Sales-related models
│   │   ├── user.py           # User models
│   │   └── *_models_*.py     # Additional model files
│   ├── routes/               # API route handlers
│   │   ├── ai_routes.py      # AI/ML endpoints
│   │   ├── auth_routes.py    # Authentication endpoints
│   │   ├── course_routes.py  # Course management endpoints
│   │   ├── sales_routes.py   # Sales portal endpoints
│   │   └── server_routes_*.py # Additional route files
│   ├── schemas/              # Pydantic schemas for validation
│   │   ├── ai.py            # AI-related schemas
│   │   ├── auth.py          # Authentication schemas
│   │   ├── course.py        # Course schemas
│   │   └── sales.py         # Sales schemas
│   ├── services/             # Business logic services
│   │   ├── ai_service.py     # AI/ML service layer
│   │   ├── auth_service.py   # Authentication service
│   │   ├── course_service.py # Course management service
│   │   ├── sales_service.py  # Sales service
│   │   └── *_service.py      # Additional services
│   └── utils/                # Utility functions
├── tests/                    # Test files
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Python project configuration
├── run.py                   # Development server runner
└── Dockerfile.prod          # Production Docker configuration
```

## Documentation Structure

```
docs/
├── README.md                 # Project overview and setup
├── product/                  # Product documentation
│   ├── PRD.md               # Original monolithic PRD
│   └── epics-and-user-stories.md
├── architecture/             # Architecture documentation (sharded)
│   ├── overview.md           # High-level architecture overview
│   ├── tech-stack.md         # Technology stack decisions
│   ├── system-components.md  # Major system components
│   ├── data-models.md        # Data model definitions
│   ├── security-architecture.md # Security design
│   ├── scalability-resilience.md # Scalability considerations
│   ├── monitoring-logging.md # Monitoring strategy
│   ├── deployment-strategy.md # Deployment approach
│   ├── coding-standards.md   # Development standards
│   ├── source-tree.md        # This document
│   ├── future-considerations.md # Future roadmap
│   └── components/           # Legacy component docs
├── prd/                      # Sharded PRD (BMAD v4)
│   ├── introduction.md       # Project introduction
│   ├── problem-statement.md  # Problem definition
│   ├── goals-and-objectives.md # Goals and success metrics
│   ├── target-audience.md    # User personas
│   ├── core-features.md      # Feature specifications
│   ├── non-functional-requirements.md # NFRs
│   ├── scope-and-constraints.md # Scope and limitations
│   ├── success-metrics.md    # Success measurements
│   ├── future-roadmap.md     # Future enhancements
│   ├── risk-assessment.md    # Risk analysis
│   ├── epic-1-sales-portal.md # Sales portal epic
│   ├── epic-2-course-generation-engine.md # CGE epic
│   ├── epic-3-course-manager-dashboard.md # Course manager epic
│   ├── epic-4-trainer-portal.md # Trainer portal epic
│   └── epic-5-student-portal.md # Student portal epic
└── stories/                  # User stories (to be created)
```

## Deployment Structure

```
deployment/
├── ci-cd-config.txt         # CI/CD configuration notes
├── docker/                  # Docker configurations
├── kubernetes/              # Kubernetes manifests
├── terraform/               # Infrastructure as code
└── final_repo_structure.py # Repository analysis script
```

## Key File Purposes

### Configuration Files
- **docker-compose.yml**: Local development environment setup
- **docker-compose.prod.yml**: Production deployment configuration
- **.env.example**: Environment variable template
- **package.json**: Frontend dependencies and build scripts
- **requirements.txt**: Python backend dependencies
- **pyproject.toml**: Python project metadata and tool configuration

### Entry Points
- **client/src/main.jsx**: Frontend application entry point
- **server/app/main.py**: Backend API server entry point
- **server/run.py**: Development server runner
- **start-dev.sh**: Development environment startup script

### BMAD Framework Integration
- **.bmad-core/core-config.yml**: BMAD method v4 configuration
- **.bmad-core/agents/**: AI agent definitions for development workflow
- **.bmad-core/data/bmad-kb.md**: BMAD knowledge base

## Development Workflow Directories

### Frontend Development
- **client/src/components/**: Organized by feature/domain
- **client/src/pages/**: Route-based page components
- **client/src/services/**: API integration and external services

### Backend Development
- **server/app/routes/**: API endpoint definitions
- **server/app/services/**: Business logic implementation
- **server/app/models/**: Database schema definitions
- **server/app/schemas/**: Request/response validation

### Testing
- **client/src/**/__tests__/**: Frontend component tests
- **server/tests/**: Backend service and integration tests
- **server/test_*.py**: Specific test files for various components

## Build and Deployment Artifacts

### Frontend Build
- **client/dist/**: Built frontend assets
- **client/node_modules/**: Node.js dependencies

### Backend Runtime
- **server/app/**: Production Python application code
- **Dockerfile.prod**: Production container configuration

This structure supports both monolithic development for rapid prototyping and microservices architecture for production deployment, with clear separation of concerns and comprehensive documentation following BMAD method v4 principles.