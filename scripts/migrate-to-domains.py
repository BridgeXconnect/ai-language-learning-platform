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
