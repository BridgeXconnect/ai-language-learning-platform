from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os
import uuid
from werkzeug.utils import secure_filename

from app.models.sales import CourseRequest, SOPDocument, ClientFeedback, RequestStatus, Priority
from app.models.user import User
from app.models.course import Course
from app.schemas.sales import (
    CourseRequestCreateRequest, 
    CourseRequestUpdateRequest,
    ClientFeedbackCreateRequest,
    SalesDashboardStats
)
import aiohttp
import asyncio

class SalesService:
    
    @staticmethod
    def create_course_request(
        db: Session,
        request_data: CourseRequestCreateRequest,
        sales_user_id: int
    ) -> CourseRequest:
        """Create a new course request"""
        try:
            data = request_data.model_dump()
            # Convert Enum values to .name for SQLAlchemy Enum fields
            for key in ["delivery_method", "priority", "current_cefr", "target_cefr"]:
                if key in data and hasattr(data[key], "name"):
                    data[key] = data[key].name
            
            # Map fields for database compatibility
            if "current_cefr" in data:
                data["current_english_level"] = data["current_cefr"]
            if "target_cefr" in data:
                data["target_english_level"] = data["target_cefr"]
            if "training_objectives" in data:
                data["training_goals"] = data["training_objectives"]
            if "cohort_size" in data:
                data["participant_count"] = data["cohort_size"]
            if "pain_points" in data:
                data["specific_challenges"] = data["pain_points"]
            
            # Set required fields with defaults if not provided
            if "project_title" not in data or not data["project_title"]:
                data["project_title"] = f"Training Request for {data.get('company_name', 'Unknown Company')}"
            if "project_description" not in data or not data["project_description"]:
                data["project_description"] = data.get("training_objectives", "Language training program")
            
            db_request = CourseRequest(
                sales_user_id=sales_user_id,
                **data
            )
            db.add(db_request)
            db.commit()
            db.refresh(db_request)
            return db_request
        except Exception as e:
            print('ERROR in create_course_request:', str(e))
            raise
    
    @staticmethod
    def create_course_request_from_wizard(
        db: Session,
        request_data: Dict[str, Any],
        sales_user_id: int
    ) -> CourseRequest:
        """Create a new course request from comprehensive wizard data"""
        # Create course request with wizard data
        db_request = CourseRequest(
            sales_user_id=sales_user_id,
            **request_data
        )
        
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        return db_request
    
    @staticmethod
    def get_course_request_by_id(db: Session, request_id: int) -> Optional[CourseRequest]:
        """Get a course request by ID"""
        return db.query(CourseRequest).filter(CourseRequest.id == request_id).first()
    
    @staticmethod
    def get_course_requests(
        db: Session,
        sales_user_id: Optional[int] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CourseRequest]:
        """Get course requests with optional filtering"""
        query = db.query(CourseRequest)
        
        if sales_user_id:
            query = query.filter(CourseRequest.sales_user_id == sales_user_id)
        
        if status:
            query = query.filter(CourseRequest.status == status)
            
        if priority:
            query = query.filter(CourseRequest.priority == priority)
        
        return query.order_by(desc(CourseRequest.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_course_request(
        db: Session,
        request_id: int,
        update_data: CourseRequestUpdateRequest
    ) -> Optional[CourseRequest]:
        """Update a course request"""
        db_request = db.query(CourseRequest).filter(CourseRequest.id == request_id).first()
        
        if not db_request:
            return None
        
        # Only update fields that are provided
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_request, field, value)
        
        db_request.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_request)
        return db_request
    
    @staticmethod
    def submit_course_request(db: Session, request_id: int) -> bool:
        """Submit a course request for processing"""
        db_request = db.query(CourseRequest).filter(CourseRequest.id == request_id).first()
        
        if not db_request or db_request.status != RequestStatus.DRAFT:
            return False
        
        db_request.status = RequestStatus.SUBMITTED
        db_request.submitted_at = datetime.utcnow()
        db_request.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Trigger agent orchestration asynchronously
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(SalesService._trigger_agent_orchestration(db_request))
        except RuntimeError:
            # No event loop, create a new one (for testing)
            asyncio.run(SalesService._trigger_agent_orchestration(db_request))
        
        return True
    
    @staticmethod
    async def _trigger_agent_orchestration(course_request: CourseRequest):
        """Trigger the agent orchestration workflow for a submitted course request"""
        try:
            orchestrator_url = "http://localhost:8100/orchestrate-course"
            
            # Prepare the course request data for the orchestrator
            orchestration_data = {
                "course_request_id": course_request.id,
                "company_name": course_request.company_name,
                "industry": course_request.industry or "General",
                "training_goals": course_request.training_goals,
                "current_english_level": course_request.current_english_level,
                "duration_weeks": 8,  # Default duration
                "target_audience": f"{course_request.participant_count} participants",
                "specific_needs": course_request.specific_challenges or course_request.specific_requirements
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(orchestrator_url, json=orchestration_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Agent orchestration triggered for request #{course_request.id}")
                        print(f"Workflow result: {result.get('success', False)}")
                        return True
                    else:
                        print(f"❌ Failed to trigger agent orchestration: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error triggering agent orchestration: {e}")
            return False
    
    @staticmethod
    def delete_course_request(db: Session, request_id: int) -> bool:
        """Delete a course request (only if in draft status)"""
        db_request = db.query(CourseRequest).filter(CourseRequest.id == request_id).first()
        
        if not db_request or db_request.status != RequestStatus.DRAFT:
            return False
        
        db.delete(db_request)
        db.commit()
        return True

class SOPService:
    
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'xlsx', 'xls'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in SOPService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """Generate a unique filename while preserving extension"""
        name, ext = os.path.splitext(secure_filename(original_filename))
        unique_name = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        return unique_name
    
    @staticmethod
    def create_sop_document(
        db: Session,
        request_id: int,
        filename: str,
        original_filename: str,
        s3_key: str,
        content_type: str,
        file_size: int,
        upload_notes: Optional[str] = None
    ) -> SOPDocument:
        """Create a new SOP document record"""
        sop_doc = SOPDocument(
            request_id=request_id,
            filename=filename,
            original_filename=original_filename,
            s3_key=s3_key,
            content_type=content_type,
            file_size=file_size,
            upload_notes=upload_notes,
            processing_status="pending"
        )
        
        db.add(sop_doc)
        db.commit()
        db.refresh(sop_doc)
        return sop_doc
    
    @staticmethod
    def get_sop_documents_by_request(db: Session, request_id: int) -> List[SOPDocument]:
        """Get all SOP documents for a request"""
        return db.query(SOPDocument).filter(SOPDocument.request_id == request_id).all()
    
    @staticmethod
    def get_sop_document_by_id(db: Session, sop_id: int) -> Optional[SOPDocument]:
        """Get a specific SOP document"""
        return db.query(SOPDocument).filter(SOPDocument.id == sop_id).first()
    
    @staticmethod
    def update_sop_processing_status(
        db: Session,
        sop_id: int,
        status: str,
        vector_db_id: Optional[str] = None,
        extracted_text_preview: Optional[str] = None,
        processing_error: Optional[str] = None
    ) -> bool:
        """Update SOP document processing status"""
        sop_doc = db.query(SOPDocument).filter(SOPDocument.id == sop_id).first()
        
        if not sop_doc:
            return False
        
        sop_doc.processing_status = status
        if vector_db_id:
            sop_doc.vector_db_id = vector_db_id
        if extracted_text_preview:
            sop_doc.extracted_text_preview = extracted_text_preview
        if processing_error:
            sop_doc.processing_error = processing_error
        
        if status in ["completed", "failed"]:
            sop_doc.processed_at = datetime.utcnow()
        
        db.commit()
        return True
    
    @staticmethod
    def delete_sop_document(db: Session, sop_id: int) -> bool:
        """Delete an SOP document"""
        sop_doc = db.query(SOPDocument).filter(SOPDocument.id == sop_id).first()
        
        if not sop_doc:
            return False
        
        db.delete(sop_doc)
        db.commit()
        return True

class ClientFeedbackService:
    
    @staticmethod
    def create_feedback(
        db: Session,
        request_id: int,
        feedback_data: ClientFeedbackCreateRequest
    ) -> ClientFeedback:
        """Create new client feedback"""
        feedback = ClientFeedback(
            request_id=request_id,
            **feedback_data.dict()
        )
        
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback
    
    @staticmethod
    def get_feedback_by_request(db: Session, request_id: int) -> List[ClientFeedback]:
        """Get all feedback for a request"""
        return db.query(ClientFeedback).filter(
            ClientFeedback.request_id == request_id
        ).order_by(desc(ClientFeedback.created_at)).all()
    
    @staticmethod
    def address_feedback(
        db: Session,
        feedback_id: int,
        response_notes: str
    ) -> bool:
        """Mark feedback as addressed"""
        feedback = db.query(ClientFeedback).filter(ClientFeedback.id == feedback_id).first()
        
        if not feedback:
            return False
        
        feedback.is_addressed = True
        feedback.response_notes = response_notes
        feedback.addressed_at = datetime.utcnow()
        
        db.commit()
        return True

class SalesAnalyticsService:
    
    @staticmethod
    def get_dashboard_stats(db: Session, sales_user_id: Optional[int] = None) -> SalesDashboardStats:
        """Get sales dashboard statistics"""
        base_query = db.query(CourseRequest)
        
        if sales_user_id:
            base_query = base_query.filter(CourseRequest.sales_user_id == sales_user_id)
        
        # Basic counts
        total_requests = base_query.count()
        active_requests = base_query.filter(
            CourseRequest.status.in_([RequestStatus.SUBMITTED, RequestStatus.IN_PROGRESS])
        ).count()
        completed_requests = base_query.filter(
            CourseRequest.status == RequestStatus.COMPLETED
        ).count()
        pending_review = base_query.filter(
            CourseRequest.status == RequestStatus.SUBMITTED
        ).count()
        
        # This month's requests
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        requests_this_month = base_query.filter(
            CourseRequest.created_at >= start_of_month
        ).count()
        
        # Conversion rate (completed / total)
        conversion_rate = (completed_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Average processing time
        completed_with_times = base_query.filter(
            and_(
                CourseRequest.status == RequestStatus.COMPLETED,
                CourseRequest.submitted_at.isnot(None)
            )
        ).all()
        
        if completed_with_times:
            total_days = sum([
                (req.updated_at - req.submitted_at).days 
                for req in completed_with_times
            ])
            avg_processing_time_days = total_days / len(completed_with_times)
        else:
            avg_processing_time_days = 0
        
        # Priority breakdown
        priority_breakdown = {}
        for priority in Priority:
            count = base_query.filter(CourseRequest.priority == priority).count()
            priority_breakdown[priority.value] = count
        
        # Status breakdown
        status_breakdown = {}
        for status in RequestStatus:
            count = base_query.filter(CourseRequest.status == status).count()
            status_breakdown[status.value] = count
        
        return SalesDashboardStats(
            total_requests=total_requests,
            active_requests=active_requests,
            completed_requests=completed_requests,
            pending_review=pending_review,
            requests_this_month=requests_this_month,
            conversion_rate=round(conversion_rate, 2),
            avg_processing_time_days=round(avg_processing_time_days, 1),
            priority_breakdown=priority_breakdown,
            status_breakdown=status_breakdown
        )
    
    @staticmethod
    def get_requests_by_date_range(
        db: Session,
        start_date: datetime,
        end_date: datetime,
        sales_user_id: Optional[int] = None
    ) -> List[CourseRequest]:
        """Get requests within a date range"""
        query = db.query(CourseRequest).filter(
            and_(
                CourseRequest.created_at >= start_date,
                CourseRequest.created_at <= end_date
            )
        )
        
        if sales_user_id:
            query = query.filter(CourseRequest.sales_user_id == sales_user_id)
        
        return query.order_by(desc(CourseRequest.created_at)).all()
    
    @staticmethod
    def get_top_performing_sales_users(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing sales users by completed requests"""
        results = db.query(
            User.id,
            User.username,
            User.first_name,
            User.last_name,
            func.count(CourseRequest.id).label('completed_count')
        ).join(
            CourseRequest, User.id == CourseRequest.sales_user_id
        ).filter(
            CourseRequest.status == RequestStatus.COMPLETED
        ).group_by(
            User.id, User.username, User.first_name, User.last_name
        ).order_by(
            desc('completed_count')
        ).limit(limit).all()
        
        return [
            {
                'user_id': result.id,
                'username': result.username,
                'full_name': f"{result.first_name or ''} {result.last_name or ''}".strip(),
                'completed_requests': result.completed_count
            }
            for result in results
        ] 