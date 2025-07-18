#!/bin/bash

# Cleanup Root Files - Organize scattered files into appropriate directories
# This script organizes all loose files at the root level into proper directories

set -e

PROJECT_ROOT="/Users/roymkhabela/Downloads/AI Language Learning Platform"
BACKUP_DIR="$PROJECT_ROOT/refactoring-backups/root-cleanup-$(date +%Y%m%d_%H%M%S)"

echo "🧹 Starting Root Files Cleanup"
echo "📁 Backup directory: $BACKUP_DIR"

# Create backup directory
mkdir -p "$BACKUP_DIR"

cd "$PROJECT_ROOT"

# Function to backup and move file
backup_and_move() {
    local source="$1"
    local destination="$2"
    
    if [ -f "$source" ]; then
        # Backup original
        cp "$source" "$BACKUP_DIR/"
        echo "✓ Backed up: $(basename "$source")"
        
        # Create destination directory if it doesn't exist
        mkdir -p "$(dirname "$destination")"
        
        # Move file
        mv "$source" "$destination"
        echo "✓ Moved: $source → $destination"
    else
        echo "⚠️  Source not found: $source"
    fi
}

# Function to backup and remove file
backup_and_remove() {
    local file="$1"
    local reason="$2"
    
    if [ -f "$file" ]; then
        # Backup original
        cp "$file" "$BACKUP_DIR/"
        echo "✓ Backed up: $(basename "$file")"
        
        # Remove file
        rm "$file"
        echo "✓ Removed: $file ($reason)"
    fi
}

echo ""
echo "📋 Step 1: Create organized directory structure"

# Create directories for different file types
mkdir -p "docs/progress-reports"
mkdir -p "docs/archived"
mkdir -p "logs"
mkdir -p "scripts/legacy"
mkdir -p "scripts/deployment"
mkdir -p "config/docker"
mkdir -p "config/testing"
mkdir -p "temp"

echo ""
echo "📋 Step 2: Organize documentation files"

# Progress reports and summaries
backup_and_move "AUTHENTICATION_REBUILD_COMPLETE.md" "docs/progress-reports/"
backup_and_move "AUTH_SYSTEM_FIXES.md" "docs/progress-reports/"
backup_and_move "AI_ENHANCEMENT_COMPLETION_SUMMARY.md" "docs/progress-reports/"
backup_and_move "AI_IMPLEMENTATION_ROADMAP.md" "docs/progress-reports/"
backup_and_move "AI_AGENT_INTEGRATION_SUMMARY.md" "docs/progress-reports/"
backup_and_move "SOLUTION_SUMMARY.md" "docs/progress-reports/"
backup_and_move "CLEANUP_SUMMARY.md" "docs/progress-reports/"
backup_and_move "MVP_COMPLETION_PLAN.md" "docs/progress-reports/"
backup_and_move "ORGANIZATION_REPORT.md" "docs/progress-reports/"
backup_and_move "PROJECT_REORGANIZATION_PLAN.md" "docs/progress-reports/"
backup_and_move "MIGRATION_PLAN.md" "docs/progress-reports/"
backup_and_move "PERMANENT_SETUP_GUIDE.md" "docs/progress-reports/"
backup_and_move "ARCHON_AUTOMATION_GUIDE.md" "docs/progress-reports/"

echo ""
echo "📋 Step 3: Organize log files"

# Log files
backup_and_move "agent_logs.txt" "logs/"
backup_and_move "frontend_logs.txt" "logs/"
backup_and_move "pytest_output.txt" "logs/"

echo ""
echo "📋 Step 4: Organize configuration files"

# Docker configurations
backup_and_move "docker-compose.yml" "config/docker/"
backup_and_move "docker-compose.prod.yml" "config/docker/"
backup_and_move "docker-compose.staging.yml" "config/docker/"

# Testing configurations
backup_and_move "jest.config.js" "config/testing/"

# MCP configuration
backup_and_move "mcp-config.json" "config/"

echo ""
echo "📋 Step 5: Organize scripts"

# Deployment scripts
backup_and_move "github-setup.sh" "scripts/deployment/"
backup_and_move "setup-dev-env.sh" "scripts/deployment/"
backup_and_move "start-app.sh" "scripts/deployment/"
backup_and_move "stop-app.sh" "scripts/deployment/"
backup_and_move "health-check.sh" "scripts/deployment/"

# Legacy/organization scripts
backup_and_move "cleanup-docs.sh" "scripts/legacy/"
backup_and_move "quick-organize.sh" "scripts/legacy/"
backup_and_move "organize-repository.sh" "scripts/legacy/"

echo ""
echo "📋 Step 6: Organize test and debug files"

# Test files
backup_and_move "test_workflow.py" "temp/"

# Debug files
backup_and_move "debug-auth.html" "temp/"

echo ""
echo "📋 Step 7: Clean up temporary and system files"

# Remove temporary files
backup_and_remove ".agent_pids" "temporary process file"
backup_and_remove ".DS_Store" "macOS system file"

echo ""
echo "📋 Step 8: Update .gitignore for new structure"

# Update .gitignore to reflect new structure
cat >> .gitignore << 'EOF'

# Logs directory
logs/

# Temporary files
temp/

# Legacy scripts
scripts/legacy/

# Archived documentation
docs/archived/
docs/progress-reports/

EOF

echo ""
echo "📋 Step 9: Create directory structure documentation"

# Create a README for the new structure
cat > "docs/DIRECTORY_STRUCTURE.md" << 'EOF'
# Directory Structure Guide

## Root Level
- `client/` - Next.js frontend application
- `server/` - Python FastAPI backend application
- `packages/` - Shared utilities and types
- `agents/` - AI agent implementations
- `docs/` - Project documentation
- `scripts/` - Project-wide scripts and utilities
- `config/` - Configuration files
- `logs/` - Application and test logs
- `temp/` - Temporary files and debug artifacts

## Documentation Organization
- `docs/progress-reports/` - Development progress reports and summaries
- `docs/archived/` - Archived documentation
- `docs/prd/` - Product requirements documentation
- `docs/architecture/` - System architecture documentation

## Configuration Organization
- `config/docker/` - Docker configuration files
- `config/testing/` - Testing configuration files
- `config/environments/` - Environment-specific configurations

## Scripts Organization
- `scripts/deployment/` - Deployment and environment setup scripts
- `scripts/legacy/` - Legacy organization and cleanup scripts
- `scripts/` - Current project scripts

## Logs Organization
- `logs/` - All application logs, test outputs, and debugging information

## Temporary Files
- `temp/` - Debug files, test artifacts, and temporary development files

## Guidelines for New Files
1. **Documentation**: Place in appropriate `docs/` subdirectory
2. **Configuration**: Place in appropriate `config/` subdirectory
3. **Scripts**: Place in appropriate `scripts/` subdirectory
4. **Logs**: Place in `logs/` directory
5. **Temporary files**: Place in `temp/` directory
6. **Never leave files at root level** unless they are essential project files (README, .gitignore, etc.)
EOF

echo ""
echo "📋 Step 10: Create cleanup summary"

# Create cleanup summary
cat > "docs/ROOT_CLEANUP_SUMMARY.md" << EOF
# Root Files Cleanup Summary

## Cleanup Completed: $(date)

### Files Organized
- **Documentation**: 13 files moved to \`docs/progress-reports/\`
- **Logs**: 3 files moved to \`logs/\`
- **Configuration**: 5 files moved to \`config/\` subdirectories
- **Scripts**: 7 files moved to \`scripts/\` subdirectories
- **Temporary**: 2 files moved to \`temp/\`

### Files Removed
- **System files**: 2 files removed (.DS_Store, .agent_pids)

### New Structure Created
- \`docs/progress-reports/\` - Development progress documentation
- \`logs/\` - Application and test logs
- \`config/docker/\` - Docker configurations
- \`config/testing/\` - Testing configurations
- \`scripts/deployment/\` - Deployment scripts
- \`scripts/legacy/\` - Legacy organization scripts
- \`temp/\` - Temporary and debug files

### Backup Location
All original files backed up to: \`$BACKUP_DIR\`

### Next Steps
1. Review the new organization
2. Update any hardcoded file paths in scripts
3. Update documentation references
4. Commit the new structure to version control

## Files Moved

### Documentation Files
$(ls -1 docs/progress-reports/ 2>/dev/null | sed 's/^/- /' || echo "- No files found")

### Log Files
$(ls -1 logs/ 2>/dev/null | sed 's/^/- /' || echo "- No files found")

### Configuration Files
$(find config/ -type f 2>/dev/null | sed 's/^/- /' || echo "- No files found")

### Script Files
$(find scripts/ -type f 2>/dev/null | sed 's/^/- /' || echo "- No files found")
EOF

echo ""
echo "✅ Root Files Cleanup Complete!"

echo ""
echo "📊 Summary:"
echo "  • Organized $(find docs/progress-reports/ logs/ config/ scripts/ temp/ -type f 2>/dev/null | wc -l | tr -d ' ') files into appropriate directories"
echo "  • Removed 2 system/temporary files"
echo "  • Created organized directory structure"
echo "  • Updated .gitignore for new structure"
echo "  • Created directory structure documentation"
echo "  • Backed up all original files to: $BACKUP_DIR"

echo ""
echo "🔄 Next Steps:"
echo "  1. Review the new organization in docs/DIRECTORY_STRUCTURE.md"
echo "  2. Update any hardcoded file paths in your scripts"
echo "  3. Commit the new structure to version control"
echo "  4. Update documentation references to new file locations"

echo ""
echo "📝 Files are now organized by type and purpose!" 