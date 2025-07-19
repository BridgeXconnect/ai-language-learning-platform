from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.domains.courses.models import Course, Module, Lesson, CourseReview, Exercise, Assessment
from app.domains.auth.models import User
from datetime import datetime

class CourseService:
    @staticmethod
    def create_course(
        db: Session,
        title: str,
        description: str,
        cefr_level: str,
        created_by: int
    ) -> Course:
        course = Course(
            title=title,
            description=description,
            cefr_level=cefr_level,
            created_by=created_by,
            status='draft'
        )
        
        try:
            db.add(course)
            db.commit()
            db.refresh(course)
            return course
        except IntegrityError:
            db.rollback()
            raise ValueError("Failed to create course")

    @staticmethod
    def get_course_by_id(db: Session, course_id: int) -> Optional[Course]:
        return db.query(Course).filter(Course.id == course_id).first()

    @staticmethod
    def get_courses(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        created_by: Optional[int] = None
    ) -> List[Course]:
        query = db.query(Course)
        
        if status:
            query = query.filter(Course.status == status)
        if created_by:
            query = query.filter(Course.created_by == created_by)
            
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_course(
        db: Session,
        course_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Course]:
        course = CourseService.get_course_by_id(db, course_id)
        if not course:
            return None
            
        for key, value in update_data.items():
            if hasattr(course, key):
                setattr(course, key, value)
        
        course.updated_at = datetime.utcnow()
        
        try:
            db.commit()
            db.refresh(course)
            return course
        except IntegrityError:
            db.rollback()
            raise ValueError("Update failed")

    @staticmethod
    def delete_course(db: Session, course_id: int) -> bool:
        course = CourseService.get_course_by_id(db, course_id)
        if not course:
            return False
            
        try:
            db.delete(course)
            db.commit()
            return True
        except:
            db.rollback()
            return False

    @staticmethod
    def submit_for_review(db: Session, course_id: int) -> bool:
        course = CourseService.get_course_by_id(db, course_id)
        if not course or course.status != 'draft':
            return False
            
        course.status = 'pending_review'
        course.updated_at = datetime.utcnow()
        
        try:
            db.commit()
            return True
        except:
            db.rollback()
            return False

    @staticmethod
    def approve_course(
        db: Session,
        course_id: int,
        reviewer_id: int,
        feedback: Optional[str] = None
    ) -> bool:
        course = CourseService.get_course_by_id(db, course_id)
        if not course or course.status != 'pending_review':
            return False
            
        # Update course status
        course.status = 'approved'
        course.approved_by = reviewer_id
        course.updated_at = datetime.utcnow()
        
        # Create review record
        review = CourseReview(
            course_id=course_id,
            reviewer_id=reviewer_id,
            status='approved',
            feedback=feedback
        )
        
        try:
            db.add(review)
            db.commit()
            return True
        except:
            db.rollback()
            return False

    @staticmethod
    def reject_course(
        db: Session,
        course_id: int,
        reviewer_id: int,
        feedback: str
    ) -> bool:
        course = CourseService.get_course_by_id(db, course_id)
        if not course or course.status != 'pending_review':
            return False
            
        # Update course status
        course.status = 'rejected'
        course.updated_at = datetime.utcnow()
        
        # Create review record
        review = CourseReview(
            course_id=course_id,
            reviewer_id=reviewer_id,
            status='rejected',
            feedback=feedback
        )
        
        try:
            db.add(review)
            db.commit()
            return True
        except:
            db.rollback()
            return False

class ModuleService:
    @staticmethod
    def create_module(
        db: Session,
        course_id: int,
        title: str,
        description: str,
        sequence_number: int
    ) -> Module:
        module = Module(
            course_id=course_id,
            title=title,
            description=description,
            sequence_number=sequence_number
        )
        
        try:
            db.add(module)
            db.commit()
            db.refresh(module)
            return module
        except IntegrityError:
            db.rollback()
            raise ValueError("Failed to create module")

    @staticmethod
    def get_modules_by_course(db: Session, course_id: int) -> List[Module]:
        return db.query(Module).filter(
            Module.course_id == course_id
        ).order_by(Module.sequence_number).all()

    @staticmethod
    def update_module(
        db: Session,
        module_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Module]:
        module = db.query(Module).filter(Module.id == module_id).first()
        if not module:
            return None
            
        for key, value in update_data.items():
            if hasattr(module, key):
                setattr(module, key, value)
        
        try:
            db.commit()
            db.refresh(module)
            return module
        except IntegrityError:
            db.rollback()
            raise ValueError("Update failed")

class LessonService:
    @staticmethod
    def create_lesson(
        db: Session,
        module_id: int,
        title: str,
        content_id: str,
        sequence_number: int,
        duration_minutes: Optional[int] = None
    ) -> Lesson:
        lesson = Lesson(
            module_id=module_id,
            title=title,
            content_id=content_id,
            sequence_number=sequence_number,
            duration_minutes=duration_minutes
        )
        
        try:
            db.add(lesson)
            db.commit()
            db.refresh(lesson)
            return lesson
        except IntegrityError:
            db.rollback()
            raise ValueError("Failed to create lesson")

    @staticmethod
    def get_lessons_by_module(db: Session, module_id: int) -> List[Lesson]:
        return db.query(Lesson).filter(
            Lesson.module_id == module_id
        ).order_by(Lesson.sequence_number).all()

    @staticmethod
    def update_lesson(
        db: Session,
        lesson_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Lesson]:
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            return None
            
        for key, value in update_data.items():
            if hasattr(lesson, key):
                setattr(lesson, key, value)
        
        try:
            db.commit()
            db.refresh(lesson)
            return lesson
        except IntegrityError:
            db.rollback()
            raise ValueError("Update failed") 