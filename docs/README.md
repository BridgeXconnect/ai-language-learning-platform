# Dynamic English Course Creator App

An AI-powered platform for creating customized English language courses based on client SOPs and CEFR standards.

## Repository Structure

```
dynamic-english-course-creator/
├── README.md
├── .gitignore
├── docker-compose.yml
├── docs/
│   ├── architecture/
│   │   ├── app-architecture.md
│   │   ├── frontend-architecture.md
│   │   └── database-schema.md
│   ├── product/
│   │   ├── PRD.md
│   │   ├── epics-and-user-stories.md
│   │   └── sprint-planning/
│   │       └── sprint-1.md
│   └── api/
│       └── api-documentation.md
├── client/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── context/
│   │   └── App.jsx
│   └── public/
├── server/
│   ├── pyproject.toml
│   ├── .env.example
│   ├── run.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   └── services/
│   └── tests/
└── deployment/
    ├── kubernetes/
    ├── terraform/
    └── docker/
```

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL 14+
- Poetry (for Python dependency management)

### Backend Setup

1. Navigate to server directory:
```bash
cd server
```

2. Install dependencies:
```bash
poetry install
poetry shell
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials and secret key
```

4. Run the Flask application:
```bash
python run.py
```

### Frontend Setup

1. Navigate to client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

## Architecture Overview

This application follows a microservices architecture with:

- **Frontend**: React.js with TypeScript and Tailwind CSS
- **Backend**: Flask with SQLAlchemy and JWT authentication
- **Database**: PostgreSQL with vector database for RAG
- **AI/ML**: Integration with OpenAI/Anthropic APIs for content generation
- **Deployment**: AWS EKS with containerized services

## Key Features

- **Sales Portal**: Client request submission and SOP uploads
- **Course Generation Engine**: AI-powered curriculum and content creation
- **Course Manager Dashboard**: Review, approval, and content management
- **Trainer Portal**: Lesson delivery and student feedback
- **Student Portal**: Interactive learning and progress tracking

## Development Workflow

1. **Sprint Planning**: 2-week sprints with clear goals and deliverables
2. **Code Review**: All changes require peer review
3. **Testing**: Comprehensive unit and integration tests
4. **CI/CD**: Automated deployment pipeline

## Contributing

Please read our contribution guidelines and ensure all tests pass before submitting PRs.

## License

[License details to be added]