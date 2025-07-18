# server/app/models.py (Extended)
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='student')  # sales, course_manager, trainer, student, admin
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    course_requests = db.relationship('CourseRequest', backref='creator', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    student_enrollments = db.relationship('StudentEnrollment', backref='student', lazy=True)
    trainer_assignments = db.relationship('TrainerAssignment', backref='trainer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class CourseRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Client Information
    company_name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100))
    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20))
    
    # Training Details
    course_title = db.Column(db.String(200))
    cohort_size = db.Column(db.Integer)
    current_cefr = db.Column(db.String(2), default='A1')
    target_cefr = db.Column(db.String(2), default='A2')
    training_objectives = db.Column(db.Text)
    pain_points = db.Column(db.Text)
    
    # Course Structure
    course_length_hours = db.Column(db.Integer)
    lessons_per_week = db.Column(db.Integer)
    delivery_method = db.Column(db.String(20), default='in_person')  # in_person, virtual, blended
    
    # Status and Tracking
    status = db.Column(db.String(20), default='pending')  # pending, generating, pending_review, approved, rejected, completed
    priority = db.Column(db.String(10), default='normal')  # low, normal, high, urgent
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    
    # Relationships
    sop_documents = db.relationship('SOPDocument', backref='course_request', lazy=True, cascade='all, delete-orphan')
    courses = db.relationship('Course', backref='request', lazy=True)

class SOPDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('course_request.id'), nullable=False)
    
    # File Information
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)  # S3 key or local path
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    
    # Processing Status
    processing_status = db.Column(db.String(20), default='uploaded')  # uploaded, processing, processed, failed
    extracted_text = db.Column(db.Text)
    word_count = db.Column(db.Integer)
    vector_id = db.Column(db.String(100))  # Reference to vector database
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('course_request.id'), nullable=False)
    
    # Course Information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    cefr_level = db.Column(db.String(2), nullable=False)
    estimated_duration_hours = db.Column(db.Integer)
    
    # Status and Version
    status = db.Column(db.String(20), default='generating')  # generating, pending_review, approved, needs_revision, rejected, published
    version = db.Column(db.String(10), default='1.0')
    
    # AI Generation Metadata
    ai_confidence_score = db.Column(db.Float)
    generation_model = db.Column(db.String(50))
    generation_prompt_version = db.Column(db.String(20))
    
    # Review Information
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    review_feedback = db.Column(db.Text)
    review_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    generated_at = db.Column(db.DateTime)
    reviewed_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    published_at = db.Column(db.DateTime)
    
    # Relationships
    modules = db.relationship('Module', backref='course', lazy=True, cascade='all, delete-orphan', order_by='Module.order')
    enrollments = db.relationship('StudentEnrollment', backref='course', lazy=True)
    assignments = db.relationship('TrainerAssignment', backref='course', lazy=True)

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    # Module Information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    objectives = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)
    estimated_duration_hours = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='module', lazy=True, cascade='all, delete-orphan', order_by='Lesson.order')

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    
    # Lesson Information
    title = db.Column(db.String(200), nullable=False)
    objectives = db.Column(db.Text)
    content = db.Column(db.Text)  # JSON string containing lesson content
    order = db.Column(db.Integer, nullable=False)
    estimated_duration = db.Column(db.Integer, default=60)  # minutes
    
    # Lesson Type and Skills
    lesson_type = db.Column(db.String(20), default='mixed')  # reading, listening, speaking, writing, grammar, vocabulary, mixed
    skill_focus = db.Column(db.String(100))  # JSON array of skills
    difficulty_level = db.Column(db.String(10))  # easy, medium, hard
    
    # AI Metadata
    ai_generated = db.Column(db.Boolean, default=True)
    content_source = db.Column(db.String(50))  # openai, anthropic, human
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exercises = db.relationship('Exercise', backref='lesson', lazy=True, cascade='all, delete-orphan')
    student_progress = db.relationship('StudentProgress', backref='lesson', lazy=True)

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    
    # Exercise Information
    title = db.Column(db.String(200))
    exercise_type = db.Column(db.String(30), nullable=False)  # multiple_choice, fill_blank, matching, speaking, writing, drag_drop
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)  # JSON array for multiple choice options
    correct_answer = db.Column(db.Text)
    explanation = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)
    
    # Difficulty and Points
    difficulty = db.Column(db.String(10), default='medium')
    points = db.Column(db.Integer, default=1)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student_responses = db.relationship('StudentResponse', backref='exercise', lazy=True)

class StudentEnrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    # Enrollment Information
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    start_date = db.Column(db.DateTime)
    target_completion_date = db.Column(db.DateTime)
    actual_completion_date = db.Column(db.DateTime)
    
    # Progress Tracking
    status = db.Column(db.String(20), default='active')  # active, completed, dropped, paused
    progress_percentage = db.Column(db.Float, default=0.0)
    current_lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    
    # Performance Metrics
    total_time_spent = db.Column(db.Integer, default=0)  # minutes
    average_score = db.Column(db.Float)
    completed_lessons = db.Column(db.Integer, default=0)
    total_lessons = db.Column(db.Integer)

class StudentProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    
    # Progress Information
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed
    completion_percentage = db.Column(db.Float, default=0.0)
    time_spent = db.Column(db.Integer, default=0)  # minutes
    
    # Performance
    score = db.Column(db.Float)
    attempts = db.Column(db.Integer, default=0)
    
    # Timestamps
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)

class StudentResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    
    # Response Information
    answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean)
    score = db.Column(db.Float)
    
    # AI Feedback
    ai_feedback = db.Column(db.Text)
    feedback_confidence = db.Column(db.Float)
    
    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    feedback_entries = db.relationship('TrainerFeedback', backref='student_response', lazy=True)

class TrainerAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    # Assignment Information
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    
    # Responsibilities
    responsibilities = db.Column(db.Text)  # JSON array of responsibilities
    notes = db.Column(db.Text)

class TrainerFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    response_id = db.Column(db.Integer, db.ForeignKey('student_response.id'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    
    # Feedback Information
    feedback_type = db.Column(db.String(20), nullable=False)  # exercise, lesson, general, speaking, writing
    feedback_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)  # 1-5 scale
    
    # Categories for detailed feedback
    grammar_score = db.Column(db.Integer)
    vocabulary_score = db.Column(db.Integer)
    pronunciation_score = db.Column(db.Integer)
    fluency_score = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Notification Information
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='info')  # info, success, warning, error, urgent
    
    # Status
    read = db.Column(db.Boolean, default=False)
    
    # Additional Data
    data = db.Column(db.Text)  # JSON string for additional notification data
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)

class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Action Information
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.Integer)
    
    # Details
    details = db.Column(db.Text)  # JSON string with action details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# client/src/components/student/LessonPlayer.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';
import ExerciseComponent from './ExerciseComponent';
import { 
  ChevronLeftIcon, 
  ChevronRightIcon, 
  BookOpenIcon,
  SpeakerWaveIcon,
  PencilSquareIcon
} from '@heroicons/react/24/outline';

const LessonPlayer = () => {
  const { courseId, lessonId } = useParams();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentSection, setCurrentSection] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    fetchLesson();
  }, [courseId, lessonId]);

  const fetchLesson = async () => {
    try {
      const response = await api.get(`/student/courses/${courseId}/lessons/${lessonId}`);
      setLesson(response.data.lesson);
      setProgress(response.data.progress || 0);
    } catch (error) {
      console.error('Error fetching lesson:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateProgress = async (sectionIndex) => {
    try {
      const newProgress = ((sectionIndex + 1) / getTotalSections()) * 100;
      await api.post(`/student/lessons/${lessonId}/progress`, {
        section: sectionIndex,
        progress: newProgress
      });
      setProgress(newProgress);
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  const getTotalSections = () => {
    if (!lesson?.content) return 0;
    const content = typeof lesson.content === 'string' ? JSON.parse(lesson.content) : lesson.content;
    return Object.keys(content).filter(key => content[key] && content[key] !== '').length;
  };

  const getSectionKeys = () => {
    if (!lesson?.content) return [];
    const content = typeof lesson.content === 'string' ? JSON.parse(lesson.content) : lesson.content;
    return Object.keys(content).filter(key => content[key] && content[key] !== '');
  };

  const nextSection = () => {
    const totalSections = getTotalSections();
    if (currentSection < totalSections - 1) {
      const newSection = currentSection + 1;
      setCurrentSection(newSection);
      updateProgress(newSection);
    }
  };

  const prevSection = () => {
    if (currentSection > 0) {
      setCurrentSection(currentSection - 1);
    }
  };

  const renderContent = (type, content) => {
    switch (type) {
      case 'dialogue':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center">
              <SpeakerWaveIcon className="h-5 w-5 mr-2" />
              Dialogue
            </h3>
            <div className="bg-blue-50 p-4 rounded-lg">
              <pre className="whitespace-pre-wrap text-gray-700">{content}</pre>
            </div>
          </div>
        );
      
      case 'vocabulary':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center">
              <BookOpenIcon className="h-5 w-5 mr-2" />
              Vocabulary
            </h3>
            <div className="grid gap-4">
              {Array.isArray(content) ? content.map((item, index) => (
                <div key={index} className="bg-green-50 p-4 rounded-lg">
                  <div className="font-medium text-green-800">{item.word}</div>
                  <div className="text-green-600">{item.definition}</div>
                  {item.example && (
                    <div className="text-sm text-green-500 italic mt-1">
                      Example: {item.example}
                    </div>
                  )}
                </div>
              )) : (
                <div className="bg-green-50 p-4 rounded-lg">
                  <pre className="whitespace-pre-wrap text-gray-700">{content}</pre>
                </div>
              )}
            </div>
          </div>
        );
      
      case 'grammar':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center">
              <PencilSquareIcon className="h-5 w-5 mr-2" />
              Grammar Focus
            </h3>
            <div className="bg-purple-50 p-4 rounded-lg">
              {typeof content === 'object' ? (
                <div>
                  <h4 className="font-medium text-purple-800">{content.topic}</h4>
                  <p className="text-purple-600 mt-2">{content.explanation}</p>
                  {content.examples && (
                    <div className="mt-3">
                      <p className="font-medium text-purple-700">Examples:</p>
                      <ul className="list-disc list-inside text-purple-600">
                        {content.examples.map((example, index) => (
                          <li key={index}>{example}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <pre className="whitespace-pre-wrap text-gray-700">{content}</pre>
              )}
            </div>
          </div>
        );
      
      case 'reading':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center">
              <BookOpenIcon className="h-5 w-5 mr-2" />
              Reading Passage
            </h3>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <pre className="whitespace-pre-wrap text-gray-700">{content}</pre>
            </div>
          </div>
        );
      
      case 'exercises':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Exercises</h3>
            {Array.isArray(content) ? content.map((exercise, index) => (
              <ExerciseComponent 
                key={index} 
                exercise={exercise} 
                exerciseIndex={index}
                lessonId={lessonId}
              />
            )) : (
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-700">{content}</p>
              </div>
            )}
          </div>
        );
      
      default:
        return (
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold capitalize">{type.replace('_', ' ')}</h3>
            <pre className="whitespace-pre-wrap text-gray-700 mt-2">{content}</pre>
          </div>
        );
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading lesson..." />;
  }

  if (!lesson) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Lesson not found</p>
      </div>
    );
  }

  const content = typeof lesson.content === 'string' ? JSON.parse(lesson.content) : lesson.content;
  const sectionKeys = getSectionKeys();
  const currentSectionKey = sectionKeys[currentSection];
  const currentContent = content[currentSectionKey];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{lesson.title}</h1>
              <p className="text-gray-600 mt-1">{lesson.objectives}</p>
            </div>
            <button
              onClick={() => navigate(`/student/courses/${courseId}`)}
              className="text-gray-500 hover:text-gray-700"
            >
              <ChevronLeftIcon className="h-6 w-6" />
            </button>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-6">
          {currentContent && renderContent(currentSectionKey, currentContent)}
        </div>
        
        {/* Navigation */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
          <button
            onClick={prevSection}
            disabled={currentSection === 0}
            className="flex items-center px-4 py-2 text-gray-600 disabled:text-gray-400 disabled:cursor-not-allowed"
          >
            <ChevronLeftIcon className="h-5 w-5 mr-1" />
            Previous
          </button>
          
          <span className="text-sm text-gray-500">
            {currentSection + 1} of {getTotalSections()}
          </span>
          
          <button
            onClick={nextSection}
            disabled={currentSection >= getTotalSections() - 1}
            className="flex items-center px-4 py-2 text-blue-600 disabled:text-gray-400 disabled:cursor-not-allowed"
          >
            Next
            <ChevronRightIcon className="h-5 w-5 ml-1" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default LessonPlayer;

// client/src/components/student/ExerciseComponent.jsx
import React, { useState } from 'react';
import api from '../../services/api';
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';

const ExerciseComponent = ({ exercise, exerciseIndex, lessonId }) => {
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!selectedAnswer) return;
    
    setLoading(true);
    try {
      const response = await api.post(`/student/lessons/${lessonId}/exercises/${exerciseIndex}`, {
        answer: selectedAnswer
      });
      
      setFeedback(response.data);
      setSubmitted(true);
    } catch (error) {
      console.error('Error submitting exercise:', error);
    } finally {
      setLoading(false);
    }
  };

  const resetExercise = () => {
    setSelectedAnswer('');
    setSubmitted(false);
    setFeedback(null);
  };

  const renderExercise = () => {
    switch (exercise.type) {
      case 'multiple_choice':
        return (
          <div className="space-y-3">
            <p className="font-medium">{exercise.question}</p>
            <div className="space-y-2">
              {exercise.options?.map((option, index) => (
                <label key={index} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name={`exercise-${exerciseIndex}`}
                    value={option}
                    checked={selectedAnswer === option}
                    onChange={(e) => setSelectedAnswer(e.target.value)}
                    disabled={submitted}
                    className="text-blue-600"
                  />
                  <span className={submitted && option === exercise.correct_answer ? 'text-green-600 font-medium' : ''}>{option}</span>
                  {submitted && option === exercise.correct_answer && (
                    <CheckIcon className="h-4 w-4 text-green-600" />
                  )}
                  {submitted && option === selectedAnswer && option !== exercise.correct_answer && (
                    <XMarkIcon className="h-4 w-4 text-red-600" />
                  )}
                </label>
              ))}
            </div>
          </div>
        );
      
      case 'fill_blank':
        return (
          <div className="space-y-3">
            <p className="font-medium">{exercise.question}</p>
            <input
              type="text"
              value={selectedAnswer}
              onChange={(e) => setSelectedAnswer(e.target.value)}
              disabled={submitted}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
              placeholder="Type your answer here..."
            />
          </div>
        );
      
      case 'short_answer':
        return (
          <div className="space-y-3">
            <p className="font-medium">{exercise.question}</p>
            <textarea
              value={selectedAnswer}
              onChange={(e) => setSelectedAnswer(e.target.value)}
              disabled={submitted}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
              placeholder="Write your answer here..."
            />
          </div>
        );
      
      default:
        return (
          <div className="space-y-3">
            <p className="font-medium">{exercise.question}</p>
            <p className="text-gray-600">Exercise type not supported yet.</p>
          </div>
        );
    }
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      {renderExercise()}
      
      {/* Action Buttons */}
      <div className="mt-4 flex justify-between items-center">
        {!submitted ? (
          <button
            onClick={handleSubmit}
            disabled={!selectedAnswer || loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Submitting...' : 'Submit Answer'}
          </button>
        ) : (
          <button
            onClick={resetExercise}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            Try Again
          </button>
        )}
      </div>
      
      {/* Feedback */}
      {feedback && (
        <div className={`mt-4 p-3 rounded-md ${feedback.correct ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
          <div className="flex items-center">
            {feedback.correct ? (
              <CheckIcon className="h-5 w-5 text-green-600 mr-2" />
            ) : (
              <XMarkIcon className="h-5 w-5 text-red-600 mr-2" />
            )}
            <span className={`font-medium ${feedback.correct ? 'text-green-800' : 'text-red-800'}`}>
              {feedback.correct ? 'Correct!' : 'Incorrect'}
            </span>
          </div>
          {feedback.explanation && (
            <p className={`mt-2 text-sm ${feedback.correct ? 'text-green-700' : 'text-red-700'}`}>
              {feedback.explanation}
            </p>
          )}
          {feedback.ai_feedback && (
            <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded">
              <p className="text-sm text-blue-700">
                <strong>AI Feedback:</strong> {feedback.ai_feedback}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ExerciseComponent;

// client/src/pages/trainer/StudentsPage.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import Layout from '../../components/layout/Layout';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  UserIcon, 
  ChartBarIcon,
  ClockIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline';

const StudentsPage = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCourse, setFilterCourse] = useState('all');
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    fetchStudents();
    fetchCourses();
  }, []);

  const fetchStudents = async () => {
    try {
      const response = await api.get('/trainer/students');
      setStudents(response.data.students || []);
    } catch (error) {
      console.error('Error fetching students:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCourses = async () => {
    try {
      const response = await api.get('/trainer/courses');
      setCourses(response.data.courses || []);
    } catch (error) {
      console.error('Error fetching courses:', error);
    }
  };

  const filteredStudents = students.filter(student => {
    const matchesSearch = student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         student.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCourse = filterCourse === 'all' || student.course_id === parseInt(filterCourse);
    return matchesSearch && matchesCourse;
  });

  const getProgressColor = (progress) => {
    if (progress >= 80) return 'text-green-600';
    if (progress >= 50) return 'text-blue-600';
    if (progress >= 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProgressBgColor = (progress) => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 50) return 'bg-blue-500';
    if (progress >= 20) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <Layout>
        <LoadingSpinner text="Loading students..." />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">My Students</h1>
          <div className="text-sm text-gray-500">
            {filteredStudents.length} students
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Students
              </label>
              <input
                type="text"
                placeholder="Search by name or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Course
              </label>
              <select
                value={filterCourse}
                onChange={(e) => setFilterCourse(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Courses</option>
                {courses.map(course => (
                  <option key={course.id} value={course.id}>
                    {course.title}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Students Grid */}
        {filteredStudents.length === 0 ? (
          <div className="text-center py-12">
            <UserIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No students found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || filterCourse !== 'all' 
                ? "Try adjusting your search or filter criteria." 
                : "You don't have any students assigned yet."
              }
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredStudents.map((student) => (
              <div key={student.id} className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
                <div className="p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-12 w-12 bg-gray-200 rounded-full flex items-center justify-center">
                        <UserIcon className="h-6 w-6 text-gray-600" />
                      </div>
                    </div>
                    <div className="ml-4 flex-1">
                      <h3 className="text-lg font-medium text-gray-900">
                        {student.name}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {student.email}
                      </p>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                      <span>Course Progress</span>
                      <span className={`font-medium ${getProgressColor(student.progress || 0)}`}>
                        {Math.round(student.progress || 0)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${getProgressBgColor(student.progress || 0)}`}
                        style={{ width: `${student.progress || 0}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center text-gray-600">
                      <AcademicCapIcon className="h-4 w-4 mr-1" />
                      <span>{student.completed_lessons || 0}/{student.total_lessons || 0} lessons</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <ChartBarIcon className="h-4 w-4 mr-1" />
                      <span>{student.average_score || 0}% avg</span>
                    </div>
                  </div>
                  
                  <div className="mt-4 text-sm text-gray-500">
                    <p><strong>Course:</strong> {student.course_title}</p>
                    {student.last_activity && (
                      <p><strong>Last Activity:</strong> {new Date(student.last_activity).toLocaleDateString()}</p>
                    )}
                  </div>
                  
                  <div className="mt-6">
                    <Link
                      to={`/trainer/students/${student.id}`}
                      className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                    >
                      View Details
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default StudentsPage;

// client/src/components/common/ErrorBoundary.jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // Log error to monitoring service
    console.error('Error Boundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
            <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div className="mt-4 text-center">
              <h3 className="text-lg font-medium text-gray-900">Something went wrong</h3>
              <p className="mt-2 text-sm text-gray-500">
                We're sorry, but something unexpected happened. Please try refreshing the page.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => window.location.reload()}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Refresh Page
                </button>
              </div>
              {process.env.NODE_ENV === 'development' && (
                <details className="mt-4 text-left">
                  <summary className="cursor-pointer text-sm text-gray-500">Error Details</summary>
                  <pre className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded overflow-auto">
                    {this.state.error && this.state.error.toString()}
                    <br />
                    {this.state.errorInfo.componentStack}
                  </pre>
                </details>
              )}
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

// client/src/hooks/useNotifications.js
import { useState, useEffect } from 'react';
import api from '../services/api';

export const useNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await api.get('/common/notifications');
      setNotifications(response.data.notifications || []);
      setUnreadCount(response.data.notifications?.filter(n => !n.read).length || 0);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await api.post(`/common/notifications/${notificationId}/read`);
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.post('/common/notifications/mark-all-read');
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  return {
    notifications,
    unreadCount,
    loading,
    fetchNotifications,
    markAsRead,
    markAllAsRead
  };
};
