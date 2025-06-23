#!/bin/bash

# AI Language Learning Platform - Development Startup Script
echo "🚀 Starting AI Language Learning Platform..."

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start backend server
echo "🔧 Starting backend server on port 8000..."
cd server && python3 run.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend client
echo "🎨 Starting frontend client on port 3000..."
cd ../client && npm run dev &
FRONTEND_PID=$!

echo "✅ Application started successfully!"
echo "📖 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait 