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
