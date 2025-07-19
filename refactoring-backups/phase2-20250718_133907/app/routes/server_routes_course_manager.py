"""
Course Manager routes for reviewing and managing AI-generated courses.
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy import func, and_, or_

from app import db
from app.models.user import User
from app.models.course import (
    CourseRequest, Course, RequestRejection, RevisionRequest, 
    CourseRequestStatus
)
from app.models.content import CourseModule, Lesson
from app.models.enrollment import StudentEnrollment, TrainerAssignment
from app.services.notification_service import notify_sales_course_status

course_manager_bp = Blueprint('course_manager', __name__)


# Validation Schemas
class CourseApprovalSchema(Schema):
    feedback = fields.Str(validate=validate.Length(max=1000))


class CourseRejectionSchema(Schema):
    reason = fields.Str(required=True, validate=validate.Length(min=10, max=1000))


class RevisionRequestSchema(Schema):
    feedback = fields.Str(required=True, validate=validate.Length(min=10, max=1000))


class UserCreationSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    role = fields.Str(required=True, validate=validate.OneOf(['student', 'trainer', 'sales', 'course_manager']))
    first_name = fields.Str(validate=validate.Length(max=100))
    last_name = fields.Str(validate=validate.Length(max=100))


class TrainerAssignmentSchema(Schema):
    trainer_id = fields.Int(required=True)
    course_id = fields.Int(required=True)
    assignment_notes = fields.Str(validate=validate.Length(max=500))


# Dashboard and Overview Routes
@course_manager_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics for course managers."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('review_courses'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Course review queue
    pending_review = Course.query.filter_by(status='pending_review').count()
    needs_revision = Course.query.filter_by(status='needs_revision').count()
    total_courses = Course.query.count()
    approved_courses = Course.query.filter_by(status='approved').count()
    
    # Request pipeline
    total_requests = CourseRequest.query.count()
    submitted_requests = CourseRequest.query.filter_by(status=CourseRequestStatus.SUBMITTED).count()
    generating_requests = CourseRequest.query.filter_by(status=CourseRequestStatus.GENERATING).count()
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_courses = Course.query.filter(Course.generated_at >= week_ago).count()
    recent_requests = CourseRequest.query.filter(CourseRequest.created_at >= week_ago).count()
    
    # User statistics
    total_users = User.query.count()
    active_students = StudentEnrollment.query.filter_by(status='active').count()
    active_trainers = TrainerAssignment.query.filter_by(is_active=True).count()
    
    return jsonify({
        'review_queue': {
            'pending_review': pending_review,
            'needs_revision': needs_revision,
            'total_courses': total_courses,
            'approved_courses': approved_courses
        },
        'request_pipeline': {
            'total_requests': total_requests,
            'submitted': submitted_requests,
            'generating': generating_requests
        },
        'recent_activity': {
            'courses_generated_week': recent_courses,
            'requests_submitted_week': recent_requests
        },
        'user_stats': {
            'total_users': total_users,
            'active_students': active_students,
            'active_trainers': active_trainers
        }
    }), 200


# Course Review Routes
@course_manager_bp.route('/pending-courses', methods=['GET'])
@jwt_required()
def get_pending_courses():
    """Get courses pending review."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('review_courses'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status_filter = request.args.get('status', 'pending_review')
    search = request.args.get('search', '').strip()
    
    # Base query
    query = Course.query.join(CourseRequest)
    
    # Apply status filter
    if status_filter == 'pending_review':
        query = query.filter(Course.status == 'pending_review')
    elif status_filter == 'needs_revision':
        query = query.filter(Course.status == 'needs_revision')
    elif status_filter == 'all_pending':
        query = query.filter(Course.status.in_(['pending_review', 'needs_revision']))
    
    # Apply search filter
    if search:
        query = query.filter(
            or_(
                Course.title.ilike(f'%{search}%'),
                CourseRequest.company_name.ilike(f'%{search}%'),
                CourseRequest.request_id.ilike(f'%{search}%')
            )
        )
    
    # Order by generation date (newest first)
    query = query.order_by(Course.generated_at.desc())
    
    # Paginate
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    courses = pagination.items
    
    return jsonify({
        'courses': [course.to_dict(include_content=False) for course in courses],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@course_manager_bp.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_details(course_id):
    """Get detailed course information for review."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('review_courses'):
        return jsonify({'message': 'Access denied'}), 403
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'message': 'Course not found'}), 404
    
    # Include full content for review
    course_data = course.to_dict(include_content=True)
    
    # Add revision history if any
    revisions = RevisionRequest.query.filter_by(
        course_request_id=course.course_request_id
    ).order_by(RevisionRequest.requested_at.desc()).all()
    
    course_data['revision_history'] = [
        {
            'id': rev.id,
            'feedback': rev.feedback,
            'requested_by': rev.requested_by.to_dict() if rev.requested_by else None,
            'requested_at': rev.requested_at.isoformat(),
            'addressed': rev.addressed,
            'addressed_at': rev.addressed_at.isoformat() if rev.addressed_at else None
        }
        for rev in revisions
    ]
    
    return jsonify({'course': course_data}), 200


@course_manager_bp.route('/courses/<int:course_id>/approve', methods=['POST'])
@jwt_required()
def approve_course(course_id):
    """Approve a course for use."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('approve_courses'):
        return jsonify({'message': 'Access denied'}), 403
    
    schema = CourseApprovalSchema()
    
    try:
        data = schema.load(request.json or {})
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'message': 'Course not found'}), 404
    
    if course.status not in ['pending_review', 'needs_revision']:
        return jsonify({'message': 'Course cannot be approved in current status'}), 400
    
    try:
        # Approve the course
        course.approve(current_user_id)
        
        # Also approve the course request
        course_request = course.original_request
        if course_request:
            course_request.approve(current_user_id)
            
            # Notify sales rep
            notify_sales_course_status(
                course_request.id, 
                'approved', 
                data.get('feedback', 'Course has been approved and is ready for assignment.')
            )
        
        current_app.logger.info(f'Course approved: {course.title} by {user.username}')
        
        return jsonify({
            'message': 'Course approved successfully',
            'course': course.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Course approval error: {str(e)}')
        return jsonify({'message': 'Failed to approve course'}), 500


@course_manager_bp.route('/courses/<int:course_id>/reject', methods=['POST'])
@jwt_required()
def reject_course(course_id):
    """Reject a course."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('approve_courses'):
        return jsonify({'message': 'Access denied'}), 403
    
    schema = CourseRejectionSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'message': 'Course not found'}), 404
    
    if course.status not in ['pending_review', 'needs_revision']:
        return jsonify({'message': 'Course cannot be rejected in current status'}), 400
    
    try:
        # Reject the course request
        course_request = course.original_request
        if course_request:
            course_request.reject(data['reason'])
            
            # Create rejection record
            rejection = RequestRejection(
                course_request_id=course_request.id,
                reason=data['reason'],
                rejected_by_id=current_user_id,
                rejected_at=datetime.utcnow()
            )
            db.session.add(rejection)
            
            # Notify sales rep
            notify_sales_course_status(
                course_request.id, 
                'rejected', 
                data['reason']
            )
        
        db.session.commit()
        
        current_app.logger.info(f'Course rejected: {course.title} by {user.username}')
        
        return jsonify({
            'message': 'Course rejected successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Course rejection error: {str(e)}')
        return jsonify({'message': 'Failed to reject course'}), 500


@course_manager_bp.route('/courses/<int:course_id>/request-revision', methods=['POST'])
@jwt_required()
def request_course_revision(course_id):
    """Request revision for a course."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('approve_courses'):
        return jsonify({'message': 'Access denied'}), 403
    
    schema = RevisionRequestSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'message': 'Course not found'}), 404
    
    if course.status not in ['pending_review', 'needs_revision']:
        return jsonify({'message': 'Course revision cannot be requested in current status'}), 400
    
    try:
        # Request revision
        course.request_revision()
        
        # Create revision request record
        course_request = course.original_request
        if course_request:
            course_request.request_revision(data['feedback'])
            
            revision = RevisionRequest(
                course_request_id=course_request.id,
                feedback=data['feedback'],
                requested_by_id=current_user_id,
                requested_at=datetime.utcnow()
            )
            db.session.add(revision)
            
            # Notify sales rep
            notify_sales_course_status(
                course_request.id, 
                'needs_revision', 
                data['feedback']
            )
        
        db.session.commit()
        
        current_app.logger.info(f'Course revision requested: {course.title} by {user.username}')
        
        # TODO: Trigger AI regeneration process
        # regenerate_course_content.delay(course.id, data['feedback'])
        
        return jsonify({
            'message': 'Course revision requested successfully',
            'course': course.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Course revision request error: {str(e)}')
        return jsonify({'message': 'Failed to request course revision'}), 500


# Content Library Management
@course_manager_bp.route('/content-library', methods=['GET'])
@jwt_required()
def get_content_library():
    """Get approved content library."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('manage_content_library'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    content_type = request.args.get('type', 'all')  # course, module, lesson
    cefr_level = request.args.get('cefr_level')
    search = request.args.get('search', '').strip()
    
    results = {}
    
    if content_type in ['all', 'course']:
        # Get approved courses
        course_query = Course.query.filter_by(status='approved')
        
        if search:
            course_query = course_query.filter(Course.title.ilike(f'%{search}%'))
        
        course_pagination = course_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        results['courses'] = {
            'items': [course.to_dict() for course in course_pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': course_pagination.total,
                'pages': course_pagination.pages
            }
        }
    
    if content_type in ['all', 'lesson']:
        # Get lessons from approved courses
        lesson_query = Lesson.query.join(CourseModule).join(Course).filter(
            Course.status == 'approved'
        )
        
        if cefr_level:
            lesson_query = lesson_query.filter(Lesson.cefr_level == cefr_level)
        
        if search:
            lesson_query = lesson_query.filter(
                or_(
                    Lesson.title.ilike(f'%{search}%'),
                    Lesson.description.ilike(f'%{search}%')
                )
            )
        
        lesson_pagination = lesson_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        results['lessons'] = {
            'items': [lesson.to_dict() for lesson in lesson_pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': lesson_pagination.total,
                'pages': lesson_pagination.pages
            }
        }
    
    return jsonify(results), 200


# User Management Routes
@course_manager_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (admin only)."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('manage_users'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)
    role_filter = request.args.get('role')
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status')  # active, inactive
    
    # Base query
    query = User.query
    
    # Apply filters
    if role_filter:
        query = query.filter(User.role == role_filter)
    
    if status_filter == 'active':
        query = query.filter(User.is_active == True)
    elif status_filter == 'inactive':
        query = query.filter(User.is_active == False)
    
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )
    
    # Order by creation date
    query = query.order_by(User.created_at.desc())
    
    # Paginate
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    users = pagination.items
    
    return jsonify({
        'users': [user.to_dict() for user in users],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@course_manager_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """Create a new user (admin only)."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('manage_users'):
        return jsonify({'message': 'Access denied'}), 403
    
    schema = UserCreationSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    try:
        # Create new user
        new_user = User.create_user(**data)
        
        current_app.logger.info(f'New user created: {new_user.username} by {user.username}')
        
        return jsonify({
            'message': 'User created successfully',
            'user': new_user.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'message': str(e)}), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'User creation error: {str(e)}')
        return jsonify({'message': 'Failed to create user'}), 500


# Trainer Assignment Routes
@course_manager_bp.route('/trainer-assignments', methods=['GET'])
@jwt_required()
def get_trainer_assignments():
    """Get all trainer assignments."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('assign_trainers'):
        return jsonify({'message': 'Access denied'}), 403
    
    assignments = TrainerAssignment.query.filter_by(is_active=True).all()
    
    return jsonify({
        'assignments': [assignment.to_dict() for assignment in assignments]
    }), 200


@course_manager_bp.route('/trainer-assignments', methods=['POST'])
@jwt_required()
def create_trainer_assignment():
    """Assign a trainer to a course."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('assign_trainers'):
        return jsonify({'message': 'Access denied'}), 403
    
    schema = TrainerAssignmentSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Validate trainer and course exist
    trainer = User.query.filter_by(id=data['trainer_id'], role='trainer').first()
    if not trainer:
        return jsonify({'message': 'Trainer not found'}), 404
    
    course = Course.query.filter_by(id=data['course_id'], status='approved').first()
    if not course:
        return jsonify({'message': 'Approved course not found'}), 404
    
    # Check if assignment already exists
    existing = TrainerAssignment.query.filter_by(
        trainer_id=data['trainer_id'],
        course_id=data['course_id'],
        is_active=True
    ).first()
    
    if existing:
        return jsonify({'message': 'Trainer already assigned to this course'}), 409
    
    try:
        # Create assignment
        assignment = TrainerAssignment(
            trainer_id=data['trainer_id'],
            course_id=data['course_id'],
            assigned_by_id=current_user_id,
            assignment_notes=data.get('assignment_notes')
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        current_app.logger.info(
            f'Trainer assigned: {trainer.username} to course {course.title} by {user.username}'
        )
        
        return jsonify({
            'message': 'Trainer assigned successfully',
            'assignment': assignment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Trainer assignment error: {str(e)}')
        return jsonify({'message': 'Failed to assign trainer'}), 500


# Error handlers
@course_manager_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'message': 'Bad request'}), 400


@course_manager_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'message': 'Access denied'}), 403


@course_manager_bp.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Resource not found'}), 404


@course_manager_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'message': 'Internal server error'}), 500