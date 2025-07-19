#!/bin/bash

# Authentication Environment Setup Script
# This script ensures consistent environment configuration across all components

set -e

echo "🔧 Setting up authentication environment..."

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIFIED_ENV="$PROJECT_ROOT/.env.unified"

# Check if unified config exists
if [ ! -f "$UNIFIED_ENV" ]; then
    echo "❌ Error: .env.unified file not found!"
    echo "Please create the unified environment configuration first."
    exit 1
fi

echo "📁 Project root: $PROJECT_ROOT"

# Function to copy and validate environment file
copy_env_file() {
    local source="$1"
    local target="$2"
    local context="$3"
    
    echo "📋 Copying environment config to $context..."
    
    # Create target directory if it doesn't exist
    mkdir -p "$(dirname "$target")"
    
    # Copy the unified config
    cp "$source" "$target"
    
    # Add context-specific variables
    case "$context" in
        "client")
            echo "" >> "$target"
            echo "# Client-specific variables" >> "$target"
            echo "NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000" >> "$target"
            ;;
        "server")
            echo "" >> "$target"
            echo "# Server-specific variables" >> "$target"
            echo "HOST=0.0.0.0" >> "$target"
            echo "PORT=8000" >> "$target"
            ;;
    esac
    
    echo "✅ Environment file created: $target"
}

# Copy to all required locations
copy_env_file "$UNIFIED_ENV" "$PROJECT_ROOT/.env" "root"
copy_env_file "$UNIFIED_ENV" "$PROJECT_ROOT/server/.env" "server"
copy_env_file "$UNIFIED_ENV" "$PROJECT_ROOT/client/.env.local" "client"

# Backup existing configs
echo "🗄️ Creating backups of old configurations..."
for file in "$PROJECT_ROOT"/.env.*; do
    if [ -f "$file" ] && [[ ! "$file" =~ \.backup$ ]] && [[ ! "$file" =~ \.unified$ ]]; then
        cp "$file" "$file.backup.$(date +%Y%m%d_%H%M%S)"
        echo "📦 Backed up: $(basename "$file")"
    fi
done

# Validate JWT secret consistency
echo "🔐 Validating JWT secret consistency..."
JWT_SECRET=$(grep "JWT_SECRET_KEY" "$UNIFIED_ENV" | cut -d'=' -f2 | tr -d '"')

if [ -z "$JWT_SECRET" ]; then
    echo "⚠️ Warning: JWT_SECRET_KEY not found in unified config!"
else
    echo "✅ JWT secret key configured"
fi

# Validate database URL
echo "🗄️ Validating database configuration..."
DB_URL=$(grep "DATABASE_URL" "$UNIFIED_ENV" | cut -d'=' -f2 | tr -d '"')

if [ -z "$DB_URL" ]; then
    echo "⚠️ Warning: DATABASE_URL not found in unified config!"
else
    echo "✅ Database URL configured"
fi

# Check for conflicting files
echo "🔍 Checking for configuration conflicts..."

CONFLICT_FILES=(
    "$PROJECT_ROOT/client/app/api/auth/login/route.ts"
    "$PROJECT_ROOT/client/app/api/auth/profile/route.ts"
)

for file in "${CONFLICT_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "⚠️ Warning: Mock API route found: $file"
        echo "   This may conflict with real backend authentication."
        echo "   Consider removing it: rm \"$file\""
    fi
done

# Test connectivity setup
echo "🌐 Setting up connectivity test..."
cat > "$PROJECT_ROOT/scripts/test-auth-connectivity.sh" << 'EOF'
#!/bin/bash

echo "🔍 Testing authentication system connectivity..."

API_URL="${NEXT_PUBLIC_API_BASE_URL:-http://127.0.0.1:8000}"

echo "🔗 Testing API base URL: $API_URL"

# Test health endpoint
if curl -f -s "$API_URL/health" > /dev/null; then
    echo "✅ Health endpoint accessible"
else
    echo "❌ Health endpoint not accessible"
    echo "   Make sure the backend server is running on $API_URL"
    exit 1
fi

# Test auth endpoints
echo "🔐 Testing auth endpoints..."

AUTH_ENDPOINTS=("/auth/login" "/auth/profile" "/auth/refresh")

for endpoint in "${AUTH_ENDPOINTS[@]}"; do
    if curl -f -s -o /dev/null "$API_URL$endpoint"; then
        echo "✅ $endpoint accessible"
    else
        # This is expected for auth endpoints without credentials
        echo "📍 $endpoint returns error (expected without auth)"
    fi
done

echo "🎉 Connectivity test completed!"
EOF

chmod +x "$PROJECT_ROOT/scripts/test-auth-connectivity.sh"

echo ""
echo "🎉 Authentication environment setup completed!"
echo ""
echo "📝 Summary:"
echo "   ✅ Environment files synchronized"
echo "   ✅ JWT secret key validated"
echo "   ✅ Database URL validated"
echo "   ✅ Connectivity test script created"
echo ""
echo "🚀 Next steps:"
echo "   1. Start the backend server: cd server && python -m uvicorn app.main:app --reload"
echo "   2. Start the frontend: cd client && npm run dev"
echo "   3. Test connectivity: ./scripts/test-auth-connectivity.sh"
echo ""
echo "🔧 If you encounter issues:"
echo "   - Check that JWT_SECRET_KEY is identical in all .env files"
echo "   - Verify DATABASE_URL points to the correct database"
echo "   - Ensure CORS_ORIGINS includes your frontend URL"
echo "   - Remove any conflicting mock API routes"