"""
Tools for Agent Orchestrator
Implements workflow management, agent coordination, and system monitoring tools
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

# Database and external service imports
import asyncpg
from supabase import create_client, Client

# Monitoring and metrics
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Shared database connection for orchestrator tools."""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase: Optional[Client] = None
        
        # Skip actual connection for mock/test environments
        if (self.supabase_url and self.supabase_key and 
            not self.supabase_url.startswith('https://mock-') and
            not self.supabase_key.startswith('mock-')):
            try:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
            except Exception as e:
                logger.warning(f"Failed to connect to Supabase: {e}")
        else:
            logger.info("Using mock database connection for testing")
    
    def is_connected(self) -> bool:
        return self.supabase is not None

# Global database connection
db_connection = DatabaseConnection()

class WorkflowManager:
    """Manages workflow execution, tracking, and persistence."""
    
    def __init__(self):
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.completed_workflows: List[Dict[str, Any]] = []
        self.workflow_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def create_workflow(self, course_request_id: int, config: Dict[str, Any]) -> str:
        """Create a new workflow and return its ID."""
        
        workflow_id = str(uuid.uuid4())
        
        workflow = {
            "workflow_id": workflow_id,
            "course_request_id": course_request_id,
            "status": "initialized",
            "created_at": datetime.utcnow().isoformat(),
            "config": config,
            "stages": {
                "planning": {"status": "pending", "start_time": None, "end_time": None},
                "content_creation": {"status": "pending", "start_time": None, "end_time": None},
                "quality_review": {"status": "pending", "start_time": None, "end_time": None}
            },
            "retry_count": 0,
            "error_log": [],
            "metrics": {
                "total_start_time": datetime.utcnow().isoformat(),
                "stage_durations": {},
                "agent_response_times": {}
            }
        }
        
        self.active_workflows[workflow_id] = workflow
        logger.info(f"Created workflow {workflow_id} for course request {course_request_id}")
        
        return workflow_id
    
    def update_workflow_stage(self, workflow_id: str, stage: str, status: str, 
                            result: Optional[Dict[str, Any]] = None) -> bool:
        """Update the status of a workflow stage."""
        
        if workflow_id not in self.active_workflows:
            logger.error(f"Workflow {workflow_id} not found")
            return False
        
        workflow = self.active_workflows[workflow_id]
        
        if stage not in workflow["stages"]:
            logger.error(f"Invalid stage {stage} for workflow {workflow_id}")
            return False
        
        # Update stage status
        stage_data = workflow["stages"][stage]
        old_status = stage_data["status"]
        stage_data["status"] = status
        
        # Track timing
        now = datetime.utcnow().isoformat()
        if status == "in_progress" and old_status == "pending":
            stage_data["start_time"] = now
        elif status in ["completed", "failed"]:
            stage_data["end_time"] = now
            if stage_data["start_time"]:
                start_time = datetime.fromisoformat(stage_data["start_time"])
                end_time = datetime.fromisoformat(now)
                duration = (end_time - start_time).total_seconds()
                workflow["metrics"]["stage_durations"][stage] = duration
        
        # Store result if provided
        if result:
            stage_data["result"] = result
        
        # Update overall workflow status
        self._update_workflow_status(workflow_id)
        
        logger.info(f"Updated workflow {workflow_id} stage {stage} to {status}")
        return True
    
    def _update_workflow_status(self, workflow_id: str):
        """Update overall workflow status based on stage statuses."""
        
        workflow = self.active_workflows[workflow_id]
        stages = workflow["stages"]
        
        # Check if any stage failed
        if any(stage["status"] == "failed" for stage in stages.values()):
            workflow["status"] = "failed"
            workflow["completion_time"] = datetime.utcnow().isoformat()
            self._archive_workflow(workflow_id)
            return
        
        # Check if all stages completed
        if all(stage["status"] == "completed" for stage in stages.values()):
            workflow["status"] = "completed"
            workflow["completion_time"] = datetime.utcnow().isoformat()
            self._archive_workflow(workflow_id)
            return
        
        # Check if any stage is in progress
        if any(stage["status"] == "in_progress" for stage in stages.values()):
            workflow["status"] = "in_progress"
            return
        
        # Otherwise, still queued/pending
        workflow["status"] = "queued"
    
    def _archive_workflow(self, workflow_id: str):
        """Move completed workflow to history."""
        
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows.pop(workflow_id)
            self.completed_workflows.append(workflow)
            
            # Keep only last 100 completed workflows
            if len(self.completed_workflows) > 100:
                self.completed_workflows = self.completed_workflows[-100:]
            
            logger.info(f"Archived workflow {workflow_id} with status {workflow['status']}")
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow."""
        
        # Check active workflows first
        if workflow_id in self.active_workflows:
            return self.active_workflows[workflow_id]
        
        # Check completed workflows
        for workflow in self.completed_workflows:
            if workflow["workflow_id"] == workflow_id:
                return workflow
        
        return None
    
    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all currently active workflows."""
        return list(self.active_workflows.values())
    
    def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get comprehensive workflow metrics."""
        
        total_workflows = len(self.completed_workflows) + len(self.active_workflows)
        completed_count = len(self.completed_workflows)
        failed_count = len([w for w in self.completed_workflows if w["status"] == "failed"])
        successful_count = completed_count - failed_count
        
        # Calculate average durations
        completed_workflows = [w for w in self.completed_workflows if w["status"] == "completed"]
        avg_duration = 0
        if completed_workflows:
            durations = []
            for workflow in completed_workflows:
                start_time = datetime.fromisoformat(workflow["metrics"]["total_start_time"])
                end_time = datetime.fromisoformat(workflow["completion_time"])
                durations.append((end_time - start_time).total_seconds())
            avg_duration = sum(durations) / len(durations)
        
        return {
            "total_workflows": total_workflows,
            "active_workflows": len(self.active_workflows),
            "completed_workflows": completed_count,
            "successful_workflows": successful_count,
            "failed_workflows": failed_count,
            "success_rate": (successful_count / total_workflows * 100) if total_workflows > 0 else 0,
            "average_duration": avg_duration,
            "current_load": len(self.active_workflows)
        }

class AgentHealthMonitor:
    """Monitors health and performance of all agents in the system."""
    
    def __init__(self):
        self.agent_endpoints = {
            "course_planner": os.getenv("COURSE_PLANNER_URL", "http://localhost:8101"),
            "content_creator": os.getenv("CONTENT_CREATOR_URL", "http://localhost:8102"),
            "quality_assurance": os.getenv("QUALITY_ASSURANCE_URL", "http://localhost:8103")
        }
        self.health_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.performance_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
    
    async def check_agent_health(self, agent_name: str) -> Dict[str, Any]:
        """Check health of a specific agent."""
        
        if agent_name not in self.agent_endpoints:
            return {
                "agent": agent_name,
                "healthy": False,
                "error": "Unknown agent",
                "checked_at": datetime.utcnow().isoformat()
            }
        
        endpoint = self.agent_endpoints[agent_name]
        
        try:
            import aiohttp
            
            start_time = time.time()
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{endpoint}/health") as response:
                    response_time = time.time() - start_time
                    
                    health_data = {
                        "agent": agent_name,
                        "healthy": response.status == 200,
                        "status_code": response.status,
                        "response_time": response_time,
                        "endpoint": endpoint,
                        "checked_at": datetime.utcnow().isoformat()
                    }
                    
                    if response.status == 200:
                        response_data = await response.json()
                        health_data["response"] = response_data
                    else:
                        health_data["error"] = f"HTTP {response.status}"
                    
                    # Record performance metrics
                    self.performance_metrics[agent_name]["last_response_time"] = response_time
                    self.performance_metrics[agent_name]["last_check"] = datetime.utcnow().isoformat()
                    
                    # Add to health history
                    self.health_history[agent_name].append(health_data)
                    if len(self.health_history[agent_name]) > 50:  # Keep last 50 checks
                        self.health_history[agent_name] = self.health_history[agent_name][-50:]
                    
                    return health_data
        
        except Exception as e:
            error_data = {
                "agent": agent_name,
                "healthy": False,
                "error": str(e),
                "endpoint": endpoint,
                "checked_at": datetime.utcnow().isoformat()
            }
            
            self.health_history[agent_name].append(error_data)
            return error_data
    
    async def check_all_agents_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all agents concurrently."""
        
        tasks = []
        for agent_name in self.agent_endpoints.keys():
            tasks.append(self.check_agent_health(agent_name))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_status = {}
        for i, result in enumerate(results):
            agent_name = list(self.agent_endpoints.keys())[i]
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
    
    def get_agent_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all agents."""
        
        summary = {}
        
        for agent_name in self.agent_endpoints.keys():
            agent_history = self.health_history.get(agent_name, [])
            
            if not agent_history:
                summary[agent_name] = {
                    "status": "no_data",
                    "uptime_percentage": 0,
                    "average_response_time": 0,
                    "last_check": None
                }
                continue
            
            # Calculate uptime percentage
            recent_checks = agent_history[-20:]  # Last 20 checks
            healthy_checks = [check for check in recent_checks if check.get("healthy", False)]
            uptime_percentage = (len(healthy_checks) / len(recent_checks)) * 100
            
            # Calculate average response time
            response_times = [check.get("response_time", 0) for check in recent_checks if check.get("response_time")]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            summary[agent_name] = {
                "status": "healthy" if uptime_percentage > 80 else "degraded",
                "uptime_percentage": uptime_percentage,
                "average_response_time": avg_response_time,
                "total_checks": len(agent_history),
                "last_check": agent_history[-1]["checked_at"] if agent_history else None,
                "health_trend": self._calculate_health_trend(agent_history)
            }
        
        return summary
    
    def _calculate_health_trend(self, health_history: List[Dict[str, Any]]) -> str:
        """Calculate health trend for an agent."""
        
        if len(health_history) < 5:
            return "insufficient_data"
        
        recent_checks = health_history[-10:]
        older_checks = health_history[-20:-10] if len(health_history) >= 20 else health_history[:-10]
        
        recent_health = sum(1 for check in recent_checks if check.get("healthy", False)) / len(recent_checks)
        older_health = sum(1 for check in older_checks if check.get("healthy", False)) / len(older_checks) if older_checks else 0
        
        if recent_health > older_health + 0.1:
            return "improving"
        elif recent_health < older_health - 0.1:
            return "degrading"
        else:
            return "stable"

class ConfigurationManager:
    """Manages system configuration and environment settings."""
    
    def __init__(self):
        self.config = self._load_configuration()
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        
        return {
            "agents": {
                "enabled": os.getenv("AGENTS_ENABLED", "true").lower() == "true",
                "fallback_to_traditional": os.getenv("FALLBACK_TO_TRADITIONAL", "true").lower() == "true",
                "max_concurrent_workflows": int(os.getenv("MAX_CONCURRENT_WORKFLOWS", "5")),
                "workflow_timeout_seconds": int(os.getenv("WORKFLOW_TIMEOUT_SECONDS", "600")),
                "agent_request_timeout": int(os.getenv("AGENT_REQUEST_TIMEOUT_SECONDS", "300"))
            },
            "quality": {
                "approval_threshold": int(os.getenv("QUALITY_APPROVAL_THRESHOLD", "80")),
                "enable_quality_gates": True,
                "max_retry_attempts": 3
            },
            "monitoring": {
                "health_check_interval": int(os.getenv("HEALTH_CHECK_INTERVAL_SECONDS", "30")),
                "metrics_retention_days": 7,
                "enable_performance_tracking": True
            },
            "database": {
                "url": os.getenv("DATABASE_URL", ""),
                "connection_pool_size": 10,
                "query_timeout_seconds": 30
            },
            "ai_services": {
                "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
                "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY", ""),
                "default_model": "gpt-4o-mini",
                "temperature": 0.3
            }
        }
    
    def get_config(self, key_path: str) -> Any:
        """Get configuration value by dot-separated key path."""
        
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def update_config(self, key_path: str, value: Any) -> bool:
        """Update configuration value by key path."""
        
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        logger.info(f"Updated configuration {key_path} = {value}")
        
        return True
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration and return status."""
        
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "missing_requirements": []
        }
        
        # Check required API keys
        if not self.config["ai_services"]["openai_api_key"] and not self.config["ai_services"]["anthropic_api_key"]:
            validation_results["errors"].append("No AI API keys configured")
            validation_results["valid"] = False
        
        # Check database configuration
        if not self.config["database"]["url"]:
            validation_results["warnings"].append("Database URL not configured")
        
        # Check agent endpoints
        required_agents = ["course_planner", "content_creator", "quality_assurance"]
        for agent in required_agents:
            endpoint_key = f"{agent.upper()}_URL"
            if not os.getenv(endpoint_key):
                validation_results["warnings"].append(f"Agent endpoint not configured: {endpoint_key}")
        
        # Validate timeout values
        if self.config["agents"]["workflow_timeout_seconds"] < 60:
            validation_results["warnings"].append("Workflow timeout may be too short")
        
        # Check resource limits
        max_workflows = self.config["agents"]["max_concurrent_workflows"]
        if max_workflows > 10:
            validation_results["warnings"].append("High concurrent workflow limit may impact performance")
        elif max_workflows < 1:
            validation_results["errors"].append("Invalid max concurrent workflows value")
            validation_results["valid"] = False
        
        return validation_results

class PerformanceTracker:
    """Tracks and analyzes system performance metrics."""
    
    def __init__(self):
        self.metrics_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.start_time = datetime.utcnow()
    
    def record_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a performance metric."""
        
        metric_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "value": value,
            "tags": tags or {}
        }
        
        self.metrics_data[metric_name].append(metric_entry)
        
        # Keep only recent metrics (last 1000 entries per metric)
        if len(self.metrics_data[metric_name]) > 1000:
            self.metrics_data[metric_name] = self.metrics_data[metric_name][-1000:]
    
    def get_metric_summary(self, metric_name: str, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get summary statistics for a metric within a time window."""
        
        if metric_name not in self.metrics_data:
            return {"error": f"Metric {metric_name} not found"}
        
        # Filter metrics within time window
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        recent_metrics = [
            metric for metric in self.metrics_data[metric_name]
            if datetime.fromisoformat(metric["timestamp"]) > cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No recent data available"}
        
        values = [metric["value"] for metric in recent_metrics]
        
        return {
            "metric_name": metric_name,
            "time_window_minutes": time_window_minutes,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "average": sum(values) / len(values),
            "latest": values[-1] if values else None,
            "trend": self._calculate_trend(values)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values."""
        
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple trend calculation using first and last quarters
        quarter_size = len(values) // 4
        if quarter_size < 1:
            return "insufficient_data"
        
        early_avg = sum(values[:quarter_size]) / quarter_size
        late_avg = sum(values[-quarter_size:]) / quarter_size
        
        change_percent = ((late_avg - early_avg) / early_avg) * 100 if early_avg != 0 else 0
        
        if change_percent > 5:
            return "increasing"
        elif change_percent < -5:
            return "decreasing"
        else:
            return "stable"
    
    def get_system_performance_overview(self) -> Dict[str, Any]:
        """Get comprehensive system performance overview."""
        
        uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
        
        overview = {
            "uptime_seconds": uptime_seconds,
            "uptime_formatted": self._format_duration(uptime_seconds),
            "metrics_tracked": len(self.metrics_data),
            "total_data_points": sum(len(metrics) for metrics in self.metrics_data.values()),
            "key_metrics": {}
        }
        
        # Add summaries for key metrics
        key_metrics = ["workflow_duration", "agent_response_time", "quality_score", "error_rate"]
        
        for metric in key_metrics:
            if metric in self.metrics_data:
                overview["key_metrics"][metric] = self.get_metric_summary(metric)
        
        return overview
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

# Global tool instances
workflow_manager = WorkflowManager()
health_monitor = AgentHealthMonitor()
config_manager = ConfigurationManager()
performance_tracker = PerformanceTracker()