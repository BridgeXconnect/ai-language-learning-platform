#!/bin/bash

# 🚀 AI Language Learning Platform - Deployment Setup
# Single source of truth for deployment configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$SCRIPT_DIR/config"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"
DOCS_DIR="$SCRIPT_DIR/docs"

# Function to print colored output
print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${CYAN}→${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to prompt for input with default
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    if [ -n "$default" ]; then
        echo -e "${BLUE}$prompt${NC} (default: $default): "
        read -r input
        if [ -z "$input" ]; then
            input="$default"
        fi
    else
        echo -e "${BLUE}$prompt${NC}: "
        read -r input
    fi
    
    eval "$var_name=\"$input\""
}

# Function to validate URL
validate_url() {
    local url="$1"
    if [[ $url =~ ^https?:// ]]; then
        return 0
    else
        return 1
    fi
}

# Function to validate email
validate_email() {
    local email="$1"
    if [[ $email =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to create directory structure
create_directory_structure() {
    print_status "Creating deployment directory structure..."
    
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$SCRIPTS_DIR"
    mkdir -p "$DOCS_DIR"
    mkdir -p "$SCRIPT_DIR/backup"
    
    print_success "Directory structure created"
}

# Function to check requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    local missing_tools=()
    
    # Check for required tools
    if ! command_exists git; then
        missing_tools+=("git")
    fi
    
    if ! command_exists curl; then
        missing_tools+=("curl")
    fi
    
    if ! command_exists jq; then
        print_warning "jq not found - JSON parsing will be limited"
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        print_error "Please install them and run this script again"
        exit 1
    fi
    
    print_success "System requirements check passed"
}

# Function to check repository status
check_repository() {
    print_status "Checking repository status..."
    
    if [ ! -d "$PROJECT_ROOT/.git" ]; then
        print_error "Not a Git repository. Please run this script from your project root."
        exit 1
    fi
    
    # Check if we're on main branch
    local current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
    if [ "$current_branch" != "main" ]; then
        print_warning "You're not on the main branch. Current branch: $current_branch"
    fi
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        print_warning "You have uncommitted changes. Consider committing them before deployment."
    fi
    
    print_success "Repository check completed"
}

# Function to setup Supabase
setup_supabase() {
    print_header "Setting up Supabase Database"
    
    print_step "You'll need to create a Supabase project manually"
    print_step "Go to https://supabase.com and create a new project"
    print_step "Then run the SQL commands from the database schema"
    
    prompt_with_default "Enter your Supabase project URL" "" SUPABASE_URL
    prompt_with_default "Enter your Supabase anon key" "" SUPABASE_ANON_KEY
    
    if ! validate_url "$SUPABASE_URL"; then
        print_error "Invalid Supabase URL. Please enter a valid HTTPS URL."
        return 1
    fi
    
    # Create Supabase configuration
    cat > "$CONFIG_DIR/supabase.sql" << EOF
-- AI Language Learning Platform Database Schema
-- Run this in your Supabase SQL editor

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'student',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    language VARCHAR(50) NOT NULL,
    level VARCHAR(50) NOT NULL,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Course requests table
CREATE TABLE IF NOT EXISTS course_requests (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    client_name VARCHAR(255) NOT NULL,
    client_email VARCHAR(255) NOT NULL,
    language VARCHAR(50) NOT NULL,
    level VARCHAR(50) NOT NULL,
    requirements TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_courses_language ON courses(language);
CREATE INDEX IF NOT EXISTS idx_course_requests_status ON course_requests(status);
EOF
    
    print_success "Supabase configuration created"
    print_step "Run the SQL commands in your Supabase SQL editor"
}

# Function to setup Vercel
setup_vercel() {
    print_header "Setting up Vercel Frontend"
    
    print_step "You'll need to connect your GitHub repository to Vercel"
    print_step "Go to https://vercel.com and import your repository"
    print_step "Set the root directory to 'client'"
    
    prompt_with_default "Enter your Vercel project URL" "" VERCEL_URL
    prompt_with_default "Enter your Vercel project ID" "" VERCEL_PROJECT_ID
    
    if ! validate_url "$VERCEL_URL"; then
        print_error "Invalid Vercel URL. Please enter a valid HTTPS URL."
        return 1
    fi
    
    # Create Vercel configuration
    cat > "$CONFIG_DIR/vercel.json" << EOF
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-backend-url.onrender.com/api/:path*"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-backend-url.onrender.com",
    "NEXT_PUBLIC_SUPABASE_URL": "$SUPABASE_URL",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "$SUPABASE_ANON_KEY"
  }
}
EOF
    
    print_success "Vercel configuration created"
}

# Function to setup Render
setup_render() {
    print_header "Setting up Render Backend"
    
    print_step "You'll need to create a Render web service"
    print_step "Go to https://render.com and create a new web service"
    print_step "Connect your GitHub repository and set root directory to 'server'"
    
    prompt_with_default "Enter your Render backend URL" "" RENDER_BACKEND_URL
    prompt_with_default "Enter your Render service ID" "" RENDER_SERVICE_ID
    
    if ! validate_url "$RENDER_BACKEND_URL"; then
        print_error "Invalid Render URL. Please enter a valid HTTPS URL."
        return 1
    fi
    
    # Create Render configuration
    cat > "$CONFIG_DIR/render.yaml" << EOF
services:
  - type: web
    name: ai-language-learning-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port \$PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ai-language-learning-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: OPENAI_API_KEY
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: ENVIRONMENT
        value: production
      - key: CORS_ORIGINS
        value: $VERCEL_URL

  - type: redis
    name: ai-language-learning-redis
    ipAllowList: []

databases:
  - name: ai-language-learning-db
    databaseName: ai_lang_db
    user: ai_lang_user
EOF
    
    print_success "Render configuration created"
}

# Function to create environment files
create_environment_files() {
    print_status "Creating environment files..."
    
    # Frontend environment
    cat > "$PROJECT_ROOT/client/.env.local" << EOF
# Frontend Environment Variables
NEXT_PUBLIC_API_URL=$RENDER_BACKEND_URL
NEXT_PUBLIC_SUPABASE_URL=$SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
EOF
    
    # Backend environment
    cat > "$PROJECT_ROOT/server/.env" << EOF
# Backend Environment Variables
DATABASE_URL=postgresql://your-supabase-connection-string
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
ENVIRONMENT=production
CORS_ORIGINS=$VERCEL_URL
REDIS_URL=redis://your-redis-url
EOF
    
    print_success "Environment files created"
}

# Function to create deployment scripts
create_deployment_scripts() {
    print_status "Creating deployment scripts..."
    
    # Health check script
    cat > "$SCRIPTS_DIR/health-check.sh" << 'EOF'
#!/bin/bash

# Health check script for all services

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_service() {
    local name="$1"
    local url="$2"
    
    echo -n "Checking $name... "
    
    if curl -s -f "$url" > /dev/null; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

echo "Running health checks..."

# Check frontend
if [ -n "$NEXT_PUBLIC_API_URL" ]; then
    check_service "Frontend" "$NEXT_PUBLIC_API_URL"
fi

# Check backend
if [ -n "$RENDER_BACKEND_URL" ]; then
    check_service "Backend" "$RENDER_BACKEND_URL/health"
fi

echo "Health checks completed"
EOF
    
    # Deploy script
    cat > "$SCRIPT_DIR/deploy.sh" << 'EOF'
#!/bin/bash

# Deployment script

set -e

ENVIRONMENT="${1:-staging}"
BRANCH="${2:-main}"

echo "Deploying to $ENVIRONMENT from branch $BRANCH..."

# Check if we're on the right branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "$BRANCH" ]; then
    echo "Warning: You're not on the $BRANCH branch"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Push to trigger deployment
git push origin $BRANCH

echo "Deployment triggered. Check your deployment platform for status."
EOF
    
    # Make scripts executable
    chmod +x "$SCRIPTS_DIR/health-check.sh"
    chmod +x "$SCRIPT_DIR/deploy.sh"
    
    print_success "Deployment scripts created"
}

# Function to create documentation
create_documentation() {
    print_status "Creating documentation..."
    
    # Troubleshooting guide
    cat > "$DOCS_DIR/troubleshooting.md" << 'EOF'
# Troubleshooting Guide

## Common Issues

### Build Failures
1. Check the build logs in your deployment platform
2. Ensure all dependencies are properly installed
3. Verify environment variables are set correctly

### Database Connection Issues
1. Check your DATABASE_URL format
2. Ensure your database is accessible
3. Verify network connectivity

### Environment Variable Issues
1. Check that all required variables are set
2. Ensure variable names match exactly
3. Restart your services after changing variables

## Getting Help
1. Check the logs: `./deployment/scripts/check-logs.sh`
2. Run diagnostics: `./deployment/scripts/diagnostics.sh`
3. Contact support for your deployment platform
EOF
    
    # Monitoring guide
    cat > "$DOCS_DIR/monitoring.md" << 'EOF'
# Monitoring Guide

## Built-in Monitoring
- **Vercel**: Analytics, performance, and error tracking
- **Render**: Logs, metrics, and health checks
- **Supabase**: Database monitoring and alerts

## Manual Monitoring
- Run health checks: `./deployment/scripts/health-check.sh`
- Check logs: `./deployment/scripts/check-logs.sh`
- Monitor performance: Use your platform's dashboard

## Alerts
Set up alerts for:
- Service downtime
- High error rates
- Performance degradation
- Database issues
EOF
    
    print_success "Documentation created"
}

# Function to validate setup
validate_setup() {
    print_status "Validating setup..."
    
    local errors=()
    
    # Check if all required files exist
    if [ ! -f "$CONFIG_DIR/vercel.json" ]; then
        errors+=("Vercel configuration missing")
    fi
    
    if [ ! -f "$CONFIG_DIR/render.yaml" ]; then
        errors+=("Render configuration missing")
    fi
    
    if [ ! -f "$CONFIG_DIR/supabase.sql" ]; then
        errors+=("Supabase configuration missing")
    fi
    
    if [ ! -f "$PROJECT_ROOT/client/.env.local" ]; then
        errors+=("Frontend environment file missing")
    fi
    
    if [ ! -f "$PROJECT_ROOT/server/.env" ]; then
        errors+=("Backend environment file missing")
    fi
    
    if [ ${#errors[@]} -ne 0 ]; then
        print_error "Setup validation failed:"
        for error in "${errors[@]}"; do
            print_error "  - $error"
        done
        return 1
    fi
    
    print_success "Setup validation passed"
}

# Function to display next steps
display_next_steps() {
    print_header "Setup Complete! Next Steps"
    
    echo -e "${GREEN}1.${NC} Update environment variables with your actual values:"
    echo "   - Edit client/.env.local"
    echo "   - Edit server/.env"
    
    echo -e "${GREEN}2.${NC} Set up your services:"
    echo "   - Create Supabase project and run the SQL schema"
    echo "   - Connect GitHub to Vercel and deploy frontend"
    echo "   - Connect GitHub to Render and deploy backend"
    
    echo -e "${GREEN}3.${NC} Test your deployment:"
    echo "   ./deployment/scripts/health-check.sh"
    
    echo -e "${GREEN}4.${NC} Deploy to staging:"
    echo "   ./deployment/deploy.sh staging"
    
    echo -e "${GREEN}5.${NC} Deploy to production:"
    echo "   ./deployment/deploy.sh production"
    
    echo ""
    echo -e "${YELLOW}Need help?${NC} Check DEPLOYMENT.md for detailed instructions"
}

# Main execution
main() {
    print_header "AI Language Learning Platform - Deployment Setup"
    
    # Check if we're in the right directory
    if [ ! -f "$PROJECT_ROOT/package.json" ] && [ ! -f "$PROJECT_ROOT/client/package.json" ]; then
        print_error "Please run this script from your project root directory"
        exit 1
    fi
    
    # Run setup steps
    check_requirements
    check_repository
    create_directory_structure
    setup_supabase
    setup_vercel
    setup_render
    create_environment_files
    create_deployment_scripts
    create_documentation
    validate_setup
    
    print_header "Setup Complete!"
    display_next_steps
}

# Run main function
main "$@" 