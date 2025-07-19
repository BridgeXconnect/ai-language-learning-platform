"""
Main FastAPI Application for AI Language Learning Platform
Created by: James (BMAD Developer)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.database.database import engine, Base
from app.routes.auth_routes_v2 import router as auth_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AI Language Learning Platform...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Language Learning Platform...")

# Create FastAPI application
app = FastAPI(
    title="AI Language Learning Platform",
    description="A comprehensive AI-powered language learning platform with course creation, assessment, and personalized tutoring.",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
    )

# Include routers
app.include_router(auth_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with platform information"""
    return {
        "message": "AI Language Learning Platform API",
        "version": "2.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-language-learning-platform",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT
    }

# API information endpoint
@app.get("/api/info")
async def api_info():
    """API information and available endpoints"""
    return {
        "name": "AI Language Learning Platform API",
        "version": "2.0.0",
        "description": "Comprehensive AI-powered language learning platform",
        "endpoints": {
            "authentication": "/api/v1/auth",
            "courses": "/api/v1/courses",
            "assessments": "/api/v1/assessments",
            "ai": "/api/v1/ai",
            "progress": "/api/v1/progress"
        },
        "features": [
            "User authentication and authorization",
            "AI-powered course creation",
            "Interactive assessments",
            "Personalized learning paths",
            "Real-time AI tutoring",
            "Progress tracking and analytics"
        ]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return {
        "error": "Not Found",
        "message": "The requested resource was not found",
        "path": str(request.url.path)
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal Server Error",
        "message": "An internal server error occurred"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level="info"
    ) 