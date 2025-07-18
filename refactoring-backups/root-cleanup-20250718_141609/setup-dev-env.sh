#!/bin/bash

# Development Environment Setup Script
set -e

echo "🔧 Setting up development environment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "server" ] || [ ! -d "client" ]; then
    echo "❌ Please run this script from the AI Language Learning Platform root directory"
    exit 1
fi

# Setup Python environment
print_status "Setting up Python environment..."
cd server

if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

print_success "Python environment setup complete!"

# Setup Node.js environment
print_status "Setting up Node.js environment..."
cd ../client

if [ ! -d "node_modules" ]; then
    print_status "Installing Node.js dependencies..."
    npm install --legacy-peer-deps
fi

print_success "Node.js environment setup complete!"

cd ..

print_success "Development environment setup complete!"
echo ""
echo "You can now run: ./start-app.sh" 