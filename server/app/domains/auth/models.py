"""
Auth Domain - Models
Consolidated from: user.py, server_models_user.py
"""

from app.core.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Boolean, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

# Association table for user roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user_roles_rel = relationship("Role", secondary=user_roles, back_populates="users")
    course_requests = relationship("CourseRequest", back_populates="sales_user", lazy="dynamic")
    created_courses = relationship("Course", foreign_keys="Course.created_by", back_populates="creator", lazy="dynamic") 
    approved_courses = relationship("Course", foreign_keys="Course.approved_by", back_populates="approver", lazy="dynamic")

    @property
    def roles(self):
        return self.user_roles_rel

    def has_role(self, role_name: str) -> bool:
        return any(role.name == role_name for role in self.roles)

    def has_permission(self, permission_name: str) -> bool:
        for role in self.roles:
            if any(perm.name == permission_name for perm in role.permissions):
                return True
        return False

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'status': self.status,
            'roles': [role.name for role in self.user_roles_rel],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

    # Relationships
    users = relationship('User', secondary=user_roles, back_populates='user_roles_rel')
    permissions = relationship('Permission', secondary='role_permissions')

    def __repr__(self):
        return f"<Role {self.name}>"


class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))

    def __repr__(self):
        return f"<Permission {self.name}>"

# Association table for role permissions
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
) 
class UserExtended(Base):
    """Extended User model for authentication and authorization."""
    
    __tablename__ = 'users_extended'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(
        'admin', 'sales', 'course_manager', 'trainer', 'student',
        name='user_roles'
    ), nullable=False, default='student')
    
    # Profile information
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    avatar_url = Column(String(255))
    
    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course_requests = relationship('CourseRequest', back_populates='sales_rep', lazy='dynamic')
    trainer_assignments = relationship('TrainerAssignment', back_populates='trainer', lazy='dynamic')
    student_enrollments = relationship('StudentEnrollment', back_populates='student', lazy='dynamic')
    
    def __init__(self, username, email, password, role='student', **kwargs):
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        # Note: session commit should be handled by the service layer
    
    @property
    def full_name(self):
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'admin'
    
    @property
    def is_sales(self):
        """Check if user is a sales representative."""
        return self.role == 'sales'
    
    @property
    def is_course_manager(self):
        """Check if user is a course manager."""
        return self.role == 'course_manager'
    
    @property
    def is_trainer(self):
        """Check if user is a trainer."""
        return self.role == 'trainer'
    
    @property
    def is_student(self):
        """Check if user is a student."""
        return self.role == 'student'
    
    def has_permission(self, permission):
        """Check if user has a specific permission."""
        role_permissions = {
            'admin': [
                'manage_users', 'manage_courses', 'view_analytics', 
                'manage_system', 'access_all_portals'
            ],
            'sales': [
                'create_course_requests', 'upload_sops', 'view_own_requests'
            ],
            'course_manager': [
                'review_courses', 'approve_courses', 'manage_content_library',
                'assign_trainers', 'view_course_analytics'
            ],
            'trainer': [
                'view_assigned_courses', 'access_lesson_plans', 'track_student_progress',
                'provide_feedback'
            ],
            'student': [
                'access_enrolled_courses', 'complete_exercises', 'view_progress',
                'submit_assessments'
            ]
        }
        
        return permission in role_permissions.get(self.role, [])
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary representation."""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    @classmethod
    def create_user(cls, username, email, password, role='student', **kwargs):
        """Create a new user with validation."""
        # Check if username or email already exists
        existing_user = cls.query.filter(
            (cls.username == username) | (cls.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                raise ValueError("Username already exists")
            if existing_user.email == email:
                raise ValueError("Email already exists")
        
        # Create new user
        user = cls(username=username, email=email, password=password, role=role, **kwargs)
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @classmethod
    def get_by_username_or_email(cls, identifier):
        """Get user by username or email."""
        return cls.query.filter(
            (cls.username == identifier) | (cls.email == identifier)
        ).first()
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'



class UserSession(Base):
    """Track user sessions for security and analytics."""
    
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationship
    user = relationship('User', back_populates='sessions')
    
    def __repr__(self):
        return f'<UserSession {self.user.username} - {self.ip_address}>'



class PasswordResetToken(Base):
    """Manage password reset tokens."""
    
    __tablename__ = 'password_reset_tokens'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    
    # Relationship
    user = relationship('User', back_populates='reset_tokens')
    
    @property
    def is_expired(self):
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if token is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired
    
    def mark_as_used(self):
        """Mark token as used."""
        self.is_used = True
        db.session.commit()
    
    def __repr__(self):
        return f'<PasswordResetToken {self.user.username}>'
