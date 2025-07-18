#!/usr/bin/env python3
"""
Create an admin user for the AI Language Learning Platform
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.domains.auth.services import AuthService

def create_admin_user():
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
        
        # Insert admin role
        db.execute(text("""
        INSERT INTO roles (name, description) 
        VALUES ('admin', 'Administrator') 
        ON CONFLICT (name) DO NOTHING
        """))
        
        db.commit()
        
        # Create admin user
        password_hash = AuthService.get_password_hash("admin123")
        
        # Insert admin user
        result = db.execute(text("""
        INSERT INTO users (username, email, password_hash, first_name, last_name, status)
        VALUES ('admin', 'admin@example.com', :password_hash, 'Admin', 'User', 'active')
        ON CONFLICT (email) DO UPDATE SET
            password_hash = :password_hash,
            first_name = 'Admin',
            last_name = 'User'
        RETURNING id
        """), {
            "username": "admin",
            "email": "admin@example.com", 
            "password_hash": password_hash,
            "first_name": "Admin",
            "last_name": "User"
        })
        
        user_id = result.fetchone()[0]
        
        # Get admin role ID
        role_result = db.execute(text("""
        SELECT id FROM roles WHERE name = 'admin'
        """))
        
        role_id = role_result.fetchone()[0]
        
        # Insert user role
        db.execute(text("""
        INSERT INTO user_roles (user_id, role_id)
        VALUES (:user_id, :role_id)
        ON CONFLICT DO NOTHING
        """), {"user_id": user_id, "role_id": role_id})
        
        db.commit()
        print("✅ Admin user created successfully!")
        print("\n🔑 Admin Login Details:")
        print("📧 Email: admin@example.com")
        print("🔐 Password: admin123")
        print("👤 Username: admin")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user() 