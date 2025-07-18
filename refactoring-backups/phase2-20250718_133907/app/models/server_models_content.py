"""
Course content models (modules, lessons, exercises, etc.).
"""

from datetime import datetime
from enum import Enum
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from app import db


class SkillType(Enum):
    """English language skills."""
    LISTENING = "listening"
    SPEAKING = "speaking"
    READING = "reading"
    WRITING = "writing"
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    PRONUNCIATION = "pronunciation"


class ContentType(Enum):
    """Types of lesson content."""
    DIALOGUE = "dialogue"
    READING = "reading"
    GRAMMAR_EXPLANATION = "grammar_explanation"
    VOCABULARY_LIST = "vocabulary_list"
    EXERCISE = "exercise"
    ASSESSMENT = "assessment"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"


class ExerciseType(Enum):
    """Types of exercises."""
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_BLANK = "fill_in_blank"
    MATCHING = "matching"
    DRAG_AND_DROP = "drag_and_drop"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    SPEAKING_PROMPT = "speaking_prompt"
    WRITING_PROMPT = "writing_prompt"
    ORDERING = "ordering"


class CourseModule(db.Model):
    """Course module containing multiple lessons."""
    
    __tablename__ = 'course_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # Module metadata
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, nullable=False)
    
    # Learning objectives
    objectives = db.Column(JSON)  # List of learning objectives
    
    # Estimated duration
    estimated_duration_hours = db.Column(db.Integer)
    
    # Skills focus
    skill_focus = db.Column(ARRAY(db.Enum(SkillType)))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='module', lazy='dynamic', 
                            order_by='Lesson.order_index', cascade='all, delete-orphan')
    
    @property
    def total_lessons(self):
        """Get total number of lessons in this module."""
        return self.lessons.count()
    
    def to_dict(self, include_content=False):
        """Convert to dictionary representation."""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'order_index': self.order_index,
            'objectives': self.objectives,
            'estimated_duration_hours': self.estimated_duration_hours,
            'skill_focus': [skill.value for skill in self.skill_focus] if self.skill_focus else [],
            'total_lessons': self.total_lessons,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_content:
            data['lessons'] = [lesson.to_dict(include_content=True) for lesson in self.lessons]
        
        return data
    
    def __repr__(self):
        return f'<CourseModule {self.title}>'


class Lesson(db.Model):
    """Individual lesson within a module."""
    
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('course_modules.id'), nullable=False)
    
    # Lesson metadata
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, nullable=False)
    
    # Learning objectives
    objectives = db.Column(JSON)  # List of learning objectives
    
    # CEFR level for this specific lesson
    cefr_level = db.Column(db.Enum(
        'A1', 'A2', 'B1', 'B2', 'C1', 'C2',
        name='cefr_levels'
    ))
    
    # Skills focus
    skill_focus = db.Column(ARRAY(db.Enum(SkillType)))
    
    # Estimated duration
    estimated_duration_minutes = db.Column(db.Integer)
    
    # AI generation metadata
    generated_from_sop = db.Column(db.Boolean, default=False)
    generation_prompt = db.Column(db.Text)
    confidence_score = db.Column(db.Float)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    content_items = db.relationship('LessonContent', backref='lesson', lazy='dynamic',
                                  order_by='LessonContent.order_index', cascade='all, delete-orphan')
    exercises = db.relationship('Exercise', backref='lesson', lazy='dynamic',
                              order_by='Exercise.order_index', cascade='all, delete-orphan')
    
    @property
    def total_content_items(self):
        """Get total number of content items in this lesson."""
        return self.content_items.count()
    
    @property
    def total_exercises(self):
        """Get total number of exercises in this lesson."""
        return self.exercises.count()
    
    def to_dict(self, include_content=False):
        """Convert to dictionary representation."""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'order_index': self.order_index,
            'objectives': self.objectives,
            'cefr_level': self.cefr_level,
            'skill_focus': [skill.value for skill in self.skill_focus] if self.skill_focus else [],
            'estimated_duration_minutes': self.estimated_duration_minutes,
            'generated_from_sop': self.generated_from_sop,
            'confidence_score': self.confidence_score,
            'total_content_items': self.total_content_items,
            'total_exercises': self.total_exercises,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_content:
            data['content_items'] = [item.to_dict() for item in self.content_items]
            data['exercises'] = [exercise.to_dict() for exercise in self.exercises]
        
        return data
    
    def __repr__(self):
        return f'<Lesson {self.title}>'


class LessonContent(db.Model):
    """Individual content items within a lesson."""
    
    __tablename__ = 'lesson_content'
    
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    
    # Content metadata
    title = db.Column(db.String(200))
    content_type = db.Column(db.Enum(ContentType), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    
    # Content data
    content_data = db.Column(JSON, nullable=False)  # Flexible content storage
    
    # File references (for audio, video, images)
    file_url = db.Column(db.String(500))
    file_type = db.Column(db.String(50))
    
    # AI generation metadata
    generated_by_ai = db.Column(db.Boolean, default=True)
    source_sop_reference = db.Column(db.String(200))  # Reference to specific SOP section
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'title': self.title,
            'content_type': self.content_type.value,
            'order_index': self.order_index,
            'content_data': self.content_data,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'generated_by_ai': self.generated_by_ai,
            'source_sop_reference': self.source_sop_reference,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<LessonContent {self.content_type.value} - {self.title}>'


class Exercise(db.Model):
    """Exercises and assessments within lessons."""
    
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    
    # Exercise metadata
    title = db.Column(db.String(200), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    exercise_type = db.Column(db.Enum(ExerciseType), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    
    # Skill being assessed
    skill_type = db.Column(db.Enum(SkillType), nullable=False)
    
    # Exercise data
    question_data = db.Column(JSON, nullable=False)  # Questions, options, etc.
    correct_answers = db.Column(JSON, nullable=False)  # Answer key
    explanation = db.Column(db.Text)  # Explanation of correct answers
    
    # Scoring
    max_score = db.Column(db.Integer, default=100)
    passing_score = db.Column(db.Integer, default=70)
    
    # Difficulty and metadata
    difficulty_level = db.Column(db.Enum(
        'beginner', 'intermediate', 'advanced',
        name='difficulty_levels'
    ), default='intermediate')
    
    estimated_duration_minutes = db.Column(db.Integer)
    
    # AI generation metadata
    generated_by_ai = db.Column(db.Boolean, default=True)
    source_sop_reference = db.Column(db.String(200))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submissions = db.relationship('ExerciseSubmission', backref='exercise', lazy='dynamic')
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'title': self.title,
            'instructions': self.instructions,
            'exercise_type': self.exercise_type.value,
            'order_index': self.order_index,
            'skill_type': self.skill_type.value,
            'question_data': self.question_data,
            'explanation': self.explanation,
            'max_score': self.max_score,
            'passing_score': self.passing_score,
            'difficulty_level': self.difficulty_level,
            'estimated_duration_minutes': self.estimated_duration_minutes,
            'generated_by_ai': self.generated_by_ai,
            'source_sop_reference': self.source_sop_reference,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def to_dict_for_student(self):
        """Convert to dictionary without answers (for students)."""
        data = self.to_dict()
        data.pop('correct_answers', None)
        return data
    
    def __repr__(self):
        return f'<Exercise {self.title} ({self.exercise_type.value})>'


class ExerciseSubmission(db.Model):
    """Student submissions for exercises."""
    
    __tablename__ = 'exercise_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Submission data
    answers = db.Column(JSON, nullable=False)  # Student's answers
    score = db.Column(db.Integer)  # Calculated score
    feedback = db.Column(db.Text)  # AI-generated feedback
    
    # Timing
    started_at = db.Column(db.DateTime, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    time_spent_seconds = db.Column(db.Integer)
    
    # Status
    is_completed = db.Column(db.Boolean, default=True)
    attempt_number = db.Column(db.Integer, default=1)
    
    # Grading
    auto_graded = db.Column(db.Boolean, default=True)
    manually_graded = db.Column(db.Boolean, default=False)
    graded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    graded_at = db.Column(db.DateTime)
    
    # Relationships
    student = db.relationship('User', foreign_keys=[student_id])
    graded_by = db.relationship('User', foreign_keys=[graded_by_id])
    
    def calculate_score(self):
        """Calculate score based on correct answers."""
        # This would contain the logic to compare student answers
        # with correct answers and calculate a score
        pass
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'exercise_id': self.exercise_id,
            'student': self.student.to_dict() if self.student else None,
            'answers': self.answers,
            'score': self.score,
            'feedback': self.feedback,
            'started_at': self.started_at.isoformat(),
            'submitted_at': self.submitted_at.isoformat(),
            'time_spent_seconds': self.time_spent_seconds,
            'is_completed': self.is_completed,
            'attempt_number': self.attempt_number,
            'auto_graded': self.auto_graded,
            'manually_graded': self.manually_graded,
            'graded_by': self.graded_by.to_dict() if self.graded_by else None,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None
        }
    
    def __repr__(self):
        return f'<ExerciseSubmission {self.exercise_id} by {self.student.username}>'