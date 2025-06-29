"""
Agent Communication Client
Handles HTTP communication with all specialized agents
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import asyncio
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentClient:
    """Client for communicating with all specialized agents."""
    
    def __init__(self):
        # Agent endpoints configuration
        self.agent_endpoints = {
            "course_planner": {
                "base_url": os.getenv("COURSE_PLANNER_URL", "http://localhost:8101"),
                "health_endpoint": "/health",
                "capabilities_endpoint": "/capabilities"
            },
            "content_creator": {
                "base_url": os.getenv("CONTENT_CREATOR_URL", "http://localhost:8102"),
                "health_endpoint": "/health",
                "capabilities_endpoint": "/capabilities"
            },
            "quality_assurance": {
                "base_url": os.getenv("QUALITY_ASSURANCE_URL", "http://localhost:8103"),
                "health_endpoint": "/health",
                "capabilities_endpoint": "/capabilities"
            }
        }
        
        # HTTP client configuration
        self.timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes
        self.retry_attempts = 3
        self.retry_delay = 2  # seconds
        
        # Performance tracking
        self.request_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "agent_response_times": {}
        }
    
    async def call_course_planner(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call the Course Planner Agent."""
        
        endpoint_map = {
            "plan_course": "/plan-course",
            "validate_request": "/validate-request",
            "get_capabilities": "/capabilities"
        }
        
        endpoint = endpoint_map.get(action)
        if not endpoint:
            raise ValueError(f"Unknown Course Planner action: {action}")
        
        return await self._make_agent_request("course_planner", endpoint, data)
    
    async def call_content_creator(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call the Content Creator Agent."""
        
        endpoint_map = {
            "create_lesson_content": "/create-lesson",
            "create_exercises": "/create-exercises",
            "create_assessment": "/create-assessment",
            "adapt_content": "/adapt-content",
            "get_capabilities": "/capabilities"
        }
        
        endpoint = endpoint_map.get(action)
        if not endpoint:
            raise ValueError(f"Unknown Content Creator action: {action}")
        
        return await self._make_agent_request("content_creator", endpoint, data)
    
    async def call_quality_assurance(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call the Quality Assurance Agent."""
        
        endpoint_map = {
            "review_content": "/review-content",
            "improve_content": "/improve-content",
            "batch_review": "/batch-review",
            "get_capabilities": "/capabilities"
        }
        
        endpoint = endpoint_map.get(action)
        if not endpoint:
            raise ValueError(f"Unknown Quality Assurance action: {action}")
        
        return await self._make_agent_request("quality_assurance", endpoint, data)
    
    async def _make_agent_request(
        self, 
        agent_name: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        method: str = "POST"
    ) -> Dict[str, Any]:
        """Make an HTTP request to an agent."""
        
        agent_config = self.agent_endpoints.get(agent_name)
        if not agent_config:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        url = f"{agent_config['base_url']}{endpoint}"
        start_time = datetime.utcnow()
        
        # Track request
        self.request_metrics["total_requests"] += 1
        
        for attempt in range(self.retry_attempts):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    # Prepare request
                    kwargs = {
                        "url": url,
                        "headers": {"Content-Type": "application/json"}
                    }
                    
                    if data and method.upper() in ["POST", "PUT", "PATCH"]:
                        kwargs["json"] = data
                    elif data and method.upper() == "GET":
                        kwargs["params"] = data
                    
                    # Make request
                    async with getattr(session, method.lower())(**kwargs) as response:
                        response_data = await response.json()
                        
                        # Calculate response time
                        response_time = (datetime.utcnow() - start_time).total_seconds()
                        self._update_response_metrics(agent_name, response_time)
                        
                        if response.status == 200:
                            self.request_metrics["successful_requests"] += 1
                            logger.info(f"Agent {agent_name} request successful: {endpoint} ({response_time:.2f}s)")
                            return response_data
                        else:
                            error_msg = response_data.get("error", f"HTTP {response.status}")
                            logger.error(f"Agent {agent_name} request failed: {error_msg}")
                            
                            if attempt == self.retry_attempts - 1:
                                self.request_metrics["failed_requests"] += 1
                                return {
                                    "success": False,
                                    "error": error_msg,
                                    "status_code": response.status
                                }
                            
                            # Wait before retry
                            await asyncio.sleep(self.retry_delay * (attempt + 1))
                            
            except asyncio.TimeoutError:
                logger.error(f"Agent {agent_name} request timeout: {endpoint}")
                if attempt == self.retry_attempts - 1:
                    self.request_metrics["failed_requests"] += 1
                    return {
                        "success": False,
                        "error": "Request timeout"
                    }
                await asyncio.sleep(self.retry_delay * (attempt + 1))
                
            except aiohttp.ClientError as e:
                logger.error(f"Agent {agent_name} connection error: {e}")
                if attempt == self.retry_attempts - 1:
                    self.request_metrics["failed_requests"] += 1
                    return {
                        "success": False,
                        "error": f"Connection error: {str(e)}"
                    }
                await asyncio.sleep(self.retry_delay * (attempt + 1))
                
            except Exception as e:
                logger.error(f"Agent {agent_name} unexpected error: {e}")
                if attempt == self.retry_attempts - 1:
                    self.request_metrics["failed_requests"] += 1
                    return {
                        "success": False,
                        "error": f"Unexpected error: {str(e)}"
                    }
                await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        # Should not reach here
        return {
            "success": False,
            "error": "All retry attempts failed"
        }
    
    async def check_agent_health(self, agent_name: str) -> Dict[str, Any]:
        """Check the health of a specific agent."""
        
        agent_config = self.agent_endpoints.get(agent_name)
        if not agent_config:
            return {
                "agent": agent_name,
                "healthy": False,
                "error": "Unknown agent"
            }
        
        try:
            result = await self._make_agent_request(
                agent_name, 
                agent_config["health_endpoint"], 
                method="GET"
            )
            
            return {
                "agent": agent_name,
                "healthy": result.get("status") == "healthy",
                "response": result,
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "agent": agent_name,
                "healthy": False,
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat()
            }
    
    async def check_all_agents_health(self) -> Dict[str, Dict[str, Any]]:
        """Check the health of all agents concurrently."""
        
        health_tasks = []
        agent_names = list(self.agent_endpoints.keys())
        
        for agent_name in agent_names:
            task = self.check_agent_health(agent_name)
            health_tasks.append(task)
        
        # Execute health checks concurrently
        health_results = await asyncio.gather(*health_tasks, return_exceptions=True)
        
        # Compile results
        health_status = {}
        for i, result in enumerate(health_results):
            agent_name = agent_names[i]
            
            if isinstance(result, Exception):
                health_status[agent_name] = {
                    "agent": agent_name,
                    "healthy": False,
                    "error": str(result),
                    "checked_at": datetime.utcnow().isoformat()
                }
            else:
                health_status[agent_name] = result
        
        return health_status
    
    async def get_agent_capabilities(self, agent_name: str) -> Dict[str, Any]:
        """Get capabilities of a specific agent."""
        
        agent_config = self.agent_endpoints.get(agent_name)
        if not agent_config:
            return {
                "error": f"Unknown agent: {agent_name}"
            }
        
        try:
            result = await self._make_agent_request(
                agent_name,
                agent_config["capabilities_endpoint"],
                method="GET"
            )
            
            return result
            
        except Exception as e:
            return {
                "error": f"Failed to get capabilities for {agent_name}: {str(e)}"
            }
    
    async def get_all_agent_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Get capabilities of all agents."""
        
        capabilities_tasks = []
        agent_names = list(self.agent_endpoints.keys())
        
        for agent_name in agent_names:
            task = self.get_agent_capabilities(agent_name)
            capabilities_tasks.append(task)
        
        # Execute capability requests concurrently
        capability_results = await asyncio.gather(*capabilities_tasks, return_exceptions=True)
        
        # Compile results
        all_capabilities = {}
        for i, result in enumerate(capability_results):
            agent_name = agent_names[i]
            
            if isinstance(result, Exception):
                all_capabilities[agent_name] = {
                    "error": str(result)
                }
            else:
                all_capabilities[agent_name] = result
        
        return all_capabilities
    
    def _update_response_metrics(self, agent_name: str, response_time: float):
        """Update response time metrics."""
        
        # Update overall average
        total_requests = self.request_metrics["total_requests"]
        current_avg = self.request_metrics["average_response_time"]
        new_avg = ((current_avg * (total_requests - 1)) + response_time) / total_requests
        self.request_metrics["average_response_time"] = new_avg
        
        # Update agent-specific metrics
        if agent_name not in self.request_metrics["agent_response_times"]:
            self.request_metrics["agent_response_times"][agent_name] = {
                "total_requests": 0,
                "average_response_time": 0.0,
                "min_response_time": response_time,
                "max_response_time": response_time
            }
        
        agent_metrics = self.request_metrics["agent_response_times"][agent_name]
        agent_requests = agent_metrics["total_requests"]
        agent_avg = agent_metrics["average_response_time"]
        
        # Update agent average
        new_agent_avg = ((agent_avg * agent_requests) + response_time) / (agent_requests + 1)
        agent_metrics["average_response_time"] = new_agent_avg
        agent_metrics["total_requests"] += 1
        
        # Update min/max
        agent_metrics["min_response_time"] = min(agent_metrics["min_response_time"], response_time)
        agent_metrics["max_response_time"] = max(agent_metrics["max_response_time"], response_time)
    
    def get_client_metrics(self) -> Dict[str, Any]:
        """Get client performance metrics."""
        
        return {
            "request_metrics": self.request_metrics,
            "agent_endpoints": {
                name: config["base_url"] 
                for name, config in self.agent_endpoints.items()
            },
            "configuration": {
                "timeout_seconds": self.timeout.total,
                "retry_attempts": self.retry_attempts,
                "retry_delay": self.retry_delay
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def test_all_agents(self) -> Dict[str, Any]:
        """Test basic functionality of all agents."""
        
        test_results = {}
        
        # Test Course Planner
        try:
            cp_result = await self.call_course_planner("get_capabilities", {})
            test_results["course_planner"] = {
                "test": "get_capabilities",
                "success": cp_result.get("agent_name") == "Course Planning Specialist",
                "response": cp_result
            }
        except Exception as e:
            test_results["course_planner"] = {
                "test": "get_capabilities",
                "success": False,
                "error": str(e)
            }
        
        # Test Content Creator
        try:
            cc_result = await self.call_content_creator("get_capabilities", {})
            test_results["content_creator"] = {
                "test": "get_capabilities", 
                "success": cc_result.get("agent_name") == "Content Creator Agent",
                "response": cc_result
            }
        except Exception as e:
            test_results["content_creator"] = {
                "test": "get_capabilities",
                "success": False,
                "error": str(e)
            }
        
        # Test Quality Assurance
        try:
            qa_result = await self.call_quality_assurance("get_capabilities", {})
            test_results["quality_assurance"] = {
                "test": "get_capabilities",
                "success": qa_result.get("agent_name") == "Quality Assurance Agent",
                "response": qa_result
            }
        except Exception as e:
            test_results["quality_assurance"] = {
                "test": "get_capabilities",
                "success": False,
                "error": str(e)
            }
        
        # Overall test status
        all_success = all(result.get("success", False) for result in test_results.values())
        
        return {
            "overall_success": all_success,
            "tests_run": len(test_results),
            "tests_passed": sum(1 for result in test_results.values() if result.get("success", False)),
            "agent_tests": test_results,
            "tested_at": datetime.utcnow().isoformat()
        }
    
    async def ping_all_agents(self) -> Dict[str, Any]:
        """Quick ping test for all agents."""
        
        ping_results = {}
        
        for agent_name in self.agent_endpoints.keys():
            start_time = datetime.utcnow()
            
            try:
                health_result = await self.check_agent_health(agent_name)
                response_time = (datetime.utcnow() - start_time).total_seconds()
                
                ping_results[agent_name] = {
                    "reachable": health_result.get("healthy", False),
                    "response_time_ms": round(response_time * 1000, 2),
                    "status": "online" if health_result.get("healthy", False) else "offline"
                }
                
            except Exception as e:
                response_time = (datetime.utcnow() - start_time).total_seconds()
                ping_results[agent_name] = {
                    "reachable": False,
                    "response_time_ms": round(response_time * 1000, 2),
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "ping_results": ping_results,
            "all_agents_reachable": all(result.get("reachable", False) for result in ping_results.values()),
            "pinged_at": datetime.utcnow().isoformat()
        }