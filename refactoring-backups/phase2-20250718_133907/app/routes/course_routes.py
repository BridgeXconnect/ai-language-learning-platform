from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from app.database import get_db
from app.services.course_service import CourseService, ModuleService, LessonService
from app.services.auth_service import AuthService
from app.schemas.course import (
    CourseCreateRequest,
    CourseUpdateRequest,
    CourseResponse,
    CourseDetailResponse,
    CourseReviewRequest,
    ModuleCreateRequest,
    ModuleResponse,
    LessonCreateRequest,
    LessonResponse
)

router = APIRouter(prefix="/courses", tags=["courses"])
security = HTTPBearer()

@router.get("/", response_model=List[CourseResponse])
async def get_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None),
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = AuthService.get_current_user(db, token.credentials)
    
    # Filter by user role
    created_by = None
    if user.roles and not any(role.name in ['admin', 'course_manager'] for role in user.roles):
        created_by = user.id
    
    courses = CourseService.get_courses(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        created_by=created_by
    )
    
    return courses

@router.post("/", response_model=CourseResponse)
async def create_course(
    request: CourseCreateRequest,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = AuthService.get_current_user(db, token.credentials)
    
    try:
        course = CourseService.create_course(
            db=db,
            title=request.title,
            description=request.description,
            cefr_level=request.cefr_level,
            created_by=user.id
        )
        return course
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{course_id}", response_model=CourseDetailResponse)
async def get_course(
    course_id: int,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = AuthService.get_current_user(db, token.credentials)
    course = CourseService.get_course_by_id(db, course_id)
    
    if not course:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Course not found")
    
    # Check permissions
    if (course.created_by != user.id and 
        not any(role.name in ['admin', 'course_manager'] for role in user.roles)):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
    
    return course

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    request: CourseUpdateRequest,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = AuthService.get_current_user(db, token.credentials)
    course = CourseService.get_course_by_id(db, course_id)
    
    if not course:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Course not found")
    
    # Check permissions
    if (course.created_by != user.id and 
        not any(role.name in ['admin', 'course_manager'] for role in user.roles)):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
    
    try:
        updated_course = CourseService.update_course(
            db=db,
            course_id=course_id,
            update_data=request.dict(exclude_unset=True)
        )
        return updated_course
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = AuthService.get_current_user(db, token.credentials)
    course = CourseService.get_course_by_id(db, course_id)
    
    if not course:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Course not found")
    
    # Check permissions
    if (course.created_by != user.id and 
        not any(role.name in ['admin', 'course_manager'] for role in user.roles)):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
    
    success = CourseService.delete_course(db, course_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete course")
    
    return {"message": "Course deleted successfully"}

@router.post("/{course_id}/submit")
async def submit_course_for_review(
    course_id: int,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = AuthService.get_current_user(db, token.credentials)
    course = CourseService.get_course_by_id(db, course_id)
    
    if not course:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Course not found")
    
    # Check permissions
    if course.created_by != user.id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
    
    success = CourseService.submit_for_review(db, course_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to submit course for review")
    
    return {"message": "Course submitted for review"}

@router.post("/{course_id}/review")
async def review_course(
    course_id: int,
    request: CourseReviewRequest,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = AuthService.get_current_user(db, token.credentials)
    
    # Check if user has review permissions
    if not any(role.name in ['admin', 'course_manager'] for role in user.roles):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    course = CourseService.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Course not found")
    
    if request.status == 'approved':
        success = CourseService.approve_course(
            db=db,
            course_id=course_id,
            reviewer_id=user.id,
            feedback=request.feedback
        )
    else:
        if not request.feedback:
            raise HTTPException(status_code=400, detail="Feedback is required for rejection")
        success = CourseService.reject_course(
            db=db,
            course_id=course_id,
            reviewer_id=user.id,
            feedback=request.feedback
        )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to review course")
    
    return {"message": f"Course {request.status} successfully"}

# Module routes
@router.get("/{course_id}/modules", response_model=List[ModuleResponse])
async def get_course_modules(
    course_id: int,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = AuthService.get_current_user(db, token.credentials)
    course = CourseService.get_course_by_id(db, course_id)
    
    if not course:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Course not found")
    
    modules = ModuleService.get_modules_by_course(db, course_id)
    return modules

@router.post("/{course_id}/modules", response_model=ModuleResponse)
async def create_module(
    course_id: int,
    request: ModuleCreateRequest,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = AuthService.get_current_user(db, token.credentials)
    course = CourseService.get_course_by_id(db, course_id)
    
    if not course:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Course not found")
    
    # Check permissions
    if (course.created_by != user.id and 
        not any(role.name in ['admin', 'course_manager'] for role in user.roles)):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
    
    try:
        module = ModuleService.create_module(
            db=db,
            course_id=course_id,
            title=request.title,
            description=request.description,
            sequence_number=request.sequence_number
        )
        return module
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Lesson routes
@router.get("/modules/{module_id}/lessons", response_model=List[LessonResponse])
async def get_module_lessons(
    module_id: int,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = AuthService.get_current_user(db, token.credentials)
    lessons = LessonService.get_lessons_by_module(db, module_id)
    return lessons

@router.post("/modules/{module_id}/lessons", response_model=LessonResponse)
async def create_lesson(
    module_id: int,
    request: LessonCreateRequest,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = AuthService.get_current_user(db, token.credentials)
    
    try:
        lesson = LessonService.create_lesson(
            db=db,
            module_id=module_id,
            title=request.title,
            content_id=request.content_id,
            sequence_number=request.sequence_number,
            duration_minutes=request.duration_minutes
        )
        return lesson
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 