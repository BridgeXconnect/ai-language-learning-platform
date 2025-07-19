from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class RequestStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CEFRLevelEnum(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

class DeliveryMethodEnum(str, Enum):
    IN_PERSON = "IN_PERSON"
    VIRTUAL = "VIRTUAL"
    BLENDED = "BLENDED"

class UrgencyLevelEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CourseRequestCreateRequest(BaseModel):
    # Client Information
    company_name: constr(min_length=2, max_length=200)
    industry: Optional[constr(max_length=100)] = None
    contact_person: constr(min_length=2, max_length=200)
    contact_email: EmailStr
    contact_phone: Optional[constr(max_length=20)] = None
    
    # Training Requirements
    cohort_size: int
    current_cefr: CEFRLevelEnum
    target_cefr: CEFRLevelEnum
    training_objectives: constr(min_length=10, max_length=500)
    pain_points: Optional[constr(max_length=300)] = None
    specific_requirements: Optional[str] = None
    
    # Course Structure Preferences
    course_length_hours: Optional[int] = None
    lessons_per_module: Optional[int] = None
    delivery_method: Optional[DeliveryMethodEnum] = None
    preferred_schedule: Optional[str] = None
    
    # Request Management
    priority: PriorityEnum = PriorityEnum.MEDIUM
    internal_notes: Optional[str] = None

    @validator('cohort_size')
    def validate_cohort_size(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('Cohort size must be between 1 and 1000')
        return v

    @validator('course_length_hours')
    def validate_course_length(cls, v):
        if v is not None and (v < 1 or v > 500):
            raise ValueError('Course length must be between 1 and 500 hours')
        return v
    
    @validator('target_cefr')
    def validate_cefr_progression(cls, v, values):
        if 'current_cefr' in values:
            current = values['current_cefr']
            target = v
            
            # Define CEFR level hierarchy
            levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
            
            if current not in levels or target not in levels:
                return v
            
            current_index = levels.index(current)
            target_index = levels.index(target)
            
            # Check for regression (going backwards)
            if target_index < current_index:
                raise ValueError('Target CEFR level must be same or higher than current level')
            
            # Check for too many levels jump (more than 2 levels)
            if target_index - current_index > 2:
                raise ValueError('CEFR progression cannot exceed max 2 levels progression')
        
        return v

class CourseRequestUpdateRequest(BaseModel):
    # All fields optional for updates
    company_name: Optional[constr(min_length=2, max_length=200)] = None
    industry: Optional[constr(max_length=100)] = None
    contact_person: Optional[constr(min_length=2, max_length=200)] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[constr(max_length=20)] = None
    cohort_size: Optional[int] = None
    current_cefr: Optional[CEFRLevelEnum] = None
    target_cefr: Optional[CEFRLevelEnum] = None
    training_objectives: Optional[constr(min_length=10)] = None
    pain_points: Optional[str] = None
    specific_requirements: Optional[str] = None
    course_length_hours: Optional[int] = None
    lessons_per_module: Optional[int] = None
    delivery_method: Optional[DeliveryMethodEnum] = None
    preferred_schedule: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    internal_notes: Optional[str] = None

class CourseRequestWizardRequest(BaseModel):
    """Comprehensive course request schema for the wizard submission"""
    
    # Client Information
    company_name: constr(min_length=2, max_length=200)
    industry: constr(min_length=1, max_length=100)
    company_size: constr(min_length=1, max_length=100)
    location: constr(min_length=2, max_length=200)
    website: Optional[str] = None
    
    # Contact Information
    contact_person: constr(min_length=2, max_length=200)
    contact_email: EmailStr
    contact_phone: constr(min_length=10, max_length=20)
    decision_maker: constr(min_length=2, max_length=200)
    decision_maker_role: constr(min_length=2, max_length=200)
    
    # Project Information
    project_title: constr(min_length=5, max_length=300)
    project_description: constr(min_length=20)
    estimated_budget: constr(min_length=1, max_length=100)
    timeline: constr(min_length=1, max_length=100)
    urgency: UrgencyLevelEnum
    has_existing_training: bool = False
    existing_training_description: Optional[str] = None
    
    # Training Requirements
    participant_count: int
    current_english_level: CEFRLevelEnum
    target_english_level: CEFRLevelEnum
    target_roles: List[str]
    communication_scenarios: List[str]
    training_goals: constr(min_length=20)
    specific_challenges: constr(min_length=10)
    success_metrics: constr(min_length=10)
    
    @validator('participant_count')
    def validate_participant_count(cls, v):
        if v < 1 or v > 10000:
            raise ValueError('Participant count must be between 1 and 10,000')
        return v
    
    @validator('target_roles')
    def validate_target_roles(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one target role must be selected')
        return v
    
    @validator('communication_scenarios') 
    def validate_communication_scenarios(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one communication scenario must be selected')
        return v
    
    @validator('website')
    def validate_website(cls, v):
        if v and v.strip():
            # Simple URL validation
            if not (v.startswith('http://') or v.startswith('https://') or v.startswith('www.')):
                raise ValueError('Website must be a valid URL')
        return v

class SOPDocumentResponse(BaseModel):
    id: int
    request_id: int
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    processing_status: str
    extraction_status: str
    extracted_text_preview: Optional[str]
    upload_notes: Optional[str]
    processing_error: Optional[str]
    uploaded_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True

class CourseRequestResponse(BaseModel):
    id: int
    sales_user_id: int
    
    # Client Information
    company_name: str
    industry: Optional[str]
    contact_person: str
    contact_email: str
    contact_phone: Optional[str]
    
    # Training Requirements
    cohort_size: int
    current_cefr: str
    target_cefr: str
    training_objectives: str
    pain_points: Optional[str]
    specific_requirements: Optional[str]
    
    # Course Structure Preferences
    course_length_hours: Optional[int]
    lessons_per_module: Optional[int]
    delivery_method: Optional[str]
    preferred_schedule: Optional[str]
    
    # Request Management
    priority: str
    status: str
    internal_notes: Optional[str]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    
    # Related data
    sop_documents: List[SOPDocumentResponse] = []

    class Config:
        from_attributes = True

class CourseRequestDetailResponse(CourseRequestResponse):
    # Additional details for single request view
    sales_user_name: Optional[str] = None
    generated_course_id: Optional[int] = None
    generated_course_title: Optional[str] = None

class ClientFeedbackCreateRequest(BaseModel):
    feedback_type: str
    rating: Optional[int] = None
    feedback_text: constr(min_length=10)
    areas_of_concern: Optional[str] = None
    suggestions: Optional[str] = None
    feedback_by: Optional[str] = None
    feedback_email: Optional[EmailStr] = None

    @validator('feedback_type')
    def validate_feedback_type(cls, v):
        if v not in ['initial', 'revision', 'final']:
            raise ValueError('Feedback type must be one of: initial, revision, final')
        return v

    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v

class ClientFeedbackResponse(BaseModel):
    id: int
    request_id: int
    feedback_type: str
    rating: Optional[int]
    feedback_text: str
    areas_of_concern: Optional[str]
    suggestions: Optional[str]
    feedback_by: Optional[str]
    feedback_email: Optional[str]
    is_addressed: bool
    response_notes: Optional[str]
    created_at: datetime
    addressed_at: Optional[datetime]

    class Config:
        from_attributes = True

class SalesDashboardStats(BaseModel):
    total_requests: int
    active_requests: int
    completed_requests: int
    pending_review: int
    requests_this_month: int
    conversion_rate: float
    avg_processing_time_days: float
    priority_breakdown: Dict[str, int]
    status_breakdown: Dict[str, int]

class SOPUploadResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    processing_status: str
    message: str 