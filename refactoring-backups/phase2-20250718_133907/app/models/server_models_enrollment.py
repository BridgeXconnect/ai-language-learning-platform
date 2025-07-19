"""
Models for course enrollment, assignments, and progress tracking.
"""

from datetime import datetime
from enum import Enum
from sqlalchemy.dialects.postgresql import JSON
from app import db


class EnrollmentStatus(Enum):
    """Student enrollment status."""
    ENROLLED = "enrolled"
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
    SUSPENDED = "suspended"


class StudentEnrollment(db.Model):
    """Student enrollment in courses."""
    
    __tablename__ = 'student_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # Enrollment details
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    start_date = db.Column(db.DateTime)
    target_completion_date = db.Column(db.DateTime)
    actual_completion_date = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.Enum(EnrollmentStatus), default=EnrollmentStatus.ENROLLED)
    
    # Progress tracking
    progress_percentage = db.Column(db.Float, default=0.0)
    modules_completed = db.Column(db.Integer, default=0)
    lessons_completed = db.Column(db.Integer, default=0)
    exercises_completed = db.Column(db.Integer, default=0)
    
    # Performance metrics
    average_score = db.Column(db.Float)
    total_time_spent_minutes = db.Column(db.Integer, default=0)
    
    # Last activity
    last_accessed = db.Column(db.DateTime)
    last_lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    last_lesson = db.relationship('Lesson', foreign_keys=[last_lesson_id])
    progress_records = db.relationship('StudentProgress', backref='enrollment', lazy='dynamic')
    
    def update_progress(self):
        """Calculate and update progress metrics."""
        # This would calculate progress based on completed lessons/exercises
        # Implementation would depend on specific business rules
        pass
    
    def mark_lesson_completed(self, lesson_id):
        """Mark a lesson as completed and update progress."""
        # Check if already completed
        existing_progress = StudentProgress.query.filter_by(
            enrollment_id=self.id,
            lesson_id=lesson_id,
            is_completed=True
        ).first()
        
        if not existing_progress:
            # Create new progress record
            progress = StudentProgress(
                enrollment_id=self.id,
                lesson_id=lesson_id,
                is_completed=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(progress)
            
            # Update counters
            self.lessons_completed += 1
            self.last_lesson_id = lesson_id
            self.last_accessed = datetime.utcnow()
            
            # Recalculate progress percentage
            self.update_progress()
            
            db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'student': self.student.to_dict() if self.student else None,
            'course': self.course.to_dict() if self.course else None,
            'enrollment_date': self.enrollment_date.isoformat(),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'target_completion_date': self.target_completion_date.isoformat() if self.target_completion_date else None,
            'actual_completion_date': self.actual_completion_date.isoformat() if self.actual_completion_date else None,
            'status': self.status.value,
            'progress_percentage': self.progress_percentage,
            'modules_completed': self.modules_completed,
            'lessons_completed': self.lessons_completed,
            'exercises_completed': self.exercises_completed,
            'average_score': self.average_score,
            'total_time_spent_minutes': self.total_time_spent_minutes,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'last_lesson': self.last_lesson.to_dict() if self.last_lesson else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<StudentEnrollment {self.student.username} in {self.course.title}>'


class TrainerAssignment(db.Model):
    """Trainer assignments to courses."""
    
    __tablename__ = 'trainer_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # Assignment details
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Notes
    assignment_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_by = db.relationship('User', foreign_keys=[assigned_by_id])
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'trainer': self.trainer.to_dict() if self.trainer else None,
            'course': self.course.to_dict() if self.course else None,
            'assigned_date': self.assigned_date.isoformat(),
            'assigned_by': self.assigned_by.to_dict() if self.assigned_by else None,
            'is_active': self.is_active,
            'assignment_notes': self.assignment_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<TrainerAssignment {self.trainer.username} to {self.course.title}>'


class StudentProgress(db.Model):
    """Detailed progress tracking for students."""
    
    __tablename__ = 'student_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('student_enrollments.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    
    # Progress status
    is_started = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False)
    
    # Timing
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    time_spent_minutes = db.Column(db.Integer, default=0)
    
    # Performance
    score = db.Column(db.Float)  # Average score for lesson exercises
    attempts = db.Column(db.Integer, default=0)
    
    # Detailed tracking
    content_items_viewed = db.Column(JSON)  # List of viewed content item IDs
    exercises_completed = db.Column(JSON)  # List of completed exercise IDs
    
    # Last activity
    last_accessed = db.Column(db.DateTime)
    last_position = db.Column(db.String(100))  # Track position within lesson
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lesson = db.relationship('Lesson')
    
    def start_lesson(self):
        """Mark lesson as started."""
        if not self.is_started:
            self.is_started = True
            self.started_at = datetime.utcnow()
            db.session.commit()
    
    def complete_lesson(self, score=None):
        """Mark lesson as completed."""
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = datetime.utcnow()
            if score is not None:
                self.score = score
            
            # Update enrollment progress
            self.enrollment.mark_lesson_completed(self.lesson_id)
            
            db.session.commit()
    
    def update_activity(self, position=None):
        """Update last activity tracking."""
        self.last_accessed = datetime.utcnow()
        if position:
            self.last_position = position
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'lesson': self.lesson.to_dict() if self.lesson else None,
            'is_started': self.is_started,
            'is_completed': self.is_completed,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'time_spent_minutes': self.time_spent_minutes,
            'score': self.score,
            'attempts': self.attempts,
            'content_items_viewed': self.content_items_viewed,
            'exercises_completed': self.exercises_completed,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'last_position': self.last_position,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<StudentProgress {self.enrollment.student.username} - {self.lesson.title}>'


class Feedback(db.Model):
    """General feedback model for various entities."""
    
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # What the feedback is about
    target_type = db.Column(db.Enum(
        'course', 'lesson', 'exercise', 'content', 'system',
        name='feedback_targets'
    ), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    
    # Feedback content
    rating = db.Column(db.Integer)  # 1-5 scale
    title = db.Column(db.String(200))
    comment = db.Column(db.Text, nullable=False)
    
    # Categorization
    category = db.Column(db.Enum(
        'bug', 'suggestion', 'content_error', 'difficulty', 'general',
        name='feedback_categories'
    ), default='general')
    
    # Status
    status = db.Column(db.Enum(
        'new', 'reviewed', 'in_progress', 'resolved', 'dismissed',
        name='feedback_status'
    ), default='new')
    
    # Response
    response = db.Column(db.Text)
    responded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    responded_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    responded_by = db.relationship('User', foreign_keys=[responded_by_id])
    
    def respond(self, response_text, responded_by_id):
        """Add a response to the feedback."""
        self.response = response_text
        self.responded_by_id = responded_by_id
        self.responded_at = datetime.utcnow()
        self.status = 'resolved'
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'user': self.user.to_dict() if self.user else None,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'rating': self.rating,
            'title': self.title,
            'comment': self.comment,
            'category': self.category,
            'status': self.status,
            'response': self.response,
            'responded_by': self.responded_by.to_dict() if self.responded_by else None,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Feedback {self.target_type} by {self.user.username}>'