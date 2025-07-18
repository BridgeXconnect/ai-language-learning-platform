"""
Pydantic schemas for AI-related operations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, validator

class DocumentProcessingRequest(BaseModel):
    """Request for processing a document."""
    file_name: str
    content_type: str = "application/pdf"
    
    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        ]
        if v not in allowed_types:
            raise ValueError(f'Content type must be one of: {allowed_types}')
        return v

class DocumentProcessingResponse(BaseModel):
    """Response from document processing."""
    success: bool
    file_name: str
    word_count: int
    char_count: int
    chunks_created: int
    key_terms: List[Dict[str, Any]]
    processing_time_seconds: float
    error_message: Optional[str] = None

class CourseGenerationRequest(BaseModel):
    """Request for AI course generation."""
    course_request_id: int
    duration_weeks: int = 8
    lessons_per_week: int = 2
    exercise_count_per_lesson: int = 5
    include_assessments: bool = True
    ai_model: str = "gpt-4o-mini"
    temperature: float = 0.3
    force_regenerate: bool = False

    @validator('duration_weeks')
    def validate_duration(cls, v):
        if not 1 <= v <= 24:
            raise ValueError('Duration must be between 1 and 24 weeks')
        return v
    
    @validator('lessons_per_week')
    def validate_lessons(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Lessons per week must be between 1 and 5')
        return v
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v

class CourseGenerationResponse(BaseModel):
    """Response from course generation."""
    success: bool
    course_id: Optional[int] = None
    course_title: Optional[str] = None
    modules_created: int = 0
    lessons_created: int = 0
    exercises_created: int = 0
    assessments_created: int = 0
    indexed_sources: int = 0
    generation_time_seconds: float
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class RAGSearchRequest(BaseModel):
    """Request for RAG content search."""
    query: str
    source_ids: Optional[List[str]] = None
    max_results: int = 5
    min_score: float = 0.3
    content_type: str = "general"
    
    @validator('query')
    def validate_query(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Query must be at least 3 characters long')
        return v.strip()
    
    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = ["general", "vocabulary", "procedures", "guidelines", "examples"]
        if v not in allowed_types:
            raise ValueError(f'Content type must be one of: {allowed_types}')
        return v

class RAGSearchResponse(BaseModel):
    """Response from RAG search."""
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    search_time_seconds: float
    
    class Config:
        from_attributes = True

class ContentGenerationRequest(BaseModel):
    """Request for AI content generation."""
    content_type: str
    context: Dict[str, Any]
    parameters: Dict[str, Any] = {}
    
    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = ["curriculum", "lesson", "exercise", "assessment", "vocabulary"]
        if v not in allowed_types:
            raise ValueError(f'Content type must be one of: {allowed_types}')
        return v

class ContentGenerationResponse(BaseModel):
    """Response from content generation."""
    success: bool
    content_type: str
    content: Dict[str, Any]
    generation_time_seconds: float
    tokens_used: Optional[int] = None
    error_message: Optional[str] = None

class CourseAnalysisRequest(BaseModel):
    """Request for course content analysis."""
    course_id: int
    analysis_type: str = "coverage"
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        allowed_types = ["coverage", "difficulty", "completeness", "engagement"]
        if v not in allowed_types:
            raise ValueError(f'Analysis type must be one of: {allowed_types}')
        return v

class CourseAnalysisResponse(BaseModel):
    """Response from course analysis."""
    course_id: int
    analysis_type: str
    results: Dict[str, Any]
    recommendations: List[str]
    overall_score: float
    analysis_time_seconds: float

class AIServiceStatus(BaseModel):
    """Status of AI services."""
    ai_service_available: bool
    rag_service_available: bool
    document_processor_available: bool
    openai_configured: bool
    anthropic_configured: bool
    vector_store_stats: Dict[str, Any]
    
    class Config:
        from_attributes = True

class ComponentRegenerationRequest(BaseModel):
    """Request for regenerating a course component."""
    course_id: int
    component_type: str
    component_id: int
    config: Dict[str, Any] = {}
    
    @validator('component_type')
    def validate_component_type(cls, v):
        allowed_types = ["module", "lesson", "exercise", "assessment"]
        if v not in allowed_types:
            raise ValueError(f'Component type must be one of: {allowed_types}')
        return v

class ComponentRegenerationResponse(BaseModel):
    """Response from component regeneration."""
    success: bool
    component_type: str
    component_id: int
    regenerated_at: datetime
    changes_made: List[str]
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class VocabularyExtractionRequest(BaseModel):
    """Request for vocabulary extraction from content."""
    text: str
    cefr_level: str = "B1"
    max_terms: int = 50
    include_phrases: bool = True
    
    @validator('cefr_level')
    def validate_cefr_level(cls, v):
        if v not in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            raise ValueError('CEFR level must be one of: A1, A2, B1, B2, C1, C2')
        return v
    
    @validator('text')
    def validate_text(cls, v):
        if len(v.strip()) < 100:
            raise ValueError('Text must be at least 100 characters long')
        return v.strip()

class VocabularyExtractionResponse(BaseModel):
    """Response from vocabulary extraction."""
    cefr_level: str
    vocabulary_terms: List[Dict[str, Any]]
    total_terms: int
    phrases_included: bool
    processing_time_seconds: float

class LessonPlanRequest(BaseModel):
    """Request for detailed lesson plan generation."""
    lesson_title: str
    module_context: str
    vocabulary_themes: List[str]
    grammar_focus: List[str]
    cefr_level: str
    duration_minutes: int = 60
    learning_style: str = "mixed"
    
    @validator('cefr_level')
    def validate_cefr_level(cls, v):
        if v not in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            raise ValueError('CEFR level must be one of: A1, A2, B1, B2, C1, C2')
        return v
    
    @validator('learning_style')
    def validate_learning_style(cls, v):
        allowed_styles = ["visual", "auditory", "kinesthetic", "mixed"]
        if v not in allowed_styles:
            raise ValueError(f'Learning style must be one of: {allowed_styles}')
        return v

class LessonPlanResponse(BaseModel):
    """Response from lesson plan generation."""
    lesson_title: str
    duration_minutes: int
    lesson_plan: Dict[str, Any]
    activities: List[Dict[str, Any]]
    materials_needed: List[str]
    learning_objectives: List[str]
    assessment_criteria: List[str]
    
    class Config:
        from_attributes = True

class ProgressTrackingUpdate(BaseModel):
    """Update for generation progress tracking."""
    task_id: str
    status: str
    progress_percentage: int
    current_step: str
    estimated_completion: Optional[datetime] = None
    details: Dict[str, Any] = {}
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ["pending", "in_progress", "completed", "failed", "cancelled"]
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {allowed_statuses}')
        return v
    
    @validator('progress_percentage')
    def validate_progress(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Progress percentage must be between 0 and 100')
        return v