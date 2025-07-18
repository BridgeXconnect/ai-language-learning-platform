from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .user import Base
import enum

class RequestStatus(enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    GENERATION_IN_PROGRESS = "generation_in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Priority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CEFRLevel(enum.Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

class DeliveryMethod(enum.Enum):
    IN_PERSON = "IN_PERSON"
    VIRTUAL = "VIRTUAL"
    BLENDED = "BLENDED"

class UrgencyLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class CourseRequest(Base):
    __tablename__ = "course_requests"

    id = Column(Integer, primary_key=True, index=True)
    sales_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Client Information
    company_name = Column(String(200), nullable=False)
    industry = Column(String(100))
    company_size = Column(String(100))
    location = Column(String(200))
    website = Column(String(500))
    
    # Contact Information
    contact_person = Column(String(200), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(20))
    decision_maker = Column(String(200))
    decision_maker_role = Column(String(200))
    
    # Project Information
    project_title = Column(String(300), nullable=False)
    project_description = Column(Text, nullable=False)
    estimated_budget = Column(String(100))
    timeline = Column(String(100))
    urgency = Column(Enum(UrgencyLevel), nullable=False, default=UrgencyLevel.MEDIUM)
    has_existing_training = Column(Boolean, default=False)
    existing_training_description = Column(Text)
    
    # Training Requirements
    participant_count = Column(Integer, nullable=False)
    current_english_level = Column(Enum(CEFRLevel), nullable=False)
    target_english_level = Column(Enum(CEFRLevel), nullable=False)
    target_roles = Column(JSON)  # Array of role names
    communication_scenarios = Column(JSON)  # Array of scenario names
    training_goals = Column(Text, nullable=False)
    specific_challenges = Column(Text)
    success_metrics = Column(Text)
    
    # Legacy fields (kept for backwards compatibility)
    cohort_size = Column(Integer)  # Maps to participant_count
    current_cefr = Column(Enum(CEFRLevel))  # Maps to current_english_level
    target_cefr = Column(Enum(CEFRLevel))  # Maps to target_english_level
    training_objectives = Column(Text)  # Maps to training_goals
    pain_points = Column(Text)  # Maps to specific_challenges
    specific_requirements = Column(Text)
    
    # Course Structure Preferences
    course_length_hours = Column(Integer)
    lessons_per_module = Column(Integer)
    delivery_method = Column(Enum(DeliveryMethod))
    preferred_schedule = Column(Text)
    
    # Request Management
    priority = Column(Enum(Priority), nullable=False, default=Priority.MEDIUM)
    status = Column(Enum(RequestStatus), nullable=False, default=RequestStatus.DRAFT)
    internal_notes = Column(Text)
    
    # Workflow Integration
    workflow_id = Column(String(100))  # Links to agent orchestrator workflow
    generation_progress = Column(Float)  # Progress percentage (0-100)
    quality_score = Column(Float)  # AI-generated quality score
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True))
    
    # Relationships
    sales_user = relationship("User", back_populates="course_requests")
    sop_documents = relationship("SOPDocument", back_populates="course_request", cascade="all, delete-orphan")
    generated_course = relationship("Course", foreign_keys="Course.course_request_id", back_populates="course_request", uselist=False)

class SOPDocument(Base):
    __tablename__ = "sop_documents"

    id = Column(Integer, primary_key=True, index=True)
    course_request_id = Column(Integer, ForeignKey("course_requests.id"), nullable=False)
    
    # File Information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500))  # Local file path for development
    s3_key = Column(String(500))  # S3 key for production
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Processing Status
    processing_status = Column(String(50), nullable=False, default="pending")
    vector_db_id = Column(String(100))
    extraction_status = Column(String(50), default="pending")
    extracted_text_preview = Column(Text)
    
    # Metadata
    upload_notes = Column(Text)
    processing_error = Column(Text)
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    course_request = relationship("CourseRequest", back_populates="sop_documents")

class ClientFeedback(Base):
    __tablename__ = "client_feedback"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("course_requests.id"), nullable=False)
    
    # Feedback Details
    feedback_type = Column(String(50), nullable=False)  # initial, revision, final
    rating = Column(Integer)  # 1-5 scale
    feedback_text = Column(Text, nullable=False)
    areas_of_concern = Column(Text)
    suggestions = Column(Text)
    
    # Contact Information
    feedback_by = Column(String(200))  # Client contact person
    feedback_email = Column(String(255))
    
    # Status
    is_addressed = Column(Boolean, default=False)
    response_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    addressed_at = Column(DateTime(timezone=True))
    
    # Relationships
    course_request = relationship("CourseRequest") 