#!/usr/bin/env python3
"""
Database Setup Script for AI Language Learning Platform
Created by: James (BMAD Developer)
"""

import asyncio
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import importlib
import importlib.util, os, sys

# Load database.py explicitly to avoid package name conflict
base_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(base_dir, "app", "database.py")
spec = importlib.util.spec_from_file_location("database_file", module_path)
if spec and spec.loader:
    db_mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = db_mod
    spec.loader.exec_module(db_mod)
else:
    raise ImportError("Unable to load database module from path: " + module_path)

engine = db_mod.engine
Base = db_mod.Base

from app.models.database_models import User, Role
from app.services.authentication_service import auth_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database_tables():
    """Create all database tables"""
    try:
        logger.info("Creating database tables...")
        # Drop existing tables to ensure fresh schema
        try:
            Base.metadata.drop_all(bind=engine)
            logger.info("Dropped existing tables")
        except Exception as d:
            logger.warning(f"Could not drop existing tables: {d}")

        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        return False

def seed_initial_data():
    """Seed initial data (roles, admin user)"""
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        logger.info("Seeding initial data...")
        
        # Create roles if they don't exist
        roles_data = [
            {"name": "admin", "description": "Administrator with full access"},
            {"name": "trainer", "description": "Course creator and trainer"},
            {"name": "student", "description": "Learning student"},
            {"name": "moderator", "description": "Content moderator"}
        ]
        
        for role_data in roles_data:
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing_role:
                role = Role(**role_data)
                db.add(role)
                logger.info(f"Created role: {role_data['name']}")
        
        db.commit()
        
        # Create admin user if it doesn't exist
        admin_email = "admin@ailanguageplatform.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if not existing_admin:
            # Hash password
            admin_password = "admin123"  # Change this in production!
            hashed_password = auth_service.hash_password(admin_password)
            
            # Create admin user
            admin_user = User(
                email=admin_email,
                username="admin",
                password_hash=hashed_password,
                first_name="Admin",
                last_name="User",
                status="active",
                email_verified=True
            )
            
            # Assign admin role
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            if admin_role:
                admin_user.user_roles_rel.append(admin_role)
            
            db.add(admin_user)
            db.commit()
            logger.info(f"✅ Created admin user: {admin_email}")
            logger.warning(f"⚠️  Admin password: {admin_password} - CHANGE THIS IN PRODUCTION!")
        else:
            logger.info("✅ Admin user already exists")
        
        # Create demo trainer user
        trainer_email = "trainer@ailanguageplatform.com"
        existing_trainer = db.query(User).filter(User.email == trainer_email).first()
        
        if not existing_trainer:
            trainer_password = "trainer123"
            hashed_password = auth_service.hash_password(trainer_password)
            
            trainer_user = User(
                email=trainer_email,
                username="demo_trainer",
                password_hash=hashed_password,
                first_name="Demo",
                last_name="Trainer",
                status="active",
                email_verified=True
            )
            
            trainer_role = db.query(Role).filter(Role.name == "trainer").first()
            if trainer_role:
                trainer_user.user_roles_rel.append(trainer_role)
            
            db.add(trainer_user)
            db.commit()
            logger.info(f"✅ Created demo trainer: {trainer_email}")
            logger.warning(f"⚠️  Trainer password: {trainer_password} - CHANGE THIS IN PRODUCTION!")
        else:
            logger.info("✅ Demo trainer already exists")
        
        # Create demo student user
        student_email = "student@ailanguageplatform.com"
        existing_student = db.query(User).filter(User.email == student_email).first()
        
        if not existing_student:
            student_password = "student123"
            hashed_password = auth_service.hash_password(student_password)
            
            student_user = User(
                email=student_email,
                username="demo_student",
                password_hash=hashed_password,
                first_name="Demo",
                last_name="Student",
                status="active",
                email_verified=True
            )
            
            student_role = db.query(Role).filter(Role.name == "student").first()
            if student_role:
                student_user.user_roles_rel.append(student_role)
            
            db.add(student_user)
            db.commit()
            logger.info(f"✅ Created demo student: {student_email}")
            logger.warning(f"⚠️  Student password: {student_password} - CHANGE THIS IN PRODUCTION!")
        else:
            logger.info("✅ Demo student already exists")
        
        db.close()
        logger.info("✅ Initial data seeded successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to seed initial data: {e}")
        db.rollback()
        db.close()
        return False

def verify_database_connection():
    """Verify database connection"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def show_database_info():
    """Show database information"""
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Count users
        user_count = db.query(User).count()
        logger.info(f"📊 Total users: {user_count}")
        
        # Count roles
        role_count = db.query(Role).count()
        logger.info(f"📊 Total roles: {role_count}")
        
        # Show roles
        roles = db.query(Role).all()
        logger.info("📋 Available roles:")
        for role in roles:
            user_count = len(role.users)
            logger.info(f"  - {role.name}: {user_count} users")
        
        db.close()
        
    except Exception as e:
        logger.error(f"❌ Failed to get database info: {e}")

def main():
    """Main setup function"""
    logger.info("🚀 Starting AI Language Learning Platform Database Setup")
    logger.info("=" * 60)
    
    # Step 1: Verify database connection
    if not verify_database_connection():
        logger.error("❌ Cannot proceed without database connection")
        return False
    
    # Step 2: Create tables
    if not create_database_tables():
        logger.error("❌ Cannot proceed without database tables")
        return False
    
    # Step 3: Seed initial data
    if not seed_initial_data():
        logger.error("❌ Failed to seed initial data")
        return False
    
    # Step 4: Show database information
    logger.info("=" * 60)
    show_database_info()
    
    logger.info("=" * 60)
    logger.info("🎉 Database setup completed successfully!")
    logger.info("")
    logger.info("📝 Demo Accounts Created:")
    logger.info("  Admin: admin@ailanguageplatform.com / admin123")
    logger.info("  Trainer: trainer@ailanguageplatform.com / trainer123")
    logger.info("  Student: student@ailanguageplatform.com / student123")
    logger.info("")
    logger.info("⚠️  IMPORTANT: Change these passwords in production!")
    logger.info("")
    logger.info("🚀 You can now start the application with:")
    logger.info("  python -m uvicorn app.main_v2:app --reload")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1) 