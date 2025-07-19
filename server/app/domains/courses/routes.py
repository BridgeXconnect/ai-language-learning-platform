"""
Courses Domain - Routes
Consolidated from: course_routes.py
"""

from app.core.database import get_db
from app.domains.courses.schemas import (
from app.domains.auth.services import AuthService
from app.domains.courses.services import CourseService, ModuleService, LessonService
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from typing import List, Optional
