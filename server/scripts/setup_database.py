#!/usr/bin/env python3
"""
Database Setup Script for AI Language Learning Platform
Creates all necessary tables and initializes the database
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import engine
from app.domains.auth.models import User
from app.domains.courses.models import Course
from app.domains.sales.models import CourseRequest, SOPDocument, ClientFeedback
# Only use FastAPI models, skip Flask models for now

def setup_database():
    """Setup database tables"""
    print("Setting up database tables...")
    
    try:
        # Import all models to ensure they're registered with SQLAlchemy
        print("Importing models...")
        
        # Create tables for each model
        print("Creating users table...")
        User.__table__.create(engine, checkfirst=True)
        
        print("Creating courses table...")
        Course.__table__.create(engine, checkfirst=True)
        
        print("Creating course requests table...")
        CourseRequest.__table__.create(engine, checkfirst=True)
        
        print("Creating SOP documents table...")
        SOPDocument.__table__.create(engine, checkfirst=True)
        
        print("Creating client feedback table...")
        ClientFeedback.__table__.create(engine, checkfirst=True)
        
        # Server models will be created separately if needed
        
        print("✅ Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def verify_database():
    """Verify database connection and tables"""
    print("Verifying database connection...")
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            result.fetchone()
            print("✅ Database connection successful")
            
        # Check if tables exist
        with engine.connect() as conn:
            tables = ['users', 'courses', 'course_requests', 'sop_documents', 'client_feedback']
            for table in tables:
                try:
                    result = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    count = result.fetchone()[0]
                    print(f"✅ Table {table} exists with {count} records")
                except Exception as e:
                    print(f"❌ Table {table} not found: {e}")
                    
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Database Setup for AI Language Learning Platform")
    print("=" * 50)
    
    if setup_database():
        print("\n" + "=" * 50)
        verify_database()
    else:
        sys.exit(1) 