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
