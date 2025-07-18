from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
import time

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify server and database connectivity
    """
    start_time = time.time()
    
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    response_time = round((time.time() - start_time) * 1000, 2)
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": int(time.time()),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "response_time_ms": response_time,
        "cors_origins": settings.cors_origins_list
    }

@router.get("/health/simple")
async def simple_health_check():
    """
    Simple health check that doesn't require database
    """
    return {
        "status": "healthy",
        "timestamp": int(time.time()),
        "message": "Server is running"
    }