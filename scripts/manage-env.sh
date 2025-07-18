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
