"""
Courses Domain - Schemas
Consolidated from: course.py
"""

from datetime import datetime
from pydantic import BaseModel, constr, validator
from typing import List, Optional, Dict, Any

class CourseCreateRequest(BaseModel):
    title: constr(min_length=3, max_length=255)
    description: Optional[str] = None
    cefr_level: str

    @validator('cefr_level')
    def validate_cefr_level(cls, v):
        if v not in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            raise ValueError('CEFR level must be one of: A1, A2, B1, B2, C1, C2')
        return v


class CourseUpdateRequest(BaseModel):
    title: Optional[constr(min_length=3, max_length=255)] = None
    description: Optional[str] = None
    cefr_level: Optional[str] = None

    status: Optional[str] = None

    @validator('cefr_level')
    def validate_cefr_level(cls, v):
        if v is not None and v not in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            raise ValueError('CEFR level must be one of: A1, A2, B1, B2, C1, C2')
        return v


class CourseResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    cefr_level: str
    status: str
    version: int
    created_by: int
    approved_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModuleCreateRequest(BaseModel):
    title: constr(min_length=3, max_length=255)
    description: Optional[str] = None
    sequence_number: int


class ModuleResponse(BaseModel):
    id: int
    course_id: int
    title: str
    description: Optional[str]
    sequence_number: int
    created_at: datetime

    class Config:
        from_attributes = True


class LessonCreateRequest(BaseModel):
    title: constr(min_length=3, max_length=255)
    content_id: str
    sequence_number: int
    duration_minutes: Optional[int] = None


class LessonResponse(BaseModel):
    id: int
    module_id: int
    title: str
    content_id: str
    sequence_number: int
    duration_minutes: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class CourseReviewRequest(BaseModel):
    status: str
    feedback: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v not in ['approved', 'rejected']:
            raise ValueError('Status must be either approved or rejected')
        return v


class CourseReviewResponse(BaseModel):
    id: int
    course_id: int
    reviewer_id: int
    status: str
    feedback: Optional[str]
    reviewed_at: datetime

    class Config:
        from_attributes = True


class ExerciseCreateRequest(BaseModel):
    title: constr(min_length=3, max_length=255)
    exercise_type: str
    content: Dict[str, Any]
    answers: Dict[str, Any]
    points: int = 1
    sequence_number: int


class ExerciseResponse(BaseModel):
    id: int
    lesson_id: int
    title: str
    exercise_type: str
    content: Dict[str, Any]
    points: int
    sequence_number: int
    created_at: datetime

    class Config:
        from_attributes = True


class AssessmentCreateRequest(BaseModel):
    title: constr(min_length=3, max_length=255)
    assessment_type: str
    content: Dict[str, Any]
    scoring_config: Dict[str, Any]
    time_limit_minutes: Optional[int] = None
    is_final: bool = False


class AssessmentResponse(BaseModel):
    id: int
    course_id: int
    title: str
    assessment_type: str
    content: Dict[str, Any]
    scoring_config: Dict[str, Any]
    time_limit_minutes: Optional[int]
    is_final: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CourseDetailResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    cefr_level: str
    status: str
    version: int
    created_by: int
    approved_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    modules: List[ModuleResponse]
    reviews: List[CourseReviewResponse]

    class Config:
        from_attributes = True 
