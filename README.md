# 🎓 AI Language Learning Platform

> An intelligent, AI-powered platform for creating customized English language courses based on client SOPs and CEFR standards.

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

## 🌟 Overview

The AI Language Learning Platform revolutionizes corporate English training by automatically generating customized curricula from client Standard Operating Procedures (SOPs). Using advanced AI agents and natural language processing, it creates contextually relevant learning materials that align with CEFR standards.

### Key Features

- 🤖 **AI-Powered Course Generation**: Automatic curriculum creation from client SOPs
- 📚 **Multi-Agent Architecture**: Specialized AI agents for different aspects of course creation
- 🎯 **CEFR Alignment**: Content tailored to Common European Framework levels
- 👥 **Multi-Portal System**: Dedicated interfaces for Sales, Trainers, Course Managers, and Students  
- 📊 **Progress Tracking**: Comprehensive analytics and learning progress monitoring
- 🔄 **Quality Assurance**: Automated content review and validation

## 🏗️ Architecture

### System Components

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Sales Portal  │  │ Course Manager  │  │ Trainer Portal  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                    ┌─────────────────┐
                    │   API Gateway   │
                    └─────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Orchestrator   │  │ Course Planner  │  │Content Creator  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                    ┌─────────────────┐
                    │Quality Assurance│
                    └─────────────────┘
```

### Technology Stack

**Frontend**: Next.js, React, TypeScript, Tailwind CSS  
**Backend**: FastAPI, Python, PostgreSQL, Redis  
**AI/ML**: OpenAI GPT, Anthropic Claude, Vector Databases  
**Infrastructure**: Docker, Kubernetes, AWS  
**Message Queue**: Redis, WebSockets  

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.9+
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "AI Language Learning Platform"
```

### 2. One-Time Setup

```bash
# Run the permanent setup script (creates virtual environment and installs dependencies)
./setup-dev-env.sh
```

### 3. Start the Application

```bash
# Start both frontend and backend
./start-app.sh
```

### 4. Stop the Application

```bash
# Stop all services
./stop-app.sh
```

### 5. Check Application Health

```bash
# Verify all services are running
./health-check.sh
```

## 📋 Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `./start-app.sh` | Start full application | Daily development |
| `./stop-app.sh` | Stop all services | When done working |
| `./health-check.sh` | Check application status | Troubleshooting |
| `./setup-dev-env.sh` | Setup development environment | One-time setup |

## 🔧 Troubleshooting

If you encounter any issues:

1. **Check application health:**
   ```bash
   ./health-check.sh
   ```

2. **Re-setup environment:**
   ```bash
   ./setup-dev-env.sh
   ```

3. **View detailed setup guide:**
   ```bash
   cat PERMANENT_SETUP_GUIDE.md
   ```

## 📱 Application Access

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main application interface |
| **Backend API** | http://localhost:8000 | FastAPI backend |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |

## 👤 Default User Accounts

| Username | Password | Role | Portal Access |
|----------|----------|------|---------------|
| `admin` | `admin123` | Administrator | All portals |
| `demo_sales` | `demo123` | Sales User | Sales Portal |
| `demo_trainer` | `demo123` | Trainer | Trainer Portal |
| `demo_manager` | `demo123` | Course Manager | Course Manager Portal |
| `demo_student` | `demo123` | Student | Student Portal |

## 🏢 Portal Overview

### Sales Portal
- Submit new course requests
- Upload client SOPs and documents
- Track request status and progress
- Manage client relationships

### Course Manager Portal  
- Review AI-generated curricula
- Approve/modify course content
- Manage content library
- Oversee quality standards

### Trainer Portal
- Access assigned courses
- Deliver lessons to students
- Provide feedback and assessments
- Track student progress

### Student Portal
- Access personalized learning paths
- Interactive lessons and exercises
- Progress tracking and achievements
- Practice simulations

## 🤖 AI Agent System

### Orchestrator Agent
**Purpose**: Coordinates workflow between all agents  
**Responsibilities**: Task routing, progress monitoring, error handling

### Course Planner Agent  
**Purpose**: Creates learning curricula from SOPs  
**Responsibilities**: Content analysis, curriculum structure, CEFR alignment

### Content Creator Agent
**Purpose**: Generates detailed learning materials  
**Responsibilities**: Lesson creation, exercise generation, multimedia content

### Quality Assurance Agent
**Purpose**: Validates and reviews generated content  
**Responsibilities**: Content accuracy, language quality, standard compliance

## 📁 Project Structure

```
AI Language Learning Platform/
├── 📄 README.md                    # This file
├── 📄 docker-compose.yml           # Development orchestration
├── 📄 docker-compose.prod.yml      # Production orchestration
├── 📄 .env.example                 # Environment template
│
├── 📁 client/                      # Frontend application
│   ├── 📁 src/components/          # React components
│   ├── 📁 src/pages/               # Page components
│   ├── 📁 src/services/            # API integration
│   └── 📄 package.json
│
├── 📁 server/                      # Backend API
│   ├── 📁 app/                     # Application code
│   ├── 📁 app/routes/              # API endpoints
│   ├── 📁 app/services/            # Business logic
│   └── 📄 requirements.txt
│
├── 📁 agents/                      # AI Agent services
│   ├── 📁 orchestrator/            # Master coordinator
│   ├── 📁 course-planner/          # Curriculum planning
│   ├── 📁 content-creator/         # Content generation
│   └── 📁 quality-assurance/       # Content validation
│
├── 📁 docs/                        # Documentation
│   ├── 📁 architecture/            # Technical docs
│   ├── 📁 api/                     # API documentation
│   └── 📁 product/                 # Product requirements
│
└── 📁 scripts/                     # Automation scripts
    ├── 📄 start-agents.sh          # Start all agents
    └── 📄 setup-mcp.sh             # MCP configuration
```

## 🔧 Development

### Running Tests

```bash
# Backend tests
cd server
python -m pytest

# Frontend tests  
cd client
npm test

# Agent tests
cd agents/course-planner
python -m pytest
```

### Code Quality

```bash
# Backend linting
cd server
black . && flake8 .

# Frontend linting
cd client
npm run lint
```

### Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# Core Application
APP_NAME="AI Language Learning Platform"
DATABASE_URL="postgresql://user:pass@localhost:5432/ai_lang_db"
JWT_SECRET_KEY="your-jwt-secret-key"

# AI Service APIs
OPENAI_API_KEY="your-openai-key"
ANTHROPIC_API_KEY="your-anthropic-key"

# Agent Service URLs
ORCHESTRATOR_URL="http://localhost:8100"
COURSE_PLANNER_URL="http://localhost:8101" 
CONTENT_CREATOR_URL="http://localhost:8102"
QUALITY_ASSURANCE_URL="http://localhost:8103"
```

## 📖 Documentation

- **[Architecture Guide](docs/architecture/overview.md)** - System architecture and design decisions
- **[API Documentation](docs/api/)** - REST API reference
- **[Product Requirements](docs/product/PRD.md)** - Product specification and requirements
- **[Setup Guide](SETUP.md)** - Detailed setup instructions
- **[Deployment Guide](docs/deployment/)** - Production deployment instructions

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`) 
5. **Open** a Pull Request

### Development Guidelines

- Follow existing code style and conventions
- Write tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 🚧 Current Status

### ✅ Completed Features
- [x] Multi-portal user authentication
- [x] Sales request submission workflow
- [x] Basic AI agent architecture
- [x] Docker containerization
- [x] Database schema and models

### 🚧 In Progress  
- [ ] AI agent integration and testing
- [ ] Course generation workflow
- [ ] Content review and approval system
- [ ] Student learning interface

### 📋 Planned Features
- [ ] Advanced analytics dashboard
- [ ] Mobile application
- [ ] Multi-language support
- [ ] Third-party LMS integration

## 📞 Support

For technical issues or questions:

1. **Check Documentation**: Review relevant docs in `/docs`
2. **Search Issues**: Look through existing GitHub issues
3. **API Reference**: Check `/docs/api` for API-related questions
4. **Create Issue**: Submit detailed bug reports or feature requests

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for modern language learning** 