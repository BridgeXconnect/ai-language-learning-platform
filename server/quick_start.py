#!/usr/bin/env python3
"""
Quick start script for AI Language Learning Platform
Run this after setting up PostgreSQL and creating your .env file
"""

import os
import sys
from pathlib import Path

def check_env():
    """Check if .env file exists with required variables"""
    if not Path('.env').exists():
        print("❌ .env file not found!")
        print("\nPlease create a .env file with the following content:")
        print("-" * 50)
        print('''DATABASE_URL="postgresql://username:password@localhost:5432/ai_language_platform"
JWT_SECRET_KEY="your-secret-key-here"
REDIS_URL="redis://localhost:6379/0"
DEBUG=True''')
        print("-" * 50)
        return False
    
    print("✅ .env file found")
    return True

def test_imports():
    """Test if all imports work"""
    print("Testing imports...")
    
    try:
        from app.database import engine, Base
        print("✅ Database imports OK")
        
        from app.models.user import User, Role, Permission
        print("✅ User models OK")
        
        from app.models.sales import CourseRequest, SOPDocument, ClientFeedback
        print("✅ Sales models OK")
        
        from app.models.course import Course, Module, Lesson
        print("✅ Course models OK")
        
        from app.services.auth_service import AuthService
        from app.services.user_service import UserService
        print("✅ Services OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def create_tables():
    """Create database tables"""
    print("Creating database tables...")
    
    try:
        from app.database import engine, Base
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def initialize_data():
    """Initialize database with default data"""
    print("Initializing database data...")
    
    try:
        from app.init_db import init_database
        init_database()
        print("✅ Database initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize data: {e}")
        print("Error details:", str(e))
        return False

def main():
    """Main function"""
    print("🚀 AI Language Learning Platform - Quick Start")
    print("=" * 50)
    
    # Check prerequisites
    if not check_env():
        return False
    
    if not test_imports():
        print("\n💡 If you see import errors, try:")
        print("   pip install -r requirements.txt")
        return False
    
    # Create tables
    if not create_tables():
        return False
    
    # Initialize data
    if not initialize_data():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("=" * 50)
    print("\n📝 Default users created:")
    print("   admin / admin123 (Administrator)")
    print("   demo_sales / demo123 (Sales User)")
    print("   demo_trainer / demo123 (Trainer)")
    print("   demo_manager / demo123 (Course Manager)")
    print("   demo_student / demo123 (Student)")
    
    print("\n🏃 To start the server:")
    print("   python run.py")
    print("\n🌐 Then visit:")
    print("   http://localhost:8000/docs (API Documentation)")
    print("   http://localhost:8000/health (Health Check)")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)