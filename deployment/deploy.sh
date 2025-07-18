#!/bin/bash

# 🚀 AI Language Learning Platform - Deployment Script
# Simple deployment trigger

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

ENVIRONMENT="${1:-staging}"
BRANCH="${2:-main}"

echo -e "${BLUE}🚀 Deploying AI Language Learning Platform${NC}"
echo -e "${BLUE}Environment:${NC} $ENVIRONMENT"
echo -e "${BLUE}Branch:${NC} $BRANCH"
echo ""

# Check if we're on the right branch
current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
if [ "$current_branch" != "$BRANCH" ]; then
    echo -e "${YELLOW}Warning: You're not on the $BRANCH branch${NC}"
    echo -e "${YELLOW}Current branch: $current_branch${NC}"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Deployment cancelled${NC}"
        exit 1
    fi
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    echo -e "${YELLOW}Warning: You have uncommitted changes${NC}"
    echo ""
    read -p "Commit changes before deploying? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Committing changes...${NC}"
        git add .
        git commit -m "Auto-commit before deployment to $ENVIRONMENT"
    fi
fi

# Push to trigger deployment
echo -e "${BLUE}Pushing to $BRANCH to trigger deployment...${NC}"
git push origin $BRANCH

echo ""
echo -e "${GREEN}✅ Deployment triggered successfully!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Check your deployment platform for build status"
echo "2. Monitor the deployment logs"
echo "3. Run health checks: ./deployment/scripts/health-check.sh"
echo ""
echo -e "${YELLOW}Deployment platforms:${NC}"
echo "- Frontend: https://vercel.com/dashboard"
echo "- Backend: https://render.com/dashboard"
echo "- Database: https://supabase.com/dashboard" 