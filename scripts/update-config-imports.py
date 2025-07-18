#!/usr/bin/env python3

"""
Configuration Import Update Script
Updates Python files to use consolidated configuration
"""

import os
import re
import sys
from pathlib import Path

def update_config_imports(root_path):
    """Update configuration imports in Python files"""
    
    # Files to update
    python_files = []
    server_path = Path(root_path) / "server"
    
    # Find all Python files in server directory
    for file_path in server_path.rglob("*.py"):
        if file_path.is_file() and not file_path.name.startswith('.'):
            python_files.append(file_path)
    
    updated_files = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Update import patterns for configuration
            # These are common patterns that might need updating
            patterns = [
                (r'from \.config import', 'from app.core.config import'),
                (r'from config import', 'from app.core.config import'),
                (r'import config', 'from app.core import config'),
            ]
            
            for old_pattern, new_pattern in patterns:
                content = re.sub(old_pattern, new_pattern, content)
            
            # Only write if content changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_files.append(str(file_path))
                print(f"✓ Updated: {file_path.relative_to(root_path)}")
        
        except Exception as e:
            print(f"⚠️  Error updating {file_path}: {e}")
    
    return updated_files

if __name__ == "__main__":
    root_path = Path(__file__).parent.parent
    print("🔧 Updating configuration imports...")
    updated = update_config_imports(root_path)
    print(f"✅ Updated {len(updated)} files")
