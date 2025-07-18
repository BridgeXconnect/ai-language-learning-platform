"""
Student portal routes for accessing courses, completing exercises, and tracking progress.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy import and_, or_, func

from app import db
from app.domains.auth.models import User
from app.domains.courses.models import Course
from app.models.content import CourseModule, Lesson, LessonContent, Exercise, ExerciseSubmission
from app.models.enrollment import StudentEnrollment, StudentProgress, Feedback

student_bp = Blueprint('student', __name__)


# Validation Schemas
class ExerciseSubmissionSchema(Schema):
    answers = fields.Raw(required=True)  # JSON object containing answers
    time_spent_seconds = fields.Int(validate=validate.Range(min=0))


class FeedbackSchema(Schema):
    target_type = fields.Str(required=True, validate=validate.OneOf(['course', 'lesson', 'exercise', 'content']))
    target_id = fields.Int(required=True)
    rating = fields.Int(validate=validate.Range(min=1, max=5))
    title = fields.Str(validate=validate.Length(max=200))
    comment = fields.Str(required=True, validate=validate.Length(min=10, max=1000))
    category = fields.Str(validate=validate.OneOf(['bug', 'suggestion', 'content_error', 'difficulty', 'general']))


# Dashboard and Overview Routes
@student_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics for students."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('access_enrolled_courses'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Get student enrollments
    enrollments = StudentEnrollment.query.filter_by(student_id=current_user_id).all()
    
    total_courses = len(enrollments)
    active_courses = len([e for e in enrollments if e.status == 'active'])
    completed_courses = len([e for e in enrollments if e.status == 'completed'])
    
    # Current course progress
    current_enrollment = next((e for e in enrollments if e.status == 'active'), None)
    
    # Recent activity
    recent_progress = StudentProgress.query.filter_by(
        enrollment_id=current_enrollment.id if current_enrollment else 0
    ).order_by(StudentProgress.last_accessed.desc()).limit(5).all()
    
    return jsonify({
        'overview': {
            'total_courses': total_courses,
            'active_courses': active_courses,
            'completed_courses': completed_courses,
            'current_progress': current_enrollment.progress_percentage if current_enrollment else 0
        },
        'current_course': current_enrollment.to_dict() if current_enrollment else None,
        'recent_activity': [progress.to_dict() for progress in recent_progress]
    }), 200


# Course Access Routes
@student_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_enrolled_courses():
    """Get all courses the student is enrolled in."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('access_enrolled_courses'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Get enrollments with course data
    enrollments = StudentEnrollment.query.filter_by(
        student_id=current_user_id
    ).join(Course).order_by(StudentEnrollment.enrollment_date.desc()).all()
    
    courses_data = []
    for enrollment in enrollments:
        course_data = enrollment.course.to_dict()
        course_data['enrollment'] = {
            'id': enrollment.id,
            'status': enrollment.status.value,
            'progress_percentage': enrollment.progress_percentage,
            'enrollment_date': enrollment.enrollment_date.isoformat(),
            'last_accessed': enrollment.last_accessed.isoformat() if enrollment.last_accessed else None,
            'lessons_completed': enrollment.lessons_completed,
            'average_score': enrollment.average_score
        }
        courses_data.append(course_data)
    
    return jsonify({
        'courses': courses_data
    }), 200


@student_bp.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_details(course_id):
    """Get detailed course information for a student."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('access_enrolled_courses'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Check if student is enrolled in this course
    enrollment = StudentEnrollment.query.filter_by(
        student_id=current_user_id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        return jsonify({'message': 'Course not found or not enrolled'}), 404
    
    course = enrollment.course
    course_data = course.to_dict(include_content=True)
    
    # Add enrollment-specific data
    course_data['enrollment'] = enrollment.to_dict()
    
    # Add progress data for each lesson
    for module in course_data.get('modules', []):
        for lesson in module.get('lessons', []):
            progress = StudentProgress.query.filter_by(
                enrollment_id=enrollment.id,
                lesson_id=lesson['id']
            ).first()
            
            lesson['progress'] = progress.to_dict() if progress else {
                'is_started': False,
                'is_completed': False,
                'score': None
            }
    
    return jsonify({
        'course': course_data
    }), 200


@student_bp.route('/courses/<int:course_id>/progress', methods=['GET'])
@jwt_required()
def get_course_progress(course_id):
    """Get detailed progress for a specific course."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('access_enrolled_courses'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Check enrollment
    enrollment = StudentEnrollment.query.filter_by(
        student_id=current_user_id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        return jsonify({'message': 'Course not found or not enrolled'}), 404
    
    # Get all progress records for this enrollment
    progress_records = StudentProgress.query.filter_by(
        enrollment_id=enrollment.id
    ).join(Lesson).order_by(Lesson.order_index).all()
    
    # Calculate statistics
    total_lessons = Lesson.query.join(CourseModule).filter(
        CourseModule.course_id == course_id
    ).count()
    
    completed_lessons = len([p for p in progress_records if p.is_completed])
    average_score = sum([p.score for p in progress_records if p.score]) / len(
        [p for p in progress_records if p.score]
    ) if any(p.score for p in progress_records) else None
    
    return jsonify({
        'enrollment': enrollment.to_dict(),
        'progress_overview': {
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'completion_percentage': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0,
            'average_score': average_score
        },
        'lesson_progress': [progress.to_dict() for progress in progress_records]
    }), 200


# Lesson Access Routes
@student_bp.route('/courses/<int:course_id>/lessons/<int:lesson_id>', methods=['GET'])
@jwt_required()
def get_lesson_content(course_id, lesson_id):
    """Get lesson content for a student."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('access_enrolled_courses'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Check enrollment
    enrollment = StudentEnrollment.query.filter_by(
        student_id=current_user_id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        return jsonify({'message': 'Course not found or not enrolled'}), 404
    
    # Get lesson
    lesson = Lesson.query.join(CourseModule).filter(
        and_(
            Lesson.id == lesson_id,
            CourseModule.course_id == course_id
        )
    ).first()
    
    if not lesson:
        return jsonify({'message': 'Lesson not found'}), 404
    
    # Get or create progress record
    progress = StudentProgress.query.filter_by(
        enrollment_id=enrollment.id,
        lesson_id=lesson_id
    ).first()
    
    if not progress:
        progress = StudentProgress(
            enrollment_id=enrollment.id,
            lesson_id=lesson_id
        )
        db.session.add(progress)
    
    # Mark lesson as started if not already
    if not progress.is_started:
        progress.start_lesson()
    else:
        progress.update_activity()
    
    db.session.commit()
    
    # Get lesson content and exercises
    lesson_data = lesson.to_dict(include_content=True)
    lesson_data['progress'] = progress.to_dict()
    
    # Hide correct answers from exercises (students shouldn't see them)
    for exercise in lesson_data.get('exercises', []):
        exercise.pop('correct_answers', None)
    
    return jsonify({
        'lesson': lesson_data
    }), 200


# Exercise Submission Routes
@student_bp.route('/exercises/<int:exercise_id>/submit', methods=['POST'])
@jwt_required()
def submit_exercise(exercise_id):
    """Submit answers for an exercise."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('complete_exercises'):
        return jsonify({'message': 'Access denied'}), 403
    
    schema = ExerciseSubmissionSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Get exercise
    exercise = Exercise.query.get(exercise_id)
    if not exercise:
        return jsonify({'message': 'Exercise not found'}), 404
    
    # Check if student has access to this exercise's course
    course_id = exercise.lesson.module.course_id
    enrollment = StudentEnrollment.query.filter_by(
        student_id=current_user_id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        return jsonify({'message': 'Access denied - not enrolled in course'}), 403
    
    try:
        # Create exercise submission
        submission = ExerciseSubmission(
            exercise_id=exercise_id,
            student_id=current_user_id,
            answers=data['answers'],
            started_at=datetime.utcnow(),
            time_spent_seconds=data.get('time_spent_seconds', 0)
        )
        
        # Calculate score (this would be more sophisticated in real implementation)
        score = calculate_exercise_score(exercise, data['answers'])
        submission.score = score
        
        # Generate AI feedback (placeholder - would integrate with AI service)
        feedback = generate_exercise_feedback(exercise, data['answers'], score)
        submission.feedback = feedback
        
        db.session.add(submission)
        
        # Update student progress
        progress = StudentProgress.query.filter_by(
            enrollment_id=enrollment.id,
            lesson_id=exercise.lesson_id
        ).first()
        
        if progress:
            # Update exercises completed list
            if not progress.exercises_completed:
                progress.exercises_completed = []
            
            if exercise_id not in progress.exercises_completed:
                progress.exercises_completed.append(exercise_id)
            
            # Update attempt count and score
            progress.attempts += 1
            
            # Check if lesson is now complete
            total_exercises = Exercise.query.filter_by(lesson_id=exercise.lesson_id).count()
            completed_exercises = len(progress.exercises_completed)
            
            if completed_exercises >= total_exercises and not progress.is_completed:
                # Calculate average lesson score
                lesson_submissions = ExerciseSubmission.query.join(Exercise).filter(
                    and_(
                        Exercise.lesson_id == exercise.lesson_id,
                        ExerciseSubmission.student_id == current_user_id
                    )
                ).all()
                
                if lesson_submissions:
                    avg_score = sum(s.score for s in lesson_submissions) / len(lesson_submissions)
                    progress.complete_lesson(avg_score)
        
        db.session.commit()
        
        current_app.logger.info(f'Exercise submitted: {exercise_id} by {user.username}, score: {score}')
        
        return jsonify({
            'message': 'Exercise submitted successfully',
            'submission': submission.to_dict(),
            'lesson_completed': progress.is_completed if progress else False
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Exercise submission error: {str(e)}')
        return jsonify({'message': 'Failed to submit exercise'}), 500


@student_bp.route('/exercise-submissions/<int:submission_id>', methods=['GET'])
@jwt_required()
def get_exercise_result(submission_id):
    """Get results for a specific exercise submission."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('complete_exercises'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Get submission (only student's own submissions)
    submission = ExerciseSubmission.query.filter_by(
        id=submission_id,
        student_id=current_user_id
    ).first()
    
    if not submission:
        return jsonify({'message': 'Submission not found'}), 404
    
    return jsonify({
        'submission': submission.to_dict()
    }), 200


# Progress and Performance Routes
@student_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_overall_progress():
    """Get overall learning progress across all courses."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('view_progress'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Get all enrollments
    enrollments = StudentEnrollment.query.filter_by(student_id=current_user_id).all()
    
    total_courses = len(enrollments)
    active_courses = len([e for e in enrollments if e.status == 'active'])
    completed_courses = len([e for e in enrollments if e.status == 'completed'])
    
    # Calculate overall progress
    total_progress = sum(e.progress_percentage for e in enrollments)
    average_progress = total_progress / total_courses if total_courses > 0 else 0
    
    # Get recent activity
    recent_activity = StudentProgress.query.filter(
        StudentProgress.enrollment_id.in_([e.id for e in enrollments])
    ).order_by(StudentProgress.last_accessed.desc()).limit(10).all()
    
    return jsonify({
        'overview': {
            'total_courses': total_courses,
            'active_courses': active_courses,
            'completed_courses': completed_courses,
            'average_progress': average_progress
        },
        'enrollments': [enrollment.to_dict() for enrollment in enrollments],
        'recent_activity': [activity.to_dict() for activity in recent_activity]
    }), 200


@student_bp.route('/performance', methods=['GET'])
@jwt_required()
def get_performance_stats():
    """Get detailed performance statistics."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_permission('view_progress'):
        return jsonify({'message': 'Access denied'}), 403
    
    # Get all exercise submissions
    submissions = ExerciseSubmission.query.filter_by(student_id=current_user_id).all()
    
    if not submissions:
        return jsonify({
            'message': 'No performance data available yet'
        }), 200
    
    # Calculate statistics
    total_submissions = len(submissions)
    average_score = sum(s.score for s in submissions if s.score) / len(
        [s for s in submissions if s.score]
    ) if any(s.score for s in submissions) else 0
    
    total_time_spent = sum(s.time_spent_seconds for s in submissions if s.time_spent_seconds)
    
    # Performance by skill type
    skill_performance = {}
    for submission in submissions:
        skill = submission.exercise.skill_type.value
        if skill not in skill_performance:
            skill_performance[skill] = []
        skill_performance[skill].append(submission.score)
    
    # Calculate averages by skill
    skill_averages = {
        skill: sum(scores) / len(scores) if scores else 0
        for skill, scores in skill_performance.items()
    }
    
    return jsonify({
        'overview': {
            'total_submissions': total_submissions,
            'average_score': average_score,
            'total_time_spent_hours': total_time_spent / 3600
        },
        'skill_performance': skill_averages,
        'recent_submissions': [s.to_dict() for s in submissions[-10:]]  # Last 10 submissions
    }), 200


# Feedback Routes
@student_bp.route('/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    """Submit feedback on course content or system."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    schema = FeedbackSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    try:
        feedback = Feedback(
            user_id=current_user_id,
            target_type=data['target_type'],
            target_id=data['target_id'],
            rating=data.get('rating'),
            title=data.get('title'),
            comment=data['comment'],
            category=data.get('category', 'general')
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        current_app.logger.info(f'Feedback submitted by {user.username} on {data["target_type"]} {data["target_id"]}')
        
        return jsonify({
            'message': 'Feedback submitted successfully',
            'feedback': feedback.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Feedback submission error: {str(e)}')
        return jsonify({'message': 'Failed to submit feedback'}), 500


# Helper functions
def calculate_exercise_score(exercise, student_answers):
    """Calculate score for an exercise based on student answers."""
    # This is a simplified implementation
    # Real implementation would depend on exercise type and complexity
    
    correct_answers = exercise.correct_answers
    if not correct_answers or not student_answers:
        return 0
    
    total_questions = len(correct_answers)
    correct_count = 0
    
    for question_id, correct_answer in correct_answers.items():
        student_answer = student_answers.get(question_id)
        if student_answer == correct_answer:
            correct_count += 1
    
    return int((correct_count / total_questions) * 100) if total_questions > 0 else 0


def generate_exercise_feedback(exercise, student_answers, score):
    """Generate AI feedback for exercise submission."""
    # This is a placeholder - real implementation would integrate with AI service
    
    if score >= 90:
        return "Excellent work! You've mastered this concept."
    elif score >= 70:
        return "Good job! Review the areas where you made mistakes and try again."
    elif score >= 50:
        return "You're making progress. Review the lesson content and practice more."
    else:
        return "This concept needs more practice. Review the lesson and try the exercise again."


# Error handlers
@student_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'message': 'Bad request'}), 400


@student_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'message': 'Access denied'}), 403


@student_bp.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Resource not found'}), 404


@student_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'message': 'Internal server error'}), 500