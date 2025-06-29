#!/usr/bin/env python3
"""
Simple script to create a test user without complex relationships
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.services.auth_service import AuthService

def create_simple_user():
    # Connect to database
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create roles table if not exists
        db.execute(text("""
        CREATE TABLE IF NOT EXISTS roles (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL,
            description VARCHAR(255)
        )
        """))
        
        # Create users table if not exists  
        db.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            phone VARCHAR(20),
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """))
        
        # Create user_roles table if not exists
        db.execute(text("""
        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INTEGER REFERENCES users(id),
            role_id INTEGER REFERENCES roles(id),
            PRIMARY KEY (user_id, role_id)
        )
        """))
        
        db.commit()
        
        # Insert roles
        roles = [
            ("sales", "Sales team member"),
            ("course_manager", "Course manager"), 
            ("trainer", "Trainer"),
            ("student", "Student"),
            ("admin", "Administrator")
        ]
        
        for role_name, description in roles:
            db.execute(text("""
            INSERT INTO roles (name, description) 
            VALUES (:name, :description) 
            ON CONFLICT (name) DO NOTHING
            """), {"name": role_name, "description": description})
        
        db.commit()
        
        # Create test users
        password_hash = AuthService.get_password_hash("password123")
        
        test_users = [
            ("sales_user", "sales@example.com", "Sales", "User", "sales"),
            ("manager_user", "manager@example.com", "Course", "Manager", "course_manager"),
            ("trainer_user", "trainer@example.com", "Trainer", "User", "trainer"),
            ("student_user", "student@example.com", "Student", "User", "student")
        ]
        
        for username, email, first_name, last_name, role_name in test_users:
            # Insert user
            result = db.execute(text("""
            INSERT INTO users (username, email, password_hash, first_name, last_name, status)
            VALUES (:username, :email, :password_hash, :first_name, :last_name, 'active')
            ON CONFLICT (email) DO UPDATE SET
                password_hash = :password_hash,
                first_name = :first_name,
                last_name = :last_name
            RETURNING id
            """), {
                "username": username,
                "email": email, 
                "password_hash": password_hash,
                "first_name": first_name,
                "last_name": last_name
            })
            
            user_id = result.fetchone()[0]
            
            # Get role ID
            role_result = db.execute(text("""
            SELECT id FROM roles WHERE name = :role_name
            """), {"role_name": role_name})
            
            role_id = role_result.fetchone()[0]
            
            # Insert user role
            db.execute(text("""
            INSERT INTO user_roles (user_id, role_id)
            VALUES (:user_id, :role_id)
            ON CONFLICT DO NOTHING
            """), {"user_id": user_id, "role_id": role_id})
            
            print(f"✅ Created user: {email} with role: {role_name}")
        
        db.commit()
        print("\n🎉 All test users created successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_simple_user()
    print("\nYou can now log in with:")
    print("📧 Email: sales@example.com | Password: password123")
    print("📧 Email: manager@example.com | Password: password123") 
    print("📧 Email: trainer@example.com | Password: password123")
    print("📧 Email: student@example.com | Password: password123")