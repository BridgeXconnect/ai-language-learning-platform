"""
FastAPI server wrapper for Course Planner Agent
Provides HTTP endpoints for agent communication and health monitoring
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import uvicorn
import asyncio
from datetime import datetime

from main import CoursePlannerService, CourseRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Course Planner Agent",
    description="AI agent for analyzing SOPs and creating curriculum structures",
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
course_planner_service = CoursePlannerService()

# Pydantic models for API
class PlanCourseRequest(BaseModel):
    course_request_id: int
    company_name: str
    industry: str
    training_goals: str
    current_english_level: str
    duration_weeks: int = 8
    target_audience: str = "Professional staff"
    specific_needs: Optional[str] = None

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
    
    capabilities = await course_planner_service.get_planning_capabilities()
    
    return HealthResponse(
        status="healthy",
        agent="Course Planner Agent",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        capabilities=capabilities
    )

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get detailed agent status."""
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    return StatusResponse(
        agent_name="Course Planner Agent",
        status="active",
        uptime_seconds=uptime,
        requests_processed=requests_processed,
        last_activity=last_activity
    )

@app.get("/capabilities")
async def get_capabilities():
    """Get agent capabilities and supported features."""
    return await course_planner_service.get_planning_capabilities()

@app.post("/plan-course", response_model=PlanCourseResponse)
async def plan_course(request: PlanCourseRequest):
    """Plan a course curriculum based on company requirements."""
    global requests_processed, last_activity
    
    start_time_req = datetime.utcnow()
    requests_processed += 1
    last_activity = start_time_req.isoformat()
    
    try:
        logger.info(f"Planning course for {request.company_name} (Request ID: {request.course_request_id})")
        
        # Validate request
        course_request = CourseRequest(**request.dict())
        validation = await course_planner_service.validate_course_request(course_request)
        
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid request: {', '.join(validation['errors'])}"
            )
        
        # Plan the course
        curriculum = await course_planner_service.plan_course(course_request)
        
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

@app.post("/plan-course-async")
async def plan_course_async(request: PlanCourseRequest, background_tasks: BackgroundTasks):
    """Plan a course asynchronously - returns immediately with task ID."""
    global requests_processed, last_activity
    
    requests_processed += 1
    last_activity = datetime.utcnow().isoformat()
    
    task_id = f"plan_{request.course_request_id}_{int(datetime.utcnow().timestamp())}"
    
    # Add background task
    background_tasks.add_task(plan_course_background, request, task_id)
    
    return {
        "task_id": task_id,
        "status": "queued",
        "message": f"Course planning started for {request.company_name}"
    }

async def plan_course_background(request: PlanCourseRequest, task_id: str):
    """Background task for course planning."""
    try:
        logger.info(f"Background planning started for task {task_id}")
        
        course_request = CourseRequest(**request.dict())
        curriculum = await course_planner_service.plan_course(course_request)
        
        # Here you would typically save the result to a database or cache
        # For now, we'll just log the completion
        logger.info(f"Background planning completed for task {task_id}")
        
    except Exception as e:
        logger.error(f"Background planning failed for task {task_id}: {e}")

@app.post("/validate-request")
async def validate_course_request(request: PlanCourseRequest):
    """Validate a course planning request."""
    try:
        course_request = CourseRequest(**request.dict())
        validation = await course_planner_service.validate_course_request(course_request)
        return validation
    except Exception as e:
        logger.error(f"Request validation failed: {e}")
        return {
            "valid": False,
            "errors": [str(e)],
            "warnings": []
        }

@app.get("/metrics")
async def get_metrics():
    """Get agent performance metrics."""
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    return {
        "agent": "Course Planner Agent",
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
        "agent": "Course Planner Agent",
        "version": "1.0.0",
        "description": "Analyzes company SOPs and creates comprehensive curriculum structures",
        "status": "active",
        "endpoints": [
            "/health",
            "/status", 
            "/capabilities",
            "/plan-course",
            "/plan-course-async",
            "/validate-request",
            "/metrics"
        ]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint not found",
        "agent": "Course Planner Agent",
        "available_endpoints": [
            "/health", "/status", "/capabilities", "/plan-course", 
            "/plan-course-async", "/validate-request", "/metrics"
        ]
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal server error",
        "agent": "Course Planner Agent",
        "message": "Please check agent logs for details"
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Course Planner Agent server starting up...")
    logger.info("Checking agent capabilities...")
    
    try:
        capabilities = await course_planner_service.get_planning_capabilities()
        logger.info(f"Agent capabilities: {capabilities}")
        logger.info("Course Planner Agent server ready!")
    except Exception as e:
        logger.error(f"Startup check failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Course Planner Agent server shutting down...")
    logger.info(f"Total requests processed: {requests_processed}")
    uptime = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Total uptime: {uptime:.2f} seconds ({uptime/3600:.2f} hours)")

# Main execution
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8101,
        reload=True,
        log_level="info"
    )