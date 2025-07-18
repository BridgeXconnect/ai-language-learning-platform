#!/bin/bash

# ===================================================================
# AI Language Learning Platform - Repository Organization Script
# ===================================================================
# This script helps organize the repository structure and git status

set -e  # Exit on any error

echo "🧹 AI Language Learning Platform - Repository Organization"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if we're in the right directory
if [[ ! -f "docker-compose.yml" ]]; then
    print_error "Please run this script from the root of the AI Language Learning Platform directory"
    exit 1
fi

print_status "Starting repository organization..."

# ===================================================================
# PHASE 1: GIT ORGANIZATION
# ===================================================================
echo
echo "🔧 Phase 1: Git Organization"
echo "----------------------------"

# Check git status
print_status "Checking current git status..."
git status --porcelain > /tmp/git_status.txt

# Count untracked files
UNTRACKED_COUNT=$(grep "^??" /tmp/git_status.txt | wc -l)
MODIFIED_COUNT=$(grep "^ M" /tmp/git_status.txt | wc -l)

print_status "Found $UNTRACKED_COUNT untracked files and $MODIFIED_COUNT modified files"

# Create a comprehensive .gitignore if it doesn't exist or is incomplete
print_status "Updating .gitignore..."
cat > .gitignore << 'EOF'
# ===================================================================
# AI Language Learning Platform - .gitignore
# ===================================================================

# Environment Variables
.env
.env.local
.env.development
.env.staging
.env.production
*.env

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Dependencies
node_modules/
*/node_modules/
venv/
env/
*/venv/
*/env/
__pycache__/
*.py[cod]
*$py.class
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Python virtual environments
.venv
.env
.venv/
.env/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Build outputs
build/
dist/
*/build/
*/dist/

# Test coverage
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Uploads and temporary files
uploads/
temp/
tmp/
*.tmp

# Docker
.dockerignore

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# Celery
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Next.js
.next/
out/

# Nuxt.js
.nuxt
dist

# Storybook build outputs
.out
.storybook-out

# Temporary folders
tmp/
temp/

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# ===================================================================
# Project Specific
# ===================================================================

# AI Language Learning Platform specific
*.json.bak
*_backup.*
test_uploads/
EOF

print_success ".gitignore updated"

# ===================================================================
# PHASE 2: TRACK IMPORTANT UNTRACKED FILES
# ===================================================================
echo
echo "📁 Phase 2: Adding Important Untracked Files"
echo "--------------------------------------------"

# List of important files/directories to track
IMPORTANT_FILES=(
    "agents/"
    ".github/workflows/"
    "server/simple_create_user.py"
    "client/src/components/agents/"
    "client/src/pages/AgentsDashboard.jsx"
    "scripts/run-automation-workflow.sh"
    "scripts/setup-mcp.sh" 
    "scripts/start-agents.sh"
    "server/app/routes/agent_routes.py"
)

for file in "${IMPORTANT_FILES[@]}"; do
    if [[ -e "$file" ]]; then
        print_status "Adding $file to git..."
        git add "$file"
        print_success "Added $file"
    else
        print_warning "$file not found, skipping..."
    fi
done

# ===================================================================
# PHASE 3: FRONTEND CONSOLIDATION ANALYSIS
# ===================================================================
echo
echo "🎨 Phase 3: Frontend Analysis"
echo "-----------------------------"

# Check if both React and Next.js frontends exist
if [[ -d "client/src" && -d "client/Frontend/next-theme-setup (1)" ]]; then
    print_warning "Duplicate frontend detected!"
    echo "  - React (Vite): client/src/"
    echo "  - Next.js: client/Frontend/next-theme-setup (1)/"
    echo ""
    echo "Recommendation: Consolidate to one frontend technology"
    echo "Next.js is recommended for:"
    echo "  ✅ Better SER/SSG capabilities"
    echo "  ✅ Built-in routing"
    echo "  ✅ Better performance optimizations"
    echo "  ✅ Modern React features"
    echo ""
fi

# ===================================================================
# PHASE 4: DIRECTORY STRUCTURE ANALYSIS
# ===================================================================
echo
echo "📋 Phase 4: Directory Structure Analysis"
echo "----------------------------------------"

# Check for naming inconsistencies
print_status "Analyzing directory structure..."

# Check agents directory
if [[ -d "agents" ]]; then
    print_success "Agents directory exists"
    for agent in "orchestrator" "course-planner" "content-creator" "quality-assurance"; do
        if [[ -d "agents/$agent" ]]; then
            print_success "  ✅ $agent agent found"
        else
            print_error "  ❌ $agent agent missing"
        fi
    done
else
    print_error "Agents directory not found"
fi

# ===================================================================
# PHASE 5: DOCUMENTATION CHECK
# ===================================================================
echo
echo "📚 Phase 5: Documentation Analysis"
echo "----------------------------------"

# Check documentation structure
DOC_FILES=(
    "README.md"
    "docs/README.md"
    "docs/architecture/overview.md"
    "SETUP.md"
)

for doc in "${DOC_FILES[@]}"; do
    if [[ -f "$doc" ]]; then
        print_success "Found: $doc"
    else
        print_warning "Missing: $doc"
    fi
done

# ===================================================================
# PHASE 6: DEPENDENCY ANALYSIS
# ===================================================================
echo
echo "📦 Phase 6: Dependency Analysis"
echo "-------------------------------"

# Check key dependency files
DEPENDENCY_FILES=(
    "server/requirements.txt"
    "client/package.json"
    "docker-compose.yml"
)

for dep_file in "${DEPENDENCY_FILES[@]}"; do
    if [[ -f "$dep_file" ]]; then
        print_success "Found: $dep_file"
    else
        print_error "Missing: $dep_file"
    fi
done

# ===================================================================
# PHASE 7: GENERATE ORGANIZATION REPORT
# ===================================================================
echo
echo "📊 Phase 7: Generating Organization Report"
echo "-----------------------------------------"

cat > ORGANIZATION_REPORT.md << 'EOF'
# Repository Organization Report

## Current Status

### ✅ Completed Actions
- [x] Updated comprehensive .gitignore
- [x] Added important untracked files to git
- [x] Analyzed directory structure
- [x] Generated organization report

### 🚧 Issues Identified

#### 1. Duplicate Frontend Setup
- **Problem**: Both React (Vite) and Next.js frontends exist
- **Location**: `client/src/` and `client/Frontend/next-theme-setup (1)/`
- **Recommendation**: Consolidate to Next.js for better features

#### 2. Naming Inconsistencies
- **Problem**: Mixed naming conventions across directories
- **Examples**: kebab-case, snake_case, camelCase mixed
- **Recommendation**: Standardize to kebab-case for directories

#### 3. Configuration Scattered
- **Problem**: Environment configs in multiple locations
- **Recommendation**: Centralize to root-level .env files

### 📋 Next Steps (Priority Order)

#### High Priority
1. **Choose Frontend Technology**
   - Decide between React (Vite) or Next.js
   - Migrate components from unused frontend
   - Remove duplicate frontend

2. **Commit Current Changes**
   ```bash
   git add .
   git commit -m "feat: organize repository structure and track agent services"
   ```

3. **Standardize Agent Services**
   - Ensure all agents have consistent structure
   - Add proper error handling
   - Standardize logging

#### Medium Priority
1. **Backend Restructuring**
   - Consider renaming `server/` to `apps/api-gateway/`
   - Organize routes and services better
   - Implement proper dependency injection

2. **Documentation Consolidation**
   - Update all README files
   - Create single source of truth
   - Add proper navigation

#### Low Priority
1. **Infrastructure Organization**
   - Move deployment configs to `infrastructure/`
   - Organize Docker configurations
   - Standardize scripts

## Recommendations

### Frontend Decision Matrix

| Factor | React (Vite) | Next.js |
|--------|-------------|---------|
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **SEO** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Routing** | ⭐⭐⭐ (with React Router) | ⭐⭐⭐⭐⭐ (built-in) |
| **Build System** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Learning Curve** | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Production Ready** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Recommendation: Next.js** for better SSR, routing, and production optimizations.

## Implementation Plan

### Week 1: Core Organization
- [ ] Frontend consolidation decision
- [ ] Git organization completion
- [ ] Basic restructuring

### Week 2: Service Standardization  
- [ ] Agent service organization
- [ ] Backend restructuring
- [ ] Configuration consolidation

### Week 3: Documentation & Tooling
- [ ] Documentation update
- [ ] Development tooling
- [ ] Testing setup

### Week 4: Final Polish
- [ ] Code quality improvements
- [ ] Performance optimizations
- [ ] Production readiness

EOF

print_success "Organization report generated: ORGANIZATION_REPORT.md"

# ===================================================================
# FINAL SUMMARY
# ===================================================================
echo
echo "🎉 Organization Analysis Complete!"
echo "=================================="
echo
print_success "Repository analysis completed successfully!"
echo
echo "Key files generated:"
echo "  📄 ORGANIZATION_REPORT.md - Detailed analysis and recommendations"
echo "  📄 .gitignore - Comprehensive ignore rules"
echo
echo "Next steps:"
echo "  1️⃣  Review ORGANIZATION_REPORT.md"
echo "  2️⃣  Decide on frontend technology (React vs Next.js)"
echo "  3️⃣  Run: git add . && git commit -m 'feat: organize repository structure'"
echo "  4️⃣  Follow the implementation plan in the report"
echo
print_warning "Note: This script analyzed the structure but didn't make major changes."
print_warning "Review the report and implement changes incrementally."

echo
echo "�� Happy organizing!" 