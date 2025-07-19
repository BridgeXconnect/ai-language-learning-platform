"""
FastAPI server wrapper for Content Creator Agent
Provides HTTP endpoints for content generation and management
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import uvicorn
import asyncio
from datetime import datetime

from main import ContentCreatorService, ContentCreationRequest, LessonContent, ExerciseContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Content Creator Agent",
    description="AI agent for creating engaging lessons, exercises, and learning materials",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service
content_creator_service = ContentCreatorService()

# Pydantic models for API
class CreateLessonRequest(BaseModel):
    course_id: int
    module_id: Optional[int] = None
    lesson_title: str
    module_context: str
    vocabulary_themes: List[str]
    grammar_focus: List[str]
    cefr_level: str
    duration_minutes: int = 60
    company_context: Optional[Dict[str, Any]] = None

class CreateExerciseRequest(BaseModel):
    lesson_context: Dict[str, Any]
    exercise_types: List[str]
    exercise_count: int = 5
    cefr_level: str

class CreateAssessmentRequest(BaseModel):
    course_context: Dict[str, Any]
    assessment_type: str = "lesson"
    duration_minutes: int = 30

class ContentResponse(BaseModel):
    success: bool
    content: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    generation_time_seconds: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    agent: str
    version: str
    timestamp: str
    capabilities: Dict[str, Any]

class StatusResponse(BaseModel):
    agent_name: str
    status: str
    uptime_seconds: float
    requests_processed: int
    last_activity: Optional[str] = None

# Global metrics
start_time = datetime.utcnow()
requests_processed = 0
last_activity = None

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global last_activity
    last_activity = datetime.utcnow().isoformat()
    
    capabilities = await content_creator_service.get_content_capabilities()
    
    return HealthResponse(
        status="healthy",
        agent="Content Creator Agent",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        capabilities=capabilities
    )

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get detailed agent status."""
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    return StatusResponse(
        agent_name="Content Creator Agent",
        status="active",
        uptime_seconds=uptime,
        requests_processed=requests_processed,
        last_activity=last_activity
    )

@app.get("/capabilities")
async def get_capabilities():
    """Get agent capabilities and supported features."""
    return await content_creator_service.get_content_capabilities()

@app.post("/create-lesson", response_model=ContentResponse)
async def create_lesson(request: CreateLessonRequest):
    """Create comprehensive lesson content."""
    global requests_processed, last_activity
    
    start_time_req = datetime.utcnow()
    requests_processed += 1
    last_activity = start_time_req.isoformat()
    
    try:
        logger.info(f"Creating lesson content: {request.lesson_title}")
        
        # Validate request
        content_request = ContentCreationRequest(**request.dict())
        validation = await content_creator_service.validate_content_request(content_request)
        
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid request: {', '.join(validation['errors'])}"
            )
        
        # Create lesson content
        lesson_content = await content_creator_service.create_lesson_content(content_request)
        
        generation_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        logger.info(f"Lesson content created in {generation_time:.2f} seconds")
        
        return ContentResponse(
            success=True,
            content=lesson_content.dict(),
            generation_time_seconds=generation_time
        )
        
    except Exception as e:
        logger.error(f"Lesson creation failed: {e}")
        generation_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        return ContentResponse(
            success=False,
            error=str(e),
            generation_time_seconds=generation_time
        )

@app.post("/create-exercises", response_model=ContentResponse)
async def create_exercises(request: CreateExerciseRequest):
    """Create a set of varied exercises."""
    global requests_processed, last_activity
    
    start_time_req = datetime.utcnow()
    requests_processed += 1
    last_activity = start_time_req.isoformat()
    
    try:
        logger.info(f"Creating {request.exercise_count} exercises of types: {request.exercise_types}")
        
        # Create exercises
        exercises = await content_creator_service.create_exercise_set(
            lesson_context=request.lesson_context,
            exercise_types=request.exercise_types,
            count=request.exercise_count
        )
        
        generation_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        logger.info(f"Created {len(exercises)} exercises in {generation_time:.2f} seconds")
        
        return ContentResponse(
            success=True,
            content={
                "exercises": [exercise.dict() for exercise in exercises],
                "count": len(exercises),
                "types": request.exercise_types
            },
            generation_time_seconds=generation_time
        )
        
    except Exception as e:
        logger.error(f"Exercise creation failed: {e}")
        generation_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        return ContentResponse(
            success=False,
            error=str(e),
            generation_time_seconds=generation_time
        )

@app.post("/create-assessment", response_model=ContentResponse)
async def create_assessment(request: CreateAssessmentRequest):
    """Create comprehensive assessment content."""
    global requests_processed, last_activity
    
    start_time_req = datetime.utcnow()
    requests_processed += 1
    last_activity = start_time_req.isoformat()
    
    try:
        logger.info(f"Creating {request.assessment_type} assessment")
        
        # Create assessment
        assessment = await content_creator_service.create_assessment(
            course_context=request.course_context,
            assessment_type=request.assessment_type
        )
        
        generation_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        logger.info(f"Assessment created in {generation_time:.2f} seconds")
        
        return ContentResponse(
            success=True,
            content=assessment,
            generation_time_seconds=generation_time
        )
        
    except Exception as e:
        logger.error(f"Assessment creation failed: {e}")
        generation_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        return ContentResponse(
            success=False,
            error=str(e),
            generation_time_seconds=generation_time
        )

@app.post("/create-lesson-async")
async def create_lesson_async(request: CreateLessonRequest, background_tasks: BackgroundTasks):
    """Create lesson content asynchronously."""
    global requests_processed, last_activity
    
    requests_processed += 1
    last_activity = datetime.utcnow().isoformat()
    
    task_id = f"lesson_{request.course_id}_{int(datetime.utcnow().timestamp())}"
    
    # Add background task
    background_tasks.add_task(create_lesson_background, request, task_id)
    
    return {
        "task_id": task_id,
        "status": "queued",
        "message": f"Lesson creation started for: {request.lesson_title}"
    }

async def create_lesson_background(request: CreateLessonRequest, task_id: str):
    """Background task for lesson creation."""
    try:
        logger.info(f"Background lesson creation started for task {task_id}")
        
        content_request = ContentCreationRequest(**request.dict())
        lesson_content = await content_creator_service.create_lesson_content(content_request)
        
        # Here you would typically save the result to a database or cache
        logger.info(f"Background lesson creation completed for task {task_id}")
        
    except Exception as e:
        logger.error(f"Background lesson creation failed for task {task_id}: {e}")

@app.post("/validate-content-request")
async def validate_content_request(request: CreateLessonRequest):
    """Validate a content creation request."""
    try:
        content_request = ContentCreationRequest(**request.dict())
        validation = await content_creator_service.validate_content_request(content_request)
        return validation
    except Exception as e:
        logger.error(f"Content request validation failed: {e}")
        return {
            "valid": False,
            "errors": [str(e)],
            "warnings": []
        }

@app.post("/adapt-content")
async def adapt_content(content: Dict[str, Any], target_level: str):
    """Adapt existing content for a different CEFR level."""
    global requests_processed, last_activity
    
    start_time_req = datetime.utcnow()
    requests_processed += 1
    last_activity = start_time_req.isoformat()
    
    try:
        logger.info(f"Adapting content for {target_level} level")
        
        # Use the lesson generator to adapt content
        from tools import LessonContentGenerator
        generator = LessonContentGenerator()
        adapted_content = await generator.adapt_for_cefr_level(content, target_level)
        
        generation_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        return ContentResponse(
            success=True,
            content=adapted_content,
            generation_time_seconds=generation_time
        )
        
    except Exception as e:
        logger.error(f"Content adaptation failed: {e}")
        generation_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        return ContentResponse(
            success=False,
            error=str(e),
            generation_time_seconds=generation_time
        )

@app.get("/exercise-types")
async def get_exercise_types():
    """Get available exercise types and their descriptions."""
    capabilities = await content_creator_service.get_content_capabilities()
    return {
        "exercise_types": capabilities.get("supported_exercise_types", []),
        "descriptions": {
            "multiple-choice": "Questions with 4 answer options",
            "fill-in-blank": "Complete sentences with missing words",
            "matching": "Connect related items in two columns",
            "drag-drop": "Organize or categorize items",
            "reading-comprehension": "Text passage with comprehension questions",
            "listening-exercise": "Audio content with related tasks",
            "speaking-prompt": "Situations for oral responses",
            "writing-task": "Prompts for written responses",
            "role-play": "Interactive scenarios with specific roles",
            "case-study": "Business scenarios requiring analysis"
        }
    }

@app.get("/cefr-levels")
async def get_cefr_levels():
    """Get CEFR level information and guidelines."""
    return {
        "levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
        "descriptions": {
            "A1": "Beginner - Basic everyday expressions",
            "A2": "Elementary - Frequently used expressions and basic information",
            "B1": "Intermediate - Main points on familiar topics",
            "B2": "Upper-Intermediate - Complex text and fluent interaction",
            "C1": "Advanced - Wide range of demanding texts",
            "C2": "Proficient - Virtually everything with ease"
        },
        "guidelines": {
            "A1": {"vocabulary": 500, "grammar": "Present simple, basic questions"},
            "A2": {"vocabulary": 1000, "grammar": "Past simple, going to future"},
            "B1": {"vocabulary": 2000, "grammar": "Present perfect, conditionals"},
            "B2": {"vocabulary": 3500, "grammar": "Advanced conditionals, reported speech"},
            "C1": {"vocabulary": 5000, "grammar": "All tenses, advanced structures"},
            "C2": {"vocabulary": 7000, "grammar": "Native-like flexibility"}
        }
    }

@app.get("/metrics")
async def get_metrics():
    """Get agent performance metrics."""
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    return {
        "agent": "Content Creator Agent",
        "uptime_seconds": uptime,
        "uptime_hours": round(uptime / 3600, 2),
        "requests_processed": requests_processed,
        "requests_per_hour": round(requests_processed / (uptime / 3600), 2) if uptime > 0 else 0,
        "last_activity": last_activity,
        "start_time": start_time.isoformat(),
        "current_time": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint with agent information."""
    return {
        "agent": "Content Creator Agent",
        "version": "1.0.0",
        "description": "Creates engaging lessons, exercises, and learning materials",
        "status": "active",
        "endpoints": [
            "/health", "/status", "/capabilities",
            "/create-lesson", "/create-exercises", "/create-assessment",
            "/create-lesson-async", "/validate-content-request",
            "/adapt-content", "/exercise-types", "/cefr-levels", "/metrics"
        ]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint not found",
        "agent": "Content Creator Agent",
        "available_endpoints": [
            "/health", "/status", "/capabilities", "/create-lesson",
            "/create-exercises", "/create-assessment", "/metrics"
        ]
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal server error",
        "agent": "Content Creator Agent",
        "message": "Please check agent logs for details"
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Content Creator Agent server starting up...")
    logger.info("Checking agent capabilities...")
    
    try:
        capabilities = await content_creator_service.get_content_capabilities()
        logger.info(f"Agent capabilities: {capabilities}")
        logger.info("Content Creator Agent server ready!")
    except Exception as e:
        logger.error(f"Startup check failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Content Creator Agent server shutting down...")
    logger.info(f"Total requests processed: {requests_processed}")
    uptime = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Total uptime: {uptime:.2f} seconds ({uptime/3600:.2f} hours)")

# Main execution
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8102,
        reload=True,
        log_level="info"
    )