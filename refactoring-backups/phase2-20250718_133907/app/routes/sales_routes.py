from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import tempfile

from app.database import get_db
from app.middleware.auth_middleware import require_auth, require_roles
from app.services.sales_service import SalesService, SOPService, ClientFeedbackService, SalesAnalyticsService
from app.services.auth_service import AuthService
from app.schemas.sales import (
    CourseRequestCreateRequest,
    CourseRequestUpdateRequest,
    CourseRequestWizardRequest,
    CourseRequestResponse,
    CourseRequestDetailResponse,
    SOPDocumentResponse,
    SOPUploadResponse,
    ClientFeedbackCreateRequest,
    ClientFeedbackResponse,
    SalesDashboardStats
)

router = APIRouter(prefix="/api/sales", tags=["sales"])
security = HTTPBearer()

# Course Request Management
@router.get("/course-requests", response_model=List[CourseRequestResponse])
async def get_course_requests(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get course requests with optional filtering"""
    try:
        current_user = AuthService.get_current_user(db, token.credentials)
        
        # Sales users can only see their own requests, admins see all
        sales_user_id = current_user.id if not current_user.has_role("admin") else None
        
        requests = SalesService.get_course_requests(
            db=db,
            sales_user_id=sales_user_id,
            status=status,
            priority=priority,
            skip=skip,
            limit=limit
        )
        
        return requests
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/course-requests", response_model=CourseRequestResponse, status_code=201)
async def create_course_request(
    request: CourseRequestCreateRequest,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a new course request"""
    try:
        current_user = AuthService.get_current_user(db, token.credentials)
        
        course_request = SalesService.create_course_request(
            db=db,
            request_data=request,
            sales_user_id=current_user.id
        )
        
        return course_request
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/course-requests/wizard", response_model=CourseRequestResponse)
async def create_course_request_from_wizard(
    request: CourseRequestWizardRequest,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a new course request from the comprehensive wizard"""
    try:
        current_user = AuthService.get_current_user(db, token.credentials)
        
        # Convert wizard request to database format
        course_request_data = {
            # Client Information
            "company_name": request.company_name,
            "industry": request.industry,
            "company_size": request.company_size,
            "location": request.location,
            "website": request.website,
            
            # Contact Information
            "contact_person": request.contact_person,
            "contact_email": request.contact_email,
            "contact_phone": request.contact_phone,
            "decision_maker": request.decision_maker,
            "decision_maker_role": request.decision_maker_role,
            
            # Project Information
            "project_title": request.project_title,
            "project_description": request.project_description,
            "estimated_budget": request.estimated_budget,
            "timeline": request.timeline,
            "urgency": request.urgency,
            "has_existing_training": request.has_existing_training,
            "existing_training_description": request.existing_training_description,
            
            # Training Requirements
            "participant_count": request.participant_count,
            "current_english_level": request.current_english_level,
            "target_english_level": request.target_english_level,
            "target_roles": request.target_roles,
            "communication_scenarios": request.communication_scenarios,
            "training_goals": request.training_goals,
            "specific_challenges": request.specific_challenges,
            "success_metrics": request.success_metrics,
            
            # Map to legacy fields for backwards compatibility
            "cohort_size": request.participant_count,
            "current_cefr": request.current_english_level,
            "target_cefr": request.target_english_level,
            "training_objectives": request.training_goals,
            "pain_points": request.specific_challenges,
            
            # Set defaults
            "priority": "medium",  # Map urgency to priority
            "status": "submitted",  # Wizard submissions are automatically submitted
        }
        
        course_request = SalesService.create_course_request_from_wizard(
            db=db,
            request_data=course_request_data,
            sales_user_id=current_user.id
        )
        
        return course_request
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/course-requests/{request_id}", response_model=CourseRequestDetailResponse)
async def get_course_request(
    request_id: int,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get a specific course request"""
    try:
        current_user = AuthService.get_current_user(db, token.credentials)
        
        course_request = SalesService.get_course_request_by_id(db, request_id)
        if not course_request:
            raise HTTPException(status_code=404, detail="Course request not found")
        
        # Check permissions
        if not current_user.has_role("admin") and course_request.sales_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Add additional details
        response_data = CourseRequestDetailResponse.from_orm(course_request)
        response_data.sales_user_name = f"{course_request.sales_user.first_name or ''} {course_request.sales_user.last_name or ''}".strip()
        
        if course_request.generated_course:
            response_data.generated_course_id = course_request.generated_course.id
            response_data.generated_course_title = course_request.generated_course.title
        
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/course-requests/{request_id}", response_model=CourseRequestResponse)
async def update_course_request(
    request_id: int,
    request: CourseRequestUpdateRequest,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Update a course request"""
    try:
        current_user = AuthService.get_current_user(db, token.credentials)
        
        # Check if request exists and user has permission
        existing_request = SalesService.get_course_request_by_id(db, request_id)
        if not existing_request:
            raise HTTPException(status_code=404, detail="Course request not found")
        
        if not current_user.has_role("admin") and existing_request.sales_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Only allow updates if request is in draft status
        if existing_request.status.value != "draft":
            raise HTTPException(status_code=400, detail="Can only update draft requests")
        
        updated_request = SalesService.update_course_request(
            db=db,
            request_id=request_id,
            update_data=request
        )
        
        if not updated_request:
            raise HTTPException(status_code=404, detail="Failed to update request")
        
        return updated_request
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/course-requests/{request_id}/submit")
async def submit_course_request(
    request_id: int,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Submit a course request for processing"""
    try:
        current_user = AuthService.get_current_user(db, token.credentials)
        
        # Check permissions
        course_request = SalesService.get_course_request_by_id(db, request_id)
        if not course_request:
            raise HTTPException(status_code=404, detail="Course request not found")
        
        if not current_user.has_role("admin") and course_request.sales_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = SalesService.submit_course_request(db, request_id)
        if not success:
            raise HTTPException(status_code=400, detail="Cannot submit request in current status")
        
        return {"message": "Course request submitted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/course-requests/{request_id}")
async def delete_course_request(
    request_id: int,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Delete a course request (only if in draft status)"""
    try:
        current_user = AuthService.get_current_user(db, token.credentials)
        
        # Check permissions
        course_request = SalesService.get_course_request_by_id(db, request_id)
        if not course_request:
            raise HTTPException(status_code=404, detail="Course request not found")
        
        if not current_user.has_role("admin") and course_request.sales_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = SalesService.delete_course_request(db, request_id)
        if not success:
            raise HTTPException(status_code=400, detail="Cannot delete request in current status")
        
        return {"message": "Course request deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# SOP Document Management
@router.post("/course-requests/{request_id}/sop", response_model=SOPUploadResponse)
async def upload_sop_document(
    request_id: int,
    file: UploadFile = File(...),
    upload_notes: Optional[str] = Form(None),
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Upload an SOP document for a course request"""
    try:
        current_user = AuthService.get_current_user(db, token.credentials)
        
        # Check if request exists and user has permission
        course_request = SalesService.get_course_request_by_id(db, request_id)
        if not course_request:
            raise HTTPException(status_code=404, detail="Course request not found")
        
        if not current_user.has_role("admin") and course_request.sales_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Enhanced file validation
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
            
        if not SOPService.allowed_file(file.filename):
            allowed_extensions = ', '.join(SOPService.ALLOWED_EXTENSIONS)
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Supported formats: {allowed_extensions}"
            )
        
        if file.size and file.size > SOPService.MAX_FILE_SIZE:
            max_size_mb = SOPService.MAX_FILE_SIZE // (1024 * 1024)
            raise HTTPException(
                status_code=400, 
                detail=f"File size too large. Maximum allowed: {max_size_mb}MB"
            )
        
        # Check for potentially dangerous file names
        if '..' in file.filename or '/' in file.filename or '\\' in file.filename:
            raise HTTPException(status_code=400, detail="Invalid file name")
        
        # Generate unique filename
        unique_filename = SOPService.generate_unique_filename(file.filename)
        
        # Save file temporarily and upload to S3 (simplified for demo)
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                content = await file.read()
                
                # Validate file content isn't empty
                if len(content) == 0:
                    raise HTTPException(status_code=400, detail="File is empty")
                
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # In production, upload to S3 here
            s3_key = f"sop-documents/{request_id}/{unique_filename}"
            
            # Create SOP document record
            sop_doc = SOPService.create_sop_document(
                db=db,
                request_id=request_id,
                filename=unique_filename,
                original_filename=file.filename,
                s3_key=s3_key,
                content_type=file.content_type or "application/octet-stream",
                file_size=len(content),
                upload_notes=upload_notes
            )
            
            return SOPUploadResponse(
                id=sop_doc.id,
                filename=sop_doc.filename,
                file_size=sop_doc.file_size,
                processing_status=sop_doc.processing_status,
                message="SOP document uploaded successfully"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            # Log the error for debugging
            print(f"Error during SOP upload: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to process uploaded file. Please try again."
            )
        finally:
            # Clean up temp file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    print(f"Warning: Failed to clean up temp file {temp_file_path}: {e}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/course-requests/{request_id}/sop", response_model=List[SOPDocumentResponse])
async def get_sop_documents(
    request_id: int,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get all SOP documents for a course request"""
    try:
        current_user = AuthService.get_current_user(db, token.credentials)
        
        # Check permissions
        course_request = SalesService.get_course_request_by_id(db, request_id)
        if not course_request:
            raise HTTPException(status_code=404, detail="Course request not found")
        
        if not current_user.has_role("admin") and course_request.sales_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        sop_documents = SOPService.get_sop_documents_by_request(db, request_id)
        return sop_documents
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/course-requests/{request_id}/sop/{sop_id}")
async def delete_sop_document(
    request_id: int,
    sop_id: int,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Delete an SOP document"""
    try:
        current_user = AuthService.get_current_user(db, token.credentials)
        
        # Check permissions
        course_request = SalesService.get_course_request_by_id(db, request_id)
        if not course_request:
            raise HTTPException(status_code=404, detail="Course request not found")
        
        if not current_user.has_role("admin") and course_request.sales_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if SOP document exists and belongs to the request
        sop_doc = SOPService.get_sop_document_by_id(db, sop_id)
        if not sop_doc or sop_doc.request_id != request_id:
            raise HTTPException(status_code=404, detail="SOP document not found")
        
        success = SOPService.delete_sop_document(db, sop_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete SOP document")
        
        return {"message": "SOP document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Client Feedback Management
@router.post("/course-requests/{request_id}/feedback", response_model=ClientFeedbackResponse)
async def create_client_feedback(
    request_id: int,
    feedback: ClientFeedbackCreateRequest,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create client feedback for a course request"""
    try:
        current_user = AuthService.get_current_user(db, token.credentials)
        
        # Check if request exists
        course_request = SalesService.get_course_request_by_id(db, request_id)
        if not course_request:
            raise HTTPException(status_code=404, detail="Course request not found")
        
        if not current_user.has_role("admin") and course_request.sales_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        client_feedback = ClientFeedbackService.create_feedback(
            db=db,
            request_id=request_id,
            feedback_data=feedback
        )
        
        return client_feedback
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/course-requests/{request_id}/feedback", response_model=List[ClientFeedbackResponse])
async def get_client_feedback(
    request_id: int,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get all client feedback for a course request"""
    try:
        current_user = AuthService.get_current_user(db, token.credentials)
        
        # Check permissions
        course_request = SalesService.get_course_request_by_id(db, request_id)
        if not course_request:
            raise HTTPException(status_code=404, detail="Course request not found")
        
        if not current_user.has_role("admin") and course_request.sales_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        feedback_list = ClientFeedbackService.get_feedback_by_request(db, request_id)
        return feedback_list
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics and Dashboard
@router.get("/dashboard-stats", response_model=SalesDashboardStats)
async def get_dashboard_stats(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get sales dashboard statistics"""
    try:
        current_user = AuthService.get_current_user(db, token.credentials)
        
        # Sales users see only their stats, admins see all
        sales_user_id = current_user.id if not current_user.has_role("admin") else None
        
        stats = SalesAnalyticsService.get_dashboard_stats(db, sales_user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/top-performers")
async def get_top_performers(
    limit: int = Query(10, ge=1, le=50),
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get top performing sales users (admin only)"""
    try:
        top_performers = SalesAnalyticsService.get_top_performing_sales_users(db, limit)
        return {"top_performers": top_performers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 