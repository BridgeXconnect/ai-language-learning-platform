"""
FastAPI server wrapper for Quality Assurance Agent
Provides HTTP endpoints for content quality review and improvement
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import uvicorn
import asyncio
from datetime import datetime

from main import QualityAssuranceService, QualityReviewRequest, QualityReport, ContentImprovement

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Quality Assurance Agent",
    description="AI agent for reviewing and improving course content quality",
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
qa_service = QualityAssuranceService()

# Pydantic models for API
class ReviewContentRequest(BaseModel):
    content_id: str
    content_type: str
    content_data: Dict[str, Any]
    target_cefr_level: str
    review_criteria: List[str] = ["linguistic_accuracy", "cefr_alignment", "cultural_sensitivity", "engagement_relevance"]
    company_context: Optional[Dict[str, Any]] = None

class ImproveContentRequest(BaseModel):
    content: Dict[str, Any]
    quality_issues: List[Dict[str, Any]]

class BatchReviewRequest(BaseModel):
    content_items: List[Dict[str, Any]]
    review_criteria: List[str] = ["linguistic_accuracy", "cefr_alignment", "cultural_sensitivity"]

class QAResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_seconds: Optional[float] = None

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
    reviews_processed: int
    last_activity: Optional[str] = None

# Global metrics
start_time = datetime.utcnow()
reviews_processed = 0
last_activity = None

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global last_activity
    last_activity = datetime.utcnow().isoformat()
    
    capabilities = await qa_service.get_qa_capabilities()
    
    return HealthResponse(
        status="healthy",
        agent="Quality Assurance Agent",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        capabilities=capabilities
    )

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get detailed agent status."""
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    return StatusResponse(
        agent_name="Quality Assurance Agent",
        status="active",
        uptime_seconds=uptime,
        reviews_processed=reviews_processed,
        last_activity=last_activity
    )

@app.get("/capabilities")
async def get_capabilities():
    """Get agent capabilities and supported features."""
    return await qa_service.get_qa_capabilities()

@app.post("/review-content", response_model=QAResponse)
async def review_content(request: ReviewContentRequest):
    """Review content for quality and provide detailed analysis."""
    global reviews_processed, last_activity
    
    start_time_req = datetime.utcnow()
    reviews_processed += 1
    last_activity = start_time_req.isoformat()
    
    try:
        logger.info(f"Reviewing {request.content_type} content: {request.content_id}")
        
        # Validate request
        review_request = QualityReviewRequest(**request.dict())
        validation = await qa_service.validate_review_request(review_request)
        
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid review request: {', '.join(validation['errors'])}"
            )
        
        # Perform quality review
        quality_report = await qa_service.review_content(review_request)
        
        processing_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        logger.info(f"Content review completed in {processing_time:.2f} seconds")
        logger.info(f"Quality score: {quality_report.overall_score}, Approved: {quality_report.approved_for_release}")
        
        return QAResponse(
            success=True,
            result=quality_report.dict(),
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        logger.error(f"Content review failed: {e}")
        processing_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        return QAResponse(
            success=False,
            error=str(e),
            processing_time_seconds=processing_time
        )

@app.post("/improve-content", response_model=QAResponse)
async def improve_content(request: ImproveContentRequest):
    """Generate improved content based on quality issues."""
    global reviews_processed, last_activity
    
    start_time_req = datetime.utcnow()
    reviews_processed += 1
    last_activity = start_time_req.isoformat()
    
    try:
        logger.info(f"Improving content with {len(request.quality_issues)} issues")
        
        # Generate improvements
        improvement = await qa_service.improve_content(
            content=request.content,
            quality_issues=request.quality_issues
        )
        
        processing_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        logger.info(f"Content improvement completed in {processing_time:.2f} seconds")
        logger.info(f"Improvement score: {improvement.improvement_score}")
        
        return QAResponse(
            success=True,
            result=improvement.dict(),
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        logger.error(f"Content improvement failed: {e}")
        processing_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        return QAResponse(
            success=False,
            error=str(e),
            processing_time_seconds=processing_time
        )

@app.post("/batch-review", response_model=QAResponse)
async def batch_review(request: BatchReviewRequest):
    """Review multiple content items in batch."""
    global reviews_processed, last_activity
    
    start_time_req = datetime.utcnow()
    reviews_processed += len(request.content_items)
    last_activity = start_time_req.isoformat()
    
    try:
        logger.info(f"Starting batch review of {len(request.content_items)} items")
        
        # Perform batch review
        review_results = await qa_service.batch_review(
            content_items=request.content_items,
            criteria=request.review_criteria
        )
        
        processing_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        # Generate summary metrics
        metrics = await qa_service.generate_quality_metrics(review_results)
        
        logger.info(f"Batch review completed in {processing_time:.2f} seconds")
        logger.info(f"Approval rate: {metrics['summary']['approval_rate']:.1f}%")
        
        return QAResponse(
            success=True,
            result={
                "reviews": [report.dict() for report in review_results],
                "metrics": metrics,
                "summary": {
                    "total_items": len(review_results),
                    "approved_items": len([r for r in review_results if r.approved_for_release]),
                    "average_score": sum(r.overall_score for r in review_results) / len(review_results)
                }
            },
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        logger.error(f"Batch review failed: {e}")
        processing_time = (datetime.utcnow() - start_time_req).total_seconds()
        
        return QAResponse(
            success=False,
            error=str(e),
            processing_time_seconds=processing_time
        )

@app.post("/review-content-async")
async def review_content_async(request: ReviewContentRequest, background_tasks: BackgroundTasks):
    """Review content asynchronously."""
    global reviews_processed, last_activity
    
    reviews_processed += 1
    last_activity = datetime.utcnow().isoformat()
    
    task_id = f"review_{request.content_id}_{int(datetime.utcnow().timestamp())}"
    
    # Add background task
    background_tasks.add_task(review_content_background, request, task_id)
    
    return {
        "task_id": task_id,
        "status": "queued",
        "message": f"Quality review started for {request.content_type}: {request.content_id}"
    }

async def review_content_background(request: ReviewContentRequest, task_id: str):
    """Background task for content review."""
    try:
        logger.info(f"Background review started for task {task_id}")
        
        review_request = QualityReviewRequest(**request.dict())
        quality_report = await qa_service.review_content(review_request)
        
        # Here you would typically save the result to a database or cache
        logger.info(f"Background review completed for task {task_id}")
        logger.info(f"Quality score: {quality_report.overall_score}")
        
    except Exception as e:
        logger.error(f"Background review failed for task {task_id}: {e}")

@app.post("/validate-review-request")
async def validate_review_request(request: ReviewContentRequest):
    """Validate a quality review request."""
    try:
        review_request = QualityReviewRequest(**request.dict())
        validation = await qa_service.validate_review_request(review_request)
        return validation
    except Exception as e:
        logger.error(f"Review request validation failed: {e}")
        return {
            "valid": False,
            "errors": [str(e)],
            "warnings": []
        }

@app.get("/review-criteria")
async def get_review_criteria():
    """Get available review criteria and their descriptions."""
    capabilities = await qa_service.get_qa_capabilities()
    return {
        "criteria": capabilities.get("review_criteria", []),
        "descriptions": {
            "linguistic_accuracy": "Grammar, vocabulary usage, language level appropriateness",
            "cefr_alignment": "Alignment with target CEFR level requirements",
            "pedagogical_effectiveness": "Learning design quality and activity effectiveness",
            "cultural_sensitivity": "Inclusive language and cultural appropriateness",
            "engagement_relevance": "Workplace applicability and learner motivation",
            "technical_quality": "Formatting, instructions clarity, assessment validity"
        },
        "weights": {
            "linguistic_accuracy": 25,
            "pedagogical_effectiveness": 25,
            "cultural_sensitivity": 20,
            "engagement_relevance": 20,
            "technical_quality": 10
        }
    }

@app.get("/quality-standards")
async def get_quality_standards():
    """Get quality standards and thresholds."""
    capabilities = await qa_service.get_qa_capabilities()
    return capabilities.get("quality_standards", {})

@app.post("/generate-quality-metrics")
async def generate_quality_metrics(review_results: List[Dict[str, Any]]):
    """Generate quality metrics from review results."""
    global reviews_processed, last_activity
    
    last_activity = datetime.utcnow().isoformat()
    
    try:
        # Convert to QualityReport objects
        quality_reports = []
        for result in review_results:
            if isinstance(result, dict):
                quality_reports.append(QualityReport(**result))
            else:
                quality_reports.append(result)
        
        metrics = await qa_service.generate_quality_metrics(quality_reports)
        
        return {
            "success": True,
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Metrics generation failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/metrics")
async def get_metrics():
    """Get agent performance metrics."""
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    return {
        "agent": "Quality Assurance Agent",
        "uptime_seconds": uptime,
        "uptime_hours": round(uptime / 3600, 2),
        "reviews_processed": reviews_processed,
        "reviews_per_hour": round(reviews_processed / (uptime / 3600), 2) if uptime > 0 else 0,
        "last_activity": last_activity,
        "start_time": start_time.isoformat(),
        "current_time": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint with agent information."""
    return {
        "agent": "Quality Assurance Agent",
        "version": "1.0.0",
        "description": "Reviews and improves generated course content for quality and effectiveness",
        "status": "active",
        "endpoints": [
            "/health", "/status", "/capabilities",
            "/review-content", "/improve-content", "/batch-review",
            "/review-content-async", "/validate-review-request",
            "/review-criteria", "/quality-standards", "/metrics"
        ]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint not found",
        "agent": "Quality Assurance Agent",
        "available_endpoints": [
            "/health", "/status", "/capabilities", "/review-content",
            "/improve-content", "/batch-review", "/metrics"
        ]
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal server error",
        "agent": "Quality Assurance Agent",
        "message": "Please check agent logs for details"
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Quality Assurance Agent server starting up...")
    logger.info("Checking agent capabilities...")
    
    try:
        capabilities = await qa_service.get_qa_capabilities()
        logger.info(f"Agent capabilities: {capabilities}")
        logger.info("Quality Assurance Agent server ready!")
    except Exception as e:
        logger.error(f"Startup check failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Quality Assurance Agent server shutting down...")
    logger.info(f"Total reviews processed: {reviews_processed}")
    uptime = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Total uptime: {uptime:.2f} seconds ({uptime/3600:.2f} hours)")

# Main execution
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8103,
        reload=True,
        log_level="info"
    )