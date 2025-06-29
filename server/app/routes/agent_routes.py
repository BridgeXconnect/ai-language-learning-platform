"""
Agent Integration API Routes
Provides HTTP endpoints for multi-agent course generation workflow
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging
import aiohttp
import os
from datetime import datetime

from app.database import get_db
from app.models.sales import CourseRequest
from app.models.course import Course
from app.services.auth_service import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["Multi-Agent System"])

# Agent endpoints configuration
AGENT_ENDPOINTS = {
    "orchestrator": os.getenv("ORCHESTRATOR_URL", "http://localhost:8100"),
    "course_planner": os.getenv("COURSE_PLANNER_URL", "http://localhost:8101"),
    "content_creator": os.getenv("CONTENT_CREATOR_URL", "http://localhost:8102"),
    "quality_assurance": os.getenv("QUALITY_ASSURANCE_URL", "http://localhost:8103")
}

# Feature flags
AGENTS_ENABLED = os.getenv("AGENTS_ENABLED", "true").lower() == "true"
FALLBACK_TO_TRADITIONAL = os.getenv("FALLBACK_TO_TRADITIONAL", "true").lower() == "true"

async def call_agent(agent_name: str, endpoint: str, data: Dict[str, Any] = None, method: str = "POST") -> Dict[str, Any]:
    """Make HTTP request to an agent."""
    
    if agent_name not in AGENT_ENDPOINTS:
        raise ValueError(f"Unknown agent: {agent_name}")
    
    url = f"{AGENT_ENDPOINTS[agent_name]}{endpoint}"
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300)) as session:
            kwargs = {"url": url, "headers": {"Content-Type": "application/json"}}
            
            if data and method.upper() in ["POST", "PUT", "PATCH"]:
                kwargs["json"] = data
            elif data and method.upper() == "GET":
                kwargs["params"] = data
            
            async with getattr(session, method.lower())(**kwargs) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    return response_data
                else:
                    error_msg = response_data.get("error", f"HTTP {response.status}")
                    return {"success": False, "error": error_msg, "status_code": response.status}
                    
    except Exception as e:
        logger.error(f"Agent {agent_name} request failed: {e}")
        return {"success": False, "error": str(e)}

@router.get("/status")
async def get_agents_status():
    """Get status of all agents."""
    
    if not AGENTS_ENABLED:
        return {
            "agents_enabled": False,
            "message": "Multi-agent system is disabled"
        }
    
    try:
        status_result = await call_agent("orchestrator", "/agents/health", method="GET")
        
        return {
            "agents_enabled": True,
            "orchestrator_available": status_result.get("success", False),
            "agent_health": status_result.get("agent_health", {}),
            "system_status": status_result.get("summary", {}).get("system_status", "unknown"),
            "checked_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        return {
            "agents_enabled": True,
            "orchestrator_available": False,
            "error": str(e)
        }

@router.post("/generate-course-with-agents")
async def generate_course_with_agents(
    course_request_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate course using multi-agent workflow."""
    
    if not AGENTS_ENABLED:
        raise HTTPException(status_code=503, detail="Multi-agent system is disabled")
    
    try:
        # Get course request from database
        course_request = db.query(CourseRequest).filter(
            CourseRequest.id == course_request_id
        ).first()
        
        if not course_request:
            raise HTTPException(status_code=404, detail=f"Course request {course_request_id} not found")
        
        # Check if user has access to this course request
        if course_request.sales_user_id != current_user.id and not current_user.has_permission("manage_all_courses"):
            raise HTTPException(status_code=403, detail="Access denied to this course request")
        
        # Prepare agent request
        agent_request = {
            "course_request_id": course_request.id,
            "company_name": course_request.company_name,
            "industry": course_request.industry or "General Business",
            "training_goals": course_request.training_goals or "Improve English communication skills",
            "current_english_level": course_request.current_english_level or "B1",
            "duration_weeks": 8,  # Default duration
            "target_audience": course_request.target_audience or "Professional staff",
            "specific_needs": course_request.specific_needs
        }
        
        # Call orchestrator for synchronous workflow
        logger.info(f"Starting agent workflow for course request {course_request_id}")
        
        result = await call_agent("orchestrator", "/orchestrate-course", agent_request)
        
        if not result.get("success", False):
            if FALLBACK_TO_TRADITIONAL:
                logger.warning(f"Agent workflow failed, falling back to traditional AI: {result.get('error', 'Unknown error')}")
                # Add background task for traditional generation
                background_tasks.add_task(fallback_to_traditional_generation, course_request_id, db)
                
                return {
                    "success": True,
                    "method": "traditional_fallback",
                    "message": "Agent workflow failed, falling back to traditional AI generation",
                    "workflow_started": True,
                    "error": result.get("error")
                }
            else:
                raise HTTPException(status_code=500, detail=f"Agent workflow failed: {result.get('error', 'Unknown error')}")
        
        workflow_result = result.get("workflow_result", {})
        
        # Save workflow result to database if successful
        if workflow_result.get("status") == "completed":
            # Here you would save the generated course to the database
            # This is a placeholder for the actual implementation
            logger.info(f"Agent workflow completed successfully for course request {course_request_id}")
        
        return {
            "success": True,
            "method": "multi_agent",
            "workflow_id": workflow_result.get("workflow_id"),
            "status": workflow_result.get("status"),
            "quality_score": workflow_result.get("quality_score"),
            "approved_for_release": workflow_result.get("approved_for_release"),
            "processing_time_seconds": result.get("processing_time_seconds"),
            "course_generated": workflow_result.get("status") == "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent course generation failed: {e}")
        
        if FALLBACK_TO_TRADITIONAL:
            logger.info("Falling back to traditional AI generation")
            background_tasks.add_task(fallback_to_traditional_generation, course_request_id, db)
            
            return {
                "success": True,
                "method": "traditional_fallback",
                "message": f"Agent generation failed ({str(e)}), falling back to traditional AI",
                "workflow_started": True
            }
        else:
            raise HTTPException(status_code=500, detail=f"Course generation failed: {str(e)}")

@router.post("/generate-course-async")
async def generate_course_async(
    course_request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start asynchronous course generation with agents."""
    
    if not AGENTS_ENABLED:
        raise HTTPException(status_code=503, detail="Multi-agent system is disabled")
    
    try:
        # Get course request from database
        course_request = db.query(CourseRequest).filter(
            CourseRequest.id == course_request_id
        ).first()
        
        if not course_request:
            raise HTTPException(status_code=404, detail=f"Course request {course_request_id} not found")
        
        # Check user access
        if course_request.sales_user_id != current_user.id and not current_user.has_permission("manage_all_courses"):
            raise HTTPException(status_code=403, detail="Access denied to this course request")
        
        # Prepare agent request
        agent_request = {
            "course_request_id": course_request.id,
            "company_name": course_request.company_name,
            "industry": course_request.industry or "General Business",
            "training_goals": course_request.training_goals or "Improve English communication skills",
            "current_english_level": course_request.current_english_level or "B1",
            "duration_weeks": 8,
            "target_audience": course_request.target_audience or "Professional staff",
            "specific_needs": course_request.specific_needs
        }
        
        # Call orchestrator for asynchronous workflow
        result = await call_agent("orchestrator", "/orchestrate-course-async", agent_request)
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=f"Failed to start async workflow: {result.get('error', 'Unknown error')}")
        
        return {
            "success": True,
            "workflow_id": result.get("workflow_id"),
            "status": result.get("status", "queued"),
            "message": result.get("message", "Async workflow started"),
            "estimated_completion": result.get("estimated_completion", "5-10 minutes")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Async agent workflow failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start async workflow: {str(e)}")

@router.get("/workflow/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get status of a specific workflow."""
    
    if not AGENTS_ENABLED:
        raise HTTPException(status_code=503, detail="Multi-agent system is disabled")
    
    try:
        result = await call_agent("orchestrator", f"/workflow/{workflow_id}", method="GET")
        
        if not result.get("success", True):  # Assume success if not specified
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")

@router.get("/workflows")
async def list_workflows():
    """List all workflows."""
    
    if not AGENTS_ENABLED:
        raise HTTPException(status_code=503, detail="Multi-agent system is disabled")
    
    try:
        result = await call_agent("orchestrator", "/workflows", method="GET")
        return result
        
    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")

@router.delete("/workflow/{workflow_id}")
async def cancel_workflow(workflow_id: str):
    """Cancel an active workflow."""
    
    if not AGENTS_ENABLED:
        raise HTTPException(status_code=503, detail="Multi-agent system is disabled")
    
    try:
        result = await call_agent("orchestrator", f"/workflow/{workflow_id}", method="DELETE")
        
        if not result.get("success", True):
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found or not cancellable")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel workflow: {str(e)}")

@router.get("/metrics")
async def get_agent_metrics():
    """Get agent system performance metrics."""
    
    if not AGENTS_ENABLED:
        return {"agents_enabled": False}
    
    try:
        result = await call_agent("orchestrator", "/metrics", method="GET")
        return {
            "agents_enabled": True,
            "metrics": result
        }
        
    except Exception as e:
        logger.error(f"Failed to get agent metrics: {e}")
        return {
            "agents_enabled": True,
            "error": str(e)
        }

@router.post("/test")
async def test_agent_system():
    """Test the multi-agent system functionality."""
    
    if not AGENTS_ENABLED:
        return {"agents_enabled": False, "test_status": "disabled"}
    
    try:
        # Test orchestrator
        orchestrator_test = await call_agent("orchestrator", "/agents/test", method="POST")
        
        # Test individual agents health
        health_test = await call_agent("orchestrator", "/agents/health", method="GET")
        
        return {
            "agents_enabled": True,
            "orchestrator_test": orchestrator_test,
            "health_test": health_test,
            "test_completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Agent system test failed: {e}")
        return {
            "agents_enabled": True,
            "test_status": "failed",
            "error": str(e)
        }

async def fallback_to_traditional_generation(course_request_id: int, db: Session):
    """Fallback to traditional AI generation when agents fail."""
    
    try:
        logger.info(f"Starting traditional AI fallback for course request {course_request_id}")
        
        # Import traditional service
        from app.services.course_generation_service import course_generation_service
        
        # Generate course using traditional AI
        result = await course_generation_service.generate_course_from_request(
            course_request_id=course_request_id,
            db=db,
            generation_config={"ai_model": "gpt-4o-mini", "use_agents": False}
        )
        
        if result.get("success", False):
            logger.info(f"Traditional AI fallback completed successfully for course request {course_request_id}")
        else:
            logger.error(f"Traditional AI fallback also failed for course request {course_request_id}: {result}")
            
    except Exception as e:
        logger.error(f"Traditional AI fallback failed for course request {course_request_id}: {e}")

# Feature flag endpoints for admin control
@router.post("/admin/enable")
async def enable_agents(current_user: User = Depends(get_current_user)):
    """Enable the multi-agent system (admin only)."""
    
    if not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    global AGENTS_ENABLED
    AGENTS_ENABLED = True
    
    return {
        "success": True,
        "agents_enabled": True,
        "message": "Multi-agent system enabled"
    }

@router.post("/admin/disable")
async def disable_agents(current_user: User = Depends(get_current_user)):
    """Disable the multi-agent system (admin only)."""
    
    if not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    global AGENTS_ENABLED
    AGENTS_ENABLED = False
    
    return {
        "success": True,
        "agents_enabled": False,
        "message": "Multi-agent system disabled"
    }

@router.get("/config")
async def get_agent_config():
    """Get current agent system configuration."""
    
    return {
        "agents_enabled": AGENTS_ENABLED,
        "fallback_to_traditional": FALLBACK_TO_TRADITIONAL,
        "agent_endpoints": AGENT_ENDPOINTS,
        "features": {
            "multi_agent_workflow": AGENTS_ENABLED,
            "traditional_fallback": FALLBACK_TO_TRADITIONAL,
            "async_generation": AGENTS_ENABLED,
            "workflow_monitoring": AGENTS_ENABLED
        }
    }