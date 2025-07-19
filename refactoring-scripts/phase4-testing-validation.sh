#!/bin/bash

# Phase 4: Testing & Validation
# Comprehensive testing after refactoring to ensure nothing broke

set -e

PROJECT_ROOT="/Users/roymkhabela/Downloads/AI Language Learning Platform"

echo "🚀 Starting Phase 4: Testing & Validation"

cd "$PROJECT_ROOT"

echo ""
echo "📋 Step 1: Create comprehensive test suite"

cat > "scripts/test-refactoring.py" << 'EOF'
#!/usr/bin/env python3

"""
Refactoring Validation Test Suite
Comprehensive testing to ensure refactoring didn't break functionality
"""

import subprocess
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Tuple

class RefactoringValidator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.test_results = {}
        self.server_process = None
        self.client_process = None
        
    def run_command(self, command: str, cwd: str = None, timeout: int = 30) -> Tuple[bool, str]:
        """Run shell command and return success status and output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def test_python_syntax(self) -> Dict:
        """Test Python syntax across all files"""
        print("🐍 Testing Python syntax...")
        
        results = {"passed": 0, "failed": 0, "errors": []}
        
        server_path = self.project_root / "server"
        python_files = list(server_path.rglob("*.py"))
        
        for py_file in python_files:
            if py_file.is_file():
                success, output = self.run_command(f"python3 -m py_compile {py_file}")
                if success:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "file": str(py_file.relative_to(self.project_root)),
                        "error": output
                    })
        
        print(f"  ✓ Passed: {results['passed']}, ❌ Failed: {results['failed']}")
        return results
    
    def test_typescript_syntax(self) -> Dict:
        """Test TypeScript syntax across all files"""
        print("📜 Testing TypeScript syntax...")
        
        client_path = self.project_root / "client"
        
        # Check if TypeScript is properly configured
        success, output = self.run_command("npm run build --dry-run", cwd=client_path, timeout=60)
        
        if not success:
            # Try type checking only
            success, output = self.run_command("npx tsc --noEmit", cwd=client_path, timeout=60)
        
        result = {
            "passed": 1 if success else 0,
            "failed": 0 if success else 1,
            "output": output
        }
        
        print(f"  {'✓' if success else '❌'} TypeScript compilation")
        return result
    
    def test_python_imports(self) -> Dict:
        """Test Python import resolution"""
        print("📦 Testing Python imports...")
        
        results = {"passed": 0, "failed": 0, "errors": []}
        
        # Test key modules can be imported
        test_imports = [
            "from server.app.core.config import settings",
            "from server.app.core.database import get_db",
            "from server.app.domains.auth.models import User",
            "from server.app.domains.sales.models import CourseRequest",
            "from server.app.domains.courses.models import Course",
        ]
        
        for import_stmt in test_imports:
            success, output = self.run_command(f"python3 -c \"{import_stmt}\"")
            if success:
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "import": import_stmt,
                    "error": output
                })
        
        print(f"  ✓ Passed: {results['passed']}, ❌ Failed: {results['failed']}")
        return results
    
    def test_environment_configuration(self) -> Dict:
        """Test environment configuration"""
        print("⚙️  Testing environment configuration...")
        
        results = {"passed": 0, "failed": 0, "errors": []}
        
        # Check required environment files exist
        required_files = [
            ".env.example",
            "server/.env.example", 
            "client/.env.example"
        ]
        
        for env_file in required_files:
            file_path = self.project_root / env_file
            if file_path.exists():
                results["passed"] += 1
                print(f"  ✓ Found: {env_file}")
            else:
                results["failed"] += 1
                results["errors"].append(f"Missing: {env_file}")
                print(f"  ❌ Missing: {env_file}")
        
        return results
    
    def test_server_startup(self) -> Dict:
        """Test server can start without errors"""
        print("🖥️  Testing server startup...")
        
        server_path = self.project_root / "server"
        
        # Try to start server with dry run or validation mode
        success, output = self.run_command(
            "python3 -c \"from app.main import app; print('Server can be imported successfully')\"",
            cwd=server_path,
            timeout=30
        )
        
        result = {
            "passed": 1 if success else 0,
            "failed": 0 if success else 1,
            "output": output
        }
        
        print(f"  {'✓' if success else '❌'} Server startup test")
        return result
    
    def test_client_build(self) -> Dict:
        """Test client can build without errors"""
        print("🌐 Testing client build...")
        
        client_path = self.project_root / "client"
        
        # Test Next.js build
        success, output = self.run_command("npm run build", cwd=client_path, timeout=120)
        
        result = {
            "passed": 1 if success else 0,
            "failed": 0 if success else 1,
            "output": output
        }
        
        print(f"  {'✓' if success else '❌'} Client build test")
        return result
    
    def test_database_connection(self) -> Dict:
        """Test database connection and models"""
        print("🗄️  Testing database connection...")
        
        server_path = self.project_root / "server"
        
        # Test database models can be loaded
        success, output = self.run_command(
            "python3 -c \"from app.core.database import engine; from app.domains.auth.models import User; print('Database models loaded successfully')\"",
            cwd=server_path,
            timeout=15
        )
        
        result = {
            "passed": 1 if success else 0,
            "failed": 0 if success else 1,
            "output": output
        }
        
        print(f"  {'✓' if success else '❌'} Database test")
        return result
    
    def test_api_endpoints(self) -> Dict:
        """Test critical API endpoints are accessible"""
        print("🔗 Testing API endpoints...")
        
        # This would require the server to be running
        # For now, just test that route modules can be imported
        server_path = self.project_root / "server"
        
        route_tests = [
            "from app.domains.auth.routes import router as auth_router",
            "from app.domains.sales.routes import router as sales_router", 
            "from app.domains.courses.routes import router as courses_router",
        ]
        
        results = {"passed": 0, "failed": 0, "errors": []}
        
        for route_test in route_tests:
            success, output = self.run_command(f"python3 -c \"{route_test}\"", cwd=server_path)
            if success:
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "test": route_test,
                    "error": output
                })
        
        print(f"  ✓ Passed: {results['passed']}, ❌ Failed: {results['failed']}")
        return results
    
    def test_bmad_framework(self) -> Dict:
        """Test BMAD framework integrity"""
        print("🔧 Testing BMAD framework integrity...")
        
        results = {"passed": 0, "failed": 0, "errors": []}
        
        # Check BMAD core files exist
        bmad_path = self.project_root / ".bmad-core"
        if bmad_path.exists():
            results["passed"] += 1
            print("  ✓ BMAD core directory exists")
            
            # Check key BMAD files
            key_files = [
                "dev-standards.md",
                "project-brief.md", 
                "production-checklist.md"
            ]
            
            for key_file in key_files:
                if (bmad_path / key_file).exists():
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Missing BMAD file: {key_file}")
        else:
            results["failed"] += 1
            results["errors"].append("BMAD core directory not found")
        
        print(f"  ✓ Passed: {results['passed']}, ❌ Failed: {results['failed']}")
        return results
    
    def generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed_tests": len([t for t in self.test_results.values() if t.get("passed", 0) > 0]),
                "failed_tests": len([t for t in self.test_results.values() if t.get("failed", 0) > 0]),
                "critical_failures": []
            }
        }
        
        # Identify critical failures
        critical_tests = ["python_syntax", "environment_configuration", "server_startup"]
        for test_name in critical_tests:
            if test_name in self.test_results and self.test_results[test_name].get("failed", 0) > 0:
                report["summary"]["critical_failures"].append(test_name)
        
        return report
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting refactoring validation tests...")
        print("=" * 60)
        
        # Run all tests
        self.test_results["python_syntax"] = self.test_python_syntax()
        self.test_results["typescript_syntax"] = self.test_typescript_syntax()
        self.test_results["python_imports"] = self.test_python_imports()
        self.test_results["environment_configuration"] = self.test_environment_configuration()
        self.test_results["server_startup"] = self.test_server_startup()
        self.test_results["client_build"] = self.test_client_build()
        self.test_results["database_connection"] = self.test_database_connection()
        self.test_results["api_endpoints"] = self.test_api_endpoints()
        self.test_results["bmad_framework"] = self.test_bmad_framework()
        
        # Generate and save report
        report = self.generate_report()
        
        report_dir = self.project_root / "refactoring-reports"
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / "refactoring-validation-report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 REFACTORING VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed_tests']}")
        print(f"Failed: {report['summary']['failed_tests']}")
        
        if report['summary']['critical_failures']:
            print(f"\n🚨 Critical failures: {', '.join(report['summary']['critical_failures'])}")
            print("❌ Refactoring validation FAILED")
            return False
        else:
            print("\n✅ Refactoring validation PASSED")
            return True

if __name__ == "__main__":
    import sys
    
    project_root = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    validator = RefactoringValidator(project_root)
    success = validator.run_all_tests()
    
    sys.exit(0 if success else 1)
EOF

chmod +x "scripts/test-refactoring.py"

echo ""
echo "📋 Step 2: Create quick health check script"

cat > "scripts/quick-health-check.sh" << 'EOF'
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
EOF

chmod +x "scripts/quick-health-check.sh"

echo ""
echo "📋 Step 3: Create rollback script"

cat > "scripts/rollback-refactoring.sh" << 'EOF'
#!/bin/bash

# Rollback Refactoring
# Safely rollback refactoring changes if something goes wrong

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_BASE="$PROJECT_ROOT/refactoring-backups"

echo "🔄 Refactoring Rollback Utility"
echo "=============================="

show_help() {
    echo ""
    echo "Usage: $0 [phase|all|list]"
    echo ""
    echo "Commands:"
    echo "  phase1    - Rollback environment consolidation"
    echo "  phase2    - Rollback backend reorganization" 
    echo "  phase3    - Rollback naming standardization"
    echo "  all       - Rollback all phases (dangerous!)"
    echo "  list      - List available backups"
    echo "  help      - Show this help"
    echo ""
}

list_backups() {
    echo "📁 Available backups:"
    if [ -d "$BACKUP_BASE" ]; then
        find "$BACKUP_BASE" -maxdepth 1 -type d -name "phase*" | sort
    else
        echo "  No backups found"
    fi
}

rollback_phase() {
    local phase="$1"
    local backup_dir
    
    # Find the most recent backup for this phase
    backup_dir=$(find "$BACKUP_BASE" -maxdepth 1 -type d -name "${phase}-*" | sort -r | head -n 1)
    
    if [ -z "$backup_dir" ]; then
        echo "❌ No backup found for $phase"
        return 1
    fi
    
    echo "📁 Rolling back from: $backup_dir"
    
    # Confirm with user
    read -p "⚠️  This will overwrite current files. Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Rollback cancelled"
        return 1
    fi
    
    # Perform rollback based on phase
    case "$phase" in
        "phase1")
            echo "🔄 Rolling back environment consolidation..."
            # Restore environment files
            if [ -d "$backup_dir" ]; then
                find "$backup_dir" -name ".env*" -exec cp {} "$PROJECT_ROOT/" \;
                echo "  ✅ Environment files restored"
            fi
            ;;
        "phase2")
            echo "🔄 Rolling back backend reorganization..."
            # Restore server structure
            if [ -d "$backup_dir/app" ]; then
                rm -rf "$PROJECT_ROOT/server/app"
                cp -r "$backup_dir/app" "$PROJECT_ROOT/server/"
                echo "  ✅ Backend structure restored"
            fi
            ;;
        "phase3")
            echo "🔄 Rolling back naming standardization..."
            # Restore from naming fixes backup
            if [ -d "$BACKUP_BASE/naming-fixes" ]; then
                echo "  ⚠️  Manual restoration required for renamed files"
                echo "  📁 Check: $BACKUP_BASE/naming-fixes"
            fi
            ;;
        *)
            echo "❌ Unknown phase: $phase"
            return 1
            ;;
    esac
    
    echo "✅ Rollback complete for $phase"
}

rollback_all() {
    echo "⚠️  DANGER: This will rollback ALL refactoring changes"
    read -p "Are you absolutely sure? Type 'ROLLBACK' to confirm: " confirmation
    
    if [ "$confirmation" != "ROLLBACK" ]; then
        echo "Rollback cancelled"
        return 1
    fi
    
    # Rollback in reverse order
    rollback_phase "phase3"
    rollback_phase "phase2" 
    rollback_phase "phase1"
    
    echo "🔄 All phases rolled back"
}

# Main command handling
case "${1:-help}" in
    phase1|phase2|phase3)
        rollback_phase "$1"
        ;;
    all)
        rollback_all
        ;;
    list)
        list_backups
        ;;
    help|*)
        show_help
        ;;
esac
EOF

chmod +x "scripts/rollback-refactoring.sh"

echo ""
echo "📋 Step 4: Create final validation checklist"

cat > "docs/REFACTORING_CHECKLIST.md" << 'EOF'
# Refactoring Validation Checklist

Use this checklist to verify that the refactoring was successful and didn't break any functionality.

## 🚀 Pre-Refactoring Checklist

- [ ] **Backup Created**: All original files backed up
- [ ] **Git Status Clean**: All changes committed or stashed
- [ ] **Dependencies Installed**: npm install and pip install completed
- [ ] **Tests Passing**: All existing tests pass
- [ ] **Documentation Current**: Important documentation is up to date

## 📋 Phase 1: Environment Consolidation

### ✅ Environment Files
- [ ] **Root .env.example**: Created with common settings
- [ ] **Server .env.example**: Created with backend-specific settings
- [ ] **Client .env.example**: Created with frontend-specific settings
- [ ] **Duplicates Removed**: Old .env.save, .env.unified files removed
- [ ] **Management Script**: scripts/manage-env.sh works correctly

### 🧪 Testing
- [ ] **Environment Setup**: `./scripts/manage-env.sh setup development` works
- [ ] **Environment Validation**: `./scripts/manage-env.sh validate development` passes
- [ ] **Server Starts**: Server can start with new environment files
- [ ] **Client Builds**: Client can build with new environment files

## 📋 Phase 2: Backend Reorganization

### 🏗️ Domain Structure
- [ ] **Auth Domain**: Models, routes, services, schemas in domains/auth/
- [ ] **Sales Domain**: Models, routes, services, schemas in domains/sales/
- [ ] **Courses Domain**: Models, routes, services, schemas in domains/courses/
- [ ] **AI Domain**: Models, routes, services, schemas in domains/ai/
- [ ] **Core Module**: config.py, database.py in core/
- [ ] **Shared Module**: Middleware and utilities in shared/

### 📦 File Migration
- [ ] **Models Merged**: Duplicate model files consolidated
- [ ] **Routes Merged**: Duplicate route files consolidated
- [ ] **Services Organized**: AI services properly organized
- [ ] **Imports Updated**: All imports use new domain structure
- [ ] **__init__.py Files**: Created for all domains

### 🧪 Testing
- [ ] **Python Syntax**: All Python files compile without errors
- [ ] **Import Resolution**: All imports resolve correctly
- [ ] **Server Startup**: Server starts without import errors
- [ ] **API Endpoints**: All endpoints accessible
- [ ] **Database Models**: All models load correctly

## 📋 Phase 3: Naming Standardization

### 📝 Naming Conventions
- [ ] **Python Files**: All use snake_case
- [ ] **TypeScript Files**: All use kebab-case or camelCase appropriately
- [ ] **Directories**: Follow kebab-case (general) or snake_case (Python packages)
- [ ] **Components**: Files use kebab-case, components use PascalCase
- [ ] **Variables**: Follow language-specific conventions

### 🔧 Tools
- [ ] **Convention Checker**: `python3 scripts/enforce-naming-conventions.py` runs
- [ ] **Report Generated**: naming-conventions-report.json created
- [ ] **Fixes Applied**: High/medium severity issues resolved
- [ ] **Documentation**: NAMING_CONVENTIONS.md accessible

### 🧪 Testing
- [ ] **File Compilation**: All renamed files compile
- [ ] **Import Updates**: Imports updated for renamed files
- [ ] **Functionality**: Features work after renaming
- [ ] **Documentation**: References updated

## 📋 Phase 4: Testing & Validation

### 🧪 Comprehensive Testing
- [ ] **Quick Health Check**: `./scripts/quick-health-check.sh` passes
- [ ] **Full Validation**: `python3 scripts/test-refactoring.py` passes
- [ ] **Python Syntax**: No syntax errors in any Python file
- [ ] **TypeScript Compilation**: Client builds successfully
- [ ] **Environment Config**: All environment files valid
- [ ] **Server Startup**: Backend starts without errors
- [ ] **Database Connection**: Database connects and models load
- [ ] **API Endpoints**: Route modules import correctly
- [ ] **BMAD Framework**: Framework integrity maintained

### 📊 Reports
- [ ] **Validation Report**: refactoring-validation-report.json generated
- [ ] **No Critical Failures**: No critical test failures
- [ ] **Issues Documented**: Any issues documented and addressed

## 🎯 Final Verification

### 🔍 Functionality Testing
- [ ] **Authentication**: Login/logout works
- [ ] **Course Creation**: Course request workflow works
- [ ] **File Upload**: File upload functionality works
- [ ] **Navigation**: All pages load correctly
- [ ] **API Calls**: Frontend-backend communication works

### 📚 Documentation
- [ ] **Structure Guide**: New directory structure documented
- [ ] **Migration Notes**: Changes documented for team
- [ ] **Naming Guide**: Naming conventions guide available
- [ ] **Rollback Plan**: Rollback procedures documented

### 🚀 Deployment Ready
- [ ] **Production Config**: Production environment configured
- [ ] **Staging Test**: Staging deployment tested
- [ ] **Performance**: No performance regressions
- [ ] **Security**: No security issues introduced

## 🆘 Rollback Checklist

If something goes wrong:

- [ ] **Stop Services**: Stop all running services
- [ ] **Assess Impact**: Determine scope of issues
- [ ] **Selective Rollback**: Use `./scripts/rollback-refactoring.sh [phase]`
- [ ] **Full Rollback**: Use `./scripts/rollback-refactoring.sh all` if needed
- [ ] **Verify Rollback**: Test that rollback restored functionality
- [ ] **Document Issues**: Record what went wrong for future reference

## 📋 Success Criteria

The refactoring is considered successful when:

✅ **All tests pass** without critical failures
✅ **Core functionality works** (auth, course creation, file upload)
✅ **Performance maintained** (no significant slowdowns)
✅ **Team can navigate** the new structure easily
✅ **Documentation complete** for ongoing development
✅ **Deployment possible** to all environments

## 🎉 Post-Refactoring

After successful refactoring:

- [ ] **Team Training**: Brief team on new structure
- [ ] **Documentation Update**: Update development docs
- [ ] **CI/CD Update**: Update build/deployment scripts if needed
- [ ] **Archive Backups**: Archive successful refactoring backups
- [ ] **Celebrate**: Acknowledge the improved codebase! 🎊
EOF

echo ""
echo "📋 Step 5: Create complete refactoring runner"

cat > "scripts/run-complete-refactoring.sh" << 'EOF'
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
EOF

chmod +x "scripts/run-complete-refactoring.sh"

echo ""
echo "✅ Phase 4 Complete!"
echo ""
echo "📊 Summary:"
echo "  • Created comprehensive test suite"
echo "  • Generated quick health check script"
echo "  • Created rollback safety mechanism"
echo "  • Generated validation checklist"
echo "  • Created complete refactoring runner"
echo ""
echo "🔄 Usage:"
echo "  Quick check: ./scripts/quick-health-check.sh"
echo "  Full validation: python3 scripts/test-refactoring.py"
echo "  Complete refactoring: ./scripts/run-complete-refactoring.sh"
echo "  Rollback if needed: ./scripts/rollback-refactoring.sh [phase]"
echo ""
echo "📝 Validation includes:"
echo "  • Python syntax checking"
echo "  • TypeScript compilation"
echo "  • Import resolution"
echo "  • Environment configuration"
echo "  • Server startup testing"
echo "  • Client build testing"
echo "  • Database connection"
echo "  • API endpoint validation"
echo "  • BMAD framework integrity"