from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    cefr_level = Column(String(10), nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    version = Column(Integer, nullable=False, default=1)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    approved_by = Column(Integer, ForeignKey('users.id'))
    course_request_id = Column(Integer, ForeignKey("course_requests.id"))
    ai_generated = Column(Boolean, default=False)
    generation_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    reviews = relationship("CourseReview", back_populates="course", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_courses")
    approver = relationship("User", foreign_keys=[approved_by], back_populates="approved_courses")
    assessments = relationship("Assessment", back_populates="course", cascade="all, delete-orphan")
    course_request = relationship("CourseRequest", foreign_keys=[course_request_id], back_populates="generated_course")

class Module(Base):
    __tablename__ = 'modules'

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    sequence_number = Column(Integer, nullable=False)
    duration_hours = Column(Integer, default=4)
    learning_objectives = Column(JSON)
    vocabulary_themes = Column(JSON)
    grammar_focus = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")

class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=False)
    title = Column(String(255), nullable=False)
    content_id = Column(String(100))  # References MongoDB content
    sequence_number = Column(Integer, nullable=False)
    duration_minutes = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    module = relationship("Module", back_populates="lessons")

class CourseReview(Base):
    __tablename__ = 'course_reviews'

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(50), nullable=False)
    feedback = Column(Text)
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="reviews")
    reviewer = relationship("User")

class Exercise(Base):
    __tablename__ = 'exercises'

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False)
    title = Column(String(255), nullable=False)
    exercise_type = Column(String(50), nullable=False)  # multiple_choice, fill_blank, etc.
    content = Column(JSON)  # Exercise content and options
    answers = Column(JSON)  # Correct answers
    points = Column(Integer, default=1)
    sequence_number = Column(Integer, nullable=False)
    instructions = Column(Text)
    feedback = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    lesson = relationship("Lesson")

class Assessment(Base):
    __tablename__ = 'assessments'

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    title = Column(String(255), nullable=False)
    assessment_type = Column(String(50), nullable=False)  # quiz, test, assignment
    content = Column(JSON)  # Assessment questions and structure
    scoring_config = Column(JSON)  # Scoring rules and weights
    time_limit_minutes = Column(Integer)
    is_final = Column(Boolean, default=False)
    instructions = Column(Text)
    pass_threshold = Column(Integer, default=70)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="assessments") 