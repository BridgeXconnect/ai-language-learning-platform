# Dynamic English Course Creator App

An AI-powered platform that generates customized English language courses for corporate clients by analyzing their Standard Operating Procedures (SOPs) and creating CEFR-aligned content.

## 🚀 Features

- **AI-Powered Course Generation**: Automatically creates custom English courses using advanced LLMs
- **SOP Integration**: Analyzes client SOPs to generate industry-specific content
- **CEFR Alignment**: Ensures content matches appropriate proficiency levels (A1-C2)
- **Multi-Portal Architecture**: Separate interfaces for Sales, Course Managers, Trainers, and Students
- **Real-time Progress Tracking**: Monitor student engagement and learning outcomes

## 🏗️ Architecture

- **Frontend**: React.js with TypeScript and Tailwind CSS
- **Backend**: Microservices using Python (FastAPI/Flask) and Node.js
- **Database**: PostgreSQL, MongoDB, Vector Database (Milvus/Pinecone)
- **AI/ML**: OpenAI GPT-4, Anthropic Claude, RAG implementation
- **Infrastructure**: AWS (EKS, S3, RDS, CloudFront)

## 📁 Project Structure

```
ai-lang-app/
├── client/                 # React frontend application
├── server/                 # Flask backend application
├── docs/                   # Project documentation
├── infrastructure/         # AWS infrastructure as code
└── scripts/               # Deployment and utility scripts
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL 14+
- Poetry (Python dependency management)

### Backend Setup
```bash
cd server
poetry install
poetry shell
cp .env.example .env  # Configure your environment variables
python run.py
```

### Frontend Setup
```bash
cd client
npm install
npm run dev
```

## 🧪 Testing

```bash
# Backend tests
cd server
poetry run pytest

# Frontend tests
cd client
npm run test
```

## 🚀 Deployment

This application is designed to be deployed on AWS using Kubernetes (EKS). See the `infrastructure/` directory for deployment configurations.

## 📚 Documentation

- [Architecture Document](docs/architecture.md)
- [API Documentation](docs/api.md)
- [User Stories](docs/user-stories.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, email support@wallstreetenglish.com or create an issue in this repository.
