"""
Load Testing Service for AI Language Learning Platform
Implements performance validation, load testing, and stress testing for QA Agent.
"""

import asyncio
import logging
import time
import statistics
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import aiohttp
import json
import random

logger = logging.getLogger(__name__)

@dataclass
class LoadTestConfig:
    """Configuration for load testing."""
    name: str
    target_url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    payload: Dict[str, Any] = field(default_factory=dict)
    concurrent_users: int = 10
    duration_seconds: int = 60
    ramp_up_seconds: int = 10
    ramp_down_seconds: int = 10
    success_criteria: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LoadTestResult:
    """Results from a load test."""
    test_name: str
    start_time: datetime
    end_time: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    response_times: List[float]
    throughput: float  # requests per second
    error_rate: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    average_response_time: float
    status: str  # passed, failed, warning

class LoadTestingService:
    """Service for conducting load tests and performance validation."""
    
    def __init__(self):
        self.test_results: Dict[str, LoadTestResult] = {}
        self.active_tests: Dict[str, bool] = {}
        self.http_session: Optional[aiohttp.ClientSession] = None
        self.default_success_criteria = {
            "max_response_time_p95": 2000,  # 2 seconds
            "max_error_rate": 0.05,  # 5%
            "min_throughput": 10,  # 10 requests per second
            "max_response_time_p99": 5000  # 5 seconds
        }
        
        logger.info("LoadTestingService initialized")
    
    async def initialize(self):
        """Initialize HTTP session for load testing."""
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(
            limit=1000,  # High limit for load testing
            limit_per_host=100,
            keepalive_timeout=30
        )
        
        self.http_session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector
        )
        
        logger.info("LoadTestingService HTTP session initialized")
    
    async def run_load_test(self, config: LoadTestConfig) -> LoadTestResult:
        """Run a comprehensive load test."""
        logger.info(f"Starting load test: {config.name}")
        
        if not self.http_session:
            await self.initialize()
        
        # Set default success criteria if not provided
        if not config.success_criteria:
            config.success_criteria = self.default_success_criteria.copy()
        
        start_time = datetime.now()
        self.active_tests[config.name] = True
        
        # Collect metrics
        response_times = []
        successful_requests = 0
        failed_requests = 0
        total_requests = 0
        
        # Calculate timing
        total_duration = config.duration_seconds + config.ramp_up_seconds + config.ramp_down_seconds
        end_time = start_time + timedelta(seconds=total_duration)
        
        # Create concurrent user tasks
        tasks = []
        for user_id in range(config.concurrent_users):
            task = self._simulate_user(
                user_id, config, start_time, end_time,
                response_times, successful_requests, failed_requests, total_requests
            )
            tasks.append(task)
        
        # Run all user simulations
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate final metrics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        throughput = total_requests / duration if duration > 0 else 0
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        
        # Calculate percentiles
        if response_times:
            p50_response_time = statistics.quantiles(response_times, n=100)[49]  # 50th percentile
            p95_response_time = statistics.quantiles(response_times, n=100)[94]  # 95th percentile
            p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            average_response_time = statistics.mean(response_times)
        else:
            p50_response_time = p95_response_time = p99_response_time = 0
            min_response_time = max_response_time = average_response_time = 0
        
        # Determine test status
        status = self._evaluate_test_status(
            p95_response_time, p99_response_time, error_rate, throughput, config.success_criteria
        )
        
        # Create result
        result = LoadTestResult(
            test_name=config.name,
            start_time=start_time,
            end_time=end_time,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            response_times=response_times,
            throughput=throughput,
            error_rate=error_rate,
            p50_response_time=p50_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            average_response_time=average_response_time,
            status=status
        )
        
        self.test_results[config.name] = result
        self.active_tests[config.name] = False
        
        logger.info(f"Load test {config.name} completed with status: {status}")
        return result
    
    async def _simulate_user(self, user_id: int, config: LoadTestConfig, 
                           start_time: datetime, end_time: datetime,
                           response_times: List[float], successful_requests: int,
                           failed_requests: int, total_requests: int):
        """Simulate a single user making requests."""
        current_time = start_time
        
        # Ramp up period
        ramp_up_delay = config.ramp_up_seconds / config.concurrent_users
        await asyncio.sleep(user_id * ramp_up_delay)
        
        while current_time < end_time and self.active_tests.get(config.name, False):
            try:
                # Make request
                request_start = time.time()
                
                async with self.http_session.request(
                    method=config.method,
                    url=config.target_url,
                    headers=config.headers,
                    json=config.payload if config.method in ["POST", "PUT", "PATCH"] else None
                ) as response:
                    response.raise_for_status()
                    await response.read()  # Ensure response is fully read
                
                response_time = (time.time() - request_start) * 1000  # Convert to milliseconds
                response_times.append(response_time)
                successful_requests += 1
                total_requests += 1
                
                # Random delay between requests (0.1 to 2 seconds)
                delay = random.uniform(0.1, 2.0)
                await asyncio.sleep(delay)
                current_time = datetime.now()
                
            except Exception as e:
                failed_requests += 1
                total_requests += 1
                logger.warning(f"Request failed for user {user_id}: {e}")
                
                # Shorter delay on failure
                await asyncio.sleep(0.5)
                current_time = datetime.now()
    
    def _evaluate_test_status(self, p95_response_time: float, p99_response_time: float,
                            error_rate: float, throughput: float,
                            success_criteria: Dict[str, Any]) -> str:
        """Evaluate if the test passed based on success criteria."""
        max_p95 = success_criteria.get("max_response_time_p95", 2000)
        max_p99 = success_criteria.get("max_response_time_p99", 5000)
        max_error_rate = success_criteria.get("max_error_rate", 0.05)
        min_throughput = success_criteria.get("min_throughput", 10)
        
        # Check all criteria
        p95_ok = p95_response_time <= max_p95
        p99_ok = p99_response_time <= max_p99
        error_ok = error_rate <= max_error_rate
        throughput_ok = throughput >= min_throughput
        
        if p95_ok and p99_ok and error_ok and throughput_ok:
            return "passed"
        elif error_ok and throughput_ok:  # Only response time issues
            return "warning"
        else:
            return "failed"
    
    async def run_stress_test(self, config: LoadTestConfig) -> LoadTestResult:
        """Run a stress test to find breaking point."""
        logger.info(f"Starting stress test: {config.name}")
        
        # Gradually increase load until failure
        stress_configs = []
        for multiplier in [1, 2, 4, 8, 16]:
            stress_config = LoadTestConfig(
                name=f"{config.name}_stress_{multiplier}x",
                target_url=config.target_url,
                method=config.method,
                headers=config.headers,
                payload=config.payload,
                concurrent_users=config.concurrent_users * multiplier,
                duration_seconds=30,  # Shorter duration for stress test
                ramp_up_seconds=5,
                ramp_down_seconds=5,
                success_criteria=config.success_criteria
            )
            stress_configs.append(stress_config)
        
        results = []
        breaking_point = None
        
        for stress_config in stress_configs:
            result = await self.run_load_test(stress_config)
            results.append(result)
            
            if result.status == "failed":
                breaking_point = stress_config.concurrent_users
                break
        
        # Return the last result with stress test metadata
        if results:
            final_result = results[-1]
            final_result.test_name = f"{config.name}_stress_test"
            final_result.breaking_point = breaking_point
            return final_result
        
        return None
    
    async def run_end_to_end_test(self, test_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run end-to-end testing with multiple scenarios."""
        logger.info(f"Starting end-to-end test with {len(test_scenarios)} scenarios")
        
        results = {}
        overall_status = "passed"
        
        for scenario in test_scenarios:
            config = LoadTestConfig(
                name=scenario["name"],
                target_url=scenario["url"],
                method=scenario.get("method", "GET"),
                headers=scenario.get("headers", {}),
                payload=scenario.get("payload", {}),
                concurrent_users=scenario.get("concurrent_users", 5),
                duration_seconds=scenario.get("duration_seconds", 30),
                success_criteria=scenario.get("success_criteria", {})
            )
            
            result = await self.run_load_test(config)
            results[scenario["name"]] = result
            
            if result.status == "failed":
                overall_status = "failed"
            elif result.status == "warning" and overall_status == "passed":
                overall_status = "warning"
        
        return {
            "overall_status": overall_status,
            "scenario_results": results,
            "total_scenarios": len(test_scenarios),
            "passed_scenarios": len([r for r in results.values() if r.status == "passed"]),
            "failed_scenarios": len([r for r in results.values() if r.status == "failed"])
        }
    
    async def run_performance_baseline_test(self) -> Dict[str, Any]:
        """Run baseline performance tests for the platform."""
        logger.info("Running performance baseline tests")
        
        baseline_scenarios = [
            {
                "name": "course_generation_api",
                "url": "http://localhost:8000/api/courses/generate",
                "method": "POST",
                "payload": {
                    "title": "Test Course",
                    "description": "Test course for performance baseline",
                    "cefr_level": "B1",
                    "duration_hours": 20
                },
                "concurrent_users": 5,
                "duration_seconds": 60
            },
            {
                "name": "user_authentication",
                "url": "http://localhost:8000/api/auth/login",
                "method": "POST",
                "payload": {
                    "email": "test@example.com",
                    "password": "testpassword"
                },
                "concurrent_users": 10,
                "duration_seconds": 60
            },
            {
                "name": "course_listing",
                "url": "http://localhost:8000/api/courses",
                "method": "GET",
                "concurrent_users": 15,
                "duration_seconds": 60
            },
            {
                "name": "ai_chat_interface",
                "url": "http://localhost:8000/api/ai/chat",
                "method": "POST",
                "payload": {
                    "message": "Hello, I need help with English grammar",
                    "user_id": 1
                },
                "concurrent_users": 8,
                "duration_seconds": 60
            }
        ]
        
        return await self.run_end_to_end_test(baseline_scenarios)
    
    def get_test_report(self, test_name: str = None) -> Dict[str, Any]:
        """Get comprehensive test report."""
        if test_name:
            result = self.test_results.get(test_name)
            if result:
                return {
                    "test_name": result.test_name,
                    "status": result.status,
                    "duration": (result.end_time - result.start_time).total_seconds(),
                    "total_requests": result.total_requests,
                    "successful_requests": result.successful_requests,
                    "failed_requests": result.failed_requests,
                    "throughput": result.throughput,
                    "error_rate": result.error_rate,
                    "response_times": {
                        "average": result.average_response_time,
                        "p50": result.p50_response_time,
                        "p95": result.p95_response_time,
                        "p99": result.p99_response_time,
                        "min": result.min_response_time,
                        "max": result.max_response_time
                    }
                }
            return None
        
        # Return summary of all tests
        return {
            "total_tests": len(self.test_results),
            "passed_tests": len([r for r in self.test_results.values() if r.status == "passed"]),
            "failed_tests": len([r for r in self.test_results.values() if r.status == "failed"]),
            "warning_tests": len([r for r in self.test_results.values() if r.status == "warning"]),
            "test_details": {
                name: {
                    "status": result.status,
                    "throughput": result.throughput,
                    "error_rate": result.error_rate,
                    "p95_response_time": result.p95_response_time
                }
                for name, result in self.test_results.items()
            }
        }
    
    async def cleanup(self):
        """Clean up resources."""
        # Stop all active tests
        for test_name in list(self.active_tests.keys()):
            self.active_tests[test_name] = False
        
        if self.http_session:
            await self.http_session.close()
        
        logger.info("LoadTestingService cleanup completed")

# Global instance
load_tester = LoadTestingService() 