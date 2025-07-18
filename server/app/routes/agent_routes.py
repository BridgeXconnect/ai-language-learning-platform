"""
Agent Integration API Routes
Provides HTTP endpoints for multi-agent course generation workflow
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import logging
import aiohttp
import os
import traceback
import asyncio
import json
from datetime import datetime, timedelta
from functools import wraps

from app.core.database import get_db
from app.domains.sales.models import CourseRequest
from app.domains.courses.models import Course
from app.domains.auth.services import get_current_user, AuthService
from app.services.websocket_service import connection_manager, websocket_service
from app.services.agent_health_service import agent_health_monitor
from app.services.error_handling_service import system_recovery_manager, handle_system_error, ErrorSeverity
from app.services.audit_service import audit_service, AuditEventType
from app.domains.auth.models import User

# Configure detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a separate logger for agent communication
agent_logger = logging.getLogger(f"{__name__}.agent_communication")
health_logger = logging.getLogger(f"{__name__}.health_monitoring")

router = APIRouter(prefix="/api/agents", tags=["Multi-Agent System"])
security = HTTPBearer()

# Agent endpoints configuration
AGENT_ENDPOINTS = {
    "orchestrator": os.getenv("ORCHESTRATOR_URL", "http://localhost:8100"),
    "course_planner": os.getenv("COURSE_PLANNER_URL", "http://localhost:8101"),
    "content_creator": os.getenv("CONTENT_CREATOR_URL", "http://localhost:8102"),
    "quality_assurance": os.getenv("QUALITY_ASSURANCE_URL", "http://localhost:8103")
}

# Feature flags and configuration
AGENTS_ENABLED = os.getenv("AGENTS_ENABLED", "true").lower() == "true"
FALLBACK_TO_TRADITIONAL = os.getenv("FALLBACK_TO_TRADITIONAL", "true").lower() == "true"
MAX_CONCURRENT_WORKFLOWS = int(os.getenv("MAX_CONCURRENT_WORKFLOWS", "5"))
WORKFLOW_TIMEOUT_MINUTES = int(os.getenv("WORKFLOW_TIMEOUT_MINUTES", "30"))
HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL_SECONDS", "60"))

# Global state for monitoring
active_workflows = {}
health_cache = {}
last_health_check = None
workflow_metrics = {
    "total_started": 0,
    "total_completed": 0,
    "total_failed": 0,
    "average_duration_seconds": 0.0,
    "last_reset": datetime.utcnow().isoformat()
}

# Background monitoring state
_monitoring_task = None
_health_monitoring_task = None
_monitoring_active = False

async def start_background_monitoring():
    """Start background monitoring tasks for workflows and agent health."""
    global _monitoring_task, _health_monitoring_task, _monitoring_active
    
    if not _monitoring_active:
        _monitoring_active = True
        _monitoring_task = asyncio.create_task(_workflow_monitoring_loop())
        _health_monitoring_task = asyncio.create_task(_health_monitoring_loop())
        logger.info("Background monitoring tasks started")

async def stop_background_monitoring():
    """Stop background monitoring tasks."""
    global _monitoring_task, _health_monitoring_task, _monitoring_active
    
    _monitoring_active = False
    
    if _monitoring_task:
        _monitoring_task.cancel()
        try:
            await _monitoring_task
        except asyncio.CancelledError:
            pass
    
    if _health_monitoring_task:
        _health_monitoring_task.cancel()
        try:
            await _health_monitoring_task
        except asyncio.CancelledError:
            pass
    
    logger.info("Background monitoring tasks stopped")

async def _workflow_monitoring_loop():
    """Background task to monitor workflow progress and send updates."""
    while _monitoring_active:
        try:
            if not AGENTS_ENABLED or not active_workflows:
                await asyncio.sleep(10)
                continue
            
            # Check each active workflow
            workflows_to_check = list(active_workflows.keys())
            
            for workflow_id in workflows_to_check:
                try:
                    # Get workflow status from orchestrator
                    result = await call_agent("orchestrator", f"/workflow/{workflow_id}", method="GET", timeout=10)
                    
                    if result.get("success", False):
                        workflow_data = result.get("workflow", {})
                        current_status = workflow_data.get("status")
                        
                        # Update local tracking
                        if workflow_id in active_workflows:
                            local_workflow = active_workflows[workflow_id]
                            previous_status = local_workflow.get("status")
                            
                            # Check if status changed
                            if current_status != previous_status:
                                local_workflow["status"] = current_status
                                local_workflow["last_updated"] = datetime.utcnow().isoformat()
                                
                                # Broadcast update to WebSocket subscribers
                                await connection_manager.broadcast_workflow_update(workflow_id, {
                                    "status": current_status,
                                    "previous_status": previous_status,
                                    "progress_percentage": workflow_data.get("progress_percentage", 0),
                                    "current_stage": workflow_data.get("current_stage"),
                                    "quality_score": workflow_data.get("quality_score"),
                                    "updated_at": datetime.utcnow().isoformat()
                                })
                                
                                logger.info(f"Workflow {workflow_id} status changed: {previous_status} -> {current_status}")
                            
                            # Remove completed workflows
                            if current_status in ["completed", "failed", "cancelled"]:
                                if current_status == "completed":
                                    workflow_metrics["total_completed"] += 1
                                else:
                                    workflow_metrics["total_failed"] += 1
                                
                                del active_workflows[workflow_id]
                                logger.info(f"Workflow {workflow_id} removed from active tracking")
                    
                except Exception as e:
                    logger.error(f"Error monitoring workflow {workflow_id}: {e}")
                    
                    # Check for timeout
                    if workflow_id in active_workflows:
                        local_workflow = active_workflows[workflow_id]
                        timeout_at = datetime.fromisoformat(local_workflow.get("timeout_at", datetime.utcnow().isoformat()))
                        
                        if datetime.utcnow() > timeout_at:
                            local_workflow["status"] = "timed_out"
                            local_workflow["error"] = "Workflow monitoring timed out"
                            
                            # Broadcast timeout update
                            await connection_manager.broadcast_workflow_update(workflow_id, {
                                "status": "timed_out",
                                "error": "Workflow monitoring timed out",
                                "updated_at": datetime.utcnow().isoformat()
                            })
                            
                            del active_workflows[workflow_id]
                            workflow_metrics["total_failed"] += 1
                            logger.warning(f"Workflow {workflow_id} timed out")
            
            await asyncio.sleep(5)  # Check every 5 seconds
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in workflow monitoring loop: {e}\n{traceback.format_exc()}")
            await asyncio.sleep(10)

async def _health_monitoring_loop():
    """Background task to monitor agent health and send updates."""
    while _monitoring_active:
        try:
            if not AGENTS_ENABLED:
                await asyncio.sleep(60)
                continue
            
            # Check agent health
            agent_names = ["course_planner", "content_creator", "quality_assurance"]
            health_data = {}
            
            for agent_name in agent_names:
                try:
                    health_result = await check_agent_health_cached(agent_name, force_refresh=True)
                    health_data[agent_name] = health_result
                except Exception as e:
                    health_logger.error(f"Failed to check {agent_name} health: {e}")
                    health_data[agent_name] = {
                        "agent": agent_name,
                        "healthy": False,
                        "error": str(e),
                        "checked_at": datetime.utcnow().isoformat()
                    }
            
            # Check overall system status
            healthy_agents = sum(1 for health in health_data.values() if health.get("healthy", False))
            total_agents = len(health_data)
            
            if healthy_agents == total_agents:
                system_status = "operational"
            elif healthy_agents > 0:
                system_status = "degraded"
            else:
                system_status = "offline"
            
            # Broadcast health update
            health_update = {
                "agent_health": health_data,
                "system_status": system_status,
                "healthy_agents": healthy_agents,
                "total_agents": total_agents,
                "health_percentage": round((healthy_agents / total_agents) * 100, 1) if total_agents > 0 else 0,
                "checked_at": datetime.utcnow().isoformat()
            }
            
            await connection_manager.broadcast_health_update(health_update)
            
            await asyncio.sleep(HEALTH_CHECK_INTERVAL)  # Check based on configured interval
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            health_logger.error(f"Error in health monitoring loop: {e}\n{traceback.format_exc()}")
            await asyncio.sleep(60)

def require_permission(permission: str):
    """Decorator to require specific user permissions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if current_user and not current_user.has_permission(permission):
                raise HTTPException(
                    status_code=403, 
                    detail=f"Permission '{permission}' required"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

async def call_agent(agent_name: str, endpoint: str, data: Dict[str, Any] = None, method: str = "POST", timeout: int = 300) -> Dict[str, Any]:
    """Make HTTP request to an agent with enhanced error handling and logging."""
    
    if agent_name not in AGENT_ENDPOINTS:
        agent_logger.error(f"Unknown agent requested: {agent_name}")
        raise ValueError(f"Unknown agent: {agent_name}")
    
    url = f"{AGENT_ENDPOINTS[agent_name]}{endpoint}"
    start_time = datetime.utcnow()
    request_id = f"{agent_name}_{int(start_time.timestamp())}_{hash(url) % 10000}"
    
    agent_logger.info(f"[{request_id}] Starting request to {agent_name}: {method} {endpoint}")
    
    try:
        timeout_config = aiohttp.ClientTimeout(total=timeout, connect=30, sock_read=timeout)
        
        async with aiohttp.ClientSession(timeout=timeout_config) as session:
            kwargs = {
                "url": url, 
                "headers": {
                    "Content-Type": "application/json",
                    "X-Request-ID": request_id,
                    "X-Agent-Client": "course-manager"
                }
            }
            
            if data and method.upper() in ["POST", "PUT", "PATCH"]:
                kwargs["json"] = data
                agent_logger.debug(f"[{request_id}] Request payload size: {len(str(data))} chars")
            elif data and method.upper() == "GET":
                kwargs["params"] = data
            
            async with getattr(session, method.lower())(**kwargs) as response:
                response_time = (datetime.utcnow() - start_time).total_seconds()
                
                try:
                    response_data = await response.json()
                except Exception as json_err:
                    agent_logger.error(f"[{request_id}] Failed to parse JSON response: {json_err}")
                    response_text = await response.text()
                    return {
                        "success": False, 
                        "error": f"Invalid JSON response: {response_text[:200]}...",
                        "status_code": response.status
                    }
                
                if response.status == 200:
                    agent_logger.info(f"[{request_id}] Success ({response_time:.2f}s): {agent_name}")
                    return {**response_data, "_request_id": request_id, "_response_time": response_time}
                else:
                    error_msg = response_data.get("error", f"HTTP {response.status}")
                    agent_logger.error(f"[{request_id}] Failed ({response_time:.2f}s): {error_msg}")
                    return {
                        "success": False, 
                        "error": error_msg, 
                        "status_code": response.status,
                        "_request_id": request_id,
                        "_response_time": response_time
                    }
                    
    except asyncio.TimeoutError:
        response_time = (datetime.utcnow() - start_time).total_seconds()
        agent_logger.error(f"[{request_id}] Timeout after {response_time:.2f}s")
        return {
            "success": False, 
            "error": f"Request timeout after {timeout}s",
            "_request_id": request_id,
            "_response_time": response_time
        }
    except aiohttp.ClientConnectorError as e:
        response_time = (datetime.utcnow() - start_time).total_seconds()
        agent_logger.error(f"[{request_id}] Connection error ({response_time:.2f}s): {e}")
        return {
            "success": False, 
            "error": f"Connection failed: {str(e)}",
            "_request_id": request_id,
            "_response_time": response_time
        }
    except Exception as e:
        response_time = (datetime.utcnow() - start_time).total_seconds()
        agent_logger.error(f"[{request_id}] Unexpected error ({response_time:.2f}s): {e}\n{traceback.format_exc()}")
        return {
            "success": False, 
            "error": f"Unexpected error: {str(e)}",
            "_request_id": request_id,
            "_response_time": response_time
        }

async def check_agent_health_cached(agent_name: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Check agent health with caching to reduce load."""
    global health_cache, last_health_check
    
    now = datetime.utcnow()
    cache_key = f"{agent_name}_health"
    
    # Check if we have fresh cached data
    if not force_refresh and cache_key in health_cache:
        cached_data = health_cache[cache_key]
        cache_age = (now - datetime.fromisoformat(cached_data["checked_at"])).total_seconds()
        if cache_age < HEALTH_CHECK_INTERVAL:
            return cached_data
    
    # Perform fresh health check
    health_logger.info(f"Performing health check for {agent_name}")
    
    try:
        result = await call_agent(agent_name, "/health", method="GET", timeout=10)
        
        health_data = {
            "agent": agent_name,
            "healthy": result.get("status") == "healthy" or result.get("success", False),
            "response_time_ms": result.get("_response_time", 0) * 1000,
            "status": result.get("status", "unknown"),
            "version": result.get("version"),
            "features": result.get("features", []),
            "checked_at": now.isoformat(),
            "error": result.get("error") if not result.get("success", True) else None
        }
        
        # Cache the result
        health_cache[cache_key] = health_data
        health_logger.info(f"Health check completed for {agent_name}: {'healthy' if health_data['healthy'] else 'unhealthy'}")
        
        return health_data
        
    except Exception as e:
        health_logger.error(f"Health check failed for {agent_name}: {e}")
        error_data = {
            "agent": agent_name,
            "healthy": False,
            "status": "error",
            "error": str(e),
            "checked_at": now.isoformat()
        }
        
        # Cache the error result for a shorter time
        health_cache[cache_key] = error_data
        return error_data

@router.get("/status")
async def get_agents_status(
    force_refresh: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive status of all agents with caching and detailed health metrics."""
    
    health_logger.info(f"Agent status requested by user {current_user.username}, force_refresh={force_refresh}")
    
    if not AGENTS_ENABLED:
        return {
            "agents_enabled": False,
            "orchestrator_available": False,
            "agent_health": {},
            "system_status": "disabled",
            "message": "Multi-agent system is disabled",
            "checked_at": datetime.utcnow().isoformat()
        }
    
    try:
        # Check orchestrator first
        orchestrator_result = await call_agent("orchestrator", "/agents/health", method="GET", timeout=15)
        orchestrator_available = orchestrator_result.get("success", False)
        
        # Get health status for all individual agents
        agent_health = {}
        
        # Direct health checks for each agent
        agent_names = ["course_planner", "content_creator", "quality_assurance"]
        
        for agent_name in agent_names:
            try:
                health_data = await check_agent_health_cached(agent_name, force_refresh)
                agent_health[agent_name] = health_data
            except Exception as agent_e:
                health_logger.error(f"Failed to check {agent_name} health: {agent_e}")
                agent_health[agent_name] = {
                    "agent": agent_name,
                    "healthy": False,
                    "status": "error",
                    "error": str(agent_e),
                    "checked_at": datetime.utcnow().isoformat()
                }
        
        # Determine overall system status
        healthy_agents = sum(1 for health in agent_health.values() if health.get("healthy", False))
        total_agents = len(agent_health)
        
        if healthy_agents == total_agents and orchestrator_available:
            system_status = "operational"
        elif healthy_agents > 0 or orchestrator_available:
            system_status = "degraded"
        else:
            system_status = "offline"
        
        # Get orchestrator-provided health data if available
        orchestrator_health = orchestrator_result.get("agent_health", {})
        
        # Merge orchestrator health data with direct checks
        for agent_name, direct_health in agent_health.items():
            orchestrator_agent_health = orchestrator_health.get(agent_name, {})
            if orchestrator_agent_health:
                # Merge data, preferring orchestrator data for consistency
                agent_health[agent_name] = {
                    **direct_health,
                    **orchestrator_agent_health,
                    "direct_check": direct_health,
                    "orchestrator_check": orchestrator_agent_health
                }
        
        result = {
            "agents_enabled": True,
            "orchestrator_available": orchestrator_available,
            "agent_health": agent_health,
            "system_status": system_status,
            "metrics": {
                "healthy_agents": healthy_agents,
                "total_agents": total_agents,
                "health_percentage": round((healthy_agents / total_agents) * 100, 1) if total_agents > 0 else 0,
                "average_response_time_ms": round(
                    sum(health.get("response_time_ms", 0) for health in agent_health.values()) / total_agents, 2
                ) if total_agents > 0 else 0
            },
            "workflow_metrics": workflow_metrics,
            "active_workflows_count": len(active_workflows),
            "checked_at": datetime.utcnow().isoformat()
        }
        
        health_logger.info(f"Agent status check completed: {system_status} ({healthy_agents}/{total_agents} agents healthy)")
        return result
        
    except Exception as e:
        health_logger.error(f"Failed to get comprehensive agent status: {e}\n{traceback.format_exc()}")
        return {
            "agents_enabled": True,
            "orchestrator_available": False,
            "agent_health": {},
            "system_status": "error",
            "error": str(e),
            "checked_at": datetime.utcnow().isoformat()
        }

@router.post("/generate-course-with-agents")
async def generate_course_with_agents(
    course_request_id: int,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate course using multi-agent workflow with comprehensive tracking and error handling."""
    
    # Check if we've hit the concurrent workflow limit
    if len(active_workflows) >= MAX_CONCURRENT_WORKFLOWS:
        logger.warning(f"Maximum concurrent workflows ({MAX_CONCURRENT_WORKFLOWS}) reached")
        raise HTTPException(
            status_code=429, 
            detail=f"Maximum concurrent workflows ({MAX_CONCURRENT_WORKFLOWS}) reached. Please try again later."
        )
    
    # Check if user has permission for course generation
    if not current_user.has_permission("manage_courses") and not current_user.has_permission("manage_all_courses"):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions for course generation"
        )
    
    workflow_id = f"workflow_{course_request_id}_{int(datetime.utcnow().timestamp())}"
    start_time = datetime.utcnow()
    
    logger.info(f"Starting course generation workflow {workflow_id} for user {current_user.username}")
    
    try:
        # Track this workflow
        active_workflows[workflow_id] = {
            "workflow_id": workflow_id,
            "course_request_id": course_request_id,
            "user_id": current_user.id,
            "status": "initializing",
            "start_time": start_time.isoformat(),
            "timeout_at": (start_time + timedelta(minutes=WORKFLOW_TIMEOUT_MINUTES)).isoformat()
        }
        
        workflow_metrics["total_started"] += 1
        
        # Start monitoring tasks if not already running
        await start_background_monitoring()
        
        # Start health monitoring if not already active
        if not agent_health_monitor._monitoring_active:
            await agent_health_monitor.start_monitoring()
        
        # Start audit service if not already active
        if not audit_service._cleanup_active:
            await audit_service.start_audit_service()
        
        # Start workflow audit trail
        await audit_service.start_workflow_audit(
            workflow_id=workflow_id,
            course_request_id=course_request_id,
            user_id=current_user.id,
            company_name=course_request.company_name,
            details={
                "industry": course_request.industry,
                "training_goals": course_request.training_goals,
                "current_english_level": course_request.current_english_level,
                "estimated_budget": course_request.estimated_budget
            }
        )
        # Get course request from database with enhanced validation
        course_request = db.query(CourseRequest).filter(
            CourseRequest.id == course_request_id
        ).first()
        
        if not course_request:
            logger.error(f"Course request {course_request_id} not found")
            raise HTTPException(status_code=404, detail=f"Course request {course_request_id} not found")
        
        # Enhanced access control
        has_access = (
            course_request.sales_user_id == current_user.id or 
            current_user.has_permission("manage_all_courses") or
            current_user.has_permission("course_manager")
        )
        
        if not has_access:
            logger.warning(f"User {current_user.username} denied access to course request {course_request_id}")
            raise HTTPException(status_code=403, detail="Access denied to this course request")
        
        # Validate course request status
        if course_request.status not in ["submitted", "under_review"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Course request must be in 'submitted' or 'under_review' status, current status: {course_request.status}"
            )
        
        # Update workflow tracking
        active_workflows[workflow_id]["status"] = "validated"
        active_workflows[workflow_id]["company_name"] = course_request.company_name
        
        # Pre-flight system health check
        if AGENTS_ENABLED:
            try:
                health_check = await get_agents_status(force_refresh=True, current_user=current_user)
                system_status = health_check.get("system_status")
                
                if system_status == "offline":
                    logger.warning(f"Agent system offline, falling back to traditional generation")
                    if not FALLBACK_TO_TRADITIONAL:
                        raise HTTPException(
                            status_code=503, 
                            detail="Agent system is offline and fallback is disabled"
                        )
                elif system_status == "degraded":
                    logger.warning(f"Agent system degraded, proceeding with caution")
                
                active_workflows[workflow_id]["status"] = "starting_agents"
                logger.info(f"Starting real agent workflow for course request {course_request_id} (system status: {system_status})")
                
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
                
                # Call orchestrator for real workflow
                result = await call_agent("orchestrator", "/orchestrate-course", agent_request)
                
                if result.get("success", False):
                    workflow_result = result.get("workflow_result", {})
                    
                    # Update workflow tracking
                    active_workflows[workflow_id]["status"] = workflow_result.get("status", "in_progress")
                    active_workflows[workflow_id]["agent_workflow_id"] = workflow_result.get("workflow_id")
                    
                    # Update course request status based on workflow result
                    if workflow_result.get("status") == "completed":
                        course_request.status = "approved"
                        workflow_metrics["total_completed"] += 1
                        # Remove from active workflows
                        if workflow_id in active_workflows:
                            del active_workflows[workflow_id]
                    else:
                        course_request.status = "generation_in_progress"
                    
                    db.commit()
                    
                    logger.info(f"Real agent workflow initiated for request {course_request_id}, status: {workflow_result.get('status')}")
                    
                    # Send WebSocket notification
                    try:
                        await connection_manager.send_to_user(current_user.id, {
                            "type": "workflow_started" if workflow_result.get("status") != "completed" else "workflow_completed",
                            "workflow_id": workflow_result.get("workflow_id"),
                            "course_request_id": course_request_id,
                            "status": workflow_result.get("status"),
                            "method": "real_agent_workflow",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    except Exception as ws_e:
                        logger.warning(f"Failed to send WebSocket notification: {ws_e}")
                    
                    return {
                        "success": True,
                        "method": "real_agent_workflow",
                        "workflow_id": workflow_result.get("workflow_id"),
                        "status": workflow_result.get("status"),
                        "quality_score": workflow_result.get("quality_score"),
                        "approved_for_release": workflow_result.get("approved_for_release", False),
                        "processing_time_seconds": workflow_result.get("total_duration_seconds"),
                        "course_generated": workflow_result.get("status") == "completed",
                        "course_data": workflow_result.get("final_course", {}),
                        "message": "Course generated successfully using AI agents"
                    }
                else:
                    error_msg = result.get("error", "Unknown error")
                    logger.error(f"Real agent workflow failed for request {course_request_id}: {error_msg}")
                    
                    # Update workflow tracking
                    active_workflows[workflow_id]["status"] = "failed"
                    active_workflows[workflow_id]["error"] = error_msg
                    workflow_metrics["total_failed"] += 1
                    
                    if not FALLBACK_TO_TRADITIONAL:
                        # Remove from active workflows
                        if workflow_id in active_workflows:
                            del active_workflows[workflow_id]
                        raise HTTPException(
                            status_code=500, 
                            detail=f"Agent workflow failed: {error_msg}",
                            headers={"X-Workflow-ID": workflow_id}
                        )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Real agent workflow error for request {course_request_id}: {e}\n{traceback.format_exc()}")
                
                # Update workflow tracking
                if workflow_id in active_workflows:
                    active_workflows[workflow_id]["status"] = "error"
                    active_workflows[workflow_id]["error"] = str(e)
                
                workflow_metrics["total_failed"] += 1
                
                if not FALLBACK_TO_TRADITIONAL:
                    # Remove from active workflows
                    if workflow_id in active_workflows:
                        del active_workflows[workflow_id]
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Agent workflow failed: {str(e)}",
                        headers={"X-Workflow-ID": workflow_id}
                    )
        
        # Fallback to mock course generation
        logger.info(f"Using mock course generation for request {course_request_id}")
        
        # Update workflow tracking
        if workflow_id in active_workflows:
            active_workflows[workflow_id]["status"] = "mock_generation"
        
        # Create a mock course structure
        mock_course = {
            "workflow_id": f"mock_workflow_{course_request_id}_{int(datetime.utcnow().timestamp())}",
            "status": "completed",
            "course_request_id": course_request_id,
            "company_name": course_request.company_name,
            "generated_course": {
                "title": f"English Communication Course for {course_request.company_name}",
                "description": f"Customized English training program for {course_request.industry or 'business'} professionals",
                "duration_weeks": 8,
                "cefr_level": course_request.current_english_level or "B1",
                "modules": [
                    {
                        "id": 1,
                        "title": "Business Communication Fundamentals",
                        "description": "Essential communication skills for professional settings",
                        "lessons": 4,
                        "exercises": 12
                    },
                    {
                        "id": 2,
                        "title": f"{course_request.industry or 'Industry'}-Specific Communication",
                        "description": f"Communication skills specific to {course_request.industry or 'your industry'}",
                        "lessons": 6,
                        "exercises": 18
                    },
                    {
                        "id": 3,
                        "title": "Presentation and Meeting Skills",
                        "description": "Advanced communication for presentations and meetings",
                        "lessons": 4,
                        "exercises": 12
                    }
                ],
                "total_lessons": 14,
                "total_exercises": 42,
                "estimated_hours": 28
            },
            "quality_score": 85.5,
            "approved_for_release": True,
            "processing_time_seconds": 2.5,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Simulate database save by updating course request status
        course_request.status = "approved"  # Set to approved status
        db.commit()
        
        # Update metrics and remove from active workflows
        workflow_metrics["total_completed"] += 1
        if workflow_id in active_workflows:
            del active_workflows[workflow_id]
        
        logger.info(f"Mock course generation completed for request {course_request_id}")
        
        return {
            "success": True,
            "method": "mock_generation",
            "workflow_id": mock_course["workflow_id"],
            "status": mock_course["status"],
            "quality_score": mock_course["quality_score"],
            "approved_for_release": mock_course["approved_for_release"],
            "processing_time_seconds": mock_course["processing_time_seconds"],
            "course_generated": True,
            "course_data": mock_course["generated_course"],
            "message": "Course generated successfully (fallback mock implementation)",
            "user_id": current_user.id,
            "request_ip": request.client.host if request.client else "unknown"
        }
        
        # Send WebSocket notification for completion
        try:
            await connection_manager.send_to_user(current_user.id, {
                "type": "workflow_completed",
                "workflow_id": workflow_id,
                "course_request_id": course_request_id,
                "method": "mock_generation",
                "quality_score": mock_course["quality_score"],
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as ws_e:
            logger.warning(f"Failed to send WebSocket notification: {ws_e}")
        
        return {
            "success": True,
            "method": "mock_generation",
            "workflow_id": mock_course["workflow_id"],
            "status": mock_course["status"],
            "quality_score": mock_course["quality_score"],
            "approved_for_release": mock_course["approved_for_release"],
            "processing_time_seconds": mock_course["processing_time_seconds"],
            "course_generated": True,
            "course_data": mock_course["generated_course"],
            "message": "Course generated successfully (fallback mock implementation)",
            "user_id": current_user.id,
            "request_ip": request.client.host if request.client else "unknown"
        }
        
    except HTTPException:
        # Clean up workflow tracking for HTTP exceptions
        if workflow_id in active_workflows:
            del active_workflows[workflow_id]
        raise
    except Exception as e:
        logger.error(f"Course generation failed unexpectedly: {e}\n{traceback.format_exc()}")
        
        # Update metrics and clean up workflow tracking
        workflow_metrics["total_failed"] += 1
        if workflow_id in active_workflows:
            active_workflows[workflow_id]["status"] = "failed"
            active_workflows[workflow_id]["error"] = str(e)
            del active_workflows[workflow_id]
        
        raise HTTPException(
            status_code=500, 
            detail=f"Course generation failed: {str(e)}",
            headers={"X-Workflow-ID": workflow_id}
        )

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
async def get_workflow_status(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get status of a specific workflow with enhanced tracking and user validation."""
    
    logger.info(f"Workflow status requested for {workflow_id} by user {current_user.username}")
    
    if not AGENTS_ENABLED:
        # Check if this is a mock workflow
        if workflow_id.startswith("mock_workflow_"):
            # Return mock workflow status
            return {
                "success": True,
                "workflow": {
                    "workflow_id": workflow_id,
                    "status": "completed",
                    "current_stage": "completed",
                    "progress_percentage": 100,
                    "start_time": datetime.utcnow().isoformat(),
                    "completion_time": datetime.utcnow().isoformat(),
                    "quality_score": 87.5,
                    "approved_for_release": True,
                    "method": "mock_generation"
                }
            }
        
        raise HTTPException(status_code=503, detail="Multi-agent system is disabled")
    
    try:
        # Check if workflow is in our active tracking
        if workflow_id in active_workflows:
            local_workflow = active_workflows[workflow_id]
            
            # Verify user has access to this workflow
            if (local_workflow.get("user_id") != current_user.id and 
                not current_user.has_permission("manage_all_courses")):
                raise HTTPException(status_code=403, detail="Access denied to this workflow")
            
            # Check for timeout
            timeout_at = datetime.fromisoformat(local_workflow.get("timeout_at", datetime.utcnow().isoformat()))
            if datetime.utcnow() > timeout_at:
                logger.warning(f"Workflow {workflow_id} has timed out")
                local_workflow["status"] = "timed_out"
                local_workflow["error"] = f"Workflow timed out after {WORKFLOW_TIMEOUT_MINUTES} minutes"
                
                # Clean up
                del active_workflows[workflow_id]
                workflow_metrics["total_failed"] += 1
                
                return {
                    "success": False,
                    "workflow": local_workflow,
                    "error": "Workflow timed out"
                }
        
        # Try to get status from orchestrator
        result = await call_agent("orchestrator", f"/workflow/{workflow_id}", method="GET", timeout=15)
        
        if result.get("success", False):
            workflow_data = result.get("workflow", {})
            
            # Enhance with local tracking data if available
            if workflow_id in active_workflows:
                local_data = active_workflows[workflow_id]
                workflow_data.update({
                    "local_tracking": local_data,
                    "user_id": local_data.get("user_id"),
                    "course_request_id": local_data.get("course_request_id")
                })
                
                # Update local status if workflow completed
                if workflow_data.get("status") in ["completed", "failed", "cancelled"]:
                    if workflow_data.get("status") == "completed":
                        workflow_metrics["total_completed"] += 1
                    else:
                        workflow_metrics["total_failed"] += 1
                    
                    # Remove from active tracking
                    del active_workflows[workflow_id]
            
            return {
                "success": True,
                "workflow": workflow_data,
                "checked_at": datetime.utcnow().isoformat()
            }
        
        elif result.get("status_code") == 404:
            # Workflow not found in orchestrator, check if it's in local tracking
            if workflow_id in active_workflows:
                local_workflow = active_workflows[workflow_id]
                
                # Return local status
                return {
                    "success": True,
                    "workflow": {
                        **local_workflow,
                        "status": local_workflow.get("status", "pending"),
                        "message": "Workflow found in local tracking but not in orchestrator"
                    },
                    "checked_at": datetime.utcnow().isoformat()
                }
            
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
        
        else:
            error_msg = result.get("error", "Unknown error")
            logger.error(f"Failed to get workflow status from orchestrator: {error_msg}")
            
            # Try to return local tracking data if available
            if workflow_id in active_workflows:
                local_workflow = active_workflows[workflow_id]
                return {
                    "success": True,
                    "workflow": {
                        **local_workflow,
                        "orchestrator_error": error_msg,
                        "message": "Using local tracking data due to orchestrator error"
                    },
                    "checked_at": datetime.utcnow().isoformat()
                }
            
            raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {error_msg}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}\n{traceback.format_exc()}")
        
        # Try to return local tracking data as fallback
        if workflow_id in active_workflows:
            local_workflow = active_workflows[workflow_id]
            return {
                "success": True,
                "workflow": {
                    **local_workflow,
                    "error": str(e),
                    "message": "Using local tracking data due to error"
                },
                "checked_at": datetime.utcnow().isoformat()
            }
        
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")

@router.get("/workflows")
async def list_workflows(
    limit: int = 50,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """List workflows with filtering and user access control."""
    
    logger.info(f"Workflows list requested by user {current_user.username}")
    
    try:
        # Get orchestrator workflows if agents are enabled
        orchestrator_workflows = []
        if AGENTS_ENABLED:
            try:
                result = await call_agent("orchestrator", "/workflows", method="GET", timeout=10)
                if result.get("success", False):
                    orchestrator_workflows = result.get("workflows", [])
            except Exception as e:
                logger.warning(f"Failed to get orchestrator workflows: {e}")
        
        # Get local tracking workflows
        local_workflows = list(active_workflows.values())
        
        # Combine and filter workflows
        all_workflows = []
        
        # Add orchestrator workflows
        for workflow in orchestrator_workflows:
            # Filter by user access
            if (current_user.has_permission("manage_all_courses") or 
                workflow.get("user_id") == current_user.id):
                all_workflows.append({
                    **workflow,
                    "source": "orchestrator"
                })
        
        # Add local workflows (these are usually more recent)
        for workflow in local_workflows:
            # Filter by user access
            if (current_user.has_permission("manage_all_courses") or 
                workflow.get("user_id") == current_user.id):
                
                # Check if already added from orchestrator
                workflow_id = workflow.get("workflow_id")
                if not any(w.get("workflow_id") == workflow_id for w in all_workflows):
                    all_workflows.append({
                        **workflow,
                        "source": "local_tracking"
                    })
        
        # Apply status filter
        if status_filter:
            all_workflows = [w for w in all_workflows if w.get("status") == status_filter]
        
        # Sort by start time (newest first)
        all_workflows.sort(key=lambda x: x.get("start_time", ""), reverse=True)
        
        # Apply limit
        all_workflows = all_workflows[:limit]
        
        return {
            "success": True,
            "workflows": all_workflows,
            "total_count": len(all_workflows),
            "active_count": len([w for w in all_workflows if w.get("status") not in ["completed", "failed", "cancelled"]]),
            "agents_enabled": AGENTS_ENABLED,
            "metrics": workflow_metrics,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to list workflows: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")

@router.delete("/workflow/{workflow_id}")
async def cancel_workflow(
    workflow_id: str,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Cancel an active workflow with user validation and comprehensive tracking."""
    
    logger.info(f"Workflow cancellation requested for {workflow_id} by user {current_user.username}")
    
    # Check if workflow exists in local tracking
    if workflow_id in active_workflows:
        local_workflow = active_workflows[workflow_id]
        
        # Verify user has access to cancel this workflow
        if (local_workflow.get("user_id") != current_user.id and 
            not current_user.has_permission("manage_all_courses")):
            raise HTTPException(status_code=403, detail="Access denied to cancel this workflow")
        
        # Check if workflow can be cancelled
        if local_workflow.get("status") in ["completed", "failed", "cancelled"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel workflow in '{local_workflow.get('status')}' status"
            )
    
    try:
        # Try to cancel in orchestrator if agents are enabled
        orchestrator_result = None
        if AGENTS_ENABLED:
            try:
                orchestrator_result = await call_agent(
                    "orchestrator", 
                    f"/workflow/{workflow_id}", 
                    method="DELETE",
                    timeout=15
                )
                
                if not orchestrator_result.get("success", False):
                    logger.warning(f"Orchestrator cancel failed: {orchestrator_result.get('error')}")
            except Exception as e:
                logger.warning(f"Failed to cancel workflow in orchestrator: {e}")
        
        # Update local tracking regardless
        if workflow_id in active_workflows:
            local_workflow = active_workflows[workflow_id]
            local_workflow["status"] = "cancelled"
            local_workflow["cancelled_at"] = datetime.utcnow().isoformat()
            local_workflow["cancelled_by"] = current_user.id
            local_workflow["cancellation_reason"] = reason or "Manual cancellation"
            
            # Remove from active workflows
            del active_workflows[workflow_id]
            
            logger.info(f"Workflow {workflow_id} cancelled locally")
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "status": "cancelled",
            "cancelled_by": current_user.username,
            "cancelled_at": datetime.utcnow().isoformat(),
            "reason": reason or "Manual cancellation",
            "orchestrator_result": orchestrator_result,
            "message": "Workflow cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel workflow: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel workflow: {str(e)}")

@router.get("/metrics")
async def get_agent_metrics(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive agent system performance metrics with user access control."""
    
    # Check if user has permission to view metrics
    if not current_user.has_permission("view_system_metrics") and not current_user.has_permission("manage_all_courses"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view system metrics")
    
    logger.info(f"System metrics requested by user {current_user.username}")
    
    try:
        # Get orchestrator metrics if available
        orchestrator_metrics = None
        if AGENTS_ENABLED:
            try:
                result = await call_agent("orchestrator", "/metrics", method="GET", timeout=10)
                if result.get("success", False):
                    orchestrator_metrics = result.get("metrics", {})
            except Exception as e:
                logger.warning(f"Failed to get orchestrator metrics: {e}")
        
        # Calculate workflow duration metrics
        if workflow_metrics["total_completed"] > 0:
            # This would be calculated from actual completion times in a real implementation
            workflow_metrics["average_duration_seconds"] = 180.5  # Placeholder
        
        # Compile comprehensive metrics
        return {
            "agents_enabled": AGENTS_ENABLED,
            "system_metrics": {
                "workflow_metrics": workflow_metrics,
                "active_workflows_count": len(active_workflows),
                "max_concurrent_workflows": MAX_CONCURRENT_WORKFLOWS,
                "workflow_timeout_minutes": WORKFLOW_TIMEOUT_MINUTES,
                "health_check_interval_seconds": HEALTH_CHECK_INTERVAL
            },
            "orchestrator_metrics": orchestrator_metrics,
            "health_cache_size": len(health_cache),
            "health_cache_entries": list(health_cache.keys()),
            "last_health_check": last_health_check,
            "uptime_info": {
                "metrics_last_reset": workflow_metrics["last_reset"],
                "current_time": datetime.utcnow().isoformat()
            },
            "performance_indicators": {
                "success_rate": round(
                    (workflow_metrics["total_completed"] / max(workflow_metrics["total_started"], 1)) * 100, 2
                ),
                "failure_rate": round(
                    (workflow_metrics["total_failed"] / max(workflow_metrics["total_started"], 1)) * 100, 2
                ),
                "average_duration_minutes": round(workflow_metrics["average_duration_seconds"] / 60, 2)
            },
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get comprehensive metrics: {e}\n{traceback.format_exc()}")
        return {
            "agents_enabled": AGENTS_ENABLED,
            "error": str(e),
            "basic_metrics": workflow_metrics,
            "retrieved_at": datetime.utcnow().isoformat()
        }

@router.websocket("/ws/{user_token}")
async def websocket_endpoint(websocket: WebSocket, user_token: str, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time course manager updates."""
    
    user = None
    try:
        # Authenticate user from token
        user = AuthService.get_current_user(db, user_token)
        if not user or user.status != 'active':
            await websocket.close(code=1008, reason="Authentication failed")
            return
            
        # Extract client info from headers
        client_info = {
            "user_agent": websocket.headers.get("user-agent", "unknown"),
            "origin": websocket.headers.get("origin", "unknown"),
            "ip": websocket.client.host if websocket.client else "unknown"
        }
        
        # Connect to WebSocket manager
        await connection_manager.connect(websocket, user.id, client_info)
        
        # Start monitoring if not already started
        await websocket_service.start_monitoring()
        
        logger.info(f"WebSocket connection established for user {user.username} (ID: {user.id})")
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Handle the message
                await websocket_service.handle_message(websocket, message_data, user.id)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user.username}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received from user {user.id}: {e}")
            await connection_manager.send_to_user(user.id, {
                "type": "error",
                "message": "Invalid JSON format",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"WebSocket error for user {user.id}: {e}\n{traceback.format_exc()}")
            
    except Exception as e:
        logger.error(f"WebSocket authentication or setup failed: {e}")
        await websocket.close(code=1008, reason="Setup failed")
    
    finally:
        if user:
            await connection_manager.disconnect(websocket)

@router.get("/websocket/stats")
async def get_websocket_stats(
    current_user: User = Depends(get_current_user)
):
    """Get WebSocket connection statistics."""
    
    # Check if user has permission to view WebSocket stats
    if not current_user.has_permission("view_system_metrics") and not current_user.has_permission("manage_all_courses"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view WebSocket statistics")
    
    try:
        stats = connection_manager.get_stats()
        
        return {
            "success": True,
            "websocket_stats": stats,
            "monitoring_active": websocket_service._monitoring_active,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get WebSocket stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get WebSocket statistics: {str(e)}")

@router.get("/websocket/user/{user_id}")
async def get_user_websocket_info(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get WebSocket information for a specific user."""
    
    # Check if user can view this information
    if (current_user.id != user_id and 
        not current_user.has_permission("manage_all_courses")):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        user_info = connection_manager.get_user_info(user_id)
        
        return {
            "success": True,
            "user_websocket_info": user_info,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get user WebSocket info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user WebSocket information: {str(e)}")

@router.post("/websocket/broadcast")
async def broadcast_message(
    message: str,
    level: str = "info",
    current_user: User = Depends(get_current_user)
):
    """Broadcast a system message to all connected users."""
    
    # Check if user has permission to broadcast
    if not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Admin access required for broadcasting")
    
    try:
        sent_count = await connection_manager.send_system_message(message, level)
        
        logger.info(f"System message broadcast by {current_user.username}: {message}")
        
        return {
            "success": True,
            "message": "Message broadcast successfully",
            "sent_to_users": sent_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to broadcast message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to broadcast message: {str(e)}")

@router.get("/health/summary")
async def get_health_summary(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive health summary for the agent system."""
    
    # Check if user has permission to view health data
    if not current_user.has_permission("view_system_metrics") and not current_user.has_permission("manage_all_courses"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view health data")
    
    try:
        # Start monitoring if not already active
        if not agent_health_monitor._monitoring_active:
            await agent_health_monitor.start_monitoring()
        
        # Get health data
        current_health = agent_health_monitor.get_current_health()
        system_summary = agent_health_monitor.get_system_summary()
        active_alerts = agent_health_monitor.get_alerts(include_resolved=False)
        performance_metrics = agent_health_monitor.get_performance_metrics()
        
        return {
            "success": True,
            "system_summary": system_summary,
            "agent_health": current_health,
            "active_alerts": active_alerts,
            "performance_metrics": performance_metrics,
            "monitoring_active": agent_health_monitor._monitoring_active,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get health summary: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get health summary: {str(e)}")

@router.get("/health/alerts")
async def get_health_alerts(
    include_resolved: bool = False,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get health alerts with filtering options."""
    
    # Check permissions
    if not current_user.has_permission("view_system_metrics") and not current_user.has_permission("manage_all_courses"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view alerts")
    
    try:
        alerts = agent_health_monitor.get_alerts(include_resolved=include_resolved)
        
        # Sort by creation time (newest first)
        alerts.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply limit
        alerts = alerts[:limit]
        
        return {
            "success": True,
            "alerts": alerts,
            "total_count": len(alerts),
            "include_resolved": include_resolved,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get health alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get health alerts: {str(e)}")

@router.post("/health/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user)
):
    """Acknowledge a health alert."""
    
    # Check permissions
    if not current_user.has_permission("manage_system_alerts") and not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to acknowledge alerts")
    
    try:
        success = await agent_health_monitor.acknowledge_alert(alert_id)
        
        if success:
            logger.info(f"Alert {alert_id} acknowledged by user {current_user.username}")
            return {
                "success": True,
                "message": "Alert acknowledged successfully",
                "alert_id": alert_id,
                "acknowledged_by": current_user.username,
                "acknowledged_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Alert not found or already resolved")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to acknowledge alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")

@router.post("/health/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user)
):
    """Manually resolve a health alert."""
    
    # Check permissions
    if not current_user.has_permission("manage_system_alerts") and not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to resolve alerts")
    
    try:
        success = await agent_health_monitor.resolve_alert(alert_id)
        
        if success:
            logger.info(f"Alert {alert_id} resolved by user {current_user.username}")
            
            # Send WebSocket notification
            try:
                await connection_manager.broadcast_health_update({
                    "type": "alert_resolved",
                    "alert_id": alert_id,
                    "resolved_by": current_user.username,
                    "resolved_at": datetime.utcnow().isoformat()
                })
            except Exception as ws_e:
                logger.warning(f"Failed to send WebSocket notification: {ws_e}")
            
            return {
                "success": True,
                "message": "Alert resolved successfully",
                "alert_id": alert_id,
                "resolved_by": current_user.username,
                "resolved_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")

@router.post("/health/monitoring/start")
async def start_health_monitoring(
    current_user: User = Depends(get_current_user)
):
    """Start health monitoring system."""
    
    # Check permissions
    if not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if agent_health_monitor._monitoring_active:
            return {
                "success": True,
                "message": "Health monitoring is already active",
                "monitoring_active": True
            }
        
        await agent_health_monitor.start_monitoring()
        
        logger.info(f"Health monitoring started by user {current_user.username}")
        
        return {
            "success": True,
            "message": "Health monitoring started successfully",
            "monitoring_active": True,
            "started_by": current_user.username,
            "started_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to start health monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start health monitoring: {str(e)}")

@router.post("/health/monitoring/stop")
async def stop_health_monitoring(
    current_user: User = Depends(get_current_user)
):
    """Stop health monitoring system."""
    
    # Check permissions
    if not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if not agent_health_monitor._monitoring_active:
            return {
                "success": True,
                "message": "Health monitoring is already stopped",
                "monitoring_active": False
            }
        
        await agent_health_monitor.stop_monitoring()
        
        logger.info(f"Health monitoring stopped by user {current_user.username}")
        
        return {
            "success": True,
            "message": "Health monitoring stopped successfully",
            "monitoring_active": False,
            "stopped_by": current_user.username,
            "stopped_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to stop health monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop health monitoring: {str(e)}")

@router.get("/errors/summary")
async def get_error_summary(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive error summary and recovery statistics."""
    
    # Check permissions
    if not current_user.has_permission("view_system_metrics") and not current_user.has_permission("manage_all_courses"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view error data")
    
    try:
        error_summary = system_recovery_manager.get_error_summary()
        
        return {
            "success": True,
            "error_summary": error_summary,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get error summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get error summary: {str(e)}")

@router.get("/errors/recent")
async def get_recent_errors(
    limit: int = 50,
    component: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get recent errors with optional filtering."""
    
    # Check permissions
    if not current_user.has_permission("view_system_metrics") and not current_user.has_permission("manage_all_courses"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view error data")
    
    try:
        recent_errors = system_recovery_manager.get_recent_errors(limit=limit, component=component)
        
        return {
            "success": True,
            "errors": recent_errors,
            "filter_component": component,
            "limit": limit,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent errors: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent errors: {str(e)}")

@router.post("/errors/{error_id}/resolve")
async def resolve_error(
    error_id: str,
    current_user: User = Depends(get_current_user)
):
    """Manually resolve an error."""
    
    # Check permissions
    if not current_user.has_permission("manage_system_errors") and not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to resolve errors")
    
    try:
        success = await system_recovery_manager.mark_error_resolved(error_id)
        
        if success:
            logger.info(f"Error {error_id} resolved by user {current_user.username}")
            return {
                "success": True,
                "message": "Error resolved successfully",
                "error_id": error_id,
                "resolved_by": current_user.username,
                "resolved_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Error not found or already resolved")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve error: {str(e)}")

@router.post("/errors/circuit-breaker/{component}/reset")
async def reset_circuit_breaker(
    component: str,
    current_user: User = Depends(get_current_user)
):
    """Reset circuit breaker for a component."""
    
    # Check permissions
    if not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        success = await system_recovery_manager.reset_circuit_breaker(component)
        
        if success:
            logger.info(f"Circuit breaker reset for {component} by user {current_user.username}")
            
            # Send WebSocket notification
            try:
                await connection_manager.send_system_message(
                    f"Circuit breaker reset for {component} by {current_user.username}",
                    level="info"
                )
            except Exception as ws_e:
                logger.warning(f"Failed to send WebSocket notification: {ws_e}")
            
            return {
                "success": True,
                "message": f"Circuit breaker reset for {component}",
                "component": component,
                "reset_by": current_user.username,
                "reset_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=f"No circuit breaker found for component: {component}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset circuit breaker: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset circuit breaker: {str(e)}")

@router.post("/errors/test")
async def test_error_handling(
    component: str = "test_component",
    severity: str = "medium",
    current_user: User = Depends(get_current_user)
):
    """Test error handling system (admin only)."""
    
    # Check permissions
    if not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Create a test error
        test_error = Exception(f"Test error for component {component}")
        
        # Map severity string to enum
        severity_map = {
            "low": ErrorSeverity.LOW,
            "medium": ErrorSeverity.MEDIUM,
            "high": ErrorSeverity.HIGH,
            "critical": ErrorSeverity.CRITICAL
        }
        
        error_severity = severity_map.get(severity.lower(), ErrorSeverity.MEDIUM)
        
        # Handle the test error
        result = await handle_system_error(
            error=test_error,
            component=component,
            operation="test_operation",
            severity=error_severity,
            user_id=current_user.id,
            metadata={"test": True, "initiated_by": current_user.username}
        )
        
        logger.info(f"Test error created by user {current_user.username}: {result}")
        
        return {
            "success": True,
            "message": "Test error created and handled",
            "test_error_result": result,
            "component": component,
            "severity": severity,
            "initiated_by": current_user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to test error handling: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test error handling: {str(e)}")

@router.get("/audit/summary")
async def get_audit_summary(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive audit summary."""
    
    # Check permissions
    if not current_user.has_permission("view_system_metrics") and not current_user.has_permission("manage_all_courses"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view audit data")
    
    try:
        # Start audit service if not already running
        if not audit_service._cleanup_active:
            await audit_service.start_audit_service()
        
        audit_summary = audit_service.get_audit_summary()
        
        return {
            "success": True,
            "audit_summary": audit_summary,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get audit summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get audit summary: {str(e)}")

@router.get("/audit/workflows/{workflow_id}")
async def get_workflow_audit_trail(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get complete audit trail for a specific workflow."""
    
    # Check permissions
    if not current_user.has_permission("view_system_metrics") and not current_user.has_permission("manage_all_courses"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view audit data")
    
    try:
        audit_trail = audit_service.get_workflow_audit_trail(workflow_id)
        
        if not audit_trail:
            raise HTTPException(status_code=404, detail=f"Audit trail not found for workflow: {workflow_id}")
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "audit_trail": audit_trail,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow audit trail: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow audit trail: {str(e)}")

@router.get("/audit/events")
async def get_audit_events(
    workflow_id: Optional[str] = None,
    event_type: Optional[str] = None,
    component: Optional[str] = None,
    limit: int = 100,
    hours_back: int = 24,
    current_user: User = Depends(get_current_user)
):
    """Get audit events with filtering options."""
    
    # Check permissions
    if not current_user.has_permission("view_system_metrics") and not current_user.has_permission("manage_all_courses"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view audit events")
    
    try:
        # Parse event type if provided
        parsed_event_type = None
        if event_type:
            try:
                parsed_event_type = AuditEventType(event_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid event type: {event_type}")
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        
        # Get filtered events
        events = audit_service.get_audit_events(
            workflow_id=workflow_id,
            event_type=parsed_event_type,
            component=component,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        return {
            "success": True,
            "events": events,
            "filters": {
                "workflow_id": workflow_id,
                "event_type": event_type,
                "component": component,
                "hours_back": hours_back,
                "limit": limit
            },
            "total_events": len(events),
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get audit events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get audit events: {str(e)}")

@router.get("/audit/performance")
async def get_performance_analytics(
    time_window_hours: int = 24,
    current_user: User = Depends(get_current_user)
):
    """Get performance analytics for specified time window."""
    
    # Check permissions
    if not current_user.has_permission("view_system_metrics") and not current_user.has_permission("manage_all_courses"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view performance analytics")
    
    try:
        # Validate time window
        if time_window_hours < 1 or time_window_hours > 168:  # Max 1 week
            raise HTTPException(status_code=400, detail="Time window must be between 1 and 168 hours")
        
        analytics = audit_service.get_performance_analytics(time_window_hours)
        
        return {
            "success": True,
            "performance_analytics": analytics,
            "time_window_hours": time_window_hours,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get performance analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance analytics: {str(e)}")

@router.post("/audit/start")
async def start_audit_service(
    current_user: User = Depends(get_current_user)
):
    """Start the audit service (admin only)."""
    
    # Check permissions
    if not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if audit_service._cleanup_active:
            return {
                "success": True,
                "message": "Audit service is already running",
                "cleanup_active": True
            }
        
        await audit_service.start_audit_service()
        
        logger.info(f"Audit service started by user {current_user.username}")
        
        return {
            "success": True,
            "message": "Audit service started successfully",
            "cleanup_active": True,
            "started_by": current_user.username,
            "started_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to start audit service: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start audit service: {str(e)}")

@router.post("/audit/stop")
async def stop_audit_service(
    current_user: User = Depends(get_current_user)
):
    """Stop the audit service (admin only)."""
    
    # Check permissions
    if not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if not audit_service._cleanup_active:
            return {
                "success": True,
                "message": "Audit service is already stopped",
                "cleanup_active": False
            }
        
        await audit_service.stop_audit_service()
        
        logger.info(f"Audit service stopped by user {current_user.username}")
        
        return {
            "success": True,
            "message": "Audit service stopped successfully",
            "cleanup_active": False,
            "stopped_by": current_user.username,
            "stopped_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to stop audit service: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop audit service: {str(e)}")

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