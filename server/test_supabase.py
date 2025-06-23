#!/usr/bin/env python3
"""
Supabase connection tester and database setup script
"""

import os
import sys
from pathlib import Path

def test_env_config():
    """Test if environment configuration is properly loaded"""
    print("🔧 Testing environment configuration...")
    
    try:
        from app.config import settings
        
        print(f"✅ App Name: {settings.APP_NAME}")
        print(f"✅ Database URL: {settings.DATABASE_URL[:50]}...")  # Don't show full URL for security
        print(f"✅ JWT Secret: {'Set' if settings.JWT_SECRET_KEY else 'Not Set'}")
        print(f"✅ Debug Mode: {settings.DEBUG}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_database_connection():
    """Test connection to Supabase database"""
    print("\n🗄️  Testing Supabase database connection...")
    
    try:
        from app.database import engine
        from sqlalchemy import text
        
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version[:50]}...")
            
        # Test if we can create tables
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Database is ready for table creation")
            
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Check if your Supabase URL is correct")
        print("   2. Verify your Supabase credentials")
        print("   3. Ensure your Supabase project is not paused")
        print("   4. Check network connectivity")
        return False

def test_model_imports():
    """Test if all model imports work correctly"""
    print("\n📋 Testing model imports...")
    
    try:
        from app.models.user import User, Role, Permission
        print("✅ User models imported")
        
        from app.models.sales import CourseRequest, SOPDocument, ClientFeedback
        print("✅ Sales models imported")
        
        from app.models.course import Course, Module, Lesson, Assessment
        print("✅ Course models imported")
        
        from app.services.auth_service import AuthService
        print("✅ Auth service imported")
        
        from app.services.user_service import UserService
        print("✅ User service imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def create_database_tables():
    """Create all database tables in Supabase"""
    print("\n🏗️  Creating database tables...")
    
    try:
        from app.database import Base, engine
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        
        # Verify tables were created
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
        print(f"✅ Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table}")
            
        return True
        
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False

def initialize_sample_data():
    """Initialize database with sample data"""
    print("\n🌱 Initializing sample data...")
    
    try:
        from app.init_db import init_database
        init_database()
        print("✅ Sample data initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Data initialization failed: {e}")
        print(f"Error details: {str(e)}")
        return False

def test_authentication():
    """Test authentication system"""
    print("\n🔐 Testing authentication system...")
    
    try:
        from app.database import SessionLocal
        from app.services.auth_service import AuthService
        from app.models.user import User
        
        db = SessionLocal()
        
        # Test if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            print("✅ Admin user found")
            
            # Test password verification
            if AuthService.verify_password("admin123", admin_user.password_hash):
                print("✅ Password verification works")
                
                # Test token creation
                tokens = AuthService.create_tokens_for_user(admin_user)
                if tokens.get("access_token"):
                    print("✅ JWT token generation works")
                    
                    # Test token verification
                    user = AuthService.get_current_user(db, tokens["access_token"])
                    if user and user.username == "admin":
                        print("✅ JWT token verification works")
                        db.close()
                        return True
        
        db.close()
        print("❌ Authentication test failed")
        return False
        
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False

def run_api_test():
    """Test if the API server can start"""
    print("\n🚀 Testing API server startup...")
    
    try:
        from app.main import app
        print("✅ FastAPI app created successfully")
        
        # Test health endpoint
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Health endpoint works")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main testing function"""
    print("🎯 Supabase Integration Test")
    print("=" * 50)
    
    tests = [
        ("Environment Configuration", test_env_config),
        ("Database Connection", test_database_connection),
        ("Model Imports", test_model_imports),
        ("Database Tables", create_database_tables),
        ("Sample Data", initialize_sample_data),
        ("Authentication", test_authentication),
        ("API Server", run_api_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        else:
            print(f"\n❌ {test_name} failed!")
            break
    
    print("\n" + "=" * 50)
    if passed == total:
        print("🎉 All tests passed! Your Supabase integration is ready!")
        print("=" * 50)
        print("\n📚 What's available now:")
        print("   • Database with all tables created")
        print("   • Sample users with different roles")
        print("   • Working authentication system")
        print("   • Complete API endpoints")
        
        print("\n🔑 Default Login Credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        
        print("\n🌐 Next Steps:")
        print("   1. Start the server: python run.py")
        print("   2. Visit: http://localhost:8000/docs")
        print("   3. Test login with admin credentials")
        
    else:
        print(f"❌ {passed}/{total} tests passed")
        print("Please fix the issues above before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)