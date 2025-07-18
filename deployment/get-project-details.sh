#!/bin/bash

# 🔧 Get Supabase Project Details
# This script helps you get your project URL and keys

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

print_step() {
    echo -e "${BLUE}→${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_header "Getting Supabase Project Details"

echo -e "${BLUE}Project Name:${NC} ai_lang_platform"
echo -e "${BLUE}Database Password:${NC} a9kDtuQBiwVnaQE9"
echo ""

print_step "1. Go to your Supabase dashboard: https://supabase.com/dashboard"
print_step "2. Click on your project: ai_lang_platform"
print_step "3. Go to Settings > API"
print_step "4. Copy the following details:"
echo ""

echo -e "${YELLOW}Project URL:${NC}"
echo "   https://[YOUR-PROJECT-REF].supabase.co"
echo ""

echo -e "${YELLOW}Anon (public) key:${NC}"
echo "   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
echo ""

echo -e "${YELLOW}Service role (secret) key:${NC}"
echo "   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
echo ""

print_step "5. Go to Settings > Database"
print_step "6. Copy the connection string"
echo ""

echo -e "${YELLOW}Database URL:${NC}"
echo "   postgresql://postgres:a9kDtuQBiwVnaQE9@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"
echo ""

read -p "Enter your Project URL: " PROJECT_URL
read -p "Enter your Anon key: " ANON_KEY
read -p "Enter your Service role key: " SERVICE_ROLE_KEY
read -p "Enter your Database URL: " DATABASE_URL

# Create environment file
cat > deployment/config/supabase-env.txt << EOF
# Supabase Configuration for ai_lang_platform
# Generated on $(date)

# Project Details
SUPABASE_URL=$PROJECT_URL
SUPABASE_ANON_KEY=$ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=$SERVICE_ROLE_KEY
DATABASE_URL=$DATABASE_URL

# Environment Variables for your app
NEXT_PUBLIC_SUPABASE_URL=$PROJECT_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=$ANON_KEY
EOF

print_success "Project details saved to: deployment/config/supabase-env.txt"
echo ""
print_step "Use these values in your environment variables when you're ready to deploy"
echo ""
print_step "Next steps:"
echo "1. Run the SQL schema: deployment/config/supabase-schema.sql"
echo "2. Run the RLS policies: deployment/config/supabase-rls.sql"
echo "3. Test your connection"
echo "4. Deploy when ready: ./deployment/setup.sh" 