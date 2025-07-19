"""
Database Models for AI Language Learning Platform
Created by: James (BMAD Developer)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, DECIMAL, func, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

# Association table with integer role_id
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"))
)

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    status = Column(String(20), nullable=False, default="active")
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user_roles_rel = relationship("Role", secondary="user_roles", back_populates="users")
    created_courses = relationship("Course", foreign_keys="Course.created_by", back_populates="creator")
    approved_courses = relationship("Course", foreign_keys="Course.approved_by", back_populates="approver")
    user_progress = relationship("UserProgress", back_populates="user")
    assessment_results = relationship("AssessmentResult", back_populates="user")
    ai_chat_sessions = relationship("AIChatSession", back_populates="user")

    @property
    def roles(self):
        return self.user_roles_rel

    def has_role(self, role_name: str) -> bool:
        return any(role.name == role_name for role in self.roles)

    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'status': self.status,
            'email_verified': self.email_verified,
            'roles': [role.name for role in self.user_roles_rel],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

    # Relationships
    users = relationship('User', secondary='user_roles', back_populates='user_roles_rel')

    def __repr__(self):
        return f"<Role {self.name}>"

class Course(Base):
    __tablename__ = 'courses'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    cefr_level = Column(String(10), nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    version = Column(Integer, nullable=False, default=1)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    ai_generated = Column(Boolean, default=False)
    generation_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="course", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_courses")
    approver = relationship("User", foreign_keys=[approved_by], back_populates="approved_courses")
    user_progress = relationship("UserProgress", back_populates="course")

    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'cefr_level': self.cefr_level,
            'status': self.status,
            'version': self.version,
            'ai_generated': self.ai_generated,
            'generation_metadata': self.generation_metadata,
            'created_by': str(self.created_by) if self.created_by else None,
            'approved_by': str(self.approved_by) if self.approved_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Module(Base):
    __tablename__ = 'modules'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    sequence_number = Column(Integer, nullable=False)
    duration_hours = Column(Integer, default=4)
    learning_objectives = Column(JSONB)
    vocabulary_themes = Column(JSONB)
    grammar_focus = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': str(self.id),
            'course_id': str(self.course_id),
            'title': self.title,
            'description': self.description,
            'sequence_number': self.sequence_number,
            'duration_hours': self.duration_hours,
            'learning_objectives': self.learning_objectives,
            'vocabulary_themes': self.vocabulary_themes,
            'grammar_focus': self.grammar_focus,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(UUID(as_uuid=True), ForeignKey('modules.id'), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(JSONB, nullable=False)
    sequence_number = Column(Integer, nullable=False)
    duration_minutes = Column(Integer)
    lesson_type = Column(String(50), default='interactive')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    module = relationship("Module", back_populates="lessons")
    user_progress = relationship("UserProgress", back_populates="lesson")

    def to_dict(self):
        return {
            'id': str(self.id),
            'module_id': str(self.module_id),
            'title': self.title,
            'content': self.content,
            'sequence_number': self.sequence_number,
            'duration_minutes': self.duration_minutes,
            'lesson_type': self.lesson_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Assessment(Base):
    __tablename__ = 'assessments'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    title = Column(String(255), nullable=False)
    assessment_type = Column(String(50), nullable=False)
    content = Column(JSONB, nullable=False)
    scoring_config = Column(JSONB)
    time_limit_minutes = Column(Integer)
    is_final = Column(Boolean, default=False)
    pass_threshold = Column(Integer, default=70)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    course = relationship("Course", back_populates="assessments")
    results = relationship("AssessmentResult", back_populates="assessment")

    def to_dict(self):
        return {
            'id': str(self.id),
            'course_id': str(self.course_id),
            'title': self.title,
            'assessment_type': self.assessment_type,
            'content': self.content,
            'scoring_config': self.scoring_config,
            'time_limit_minutes': self.time_limit_minutes,
            'is_final': self.is_final,
            'pass_threshold': self.pass_threshold,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserProgress(Base):
    __tablename__ = 'user_progress'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey('lessons.id'), nullable=False)
    progress_percentage = Column(DECIMAL(5,2), default=0)
    time_spent_minutes = Column(Integer, default=0)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="user_progress")
    course = relationship("Course", back_populates="user_progress")
    lesson = relationship("Lesson", back_populates="user_progress")

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'course_id': str(self.course_id),
            'lesson_id': str(self.lesson_id),
            'progress_percentage': float(self.progress_percentage) if self.progress_percentage else 0,
            'time_spent_minutes': self.time_spent_minutes,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AssessmentResult(Base):
    __tablename__ = 'assessment_results'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey('assessments.id'), nullable=False)
    score = Column(DECIMAL(5,2))
    answers = Column(JSONB)
    time_taken_minutes = Column(Integer)
    passed = Column(Boolean)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="assessment_results")
    assessment = relationship("Assessment", back_populates="results")

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'assessment_id': str(self.assessment_id),
            'score': float(self.score) if self.score else None,
            'answers': self.answers,
            'time_taken_minutes': self.time_taken_minutes,
            'passed': self.passed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class AIChatSession(Base):
    __tablename__ = 'ai_chat_sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'))
    session_data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="ai_chat_sessions")

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'course_id': str(self.course_id) if self.course_id else None,
            'session_data': self.session_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 