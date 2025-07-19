"""
Simplified FastAPI application for testing.
This bypasses complex domain models to test basic server functionality.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.database import engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Language Learning Platform - Simplified Version"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for dev; adjust in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting AI Language Learning Platform...")
    logger.info("Startup complete (database init skipped in simplified mode)")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Language Learning Platform API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running"
    }

@app.get("/health/simple")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
async def health_root():
    """Health endpoint for legacy frontend."""
    return await health_check()

# Explicit OPTIONS handler to satisfy browser CORS preflight for /health
@app.options("/health")
async def health_options():
    return {
        "status": "ok"
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint."""
    return {
        "api": "running",
        "database": "connected",
        "ai_services": {
            "openai": "configured" if settings.OPENAI_API_KEY else "not_configured",
            "anthropic": "configured" if settings.ANTHROPIC_API_KEY else "not_configured"
        }
    }

@app.get("/test/ai")
async def test_ai():
    """Test AI services configuration."""
    return {
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "anthropic_configured": bool(settings.ANTHROPIC_API_KEY),
        "message": "AI services configuration test"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 