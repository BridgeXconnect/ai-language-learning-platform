"""
Sales portal routes for course request management and SOP uploads.
"""

import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from werkzeug.utils import secure_filename
from sqlalchemy import and_, or_

from app import db
from app.models.user import User
from app.models.course import CourseRequest, SOPDocument, CEFRLevel, CourseRequestStatus
from app.services.file_service import save_uploaded_file, allowed_file
from app.services.notification_service import notify_course_manager_new_request

sales_bp = Blueprint('sales', __name__)


# Validation Schemas
class CourseRequestSchema(Schema):
    # Client information
    company_name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    industry = fields.Str(validate=validate.Length(max=100))
    contact_person = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    contact_email = fields.Email(required=True)
    contact_phone = fields.Str(validate=validate.Length(max=20))
    
    # Training requirements
    cohort_size = fields.Int(required=True, validate=validate.Range(min=1, max=1000))
    current_cefr = fields.Str(required=True, validate=validate.OneOf([level.value for level in CEFRLevel]))
    target_cefr = fields.Str(required=True, validate=validate.OneOf([level.value for level in CEFRLevel]))
    training_objectives = fields.Str(required=True, validate=validate.Length(min=10))
    pain_points = fields.Str(validate=validate.Length(max=1000))
    specific_requirements = fields.Str(validate=validate.Length(max=1000))
    
    # Course structure preferences
    course_length_hours = fields.Int(validate=validate.Range(min=1, max=500))
    lessons_per_module = fields.Int(validate=validate.Range(min=1, max=50))
    delivery_method = fields.Str(validate=validate.OneOf(['in_person', 'virtual', 'blended']))
    preferred_schedule = fields.Str(validate=validate.Length(max=200))
    priority = fields.Str(validate=validate.OneOf(['low', 'normal', 'high', 'urgent']))


class CourseRequestUpdateSchema(Schema):
    # Optional fields for updates - same as above but all optional
    company_name = fields.Str(validate=validate.Length(min=2, max=200))
    industry = fields.Str(validate=validate.Length(max=100))
    contact_person = fields.Str(validate=validate.Length(min=2, max=200))
    contact_email = fields.Email()
    contact_phone = fields.Str(validate=validate.Length(max=20))
    cohort_size = fields.Int(validate=validate.Range(min=1, max=1000))
    current_cefr = fields.Str(validate=validate.OneOf([level.value for level in CEFRLevel]))
    target_cefr = fields.Str(validate=validate.OneOf([level.value for level in CEFRLevel]))
    training_objectives = fields.Str(validate=validate.Length(min=10))
    pain_points = fields.Str(validate=validate.Length(max=1000))
    specific_requirements = fields.Str(validate=validate.Length(max=1000))
    course_length_hours = fields.Int(validate=validate.Range(min=1, max=500))
    lessons_per_module = fields.Int(validate=validate.Range(min=1, max=50))
    delivery_method = fields.Str(validate=validate.OneOf(['in_person', 'virtual', 'blended']))
    preferred_schedule = fields.Str(validate=validate.Length(max=200))
    priority = fields.Str(validate=validate.OneOf(['low', 'normal', 'high', 'urgent']))


# Routes
@sales_bp.route('/course-requests', methods=['GET'])
@jwt_required()
def get_course_requests():
    """Get course requests for the current sales rep."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('create_course_requests'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status_filter = request.args.get('status')
    search = request.args.get('search', '').strip()
    
    # Base query - sales reps see only their requests, admins see all
    if user.is_admin:
        query = CourseRequest.query
    else:
        query = CourseRequest.query.filter_by(sales_rep_id=current_user_id)
    
    # Apply filters
    if status_filter:
        try:
            status_enum = CourseRequestStatus(status_filter)
            query = query.filter(CourseRequest.status == status_enum)
        except ValueError:
            return jsonify({'message': 'Invalid status filter'}), 400
    
    if search:
        query = query.filter(
            or_(
                CourseRequest.company_name.ilike(f'%{search}%'),
                CourseRequest.contact_person.ilike(f'%{search}%'),
                CourseRequest.request_id.ilike(f'%{search}%'),
                CourseRequest.training_objectives.ilike(f'%{search}%')
            )
        )
    
    # Order by creation date (newest first)
    query = query.order_by(CourseRequest.created_at.desc())
    
    # Paginate
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    requests = pagination.items
    
    return jsonify({
        'requests': [req.to_dict() for req in requests],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@sales_bp.route('/course-requests', methods=['POST'])
@jwt_required()
def create_course_request():
    """Create a new course request."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('create_course_requests'):
        return jsonify({'message': 'Access denied'}), 403
    
    schema = CourseRequestSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    try:
        # Create new course request
        course_request = CourseRequest(
            sales_rep_id=current_user_id,
            **data
        )
        
        db.session.add(course_request)
        db.session.commit()
        
        current_app.logger.info(f'New course request created: {course_request.request_id} by {user.username}')
        
        return jsonify({
            'message': 'Course request created successfully',
            'request': course_request.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Course request creation error: {str(e)}')
        return jsonify({'message': 'Failed to create course request'}), 500


@sales_bp.route('/course-requests/<int:request_id>', methods=['GET'])
@jwt_required()
def get_course_request(request_id):
    """Get a specific course request."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Get course request
    if user.is_admin:
        course_request = CourseRequest.query.get(request_id)
    else:
        course_request = CourseRequest.query.filter_by(
            id=request_id, sales_rep_id=current_user_id
        ).first()
    
    if not course_request:
        return jsonify({'message': 'Course request not found'}), 404
    
    return jsonify({
        'request': course_request.to_dict()
    }), 200


@sales_bp.route('/course-requests/<int:request_id>', methods=['PUT'])
@jwt_required()
def update_course_request(request_id):
    """Update a course request (only if in draft status)."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('create_course_requests'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Get course request
    course_request = CourseRequest.query.filter_by(
        id=request_id, sales_rep_id=current_user_id
    ).first()
    
    if not course_request:
        return jsonify({'message': 'Course request not found'}), 404
    
    # Check if request can be updated
    if course_request.status != CourseRequestStatus.DRAFT:
        return jsonify({'message': 'Only draft requests can be updated'}), 400
    
    schema = CourseRequestUpdateSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    try:
        # Update fields
        for field, value in data.items():
            if hasattr(course_request, field):
                setattr(course_request, field, value)
        
        db.session.commit()
        
        current_app.logger.info(f'Course request updated: {course_request.request_id}')
        
        return jsonify({
            'message': 'Course request updated successfully',
            'request': course_request.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Course request update error: {str(e)}')
        return jsonify({'message': 'Failed to update course request'}), 500


@sales_bp.route('/course-requests/<int:request_id>/submit', methods=['POST'])
@jwt_required()
def submit_course_request(request_id):
    """Submit a course request for processing."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('create_course_requests'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Get course request
    course_request = CourseRequest.query.filter_by(
        id=request_id, sales_rep_id=current_user_id
    ).first()
    
    if not course_request:
        return jsonify({'message': 'Course request not found'}), 404
    
    # Check if request can be submitted
    if course_request.status != CourseRequestStatus.DRAFT:
        return jsonify({'message': 'Only draft requests can be submitted'}), 400
    
    try:
        # Submit the request
        course_request.submit()
        
        # Send notification to course managers
        notify_course_manager_new_request(course_request.id)
        
        current_app.logger.info(f'Course request submitted: {course_request.request_id}')
        
        return jsonify({
            'message': 'Course request submitted successfully',
            'request': course_request.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Course request submission error: {str(e)}')
        return jsonify({'message': 'Failed to submit course request'}), 500


@sales_bp.route('/course-requests/<int:request_id>/sop', methods=['POST'])
@jwt_required()
def upload_sop(request_id):
    """Upload SOP documents for a course request."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('create_course_requests'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Get course request
    course_request = CourseRequest.query.filter_by(
        id=request_id, sales_rep_id=current_user_id
    ).first()
    
    if not course_request:
        return jsonify({'message': 'Course request not found'}), 404
    
    # Check if SOPs can be uploaded
    if course_request.status not in [CourseRequestStatus.DRAFT, CourseRequestStatus.SUBMITTED]:
        return jsonify({'message': 'SOPs cannot be uploaded at this stage'}), 400
    
    # Check if file was uploaded
    if 'sop' not in request.files:
        return jsonify({'message': 'No file uploaded'}), 400
    
    file = request.files['sop']
    
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'message': 'File type not allowed'}), 400
    
    try:
        # Save file
        file_info = save_uploaded_file(file, 'sop')
        
        # Create SOP document record
        sop_doc = SOPDocument(
            course_request_id=course_request.id,
            filename=file_info['filename'],
            original_filename=file.filename,
            file_size=file_info['file_size'],
            content_type=file.content_type or 'application/octet-stream',
            file_path=file_info['file_path']
        )
        
        db.session.add(sop_doc)
        db.session.commit()
        
        # TODO: Trigger SOP processing job
        # process_sop_async.delay(sop_doc.id)
        
        current_app.logger.info(f'SOP uploaded for request {course_request.request_id}: {file.filename}')
        
        return jsonify({
            'message': 'SOP uploaded successfully',
            'sop_document': sop_doc.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'SOP upload error: {str(e)}')
        return jsonify({'message': 'Failed to upload SOP'}), 500


@sales_bp.route('/course-requests/<int:request_id>/sop/<int:sop_id>', methods=['DELETE'])
@jwt_required()
def delete_sop(request_id, sop_id):
    """Delete an uploaded SOP document."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('create_course_requests'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Get course request
    course_request = CourseRequest.query.filter_by(
        id=request_id, sales_rep_id=current_user_id
    ).first()
    
    if not course_request:
        return jsonify({'message': 'Course request not found'}), 404
    
    # Get SOP document
    sop_doc = SOPDocument.query.filter_by(
        id=sop_id, course_request_id=course_request.id
    ).first()
    
    if not sop_doc:
        return jsonify({'message': 'SOP document not found'}), 404
    
    # Check if SOP can be deleted
    if course_request.status not in [CourseRequestStatus.DRAFT, CourseRequestStatus.SUBMITTED]:
        return jsonify({'message': 'SOP cannot be deleted at this stage'}), 400
    
    try:
        # Delete file from storage
        if os.path.exists(sop_doc.file_path):
            os.remove(sop_doc.file_path)
        
        # Delete database record
        db.session.delete(sop_doc)
        db.session.commit()
        
        current_app.logger.info(f'SOP deleted: {sop_doc.original_filename}')
        
        return jsonify({'message': 'SOP deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'SOP deletion error: {str(e)}')
        return jsonify({'message': 'Failed to delete SOP'}), 500


@sales_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics for sales representatives."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('create_course_requests'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Get stats for this sales rep
    if user.is_admin:
        base_query = CourseRequest.query
    else:
        base_query = CourseRequest.query.filter_by(sales_rep_id=current_user_id)
    
    total_requests = base_query.count()
    draft_requests = base_query.filter_by(status=CourseRequestStatus.DRAFT).count()
    submitted_requests = base_query.filter_by(status=CourseRequestStatus.SUBMITTED).count()
    pending_requests = base_query.filter_by(status=CourseRequestStatus.PENDING_REVIEW).count()
    approved_requests = base_query.filter_by(status=CourseRequestStatus.APPROVED).count()
    
    return jsonify({
        'overview': {
            'total_requests': total_requests,
            'draft_requests': draft_requests,
            'submitted_requests': submitted_requests,
            'pending_requests': pending_requests,
            'approved_requests': approved_requests
        }
    }), 200


# Error handlers
@sales_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'message': 'Bad request'}), 400


@sales_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'message': 'Access denied'}), 403


@sales_bp.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Resource not found'}), 404


@sales_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'message': 'Internal server error'}), 500