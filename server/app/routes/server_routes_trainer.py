"""
Trainer portal routes for accessing assigned courses and managing students.
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy import and_, or_, func

from app import db
from app.models.user import User
from app.models.course import Course
from app.models.content import CourseModule, Lesson, Exercise, ExerciseSubmission
from app.models.enrollment import TrainerAssignment, StudentEnrollment, StudentProgress, Feedback

trainer_bp = Blueprint('trainer', __name__)


# Validation Schemas
class StudentFeedbackSchema(Schema):
    feedback_text = fields.Str(required=True, validate=validate.Length(min=10, max=1000))
    rating = fields.Int(validate=validate.Range(min=1, max=5))
    skill_ratings = fields.Dict(values=fields.Int(validate=validate.Range(min=1, max=5)))


class LessonFeedbackSchema(Schema):
    content_quality = fields.Int(validate=validate.Range(min=1, max=5))
    difficulty_level = fields.Int(validate=validate.Range(min=1, max=5))
    relevance = fields.Int(validate=validate.Range(min=1, max=5))
    suggestions = fields.Str(validate=validate.Length(max=1000))
    issues_found = fields.Str(validate=validate.Length(max=1000))


class AttendanceSchema(Schema):
    student_attendances = fields.Dict(
        keys=fields.Int(),  # student_id
        values=fields.Bool()  # present/absent
    )
    lesson_notes = fields.Str(validate=validate.Length(max=500))


# Dashboard and Overview Routes
@trainer_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics for trainers."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('view_assigned_courses'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Get trainer assignments
    assignments = TrainerAssignment.query.filter_by(
        trainer_id=current_user_id,
        is_active=True
    ).all()
    
    assigned_courses = len(assignments)
    course_ids = [assignment.course_id for assignment in assignments]
    
    # Count students across all assigned courses
    total_students = 0
    if course_ids:
        total_students = StudentEnrollment.query.filter(
            StudentEnrollment.course_id.in_(course_ids),
            StudentEnrollment.status.in_(['enrolled', 'active'])
        ).count()
    
    # Recent activity
    recent_submissions = []
    if course_ids:
        recent_submissions = ExerciseSubmission.query.join(Exercise).join(Lesson).join(CourseModule).filter(
            CourseModule.course_id.in_(course_ids)
        ).order_by(ExerciseSubmission.submitted_at.desc()).limit(10).all()
    
    return jsonify({
        'overview': {
            'assigned_courses': assigned_courses,
            'total_students': total_students,
            'recent_submissions': len(recent_submissions)
        },
        'recent_assignments': [assignment.to_dict() for assignment in assignments],
        'recent_student_activity': [submission.to_dict() for submission in recent_submissions]
    }), 200


# Course Assignment Routes
@trainer_bp.route('/assigned-courses', methods=['GET'])
@jwt_required()
def get_assigned_courses():
    """Get all courses assigned to the trainer."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('view_assigned_courses'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status_filter = request.args.get('status')  # active, completed
    
    # Get assignments
    query = TrainerAssignment.query.filter_by(
        trainer_id=current_user_id,
        is_active=True
    ).join(Course)
    
    # Apply status filter
    if status_filter:
        if status_filter == 'active':
            query = query.filter(Course.status == 'published')
        elif status_filter == 'approved':
            query = query.filter(Course.status == 'approved')
    
    # Order by assignment date
    query = query.order_by(TrainerAssignment.assigned_date.desc())
    
    # Paginate
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    assignments = pagination.items
    
    # Enrich with student count and progress data
    courses_data = []
    for assignment in assignments:
        course_data = assignment.course.to_dict()
        
        # Get student enrollment stats for this course
        enrollments = StudentEnrollment.query.filter_by(course_id=assignment.course_id).all()
        
        course_data['assignment'] = assignment.to_dict()
        course_data['student_stats'] = {
            'total_enrolled': len(enrollments),
            'active_students': len([e for e in enrollments if e.status == 'active']),
            'completed_students': len([e for e in enrollments if e.status == 'completed']),
            'average_progress': sum(e.progress_percentage for e in enrollments) / len(enrollments) if enrollments else 0
        }
        
        courses_data.append(course_data)
    
    return jsonify({
        'courses': courses_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@trainer_bp.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_details(course_id):
    """Get detailed course information for trainer."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('view_assigned_courses'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Check if trainer is assigned to this course
    assignment = TrainerAssignment.query.filter_by(
        trainer_id=current_user_id,
        course_id=course_id,
        is_active=True
    ).first()
    
    if not assignment:
        return jsonify({'message': 'Course not found or not assigned'}), 404
    
    course = assignment.course
    course_data = course.to_dict(include_content=True)
    
    # Add trainer-specific information
    course_data['assignment'] = assignment.to_dict()
    
    # Get enrolled students
    enrollments = StudentEnrollment.query.filter_by(course_id=course_id).all()
    course_data['students'] = [
        {
            'enrollment': enrollment.to_dict(),
            'student': enrollment.student.to_dict()
        }
        for enrollment in enrollments
    ]
    
    return jsonify({
        'course': course_data
    }), 200


@trainer_bp.route('/courses/<int:course_id>/lessons/<int:lesson_id>', methods=['GET'])
@jwt_required()
def get_lesson_plan(course_id, lesson_id):
    """Get detailed lesson plan for trainer preparation."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('access_lesson_plans'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Check assignment
    assignment = TrainerAssignment.query.filter_by(
        trainer_id=current_user_id,
        course_id=course_id,
        is_active=True
    ).first()
    
    if not assignment:
        return jsonify({'message': 'Course not assigned'}), 404
    
    # Get lesson
    lesson = Lesson.query.join(CourseModule).filter(
        and_(
            Lesson.id == lesson_id,
            CourseModule.course_id == course_id
        )
    ).first()
    
    if not lesson:
        return jsonify({'message': 'Lesson not found'}), 404
    
    # Get lesson with full content including answers
    lesson_data = lesson.to_dict(include_content=True)
    
    # For trainers, include exercise answers and teaching notes
    for exercise in lesson_data.get('exercises', []):
        # Add correct answers (hidden from students)
        exercise_obj = Exercise.query.get(exercise['id'])
        if exercise_obj:
            exercise['correct_answers'] = exercise_obj.correct_answers
            exercise['explanation'] = exercise_obj.explanation
    
    # Add student progress summary for this lesson
    enrollments = StudentEnrollment.query.filter_by(course_id=course_id).all()
    student_progress = []
    
    for enrollment in enrollments:
        progress = StudentProgress.query.filter_by(
            enrollment_id=enrollment.id,
            lesson_id=lesson_id
        ).first()
        
        student_progress.append({
            'student': enrollment.student.to_dict(),
            'progress': progress.to_dict() if progress else None
        })
    
    lesson_data['student_progress'] = student_progress
    
    return jsonify({
        'lesson': lesson_data
    }), 200


# Student Management Routes
@trainer_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    """Get all students assigned to trainer's courses."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('track_student_progress'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Get assigned course IDs
    assignments = TrainerAssignment.query.filter_by(
        trainer_id=current_user_id,
        is_active=True
    ).all()
    
    course_ids = [assignment.course_id for assignment in assignments]
    
    if not course_ids:
        return jsonify({'students': []}), 200
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)
    course_filter = request.args.get('course_id', type=int)
    search = request.args.get('search', '').strip()
    
    # Get student enrollments
    query = StudentEnrollment.query.filter(
        StudentEnrollment.course_id.in_(course_ids)
    ).join(User)
    
    # Apply filters
    if course_filter and course_filter in course_ids:
        query = query.filter(StudentEnrollment.course_id == course_filter)
    
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    # Order by enrollment date
    query = query.order_by(StudentEnrollment.enrollment_date.desc())
    
    # Paginate
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    enrollments = pagination.items
    
    students_data = []
    for enrollment in enrollments:
        student_data = {
            'student': enrollment.student.to_dict(),
            'enrollment': enrollment.to_dict(),
            'course': enrollment.course.to_dict()
        }
        students_data.append(student_data)
    
    return jsonify({
        'students': students_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@trainer_bp.route('/students/<int:student_id>/progress', methods=['GET'])
@jwt_required()
def get_student_progress(student_id):
    """Get detailed progress for a specific student."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('track_student_progress'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Check if student is in trainer's courses
    assignments = TrainerAssignment.query.filter_by(
        trainer_id=current_user_id,
        is_active=True
    ).all()
    
    course_ids = [assignment.course_id for assignment in assignments]
    
    enrollment = StudentEnrollment.query.filter(
        and_(
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.course_id.in_(course_ids)
        )
    ).first()
    
    if not enrollment:
        return jsonify({'message': 'Student not found in your courses'}), 404
    
    # Get detailed progress
    progress_records = StudentProgress.query.filter_by(
        enrollment_id=enrollment.id
    ).join(Lesson).order_by(Lesson.order_index).all()
    
    # Get exercise submissions
    exercise_submissions = ExerciseSubmission.query.filter_by(
        student_id=student_id
    ).join(Exercise).join(Lesson).join(CourseModule).filter(
        CourseModule.course_id == enrollment.course_id
    ).order_by(ExerciseSubmission.submitted_at.desc()).all()
    
    return jsonify({
        'student': enrollment.student.to_dict(),
        'enrollment': enrollment.to_dict(),
        'course': enrollment.course.to_dict(),
        'lesson_progress': [progress.to_dict() for progress in progress_records],
        'exercise_submissions': [submission.to_dict() for submission in exercise_submissions[:20]]  # Last 20 submissions
    }), 200


# Feedback Routes
@trainer_bp.route('/students/<int:student_id>/feedback', methods=['POST'])
@jwt_required()
def submit_student_feedback(student_id):
    """Submit feedback for a student."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('provide_feedback'):
        return jsonify({'message': 'Access denied'}), 403
    
    schema = StudentFeedbackSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Check if student is in trainer's courses
    assignments = TrainerAssignment.query.filter_by(
        trainer_id=current_user_id,
        is_active=True
    ).all()
    
    course_ids = [assignment.course_id for assignment in assignments]
    
    enrollment = StudentEnrollment.query.filter(
        and_(
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.course_id.in_(course_ids)
        )
    ).first()
    
    if not enrollment:
        return jsonify({'message': 'Student not found in your courses'}), 404
    
    try:
        # Create feedback record
        feedback = Feedback(
            user_id=current_user_id,
            target_type='student',
            target_id=student_id,
            rating=data.get('rating'),
            title=f"Trainer feedback for {enrollment.student.username}",
            comment=data['feedback_text'],
            category='general'
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        current_app.logger.info(f'Student feedback submitted by trainer {user.username} for student {student_id}')
        
        return jsonify({
            'message': 'Feedback submitted successfully',
            'feedback': feedback.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Student feedback submission error: {str(e)}')
        return jsonify({'message': 'Failed to submit feedback'}), 500


@trainer_bp.route('/lessons/<int:lesson_id>/feedback', methods=['POST'])
@jwt_required()
def submit_lesson_feedback(lesson_id):
    """Submit feedback on lesson content."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('provide_feedback'):
        return jsonify({'message': 'Access denied'}), 403
    
    schema = LessonFeedbackSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Check if lesson is in trainer's assigned courses
    lesson = Lesson.query.join(CourseModule).join(Course).join(TrainerAssignment).filter(
        and_(
            Lesson.id == lesson_id,
            TrainerAssignment.trainer_id == current_user_id,
            TrainerAssignment.is_active == True
        )
    ).first()
    
    if not lesson:
        return jsonify({'message': 'Lesson not found or not assigned'}), 404
    
    try:
        # Create feedback record
        feedback_text = f"Content Quality: {data.get('content_quality', 'N/A')}/5\n"
        feedback_text += f"Difficulty Level: {data.get('difficulty_level', 'N/A')}/5\n"
        feedback_text += f"Relevance: {data.get('relevance', 'N/A')}/5\n"
        
        if data.get('suggestions'):
            feedback_text += f"\nSuggestions: {data['suggestions']}"
        
        if data.get('issues_found'):
            feedback_text += f"\nIssues Found: {data['issues_found']}"
        
        feedback = Feedback(
            user_id=current_user_id,
            target_type='lesson',
            target_id=lesson_id,
            rating=data.get('content_quality'),
            title=f"Trainer feedback for lesson: {lesson.title}",
            comment=feedback_text,
            category='content_error' if data.get('issues_found') else 'general'
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        current_app.logger.info(f'Lesson feedback submitted by trainer {user.username} for lesson {lesson_id}')
        
        return jsonify({
            'message': 'Lesson feedback submitted successfully',
            'feedback': feedback.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Lesson feedback submission error: {str(e)}')
        return jsonify({'message': 'Failed to submit lesson feedback'}), 500


# Schedule and Attendance Routes
@trainer_bp.route('/schedule', methods=['GET'])
@jwt_required()
def get_schedule():
    """Get trainer's schedule (placeholder for future LMS integration)."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('view_assigned_courses'):
        return jsonify({'message': 'Access denied'}), 403
    
    # This is a placeholder - in a real implementation, this would integrate
    # with a scheduling system or calendar service
    
    # Get assigned courses as a basic schedule
    assignments = TrainerAssignment.query.filter_by(
        trainer_id=current_user_id,
        is_active=True
    ).all()
    
    schedule_items = []
    for assignment in assignments:
        # This would normally pull from actual scheduled sessions
        schedule_items.append({
            'course': assignment.course.to_dict(),
            'assignment_date': assignment.assigned_date.isoformat(),
            'next_session': None,  # Placeholder
            'recurring_schedule': 'TBD'  # Placeholder
        })
    
    return jsonify({
        'schedule': schedule_items,
        'message': 'Schedule integration coming soon'
    }), 200


@trainer_bp.route('/lessons/<int:lesson_id>/attendance', methods=['POST'])
@jwt_required()
def mark_attendance(lesson_id):
    """Mark attendance for a lesson (placeholder)."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('track_student_progress'):
        return jsonify({'message': 'Access denied'}), 403
    
    schema = AttendanceSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Check if lesson is in trainer's assigned courses
    lesson = Lesson.query.join(CourseModule).join(Course).join(TrainerAssignment).filter(
        and_(
            Lesson.id == lesson_id,
            TrainerAssignment.trainer_id == current_user_id,
            TrainerAssignment.is_active == True
        )
    ).first()
    
    if not lesson:
        return jsonify({'message': 'Lesson not found or not assigned'}), 404
    
    try:
        # In a real implementation, this would store attendance records
        # For now, just log the attendance
        attendance_log = {
            'lesson_id': lesson_id,
            'trainer_id': current_user_id,
            'date': datetime.utcnow().isoformat(),
            'attendances': data['student_attendances'],
            'notes': data.get('lesson_notes')
        }
        
        current_app.logger.info(f'Attendance marked by trainer {user.username} for lesson {lesson_id}: {attendance_log}')
        
        return jsonify({
            'message': 'Attendance marked successfully',
            'attendance_log': attendance_log
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Attendance marking error: {str(e)}')
        return jsonify({'message': 'Failed to mark attendance'}), 500


# Reports Routes
@trainer_bp.route('/reports/student-progress', methods=['GET'])
@jwt_required()
def get_student_progress_report():
    """Generate student progress report for trainer's courses."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('track_student_progress'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Get assigned courses
    assignments = TrainerAssignment.query.filter_by(
        trainer_id=current_user_id,
        is_active=True
    ).all()
    
    course_ids = [assignment.course_id for assignment in assignments]
    
    if not course_ids:
        return jsonify({'report': {'courses': [], 'summary': {}}}), 200
    
    # Generate report for each course
    course_reports = []
    
    for assignment in assignments:
        course = assignment.course
        enrollments = StudentEnrollment.query.filter_by(course_id=course.id).all()
        
        if not enrollments:
            continue
        
        # Calculate course statistics
        total_students = len(enrollments)
        active_students = len([e for e in enrollments if e.status == 'active'])
        completed_students = len([e for e in enrollments if e.status == 'completed'])
        average_progress = sum(e.progress_percentage for e in enrollments) / total_students
        
        # Student performance breakdown
        students_performance = []
        for enrollment in enrollments:
            # Get recent submissions for this student in this course
            submissions = ExerciseSubmission.query.filter_by(
                student_id=enrollment.student_id
            ).join(Exercise).join(Lesson).join(CourseModule).filter(
                CourseModule.course_id == course.id
            ).all()
            
            avg_score = sum(s.score for s in submissions if s.score) / len(submissions) if submissions else 0
            
            students_performance.append({
                'student': enrollment.student.to_dict(),
                'progress_percentage': enrollment.progress_percentage,
                'average_score': avg_score,
                'lessons_completed': enrollment.lessons_completed,
                'last_accessed': enrollment.last_accessed.isoformat() if enrollment.last_accessed else None
            })
        
        course_reports.append({
            'course': course.to_dict(),
            'statistics': {
                'total_students': total_students,
                'active_students': active_students,
                'completed_students': completed_students,
                'average_progress': average_progress
            },
            'students': students_performance
        })
    
    # Overall summary
    all_enrollments = StudentEnrollment.query.filter(
        StudentEnrollment.course_id.in_(course_ids)
    ).all()
    
    summary = {
        'total_courses': len(assignments),
        'total_students': len(all_enrollments),
        'overall_progress': sum(e.progress_percentage for e in all_enrollments) / len(all_enrollments) if all_enrollments else 0
    }
    
    return jsonify({
        'report': {
            'courses': course_reports,
            'summary': summary,
            'generated_at': datetime.utcnow().isoformat()
        }
    }), 200


# Error handlers
@trainer_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'message': 'Bad request'}), 400


@trainer_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'message': 'Access denied'}), 403


@trainer_bp.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Resource not found'}), 404


@trainer_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'message': 'Internal server error'}), 500