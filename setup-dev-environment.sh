#!/bin/bash

echo "🛠️  Setting up AI Language Learning Platform Development Environment"
echo "=================================================================="

# Check prerequisites
echo "Checking prerequisites..."

# Check Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js $(node --version) found"
else
    echo "❌ Node.js not found. Please install Node.js 18+"6
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python $(python3 --version) found"
else
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker $(docker --version) found"
else
    echo "❌ Docker not found. Please install Docker"
    exit 1
fi

# Check PostgreSQL
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL found"
else
    echo "⚠️  PostgreSQL not found. You can use Docker instead."
fi

echo
echo "Setting up backend..."
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

echo
echo "Setting up frontend..."
cd client
npm install
cd ..

echo
echo "🎉 Development environment setup complete!"
echo
echo "Next steps:"
echo "1. Copy .env.example to .env and configure"
echo "2. Start services with: docker-compose up -d"
echo "3. Or run manually:"
echo "   - Backend: cd server && source venv/bin/activate && python run.py"
echo "   - Frontend: cd client && npm run dev"
