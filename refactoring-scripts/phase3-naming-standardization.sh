#!/bin/bash

# Phase 3: Naming Convention Standardization
# Standardize naming across the entire codebase

set -e

PROJECT_ROOT="/Users/roymkhabela/Downloads/AI Language Learning Platform"
BACKUP_DIR="$PROJECT_ROOT/refactoring-backups/phase3-$(date +%Y%m%d_%H%M%S)"

echo "🚀 Starting Phase 3: Naming Convention Standardization"
echo "📁 Backup directory: $BACKUP_DIR"

mkdir -p "$BACKUP_DIR"
cd "$PROJECT_ROOT"

# Function to backup file before renaming
backup_and_rename() {
    local old_name="$1"
    local new_name="$2"
    
    if [ -e "$old_name" ]; then
        # Create backup
        cp -r "$old_name" "$BACKUP_DIR/"
        
        # Rename
        mv "$old_name" "$new_name"
        echo "✓ Renamed: $(basename "$old_name") → $(basename "$new_name")"
    fi
}

echo ""
echo "📋 Step 1: Standardize directory names (kebab-case)"

# Directories that need renaming (if they exist and don't follow kebab-case)
# Most directories already follow good conventions, but let's check for any outliers

# Check for any CamelCase or snake_case directories that should be kebab-case
find . -type d -name "*_*" | grep -E "(components|pages|utils|scripts)" | while read -r dir; do
    if [[ "$dir" != *"node_modules"* ]] && [[ "$dir" != *".git"* ]] && [[ "$dir" != *"__pycache__"* ]]; then
        new_dir=$(echo "$dir" | sed 's/_/-/g')
        if [ "$dir" != "$new_dir" ]; then
            backup_and_rename "$dir" "$new_dir"
        fi
    fi
done

echo ""
echo "📋 Step 2: Create naming convention enforcement script"

cat > "scripts/enforce-naming-conventions.py" << 'EOF'
#!/usr/bin/env python3

"""
Naming Convention Enforcement Script
Checks and fixes naming conventions across the codebase
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

class NamingConventionEnforcer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.violations = []
        self.fixes = []
        
    def snake_case(self, name: str) -> str:
        """Convert to snake_case"""
        # Insert underscore before uppercase letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def kebab_case(self, name: str) -> str:
        """Convert to kebab-case"""
        return self.snake_case(name).replace('_', '-')
    
    def camel_case(self, name: str) -> str:
        """Convert to camelCase"""
        components = name.split('_')
        return components[0] + ''.join(x.capitalize() for x in components[1:])
    
    def pascal_case(self, name: str) -> str:
        """Convert to PascalCase"""
        return ''.join(x.capitalize() for x in name.split('_'))
    
    def check_python_files(self):
        """Check Python file naming conventions (snake_case)"""
        print("🐍 Checking Python file naming...")
        
        for py_file in self.project_root.rglob("*.py"):
            if py_file.is_file() and not any(skip in str(py_file) for skip in ['.git', '__pycache__', 'node_modules']):
                filename = py_file.stem
                
                # Skip special files
                if filename.startswith('__') and filename.endswith('__'):
                    continue
                
                expected = self.snake_case(filename)
                if filename != expected and not self.is_snake_case(filename):
                    self.violations.append({
                        'type': 'python_file',
                        'path': str(py_file),
                        'current': filename,
                        'expected': expected,
                        'severity': 'medium'
                    })
    
    def check_directory_names(self):
        """Check directory naming conventions (kebab-case for most, snake_case for Python packages)"""
        print("📁 Checking directory naming...")
        
        for directory in self.project_root.rglob("*"):
            if (directory.is_dir() and 
                not any(skip in str(directory) for skip in ['.git', '__pycache__', 'node_modules', '.next'])):
                
                dir_name = directory.name
                
                # Skip special directories
                if dir_name.startswith('.') or dir_name.startswith('__'):
                    continue
                
                # Python packages should use snake_case
                if self.is_python_package(directory):
                    expected = self.snake_case(dir_name)
                    if dir_name != expected and not self.is_snake_case(dir_name):
                        self.violations.append({
                            'type': 'python_package_dir',
                            'path': str(directory),
                            'current': dir_name,
                            'expected': expected,
                            'severity': 'high'
                        })
                else:
                    # Other directories should use kebab-case
                    expected = self.kebab_case(dir_name)
                    if dir_name != expected and not self.is_kebab_case(dir_name):
                        self.violations.append({
                            'type': 'directory',
                            'path': str(directory),
                            'current': dir_name,
                            'expected': expected,
                            'severity': 'low'
                        })
    
    def check_typescript_files(self):
        """Check TypeScript/JavaScript file naming conventions (kebab-case or camelCase)"""
        print("📜 Checking TypeScript/JavaScript file naming...")
        
        for ts_file in self.project_root.rglob("*.{ts,tsx,js,jsx}"):
            if ts_file.is_file() and not any(skip in str(ts_file) for skip in ['.git', 'node_modules', '.next']):
                filename = ts_file.stem
                
                # Components should be PascalCase, others should be kebab-case or camelCase
                if self.is_component_file(ts_file):
                    if not self.is_pascal_case(filename) and not self.is_kebab_case(filename):
                        expected = self.kebab_case(filename)
                        self.violations.append({
                            'type': 'component_file',
                            'path': str(ts_file),
                            'current': filename,
                            'expected': expected,
                            'severity': 'medium'
                        })
                else:
                    # Utility files should be kebab-case
                    if not self.is_kebab_case(filename) and not self.is_camel_case(filename):
                        expected = self.kebab_case(filename)
                        self.violations.append({
                            'type': 'typescript_file',
                            'path': str(ts_file),
                            'current': filename,
                            'expected': expected,
                            'severity': 'low'
                        })
    
    def is_snake_case(self, name: str) -> bool:
        """Check if name follows snake_case"""
        return re.match(r'^[a-z][a-z0-9_]*$', name) is not None
    
    def is_kebab_case(self, name: str) -> bool:
        """Check if name follows kebab-case"""
        return re.match(r'^[a-z][a-z0-9-]*$', name) is not None
    
    def is_camel_case(self, name: str) -> bool:
        """Check if name follows camelCase"""
        return re.match(r'^[a-z][a-zA-Z0-9]*$', name) is not None
    
    def is_pascal_case(self, name: str) -> bool:
        """Check if name follows PascalCase"""
        return re.match(r'^[A-Z][a-zA-Z0-9]*$', name) is not None
    
    def is_python_package(self, directory: Path) -> bool:
        """Check if directory is a Python package"""
        return (directory / '__init__.py').exists()
    
    def is_component_file(self, file_path: Path) -> bool:
        """Check if file is a React component"""
        return (file_path.suffix in ['.tsx', '.jsx'] and 
                'components' in str(file_path).lower())
    
    def generate_fixes(self):
        """Generate fix commands for violations"""
        print("🔧 Generating fixes...")
        
        for violation in self.violations:
            if violation['severity'] in ['high', 'medium']:
                old_path = Path(violation['path'])
                new_name = violation['expected'] + old_path.suffix
                new_path = old_path.parent / new_name
                
                self.fixes.append({
                    'type': 'rename',
                    'old_path': str(old_path),
                    'new_path': str(new_path),
                    'command': f"mv '{old_path}' '{new_path}'"
                })
    
    def save_report(self):
        """Save violation report"""
        report = {
            'violations': self.violations,
            'fixes': self.fixes,
            'summary': {
                'total_violations': len(self.violations),
                'high_severity': len([v for v in self.violations if v['severity'] == 'high']),
                'medium_severity': len([v for v in self.violations if v['severity'] == 'medium']),
                'low_severity': len([v for v in self.violations if v['severity'] == 'low']),
            }
        }
        
        report_file = self.project_root / 'refactoring-reports' / 'naming-conventions-report.json'
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Report saved: {report_file}")
        return report
    
    def print_summary(self, report: Dict):
        """Print summary of findings"""
        print("\n📊 Naming Convention Analysis Summary:")
        print(f"  Total violations: {report['summary']['total_violations']}")
        print(f"  High severity: {report['summary']['high_severity']}")
        print(f"  Medium severity: {report['summary']['medium_severity']}")
        print(f"  Low severity: {report['summary']['low_severity']}")
        
        if report['summary']['high_severity'] > 0:
            print("\n🚨 High severity violations (require fixing):")
            for violation in self.violations:
                if violation['severity'] == 'high':
                    print(f"  • {violation['current']} → {violation['expected']} ({violation['type']})")
        
        if len(self.fixes) > 0:
            print(f"\n🔧 Generated {len(self.fixes)} automated fixes")
    
    def run_analysis(self):
        """Run complete naming convention analysis"""
        print("🚀 Starting naming convention analysis...")
        
        self.check_python_files()
        self.check_directory_names()
        self.check_typescript_files()
        self.generate_fixes()
        
        report = self.save_report()
        self.print_summary(report)
        
        return report

if __name__ == "__main__":
    import sys
    
    project_root = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    enforcer = NamingConventionEnforcer(project_root)
    enforcer.run_analysis()
EOF

chmod +x "scripts/enforce-naming-conventions.py"

echo ""
echo "📋 Step 3: Create naming convention documentation"

cat > "docs/NAMING_CONVENTIONS.md" << 'EOF'
# Naming Conventions Guide

This document outlines the standardized naming conventions for the AI Language Learning Platform.

## Overview

Consistent naming conventions improve code readability, maintainability, and developer experience. This project uses different conventions based on the technology and context.

## File and Directory Naming

### Python Files
- **Convention**: `snake_case`
- **Examples**: 
  - ✅ `auth_service.py`
  - ✅ `course_generation.py`
  - ❌ `authService.py`
  - ❌ `course-generation.py`

### TypeScript/JavaScript Files
- **Convention**: `kebab-case` (preferred) or `camelCase`
- **Examples**:
  - ✅ `auth-service.ts`
  - ✅ `course-request-wizard.tsx`
  - ✅ `useAuth.ts` (hooks)
  - ❌ `AuthService.ts`
  - ❌ `course_request_wizard.tsx`

### React Components
- **Convention**: `kebab-case` for files, `PascalCase` for components
- **Examples**:
  - ✅ File: `course-request-wizard.tsx`, Component: `CourseRequestWizard`
  - ✅ File: `auth-context.tsx`, Component: `AuthProvider`
  - ❌ File: `CourseRequestWizard.tsx`

### Directories
- **General**: `kebab-case`
- **Python Packages**: `snake_case` (with `__init__.py`)
- **Examples**:
  - ✅ `course-manager/`
  - ✅ `auth_service/` (Python package)
  - ✅ `ai-services/`
  - ❌ `courseManager/`
  - ❌ `AI_Services/`

## Code Naming

### Python
- **Variables**: `snake_case`
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

```python
# ✅ Good
class UserService:
    MAX_RETRY_ATTEMPTS = 3
    
    def __init__(self):
        self._connection = None
    
    def create_user(self, user_data: dict) -> User:
        return User(**user_data)

# ❌ Bad  
class userService:
    maxRetryAttempts = 3
    
    def createUser(self, userData: dict) -> User:
        return User(**userData)
```

### TypeScript/JavaScript
- **Variables**: `camelCase`
- **Functions**: `camelCase`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Types/Interfaces**: `PascalCase`
- **Enums**: `PascalCase`

```typescript
// ✅ Good
interface UserData {
  firstName: string;
  lastName: string;
}

class AuthService {
  private readonly MAX_RETRY_ATTEMPTS = 3;
  
  async authenticateUser(userData: UserData): Promise<User> {
    return this.processUser(userData);
  }
}

// ❌ Bad
interface user_data {
  first_name: string;
  last_name: string;
}

class auth_service {
  private readonly max_retry_attempts = 3;
  
  async authenticate_user(user_data: user_data): Promise<User> {
    return this.process_user(user_data);
  }
}
```

## Database Naming

### Tables
- **Convention**: `snake_case`
- **Examples**: `users`, `course_requests`, `lesson_content`

### Columns
- **Convention**: `snake_case`
- **Examples**: `user_id`, `created_at`, `first_name`

### Indexes
- **Convention**: `idx_{table}_{columns}`
- **Examples**: `idx_users_email`, `idx_course_requests_status`

## API Naming

### Endpoints
- **Convention**: `kebab-case` with clear resource hierarchy
- **Examples**:
  - ✅ `/api/course-requests`
  - ✅ `/api/users/{id}/courses`
  - ✅ `/api/auth/login`
  - ❌ `/api/courseRequests`
  - ❌ `/api/users/{id}/getCourses`

### JSON Fields
- **Convention**: `camelCase` for frontend APIs, `snake_case` for internal APIs
- **Examples**:
  ```json
  {
    "userId": 123,
    "firstName": "John",
    "createdAt": "2023-01-01T00:00:00Z"
  }
  ```

## Environment Variables

### Convention
- **Format**: `UPPER_SNAKE_CASE`
- **Grouping**: Use prefixes for related variables

### Examples
```bash
# ✅ Good
DATABASE_URL=postgresql://...
DATABASE_POOL_SIZE=10
JWT_SECRET_KEY=...
JWT_EXPIRE_MINUTES=30
OPENAI_API_KEY=...
SMTP_HOST=...
SMTP_PORT=587

# ❌ Bad
databaseUrl=postgresql://...
DatabasePoolSize=10
jwt-secret-key=...
openai_api_key=...
```

## Configuration Files

### File Names
- **Convention**: `kebab-case` with descriptive names
- **Examples**:
  - ✅ `next.config.mjs`
  - ✅ `tailwind.config.ts`
  - ✅ `docker-compose.yml`
  - ❌ `nextConfig.mjs`
  - ❌ `tailwind_config.ts`

## Git Branches

### Convention
- **Format**: `{type}/{short-description}`
- **Types**: `feature`, `fix`, `refactor`, `docs`, `test`

### Examples
```bash
# ✅ Good
feature/user-authentication
fix/course-generation-bug
refactor/domain-structure
docs/api-documentation

# ❌ Bad
userAuthentication
courseGenerationBugFix
Domain_Structure_Refactor
```

## Commit Messages

### Convention
- **Format**: `{type}: {description}`
- **Types**: `feat`, `fix`, `refactor`, `docs`, `test`, `style`, `chore`

### Examples
```bash
# ✅ Good
feat: add user authentication system
fix: resolve course generation timeout
refactor: reorganize backend domain structure
docs: update API documentation

# ❌ Bad
Added user authentication
Fixed bug
Refactoring
Updated docs
```

## Enforcement

Use the naming convention checker:

```bash
# Check current naming conventions
python3 scripts/enforce-naming-conventions.py

# View detailed report
cat refactoring-reports/naming-conventions-report.json
```

## Migration Guide

When renaming files or directories:

1. **Backup**: Always backup before renaming
2. **Update Imports**: Update all import statements
3. **Update Documentation**: Update any documentation references
4. **Test**: Verify functionality after changes
5. **Commit**: Commit changes with descriptive message

## Exceptions

Some exceptions to these rules are acceptable:

- **Third-party dependencies**: Keep original naming
- **Generated files**: Follow generator conventions
- **Legacy systems**: Gradual migration is acceptable
- **Industry standards**: Follow established patterns (e.g., `README.md`)

## Tools

- **Python**: Use `pylint` and `black` for formatting
- **TypeScript**: Use `eslint` and `prettier` for formatting
- **Naming Checker**: Use provided script for validation
EOF

echo ""
echo "📋 Step 4: Create automatic naming fix script"

cat > "scripts/apply-naming-fixes.sh" << 'EOF'
#!/bin/bash

# Apply Naming Convention Fixes
# Safely applies the fixes generated by the naming convention checker

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_FILE="$PROJECT_ROOT/refactoring-reports/naming-conventions-report.json"

echo "🔧 Applying naming convention fixes..."

if [ ! -f "$REPORT_FILE" ]; then
    echo "❌ Report file not found. Run naming convention check first:"
    echo "   python3 scripts/enforce-naming-conventions.py"
    exit 1
fi

# Parse report and apply fixes
python3 << EOF
import json
import os
import shutil
from pathlib import Path

report_file = "$REPORT_FILE"
project_root = "$PROJECT_ROOT"

with open(report_file, 'r') as f:
    report = json.load(f)

fixes = report.get('fixes', [])
applied = 0
failed = 0

print(f"📝 Found {len(fixes)} fixes to apply...")

for fix in fixes:
    try:
        old_path = Path(fix['old_path'])
        new_path = Path(fix['new_path'])
        
        if old_path.exists():
            # Create backup
            backup_dir = Path(project_root) / "refactoring-backups" / "naming-fixes"
            backup_dir.mkdir(exist_ok=True, parents=True)
            backup_file = backup_dir / old_path.name
            shutil.copy2(old_path, backup_file)
            
            # Apply fix
            old_path.rename(new_path)
            print(f"  ✓ {old_path.name} → {new_path.name}")
            applied += 1
        else:
            print(f"  ⚠️  File not found: {old_path}")
            
    except Exception as e:
        print(f"  ❌ Failed to rename {fix['old_path']}: {e}")
        failed += 1

print(f"\n📊 Applied {applied} fixes")
if failed > 0:
    print(f"⚠️  {failed} fixes failed")
EOF

echo ""
echo "✅ Naming fixes applied!"
echo "🔄 Next steps:"
echo "  1. Update import statements in affected files"
echo "  2. Run tests to verify functionality"
echo "  3. Update any documentation references"
EOF

chmod +x "scripts/apply-naming-fixes.sh"

echo ""
echo "✅ Phase 3 Complete!"
echo ""
echo "📊 Summary:"
echo "  • Created naming convention enforcement tools"
echo "  • Generated comprehensive naming guide"
echo "  • Created automated fixing scripts"
echo "  • Established standards for all file types"
echo ""
echo "🔄 Next Steps:"
echo "  1. Run: python3 scripts/enforce-naming-conventions.py"
echo "  2. Review: refactoring-reports/naming-conventions-report.json"
echo "  3. Apply: ./scripts/apply-naming-fixes.sh"
echo "  4. Read: docs/NAMING_CONVENTIONS.md"
echo ""
echo "📝 Naming Standards:"
echo "  • Python files: snake_case"
echo "  • TypeScript files: kebab-case"
echo "  • Directories: kebab-case (general), snake_case (Python packages)"
echo "  • Components: kebab-case files, PascalCase components"
echo "  • Variables: snake_case (Python), camelCase (TypeScript)"