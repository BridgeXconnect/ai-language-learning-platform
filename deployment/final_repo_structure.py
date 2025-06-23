# server/app/utils/__init__.py
# Utils package initialization

# server/app/utils/validators.py
import re
from typing import Dict, Any, List
from functools import wraps
from flask import request, jsonify

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_cefr_level(level: str) -> bool:
    """Validate CEFR level"""
    valid_levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    return level in valid_levels

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None

def validate_json_schema(schema: Dict[str, Any]):
    """Decorator to validate JSON request against schema"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
            
            data = request.get_json()
            errors = []
            
            for field, rules in schema.items():
                value = data.get(field)
                
                # Check required fields
                if rules.get('required', False) and value is None:
                    errors.append(f'{field} is required')
                    continue
                
                if value is not None:
                    # Check type
                    expected_type = rules.get('type')
                    if expected_type and not isinstance(value, expected_type):
                        errors.append(f'{field} must be of type {expected_type.__name__}')
                    
                    # Check string length
                    if isinstance(value, str):
                        min_length = rules.get('min_length')
                        max_length = rules.get('max_length')
                        if min_length and len(value) < min_length:
                            errors.append(f'{field} must be at least {min_length} characters')
                        if max_length and len(value) > max_length:
                            errors.append(f'{field} must be at most {max_length} characters')
                    
                    # Check custom validator
                    validator = rules.get('validator')
                    if validator and not validator(value):
                        errors.append(rules.get('error_message', f'{field} is invalid'))
            
            if errors:
                return jsonify({'errors': errors}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# server/app/utils/helpers.py
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_file_content(content: bytes) -> str:
    """Generate SHA256 hash of file content"""
    return hashlib.sha256(content).hexdigest()

def calculate_file_checksum(file_path: str) -> str:
    """Calculate checksum of a file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace dangerous characters
    dangerous_chars = '<>:"/\\|?*'
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    if len(name) > 100:
        name = name[:100]
    
    return f"{name}.{ext}" if ext else name

def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calculate estimated reading time in minutes"""
    word_count = len(text.split())
    return max(1, round(word_count / words_per_minute))

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def parse_json_safely(json_string: str) -> Optional[Dict[Any, Any]]:
    """Safely parse JSON string, return None if invalid"""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return None

def get_client_ip(request) -> str:
    """Get client IP address from request"""
    # Check for X-Forwarded-For header (from load balancer/proxy)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    
    # Check for X-Real-IP header
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    
    # Fallback to remote_addr
    return request.remote_addr

# server/app/utils/decorators.py
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from ..models import User, AuditLog
from .. import db
import logging

logger = logging.getLogger(__name__)

def require_role(allowed_roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or user.role not in allowed_roles:
                return jsonify({'msg': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def audit_action(action_name: str, resource_type: str = None):
    """Decorator to audit user actions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute the function first
            result = f(*args, **kwargs)
            
            # Log the action
            try:
                verify_jwt_in_request(optional=True)
                current_user_id = get_jwt_identity()
                
                audit_log = AuditLog(
                    user_id=current_user_id,
                    action=action_name,
                    resource_type=resource_type,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )
                
                # Extract resource ID from kwargs if available
                if 'id' in kwargs:
                    audit_log.resource_id = kwargs['id']
                
                db.session.add(audit_log)
                db.session.commit()
                
            except Exception as e:
                logger.error(f"Failed to log audit action: {str(e)}")
            
            return result
        return decorated_function
    return decorator

def rate_limit(max_requests: int, per_seconds: int):
    """Simple rate limiting decorator (in production, use Redis)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This is a simplified version
            # In production, implement proper rate limiting with Redis
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# server/migrations/001_initial_schema.sql
-- Initial database schema for AI Language Learning Platform

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    CONSTRAINT valid_role CHECK (role IN ('sales', 'course_manager', 'trainer', 'student', 'admin'))
);

-- Course requests table
CREATE TABLE course_requests (
    id SERIAL PRIMARY KEY,
    created_by INTEGER NOT NULL REFERENCES users(id),
    
    -- Client information
    company_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100),
    contact_name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(120) NOT NULL,
    contact_phone VARCHAR(20),
    
    -- Training details
    course_title VARCHAR(200),
    cohort_size INTEGER,
    current_cefr VARCHAR(2) DEFAULT 'A1',
    target_cefr VARCHAR(2) DEFAULT 'A2',
    training_objectives TEXT,
    pain_points TEXT,
    
    -- Course structure
    course_length_hours INTEGER,
    lessons_per_week INTEGER,
    delivery_method VARCHAR(20) DEFAULT 'in_person',
    
    -- Status and tracking
    status VARCHAR(20) DEFAULT 'pending',
    priority VARCHAR(10) DEFAULT 'normal',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    
    CONSTRAINT valid_cefr_current CHECK (current_cefr IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
    CONSTRAINT valid_cefr_target CHECK (target_cefr IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
    CONSTRAINT valid_delivery_method CHECK (delivery_method IN ('in_person', 'virtual', 'blended')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'generating', 'pending_review', 'approved', 'rejected', 'completed')),
    CONSTRAINT valid_priority CHECK (priority IN ('low', 'normal', 'high', 'urgent'))
);

-- SOP documents table
CREATE TABLE sop_documents (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES course_requests(id) ON DELETE CASCADE,
    
    -- File information
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    
    -- Processing status
    processing_status VARCHAR(20) DEFAULT 'uploaded',
    extracted_text TEXT,
    word_count INTEGER,
    vector_id VARCHAR(100),
    
    -- Timestamps
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    
    CONSTRAINT valid_processing_status CHECK (processing_status IN ('uploaded', 'processing', 'processed', 'failed'))
);

-- Courses table
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES course_requests(id),
    
    -- Course information
    title VARCHAR(200) NOT NULL,
    description TEXT,
    cefr_level VARCHAR(2) NOT NULL,
    estimated_duration_hours INTEGER,
    
    -- Status and version
    status VARCHAR(20) DEFAULT 'generating',
    version VARCHAR(10) DEFAULT '1.0',
    
    -- AI generation metadata
    ai_confidence_score FLOAT,
    generation_model VARCHAR(50),
    generation_prompt_version VARCHAR(20),
    
    -- Review information
    reviewed_by INTEGER REFERENCES users(id),
    review_feedback TEXT,
    review_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_at TIMESTAMP,
    reviewed_at TIMESTAMP,
    approved_at TIMESTAMP,
    published_at TIMESTAMP,
    
    CONSTRAINT valid_cefr_level CHECK (cefr_level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
    CONSTRAINT valid_course_status CHECK (status IN ('generating', 'pending_review', 'approved', 'needs_revision', 'rejected', 'published'))
);

-- Modules table
CREATE TABLE modules (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    
    -- Module information
    title VARCHAR(200) NOT NULL,
    description TEXT,
    objectives TEXT,
    order_num INTEGER NOT NULL,
    estimated_duration_hours INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lessons table
CREATE TABLE lessons (
    id SERIAL PRIMARY KEY,
    module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    
    -- Lesson information
    title VARCHAR(200) NOT NULL,
    objectives TEXT,
    content TEXT, -- JSON string containing lesson content
    order_num INTEGER NOT NULL,
    estimated_duration INTEGER DEFAULT 60, -- minutes
    
    -- Lesson type and skills
    lesson_type VARCHAR(20) DEFAULT 'mixed',
    skill_focus VARCHAR(100), -- JSON array of skills
    difficulty_level VARCHAR(10),
    
    -- AI metadata
    ai_generated BOOLEAN DEFAULT TRUE,
    content_source VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_lesson_type CHECK (lesson_type IN ('reading', 'listening', 'speaking', 'writing', 'grammar', 'vocabulary', 'mixed')),
    CONSTRAINT valid_difficulty CHECK (difficulty_level IN ('easy', 'medium', 'hard'))
);

-- Create indexes for better performance
CREATE INDEX idx_course_requests_created_by ON course_requests(created_by);
CREATE INDEX idx_course_requests_status ON course_requests(status);
CREATE INDEX idx_course_requests_created_at ON course_requests(created_at);

CREATE INDEX idx_sop_documents_request_id ON sop_documents(request_id);
CREATE INDEX idx_sop_documents_processing_status ON sop_documents(processing_status);

CREATE INDEX idx_courses_request_id ON courses(request_id);
CREATE INDEX idx_courses_status ON courses(status);
CREATE INDEX idx_courses_reviewed_by ON courses(reviewed_by);

CREATE INDEX idx_modules_course_id ON modules(course_id);
CREATE INDEX idx_lessons_module_id ON lessons(module_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to course_requests table
CREATE TRIGGER update_course_requests_updated_at 
    BEFORE UPDATE ON course_requests 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to lessons table
CREATE TRIGGER update_lessons_updated_at 
    BEFORE UPDATE ON lessons 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

# server/migrations/002_student_progress.sql
-- Student progress and engagement tracking

-- Student enrollments table
CREATE TABLE student_enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id),
    course_id INTEGER NOT NULL REFERENCES courses(id),
    
    -- Enrollment information
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    start_date TIMESTAMP,
    target_completion_date TIMESTAMP,
    actual_completion_date TIMESTAMP,
    
    -- Progress tracking
    status VARCHAR(20) DEFAULT 'active',
    progress_percentage FLOAT DEFAULT 0.0,
    current_lesson_id INTEGER REFERENCES lessons(id),
    
    -- Performance metrics
    total_time_spent INTEGER DEFAULT 0, -- minutes
    average_score FLOAT,
    completed_lessons INTEGER DEFAULT 0,
    total_lessons INTEGER,
    
    CONSTRAINT valid_enrollment_status CHECK (status IN ('active', 'completed', 'dropped', 'paused')),
    CONSTRAINT valid_progress CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    UNIQUE(student_id, course_id)
);

-- Student progress table
CREATE TABLE student_progress (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id),
    lesson_id INTEGER NOT NULL REFERENCES lessons(id),
    
    -- Progress information
    status VARCHAR(20) DEFAULT 'not_started',
    completion_percentage FLOAT DEFAULT 0.0,
    time_spent INTEGER DEFAULT 0, -- minutes
    
    -- Performance
    score FLOAT,
    attempts INTEGER DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_progress_status CHECK (status IN ('not_started', 'in_progress', 'completed')),
    CONSTRAINT valid_completion_percentage CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    UNIQUE(student_id, lesson_id)
);

-- Exercises table
CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    
    -- Exercise information
    title VARCHAR(200),
    exercise_type VARCHAR(30) NOT NULL,
    question TEXT NOT NULL,
    options TEXT, -- JSON array for multiple choice options
    correct_answer TEXT,
    explanation TEXT,
    order_num INTEGER NOT NULL,
    
    -- Difficulty and points
    difficulty VARCHAR(10) DEFAULT 'medium',
    points INTEGER DEFAULT 1,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_exercise_type CHECK (exercise_type IN ('multiple_choice', 'fill_blank', 'matching', 'speaking', 'writing', 'drag_drop')),
    CONSTRAINT valid_exercise_difficulty CHECK (difficulty IN ('easy', 'medium', 'hard'))
);

-- Student responses table
CREATE TABLE student_responses (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id),
    exercise_id INTEGER NOT NULL REFERENCES exercises(id),
    
    -- Response information
    answer TEXT NOT NULL,
    is_correct BOOLEAN,
    score FLOAT,
    
    -- AI feedback
    ai_feedback TEXT,
    feedback_confidence FLOAT,
    
    -- Timestamps
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trainer assignments table
CREATE TABLE trainer_assignments (
    id SERIAL PRIMARY KEY,
    trainer_id INTEGER NOT NULL REFERENCES users(id),
    course_id INTEGER NOT NULL REFERENCES courses(id),
    
    -- Assignment information
    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    
    -- Responsibilities
    responsibilities TEXT, -- JSON array of responsibilities
    notes TEXT,
    
    CONSTRAINT valid_assignment_status CHECK (status IN ('active', 'completed', 'cancelled'))
);

-- Trainer feedback table
CREATE TABLE trainer_feedback (
    id SERIAL PRIMARY KEY,
    trainer_id INTEGER NOT NULL REFERENCES users(id),
    student_id INTEGER NOT NULL REFERENCES users(id),
    response_id INTEGER REFERENCES student_responses(id),
    lesson_id INTEGER REFERENCES lessons(id),
    
    -- Feedback information
    feedback_type VARCHAR(20) NOT NULL,
    feedback_text TEXT NOT NULL,
    rating INTEGER,
    
    -- Categories for detailed feedback
    grammar_score INTEGER,
    vocabulary_score INTEGER,
    pronunciation_score INTEGER,
    fluency_score INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_feedback_type CHECK (feedback_type IN ('exercise', 'lesson', 'general', 'speaking', 'writing')),
    CONSTRAINT valid_rating CHECK (rating >= 1 AND rating <= 5),
    CONSTRAINT valid_grammar_score CHECK (grammar_score >= 1 AND grammar_score <= 5),
    CONSTRAINT valid_vocabulary_score CHECK (vocabulary_score >= 1 AND vocabulary_score <= 5),
    CONSTRAINT valid_pronunciation_score CHECK (pronunciation_score >= 1 AND pronunciation_score <= 5),
    CONSTRAINT valid_fluency_score CHECK (fluency_score >= 1 AND fluency_score <= 5)
);

-- Create indexes for student progress tables
CREATE INDEX idx_student_enrollments_student_id ON student_enrollments(student_id);
CREATE INDEX idx_student_enrollments_course_id ON student_enrollments(course_id);
CREATE INDEX idx_student_enrollments_status ON student_enrollments(status);

CREATE INDEX idx_student_progress_student_id ON student_progress(student_id);
CREATE INDEX idx_student_progress_lesson_id ON student_progress(lesson_id);
CREATE INDEX idx_student_progress_status ON student_progress(status);

CREATE INDEX idx_exercises_lesson_id ON exercises(lesson_id);
CREATE INDEX idx_exercises_type ON exercises(exercise_type);

CREATE INDEX idx_student_responses_student_id ON student_responses(student_id);
CREATE INDEX idx_student_responses_exercise_id ON student_responses(exercise_id);
CREATE INDEX idx_student_responses_submitted_at ON student_responses(submitted_at);

CREATE INDEX idx_trainer_assignments_trainer_id ON trainer_assignments(trainer_id);
CREATE INDEX idx_trainer_assignments_course_id ON trainer_assignments(course_id);

CREATE INDEX idx_trainer_feedback_trainer_id ON trainer_feedback(trainer_id);
CREATE INDEX idx_trainer_feedback_student_id ON trainer_feedback(student_id);

# server/migrations/003_notifications_audit.sql
-- Notifications and audit logging

-- Notifications table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    
    -- Notification information
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(20) DEFAULT 'info',
    
    -- Status
    read BOOLEAN DEFAULT FALSE,
    
    -- Additional data
    data TEXT, -- JSON string for additional notification data
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    
    CONSTRAINT valid_notification_type CHECK (type IN ('info', 'success', 'warning', 'error', 'urgent'))
);

-- System settings table
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    category VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    
    -- Action information
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    
    -- Details
    details TEXT, -- JSON string with action details
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for notifications and audit tables
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(read);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

CREATE INDEX idx_system_settings_key ON system_settings(key);
CREATE INDEX idx_system_settings_category ON system_settings(category);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Apply updated_at trigger to system_settings
CREATE TRIGGER update_system_settings_updated_at 
    BEFORE UPDATE ON system_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

# server/seeds/initial_data.py
from app import create_app, db
from app.models import User, SystemSettings
from werkzeug.security import generate_password_hash

def seed_initial_data():
    """Seed initial data for the application"""
    app = create_app()
    
    with app.app_context():
        # Create admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                role='admin',
                first_name='System',
                last_name='Administrator'
            )
            admin_user.set_password('admin123')  # Change in production
            db.session.add(admin_user)
            print("Created admin user")
        
        # Create demo users for each role
        demo_users = [
            {
                'username': 'sales_demo',
                'email': 'sales@example.com',
                'role': 'sales',
                'first_name': 'Demo',
                'last_name': 'Sales',
                'password': 'demo123'
            },
            {
                'username': 'manager_demo',
                'email': 'manager@example.com',
                'role': 'course_manager',
                'first_name': 'Demo',
                'last_name': 'Manager',
                'password': 'demo123'
            },
            {
                'username': 'trainer_demo',
                'email': 'trainer@example.com',
                'role': 'trainer',
                'first_name': 'Demo',
                'last_name': 'Trainer',
                'password': 'demo123'
            },
            {
                'username': 'student_demo',
                'email': 'student@example.com',
                'role': 'student',
                'first_name': 'Demo',
                'last_name': 'Student',
                'password': 'demo123'
            }
        ]
        
        for user_data in demo_users:
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    role=user_data['role'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                print(f"Created demo {user_data['role']} user")
        
        # Create system settings
        default_settings = [
            {
                'key': 'ai_model_default',
                'value': 'gpt-4',
                'description': 'Default AI model for content generation',
                'category': 'ai'
            },
            {
                'key': 'max_file_size_mb',
                'value': '50',
                'description': 'Maximum file size for SOP uploads in MB',
                'category': 'uploads'
            },
            {
                'key': 'session_timeout_hours',
                'value': '24',
                'description': 'User session timeout in hours',
                'category': 'security'
            },
            {
                'key': 'course_generation_timeout_minutes',
                'value': '30',
                'description': 'Timeout for AI course generation in minutes',
                'category': 'ai'
            },
            {
                'key': 'email_notifications_enabled',
                'value': 'true',
                'description': 'Enable email notifications',
                'category': 'notifications'
            },
            {
                'key': 'default_cefr_level',
                'value': 'A1',
                'description': 'Default CEFR level for new students',
                'category': 'courses'
            }
        ]
        
        for setting_data in default_settings:
            existing_setting = SystemSettings.query.filter_by(key=setting_data['key']).first()
            if not existing_setting:
                setting = SystemSettings(**setting_data)
                db.session.add(setting)
                print(f"Created system setting: {setting_data['key']}")
        
        db.session.commit()
        print("Initial data seeding completed successfully!")

if __name__ == '__main__':
    seed_initial_data()

# client/src/components/admin/UserManagement.jsx
import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';
import StatusBadge from '../common/StatusBadge';
import {
  UserPlusIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon
} from '@heroicons/react/24/outline';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/admin/users');
      setUsers(response.data.users || []);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.last_name?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filter === 'all' || user.role === filter;
    return matchesSearch && matchesFilter;
  });

  const getRoleColor = (role) => {
    const roleColors = {
      admin: 'bg-red-100 text-red-800',
      course_manager: 'bg-purple-100 text-purple-800',
      sales: 'bg-blue-100 text-blue-800',
      trainer: 'bg-green-100 text-green-800',
      student: 'bg-gray-100 text-gray-800'
    };
    return roleColors[role] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return <LoadingSpinner text="Loading users..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">User Management</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          <UserPlusIcon className="h-4 w-4 mr-2" />
          Add User
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Users
            </label>
            <input
              type="text"
              placeholder="Search by name, username, or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Role
            </label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Roles</option>
              <option value="admin">Admin</option>
              <option value="course_manager">Course Manager</option>
              <option value="sales">Sales</option>
              <option value="trainer">Trainer</option>
              <option value="student">Student</option>
            </select>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                User
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Role
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Login
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredUsers.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10">
                      <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                        <span className="text-sm font-medium text-gray-700">
                          {user.first_name?.[0] || user.username[0].toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">
                        {user.first_name && user.last_name 
                          ? `${user.first_name} ${user.last_name}`
                          : user.username
                        }
                      </div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleColor(user.role)}`}>
                    {user.role.replace('_', ' ').toUpperCase()}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <StatusBadge status={user.is_active ? 'active' : 'inactive'} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                  <button className="text-blue-600 hover:text-blue-900">
                    <EyeIcon className="h-4 w-4" />
                  </button>
                  <button className="text-yellow-600 hover:text-yellow-900">
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button className="text-red-600 hover:text-red-900">
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {filteredUsers.length === 0 && (
          <div className="text-center py-12">
            <UserPlusIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No users found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search or filter criteria.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserManagement;

# client/src/components/analytics/ProgressChart.jsx
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const ProgressChart = ({ data, title = "Progress Over Time" }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium">{formatDate(label)}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value}%
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tickFormatter={formatDate}
            stroke="#6B7280"
          />
          <YAxis 
            domain={[0, 100]}
            stroke="#6B7280"
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line
            type="monotone"
            dataKey="progress"
            stroke="#3B82F6"
            strokeWidth={2}
            dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ProgressChart;

# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'ai-lang-app-backend'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - default
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: backend
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__

  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
      - role: node
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true

# monitoring/prometheus/alert_rules.yml
groups:
  - name: ai-lang-app-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(flask_http_request_exceptions_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: DatabaseConnectionFailure
        expr: up{job="postgres"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failure"
          description: "PostgreSQL database is down"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is above 90%"

      - alert: DiskSpaceLow
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space"
          description: "Disk usage is above 80%"

      - alert: PodCrashLooping
        expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pod is crash looping"
          description: "Pod {{ $labels.pod }} is restarting frequently"

# monitoring/grafana/dashboards/ai-lang-app-dashboard.json
{
  "dashboard": {
    "id": null,
    "title": "AI Language Learning Platform",
    "tags": ["ai-lang-app"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(flask_http_request_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ],
        "yAxes": [
          {
            "label": "Requests per second"
          }
        ]
      },
      {
        "id": 2,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(flask_http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(flask_http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(flask_http_request_exceptions_total[5m])",
            "legendFormat": "Errors/sec"
          }
        ]
      },
      {
        "id": 4,
        "title": "Active Users",
        "type": "stat",
        "targets": [
          {
            "expr": "ai_lang_app_active_users_total",
            "legendFormat": "Active Users"
          }
        ]
      },
      {
        "id": 5,
        "title": "Course Generation Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ai_lang_app_courses_generated_total[1h])",
            "legendFormat": "Courses/hour"
          }
        ]
      },
      {
        "id": 6,
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends",
            "legendFormat": "Active connections"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}

# docs/README.md
# AI Language Learning Platform Documentation

## Overview

The AI Language Learning Platform is an innovative solution that automatically generates customized English language courses for corporate clients by analyzing their Standard Operating Procedures (SOPs) and creating CEFR-aligned content.

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL 14+
- Poetry (Python dependency management)
- Docker (optional, for containerized development)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/ai-lang-app.git
   cd ai-lang-app
   ```

2. **Run the setup script:**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. **Configure environment variables:**
   ```bash
   cp server/.env.example server/.env
   # Edit server/.env with your configuration
   ```

4. **Start the application:**
   ```bash
   # Terminal 1 - Backend
   cd server && poetry run python run.py
   
   # Terminal 2 - Frontend
   cd client && npm run dev
   ```

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │   API Gateway   │    │  Microservices  │
│   (Frontend)    │◄──►│   (Load Bal.)   │◄──►│   (Backend)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                               ┌───────▼───────┐
                                               │   Databases   │
                                               │ • PostgreSQL  │
                                               │ • MongoDB     │
                                               │ • Vector DB   │
                                               │ • Redis       │
                                               └───────────────┘
```

### Technology Stack

**Frontend:**
- React.js with TypeScript
- Tailwind CSS for styling
- React Router for navigation
- Axios for API communication
- Vite for build tooling

**Backend:**
- Python with Flask/FastAPI
- Node.js for specific services
- PostgreSQL for relational data
- MongoDB for document storage
- Redis for caching
- Vector Database (Milvus/Pinecone) for RAG

**AI/ML:**
- OpenAI GPT-4 for content generation
- Anthropic Claude for content review
- Custom embedding models for SOP processing
- RAG (Retrieval-Augmented Generation) pipeline

**Infrastructure:**
- AWS (EKS, RDS, S3, CloudFront)
- Kubernetes for orchestration
- Docker for containerization
- Terraform for infrastructure as code

## User Portals

### 1. Sales Portal
- Submit client requirements
- Upload SOP documents
- Track request status
- Generate custom course proposals

### 2. Course Manager Portal
- Review AI-generated content
- Approve/reject courses
- Manage content library
- Assign trainers and students

### 3. Trainer Portal
- Access lesson materials
- Track student progress
- Provide feedback
- Conduct live sessions

### 4. Student Portal
- Complete interactive lessons
- Take assessments
- Track personal progress
- Receive AI-powered feedback

## Core Features

### AI Course Generation
1. **SOP Analysis**: Automated processing of client documents
2. **Content Creation**: CEFR-aligned lesson generation
3. **Exercise Generation**: Interactive activities and assessments
4. **Quality Assurance**: Human review and approval workflow

### Learning Management
1. **Progress Tracking**: Real-time student analytics
2. **Adaptive Learning**: Personalized learning paths
3. **Assessment Engine**: Automated scoring and feedback
4. **Reporting**: Comprehensive analytics dashboards

## Development Workflow

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
```

### Testing
```bash
# Backend tests
cd server && poetry run pytest

# Frontend tests
cd client && npm run test

# E2E tests
cd client && npm run test:e2e
```

### Deployment
```bash
# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production
./scripts/deploy.sh production
```

## API Documentation

### Authentication
All API endpoints require authentication using JWT tokens:

```http
Authorization: Bearer <jwt_token>
```

### Core Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout

#### Course Requests
- `POST /api/sales/course-request` - Submit new request
- `GET /api/sales/requests` - List user's requests
- `GET /api/sales/requests/{id}` - Get specific request

#### Course Management
- `GET /api/course-manager/courses` - List courses for review
- `POST /api/course-manager/courses/{id}/review` - Review course
- `GET /api/course-manager/library` - Access content library

#### Student Learning
- `GET /api/student/courses` - List enrolled courses
- `GET /api/student/courses/{id}/lessons/{lesson_id}` - Get lesson content
- `POST /api/student/exercises/{id}/submit` - Submit exercise

## Database Schema

### Core Tables
- `users` - User authentication and profiles
- `course_requests` - Client course requirements
- `courses` - Generated course metadata
- `modules` - Course module structure
- `lessons` - Individual lesson content
- `exercises` - Interactive activities
- `student_progress` - Learning analytics

### Relationships
```sql
users (1:M) course_requests (1:M) courses (1:M) modules (1:M) lessons (1:M) exercises
users (1:M) student_enrollments (M:1) courses
users (1:M) student_progress (M:1) lessons
```

## Contributing

### Code Style
- Python: Follow PEP 8, use Black formatter
- JavaScript: Use ESLint with Airbnb config
- Commit messages: Follow Conventional Commits

### Pull Request Process
1. Create feature branch from `develop`
2. Implement changes with tests
3. Ensure all tests pass
4. Submit PR with detailed description
5. Address review feedback
6. Merge after approval

### Development Environment
```bash
# Install pre-commit hooks
pre-commit install

# Run linting
npm run lint        # Frontend
poetry run black .  # Backend

# Run full test suite
npm run test:ci     # Frontend
poetry run pytest  # Backend
```

## Deployment

### Environment Configuration
- **Development**: Local development with hot reload
- **Staging**: AWS EKS cluster for testing
- **Production**: AWS EKS with high availability

### Infrastructure
- Managed by Terraform
- Kubernetes deployments
- Automated CI/CD via GitHub Actions
- Blue/green deployment strategy

### Monitoring
- Prometheus for metrics collection
- Grafana for visualization
- ELK stack for log aggregation
- Custom dashboards for business metrics

## Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check database connection
psql -h localhost -U postgres -d ai_lang_db

# Verify environment variables
cat server/.env

# Check logs
poetry run python run.py
```

**Frontend build fails:**
```bash
# Clear cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Database migration errors:**
```bash
# Reset database
dropdb ai_lang_db
createdb ai_lang_db

# Run migrations
cd server && poetry run python migrations/001_initial_schema.sql
```

## Support

### Documentation
- [API Reference](./api.md)
- [Architecture Guide](./architecture.md)
- [Deployment Guide](./deployment.md)

### Getting Help
- GitHub Issues for bugs and feature requests
- Team Slack for development questions
- Email: support@example.com for urgent issues

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
