#!/bin/bash

# AI Language Learning Platform - Improved Startup Script
set -e

echo "🚀 Starting AI Language Learning Platform..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Kill any existing processes
print_status "Cleaning up existing processes..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start backend server
print_status "Starting backend server on port 8000..."
cd server
source venv/bin/activate
python run.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Check if backend is running
if ! lsof -i:8000 > /dev/null 2>&1; then
    print_error "Backend failed to start. Check the logs above."
    exit 1
fi

print_success "Backend started successfully!"

# Start frontend client
print_status "Starting frontend client on port 3000..."
cd ../client
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

# Check if frontend is running
if ! lsof -i:3000 > /dev/null 2>&1; then
    print_error "Frontend failed to start. Check the logs above."
    exit 1
fi

print_success "Frontend started successfully!"

echo ""
echo "✅ Application started successfully!"
echo "📖 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    print_status "Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    print_success "Services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait 