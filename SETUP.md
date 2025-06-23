# AI Language Learning Platform - Setup Guide

## Prerequisites

### 1. Install PostgreSQL
**macOS (using Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows:**
Download and install from: https://www.postgresql.org/download/windows/

### 2. Install Redis (Optional but recommended)
**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### 3. Create Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE ai_language_platform;
CREATE USER app_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_language_platform TO app_user;
\q
```

## Installation Steps

### 1. Clone and Navigate
```bash
cd "AI Language Learning Platform/server"
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file in the server directory:
```env
# Application Configuration
APP_NAME="Dynamic English Course Creator"
APP_VERSION="1.0.0"
DEBUG=True

# Database Configuration (UPDATE THESE VALUES)
DATABASE_URL="postgresql://app_user:your_password@localhost:5432/ai_language_platform"

# JWT Configuration
JWT_SECRET_KEY="your-super-secret-jwt-key-change-this-in-production"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis Configuration
REDIS_URL="redis://localhost:6379/0"

# Security Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# AI/LLM Configuration (Optional for now)
OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""
```

### 5. Initialize Database
```bash
python quick_start.py
```

### 6. Start the Server
```bash
python run.py
```

## Verification

1. **Health Check**: Visit http://localhost:8000/health
2. **API Documentation**: Visit http://localhost:8000/docs
3. **Test Login**: 
   - Username: `admin`
   - Password: `admin123`

## Default User Accounts

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| demo_sales | demo123 | Sales User |
| demo_trainer | demo123 | Trainer |
| demo_manager | demo123 | Course Manager |
| demo_student | demo123 | Student |

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Refresh token

### Sales Portal
- `GET /api/sales/course-requests` - List course requests
- `POST /api/sales/course-requests` - Create course request
- `POST /api/sales/course-requests/{id}/sop` - Upload SOP document

### Course Management
- `GET /api/courses` - List courses
- `POST /api/courses` - Create course
- `GET /api/courses/{id}` - Get course details

## Troubleshooting

### Database Connection Issues
1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify database exists: `psql -U postgres -l`
3. Test connection: `psql -U app_user -d ai_language_platform`

### Import Errors
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (should be 3.10+)

### Port Already in Use
If port 8000 is busy, modify `run.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Change port
```

## Frontend Setup (Optional)

```bash
cd ../client
npm install
npm run dev
```

The frontend will be available at http://localhost:5173

## Next Steps

1. **Configure AI APIs**: Add OpenAI/Anthropic API keys to `.env`
2. **Customize Settings**: Update application settings in `app/config.py`
3. **Add Sample Data**: Use the admin interface to create sample courses
4. **Deploy**: Use Docker or cloud platforms for production deployment

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review application logs
3. Verify database connectivity
4. Ensure all dependencies are installed