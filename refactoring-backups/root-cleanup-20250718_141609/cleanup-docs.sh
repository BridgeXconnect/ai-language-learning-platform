#!/bin/bash

# ===================================================================
# AI Language Learning Platform - Documentation Cleanup Script
# ===================================================================
# This script helps identify and clean up redundant documentation files

set -e

echo "📚 Documentation Cleanup Analysis"
echo "================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_keep() {
    echo -e "${GREEN}✅ KEEP:${NC} $1"
}

print_archive() {
    echo -e "${YELLOW}📦 ARCHIVE:${NC} $1"
}

print_delete() {
    echo -e "${RED}🗑️  DELETE:${NC} $1"
}

print_header "CURRENT DOCUMENTATION ANALYSIS"

# Create categories
echo "Analyzing your documentation files..."

print_header "CORE PROJECT DOCUMENTATION (KEEP)"
print_keep "README.md - Main project documentation"
print_keep "SETUP.md - Setup instructions"
print_keep "docs/ - Architecture and API documentation"

print_header "ORGANIZATION FILES (RECENTLY CREATED - KEEP)"
print_keep "PROJECT_REORGANIZATION_PLAN.md - Our reorganization plan"
print_keep "ORGANIZATION_REPORT.md - Current analysis"
print_keep "organize-repository.sh - Organization script"
print_keep "quick-organize.sh - Quick actions script"

print_header "REDUNDANT/OUTDATED FILES (CANDIDATES FOR CLEANUP)"

echo
echo "🔄 FRONTEND INTEGRATION (Multiple overlapping files):"
print_archive "epic-frontend-integration.md - Older frontend plan"
print_archive "FRONTEND_INTEGRATION_PLAN.md - Duplicate frontend planning"
print_archive "FRONTEND_INTEGRATION_PROGRESS.md - Progress tracking (outdated?)"

echo
echo "📊 PROGRESS TRACKING (Multiple overlapping files):"
print_archive "PROGRESS_SAVE.md - Old progress snapshot"
print_archive "RESUME_DEVELOPMENT.md - Development resumption notes"

echo
echo "🎨 UX DOCUMENTATION (Multiple overlapping files):"
print_archive "UX_ENHANCEMENT_REPORT.md - UX analysis"
print_archive "UX_IMPLEMENTATION_GUIDE.md - UX implementation"
print_archive "UX_PHASE2_IMPLEMENTATION_COMPLETE.md - UX completion report"
print_archive "UX_STRATEGY_COMPREHENSIVE.md - UX strategy"

echo
echo "🔧 V0 GENERATED FILES (Tool-generated, may be outdated):"
print_archive "v0-course-manager-portal-complete.md - V0 tool output"
print_archive "v0-prompt.md - V0 prompts"
print_archive "v0-sales-portal-complete.md - V0 tool output"
print_archive "v0-trainer-portal-complete.md - V0 tool output"
print_archive "v0-ui-enhancement-prompt.md - V0 prompts"

echo
echo "⚙️ CONFIGURATION/SCRIPTS (Review needed):"
print_keep "mcp-config.json - MCP configuration (if still used)"
print_keep "github-setup.sh - GitHub setup script"
print_keep "start-dev.sh - Development startup script"
print_keep "start-frontend-dev.sh - Frontend startup script"

print_header "CLEANUP RECOMMENDATIONS"

cat << 'EOF'

📋 CLEANUP STRATEGY:

1. 🗂️  CREATE ARCHIVE DIRECTORY
   mkdir -p docs/archive/old-planning
   mkdir -p docs/archive/v0-generated
   mkdir -p docs/archive/progress-reports

2. 📦 MOVE REDUNDANT FILES TO ARCHIVE
   # Frontend planning documents
   mv epic-frontend-integration.md docs/archive/old-planning/
   mv FRONTEND_INTEGRATION_*.md docs/archive/old-planning/
   
   # Progress/resume documents  
   mv PROGRESS_SAVE.md docs/archive/progress-reports/
   mv RESUME_DEVELOPMENT.md docs/archive/progress-reports/
   
   # UX documents (consolidate if needed)
   mv UX_*.md docs/archive/old-planning/
   
   # V0 generated files
   mv v0-*.md docs/archive/v0-generated/

3. 🧹 KEEP ONLY ESSENTIAL DOCS AT ROOT
   README.md
   SETUP.md
   PROJECT_REORGANIZATION_PLAN.md
   ORGANIZATION_REPORT.md

4. 📚 ORGANIZE REMAINING DOCS
   docs/
   ├── architecture/     # Technical architecture
   ├── api/             # API documentation  
   ├── product/         # Product requirements
   ├── development/     # Development guides
   └── archive/         # Historical documents

BENEFITS:
✅ Clean project root
✅ Preserve historical context in archives
✅ Clear current vs historical separation
✅ Easier navigation for new developers
✅ Reduced cognitive overhead

EOF

print_header "INTERACTIVE CLEANUP OPTIONS"

echo "Choose cleanup action:"
echo "1. 📦 Create archive structure and move files"
echo "2. 🗑️  Delete redundant files (after backup)"
echo "3. 📋 Just show what would be moved/deleted"
echo "4. ❌ Exit without changes"

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "Creating archive structure and moving files..."
        
        # Create archive directories
        mkdir -p docs/archive/{old-planning,v0-generated,progress-reports}
        
        # Move files to archive
        echo "Moving frontend planning docs..."
        [[ -f "epic-frontend-integration.md" ]] && mv epic-frontend-integration.md docs/archive/old-planning/
        [[ -f "FRONTEND_INTEGRATION_PLAN.md" ]] && mv FRONTEND_INTEGRATION_PLAN.md docs/archive/old-planning/
        [[ -f "FRONTEND_INTEGRATION_PROGRESS.md" ]] && mv FRONTEND_INTEGRATION_PROGRESS.md docs/archive/old-planning/
        
        echo "Moving progress reports..."
        [[ -f "PROGRESS_SAVE.md" ]] && mv PROGRESS_SAVE.md docs/archive/progress-reports/
        [[ -f "RESUME_DEVELOPMENT.md" ]] && mv RESUME_DEVELOPMENT.md docs/archive/progress-reports/
        
        echo "Moving UX documents..."
        [[ -f "UX_ENHANCEMENT_REPORT.md" ]] && mv UX_ENHANCEMENT_REPORT.md docs/archive/old-planning/
        [[ -f "UX_IMPLEMENTATION_GUIDE.md" ]] && mv UX_IMPLEMENTATION_GUIDE.md docs/archive/old-planning/
        [[ -f "UX_PHASE2_IMPLEMENTATION_COMPLETE.md" ]] && mv UX_PHASE2_IMPLEMENTATION_COMPLETE.md docs/archive/old-planning/
        [[ -f "UX_STRATEGY_COMPREHENSIVE.md" ]] && mv UX_STRATEGY_COMPREHENSIVE.md docs/archive/old-planning/
        
        echo "Moving V0 generated files..."
        [[ -f "v0-course-manager-portal-complete.md" ]] && mv v0-course-manager-portal-complete.md docs/archive/v0-generated/
        [[ -f "v0-prompt.md" ]] && mv v0-prompt.md docs/archive/v0-generated/
        [[ -f "v0-sales-portal-complete.md" ]] && mv v0-sales-portal-complete.md docs/archive/v0-generated/
        [[ -f "v0-trainer-portal-complete.md" ]] && mv v0-trainer-portal-complete.md docs/archive/v0-generated/
        [[ -f "v0-ui-enhancement-prompt.md" ]] && mv v0-ui-enhancement-prompt.md docs/archive/v0-generated/
        
        echo -e "${GREEN}✅ Files archived successfully!${NC}"
        ;;
    2)
        echo -e "${RED}⚠️  DELETE MODE${NC}"
        echo "This will permanently delete redundant files after creating a backup."
        read -p "Are you sure? Type 'DELETE' to confirm: " confirm
        if [[ "$confirm" == "DELETE" ]]; then
            # Create backup first
            backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
            mkdir -p "$backup_dir"
            
            # List of files to delete
            files_to_delete=(
                "epic-frontend-integration.md"
                "FRONTEND_INTEGRATION_PLAN.md" 
                "FRONTEND_INTEGRATION_PROGRESS.md"
                "PROGRESS_SAVE.md"
                "RESUME_DEVELOPMENT.md"
                "UX_ENHANCEMENT_REPORT.md"
                "UX_IMPLEMENTATION_GUIDE.md"
                "UX_PHASE2_IMPLEMENTATION_COMPLETE.md"
                "UX_STRATEGY_COMPREHENSIVE.md"
                "v0-course-manager-portal-complete.md"
                "v0-prompt.md"
                "v0-sales-portal-complete.md"
                "v0-trainer-portal-complete.md"
                "v0-ui-enhancement-prompt.md"
            )
            
            # Backup and delete
            for file in "${files_to_delete[@]}"; do
                if [[ -f "$file" ]]; then
                    cp "$file" "$backup_dir/"
                    rm "$file"
                    echo "Deleted: $file (backed up)"
                fi
            done
            
            echo -e "${GREEN}✅ Files deleted and backed up to $backup_dir${NC}"
        else
            echo "Delete cancelled."
        fi
        ;;
    3)
        echo "Files that would be moved to archive:"
        ls -la epic-frontend-integration.md FRONTEND_INTEGRATION_*.md PROGRESS_SAVE.md RESUME_DEVELOPMENT.md UX_*.md v0-*.md 2>/dev/null || echo "Some files not found"
        ;;
    4)
        echo "No changes made."
        ;;
    *)
        echo "Invalid choice."
        ;;
esac

print_header "SUMMARY"
echo "After cleanup, your root directory should only contain:"
echo "📄 README.md"
echo "📄 SETUP.md" 
echo "📄 PROJECT_REORGANIZATION_PLAN.md"
echo "📄 ORGANIZATION_REPORT.md"
echo "📄 docker-compose.yml"
echo "📄 .gitignore"
echo "📁 client/"
echo "📁 server/"
echo "📁 agents/"
echo "📁 docs/"
echo "📁 scripts/"

echo
echo "🎉 Much cleaner and more maintainable!" 