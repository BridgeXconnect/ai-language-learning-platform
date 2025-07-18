#!/bin/bash

# ===================================================================
# AI Language Learning Platform - Quick Organization Actions
# ===================================================================
# This script provides quick actions for immediate repository organization

set -e

echo "🚀 Quick Organization Actions"
echo "============================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_action() {
    echo -e "${BLUE}[ACTION]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Show menu
show_menu() {
    echo
    echo "Choose an action:"
    echo "1. 📦 Stage and commit current organization changes"
    echo "2. 🎨 Remove duplicate Next.js frontend (keep React/Vite)"
    echo "3. 🔄 Remove duplicate React frontend (keep Next.js)"
    echo "4. 🧹 Clean up common development files"
    echo "5. 📋 Create development environment setup"
    echo "6. 🔍 Show current git status"
    echo "7. 📊 Show project statistics"
    echo "8. ❌ Exit"
    echo
}

# Action 1: Stage and commit changes
stage_and_commit() {
    print_action "Staging and committing organization changes..."
    
    # Stage all changes
    git add .
    
    # Show what's being committed
    echo "Files to be committed:"
    git diff --cached --name-only
    
    # Commit with descriptive message
    git commit -m "feat: organize repository structure and track agent services

- Add comprehensive .gitignore
- Track all agent services (orchestrator, course-planner, content-creator, quality-assurance)
- Add organization documentation and scripts
- Standardize project structure
- Prepare for frontend consolidation"
    
    print_success "Changes committed successfully!"
}

# Action 2: Remove Next.js frontend
remove_nextjs() {
    print_warning "This will remove the Next.js frontend and keep React/Vite"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_action "Removing Next.js frontend..."
        rm -rf "client/Frontend"
        print_success "Next.js frontend removed. React/Vite frontend retained."
    else
        print_warning "Action cancelled."
    fi
}

# Action 3: Remove React frontend
remove_react() {
    print_warning "This will remove the React/Vite frontend and keep Next.js"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_action "Removing React/Vite frontend..."
        
        # First, let's move the Next.js frontend to the main client directory
        if [[ -d "client/Frontend/next-theme-setup (1)" ]]; then
            print_action "Moving Next.js frontend to main client directory..."
            
            # Backup current client directory
            mv client client_backup_$(date +%Y%m%d_%H%M%S)
            
            # Move Next.js frontend to main client directory
            mv "client_backup_$(date +%Y%m%d_%H%M%S)/Frontend/next-theme-setup (1)" client
            
            # Remove the backup
            rm -rf client_backup_*
            
            print_success "Next.js frontend moved to main client directory."
        else
            print_warning "Next.js frontend not found in expected location."
        fi
    else
        print_warning "Action cancelled."
    fi
}

# Action 4: Clean up development files
cleanup_dev_files() {
    print_action "Cleaning up common development files..."
    
    # Remove common development artifacts
    find . -name ".DS_Store" -delete 2>/dev/null || true
    find . -name "*.log" -delete 2>/dev/null || true
    find . -name "*.tmp" -delete 2>/dev/null || true
    find . -name "Thumbs.db" -delete 2>/dev/null || true
    
    # Clean up empty directories
    find . -type d -empty -delete 2>/dev/null || true
    
    print_success "Development files cleaned up."
}

# Action 5: Create development environment setup
create_dev_setup() {
    print_action "Creating development environment setup..."
    
    # Create a comprehensive development setup script
    cat > setup-dev-environment.sh << 'EOF'
#!/bin/bash

echo "🛠️  Setting up AI Language Learning Platform Development Environment"
echo "=================================================================="

# Check prerequisites
echo "Checking prerequisites..."

# Check Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js $(node --version) found"
else
    echo "❌ Node.js not found. Please install Node.js 18+"
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
EOF

    chmod +x setup-dev-environment.sh
    print_success "Development setup script created: setup-dev-environment.sh"
}

# Action 6: Show git status
show_git_status() {
    print_action "Current git status:"
    echo
    git status
}

# Action 7: Show project statistics
show_project_stats() {
    print_action "Project statistics:"
    echo
    
    # Count files by type
    echo "📊 File counts:"
    echo "   Python files: $(find . -name '*.py' -not -path './venv/*' -not -path './node_modules/*' | wc -l)"
    echo "   JavaScript/TypeScript files: $(find . -name '*.js' -o -name '*.jsx' -o -name '*.ts' -o -name '*.tsx' | wc -l)"
    echo "   Markdown files: $(find . -name '*.md' | wc -l)"
    echo "   Docker files: $(find . -name 'Dockerfile*' -o -name 'docker-compose*.yml' | wc -l)"
    echo
    
    # Count lines of code
    echo "📏 Lines of code (excluding node_modules, venv, .git):"
    find . -name '*.py' -o -name '*.js' -o -name '*.jsx' -o -name '*.ts' -o -name '*.tsx' | \
    grep -v node_modules | grep -v venv | grep -v .git | \
    xargs wc -l | tail -n 1
    echo
    
    # Show largest directories
    echo "📁 Largest directories:"
    du -sh * 2>/dev/null | sort -hr | head -5
}

# Main menu loop
while true; do
    show_menu
    read -p "Enter your choice (1-8): " choice
    
    case $choice in
        1)
            stage_and_commit
            ;;
        2)
            remove_nextjs
            ;;
        3)
            remove_react
            ;;
        4)
            cleanup_dev_files
            ;;
        5)
            create_dev_setup
            ;;
        6)
            show_git_status
            ;;
        7)
            show_project_stats
            ;;
        8)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            print_warning "Invalid choice. Please enter 1-8."
            ;;
    esac
    
    echo
    read -p "Press Enter to continue..."
done 