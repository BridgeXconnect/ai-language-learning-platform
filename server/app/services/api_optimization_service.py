"""
API Optimization Service for AI Language Learning Platform
Implements connection pooling, response time optimization, and performance monitoring.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import aiohttp
import aioredis
from contextlib import asynccontextmanager
import json

logger = logging.getLogger(__name__)

@dataclass
class ConnectionPool:
    """Connection pool configuration and management."""
    name: str
    max_connections: int = 10
    max_keepalive: int = 30
    timeout: float = 30.0
    retry_attempts: int = 3
    active_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class PerformanceMetrics:
    """Performance metrics tracking."""
    endpoint: str
    request_count: int = 0
    total_response_time: float = 0.0
    average_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    error_count: int = 0
    last_request: Optional[datetime] = None

class APIOptimizationService:
    """Service for optimizing API performance and connection management."""
    
    def __init__(self):
        self.connection_pools: Dict[str, ConnectionPool] = {}
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        self.http_session: Optional[aiohttp.ClientSession] = None
        self.redis_pool: Optional[aioredis.Redis] = None
        self.cache_enabled = True
        self.cache_ttl = 300  # 5 minutes default
        self.rate_limiting = {}
        self.circuit_breakers = {}
        
        logger.info("APIOptimizationService initialized")
    
    async def initialize(self):
        """Initialize connection pools and sessions."""
        # Initialize HTTP session with connection pooling
        connector = aiohttp.TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=30,  # Connections per host
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.http_session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
        # Initialize Redis connection pool
        try:
            self.redis_pool = aioredis.from_url(
                "redis://localhost:6379/0",
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            await self.redis_pool.ping()
            logger.info("Redis connection pool initialized successfully")
        except Exception as e:
            logger.warning(f"Redis connection pool initialization failed: {e}")
            self.cache_enabled = False
        
        logger.info("APIOptimizationService initialization completed")
    
    async def create_connection_pool(self, name: str, config: Dict[str, Any]) -> ConnectionPool:
        """Create a new connection pool."""
        pool = ConnectionPool(
            name=name,
            max_connections=config.get("max_connections", 10),
            max_keepalive=config.get("max_keepalive", 30),
            timeout=config.get("timeout", 30.0),
            retry_attempts=config.get("retry_attempts", 3)
        )
        
        self.connection_pools[name] = pool
        logger.info(f"Created connection pool: {name}")
        return pool
    
    @asynccontextmanager
    async def get_http_connection(self, pool_name: str = "default"):
        """Get HTTP connection from pool with context management."""
        if not self.http_session:
            await self.initialize()
        
        pool = self.connection_pools.get(pool_name)
        if pool and pool.active_connections >= pool.max_connections:
            logger.warning(f"Connection pool {pool_name} at capacity")
        
        try:
            if pool:
                pool.active_connections += 1
            yield self.http_session
        finally:
            if pool:
                pool.active_connections = max(0, pool.active_connections - 1)
    
    async def optimized_request(self, method: str, url: str, 
                              data: Dict[str, Any] = None, 
                              headers: Dict[str, str] = None,
                              cache_key: str = None,
                              pool_name: str = "default") -> Dict[str, Any]:
        """Make an optimized HTTP request with caching and connection pooling."""
        start_time = time.time()
        endpoint = f"{method} {url}"
        
        # Initialize metrics if not exists
        if endpoint not in self.performance_metrics:
            self.performance_metrics[endpoint] = PerformanceMetrics(endpoint=endpoint)
        
        metrics = self.performance_metrics[endpoint]
        metrics.request_count += 1
        
        # Check cache first
        if cache_key and self.cache_enabled:
            cached_response = await self._get_cached_response(cache_key)
            if cached_response:
                response_time = time.time() - start_time
                self._update_metrics(metrics, response_time, success=True)
                return {
                    "data": cached_response,
                    "cached": True,
                    "response_time": response_time
                }
        
        # Check rate limiting
        if not await self._check_rate_limit(endpoint):
            raise Exception(f"Rate limit exceeded for {endpoint}")
        
        # Check circuit breaker
        if await self._is_circuit_open(endpoint):
            raise Exception(f"Circuit breaker open for {endpoint}")
        
        # Make request with retry logic
        response_data = None
        last_error = None
        
        pool = self.connection_pools.get(pool_name)
        retry_attempts = pool.retry_attempts if pool else 3
        
        for attempt in range(retry_attempts):
            try:
                async with self.get_http_connection(pool_name):
                    async with self.http_session.request(
                        method=method,
                        url=url,
                        json=data,
                        headers=headers
                    ) as response:
                        response.raise_for_status()
                        response_data = await response.json()
                        break
                        
            except Exception as e:
                last_error = e
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise e
        
        response_time = time.time() - start_time
        
        # Cache successful response
        if cache_key and self.cache_enabled and response_data:
            await self._cache_response(cache_key, response_data)
        
        # Update metrics
        success = response_data is not None
        self._update_metrics(metrics, response_time, success)
        
        # Update circuit breaker
        await self._update_circuit_breaker(endpoint, success)
        
        return {
            "data": response_data,
            "cached": False,
            "response_time": response_time,
            "attempts": attempt + 1 if last_error else 1
        }
    
    async def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get response from cache."""
        try:
            if self.redis_pool:
                cached = await self.redis_pool.get(f"api_cache:{cache_key}")
                if cached:
                    return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
        return None
    
    async def _cache_response(self, cache_key: str, data: Dict[str, Any]):
        """Cache response data."""
        try:
            if self.redis_pool:
                await self.redis_pool.setex(
                    f"api_cache:{cache_key}",
                    self.cache_ttl,
                    json.dumps(data)
                )
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    async def _check_rate_limit(self, endpoint: str) -> bool:
        """Check if request is within rate limit."""
        if endpoint not in self.rate_limiting:
            self.rate_limiting[endpoint] = {
                "requests": [],
                "limit": 100,  # requests per minute
                "window": 60   # seconds
            }
        
        rate_limit = self.rate_limiting[endpoint]
        now = datetime.now()
        
        # Remove old requests outside the window
        rate_limit["requests"] = [
            req_time for req_time in rate_limit["requests"]
            if now - req_time < timedelta(seconds=rate_limit["window"])
        ]
        
        # Check if under limit
        if len(rate_limit["requests"]) >= rate_limit["limit"]:
            return False
        
        # Add current request
        rate_limit["requests"].append(now)
        return True
    
    async def _is_circuit_open(self, endpoint: str) -> bool:
        """Check if circuit breaker is open."""
        if endpoint not in self.circuit_breakers:
            self.circuit_breakers[endpoint] = {
                "failures": 0,
                "last_failure": None,
                "state": "closed",  # closed, open, half-open
                "threshold": 5,
                "timeout": 60  # seconds
            }
        
        circuit = self.circuit_breakers[endpoint]
        
        if circuit["state"] == "open":
            if circuit["last_failure"]:
                time_since_failure = (datetime.now() - circuit["last_failure"]).total_seconds()
                if time_since_failure > circuit["timeout"]:
                    circuit["state"] = "half-open"
                    return False
            return True
        
        return False
    
    async def _update_circuit_breaker(self, endpoint: str, success: bool):
        """Update circuit breaker state."""
        if endpoint not in self.circuit_breakers:
            return
        
        circuit = self.circuit_breakers[endpoint]
        
        if success:
            if circuit["state"] == "half-open":
                circuit["state"] = "closed"
            circuit["failures"] = 0
        else:
            circuit["failures"] += 1
            circuit["last_failure"] = datetime.now()
            
            if circuit["failures"] >= circuit["threshold"]:
                circuit["state"] = "open"
    
    def _update_metrics(self, metrics: PerformanceMetrics, response_time: float, success: bool):
        """Update performance metrics."""
        metrics.total_response_time += response_time
        metrics.average_response_time = metrics.total_response_time / metrics.request_count
        metrics.min_response_time = min(metrics.min_response_time, response_time)
        metrics.max_response_time = max(metrics.max_response_time, response_time)
        metrics.last_request = datetime.now()
        
        if not success:
            metrics.error_count += 1
    
    async def optimize_agent_communication(self, agent_endpoints: List[str], 
                                         requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize communication with multiple agents."""
        logger.info(f"Optimizing communication with {len(agent_endpoints)} agents")
        
        # Create connection pools for each agent
        for endpoint in agent_endpoints:
            if endpoint not in self.connection_pools:
                await self.create_connection_pool(
                    endpoint,
                    {"max_connections": 5, "timeout": 15.0}
                )
        
        # Execute requests in parallel
        tasks = []
        for i, request in enumerate(requests):
            endpoint = agent_endpoints[i % len(agent_endpoints)]
            task = self.optimized_request(
                method="POST",
                url=endpoint,
                data=request,
                pool_name=endpoint
            )
            tasks.append(task)
        
        # Wait for all requests to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_requests = 0
        total_response_time = 0
        
        for result in results:
            if isinstance(result, dict) and "data" in result:
                successful_requests += 1
                total_response_time += result.get("response_time", 0)
        
        return {
            "total_requests": len(requests),
            "successful_requests": successful_requests,
            "average_response_time": total_response_time / len(requests) if requests else 0,
            "results": results
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        report = {
            "connection_pools": {},
            "endpoint_metrics": {},
            "cache_stats": {
                "enabled": self.cache_enabled,
                "ttl": self.cache_ttl
            },
            "rate_limiting": {
                endpoint: {
                    "current_requests": len(data["requests"]),
                    "limit": data["limit"]
                }
                for endpoint, data in self.rate_limiting.items()
            },
            "circuit_breakers": {
                endpoint: {
                    "state": data["state"],
                    "failures": data["failures"],
                    "threshold": data["threshold"]
                }
                for endpoint, data in self.circuit_breakers.items()
            }
        }
        
        # Connection pool stats
        for name, pool in self.connection_pools.items():
            report["connection_pools"][name] = {
                "active_connections": pool.active_connections,
                "max_connections": pool.max_connections,
                "total_requests": pool.total_requests,
                "failed_requests": pool.failed_requests,
                "average_response_time": pool.average_response_time
            }
        
        # Endpoint metrics
        for endpoint, metrics in self.performance_metrics.items():
            report["endpoint_metrics"][endpoint] = {
                "request_count": metrics.request_count,
                "average_response_time": metrics.average_response_time,
                "min_response_time": metrics.min_response_time,
                "max_response_time": metrics.max_response_time,
                "error_count": metrics.error_count,
                "error_rate": metrics.error_count / metrics.request_count if metrics.request_count > 0 else 0
            }
        
        return report
    
    async def cleanup(self):
        """Clean up resources."""
        if self.http_session:
            await self.http_session.close()
        
        if self.redis_pool:
            await self.redis_pool.close()
        
        logger.info("APIOptimizationService cleanup completed")

# Global instance
api_optimizer = APIOptimizationService() 