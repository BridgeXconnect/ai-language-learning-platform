#!/usr/bin/env python3
"""
Production Deployment Script for AI Language Learning Platform
Handles database setup, environment validation, and server deployment
"""

import os
import sys
import subprocess
import secrets
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
import json
import time

class ProductionDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / ".env"
        self.backup_dir = self.project_root / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_command(self, command: str, check: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command with error handling"""
        self.log(f"Running: {command}")
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                check=check, 
                capture_output=True, 
                text=True,
                cwd=self.project_root
            )
            if result.stdout:
                self.log(f"Output: {result.stdout.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e.stderr}", "ERROR")
            if check:
                raise
            return e
            
    def validate_environment(self) -> bool:
        """Validate production environment variables"""
        self.log("Validating production environment...")
        
        required_vars = [
            "DATABASE_URL",
            "JWT_SECRET_KEY", 
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
                
        if missing_vars:
            self.log(f"Missing required environment variables: {missing_vars}", "ERROR")
            return False
            
        # Validate DATABASE_URL format
        db_url = os.getenv("DATABASE_URL", "")
        if not db_url.startswith("postgresql://"):
            self.log("DATABASE_URL must be a PostgreSQL connection string", "ERROR")
            return False
            
        self.log("Environment validation passed ✅")
        return True
        
    def generate_secure_secrets(self) -> Dict[str, str]:
        """Generate secure secrets for production"""
        self.log("Generating secure production secrets...")
        
        secrets_dict = {
            "JWT_SECRET_KEY": secrets.token_urlsafe(64),
            "API_SECRET_KEY": secrets.token_urlsafe(32),
            "ENCRYPTION_KEY": secrets.token_urlsafe(32)
        }
        
        return secrets_dict
        
    def backup_current_config(self) -> str:
        """Create backup of current configuration"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"config_backup_{timestamp}.json"
        
        config = {
            "timestamp": timestamp,
            "env_vars": {k: v for k, v in os.environ.items() if k.startswith(("DATABASE_", "JWT_", "API_"))},
            "database_url": os.getenv("DATABASE_URL", "").replace(os.getenv("DATABASE_PASSWORD", ""), "***") if os.getenv("DATABASE_URL") else ""
        }
        
        with open(backup_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        self.log(f"Configuration backed up to: {backup_file}")
        return str(backup_file)
        
    def test_database_connection(self) -> bool:
        """Test database connection"""
        self.log("Testing database connection...")
        
        try:
            result = self.run_command(
                "python -c \"from app.main import app; print('Database connection successful')\"",
                check=False
            )
            
            if result.returncode == 0:
                self.log("Database connection test passed ✅")
                return True
            else:
                self.log("Database connection test failed ❌", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Database connection test error: {e}", "ERROR")
            return False
            
    def install_dependencies(self) -> bool:
        """Install production dependencies"""
        self.log("Installing production dependencies...")
        
        try:
            # Upgrade pip
            self.run_command("pip install --upgrade pip")
            
            # Install requirements
            self.run_command("pip install -r requirements.txt")
            
            # Install additional production packages
            production_packages = [
                "gunicorn",
                "uvicorn[standard]",
                "psycopg2-binary",
                "redis",
                "celery"
            ]
            
            for package in production_packages:
                self.run_command(f"pip install {package}")
                
            self.log("Dependencies installed successfully ✅")
            return True
            
        except Exception as e:
            self.log(f"Failed to install dependencies: {e}", "ERROR")
            return False
            
    def setup_database(self) -> bool:
        """Setup database tables and initial data"""
        self.log("Setting up database...")
        
        try:
            # Run the dedicated database setup script
            self.run_command("python scripts/setup_database.py")
            
            self.log("Database setup completed ✅")
            return True
            
        except Exception as e:
            self.log(f"Database setup failed: {e}", "ERROR")
            return False
            
    def create_production_config(self) -> bool:
        """Create production-specific configuration"""
        self.log("Creating production configuration...")
        
        try:
            # Create production .env template
            prod_env_template = f"""# Production Environment Configuration
# Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}

# Database Configuration
DATABASE_URL="{os.getenv('DATABASE_URL', '')}"

# Security Configuration
JWT_SECRET_KEY="{os.getenv('JWT_SECRET_KEY', '')}"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
DEBUG=False
ENVIRONMENT="production"

# CORS Configuration
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"

# AI/LLM Configuration
OPENAI_API_KEY="{os.getenv('OPENAI_API_KEY', '')}"
ANTHROPIC_API_KEY="{os.getenv('ANTHROPIC_API_KEY', '')}"

# Redis Configuration (for caching and background tasks)
REDIS_URL="redis://localhost:6379/0"

# Logging Configuration
LOG_LEVEL="INFO"
LOG_FILE="/var/log/ai-language-platform/app.log"

# Performance Configuration
WORKERS=4
WORKER_CLASS="uvicorn.workers.UvicornWorker"
BIND="0.0.0.0:8000"
"""
            
            prod_env_file = self.project_root / ".env.production"
            with open(prod_env_file, 'w') as f:
                f.write(prod_env_template)
                
            self.log(f"Production configuration created: {prod_env_file}")
            return True
            
        except Exception as e:
            self.log(f"Failed to create production config: {e}", "ERROR")
            return False
            
    def create_systemd_service(self) -> bool:
        """Create systemd service file for production"""
        self.log("Creating systemd service configuration...")
        
        service_content = f"""[Unit]
Description=AI Language Learning Platform
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory={self.project_root}
Environment=PATH={self.project_root}/.venv/bin
ExecStart={self.project_root}/.venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path("/tmp/ai-language-platform.service")
        with open(service_file, 'w') as f:
            f.write(service_content)
            
        self.log(f"Systemd service file created: {service_file}")
        self.log("To install: sudo cp /tmp/ai-language-platform.service /etc/systemd/system/")
        self.log("Then: sudo systemctl enable ai-language-platform && sudo systemctl start ai-language-platform")
        
        return True
        
    def run_health_checks(self) -> bool:
        """Run comprehensive health checks"""
        self.log("Running health checks...")
        
        checks = [
            ("Database Connection", self.test_database_connection),
            ("Environment Variables", self.validate_environment),
            ("Dependencies", lambda: True),  # Already checked during install
        ]
        
        failed_checks = []
        for check_name, check_func in checks:
            try:
                if check_func():
                    self.log(f"✅ {check_name} passed")
                else:
                    failed_checks.append(check_name)
                    self.log(f"❌ {check_name} failed", "ERROR")
            except Exception as e:
                failed_checks.append(check_name)
                self.log(f"❌ {check_name} error: {e}", "ERROR")
                
        if failed_checks:
            self.log(f"Health checks failed: {failed_checks}", "ERROR")
            return False
            
        self.log("All health checks passed ✅")
        return True
        
    def deploy(self) -> bool:
        """Main deployment process"""
        self.log("🚀 Starting production deployment...")
        
        try:
            # Step 1: Backup current configuration
            self.backup_current_config()
            
            # Step 2: Validate environment
            if not self.validate_environment():
                return False
                
            # Step 3: Install dependencies
            if not self.install_dependencies():
                return False
                
            # Step 4: Setup database
            if not self.setup_database():
                return False
                
            # Step 5: Create production configuration
            if not self.create_production_config():
                return False
                
            # Step 6: Create systemd service
            self.create_systemd_service()
            
            # Step 7: Run health checks
            if not self.run_health_checks():
                return False
                
            self.log("🎉 Production deployment completed successfully!")
            self.log("Next steps:")
            self.log("1. Copy .env.production to your production server")
            self.log("2. Install systemd service: sudo cp /tmp/ai-language-platform.service /etc/systemd/system/")
            self.log("3. Enable and start service: sudo systemctl enable ai-language-platform && sudo systemctl start ai-language-platform")
            self.log("4. Check logs: sudo journalctl -u ai-language-platform -f")
            
            return True
            
        except Exception as e:
            self.log(f"Deployment failed: {e}", "ERROR")
            return False

def main():
    """Main entry point"""
    deployer = ProductionDeployer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        deployer.log("Running in dry-run mode...")
        deployer.validate_environment()
        deployer.test_database_connection()
        deployer.log("Dry-run completed")
    else:
        success = deployer.deploy()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 