"""
AI Domain - Cache Routes
Redis cache management and monitoring endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.domains.auth.services import get_current_user
from app.domains.auth.models import User
from app.services.redis_cache_service import (
    redis_cache,
    ai_content_cache,
    cache_performance_monitor
)
from app.domains.ai.services.core import ai_service
from app.domains.ai.services.content import AIContentService
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/ai/cache", tags=["AI Cache"])

@router.get("/status")
async def get_cache_status(current_user: User = Depends(get_current_user)):
    """Get Redis cache status and basic statistics."""
    
    try:
        cache_stats = redis_cache.get_stats()
        memory_usage = redis_cache.get_memory_usage()
        
        return {
            "success": True,
            "cache_available": redis_cache.is_available(),
            "cache_stats": cache_stats,
            "memory_usage": memory_usage,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get cache status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache status: {str(e)}")

@router.get("/performance")
async def get_cache_performance(current_user: User = Depends(get_current_user)):
    """Get comprehensive cache performance metrics."""
    
    try:
        # Record current performance
        cache_performance_monitor.record_performance()
        
        # Get performance insights
        insights = cache_performance_monitor.get_performance_insights()
        
        # Get AI content cache performance
        ai_performance = ai_content_cache.get_cache_performance()
        
        return {
            "success": True,
            "cache_performance": {
                "redis_cache": redis_cache.get_stats(),
                "ai_content_cache": ai_performance,
                "performance_insights": insights
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get cache performance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache performance: {str(e)}")

@router.get("/metrics")
async def get_cache_metrics(current_user: User = Depends(get_current_user)):
    """Get detailed cache metrics for monitoring."""
    
    try:
        stats = redis_cache.get_stats()
        memory_usage = redis_cache.get_memory_usage()
        
        # Calculate advanced metrics
        total_requests = stats["cache_stats"]["total_requests"]
        hit_rate = stats["cache_stats"]["hit_rate_percent"]
        
        return {
            "success": True,
            "metrics": {
                "cache_available": redis_cache.is_available(),
                "hit_rate_percent": hit_rate,
                "total_requests": total_requests,
                "cache_hits": stats["cache_stats"]["hits"],
                "cache_misses": stats["cache_stats"]["misses"],
                "cache_sets": stats["cache_stats"]["sets"],
                "cache_errors": stats["cache_stats"]["errors"],
                "memory_usage": memory_usage,
                "ttl_settings": stats["ttl_settings"],
                "redis_info": stats["redis_info"]
            },
            "performance_grade": (
                "excellent" if hit_rate >= 80 else
                "good" if hit_rate >= 60 else
                "needs_improvement"
            ),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get cache metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache metrics: {str(e)}")

@router.post("/clear")
async def clear_cache(
    pattern: str = "*",
    current_user: User = Depends(get_current_user)
):
    """Clear cache entries matching pattern."""
    
    # Check if user has admin permissions
    if not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        deleted_count = redis_cache.clear_pattern(pattern)
        
        logger.info(f"Cache cleared by user {current_user.username}: {deleted_count} entries deleted with pattern '{pattern}'")
        
        return {
            "success": True,
            "message": f"Cache cleared successfully",
            "deleted_entries": deleted_count,
            "pattern": pattern,
            "cleared_by": current_user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@router.post("/clear/ai-content")
async def clear_ai_content_cache(
    company_name: Optional[str] = None,
    industry: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Clear AI content cache for specific company/industry or all AI content."""
    
    # Check if user has admin permissions
    if not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if company_name and industry:
            # Clear specific company/industry cache
            deleted_count = ai_content_cache.invalidate_course_cache(company_name, industry)
            message = f"AI content cache cleared for {company_name} in {industry}"
        else:
            # Clear all AI content cache
            patterns = [
                "lesson_content:*",
                "course_curriculum:*",
                "exercises:*",
                "assessment:*",
                "adaptive_quiz:*",
                "learning_path:*"
            ]
            deleted_count = sum(redis_cache.clear_pattern(pattern) for pattern in patterns)
            message = "All AI content cache cleared"
        
        logger.info(f"AI content cache cleared by user {current_user.username}: {deleted_count} entries deleted")
        
        return {
            "success": True,
            "message": message,
            "deleted_entries": deleted_count,
            "cleared_by": current_user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to clear AI content cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear AI content cache: {str(e)}")

@router.post("/warm-up")
async def warm_up_cache(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Warm up cache with common AI operations."""
    
    # Check if user has admin permissions
    if not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Add background task to warm up cache
        background_tasks.add_task(warm_up_ai_cache)
        
        logger.info(f"Cache warm-up initiated by user {current_user.username}")
        
        return {
            "success": True,
            "message": "Cache warm-up initiated",
            "initiated_by": current_user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to initiate cache warm-up: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initiate cache warm-up: {str(e)}")

@router.get("/health")
async def get_cache_health():
    """Get cache health status for monitoring systems."""
    
    try:
        is_available = redis_cache.is_available()
        stats = redis_cache.get_stats() if is_available else {}
        
        # Determine health status
        if not is_available:
            health_status = "unhealthy"
        else:
            hit_rate = stats.get("cache_stats", {}).get("hit_rate_percent", 0)
            if hit_rate >= 70:
                health_status = "healthy"
            elif hit_rate >= 50:
                health_status = "degraded"
            else:
                health_status = "unhealthy"
        
        return {
            "status": health_status,
            "cache_available": is_available,
            "hit_rate_percent": stats.get("cache_stats", {}).get("hit_rate_percent", 0),
            "total_requests": stats.get("cache_stats", {}).get("total_requests", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/config")
async def get_cache_config(current_user: User = Depends(get_current_user)):
    """Get cache configuration settings."""
    
    try:
        return {
            "success": True,
            "config": {
                "default_ttl": redis_cache.default_ttl,
                "ai_content_ttl": redis_cache.ai_content_ttl,
                "course_curriculum_ttl": redis_cache.course_curriculum_ttl,
                "lesson_content_ttl": redis_cache.lesson_content_ttl,
                "exercise_cache_ttl": redis_cache.exercise_cache_ttl,
                "assessment_cache_ttl": redis_cache.assessment_cache_ttl,
                "cache_available": redis_cache.is_available()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get cache config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache config: {str(e)}")

@router.post("/config/update")
async def update_cache_config(
    default_ttl: Optional[int] = None,
    ai_content_ttl: Optional[int] = None,
    course_curriculum_ttl: Optional[int] = None,
    lesson_content_ttl: Optional[int] = None,
    exercise_cache_ttl: Optional[int] = None,
    assessment_cache_ttl: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """Update cache configuration settings."""
    
    # Check if user has admin permissions
    if not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        updated_settings = {}
        
        if default_ttl is not None:
            redis_cache.default_ttl = default_ttl
            updated_settings["default_ttl"] = default_ttl
            
        if ai_content_ttl is not None:
            redis_cache.ai_content_ttl = ai_content_ttl
            updated_settings["ai_content_ttl"] = ai_content_ttl
            
        if course_curriculum_ttl is not None:
            redis_cache.course_curriculum_ttl = course_curriculum_ttl
            updated_settings["course_curriculum_ttl"] = course_curriculum_ttl
            
        if lesson_content_ttl is not None:
            redis_cache.lesson_content_ttl = lesson_content_ttl
            updated_settings["lesson_content_ttl"] = lesson_content_ttl
            
        if exercise_cache_ttl is not None:
            redis_cache.exercise_cache_ttl = exercise_cache_ttl
            updated_settings["exercise_cache_ttl"] = exercise_cache_ttl
            
        if assessment_cache_ttl is not None:
            redis_cache.assessment_cache_ttl = assessment_cache_ttl
            updated_settings["assessment_cache_ttl"] = assessment_cache_ttl
        
        logger.info(f"Cache configuration updated by user {current_user.username}: {updated_settings}")
        
        return {
            "success": True,
            "message": "Cache configuration updated",
            "updated_settings": updated_settings,
            "updated_by": current_user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to update cache config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update cache config: {str(e)}")

@router.get("/keys")
async def get_cache_keys(
    pattern: str = "*",
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get cache keys matching pattern (admin only)."""
    
    # Check if user has admin permissions
    if not current_user.has_permission("system_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if not redis_cache.is_available():
            raise HTTPException(status_code=503, detail="Redis cache not available")
        
        # Get keys matching pattern
        keys = redis_cache.redis_client.keys(pattern)
        
        # Limit results
        if len(keys) > limit:
            keys = keys[:limit]
            truncated = True
        else:
            truncated = False
        
        return {
            "success": True,
            "keys": keys,
            "total_found": len(keys),
            "truncated": truncated,
            "limit": limit,
            "pattern": pattern,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get cache keys: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache keys: {str(e)}")

async def warm_up_ai_cache():
    """Background task to warm up AI cache with common operations."""
    
    logger.info("Starting AI cache warm-up process")
    
    try:
        # Sample data for warming up cache
        sample_data = [
            {
                "topic": "Business Communication",
                "difficulty": "intermediate",
                "learning_objectives": ["Improve email writing", "Enhance presentation skills"]
            },
            {
                "topic": "Technical English",
                "difficulty": "advanced",
                "learning_objectives": ["Technical documentation", "Process description"]
            },
            {
                "topic": "Customer Service",
                "difficulty": "beginner",
                "learning_objectives": ["Basic customer interaction", "Problem resolution"]
            }
        ]
        
        # Initialize AI content service
        ai_content_service = AIContentService()
        
        # Warm up with sample lesson content
        for data in sample_data:
            try:
                await ai_content_service.generate_lesson_content(
                    topic=data["topic"],
                    difficulty=data["difficulty"],
                    learning_objectives=data["learning_objectives"]
                )
                logger.info(f"Cache warmed up for lesson: {data['topic']}")
            except Exception as e:
                logger.warning(f"Failed to warm up cache for {data['topic']}: {e}")
        
        logger.info("AI cache warm-up process completed")
        
    except Exception as e:
        logger.error(f"AI cache warm-up failed: {e}")

# Add cache monitoring middleware
@router.middleware("http")
async def cache_monitoring_middleware(request, call_next):
    """Monitor cache performance for AI requests."""
    
    # Record request start time
    start_time = datetime.utcnow()
    
    # Process request
    response = await call_next(request)
    
    # Record performance if this was an AI request
    if "/ai/" in str(request.url):
        cache_performance_monitor.record_performance()
    
    return response

logger.info("AI Cache routes initialized with Redis caching and monitoring")