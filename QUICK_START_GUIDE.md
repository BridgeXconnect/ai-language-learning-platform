# 🚀 Quick Start Guide - Get Your Platform Running Today

## 🎯 **BMAD Master: Immediate Action Steps**

**Goal**: Get your AI Language Learning Platform running with real functionality in the next 2 hours

---

## ⚡ **Step 1: Environment Setup (15 minutes)**

### **1.1 Check Current Setup**
```bash
# Navigate to your project
cd "AI Language Learning Platform"

# Check if backend dependencies are installed
cd server && pip list | grep -E "(fastapi|uvicorn|sqlalchemy)"

# Check if frontend dependencies are installed  
cd ../client && npm list --depth=0
```

### **1.2 Install Missing Dependencies**
```bash
# Backend dependencies
cd server && pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart

# Frontend dependencies
cd ../client && npm install
```

---

## ⚡ **Step 2: Database Setup (30 minutes)**

### **Option A: Local PostgreSQL (Recommended for development)**
```bash
# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Create database
createdb ai_language_platform

# Update .env file
echo "DATABASE_URL=postgresql://localhost/ai_language_platform" > server/.env
```

### **Option B: Supabase (Cloud - easier setup)**
1. Go to [supabase.com](https://supabase.com)
2. Create free account
3. Create new project
4. Copy database URL
5. Add to `server/.env`:
```bash
DATABASE_URL=postgresql://your-supabase-url
```

---

## ⚡ **Step 3: AI API Keys (15 minutes)**

### **3.1 Get API Keys**
1. **OpenAI**: Go to [platform.openai.com](https://platform.openai.com) → API Keys
2. **Anthropic**: Go to [console.anthropic.com](https://console.anthropic.com) → API Keys

### **3.2 Add to Environment**
```bash
# Add to server/.env
echo "OPENAI_API_KEY=your-openai-key-here" >> server/.env
echo "ANTHROPIC_API_KEY=your-anthropic-key-here" >> server/.env
```

---

## ⚡ **Step 4: Start the Platform (10 minutes)**

### **4.1 Start Backend**
```bash
# Terminal 1
cd server
python -m uvicorn app.main:app --reload --port 8001
```

### **4.2 Start Frontend**
```bash
# Terminal 2
cd client
npm run dev
```

### **4.3 Verify Everything is Running**
- Backend: http://localhost:8001/docs (FastAPI docs)
- Frontend: http://localhost:3000 (Your platform)

---

## ⚡ **Step 5: Test Basic Functionality (20 minutes)**

### **5.1 Test Backend Health**
```bash
curl http://localhost:8001/health
# Should return: {"status": "healthy"}
```

### **5.2 Test AI Integration**
```bash
# Test AI assessment service
cd server && python -c "
from app.services.ai_assessment_service import AIAssessmentService
import asyncio

async def test():
    service = AIAssessmentService()
    result = await service.create_assessment('Business English', 'intermediate', ['multiple_choice'], 3)
    print('Assessment created:', result)

asyncio.run(test())
"
```

### **5.3 Test Frontend**
1. Open http://localhost:3000
2. Try to register a new user
3. Try to login
4. Navigate to dashboard

---

## 🎯 **What You Should See After 2 Hours**

### **✅ Working Features:**
- [ ] Backend API running on port 8001
- [ ] Frontend running on port 3000
- [ ] Database connected and working
- [ ] User registration/login (if auth is implemented)
- [ ] AI services responding (if APIs are connected)
- [ ] Basic dashboard accessible

### **❌ Still Missing (Next Steps):**
- [ ] Real authentication flow
- [ ] AI service integration
- [ ] Course creation
- [ ] Assessment system
- [ ] User management

---

## 🚨 **Troubleshooting**

### **Backend Issues:**
```bash
# Check if port 8001 is available
lsof -i :8001

# Kill process if needed
kill -9 $(lsof -t -i:8001)

# Check Python environment
python --version
pip list | grep fastapi
```

### **Frontend Issues:**
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### **Database Issues:**
```bash
# Test database connection
psql $DATABASE_URL -c "SELECT version();"

# Check if tables exist
psql $DATABASE_URL -c "\dt"
```

---

## 📋 **Next Steps After Quick Start**

### **Day 1: Authentication**
1. Implement user registration
2. Add login/logout
3. Test auth flow

### **Day 2: AI Integration**
1. Connect OpenAI API
2. Connect Anthropic API
3. Test AI responses

### **Day 3: Core Features**
1. Course creation
2. Assessment system
3. User dashboard

---

## 🎉 **Success Indicators**

**After completing this quick start, you should have:**
- ✅ Platform running locally
- ✅ Database connected
- ✅ API endpoints accessible
- ✅ Frontend interface working
- ✅ Foundation ready for development

**You're now ready to build the actual functionality!**

---

## 🚀 **Ready to Start?**

```bash
# 1. Set up environment
cd "AI Language Learning Platform"

# 2. Start backend
cd server && python -m uvicorn app.main:app --reload --port 8001

# 3. Start frontend (new terminal)
cd client && npm run dev

# 4. Open browser
open http://localhost:3000
```

**Your AI Language Learning Platform is now running! 🎉** 