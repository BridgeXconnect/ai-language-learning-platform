# server/app/routes/ai.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.ai_service import AIService
from ..services.file_service import FileService
from ..models import User, CourseRequest, Course
from .. import db
import logging

ai_bp = Blueprint('ai', __name__)
logger = logging.getLogger(__name__)

@ai_bp.route('/generate-course', methods=['POST'])
@jwt_required()
def generate_course():
    """Generate AI course content from a course request"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Check if user has permission (Course Manager or Admin)
        if user.role not in ['course_manager', 'admin']:
            return jsonify({'msg': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        request_id = data.get('request_id')
        
        if not request_id:
            return jsonify({'msg': 'Course request ID is required'}), 400
        
        course_request = CourseRequest.query.get(request_id)
        if not course_request:
            return jsonify({'msg': 'Course request not found'}), 404
        
        # Initialize AI service and generate course
        ai_service = AIService()
        result = ai_service.generate_course_from_request(course_request)
        
        if result['success']:
            return jsonify({
                'msg': 'Course generation initiated',
                'course_id': result['course_id'],
                'status': 'generating'
            }), 200
        else:
            return jsonify({
                'msg': 'Course generation failed',
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"Error in generate_course: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@ai_bp.route('/process-sop', methods=['POST'])
@jwt_required()
def process_sop():
    """Process uploaded SOP documents"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.role not in ['sales', 'course_manager', 'admin']:
            return jsonify({'msg': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        file_path = data.get('file_path')
        request_id = data.get('request_id')
        
        if not file_path or not request_id:
            return jsonify({'msg': 'File path and request ID are required'}), 400
        
        # Process SOP using AI service
        ai_service = AIService()
        result = ai_service.process_sop_document(file_path, request_id)
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        logger.error(f"Error in process_sop: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@ai_bp.route('/review-content', methods=['POST'])
@jwt_required()
def review_content():
    """Submit AI content for review and revision"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.role not in ['course_manager', 'admin']:
            return jsonify({'msg': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        course_id = data.get('course_id')
        feedback = data.get('feedback')
        action = data.get('action')  # 'approve', 'request_revision', 'reject'
        
        if not course_id or not action:
            return jsonify({'msg': 'Course ID and action are required'}), 400
        
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'msg': 'Course not found'}), 404
        
        ai_service = AIService()
        result = ai_service.process_review_feedback(course, action, feedback)
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        logger.error(f"Error in review_content: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

# server/app/routes/common.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Course, CourseRequest, Student, Trainer
from .. import db
from sqlalchemy import or_
import logging

common_bp = Blueprint('common', __name__)
logger = logging.getLogger(__name__)

@common_bp.route('/search', methods=['GET'])
@jwt_required()
def search():
    """Universal search endpoint"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        query = request.args.get('q', '')
        entity_type = request.args.get('type', 'all')  # 'courses', 'users', 'requests', 'all'
        limit = min(int(request.args.get('limit', 10)), 50)
        
        results = {}
        
        if entity_type in ['courses', 'all'] and user.role in ['course_manager', 'trainer', 'admin']:
            courses = Course.query.filter(
                or_(
                    Course.title.ilike(f'%{query}%'),
                    Course.description.ilike(f'%{query}%')
                )
            ).limit(limit).all()
            results['courses'] = [{'id': c.id, 'title': c.title, 'description': c.description} for c in courses]
        
        if entity_type in ['requests', 'all'] and user.role in ['sales', 'course_manager', 'admin']:
            requests = CourseRequest.query.filter(
                or_(
                    CourseRequest.company_name.ilike(f'%{query}%'),
                    CourseRequest.training_objectives.ilike(f'%{query}%')
                )
            ).limit(limit).all()
            results['requests'] = [{'id': r.id, 'company_name': r.company_name, 'status': r.status} for r in requests]
        
        if entity_type in ['users', 'all'] and user.role in ['course_manager', 'admin']:
            users = User.query.filter(
                or_(
                    User.username.ilike(f'%{query}%'),
                    User.email.ilike(f'%{query}%')
                )
            ).limit(limit).all()
            results['users'] = [{'id': u.id, 'username': u.username, 'email': u.email, 'role': u.role} for u in users]
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        return jsonify({'msg': 'Search failed'}), 500

@common_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user notifications"""
    try:
        current_user_id = get_jwt_identity()
        # This would integrate with a notification service
        # For now, return empty array
        return jsonify({'notifications': []}), 200
        
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        return jsonify({'msg': 'Failed to get notifications'}), 500

@common_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ai-lang-app-backend',
        'version': '1.0.0'
    }), 200

# server/app/services/__init__.py
# Services package initialization

# server/app/services/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.username = os.getenv('SMTP_USERNAME')
        self.password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.username)
    
    def send_email(self, to_emails: List[str], subject: str, body: str, 
                   html_body: Optional[str] = None, attachments: Optional[List[str]] = None) -> bool:
        """Send email to recipients"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.isfile(file_path):
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_welcome_email(self, user_email: str, username: str, temporary_password: str = None) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to AI Language Learning Platform"
        
        body = f"""
        Hello {username},
        
        Welcome to the AI Language Learning Platform!
        
        Your account has been created successfully. You can now log in using your email address.
        
        {"Temporary password: " + temporary_password if temporary_password else ""}
        
        Best regards,
        AI Language Learning Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Welcome to AI Language Learning Platform</h2>
            <p>Hello {username},</p>
            <p>Welcome to the AI Language Learning Platform!</p>
            <p>Your account has been created successfully. You can now log in using your email address.</p>
            {"<p><strong>Temporary password:</strong> " + temporary_password + "</p>" if temporary_password else ""}
            <p>Best regards,<br>AI Language Learning Team</p>
        </body>
        </html>
        """
        
        return self.send_email([user_email], subject, body, html_body)
    
    def send_password_reset_email(self, user_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
        
        subject = "Password Reset Request"
        
        body = f"""
        Hello,
        
        You have requested a password reset for your AI Language Learning Platform account.
        
        Please click the following link to reset your password:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request this password reset, please ignore this email.
        
        Best regards,
        AI Language Learning Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hello,</p>
            <p>You have requested a password reset for your AI Language Learning Platform account.</p>
            <p><a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this password reset, please ignore this email.</p>
            <p>Best regards,<br>AI Language Learning Team</p>
        </body>
        </html>
        """
        
        return self.send_email([user_email], subject, body, html_body)
    
    def send_course_notification(self, user_email: str, course_title: str, status: str) -> bool:
        """Send course status notification"""
        subject = f"Course Update: {course_title}"
        
        status_messages = {
            'approved': 'Your course has been approved and is ready for delivery!',
            'rejected': 'Your course request requires revision. Please contact your course manager.',
            'generated': 'Your course has been generated and is awaiting review.',
            'assigned': 'You have been assigned to a new course.'
        }
        
        message = status_messages.get(status, f'Course status updated to: {status}')
        
        body = f"""
        Hello,
        
        Course: {course_title}
        Status Update: {message}
        
        Please log in to your dashboard for more details.
        
        Best regards,
        AI Language Learning Team
        """
        
        return self.send_email([user_email], subject, body)

# server/app/services/file_service.py
import os
import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
import uuid
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import mimetypes

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'ai-lang-app-sops')
        self.upload_folder = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
        
        # Ensure upload folder exists
        os.makedirs(self.upload_folder, exist_ok=True)
        
        # Allowed file extensions
        self.allowed_extensions = {
            'pdf', 'docx', 'doc', 'txt', 'xlsx', 'xls', 'pptx', 'ppt'
        }
        
        # Max file size (50MB)
        self.max_file_size = 50 * 1024 * 1024
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def generate_unique_filename(self, filename: str) -> str:
        """Generate unique filename while preserving extension"""
        name, ext = os.path.splitext(secure_filename(filename))
        unique_name = f"{name}_{uuid.uuid4().hex}{ext}"
        return unique_name
    
    def upload_to_s3(self, local_file_path: str, s3_key: str) -> bool:
        """Upload file to S3"""
        try:
            # Determine content type
            content_type, _ = mimetypes.guess_type(local_file_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            self.s3_client.upload_file(
                local_file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ServerSideEncryption': 'AES256'
                }
            )
            logger.info(f"File uploaded to S3: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            return False
    
    def download_from_s3(self, s3_key: str, local_file_path: str) -> bool:
        """Download file from S3"""
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_file_path)
            logger.info(f"File downloaded from S3: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to download from S3: {str(e)}")
            return False
    
    def delete_from_s3(self, s3_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"File deleted from S3: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete from S3: {str(e)}")
            return False
    
    def get_s3_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """Generate presigned URL for S3 object"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return None
    
    def save_uploaded_file(self, file, request_id: str) -> Dict[str, Any]:
        """Save uploaded file and return file info"""
        try:
            if not file or file.filename == '':
                return {'success': False, 'error': 'No file provided'}
            
            if not self.allowed_file(file.filename):
                return {'success': False, 'error': 'File type not allowed'}
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > self.max_file_size:
                return {'success': False, 'error': 'File too large (max 50MB)'}
            
            # Generate unique filename
            unique_filename = self.generate_unique_filename(file.filename)
            
            # Save locally first
            local_path = os.path.join(self.upload_folder, unique_filename)
            file.save(local_path)
            
            # Upload to S3
            s3_key = f"sops/{request_id}/{unique_filename}"
            upload_success = self.upload_to_s3(local_path, s3_key)
            
            if upload_success:
                # Clean up local file
                os.remove(local_path)
                
                return {
                    'success': True,
                    'filename': file.filename,
                    'unique_filename': unique_filename,
                    's3_key': s3_key,
                    'file_size': file_size,
                    'upload_date': datetime.utcnow().isoformat()
                }
            else:
                # Clean up local file on S3 failure
                if os.path.exists(local_path):
                    os.remove(local_path)
                return {'success': False, 'error': 'Failed to upload to cloud storage'}
            
        except Exception as e:
            logger.error(f"Error saving uploaded file: {str(e)}")
            return {'success': False, 'error': 'File upload failed'}
    
    def extract_text_from_file(self, s3_key: str) -> Dict[str, Any]:
        """Extract text content from uploaded file"""
        try:
            # Download file locally for processing
            local_path = os.path.join(self.upload_folder, f"temp_{uuid.uuid4().hex}")
            
            if not self.download_from_s3(s3_key, local_path):
                return {'success': False, 'error': 'Failed to download file'}
            
            # Extract text based on file type
            file_extension = s3_key.split('.')[-1].lower()
            
            extracted_text = ""
            
            if file_extension == 'txt':
                with open(local_path, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
            
            elif file_extension == 'pdf':
                # PDF extraction would require PyPDF2 or pdfplumber
                extracted_text = self._extract_pdf_text(local_path)
            
            elif file_extension in ['docx', 'doc']:
                # Word document extraction would require python-docx
                extracted_text = self._extract_docx_text(local_path)
            
            elif file_extension in ['xlsx', 'xls']:
                # Excel extraction would require openpyxl or pandas
                extracted_text = self._extract_excel_text(local_path)
            
            else:
                return {'success': False, 'error': f'Unsupported file type: {file_extension}'}
            
            # Clean up local file
            os.remove(local_path)
            
            return {
                'success': True,
                'text': extracted_text,
                'word_count': len(extracted_text.split()),
                'character_count': len(extracted_text)
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from file: {str(e)}")
            return {'success': False, 'error': 'Text extraction failed'}
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        # Placeholder - would implement with PyPDF2 or pdfplumber
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except ImportError:
            logger.warning("PyPDF2 not installed, PDF extraction not available")
            return "PDF text extraction not available"
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        # Placeholder - would implement with python-docx
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            logger.warning("python-docx not installed, DOCX extraction not available")
            return "DOCX text extraction not available"
    
    def _extract_excel_text(self, file_path: str) -> str:
        """Extract text from Excel file"""
        # Placeholder - would implement with openpyxl or pandas
        try:
            import pandas as pd
            df = pd.read_excel(file_path)
            return df.to_string()
        except ImportError:
            logger.warning("pandas not installed, Excel extraction not available")
            return "Excel text extraction not available"

# server/app/services/notification_service.py
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging
from ..models import User, Notification
from .. import db
from .email_service import EmailService

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.email_service = EmailService()
    
    def create_notification(self, user_id: int, title: str, message: str, 
                          notification_type: str = 'info', data: Optional[Dict] = None) -> bool:
        """Create a new notification for a user"""
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=notification_type,
                data=json.dumps(data) if data else None,
                created_at=datetime.utcnow()
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Send email notification if it's important
            if notification_type in ['urgent', 'course_approved', 'course_rejected']:
                self._send_email_notification(user_id, title, message)
            
            logger.info(f"Notification created for user {user_id}: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create notification: {str(e)}")
            db.session.rollback()
            return False
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False, 
                             limit: int = 50) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        try:
            query = Notification.query.filter(Notification.user_id == user_id)
            
            if unread_only:
                query = query.filter(Notification.read == False)
            
            notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
            
            return [
                {
                    'id': n.id,
                    'title': n.title,
                    'message': n.message,
                    'type': n.type,
                    'read': n.read,
                    'created_at': n.created_at.isoformat(),
                    'data': json.loads(n.data) if n.data else None
                }
                for n in notifications
            ]
            
        except Exception as e:
            logger.error(f"Failed to get notifications for user {user_id}: {str(e)}")
            return []
    
    def mark_notification_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        try:
            notification = Notification.query.filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ).first()
            
            if notification:
                notification.read = True
                notification.read_at = datetime.utcnow()
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {str(e)}")
            db.session.rollback()
            return False
    
    def mark_all_read(self, user_id: int) -> bool:
        """Mark all notifications as read for a user"""
        try:
            Notification.query.filter(
                Notification.user_id == user_id,
                Notification.read == False
            ).update({
                'read': True,
                'read_at': datetime.utcnow()
            })
            
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark all notifications as read: {str(e)}")
            db.session.rollback()
            return False
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification"""
        try:
            notification = Notification.query.filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ).first()
            
            if notification:
                db.session.delete(notification)
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete notification: {str(e)}")
            db.session.rollback()
            return False
    
    def _send_email_notification(self, user_id: int, title: str, message: str) -> None:
        """Send email notification to user"""
        try:
            user = User.query.get(user_id)
            if user and user.email:
                self.email_service.send_email(
                    [user.email],
                    f"AI Language Learning Platform - {title}",
                    message
                )
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
    
    def notify_course_status_change(self, course_id: int, status: str, message: str = None) -> None:
        """Notify relevant users about course status changes"""
        try:
            from ..models import Course, CourseRequest
            
            course = Course.query.get(course_id)
            if not course:
                return
            
            course_request = CourseRequest.query.get(course.request_id)
            if not course_request:
                return
            
            # Notify the sales person who created the request
            if course_request.created_by:
                title = f"Course Status Update: {course.title}"
                default_message = f"Course '{course.title}' status changed to {status}"
                
                self.create_notification(
                    course_request.created_by,
                    title,
                    message or default_message,
                    'course_update',
                    {'course_id': course_id, 'status': status}
                )
            
            # Notify course managers
            course_managers = User.query.filter(User.role == 'course_manager').all()
            for manager in course_managers:
                self.create_notification(
                    manager.id,
                    f"Course Review: {course.title}",
                    message or f"Course '{course.title}' requires attention",
                    'course_review',
                    {'course_id': course_id, 'status': status}
                )
                
        except Exception as e:
            logger.error(f"Failed to notify course status change: {str(e)}")
    
    def notify_new_course_request(self, request_id: int) -> None:
        """Notify course managers about new course requests"""
        try:
            from ..models import CourseRequest
            
            course_request = CourseRequest.query.get(request_id)
            if not course_request:
                return
            
            # Notify all course managers
            course_managers = User.query.filter(User.role == 'course_manager').all()
            
            for manager in course_managers:
                self.create_notification(
                    manager.id,
                    "New Course Request",
                    f"New course request from {course_request.company_name}",
                    'new_request',
                    {'request_id': request_id, 'company': course_request.company_name}
                )
                
        except Exception as e:
            logger.error(f"Failed to notify new course request: {str(e)}")

# server/app/services/ai_service.py
import openai
import anthropic
from typing import Dict, Any, List, Optional
import os
import logging
import json
from datetime import datetime
from ..models import Course, CourseRequest, SOPDocument, Lesson, Module
from .. import db

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        # Initialize AI clients
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        
        # Vector database setup (placeholder for Pinecone/Milvus)
        self.vector_db_initialized = False
        self._init_vector_db()
    
    def _init_vector_db(self):
        """Initialize vector database connection"""
        try:
            # Placeholder for vector database initialization
            # This would connect to Pinecone, Milvus, or similar
            self.vector_db_initialized = True
            logger.info("Vector database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {str(e)}")
    
    def process_sop_document(self, file_path: str, request_id: int) -> Dict[str, Any]:
        """Process SOP document and create vector embeddings"""
        try:
            from .file_service import FileService
            
            file_service = FileService()
            
            # Extract text from document
            text_result = file_service.extract_text_from_file(file_path)
            
            if not text_result['success']:
                return text_result
            
            text_content = text_result['text']
            
            # Generate embeddings
            embeddings = self._generate_embeddings(text_content)
            
            # Store in vector database
            vector_id = self._store_in_vector_db(text_content, embeddings, request_id)
            
            # Update SOP document record
            sop_doc = SOPDocument.query.filter_by(
                request_id=request_id,
                file_path=file_path
            ).first()
            
            if sop_doc:
                sop_doc.processing_status = 'processed'
                sop_doc.vector_id = vector_id
                sop_doc.processed_at = datetime.utcnow()
                db.session.commit()
            
            return {
                'success': True,
                'message': 'SOP processed successfully',
                'vector_id': vector_id,
                'word_count': text_result['word_count']
            }
            
        except Exception as e:
            logger.error(f"Error processing SOP document: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _generate_embeddings(self, text: str) -> List[float]:
        """Generate vector embeddings for text"""
        try:
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            return []
    
    def _store_in_vector_db(self, text: str, embeddings: List[float], request_id: int) -> str:
        """Store embeddings in vector database"""
        try:
            # Placeholder for vector database storage
            # This would use Pinecone, Milvus, or similar
            vector_id = f"sop_{request_id}_{datetime.utcnow().timestamp()}"
            
            # Store embeddings with metadata
            metadata = {
                'request_id': request_id,
                'text': text[:1000],  # Store first 1000 characters as preview
                'created_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Stored embeddings with ID: {vector_id}")
            return vector_id
            
        except Exception as e:
            logger.error(f"Failed to store in vector database: {str(e)}")
            return ""
    
    def retrieve_relevant_context(self, query: str, request_id: int, top_k: int = 5) -> List[str]:
        """Retrieve relevant SOP context using RAG"""
        try:
            # Generate query embeddings
            query_embeddings = self._generate_embeddings(query)
            
            # Search vector database
            # Placeholder for vector similarity search
            relevant_contexts = [
                "Relevant SOP context would be retrieved here based on similarity search"
            ]
            
            return relevant_contexts
            
        except Exception as e:
            logger.error(f"Failed to retrieve relevant context: {str(e)}")
            return []
    
    def generate_course_from_request(self, course_request: CourseRequest) -> Dict[str, Any]:
        """Generate AI course content from course request"""
        try:
            # Retrieve relevant SOP context
            context = self.retrieve_relevant_context(
                course_request.training_objectives,
                course_request.id
            )
            
            # Generate course outline
            course_outline = self._generate_course_outline(course_request, context)
            
            # Create course record
            course = Course(
                request_id=course_request.id,
                title=course_outline['title'],
                description=course_outline['description'],
                status='generating',
                cefr_level=course_request.target_cefr,
                created_at=datetime.utcnow()
            )
            
            db.session.add(course)
            db.session.flush()  # Get course ID
            
            # Generate modules and lessons
            for module_data in course_outline['modules']:
                module = Module(
                    course_id=course.id,
                    title=module_data['title'],
                    description=module_data['description'],
                    order=module_data['order']
                )
                
                db.session.add(module)
                db.session.flush()  # Get module ID
                
                # Generate lessons for this module
                for lesson_data in module_data['lessons']:
                    lesson_content = self._generate_lesson_content(
                        lesson_data, context, course_request.target_cefr
                    )
                    
                    lesson = Lesson(
                        module_id=module.id,
                        title=lesson_data['title'],
                        objectives=lesson_data['objectives'],
                        content=json.dumps(lesson_content),
                        order=lesson_data['order'],
                        estimated_duration=lesson_data.get('duration', 60)
                    )
                    
                    db.session.add(lesson)
            
            # Update course status
            course.status = 'pending_review'
            course.generated_at = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'success': True,
                'course_id': course.id,
                'message': 'Course generated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error generating course: {str(e)}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def _generate_course_outline(self, course_request: CourseRequest, context: List[str]) -> Dict[str, Any]:
        """Generate course outline using AI"""
        try:
            prompt = f"""
            Create a comprehensive English language course outline based on the following requirements:
            
            Company: {course_request.company_name}
            Industry: {course_request.industry}
            Current CEFR Level: {course_request.current_cefr}
            Target CEFR Level: {course_request.target_cefr}
            Training Objectives: {course_request.training_objectives}
            Pain Points: {course_request.pain_points}
            Course Length: {course_request.course_length_hours} hours
            
            Relevant SOP Context:
            {' '.join(context[:3])}
            
            Generate a course with 4-6 modules, each containing 3-5 lessons.
            Ensure content is appropriate for the CEFR level progression.
            Include industry-specific terminology and scenarios.
            
            Return as JSON with the following structure:
            {{
                "title": "Course Title",
                "description": "Course Description",
                "modules": [
                    {{
                        "title": "Module Title",
                        "description": "Module Description",
                        "order": 1,
                        "lessons": [
                            {{
                                "title": "Lesson Title",
                                "objectives": "Lesson Objectives",
                                "order": 1,
                                "duration": 60
                            }}
                        ]
                    }}
                ]
            }}
            """
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert English language curriculum designer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Failed to generate course outline: {str(e)}")
            return self._get_default_course_outline()
    
    def _generate_lesson_content(self, lesson_data: Dict, context: List[str], cefr_level: str) -> Dict[str, Any]:
        """Generate detailed lesson content"""
        try:
            prompt = f"""
            Create detailed lesson content for:
            Title: {lesson_data['title']}
            Objectives: {lesson_data['objectives']}
            CEFR Level: {cefr_level}
            
            Context from SOPs:
            {' '.join(context)}
            
            Generate content including:
            1. Dialogue/scenario
            2. Vocabulary list (10-15 words)
            3. Grammar focus
            4. Reading passage
            5. Exercises (5-8 questions)
            6. Speaking prompts
            7. Writing task
            
            Ensure content matches {cefr_level} level complexity.
            """
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert English language content creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            # Parse and structure the response
            content = response.choices[0].message.content
            
            return {
                'dialogue': self._extract_dialogue(content),
                'vocabulary': self._extract_vocabulary(content),
                'grammar': self._extract_grammar(content),
                'reading': self._extract_reading(content),
                'exercises': self._extract_exercises(content),
                'speaking_prompts': self._extract_speaking_prompts(content),
                'writing_task': self._extract_writing_task(content)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate lesson content: {str(e)}")
            return self._get_default_lesson_content()
    
    def _extract_dialogue(self, content: str) -> str:
        """Extract dialogue from AI response"""
        # Implement content parsing logic
        return "Sample dialogue content"
    
    def _extract_vocabulary(self, content: str) -> List[Dict[str, str]]:
        """Extract vocabulary from AI response"""
        return [
            {"word": "professional", "definition": "relating to work or career", "example": "Professional communication is important."}
        ]
    
    def _extract_grammar(self, content: str) -> Dict[str, str]:
        """Extract grammar focus from AI response"""
        return {
            "topic": "Present Perfect Tense",
            "explanation": "Used to describe actions that happened at an unspecified time in the past.",
            "examples": ["I have worked here for five years."]
        }
    
    def _extract_reading(self, content: str) -> str:
        """Extract reading passage from AI response"""
        return "Sample reading passage content"
    
    def _extract_exercises(self, content: str) -> List[Dict[str, Any]]:
        """Extract exercises from AI response"""
        return [
            {
                "type": "multiple_choice",
                "question": "What is the main topic?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A"
            }
        ]
    
    def _extract_speaking_prompts(self, content: str) -> List[str]:
        """Extract speaking prompts from AI response"""
        return ["Describe your daily work routine"]
    
    def _extract_writing_task(self, content: str) -> Dict[str, str]:
        """Extract writing task from AI response"""
        return {
            "prompt": "Write an email to a colleague",
            "requirements": "Use formal language, 100-150 words"
        }
    
    def _get_default_course_outline(self) -> Dict[str, Any]:
        """Return default course outline if AI generation fails"""
        return {
            "title": "Business English Fundamentals",
            "description": "A comprehensive business English course",
            "modules": [
                {
                    "title": "Introduction to Business Communication",
                    "description": "Basic business communication skills",
                    "order": 1,
                    "lessons": [
                        {
                            "title": "Professional Greetings",
                            "objectives": "Learn professional greeting styles",
                            "order": 1,
                            "duration": 60
                        }
                    ]
                }
            ]
        }
    
    def _get_default_lesson_content(self) -> Dict[str, Any]:
        """Return default lesson content if AI generation fails"""
        return {
            'dialogue': "Sample dialogue content",
            'vocabulary': [],
            'grammar': {"topic": "Basic Grammar", "explanation": "Basic explanation"},
            'reading': "Sample reading content",
            'exercises': [],
            'speaking_prompts': [],
            'writing_task': {"prompt": "Basic writing task", "requirements": "Write a short paragraph"}
        }
    
    def process_review_feedback(self, course: Course, action: str, feedback: str = None) -> Dict[str, Any]:
        """Process course review feedback"""
        try:
            if action == 'approve':
                course.status = 'approved'
                course.approved_at = datetime.utcnow()
                
            elif action == 'request_revision':
                course.status = 'needs_revision'
                # Store feedback for AI to process
                if feedback:
                    course.review_feedback = feedback
                
            elif action == 'reject':
                course.status = 'rejected'
                if feedback:
                    course.review_feedback = feedback
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Course {action} processed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error processing review feedback: {str(e)}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
