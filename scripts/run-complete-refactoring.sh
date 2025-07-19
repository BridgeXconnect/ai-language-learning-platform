#!/bin/bash

# Complete Refactoring Runner
# Runs all refactoring phases with validation

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_DIR="$PROJECT_ROOT/refactoring-scripts"

echo "🚀 AI Language Learning Platform - Complete Refactoring"
echo "====================================================="

cd "$PROJECT_ROOT"

# Check prerequisites
echo "🔍 Checking prerequisites..."
if [ ! -d ".git" ]; then
    echo "❌ Not a git repository. Please initialize git first."
    exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Git working directory not clean. Commit or stash changes first."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run phases
echo ""
echo "📋 Running Phase 1: Environment Consolidation..."
bash "$SCRIPT_DIR/phase1-environment-consolidation.sh"

echo ""
echo "📋 Running Phase 2: Backend Reorganization..."
bash "$SCRIPT_DIR/phase2-backend-reorganization.sh"

echo ""
echo "📋 Running Phase 3: Naming Standardization..."
bash "$SCRIPT_DIR/phase3-naming-standardization.sh"

echo ""
echo "📋 Running Phase 4: Testing & Validation..."
bash "$SCRIPT_DIR/phase4-testing-validation.sh"

echo ""
echo "🧪 Running comprehensive validation..."
if python3 scripts/test-refactoring.py; then
    echo ""
    echo "🎉 REFACTORING COMPLETE!"
    echo "======================"
    echo ""
    echo "✅ All phases completed successfully"
    echo "✅ All validation tests passed"
    echo "✅ Codebase is now organized and maintainable"
    echo ""
    echo "📚 Next steps:"
    echo "  1. Review docs/REFACTORING_CHECKLIST.md"
    echo "  2. Update team documentation"
    echo "  3. Test deployment to staging"
    echo "  4. Brief team on new structure"
    echo ""
    echo "📁 New structure overview:"
    echo "  • Consolidated environment configuration"
    echo "  • Domain-based backend organization"
    echo "  • Standardized naming conventions"
    echo "  • Comprehensive testing and validation"
else
    echo ""
    echo "❌ REFACTORING FAILED"
    echo "==================="
    echo ""
    echo "❌ Validation tests failed"
    echo "🔄 Consider using rollback script if needed"
    echo "📊 Check refactoring-reports/ for details"
    echo ""
    echo "🆘 Rollback options:"
    echo "  ./scripts/rollback-refactoring.sh list"
    echo "  ./scripts/rollback-refactoring.sh [phase]"
    echo "  ./scripts/rollback-refactoring.sh all"
fi
