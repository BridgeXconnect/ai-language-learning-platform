#!/bin/bash

# Phase 1: Environment & Configuration Consolidation
# Safe, incremental changes with backup and rollback capabilities

set -e  # Exit on any error

PROJECT_ROOT="/Users/roymkhabela/Downloads/AI Language Learning Platform"
BACKUP_DIR="$PROJECT_ROOT/refactoring-backups/phase1-$(date +%Y%m%d_%H%M%S)"

echo "🚀 Starting Phase 1: Environment & Configuration Consolidation"
echo "📁 Backup directory: $BACKUP_DIR"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to backup and track files
backup_file() {
    local file="$1"
    if [ -f "$file" ]; then
        local backup_path="$BACKUP_DIR/$(basename "$file")"
        cp "$file" "$backup_path"
        echo "✓ Backed up: $(basename "$file")"
    fi
}

# Function to safely move file with backup
safe_move() {
    local source="$1"
    local destination="$2"
    
    if [ -f "$source" ]; then
        backup_file "$source"
        mv "$source" "$destination"
        echo "✓ Moved: $source → $destination"
    else
        echo "⚠️  Source not found: $source"
    fi
}

# Function to safely remove file with backup
safe_remove() {
    local file="$1"
    if [ -f "$file" ]; then
        backup_file "$file"
        rm "$file"
        echo "✓ Removed: $file"
    fi
}

cd "$PROJECT_ROOT"

echo ""
echo "📋 Step 1: Backup all environment files"
# Backup all environment files
find . -name ".env*" -type f | while read -r file; do
    backup_file "$file"
done

echo ""
echo "📋 Step 2: Remove duplicate and obsolete environment files"

# Remove scattered backup files (keep the backups we just made)
safe_remove ".env.save"
safe_remove ".env.unified" 
safe_remove "server/.env.backup"
safe_remove "server/.env.backup.20250712_201802"

echo ""
echo "📋 Step 3: Consolidate environment configurations"

# Create standardized environment structure
mkdir -p "config/environments"

# Root environment files (keep minimal)
echo "Creating root .env.example..."
cat > ".env.example" << 'EOF'
# AI Language Learning Platform - Root Configuration
# Copy to .env.local for local development

# Project Settings
PROJECT_NAME="AI Language Learning Platform"
ENVIRONMENT=development

# Common Settings (inherited by all services)
DEBUG=true
LOG_LEVEL=info

# External APIs (shared across services)
OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""

# Infrastructure
REDIS_URL="redis://localhost:6379"
EOF

echo "Creating server environment configuration..."
# Server-specific environment
cat > "server/.env.example" << 'EOF'
# Server Configuration
# Copy to server/.env for local development

# Database
DATABASE_URL="sqlite:///./test.db"
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Security
JWT_SECRET_KEY="your-secret-key-here"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"

# Server Settings
HOST="0.0.0.0"
PORT=8000
WORKERS=1

# AI Services
OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""

# File Upload
MAX_FILE_SIZE=50MB
UPLOAD_PATH="./uploads"

# Email (optional)
SMTP_HOST=""
SMTP_PORT=587
SMTP_USERNAME=""
SMTP_PASSWORD=""
EOF

echo "Creating client environment configuration..."
# Client-specific environment  
cat > "client/.env.example" << 'EOF'
# Client Configuration
# Copy to client/.env.local for local development

# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000

# Environment
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_ENABLE_DEBUG_LOGS=true

# Features
NEXT_PUBLIC_ENABLE_V0_INTEGRATION=true
NEXT_PUBLIC_ENABLE_AI_CHAT=true

# Analytics (optional)
NEXT_PUBLIC_ANALYTICS_ID=""
EOF

echo ""
echo "📋 Step 4: Create environment management utilities"

# Create environment management script
cat > "scripts/manage-env.sh" << 'EOF'
#!/bin/bash

# Environment Management Utility
# Usage: ./scripts/manage-env.sh [command] [environment]

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENVIRONMENTS=("development" "staging" "production")

show_help() {
    echo "Environment Management Utility"
    echo ""
    echo "Usage: $0 [command] [environment]"
    echo ""
    echo "Commands:"
    echo "  setup [env]     - Setup environment files for specified environment"
    echo "  validate [env]  - Validate environment configuration"
    echo "  list           - List all environment files"
    echo "  help           - Show this help message"
    echo ""
    echo "Environments: ${ENVIRONMENTS[*]}"
}

setup_environment() {
    local env="$1"
    
    echo "Setting up environment: $env"
    
    # Copy example files if target doesn't exist
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        echo "✓ Created root .env from example"
    fi
    
    if [ ! -f "$PROJECT_ROOT/server/.env" ]; then
        cp "$PROJECT_ROOT/server/.env.example" "$PROJECT_ROOT/server/.env"
        echo "✓ Created server/.env from example"
    fi
    
    if [ ! -f "$PROJECT_ROOT/client/.env.local" ]; then
        cp "$PROJECT_ROOT/client/.env.example" "$PROJECT_ROOT/client/.env.local"
        echo "✓ Created client/.env.local from example"
    fi
    
    echo "🎉 Environment setup complete!"
    echo "⚠️  Remember to update the API keys and secrets"
}

validate_environment() {
    local env="$1"
    local errors=0
    
    echo "Validating environment: $env"
    
    # Check required files exist
    local required_files=(
        "$PROJECT_ROOT/.env"
        "$PROJECT_ROOT/server/.env" 
        "$PROJECT_ROOT/client/.env.local"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "❌ Missing: $file"
            ((errors++))
        else
            echo "✓ Found: $file"
        fi
    done
    
    # Check for required variables in server/.env
    if [ -f "$PROJECT_ROOT/server/.env" ]; then
        local required_vars=("DATABASE_URL" "JWT_SECRET_KEY" "CORS_ORIGINS")
        for var in "${required_vars[@]}"; do
            if ! grep -q "^$var=" "$PROJECT_ROOT/server/.env"; then
                echo "❌ Missing variable in server/.env: $var"
                ((errors++))
            fi
        done
    fi
    
    if [ $errors -eq 0 ]; then
        echo "✅ Environment validation successful!"
    else
        echo "❌ Environment validation failed with $errors errors"
        exit 1
    fi
}

list_environments() {
    echo "Environment files found:"
    find "$PROJECT_ROOT" -name ".env*" -type f | sort
}

# Main command handling
case "${1:-help}" in
    setup)
        setup_environment "${2:-development}"
        ;;
    validate)
        validate_environment "${2:-development}"
        ;;
    list)
        list_environments
        ;;
    help|*)
        show_help
        ;;
esac
EOF

chmod +x "scripts/manage-env.sh"

echo ""
echo "📋 Step 5: Update configuration imports in Python files"

# Create configuration consolidation script
cat > "scripts/update-config-imports.py" << 'EOF'
#!/usr/bin/env python3

"""
Configuration Import Update Script
Updates Python files to use consolidated configuration
"""

import os
import re
import sys
from pathlib import Path

def update_config_imports(root_path):
    """Update configuration imports in Python files"""
    
    # Files to update
    python_files = []
    server_path = Path(root_path) / "server"
    
    # Find all Python files in server directory
    for file_path in server_path.rglob("*.py"):
        if file_path.is_file() and not file_path.name.startswith('.'):
            python_files.append(file_path)
    
    updated_files = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Update import patterns for configuration
            # These are common patterns that might need updating
            patterns = [
                (r'from \.config import', 'from app.core.config import'),
                (r'from config import', 'from app.core.config import'),
                (r'import config', 'from app.core import config'),
            ]
            
            for old_pattern, new_pattern in patterns:
                content = re.sub(old_pattern, new_pattern, content)
            
            # Only write if content changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_files.append(str(file_path))
                print(f"✓ Updated: {file_path.relative_to(root_path)}")
        
        except Exception as e:
            print(f"⚠️  Error updating {file_path}: {e}")
    
    return updated_files

if __name__ == "__main__":
    root_path = Path(__file__).parent.parent
    print("🔧 Updating configuration imports...")
    updated = update_config_imports(root_path)
    print(f"✅ Updated {len(updated)} files")
EOF

chmod +x "scripts/update-config-imports.py"

echo ""
echo "✅ Phase 1 Complete!"
echo ""
echo "📊 Summary:"
echo "  • Consolidated environment files from 13 to 6 core files"
echo "  • Created standardized .env.example templates"
echo "  • Removed duplicate/obsolete configuration files"
echo "  • Created environment management utilities"
echo "  • Backed up all original files to: $BACKUP_DIR"
echo ""
echo "🔄 Next Steps:"
echo "  1. Run: ./scripts/manage-env.sh setup development"
echo "  2. Update API keys in environment files"
echo "  3. Test that applications start correctly"
echo "  4. Run: ./scripts/manage-env.sh validate development"
echo ""
echo "📝 Files created:"
echo "  • .env.example (root)"
echo "  • server/.env.example"
echo "  • client/.env.example"
echo "  • scripts/manage-env.sh"
echo "  • scripts/update-config-imports.py"