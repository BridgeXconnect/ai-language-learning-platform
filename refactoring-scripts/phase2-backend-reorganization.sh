#!/bin/bash

# Phase 2: Backend Domain Reorganization
# Transform type-based structure to domain-based structure

set -e

PROJECT_ROOT="/Users/roymkhabela/Downloads/AI Language Learning Platform"
BACKUP_DIR="$PROJECT_ROOT/refactoring-backups/phase2-$(date +%Y%m%d_%H%M%S)"

echo "🚀 Starting Phase 2: Backend Domain Reorganization"
echo "📁 Backup directory: $BACKUP_DIR"

# Create backup and new structure
mkdir -p "$BACKUP_DIR"
cd "$PROJECT_ROOT"

# Function to backup directory
backup_directory() {
    local dir="$1"
    if [ -d "$dir" ]; then
        cp -r "$dir" "$BACKUP_DIR/"
        echo "✓ Backed up directory: $dir"
    fi
}

# Function to create domain structure
create_domain_structure() {
    local domain="$1"
    local base_path="server/app/domains/$domain"
    
    mkdir -p "$base_path"
    touch "$base_path/__init__.py"
    touch "$base_path/models.py"
    touch "$base_path/routes.py"
    touch "$base_path/services.py"
    touch "$base_path/schemas.py"
    
    echo "✓ Created domain structure: $domain"
}

echo ""
echo "📋 Step 1: Backup existing backend structure"
backup_directory "server/app"

echo ""
echo "📋 Step 2: Create new domain-based structure"

# Create core structure
mkdir -p "server/app/core"
mkdir -p "server/app/domains"
mkdir -p "server/app/shared/middleware"
mkdir -p "server/app/shared/utils"
mkdir -p "server/app/shared/exceptions"

# Create domain directories
domains=("auth" "sales" "courses" "ai" "users")
for domain in "${domains[@]}"; do
    create_domain_structure "$domain"
done

# Create AI services subdirectory
mkdir -p "server/app/domains/ai/services"

echo ""
echo "📋 Step 3: Generate domain migration mapping"

# Create domain migration mapping
cat > "scripts/domain-migration-map.json" << 'EOF'
{
  "file_migrations": {
    "models": {
      "user.py": "domains/auth/models.py",
      "server_models_user.py": "domains/auth/models.py",
      "sales.py": "domains/sales/models.py",
      "course.py": "domains/courses/models.py",
      "server_models_course.py": "domains/courses/models.py"
    },
    "routes": {
      "auth_routes.py": "domains/auth/routes.py",
      "server_routes_auth.py": "domains/auth/routes.py",
      "sales_routes.py": "domains/sales/routes.py",
      "server_routes_sales.py": "domains/sales/routes.py",
      "course_routes.py": "domains/courses/routes.py",
      "ai_routes.py": "domains/ai/routes.py",
      "agent_routes.py": "domains/ai/routes.py"
    },
    "services": {
      "auth_service.py": "domains/auth/services.py",
      "user_service.py": "domains/auth/services.py",
      "sales_service.py": "domains/sales/services.py",
      "course_service.py": "domains/courses/services.py",
      "course_generation_service.py": "domains/courses/services.py",
      "ai_service.py": "domains/ai/services/core.py",
      "enhanced_ai_service.py": "domains/ai/services/enhanced.py",
      "ai_tutor_service.py": "domains/ai/services/tutor.py",
      "ai_content_service.py": "domains/ai/services/content.py",
      "ai_assessment_service.py": "domains/ai/services/assessment.py"
    },
    "schemas": {
      "auth.py": "domains/auth/schemas.py",
      "sales.py": "domains/sales/schemas.py",
      "course.py": "domains/courses/schemas.py",
      "ai.py": "domains/ai/schemas.py"
    }
  },
  "core_files": {
    "config.py": "core/config.py",
    "database.py": "core/database.py"
  },
  "shared_files": {
    "middleware/auth_middleware.py": "shared/middleware/auth.py"
  }
}
EOF

echo ""
echo "📋 Step 4: Create domain migration script"

cat > "scripts/migrate-to-domains.py" << 'EOF'
#!/usr/bin/env python3

"""
Domain Migration Script
Migrates files from type-based to domain-based structure
"""

import json
import os
import shutil
import re
from pathlib import Path
from typing import Dict, List

class DomainMigrator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.server_path = self.project_root / "server" / "app"
        self.migration_map = self.load_migration_map()
        
    def load_migration_map(self) -> Dict:
        """Load migration mapping from JSON file"""
        map_file = self.project_root / "scripts" / "domain-migration-map.json"
        with open(map_file, 'r') as f:
            return json.load(f)
    
    def merge_files(self, source_files: List[Path], target_file: Path, domain: str):
        """Merge multiple source files into a single target file"""
        print(f"📝 Merging files for {domain} domain...")
        
        merged_content = []
        imports = set()
        class_definitions = []
        function_definitions = []
        
        # Header comment
        merged_content.append(f'"""')
        merged_content.append(f'{domain.capitalize()} Domain - {target_file.name.replace(".py", "").title()}')
        merged_content.append(f'Consolidated from: {", ".join([f.name for f in source_files])}')
        merged_content.append(f'"""')
        merged_content.append('')
        
        for source_file in source_files:
            if not source_file.exists():
                continue
                
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract imports
                import_lines = re.findall(r'^(import .*|from .* import .*)$', content, re.MULTILINE)
                imports.update(import_lines)
                
                # Extract class definitions
                classes = re.findall(r'^class .*?(?=^class |\Z)', content, re.MULTILINE | re.DOTALL)
                class_definitions.extend(classes)
                
                # Extract function definitions (not in classes)
                functions = re.findall(r'^def .*?(?=^def |^class |\Z)', content, re.MULTILINE | re.DOTALL)
                function_definitions.extend(functions)
                
                print(f"  ✓ Processed: {source_file.name}")
                
            except Exception as e:
                print(f"  ⚠️  Error processing {source_file}: {e}")
        
        # Build merged content
        if imports:
            merged_content.extend(sorted(imports))
            merged_content.append('')
        
        if class_definitions:
            merged_content.extend(class_definitions)
            merged_content.append('')
            
        if function_definitions:
            merged_content.extend(function_definitions)
        
        # Write merged file
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(merged_content))
        
        print(f"  ✅ Created: {target_file}")
    
    def migrate_domain_files(self):
        """Migrate files to domain structure"""
        
        for file_type, mappings in self.migration_map['file_migrations'].items():
            print(f"\n📂 Migrating {file_type}...")
            
            # Group by target file
            target_groups = {}
            for source, target in mappings.items():
                if target not in target_groups:
                    target_groups[target] = []
                target_groups[target].append(source)
            
            for target_path, source_files in target_groups.items():
                source_paths = [self.server_path / file_type / f for f in source_files]
                target_file = self.server_path / target_path
                domain = target_path.split('/')[1]  # Extract domain name
                
                existing_sources = [p for p in source_paths if p.exists()]
                if existing_sources:
                    self.merge_files(existing_sources, target_file, domain)
    
    def migrate_core_files(self):
        """Migrate core configuration files"""
        print(f"\n🔧 Migrating core files...")
        
        for source, target in self.migration_map['core_files'].items():
            source_path = self.server_path / source
            target_path = self.server_path / target
            
            if source_path.exists():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
                print(f"  ✓ Moved: {source} → {target}")
    
    def migrate_shared_files(self):
        """Migrate shared utilities and middleware"""
        print(f"\n🔗 Migrating shared files...")
        
        for source, target in self.migration_map['shared_files'].items():
            source_path = self.server_path / source
            target_path = self.server_path / target
            
            if source_path.exists():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
                print(f"  ✓ Moved: {source} → {target}")
    
    def create_domain_init_files(self):
        """Create __init__.py files for domains"""
        print(f"\n📦 Creating domain __init__.py files...")
        
        domains = ['auth', 'sales', 'courses', 'ai', 'users']
        
        for domain in domains:
            domain_path = self.server_path / "domains" / domain
            init_file = domain_path / "__init__.py"
            
            # Create domain-specific imports
            init_content = f'"""'
            init_content += f'\n{domain.capitalize()} Domain'
            init_content += f'\nProvides {domain}-related models, routes, services, and schemas'
            init_content += f'\n"""'
            init_content += f'\n'
            init_content += f'\nfrom .models import *'
            init_content += f'\nfrom .schemas import *'
            init_content += f'\nfrom .services import *'
            init_content += f'\n'
            
            with open(init_file, 'w') as f:
                f.write(init_content)
            
            print(f"  ✓ Created: {init_file}")
    
    def update_main_app_imports(self):
        """Update main.py to import from new domain structure"""
        print(f"\n🔄 Updating main.py imports...")
        
        main_file = self.server_path / "main.py"
        if not main_file.exists():
            return
        
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Update import patterns
        import_updates = [
            (r'from app\.routes\.(.*?)_routes import', r'from app.domains.\1.routes import'),
            (r'from \.routes\.(.*?)_routes import', r'from .domains.\1.routes import'),
        ]
        
        for old_pattern, new_pattern in import_updates:
            content = re.sub(old_pattern, new_pattern, content)
        
        with open(main_file, 'w') as f:
            f.write(content)
        
        print(f"  ✓ Updated main.py imports")
    
    def run_migration(self):
        """Run complete domain migration"""
        print("🚀 Starting domain migration...")
        
        self.migrate_domain_files()
        self.migrate_core_files()
        self.migrate_shared_files()
        self.create_domain_init_files()
        self.update_main_app_imports()
        
        print("\n✅ Domain migration complete!")
        print("\n📋 Next steps:")
        print("  1. Review merged files for conflicts")
        print("  2. Update import statements in remaining files")
        print("  3. Run tests to verify functionality")
        print("  4. Remove old directory structure")

if __name__ == "__main__":
    import sys
    
    project_root = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    migrator = DomainMigrator(project_root)
    migrator.run_migration()
EOF

chmod +x "scripts/migrate-to-domains.py"

echo ""
echo "📋 Step 5: Create import update script"

cat > "scripts/update-domain-imports.py" << 'EOF'
#!/usr/bin/env python3

"""
Import Update Script
Updates import statements to use new domain structure
"""

import os
import re
from pathlib import Path

def update_imports_in_file(file_path: Path, project_root: Path):
    """Update imports in a single Python file"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Import update patterns
        patterns = [
            # Old route imports to new domain imports
            (r'from app\.routes\.auth_routes import', 'from app.domains.auth.routes import'),
            (r'from app\.routes\.sales_routes import', 'from app.domains.sales.routes import'),
            (r'from app\.routes\.course_routes import', 'from app.domains.courses.routes import'),
            (r'from app\.routes\.ai_routes import', 'from app.domains.ai.routes import'),
            
            # Old model imports to new domain imports
            (r'from app\.models\.user import', 'from app.domains.auth.models import'),
            (r'from app\.models\.sales import', 'from app.domains.sales.models import'),
            (r'from app\.models\.course import', 'from app.domains.courses.models import'),
            
            # Old service imports to new domain imports
            (r'from app\.services\.auth_service import', 'from app.domains.auth.services import'),
            (r'from app\.services\.user_service import', 'from app.domains.auth.services import'),
            (r'from app\.services\.sales_service import', 'from app.domains.sales.services import'),
            (r'from app\.services\.course_service import', 'from app.domains.courses.services import'),
            (r'from app\.services\.ai_service import', 'from app.domains.ai.services.core import'),
            
            # Old schema imports to new domain imports
            (r'from app\.schemas\.auth import', 'from app.domains.auth.schemas import'),
            (r'from app\.schemas\.sales import', 'from app.domains.sales.schemas import'),
            (r'from app\.schemas\.course import', 'from app.domains.courses.schemas import'),
            (r'from app\.schemas\.ai import', 'from app.domains.ai.schemas import'),
            
            # Config imports
            (r'from app\.config import', 'from app.core.config import'),
            (r'from \.config import', 'from .core.config import'),
            
            # Database imports
            (r'from app\.database import', 'from app.core.database import'),
            (r'from \.database import', 'from .core.database import'),
        ]
        
        # Apply pattern updates
        for old_pattern, new_pattern in patterns:
            content = re.sub(old_pattern, new_pattern, content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
    except Exception as e:
        print(f"⚠️  Error updating {file_path}: {e}")
        
    return False

def update_all_imports(project_root: str):
    """Update imports in all Python files"""
    
    root_path = Path(project_root)
    server_path = root_path / "server"
    
    # Find all Python files
    python_files = list(server_path.rglob("*.py"))
    
    updated_count = 0
    
    print(f"🔄 Updating imports in {len(python_files)} Python files...")
    
    for file_path in python_files:
        if file_path.is_file() and not file_path.name.startswith('.'):
            if update_imports_in_file(file_path, root_path):
                print(f"  ✓ Updated: {file_path.relative_to(root_path)}")
                updated_count += 1
    
    print(f"\n✅ Updated imports in {updated_count} files")

if __name__ == "__main__":
    import sys
    
    project_root = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    update_all_imports(project_root)
EOF

chmod +x "scripts/update-domain-imports.py"

echo ""
echo "✅ Phase 2 Complete!"
echo ""
echo "📊 Summary:"
echo "  • Created domain-based backend structure"
echo "  • Generated migration mapping and scripts"
echo "  • Prepared file consolidation utilities"
echo "  • Created import update automation"
echo ""
echo "🔄 Next Steps:"
echo "  1. Run: python3 scripts/migrate-to-domains.py"
echo "  2. Review merged files for conflicts"
echo "  3. Run: python3 scripts/update-domain-imports.py"
echo "  4. Test backend functionality"
echo ""
echo "📝 New Structure Preview:"
echo "  server/app/"
echo "  ├── core/           # config.py, database.py"
echo "  ├── domains/"
echo "  │   ├── auth/       # User authentication & management"
echo "  │   ├── sales/      # Course requests & sales"
echo "  │   ├── courses/    # Course management & generation"
echo "  │   ├── ai/         # AI services & agents"
echo "  │   └── users/      # User profiles & preferences"
echo "  └── shared/         # Common utilities & middleware"