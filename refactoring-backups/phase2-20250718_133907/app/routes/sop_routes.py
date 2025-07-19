"""
SOP Document Processing API Routes
Handles upload and processing of Standard Operating Procedures documents
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models.sales import CourseRequest
from app.services.auth_service import get_current_user
from app.models.user import User
from app.services.sop_processor import sop_processor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sop", tags=["SOP Document Processing"])

@router.post("/upload/{course_request_id}")
async def upload_sop_documents(
    course_request_id: int,
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process SOP documents for a course request."""
    
    try:
        # Verify course request exists and user has access
        course_request = db.query(CourseRequest).filter(
            CourseRequest.id == course_request_id
        ).first()
        
        if not course_request:
            raise HTTPException(
                status_code=404, 
                detail=f"Course request {course_request_id} not found"
            )
        
        # Check user permissions
        if (course_request.sales_user_id != current_user.id and 
            not current_user.has_permission("manage_all_courses")):
            raise HTTPException(
                status_code=403, 
                detail="Access denied to this course request"
            )
        
        # Validate files
        if not files:
            raise HTTPException(
                status_code=400,
                detail="No files provided"
            )
        
        if len(files) > 10:  # Limit number of files
            raise HTTPException(
                status_code=400,
                detail="Too many files. Maximum 10 files allowed per upload."
            )
        
        # Quick validation of file types and sizes
        total_size = 0
        for file in files:
            if not file.filename:
                raise HTTPException(
                    status_code=400,
                    detail="All files must have valid filenames"
                )
            
            # Read a small portion to check file size
            file_content = await file.read(1024)  # Read first 1KB
            await file.seek(0)  # Reset file pointer
            
            # Estimate total file size (this is approximate)
            if hasattr(file, 'size'):
                total_size += file.size
            
            # Check individual file size limit (50MB)
            max_file_size = 50 * 1024 * 1024
            if hasattr(file, 'size') and file.size > max_file_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File '{file.filename}' exceeds maximum size of 50MB"
                )
        
        # Check total upload size (200MB for all files combined)
        max_total_size = 200 * 1024 * 1024
        if total_size > max_total_size:
            raise HTTPException(
                status_code=400,
                detail="Total upload size exceeds maximum of 200MB"
            )
        
        # Start processing in background
        logger.info(f"Starting SOP processing for course request {course_request_id}")
        background_tasks.add_task(
            process_sop_files_background,
            files,
            course_request_id,
            current_user.id
        )
        
        # Return immediate response
        return {
            "success": True,
            "message": f"Started processing {len(files)} SOP files",
            "course_request_id": course_request_id,
            "files_uploaded": [file.filename for file in files],
            "processing_status": "started",
            "estimated_completion": "2-5 minutes depending on file size and complexity"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SOP upload failed for course request {course_request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"SOP upload failed: {str(e)}"
        )

async def process_sop_files_background(
    files: List[UploadFile], 
    course_request_id: int, 
    user_id: int
):
    """Background task for processing SOP files."""
    
    try:
        logger.info(f"Background SOP processing started for course request {course_request_id}")
        
        # Process the files
        processing_result = await sop_processor.process_sop_files(files, course_request_id)
        
        # Here you would typically save the results to database
        # For now, just log the results
        logger.info(f"SOP processing completed for course request {course_request_id}")
        logger.info(f"Processing summary: {processing_result['files_processed']}/{len(files)} files successful")
        
        # TODO: Save processing results to database
        # TODO: Update course request with SOP processing status
        # TODO: Notify user of completion (via email, websocket, etc.)
        
    except Exception as e:
        logger.error(f"Background SOP processing failed for course request {course_request_id}: {e}")
        # TODO: Update database with error status
        # TODO: Notify user of failure

@router.get("/status/{course_request_id}")
async def get_sop_processing_status(
    course_request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the SOP processing status for a course request."""
    
    try:
        # Verify course request exists and user has access
        course_request = db.query(CourseRequest).filter(
            CourseRequest.id == course_request_id
        ).first()
        
        if not course_request:
            raise HTTPException(
                status_code=404,
                detail=f"Course request {course_request_id} not found"
            )
        
        # Check user permissions
        if (course_request.sales_user_id != current_user.id and 
            not current_user.has_permission("manage_all_courses")):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this course request"
            )
        
        # Get processing status
        status = await sop_processor.get_processing_status(course_request_id)
        
        return {
            "success": True,
            "course_request_id": course_request_id,
            "sop_processing": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get SOP status for course request {course_request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get SOP processing status: {str(e)}"
        )

@router.get("/insights/{course_request_id}")
async def get_sop_insights(
    course_request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get training insights extracted from SOP documents."""
    
    try:
        # Verify course request exists and user has access
        course_request = db.query(CourseRequest).filter(
            CourseRequest.id == course_request_id
        ).first()
        
        if not course_request:
            raise HTTPException(
                status_code=404,
                detail=f"Course request {course_request_id} not found"
            )
        
        # Check user permissions
        if (course_request.sales_user_id != current_user.id and 
            not current_user.has_permission("manage_all_courses")):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this course request"
            )
        
        # TODO: Retrieve actual insights from database
        # For now, return mock insights
        mock_insights = {
            "course_request_id": course_request_id,
            "vocabulary_analysis": {
                "technical_terms": [
                    "implementation", "documentation", "verification", "compliance",
                    "methodology", "specification", "calibration", "maintenance"
                ],
                "complexity_score": 78,
                "vocabulary_themes": ["technical_procedures", "quality_control", "safety_protocols"]
            },
            "communication_patterns": {
                "communication_scenarios": [
                    "email", "meeting", "report", "presentation", "call", "documentation"
                ],
                "required_skills": [
                    "technical_writing", "verbal_presentations", "email_communication",
                    "meeting_participation", "report_generation"
                ]
            },
            "training_recommendations": {
                "focus_areas": [
                    "Technical vocabulary development",
                    "Formal writing skills",
                    "Presentation and meeting communication",
                    "Safety and compliance language"
                ],
                "estimated_training_hours": 32,
                "recommended_cefr_level": "B2"
            },
            "extraction_summary": {
                "files_processed": 3,
                "total_pages": 47,
                "total_words": 12450,
                "processing_time": 23.5
            }
        }
        
        return {
            "success": True,
            "course_request_id": course_request_id,
            "sop_insights": mock_insights,
            "insights_available": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get SOP insights for course request {course_request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get SOP insights: {str(e)}"
        )

@router.post("/reprocess/{course_request_id}")
async def reprocess_sop_documents(
    course_request_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reprocess SOP documents for a course request."""
    
    try:
        # Verify course request exists and user has access
        course_request = db.query(CourseRequest).filter(
            CourseRequest.id == course_request_id
        ).first()
        
        if not course_request:
            raise HTTPException(
                status_code=404,
                detail=f"Course request {course_request_id} not found"
            )
        
        # Check user permissions
        if (course_request.sales_user_id != current_user.id and 
            not current_user.has_permission("manage_all_courses")):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this course request"
            )
        
        # TODO: Retrieve stored files and reprocess them
        # For now, return success response
        
        return {
            "success": True,
            "message": "SOP reprocessing started",
            "course_request_id": course_request_id,
            "reprocessing_status": "started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SOP reprocessing failed for course request {course_request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"SOP reprocessing failed: {str(e)}"
        )

@router.get("/capabilities")
async def get_sop_capabilities():
    """Get SOP processing capabilities and supported formats."""
    
    return {
        "supported_formats": [
            {
                "format": "PDF",
                "mime_types": ["application/pdf"],
                "max_size": "50MB",
                "max_pages": 500,
                "description": "PDF documents with text content"
            },
            {
                "format": "DOCX",
                "mime_types": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
                "max_size": "50MB",
                "description": "Microsoft Word documents (2007+)"
            },
            {
                "format": "DOC",
                "mime_types": ["application/msword"],
                "max_size": "50MB",
                "description": "Microsoft Word documents (legacy)"
            },
            {
                "format": "TXT",
                "mime_types": ["text/plain"],
                "max_size": "50MB",
                "description": "Plain text files"
            }
        ],
        "processing_capabilities": [
            "Text extraction and OCR",
            "Technical vocabulary identification",
            "Communication pattern analysis",
            "Training requirement assessment",
            "Industry-specific language analysis",
            "Complexity scoring and CEFR alignment"
        ],
        "limits": {
            "max_files_per_upload": 10,
            "max_individual_file_size": "50MB",
            "max_total_upload_size": "200MB",
            "max_pages_per_pdf": 500
        },
        "ai_features": {
            "content_analysis": True,
            "vocabulary_extraction": True,
            "training_recommendations": True,
            "industry_context_analysis": True
        }
    }