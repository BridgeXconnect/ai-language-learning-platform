"""
FastAPI server wrapper for Agent Orchestrator
Provides HTTP endpoints for multi-agent workflow coordination
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import uvicorn
import asyncio
from datetime import datetime

from main import AgentOrchestrator, CourseGenerationRequest, WorkflowResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agent Orchestrator",
    description="Multi-agent workflow coordination for course generation",
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

# Initialize orchestrator
orchestrator = AgentOrchestrator()

# Pydantic models for API
class GenerateCourseRequest(BaseModel):
    course_request_id: int
    company_name: str
    industry: str
    training_goals: str
    current_english_level: str
    duration_weeks: int = 8
    target_audience: str = "Professional staff"
    specific_needs: Optional[str] = None

class OrchestrationResponse(BaseModel):
    success: bool
    workflow_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_seconds: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    orchestrator: str
    version: str
    timestamp: str
    agent_health: Dict[str, Any]

class StatusResponse(BaseModel):
    orchestrator_name: str
    status: str
    uptime_seconds: float
    workflows_processed: int
    active_workflows: int
    last_activity: Optional[str] = None

# Global metrics
start_time = datetime.utcnow()
workflows_processed = 0
last_activity = None

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global last_activity
    last_activity = datetime.utcnow().isoformat()
    
    # Check all agents health
    agent_health = await orchestrator.agent_client.check_all_agents_health()
    
    # Determine overall health
    all_healthy = all(status.get("healthy", False) for status in agent_health.values())
    overall_status = "healthy" if all_healthy else "degraded"
    
    return HealthResponse(
        status=overall_status,
        orchestrator="Agent Orchestrator",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        agent_health=agent_health
    )

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get detailed orchestrator status."""
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    return StatusResponse(
        orchestrator_name="Agent Orchestrator",
        status="active",
        uptime_seconds=uptime,
        workflows_processed=workflows_processed,
        active_workflows=len(orchestrator.active_workflows),
        last_activity=last_activity
    )

@app.get("/capabilities")
async def get_capabilities():
    """Get orchestrator capabilities."""
    return {
        "orchestrator_name": "Agent Orchestrator",
        "version": "1.0.0",
        "capabilities": [
            "Multi-agent workflow coordination",
            "Sequential agent processing (Planner → Creator → QA)",
            "Intelligent error recovery and retries",
            "Real-time workflow status tracking",
            "Quality gates and validation",
            "Performance monitoring and metrics"
        ],
        "managed_agents": [
            "Course Planner Agent (port 8101)",
            "Content Creator Agent (port 8102)",
            "Quality Assurance Agent (port 8103)"
        ],
        "workflow_stages": [
            "initialization",
            "course_planning", 
            "content_creation",
            "quality_review",
            "content_improvement",
            "finalization"
        ],
        "quality_standards": {
            "planning_threshold": 75,
            "quality_threshold": 80,
            "max_retries": 3
        },
        "status": "active"
    }

@app.post("/orchestrate-course", response_model=OrchestrationResponse)
async def orchestrate_course_generation(request: GenerateCourseRequest):
    """Orchestrate the complete course generation workflow."""
    global workflows_processed, last_activity
    
    start_time_req = datetime.utcnow()
    workflows_processed += 1
    last_activity = start_time_req.isoformat()
    
    try:
        logger.info(f"Starting course generation orchestration for {request.company_name}")
        
        # Create course generation request
        course_request = CourseGenerationRequest(**request.dict())
        
        # Execute workflow
        workflow_result = await orchestrator.orchestrate_workflow(course_request)
        
        processing_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        logger.info(f"Workflow orchestration completed in {processing_time:.2f} seconds")
        logger.info(f"Workflow status: {workflow_result.status}")
        
        return OrchestrationResponse(
            success=workflow_result.status == "completed",
            workflow_result=workflow_result.dict(),
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        logger.error(f"Course generation orchestration failed: {e}")
        processing_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        return OrchestrationResponse(
            success=False,
            error=str(e),
            processing_time_seconds=processing_time
        )

@app.post("/orchestrate-course-async")
async def orchestrate_course_async(request: GenerateCourseRequest, background_tasks: BackgroundTasks):
    """Orchestrate course generation asynchronously."""
    global workflows_processed, last_activity
    
    workflows_processed += 1
    last_activity = datetime.utcnow().isoformat()
    
    workflow_id = f"async_workflow_{request.course_request_id}_{int(datetime.utcnow().timestamp())}"
    
    # Add background task
    background_tasks.add_task(orchestrate_course_background, request, workflow_id)
    
    return {
        "workflow_id": workflow_id,
        "status": "queued",
        "message": f"Course generation orchestration started for {request.company_name}",
        "estimated_completion": "5-10 minutes"
    }

async def orchestrate_course_background(request: GenerateCourseRequest, workflow_id: str):
    """Background task for course orchestration."""
    try:
        logger.info(f"Background orchestration started for workflow {workflow_id}")
        
        course_request = CourseGenerationRequest(**request.dict())
        workflow_result = await orchestrator.orchestrate_workflow(course_request)
        
        # Here you would typically save the result to a database or cache
        logger.info(f"Background orchestration completed for workflow {workflow_id}")
        logger.info(f"Final status: {workflow_result.status}")
        
    except Exception as e:
        logger.error(f"Background orchestration failed for workflow {workflow_id}: {e}")

@app.get("/workflow/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get the status of a specific workflow."""
    
    workflow_result = await orchestrator.get_workflow_status(workflow_id)
    
    if not workflow_result:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    return {
        "workflow_id": workflow_id,
        "status": workflow_result.status,
        "result": workflow_result.dict()
    }

@app.delete("/workflow/{workflow_id}")
async def cancel_workflow(workflow_id: str):
    """Cancel an active workflow."""
    
    cancelled = await orchestrator.cancel_workflow(workflow_id)
    
    if not cancelled:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found or not cancellable")
    
    return {
        "workflow_id": workflow_id,
        "status": "cancelled",
        "message": "Workflow cancelled successfully"
    }

@app.get("/workflows")
async def list_workflows():
    """List all workflows (active and completed)."""
    
    return {
        "active_workflows": {
            wf_id: {
                "status": wf.status,
                "course_request_id": wf.course_request_id,
                "start_time": wf.start_time
            }
            for wf_id, wf in orchestrator.active_workflows.items()
        },
        "completed_workflows": [
            {
                "workflow_id": wf.workflow_id,
                "status": wf.status,
                "course_request_id": wf.course_request_id,
                "start_time": wf.start_time,
                "completion_time": wf.completion_time,
                "duration_seconds": wf.total_duration_seconds
            }
            for wf in orchestrator.completed_workflows[-10:]  # Last 10 completed
        ],
        "summary": {
            "active_count": len(orchestrator.active_workflows),
            "completed_count": len(orchestrator.completed_workflows),
            "total_processed": workflows_processed
        }
    }

@app.get("/agents/health")
async def check_agents_health():
    """Check health of all managed agents."""
    
    health_status = await orchestrator.agent_client.check_all_agents_health()
    
    # Add summary
    healthy_count = sum(1 for status in health_status.values() if status.get("healthy", False))
    total_count = len(health_status)
    
    return {
        "agent_health": health_status,
        "summary": {
            "healthy_agents": healthy_count,
            "total_agents": total_count,
            "all_healthy": healthy_count == total_count,
            "system_status": "operational" if healthy_count == total_count else "degraded"
        },
        "checked_at": datetime.utcnow().isoformat()
    }

@app.get("/agents/capabilities")
async def get_agents_capabilities():
    """Get capabilities of all managed agents."""
    
    capabilities = await orchestrator.agent_client.get_all_agent_capabilities()
    
    return {
        "agent_capabilities": capabilities,
        "retrieved_at": datetime.utcnow().isoformat()
    }

@app.post("/agents/test")
async def test_all_agents():
    """Test basic functionality of all agents."""
    
    test_results = await orchestrator.agent_client.test_all_agents()
    
    return test_results

@app.get("/agents/ping")
async def ping_all_agents():
    """Quick ping test for all agents."""
    
    ping_results = await orchestrator.agent_client.ping_all_agents()
    
    return ping_results

@app.get("/metrics")
async def get_metrics():
    """Get orchestrator performance metrics."""
    
    orchestrator_metrics = await orchestrator.get_orchestrator_metrics()
    client_metrics = orchestrator.agent_client.get_client_metrics()
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    return {
        "orchestrator_metrics": orchestrator_metrics,
        "client_metrics": client_metrics,
        "server_metrics": {
            "uptime_seconds": uptime,
            "uptime_hours": round(uptime / 3600, 2),
            "workflows_processed": workflows_processed,
            "workflows_per_hour": round(workflows_processed / (uptime / 3600), 2) if uptime > 0 else 0,
            "last_activity": last_activity,
            "start_time": start_time.isoformat(),
            "current_time": datetime.utcnow().isoformat()
        }
    }

@app.get("/config")
async def get_configuration():
    """Get orchestrator configuration."""
    
    return {
        "workflow_config": orchestrator.workflow.config,
        "agent_endpoints": orchestrator.agent_client.agent_endpoints,
        "client_config": {
            "timeout_seconds": orchestrator.agent_client.timeout.total,
            "retry_attempts": orchestrator.agent_client.retry_attempts,
            "retry_delay": orchestrator.agent_client.retry_delay
        }
    }

@app.get("/")
async def root():
    """Root endpoint with orchestrator information."""
    return {
        "orchestrator": "Agent Orchestrator",
        "version": "1.0.0",
        "description": "Multi-agent workflow coordination for course generation",
        "status": "active",
        "managed_agents": [
            "Course Planner Agent",
            "Content Creator Agent", 
            "Quality Assurance Agent"
        ],
        "workflow": "Course Planner → Content Creator → Quality Assurance",
        "endpoints": [
            "/health", "/status", "/capabilities",
            "/orchestrate-course", "/orchestrate-course-async",
            "/workflow/{id}", "/workflows",
            "/agents/health", "/agents/capabilities", "/agents/test", "/agents/ping",
            "/metrics", "/config"
        ]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint not found",
        "orchestrator": "Agent Orchestrator",
        "available_endpoints": [
            "/health", "/status", "/capabilities", "/orchestrate-course",
            "/workflow/{id}", "/workflows", "/agents/health", "/metrics"
        ]
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal server error",
        "orchestrator": "Agent Orchestrator",
        "message": "Please check orchestrator logs for details"
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Agent Orchestrator server starting up...")
    logger.info("Checking managed agents...")
    
    try:
        # Check agent health on startup
        health_status = await orchestrator.agent_client.check_all_agents_health()
        healthy_agents = [name for name, status in health_status.items() if status.get("healthy", False)]
        
        logger.info(f"Agent health check: {len(healthy_agents)}/{len(health_status)} agents healthy")
        
        if len(healthy_agents) == len(health_status):
            logger.info("All agents healthy - Agent Orchestrator ready!")
        else:
            unhealthy = [name for name in health_status.keys() if name not in healthy_agents]
            logger.warning(f"Some agents unhealthy: {unhealthy}")
            logger.info("Agent Orchestrator starting in degraded mode")
        
    except Exception as e:
        logger.error(f"Startup agent check failed: {e}")
        logger.info("Agent Orchestrator starting without agent verification")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Agent Orchestrator server shutting down...")
    logger.info(f"Total workflows processed: {workflows_processed}")
    logger.info(f"Active workflows: {len(orchestrator.active_workflows)}")
    logger.info(f"Completed workflows: {len(orchestrator.completed_workflows)}")
    
    uptime = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Total uptime: {uptime:.2f} seconds ({uptime/3600:.2f} hours)")

# Main execution
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8100,
        reload=True,
        log_level="info"
    )