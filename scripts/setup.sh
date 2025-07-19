#!/bin/bash

# AI Language Learning Platform Setup Script

set -e

echo "🚀 Setting up AI Language Learning Platform..."

# Check if required tools are installed
check_requirements() {
    echo "📋 Checking requirements..."
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is not installed. Please install Node.js 18+ and try again."
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed. Please install Python 3.10+ and try again."
        exit 1
    fi
    
    if ! command -v poetry &> /dev/null; then
        echo "❌ Poetry is not installed. Installing Poetry..."
        curl -sSL https://install.python-poetry.org | python3 -
        echo "✅ Poetry installed! Please restart your terminal or run 'source ~/.bashrc'"
        exit 1
    fi
    
    echo "✅ Requirements check passed!"
}

# Setup backend
setup_backend() {
    echo "🐍 Setting up backend..."
    
    cd server
    
    # Install dependencies
    poetry install
    
    # Copy environment file
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "📝 Created .env file. Please update it with your configuration."
    fi
    
    cd ..
    echo "✅ Backend setup complete!"
}

# Setup frontend
setup_frontend() {
    echo "⚛️  Setting up frontend..."
    
    cd client
    
    # Install dependencies
    npm install
    
    cd ..
    echo "✅ Frontend setup complete!"
}

# Main setup function
main() {
    echo "🎯 Starting setup process..."
    
    check_requirements
    setup_backend
    setup_frontend
    
    echo ""
    echo "🎉 Setup complete! Next steps:"
    echo ""
    echo "1. Update server/.env with your configuration (database URL, API keys, etc.)"
    echo "2. Start the backend:"
    echo "   cd server && poetry run python run.py"
    echo ""
    echo "3. Start the frontend (in a new terminal):"
    echo "   cd client && npm run dev"
    echo ""
    echo "4. Visit http://localhost:5173 to view the application"
    echo ""
}

main "$@"
