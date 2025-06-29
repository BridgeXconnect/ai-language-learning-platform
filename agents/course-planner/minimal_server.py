#!/usr/bin/env python3
"""
Minimal FastAPI server for Course Planner Agent
Runs without heavy ML dependencies for testing purposes
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import uvicorn
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Course Planner Agent (Minimal)",
    description="AI agent for analyzing SOPs and creating curriculum structures - Test Mode",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class CourseRequest(BaseModel):
    course_request_id: int
    company_name: str
    industry: str
    training_goals: str
    current_english_level: str
    duration_weeks: int = 8
    target_audience: str = "Professional staff"
    specific_needs: Optional[str] = None

class CurriculumPlan(BaseModel):
    title: str
    description: str
    cefr_level: str
    duration_weeks: int
    learning_objectives: List[str]
    modules: List[Dict[str, Any]]
    vocabulary_themes: List[str]
    grammar_progression: List[str]
    assessment_strategy: Dict[str, Any]
    company_specific_content: Dict[str, Any]

class PlanCourseResponse(BaseModel):
    success: bool
    curriculum: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    planning_time_seconds: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    agent: str
    version: str
    timestamp: str
    capabilities: Dict[str, Any]

# Global metrics
start_time = datetime.utcnow()
requests_processed = 0

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    
    capabilities = {
        "agent_name": "Course Planning Specialist",
        "version": "1.0.0",
        "capabilities": [
            "SOP document analysis",
            "CEFR level mapping", 
            "Curriculum structure generation",
            "Industry-specific content planning",
            "Progressive learning design"
        ],
        "supported_industries": [
            "Technology", "Healthcare", "Manufacturing", "Finance",
            "Hospitality", "Retail", "Logistics", "General Business"
        ],
        "supported_cefr_levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
        "max_duration_weeks": 24,
        "status": "active",
        "mode": "minimal_test"
    }
    
    return HealthResponse(
        status="healthy",
        agent="Course Planner Agent (Minimal)",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        capabilities=capabilities
    )

@app.get("/status")
async def get_status():
    """Get detailed agent status."""
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    return {
        "agent_name": "Course Planner Agent (Minimal)",
        "status": "active",
        "uptime_seconds": uptime,
        "requests_processed": requests_processed,
        "mode": "test",
        "last_activity": datetime.utcnow().isoformat()
    }

@app.get("/capabilities")
async def get_capabilities():
    """Get agent capabilities and supported features."""
    return {
        "agent_name": "Course Planning Specialist",
        "version": "1.0.0",
        "capabilities": [
            "SOP document analysis",
            "CEFR level mapping",
            "Curriculum structure generation",
            "Industry-specific content planning",
            "Progressive learning design"
        ],
        "supported_industries": [
            "Technology", "Healthcare", "Manufacturing", "Finance",
            "Hospitality", "Retail", "Logistics", "General Business"
        ],
        "supported_cefr_levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
        "max_duration_weeks": 24,
        "status": "active",
        "mode": "minimal_test"
    }

@app.post("/plan-course", response_model=PlanCourseResponse)
async def plan_course(request: CourseRequest):
    """Plan a course curriculum based on company requirements (mock implementation)."""
    global requests_processed
    
    start_time_req = datetime.utcnow()
    requests_processed += 1
    
    try:
        logger.info(f"Planning course for {request.company_name} (Request ID: {request.course_request_id})")
        
        # Validate request
        validation = validate_course_request(request)
        
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid request: {', '.join(validation['errors'])}"
            )
        
        # Generate mock curriculum
        curriculum = generate_mock_curriculum(request)
        
        planning_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        logger.info(f"Course planning completed in {planning_time:.2f} seconds")
        
        return PlanCourseResponse(
            success=True,
            curriculum=curriculum.dict(),
            planning_time_seconds=planning_time
        )
        
    except Exception as e:
        logger.error(f"Course planning failed: {e}")
        planning_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        return PlanCourseResponse(
            success=False,
            error=str(e),
            planning_time_seconds=planning_time
        )

@app.post("/validate-request")
async def validate_course_request_endpoint(request: CourseRequest):
    """Validate a course planning request."""
    try:
        validation = validate_course_request(request)
        return validation
    except Exception as e:
        logger.error(f"Request validation failed: {e}")
        return {
            "valid": False,
            "errors": [str(e)],
            "message": "Validation failed"
        }

def validate_course_request(request: CourseRequest) -> Dict[str, Any]:
    """Validate a course request."""
    errors = []
    
    if not request.company_name or len(request.company_name.strip()) == 0:
        errors.append("Company name is required")
    
    if not request.industry or len(request.industry.strip()) == 0:
        errors.append("Industry is required")
    
    if not request.training_goals or len(request.training_goals.strip()) == 0:
        errors.append("Training goals are required")
    
    if request.duration_weeks < 1 or request.duration_weeks > 24:
        errors.append("Duration must be between 1 and 24 weeks")
    
    valid_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    if request.current_english_level not in valid_levels:
        errors.append(f"Invalid CEFR level. Must be one of: {', '.join(valid_levels)}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "message": "Validation completed"
    }

def generate_mock_curriculum(request: CourseRequest) -> CurriculumPlan:
    """Generate a mock curriculum plan for testing."""
    
    # Mock curriculum based on request
    modules = []
    for i in range(min(request.duration_weeks, 8)):  # Max 8 modules
        module = {
            "module_id": i + 1,
            "title": f"Module {i + 1}: {get_module_theme(i, request.industry)}",
            "description": f"Focus on {get_module_focus(i, request.current_english_level)}",
            "duration_weeks": 1,
            "learning_objectives": [
                f"Understand key {request.industry.lower()} terminology",
                f"Practice {get_skill_focus(i)} skills",
                f"Apply {request.current_english_level} level language structures"
            ],
            "lessons": [
                {
                    "lesson_id": f"{i+1}.{j+1}",
                    "title": f"Lesson {j+1}: {get_lesson_title(j, request.industry)}",
                    "duration_minutes": 60
                }
                for j in range(3)  # 3 lessons per module
            ]
        }
        modules.append(module)
    
    return CurriculumPlan(
        title=f"Business English for {request.company_name}",
        description=f"Comprehensive {request.duration_weeks}-week English training program tailored for {request.industry} professionals",
        cefr_level=request.current_english_level,
        duration_weeks=request.duration_weeks,
        learning_objectives=[
            f"Improve business communication skills in {request.industry} context",
            f"Master {request.current_english_level} level vocabulary and grammar",
            "Enhance professional presentation abilities",
            "Develop effective written communication skills"
        ],
        modules=modules,
        vocabulary_themes=[
            f"{request.industry} terminology",
            "Business communication",
            "Professional presentations",
            "Email and report writing"
        ],
        grammar_progression=[
            "Present tenses review",
            "Modal verbs for suggestions",
            "Conditional structures",
            "Passive voice in formal contexts"
        ],
        assessment_strategy={
            "formative": "Weekly progress checks",
            "summative": "Module-end assessments",
            "final": "Comprehensive business communication project"
        },
        company_specific_content={
            "industry_focus": request.industry,
            "company_name": request.company_name,
            "specific_needs": request.specific_needs or "General business English",
            "target_audience": request.target_audience
        }
    )

def get_module_theme(module_index: int, industry: str) -> str:
    """Get theme for a module based on index and industry."""
    themes = {
        0: f"Introduction to {industry} English",
        1: "Professional Communication Basics",
        2: "Meetings and Presentations",
        3: "Written Communication",
        4: "Client Relations",
        5: "Project Management Language",
        6: "Technical Discussions",
        7: "Advanced Business Communication"
    }
    return themes.get(module_index, f"Advanced {industry} Communication")

def get_module_focus(module_index: int, cefr_level: str) -> str:
    """Get focus area for a module."""
    focuses = [
        "basic vocabulary and introductions",
        "everyday workplace conversations",
        "formal presentations and meetings",
        "professional email writing",
        "customer service language",
        "project coordination skills",
        "technical explanations",
        "advanced negotiation language"
    ]
    return focuses[module_index % len(focuses)]

def get_skill_focus(module_index: int) -> str:
    """Get skill focus for a module."""
    skills = ["speaking", "listening", "writing", "reading"]
    return skills[module_index % len(skills)]

def get_lesson_title(lesson_index: int, industry: str) -> str:
    """Get lesson title based on index and industry."""
    titles = [
        f"Key {industry} Vocabulary",
        "Professional Conversations",
        "Practical Applications"
    ]
    return titles[lesson_index % len(titles)]

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Course Planner Agent - Minimal Test Server",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "status": "/status", 
            "capabilities": "/capabilities",
            "plan_course": "/plan-course",
            "validate": "/validate-request"
        },
        "mode": "minimal_test"
    }

if __name__ == "__main__":
    print("🚀 Starting Course Planner Agent - Minimal Server")
    print("=" * 60)
    print("This is a test server without heavy ML dependencies")
    print("Available at: http://localhost:8101")
    print("Health check: http://localhost:8101/health")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8101) 