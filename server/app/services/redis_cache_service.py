"""
Redis Caching Service for AI Content Creator Agent
High-performance caching for AI responses and expensive operations
"""

import redis
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from functools import wraps
from app.core.config import settings
import asyncio
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisCache:
    """Redis-based caching service for AI operations."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = None
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "errors": 0,
            "total_requests": 0
        }
        self.default_ttl = 3600  # 1 hour default
        self.ai_content_ttl = 7200  # 2 hours for AI content
        self.course_curriculum_ttl = 14400  # 4 hours for course curriculum
        self.lesson_content_ttl = 7200  # 2 hours for lesson content
        self.exercise_cache_ttl = 3600  # 1 hour for exercises
        self.assessment_cache_ttl = 7200  # 2 hours for assessments
        self.performance_metrics = {
            "cache_hit_rate": 0.0,
            "average_response_time": 0.0,
            "cache_memory_usage": 0
        }
        
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection with error handling."""
        try:
            # Use Redis URL from settings or default
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Check if Redis is available."""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate a consistent cache key from parameters."""
        # Create a sorted string of parameters
        params_str = json.dumps(kwargs, sort_keys=True)
        # Generate hash for consistent key length
        param_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{param_hash}"
    
    def _serialize_data(self, data: Any) -> str:
        """Serialize data for Redis storage."""
        cache_object = {
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "type": type(data).__name__
        }
        return json.dumps(cache_object)
    
    def _deserialize_data(self, cached_data: str) -> Any:
        """Deserialize data from Redis."""
        try:
            cache_object = json.loads(cached_data)
            return cache_object["data"]
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to deserialize cached data: {e}")
            return None
    
    def get(self, key: str) -> Optional[Any]:
        """Get data from cache."""
        if not self.is_available():
            return None
        
        start_time = time.time()
        self.cache_stats["total_requests"] += 1
        
        try:
            cached_data = self.redis_client.get(key)
            response_time = time.time() - start_time
            
            if cached_data:
                self.cache_stats["hits"] += 1
                data = self._deserialize_data(cached_data)
                logger.info(f"Cache HIT for key: {key[:50]}... (response time: {response_time:.3f}s)")
                return data
            else:
                self.cache_stats["misses"] += 1
                logger.info(f"Cache MISS for key: {key[:50]}...")
                return None
                
        except Exception as e:
            self.cache_stats["errors"] += 1
            logger.error(f"Cache GET error for key {key[:50]}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set data in cache."""
        if not self.is_available():
            return False
        
        if ttl is None:
            ttl = self.default_ttl
        
        try:
            serialized_data = self._serialize_data(value)
            result = self.redis_client.setex(key, ttl, serialized_data)
            
            if result:
                self.cache_stats["sets"] += 1
                logger.info(f"Cache SET successful for key: {key[:50]}... (TTL: {ttl}s)")
                return True
            else:
                self.cache_stats["errors"] += 1
                return False
                
        except Exception as e:
            self.cache_stats["errors"] += 1
            logger.error(f"Cache SET error for key {key[:50]}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete data from cache."""
        if not self.is_available():
            return False
        
        try:
            result = self.redis_client.delete(key)
            logger.info(f"Cache DELETE for key: {key[:50]}...")
            return result > 0
        except Exception as e:
            logger.error(f"Cache DELETE error for key {key[:50]}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.is_available():
            return False
        
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache EXISTS error for key {key[:50]}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        # Calculate hit rate
        total_gets = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_gets * 100) if total_gets > 0 else 0
        
        # Get Redis info if available
        redis_info = {}
        if self.is_available():
            try:
                info = self.redis_client.info()
                redis_info = {
                    "used_memory": info.get("used_memory_human", "N/A"),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0)
                }
            except Exception as e:
                logger.error(f"Failed to get Redis info: {e}")
        
        return {
            "cache_available": self.is_available(),
            "cache_stats": {
                **self.cache_stats,
                "hit_rate_percent": round(hit_rate, 2)
            },
            "redis_info": redis_info,
            "ttl_settings": {
                "default_ttl": self.default_ttl,
                "ai_content_ttl": self.ai_content_ttl,
                "course_curriculum_ttl": self.course_curriculum_ttl,
                "lesson_content_ttl": self.lesson_content_ttl,
                "exercise_cache_ttl": self.exercise_cache_ttl,
                "assessment_cache_ttl": self.assessment_cache_ttl
            }
        }
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching a pattern."""
        if not self.is_available():
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} keys matching pattern: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error clearing pattern {pattern}: {e}")
            return 0
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get cache memory usage statistics."""
        if not self.is_available():
            return {"available": False}
        
        try:
            info = self.redis_client.info("memory")
            return {
                "available": True,
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "N/A"),
                "used_memory_peak": info.get("used_memory_peak", 0),
                "used_memory_peak_human": info.get("used_memory_peak_human", "N/A"),
                "maxmemory": info.get("maxmemory", 0),
                "maxmemory_human": info.get("maxmemory_human", "N/A")
            }
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return {"available": False, "error": str(e)}

# Global cache instance
redis_cache = RedisCache()

# AI Content Caching Decorators
def cache_ai_content(cache_key_prefix: str, ttl: Optional[int] = None):
    """Decorator to cache AI content generation results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = redis_cache._generate_cache_key(cache_key_prefix, **kwargs)
            
            # Try to get from cache first
            cached_result = redis_cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Returning cached result for {func.__name__}")
                return cached_result
            
            # Not in cache, call the function
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Cache the result
            cache_ttl = ttl or redis_cache.ai_content_ttl
            if redis_cache.set(cache_key, result, cache_ttl):
                logger.info(f"Cached result for {func.__name__} (execution time: {execution_time:.3f}s)")
            
            return result
        return wrapper
    return decorator

def cache_course_curriculum(ttl: Optional[int] = None):
    """Decorator specifically for course curriculum caching."""
    cache_ttl = ttl or redis_cache.course_curriculum_ttl
    return cache_ai_content("course_curriculum", cache_ttl)

def cache_lesson_content(ttl: Optional[int] = None):
    """Decorator specifically for lesson content caching."""
    cache_ttl = ttl or redis_cache.lesson_content_ttl
    return cache_ai_content("lesson_content", cache_ttl)

def cache_exercises(ttl: Optional[int] = None):
    """Decorator specifically for exercise caching."""
    cache_ttl = ttl or redis_cache.exercise_cache_ttl
    return cache_ai_content("exercises", cache_ttl)

def cache_assessments(ttl: Optional[int] = None):
    """Decorator specifically for assessment caching."""
    cache_ttl = ttl or redis_cache.assessment_cache_ttl
    return cache_ai_content("assessments", cache_ttl)

class AIContentCache:
    """Specialized cache for AI content operations."""
    
    def __init__(self, cache_service: RedisCache):
        self.cache = cache_service
    
    def get_lesson_content(self, lesson_title: str, module_context: str, 
                          vocabulary_themes: List[str], grammar_focus: List[str], 
                          cefr_level: str, duration_minutes: int = 60) -> Optional[Dict[str, Any]]:
        """Get cached lesson content."""
        cache_key = self.cache._generate_cache_key(
            "lesson_content",
            lesson_title=lesson_title,
            module_context=module_context,
            vocabulary_themes=vocabulary_themes,
            grammar_focus=grammar_focus,
            cefr_level=cefr_level,
            duration_minutes=duration_minutes
        )
        return self.cache.get(cache_key)
    
    def set_lesson_content(self, lesson_title: str, module_context: str, 
                          vocabulary_themes: List[str], grammar_focus: List[str], 
                          cefr_level: str, content: Dict[str, Any], 
                          duration_minutes: int = 60) -> bool:
        """Cache lesson content."""
        cache_key = self.cache._generate_cache_key(
            "lesson_content",
            lesson_title=lesson_title,
            module_context=module_context,
            vocabulary_themes=vocabulary_themes,
            grammar_focus=grammar_focus,
            cefr_level=cefr_level,
            duration_minutes=duration_minutes
        )
        return self.cache.set(cache_key, content, self.cache.lesson_content_ttl)
    
    def get_course_curriculum(self, company_name: str, industry: str, 
                            sop_content: str, cefr_level: str, 
                            duration_weeks: int = 8) -> Optional[Dict[str, Any]]:
        """Get cached course curriculum."""
        # Use hash of sop_content to avoid extremely long keys
        sop_hash = hashlib.md5(sop_content.encode()).hexdigest()
        cache_key = self.cache._generate_cache_key(
            "course_curriculum",
            company_name=company_name,
            industry=industry,
            sop_content_hash=sop_hash,
            cefr_level=cefr_level,
            duration_weeks=duration_weeks
        )
        return self.cache.get(cache_key)
    
    def set_course_curriculum(self, company_name: str, industry: str, 
                            sop_content: str, cefr_level: str, 
                            curriculum: Dict[str, Any], duration_weeks: int = 8) -> bool:
        """Cache course curriculum."""
        sop_hash = hashlib.md5(sop_content.encode()).hexdigest()
        cache_key = self.cache._generate_cache_key(
            "course_curriculum",
            company_name=company_name,
            industry=industry,
            sop_content_hash=sop_hash,
            cefr_level=cefr_level,
            duration_weeks=duration_weeks
        )
        return self.cache.set(cache_key, curriculum, self.cache.course_curriculum_ttl)
    
    def get_exercises(self, lesson_context: str, exercise_types: List[str], 
                     cefr_level: str, count: int = 5) -> Optional[List[Dict[str, Any]]]:
        """Get cached exercises."""
        cache_key = self.cache._generate_cache_key(
            "exercises",
            lesson_context=lesson_context,
            exercise_types=exercise_types,
            cefr_level=cefr_level,
            count=count
        )
        return self.cache.get(cache_key)
    
    def set_exercises(self, lesson_context: str, exercise_types: List[str], 
                     cefr_level: str, exercises: List[Dict[str, Any]], 
                     count: int = 5) -> bool:
        """Cache exercises."""
        cache_key = self.cache._generate_cache_key(
            "exercises",
            lesson_context=lesson_context,
            exercise_types=exercise_types,
            cefr_level=cefr_level,
            count=count
        )
        return self.cache.set(cache_key, exercises, self.cache.exercise_cache_ttl)
    
    def get_assessment(self, course_context: str, assessment_type: str, 
                      cefr_level: str, duration_minutes: int = 30) -> Optional[Dict[str, Any]]:
        """Get cached assessment."""
        cache_key = self.cache._generate_cache_key(
            "assessment",
            course_context=course_context,
            assessment_type=assessment_type,
            cefr_level=cefr_level,
            duration_minutes=duration_minutes
        )
        return self.cache.get(cache_key)
    
    def set_assessment(self, course_context: str, assessment_type: str, 
                      cefr_level: str, assessment: Dict[str, Any], 
                      duration_minutes: int = 30) -> bool:
        """Cache assessment."""
        cache_key = self.cache._generate_cache_key(
            "assessment",
            course_context=course_context,
            assessment_type=assessment_type,
            cefr_level=cefr_level,
            duration_minutes=duration_minutes
        )
        return self.cache.set(cache_key, assessment, self.cache.assessment_cache_ttl)
    
    def invalidate_course_cache(self, company_name: str, industry: str) -> int:
        """Invalidate all cache entries for a specific course."""
        pattern = f"*{company_name}*{industry}*"
        return self.cache.clear_pattern(pattern)
    
    def get_cache_performance(self) -> Dict[str, Any]:
        """Get performance metrics for AI content cache."""
        stats = self.cache.get_stats()
        memory_usage = self.cache.get_memory_usage()
        
        return {
            "cache_performance": {
                "hit_rate": stats["cache_stats"]["hit_rate_percent"],
                "total_requests": stats["cache_stats"]["total_requests"],
                "cache_hits": stats["cache_stats"]["hits"],
                "cache_misses": stats["cache_stats"]["misses"],
                "memory_usage": memory_usage.get("used_memory_human", "N/A")
            },
            "ai_content_metrics": {
                "lesson_content_cache_ttl": self.cache.lesson_content_ttl,
                "course_curriculum_cache_ttl": self.cache.course_curriculum_ttl,
                "exercise_cache_ttl": self.cache.exercise_cache_ttl,
                "assessment_cache_ttl": self.cache.assessment_cache_ttl
            }
        }

# Global AI content cache instance
ai_content_cache = AIContentCache(redis_cache)

# Performance monitoring
class CachePerformanceMonitor:
    """Monitor cache performance and provide optimization insights."""
    
    def __init__(self, cache_service: RedisCache):
        self.cache = cache_service
        self.performance_history = []
    
    def record_performance(self):
        """Record current performance metrics."""
        stats = self.cache.get_stats()
        timestamp = datetime.utcnow().isoformat()
        
        performance_data = {
            "timestamp": timestamp,
            "hit_rate": stats["cache_stats"]["hit_rate_percent"],
            "total_requests": stats["cache_stats"]["total_requests"],
            "memory_usage": self.cache.get_memory_usage()
        }
        
        self.performance_history.append(performance_data)
        
        # Keep only last 100 entries
        if len(self.performance_history) > 100:
            self.performance_history.pop(0)
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """Get performance insights and recommendations."""
        if not self.performance_history:
            return {"insights": "No performance data available"}
        
        recent_data = self.performance_history[-10:]  # Last 10 records
        avg_hit_rate = sum(d["hit_rate"] for d in recent_data) / len(recent_data)
        
        insights = {
            "average_hit_rate": round(avg_hit_rate, 2),
            "total_samples": len(self.performance_history),
            "cache_efficiency": "excellent" if avg_hit_rate >= 80 else "good" if avg_hit_rate >= 60 else "needs_improvement",
            "recommendations": []
        }
        
        # Add recommendations based on performance
        if avg_hit_rate < 60:
            insights["recommendations"].append("Consider increasing cache TTL values")
            insights["recommendations"].append("Review cache key generation strategy")
        
        if avg_hit_rate >= 80:
            insights["recommendations"].append("Cache performance is excellent")
        
        return insights

# Global performance monitor
cache_performance_monitor = CachePerformanceMonitor(redis_cache)

# Utility functions
def warm_cache_for_common_queries():
    """Pre-populate cache with common queries."""
    # This could be implemented to pre-cache common content
    pass

def optimize_cache_settings():
    """Optimize cache settings based on usage patterns."""
    # This could analyze performance history and adjust TTL values
    pass

logger.info("Redis cache service initialized with AI content caching capabilities")