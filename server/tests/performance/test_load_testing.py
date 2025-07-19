"""
Performance Testing Framework for AI Language Learning Platform
Tests system performance under load conditions
"""

import asyncio
import time
import statistics
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from unittest.mock import Mock, patch
import httpx
import psutil
import os

class PerformanceMetrics:
    """Collect and analyze performance metrics"""
    
    def __init__(self):
        self.response_times = []
        self.error_count = 0
        self.success_count = 0
        self.start_time = None
        self.end_time = None
        self.memory_usage = []
        self.cpu_usage = []
    
    def add_response_time(self, response_time: float):
        """Add response time measurement"""
        self.response_times.append(response_time)
    
    def add_error(self):
        """Record an error"""
        self.error_count += 1
    
    def add_success(self):
        """Record a success"""
        self.success_count += 1
    
    def record_system_metrics(self):
        """Record system resource usage"""
        process = psutil.Process()
        self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
        self.cpu_usage.append(process.cpu_percent())
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        total_requests = self.success_count + self.error_count
        
        return {
            "total_requests": total_requests,
            "successful_requests": self.success_count,
            "failed_requests": self.error_count,
            "error_rate": self.error_count / total_requests if total_requests > 0 else 0,
            "avg_response_time": statistics.mean(self.response_times) if self.response_times else 0,
            "min_response_time": min(self.response_times) if self.response_times else 0,
            "max_response_time": max(self.response_times) if self.response_times else 0,
            "p95_response_time": statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) >= 20 else 0,
            "p99_response_time": statistics.quantiles(self.response_times, n=100)[98] if len(self.response_times) >= 100 else 0,
            "avg_memory_usage": statistics.mean(self.memory_usage) if self.memory_usage else 0,
            "max_memory_usage": max(self.memory_usage) if self.memory_usage else 0,
            "avg_cpu_usage": statistics.mean(self.cpu_usage) if self.cpu_usage else 0,
            "max_cpu_usage": max(self.cpu_usage) if self.cpu_usage else 0,
            "duration": self.end_time - self.start_time if self.start_time and self.end_time else 0
        }

class LoadTestScenario:
    """Define load testing scenarios"""
    
    @staticmethod
    def simulate_api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Simulate API request with timing"""
        start_time = time.time()
        
        # Simulate network latency and processing time
        processing_time = 0.05 + (time.time() % 0.1)  # 50-150ms
        time.sleep(processing_time)
        
        # Simulate response based on endpoint
        if endpoint == "/health":
            response = {"status": "healthy", "timestamp": time.time()}
            success = True
        elif endpoint == "/api/v1/auth/login":
            response = {"access_token": "mock_token", "token_type": "bearer"}
            success = True
        elif endpoint == "/api/v1/courses":
            response = {"courses": [{"id": i, "title": f"Course {i}"} for i in range(10)]}
            success = True
        elif endpoint == "/api/v1/ai/generate-course":
            # Simulate longer AI processing time
            time.sleep(2.0)  # 2 seconds for AI processing
            response = {"course_id": "generated_123", "status": "completed"}
            success = True
        else:
            response = {"error": "Not found"}
            success = False
        
        end_time = time.time()
        
        return {
            "response": response,
            "response_time": (end_time - start_time) * 1000,  # Convert to ms
            "success": success,
            "status_code": 200 if success else 404
        }

class TestLoadTesting:
    """Load testing test cases"""
    
    def test_concurrent_users_baseline(self):
        """Test baseline concurrent user performance"""
        metrics = PerformanceMetrics()
        metrics.start_time = time.time()
        
        # Test 10 concurrent users (baseline)
        num_concurrent_users = 10
        requests_per_user = 5
        
        with ThreadPoolExecutor(max_workers=num_concurrent_users) as executor:
            futures = []
            
            for user_id in range(num_concurrent_users):
                for request_id in range(requests_per_user):
                    future = executor.submit(
                        LoadTestScenario.simulate_api_request,
                        "/api/v1/courses"
                    )
                    futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                result = future.result()
                metrics.add_response_time(result["response_time"])
                
                if result["success"]:
                    metrics.add_success()
                else:
                    metrics.add_error()
        
        metrics.end_time = time.time()
        summary = metrics.get_summary()
        
        # Performance assertions
        assert summary["error_rate"] < 0.01, f"Error rate too high: {summary['error_rate']}"
        assert summary["avg_response_time"] < 200, f"Average response time too high: {summary['avg_response_time']}ms"
        assert summary["p95_response_time"] < 500, f"P95 response time too high: {summary['p95_response_time']}ms"
    
    def test_concurrent_users_100(self):
        """Test 100 concurrent users"""
        metrics = PerformanceMetrics()
        metrics.start_time = time.time()
        
        num_concurrent_users = 100
        requests_per_user = 3
        
        with ThreadPoolExecutor(max_workers=num_concurrent_users) as executor:
            futures = []
            
            for user_id in range(num_concurrent_users):
                for request_id in range(requests_per_user):
                    # Mix of different endpoints
                    endpoints = ["/health", "/api/v1/courses", "/api/v1/auth/login"]
                    endpoint = endpoints[request_id % len(endpoints)]
                    
                    future = executor.submit(
                        LoadTestScenario.simulate_api_request,
                        endpoint
                    )
                    futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                result = future.result()
                metrics.add_response_time(result["response_time"])
                
                if result["success"]:
                    metrics.add_success()
                else:
                    metrics.add_error()
        
        metrics.end_time = time.time()
        summary = metrics.get_summary()
        
        # Performance assertions for 100 users
        assert summary["error_rate"] < 0.05, f"Error rate too high: {summary['error_rate']}"
        assert summary["avg_response_time"] < 300, f"Average response time too high: {summary['avg_response_time']}ms"
        assert summary["p95_response_time"] < 1000, f"P95 response time too high: {summary['p95_response_time']}ms"
    
    @pytest.mark.slow
    def test_concurrent_users_1000(self):
        """Test 1000 concurrent users (full load test)"""
        metrics = PerformanceMetrics()
        metrics.start_time = time.time()
        
        num_concurrent_users = 1000
        requests_per_user = 2
        
        with ThreadPoolExecutor(max_workers=min(num_concurrent_users, 200)) as executor:
            futures = []
            
            for user_id in range(num_concurrent_users):
                for request_id in range(requests_per_user):
                    # Weighted endpoint distribution
                    if request_id % 4 == 0:
                        endpoint = "/health"
                    elif request_id % 4 == 1:
                        endpoint = "/api/v1/courses"
                    elif request_id % 4 == 2:
                        endpoint = "/api/v1/auth/login"
                    else:
                        endpoint = "/api/v1/courses"
                    
                    future = executor.submit(
                        LoadTestScenario.simulate_api_request,
                        endpoint
                    )
                    futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                result = future.result()
                metrics.add_response_time(result["response_time"])
                
                if result["success"]:
                    metrics.add_success()
                else:
                    metrics.add_error()
        
        metrics.end_time = time.time()
        summary = metrics.get_summary()
        
        # Performance assertions for 1000 users (relaxed thresholds)
        assert summary["error_rate"] < 0.1, f"Error rate too high: {summary['error_rate']}"
        assert summary["avg_response_time"] < 500, f"Average response time too high: {summary['avg_response_time']}ms"
        assert summary["p95_response_time"] < 2000, f"P95 response time too high: {summary['p95_response_time']}ms"
        
        # Log results for analysis
        print(f"\\n1000 User Load Test Results:")
        print(f"Total Requests: {summary['total_requests']}")
        print(f"Success Rate: {(summary['successful_requests'] / summary['total_requests']) * 100:.2f}%")
        print(f"Average Response Time: {summary['avg_response_time']:.2f}ms")
        print(f"P95 Response Time: {summary['p95_response_time']:.2f}ms")
        print(f"P99 Response Time: {summary['p99_response_time']:.2f}ms")

class TestAIServicePerformance:
    """Test AI service specific performance"""
    
    def test_course_generation_performance(self):
        """Test course generation performance"""
        metrics = PerformanceMetrics()
        metrics.start_time = time.time()
        
        # Test course generation with different parameters
        test_cases = [
            {"topic": "Spanish Grammar", "level": "beginner", "duration": 5},
            {"topic": "Business English", "level": "intermediate", "duration": 10},
            {"topic": "Advanced Conversation", "level": "advanced", "duration": 15}
        ]
        
        for test_case in test_cases:
            start_time = time.time()
            
            # Simulate AI course generation
            result = LoadTestScenario.simulate_api_request(
                "/api/v1/ai/generate-course",
                method="POST",
                data=test_case
            )
            
            end_time = time.time()
            processing_time = (end_time - start_time) * 1000  # Convert to ms
            
            metrics.add_response_time(processing_time)
            if result["success"]:
                metrics.add_success()
            else:
                metrics.add_error()
        
        metrics.end_time = time.time()
        summary = metrics.get_summary()
        
        # AI service performance assertions
        assert summary["error_rate"] == 0, f"AI service should not fail: {summary['error_rate']}"
        assert summary["avg_response_time"] < 30000, f"Course generation too slow: {summary['avg_response_time']}ms"  # 30 seconds
        assert summary["max_response_time"] < 45000, f"Max course generation time too high: {summary['max_response_time']}ms"  # 45 seconds
    
    def test_ai_quiz_generation_performance(self):
        """Test AI quiz generation performance"""
        metrics = PerformanceMetrics()
        metrics.start_time = time.time()
        
        # Test multiple quiz generations
        num_quizzes = 10
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for i in range(num_quizzes):
                future = executor.submit(
                    LoadTestScenario.simulate_api_request,
                    "/api/v1/ai/generate-quiz",
                    method="POST",
                    data={"topic": f"Topic {i}", "difficulty": "intermediate"}
                )
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                result = future.result()
                metrics.add_response_time(result["response_time"])
                
                if result["success"]:
                    metrics.add_success()
                else:
                    metrics.add_error()
        
        metrics.end_time = time.time()
        summary = metrics.get_summary()
        
        # Quiz generation performance assertions
        assert summary["error_rate"] < 0.1, f"Quiz generation error rate too high: {summary['error_rate']}"
        assert summary["avg_response_time"] < 5000, f"Quiz generation too slow: {summary['avg_response_time']}ms"  # 5 seconds
        assert summary["p95_response_time"] < 10000, f"P95 quiz generation time too high: {summary['p95_response_time']}ms"  # 10 seconds

class TestMemoryPerformance:
    """Test memory usage and performance"""
    
    def test_memory_usage_under_load(self):
        """Test memory usage under load"""
        import gc
        
        # Get initial memory usage
        gc.collect()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Simulate load
        test_data = []
        for i in range(1000):
            # Simulate user sessions and course data
            user_session = {
                "user_id": i,
                "courses": [{"id": j, "title": f"Course {j}", "progress": 0.5} for j in range(10)],
                "quiz_results": [{"quiz_id": k, "score": 85} for k in range(5)]
            }
            test_data.append(user_session)
        
        # Get memory usage after load
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - initial_memory
        
        # Memory usage assertions
        assert memory_increase < 500, f"Memory usage increased too much: {memory_increase}MB"
        assert current_memory < 1000, f"Total memory usage too high: {current_memory}MB"
        
        # Cleanup
        del test_data
        gc.collect()
    
    def test_memory_leak_detection(self):
        """Test for memory leaks"""
        import gc
        
        # Get initial memory
        gc.collect()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Simulate repeated operations
        for cycle in range(10):
            # Simulate request processing
            for i in range(100):
                result = LoadTestScenario.simulate_api_request("/api/v1/courses")
                # Simulate some processing
                temp_data = [{"id": j, "data": f"item_{j}"} for j in range(100)]
                del temp_data
            
            # Force garbage collection
            gc.collect()
        
        # Get final memory
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory leak assertion
        assert memory_increase < 50, f"Potential memory leak detected: {memory_increase}MB increase"

if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-s"])