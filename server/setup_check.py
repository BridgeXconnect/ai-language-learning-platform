#!/usr/bin/env python3
"""
Environment setup checker and database initialization script
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.10+"""
    print("Checking Python version...")
    major, minor = sys.version_info[:2]
    if major >= 3 and minor >= 10:
        print(f"✓ Python {major}.{minor} is supported")
        return True
    else:
        print(f"✗ Python {major}.{minor} is not supported. Please use Python 3.10+")
        return False

def check_postgresql():
    """Check if PostgreSQL is installed and running"""
    print("Checking PostgreSQL...")
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✓ PostgreSQL is installed: {result.stdout.strip()}")
        
        # Try to connect to default database
        try:
            subprocess.run(['psql', '-c', 'SELECT version();'], 
                          capture_output=True, check=True)
            print("✓ PostgreSQL is running and accessible")
            return True
        except subprocess.CalledProcessError:
            print("✗ PostgreSQL is installed but not running or not accessible")
            print("  Please start PostgreSQL service and ensure you have access")
            return False
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ PostgreSQL is not installed or not in PATH")
        print("  Please install PostgreSQL and add it to your PATH")
        return False

def check_redis():
    """Check if Redis is installed and running"""
    print("Checking Redis...")
    try:
        result = subprocess.run(['redis-cli', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✓ Redis is installed: {result.stdout.strip()}")
        
        # Try to ping Redis
        try:
            result = subprocess.run(['redis-cli', 'ping'], 
                                  capture_output=True, text=True, check=True)
            if result.stdout.strip() == 'PONG':
                print("✓ Redis is running")
                return True
            else:
                print("✗ Redis is not responding")
                return False
        except subprocess.CalledProcessError:
            print("✗ Redis is installed but not running")
            print("  Please start Redis service")
            return False
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Redis is not installed or not in PATH")
        print("  Please install Redis and add it to your PATH")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("Checking environment configuration...")
    env_path = Path('.env')
    
    if not env_path.exists():
        print("✗ .env file not found")
        print("  Creating .env file from template...")
        create_env_file()
        return False
    else:
        print("✓ .env file exists")
        
        # Check required variables
        required_vars = [
            'DATABASE_URL',
            'JWT_SECRET_KEY',
            'REDIS_URL'
        ]
        
        with open(env_path, 'r') as f:
            env_content = f.read()
        
        missing_vars = []
        for var in required_vars:
            if f"{var}=" not in env_content or f"{var}=\"\"" in env_content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"✗ Missing or empty environment variables: {', '.join(missing_vars)}")
            print("  Please update your .env file with the required values")
            return False
        else:
            print("✓ Required environment variables are set")
            return True

def create_env_file():
    """Create .env file from template"""
    env_content = '''# Application Configuration
APP_NAME="Dynamic English Course Creator"
APP_VERSION="1.0.0"
DEBUG=True

# Database Configuration
DATABASE_URL="postgresql://username:password@localhost:5432/ai_language_platform"

# JWT Configuration
JWT_SECRET_KEY="your-super-secret-jwt-key-change-this-in-production"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis Configuration
REDIS_URL="redis://localhost:6379/0"

# AWS Configuration (Optional)
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_REGION="us-east-1"

# Email Configuration (Optional)
SMTP_HOST=""
SMTP_PORT=587
SMTP_USER=""
SMTP_PASSWORD=""

# Security Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
API_KEY_HEADER="X-API-Key"
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# AI/LLM Configuration
OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""
'''
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✓ .env file created from template")
    print("  Please edit .env file and update the configuration values")

def check_database_connection():
    """Check if we can connect to the database"""
    print("Checking database connection...")
    
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Database connection successful")
            return True
            
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("  Please check your DATABASE_URL in .env file")
        print("  Make sure PostgreSQL is running and the database exists")
        return False

def create_database():
    """Create the database if it doesn't exist"""
    print("Checking if database exists...")
    
    try:
        from app.core.config import settings
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        # Parse DATABASE_URL to get connection details
        db_url = settings.DATABASE_URL
        if not db_url.startswith('postgresql://'):
            print("✗ Invalid DATABASE_URL format")
            return False
        
        # Extract database name from URL
        db_name = db_url.split('/')[-1]
        base_url = db_url.rsplit('/', 1)[0] + '/postgres'
        
        # Connect to postgres database to create our database
        conn = psycopg2.connect(base_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cur:
            # Check if database exists
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            if cur.fetchone():
                print(f"✓ Database '{db_name}' exists")
            else:
                # Create database
                cur.execute(f'CREATE DATABASE "{db_name}"')
                print(f"✓ Database '{db_name}' created")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Failed to create database: {e}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def initialize_database():
    """Initialize database with tables and data"""
    print("Initializing database...")
    
    try:
        from app.init_db import init_database
        init_database()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def main():
    """Main setup check function"""
    print("=" * 60)
    print("AI Language Learning Platform - Setup Checker")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Basic environment checks
    all_checks_passed &= check_python_version()
    all_checks_passed &= check_postgresql()
    all_checks_passed &= check_redis()
    all_checks_passed &= check_env_file()
    
    if not all_checks_passed:
        print("\n" + "=" * 60)
        print("❌ Some checks failed. Please fix the issues above before continuing.")
        print("=" * 60)
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Phase 1: Environment Setup")
    print("=" * 60)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Database setup
    if not create_database():
        sys.exit(1)
    
    if not check_database_connection():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Phase 2: Database Initialization")
    print("=" * 60)
    
    if not initialize_database():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update your .env file with proper configuration values")
    print("2. Start the server: python run.py")
    print("3. Access the API at: http://localhost:8000")
    print("4. View API docs at: http://localhost:8000/docs")
    print("\nDefault login credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("=" * 60)

if __name__ == "__main__":
    main()