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
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class CEFRLevelEnum(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

class DeliveryMethodEnum(str, Enum):
    IN_PERSON = "in_person"
    VIRTUAL = "virtual"
    BLENDED = "blended"

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
    training_objectives: constr(min_length=10)
    pain_points: Optional[str] = None
    specific_requirements: Optional[str] = None
    
    # Course Structure Preferences
    course_length_hours: Optional[int] = None
    lessons_per_module: Optional[int] = None
    delivery_method: Optional[DeliveryMethodEnum] = None
    preferred_schedule: Optional[str] = None
    
    # Request Management
    priority: PriorityEnum = PriorityEnum.NORMAL
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