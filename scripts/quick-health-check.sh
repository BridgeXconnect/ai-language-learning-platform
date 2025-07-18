#!/bin/bash

# Quick Health Check
# Fast validation that basic functionality works after refactoring

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🏥 Quick Health Check"
echo "===================="

cd "$PROJECT_ROOT"

# Check Python syntax
echo "🐍 Checking Python syntax..."
if find server -name "*.py" -exec python3 -m py_compile {} \; > /dev/null 2>&1; then
    echo "  ✅ Python syntax OK"
else
    echo "  ❌ Python syntax errors found"
    exit 1
fi

# Check TypeScript compilation
echo "📜 Checking TypeScript..."
cd client
if npm run build > /dev/null 2>&1; then
    echo "  ✅ TypeScript compilation OK"
else
    echo "  ❌ TypeScript compilation failed"
    exit 1
fi

cd "$PROJECT_ROOT"

# Check environment files
echo "⚙️  Checking environment files..."
required_files=(".env.example" "server/.env.example" "client/.env.example")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file exists"
    else
        echo "  ❌ $file missing"
        exit 1
    fi
done

# Check BMAD framework
echo "🔧 Checking BMAD framework..."
if [ -d ".bmad-core" ]; then
    echo "  ✅ BMAD core directory exists"
else
    echo "  ❌ BMAD core directory missing"
    exit 1
fi

echo ""
echo "✅ Quick health check PASSED"
echo "🔄 Run full validation: python3 scripts/test-refactoring.py"
