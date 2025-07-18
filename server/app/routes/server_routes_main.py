"""
Main application routes and dashboard endpoints.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime, timedelta

from app import db
from app.domains.auth.models import User
from app.domains.courses.models import CourseRequest, Course
from app.models.enrollment import StudentEnrollment, TrainerAssignment

main_bp = Blueprint('main', __name__)


@main_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503


@main_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    """Get dashboard data based on user role."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Get role-specific dashboard data
    if user.is_admin:
        data = get_admin_dashboard_data()
    elif user.is_sales:
        data = get_sales_dashboard_data(user.id)
    elif user.is_course_manager:
        data = get_course_manager_dashboard_data()
    elif user.is_trainer:
        data = get_trainer_dashboard_data(user.id)
    elif user.is_student:
        data = get_student_dashboard_data(user.id)
    else:
        data = {'message': 'Unknown role'}
    
    return jsonify({
        'message': f'Welcome back, {user.username}!',
        'user': user.to_dict(),
        'dashboard_data': data
    }), 200


def get_admin_dashboard_data():
    """Get dashboard data for admin users."""
    # System overview statistics
    total_users = User.query.count()
    total_courses = Course.query.count()
    total_requests = CourseRequest.query.count()
    
    # Recent activity
    recent_requests = CourseRequest.query.order_by(
        CourseRequest.created_at.desc()
    ).limit(5).all()
    
    # User distribution
    user_roles = db.session.query(
        User.role, func.count(User.id)
    ).group_by(User.role).all()
    
    # Course request status distribution
    request_statuses = db.session.query(
        CourseRequest.status, func.count(CourseRequest.id)
    ).group_by(CourseRequest.status).all()
    
    return {
        'overview': {
            'total_users': total_users,
            'total_courses': total_courses,
            'total_requests': total_requests,
            'active_enrollments': StudentEnrollment.query.filter_by(status='active').count()
        },
        'user_distribution': {role: count for role, count in user_roles},
        'request_status_distribution': {status.value: count for status, count in request_statuses},
        'recent_requests': [req.to_dict() for req in recent_requests]
    }


def get_sales_dashboard_data(user_id):
    """Get dashboard data for sales representatives."""
    # My requests statistics
    my_requests = CourseRequest.query.filter_by(sales_rep_id=user_id)
    
    total_requests = my_requests.count()
    pending_requests = my_requests.filter_by(status='pending_review').count()
    approved_requests = my_requests.filter_by(status='approved').count()
    
    # Recent requests
    recent_requests = my_requests.order_by(
        CourseRequest.created_at.desc()
    ).limit(10).all()
    
    # Request status breakdown
    status_breakdown = db.session.query(
        CourseRequest.status, func.count(CourseRequest.id)
    ).filter_by(sales_rep_id=user_id).group_by(CourseRequest.status).all()
    
    # Monthly request trends (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_requests = db.session.query(
        func.date_trunc('month', CourseRequest.created_at).label('month'),
        func.count(CourseRequest.id).label('count')
    ).filter(
        CourseRequest.sales_rep_id == user_id,
        CourseRequest.created_at >= six_months_ago
    ).group_by('month').order_by('month').all()
    
    return {
        'overview': {
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'approved_requests': approved_requests
        },
        'status_breakdown': {status.value: count for status, count in status_breakdown},
        'recent_requests': [req.to_dict() for req in recent_requests],
        'monthly_trends': [
            {'month': month.isoformat(), 'count': count} 
            for month, count in monthly_requests
        ]
    }


def get_course_manager_dashboard_data():
    """Get dashboard data for course managers."""
    # Course review queue
    pending_review = Course.query.filter_by(status='pending_review').count()
    needs_revision = Course.query.filter_by(status='needs_revision').count()
    
    # Recent activity
    recent_courses = Course.query.order_by(
        Course.generated_at.desc()
    ).limit(10).all()
    
    # Course status distribution
    course_statuses = db.session.query(
        Course.status, func.count(Course.id)
    ).group_by(Course.status).all()
    
    # Request processing pipeline
    request_pipeline = db.session.query(
        CourseRequest.status, func.count(CourseRequest.id)
    ).group_by(CourseRequest.status).all()
    
    return {
        'review_queue': {
            'pending_review': pending_review,
            'needs_revision': needs_revision
        },
        'course_status_distribution': {status: count for status, count in course_statuses},
        'request_pipeline': {status.value: count for status, count in request_pipeline},
        'recent_courses': [course.to_dict() for course in recent_courses]
    }


def get_trainer_dashboard_data(user_id):
    """Get dashboard data for trainers."""
    # My assignments
    my_assignments = TrainerAssignment.query.filter_by(
        trainer_id=user_id, is_active=True
    )
    
    assigned_courses = my_assignments.count()
    
    # Students under my supervision
    total_students = 0
    course_ids = [assignment.course_id for assignment in my_assignments]
    if course_ids:
        total_students = StudentEnrollment.query.filter(
            StudentEnrollment.course_id.in_(course_ids),
            StudentEnrollment.status.in_(['enrolled', 'active'])
        ).count()
    
    # Recent assignments
    recent_assignments = my_assignments.order_by(
        TrainerAssignment.assigned_date.desc()
    ).limit(5).all()
    
    return {
        'overview': {
            'assigned_courses': assigned_courses,
            'total_students': total_students
        },
        'recent_assignments': [assignment.to_dict() for assignment in recent_assignments]
    }


def get_student_dashboard_data(user_id):
    """Get dashboard data for students."""
    # My enrollments
    my_enrollments = StudentEnrollment.query.filter_by(student_id=user_id)
    
    total_courses = my_enrollments.count()
    active_courses = my_enrollments.filter_by(status='active').count()
    completed_courses = my_enrollments.filter_by(status='completed').count()
    
    # Current progress
    current_enrollment = my_enrollments.filter_by(status='active').first()
    
    # Recent activity
    recent_enrollments = my_enrollments.order_by(
        StudentEnrollment.last_accessed.desc()
    ).limit(5).all()
    
    return {
        'overview': {
            'total_courses': total_courses,
            'active_courses': active_courses,
            'completed_courses': completed_courses
        },
        'current_course': current_enrollment.to_dict() if current_enrollment else None,
        'recent_activity': [enrollment.to_dict() for enrollment in recent_enrollments]
    }


@main_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user notifications."""
    current_user_id = get_jwt_identity()
    
    # This would fetch notifications from a notifications table
    # For now, return empty list
    return jsonify({
        'notifications': [],
        'unread_count': 0
    }), 200


@main_bp.route('/search', methods=['GET'])
@jwt_required()
def search():
    """Global search endpoint."""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')  # all, courses, users, requests
    limit = min(int(request.args.get('limit', 20)), 100)
    
    if not query:
        return jsonify({'message': 'Search query is required'}), 400
    
    results = {
        'query': query,
        'courses': [],
        'users': [],
        'requests': []
    }
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Search based on user permissions
    if search_type in ['all', 'courses'] and user.has_permission('view_courses'):
        courses = Course.query.filter(
            Course.title.ilike(f'%{query}%')
        ).limit(limit).all()
        results['courses'] = [course.to_dict() for course in courses]
    
    if search_type in ['all', 'users'] and user.has_permission('view_users'):
        users = User.query.filter(
            User.username.ilike(f'%{query}%') |
            User.email.ilike(f'%{query}%') |
            User.first_name.ilike(f'%{query}%') |
            User.last_name.ilike(f'%{query}%')
        ).limit(limit).all()
        results['users'] = [u.to_dict() for u in users]
    
    if search_type in ['all', 'requests'] and user.has_permission('view_requests'):
        requests = CourseRequest.query.filter(
            CourseRequest.company_name.ilike(f'%{query}%') |
            CourseRequest.contact_person.ilike(f'%{query}%') |
            CourseRequest.request_id.ilike(f'%{query}%')
        ).limit(limit).all()
        results['requests'] = [req.to_dict() for req in requests]
    
    return jsonify(results), 200


@main_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get system statistics."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403
    
    # System-wide statistics
    stats = {
        'users': {
            'total': User.query.count(),
            'active': User.query.filter_by(is_active=True).count(),
            'by_role': dict(db.session.query(
                User.role, func.count(User.id)
            ).group_by(User.role).all())
        },
        'courses': {
            'total': Course.query.count(),
            'published': Course.query.filter_by(status='published').count(),
            'pending_review': Course.query.filter_by(status='pending_review').count()
        },
        'requests': {
            'total': CourseRequest.query.count(),
            'pending': CourseRequest.query.filter_by(status='pending_review').count(),
            'approved': CourseRequest.query.filter_by(status='approved').count()
        },
        'enrollments': {
            'total': StudentEnrollment.query.count(),
            'active': StudentEnrollment.query.filter_by(status='active').count(),
            'completed': StudentEnrollment.query.filter_by(status='completed').count()
        }
    }
    
    return jsonify(stats), 200