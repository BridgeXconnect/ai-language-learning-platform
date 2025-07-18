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
