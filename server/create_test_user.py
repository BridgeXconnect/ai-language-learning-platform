#!/usr/bin/env python3
"""
Create a test user for development purposes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db, engine, Base
from app.services.user_service import UserService
from app.models.user import Role
from sqlalchemy.orm import Session

def create_test_user():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if roles exist, create them if not
        roles_to_create = [
            {"name": "sales", "description": "Sales team member"},
            {"name": "course_manager", "description": "Course manager"},
            {"name": "trainer", "description": "Trainer"},
            {"name": "student", "description": "Student"},
            {"name": "admin", "description": "Administrator"}
        ]
        
        for role_data in roles_to_create:
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing_role:
                role = Role(name=role_data["name"], description=role_data["description"])
                db.add(role)
        
        db.commit()
        
        # Create test users
        test_users = [
            {
                "username": "sales_user",
                "email": "sales@example.com",
                "password": "password123",
                "first_name": "Sales",
                "last_name": "User",
                "roles": ["sales"]
            },
            {
                "username": "course_manager",
                "email": "manager@example.com", 
                "password": "password123",
                "first_name": "Course",
                "last_name": "Manager",
                "roles": ["course_manager"]
            },
            {
                "username": "trainer_user",
                "email": "trainer@example.com",
                "password": "password123", 
                "first_name": "Trainer",
                "last_name": "User",
                "roles": ["trainer"]
            },
            {
                "username": "student_user",
                "email": "student@example.com",
                "password": "password123",
                "first_name": "Student", 
                "last_name": "User",
                "roles": ["student"]
            }
        ]
        
        for user_data in test_users:
            try:
                user = UserService.create_user(
                    db=db,
                    username=user_data["username"],
                    email=user_data["email"], 
                    password=user_data["password"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    roles=user_data["roles"]
                )
                print(f"✅ Created user: {user.email} ({user.username}) with roles: {user_data['roles']}")
            except ValueError as e:
                print(f"⚠️  User {user_data['email']} already exists: {e}")
                
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
    print("\n🎉 Test user creation complete!")
    print("\nYou can now log in with:")
    print("📧 Email: sales@example.com | Password: password123 (Sales Portal)")
    print("📧 Email: manager@example.com | Password: password123 (Course Manager Portal)")
    print("📧 Email: trainer@example.com | Password: password123 (Trainer Portal)")
    print("📧 Email: student@example.com | Password: password123 (Student Portal)")