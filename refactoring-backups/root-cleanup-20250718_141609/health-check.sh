#!/bin/bash

echo "🏥 Health Check for AI Language Learning Platform"
echo "================================================"

# Check backend
if lsof -i:8000 > /dev/null 2>&1; then
    echo "✅ Backend (port 8000): RUNNING"
else
    echo "❌ Backend (port 8000): NOT RUNNING"
fi

# Check frontend
if lsof -i:3000 > /dev/null 2>&1; then
    echo "✅ Frontend (port 3000): RUNNING"
else
    echo "❌ Frontend (port 3000): NOT RUNNING"
fi

# Check virtual environment
if [ -d "server/venv" ]; then
    echo "✅ Python virtual environment: EXISTS"
else
    echo "❌ Python virtual environment: MISSING"
fi

# Check node_modules
if [ -d "client/node_modules" ]; then
    echo "✅ Node.js dependencies: INSTALLED"
else
    echo "❌ Node.js dependencies: MISSING"
fi

echo "================================================" 