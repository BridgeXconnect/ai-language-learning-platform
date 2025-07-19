"""
Courses Domain - Models
Consolidated from: course.py, server_models_course.py
"""

from app.core.database import Base
from app.core.database import Base
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, func
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from sqlalchemy.orm import relationship

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
class CEFRLevel(Enum):
    """CEFR proficiency levels."""
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"



class CourseRequestStatus(Enum):
    """Course request lifecycle status."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    SOP_PROCESSING = "sop_processing"
    GENERATING = "generating"
    PENDING_REVIEW = "pending_review"
    NEEDS_REVISION = "needs_revision"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"



class CourseRequest(db.Model):
    """Model for custom course creation requests from sales."""
    
    __tablename__ = 'course_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Sales rep who created the request
    sales_rep_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Client information
    company_name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100))
    contact_person = db.Column(db.String(200), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20))
    
    # Training requirements
    cohort_size = db.Column(db.Integer, nullable=False)
    current_cefr = db.Column(db.Enum(CEFRLevel), nullable=False)
    target_cefr = db.Column(db.Enum(CEFRLevel), nullable=False)
    training_objectives = db.Column(db.Text, nullable=False)
    pain_points = db.Column(db.Text)
    specific_requirements = db.Column(db.Text)
    
    # Course structure preferences
    course_length_hours = db.Column(db.Integer)
    lessons_per_module = db.Column(db.Integer)
    delivery_method = db.Column(db.Enum(
        'in_person', 'virtual', 'blended',
        name='delivery_methods'
    ), default='blended')
    preferred_schedule = db.Column(db.String(200))
    
    # Status and workflow
    status = db.Column(db.Enum(CourseRequestStatus), default=CourseRequestStatus.DRAFT)
    priority = db.Column(db.Enum(
        'low', 'normal', 'high', 'urgent',
        name='request_priorities'
    ), default='normal')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    
    # Relationships
    sop_documents = db.relationship('SOPDocument', backref='course_request', lazy='dynamic', cascade='all, delete-orphan')
    generated_course = db.relationship('Course', backref='original_request', uselist=False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.request_id:
            self.request_id = self.generate_request_id()
    
    @staticmethod
    def generate_request_id():
        """Generate a unique request ID."""
        import random
        import string
        from datetime import datetime
        
        # Format: CR-YYYYMMDD-XXXX (e.g., CR-20241215-A3B7)
        date_str = datetime.utcnow().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        request_id = f"CR-{date_str}-{random_str}"
        
        # Ensure uniqueness
        while CourseRequest.query.filter_by(request_id=request_id).first():
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            request_id = f"CR-{date_str}-{random_str}"
        
        return request_id
    
    def submit(self):
        """Submit the request for processing."""
        if self.status == CourseRequestStatus.DRAFT:
            self.status = CourseRequestStatus.SUBMITTED
            self.submitted_at = datetime.utcnow()
            db.session.commit()
    
    def start_sop_processing(self):
        """Mark request as SOP processing."""
        self.status = CourseRequestStatus.SOP_PROCESSING
        db.session.commit()
    
    def start_generation(self):
        """Mark request as generating course content."""
        self.status = CourseRequestStatus.GENERATING
        db.session.commit()
    
    def ready_for_review(self):
        """Mark request as ready for course manager review."""
        self.status = CourseRequestStatus.PENDING_REVIEW
        db.session.commit()
    
    def approve(self, approved_by_id):
        """Approve the generated course."""
        self.status = CourseRequestStatus.APPROVED
        self.approved_at = datetime.utcnow()
        if self.generated_course:
            self.generated_course.approve(approved_by_id)
        db.session.commit()
    
    def reject(self, reason):
        """Reject the course request."""
        self.status = CourseRequestStatus.REJECTED
        # Create rejection record
        rejection = RequestRejection(
            course_request_id=self.id,
            reason=reason,
            rejected_at=datetime.utcnow()
        )
        db.session.add(rejection)
        db.session.commit()
    
    def request_revision(self, feedback):
        """Request revision of the generated course."""
        self.status = CourseRequestStatus.NEEDS_REVISION
        # Create revision request record
        revision = RevisionRequest(
            course_request_id=self.id,
            feedback=feedback,
            requested_at=datetime.utcnow()
        )
        db.session.add(revision)
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'request_id': self.request_id,
            'sales_rep': self.sales_rep.to_dict() if self.sales_rep else None,
            'company_name': self.company_name,
            'industry': self.industry,
            'contact_person': self.contact_person,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'cohort_size': self.cohort_size,
            'current_cefr': self.current_cefr.value if self.current_cefr else None,
            'target_cefr': self.target_cefr.value if self.target_cefr else None,
            'training_objectives': self.training_objectives,
            'pain_points': self.pain_points,
            'specific_requirements': self.specific_requirements,
            'course_length_hours': self.course_length_hours,
            'lessons_per_module': self.lessons_per_module,
            'delivery_method': self.delivery_method,
            'preferred_schedule': self.preferred_schedule,
            'status': self.status.value,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'sop_documents': [doc.to_dict() for doc in self.sop_documents],
            'generated_course': self.generated_course.to_dict() if self.generated_course else None
        }
    
    def __repr__(self):
        return f'<CourseRequest {self.request_id} - {self.company_name}>'



class SOPDocument(db.Model):
    """Model for SOP documents uploaded with course requests."""
    
    __tablename__ = 'sop_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    course_request_id = db.Column(db.Integer, db.ForeignKey('course_requests.id'), nullable=False)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    
    # Processing status
    processing_status = db.Column(db.Enum(
        'uploaded', 'processing', 'processed', 'failed',
        name='sop_processing_status'
    ), default='uploaded')
    
    # Extracted content
    extracted_text_path = db.Column(db.String(500))
    text_length = db.Column(db.Integer)
    
    # Vector embeddings
    vector_index_id = db.Column(db.String(100))  # Reference to vector DB
    embedding_model = db.Column(db.String(100))
    chunks_count = db.Column(db.Integer)
    
    # Metadata
    processing_started_at = db.Column(db.DateTime)
    processing_completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def start_processing(self):
        """Mark document as processing."""
        self.processing_status = 'processing'
        self.processing_started_at = datetime.utcnow()
        db.session.commit()
    
    def complete_processing(self, extracted_text_path, vector_index_id, chunks_count):
        """Mark document processing as complete."""
        self.processing_status = 'processed'
        self.processing_completed_at = datetime.utcnow()
        self.extracted_text_path = extracted_text_path
        self.vector_index_id = vector_index_id
        self.chunks_count = chunks_count
        db.session.commit()
    
    def fail_processing(self, error_message):
        """Mark document processing as failed."""
        self.processing_status = 'failed'
        self.error_message = error_message
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'content_type': self.content_type,
            'processing_status': self.processing_status,
            'text_length': self.text_length,
            'chunks_count': self.chunks_count,
            'created_at': self.created_at.isoformat(),
            'processing_started_at': self.processing_started_at.isoformat() if self.processing_started_at else None,
            'processing_completed_at': self.processing_completed_at.isoformat() if self.processing_completed_at else None,
            'error_message': self.error_message
        }
    
    def __repr__(self):
        return f'<SOPDocument {self.original_filename}>'



class Course(db.Model):
    """Model for generated courses."""
    
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_request_id = db.Column(db.Integer, db.ForeignKey('course_requests.id'), nullable=False)
    
    # Course metadata
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    version = db.Column(db.String(10), default='1.0', nullable=False)
    
    # Course structure
    total_modules = db.Column(db.Integer, nullable=False)
    total_lessons = db.Column(db.Integer, nullable=False)
    estimated_duration_hours = db.Column(db.Integer)
    
    # CEFR alignment
    cefr_level_range = db.Column(db.String(10))  # e.g., "A2-B1"
    
    # Status
    status = db.Column(db.Enum(
        'generating', 'pending_review', 'needs_revision', 'approved', 'published',
        name='course_status'
    ), default='generating')
    
    # Approval workflow
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    
    # AI generation metadata
    generation_model = db.Column(db.String(100))
    generation_prompt_version = db.Column(db.String(20))
    confidence_score = db.Column(db.Float)
    
    # Timestamps
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])
    modules = db.relationship('CourseModule', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    enrollments = db.relationship('StudentEnrollment', backref='course', lazy='dynamic')
    
    def approve(self, approved_by_id):
        """Approve the course for use."""
        self.status = 'approved'
        self.approved_by_id = approved_by_id
        self.approved_at = datetime.utcnow()
        db.session.commit()
    
    def publish(self):
        """Publish the course for student enrollment."""
        if self.status == 'approved':
            self.status = 'published'
            db.session.commit()
    
    def request_revision(self):
        """Mark course as needing revision."""
        self.status = 'needs_revision'
        db.session.commit()
    
    def to_dict(self, include_content=False):
        """Convert to dictionary representation."""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'version': self.version,
            'total_modules': self.total_modules,
            'total_lessons': self.total_lessons,
            'estimated_duration_hours': self.estimated_duration_hours,
            'cefr_level_range': self.cefr_level_range,
            'status': self.status,
            'approved_by': self.approved_by.to_dict() if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'generation_model': self.generation_model,
            'confidence_score': self.confidence_score,
            'generated_at': self.generated_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_content:
            data['modules'] = [module.to_dict(include_content=True) for module in self.modules]
        
        return data
    
    def __repr__(self):
        return f'<Course {self.title} (v{self.version})>'



class RequestRejection(db.Model):
    """Model for tracking course request rejections."""
    
    __tablename__ = 'request_rejections'
    
    id = db.Column(db.Integer, primary_key=True)
    course_request_id = db.Column(db.Integer, db.ForeignKey('course_requests.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    rejected_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rejected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    rejected_by = db.relationship('User')
    
    def __repr__(self):
        return f'<RequestRejection {self.course_request_id}>'



class RevisionRequest(db.Model):
    """Model for tracking course revision requests."""
    
    __tablename__ = 'revision_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    course_request_id = db.Column(db.Integer, db.ForeignKey('course_requests.id'), nullable=False)
    feedback = db.Column(db.Text, nullable=False)
    requested_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    requested_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    addressed = db.Column(db.Boolean, default=False)
    addressed_at = db.Column(db.DateTime)
    
    # Relationships
    requested_by = db.relationship('User')
    
    def mark_addressed(self):
        """Mark revision as addressed."""
        self.addressed = True
        self.addressed_at = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<RevisionRequest {self.course_request_id}>'
