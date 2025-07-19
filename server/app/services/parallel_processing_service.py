"""
Parallel Processing Service for AI Language Learning Platform
Implements concurrent course generation and optimized agent communication protocols.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass
from datetime import datetime
import time
import json

logger = logging.getLogger(__name__)

@dataclass
class ProcessingTask:
    """Represents a processing task for parallel execution."""
    task_id: str
    task_type: str
    priority: int
    payload: Dict[str, Any]
    created_at: datetime
    estimated_duration: float
    dependencies: List[str] = None
    status: str = "pending"
    result: Any = None
    error: str = None

class ParallelProcessingService:
    """Service for managing parallel processing of AI tasks."""
    
    def __init__(self, max_workers: int = 4, max_processes: int = 2):
        self.max_workers = max_workers
        self.max_processes = max_processes
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=max_processes)
        self.active_tasks: Dict[str, ProcessingTask] = {}
        self.task_queue: List[ProcessingTask] = []
        self.completed_tasks: Dict[str, ProcessingTask] = {}
        self.processing_stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_processing_time": 0.0,
            "total_processing_time": 0.0
        }
        logger.info(f"ParallelProcessingService initialized with {max_workers} threads and {max_processes} processes")
    
    async def submit_task(self, task_type: str, payload: Dict[str, Any], 
                         priority: int = 1, dependencies: List[str] = None) -> str:
        """Submit a task for parallel processing."""
        task_id = f"{task_type}_{int(time.time() * 1000)}"
        
        task = ProcessingTask(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            payload=payload,
            created_at=datetime.now(),
            estimated_duration=self._estimate_duration(task_type, payload),
            dependencies=dependencies or []
        )
        
        self.active_tasks[task_id] = task
        self.task_queue.append(task)
        self.processing_stats["total_tasks"] += 1
        
        # Sort queue by priority (higher priority first)
        self.task_queue.sort(key=lambda x: x.priority, reverse=True)
        
        logger.info(f"Submitted task {task_id} of type {task_type} with priority {priority}")
        return task_id
    
    async def process_course_generation_parallel(self, course_request: Dict[str, Any]) -> Dict[str, Any]:
        """Process course generation using parallel execution."""
        logger.info("Starting parallel course generation")
        start_time = time.time()
        
        # Break down course generation into parallel tasks
        tasks = [
            ("content_analysis", {"request": course_request}),
            ("curriculum_planning", {"request": course_request}),
            ("learning_objectives", {"request": course_request}),
            ("assessment_framework", {"request": course_request})
        ]
        
        # Submit all tasks
        task_ids = []
        for task_type, payload in tasks:
            task_id = await self.submit_task(task_type, payload, priority=2)
            task_ids.append(task_id)
        
        # Wait for all tasks to complete
        results = await self.wait_for_tasks(task_ids)
        
        # Combine results
        course_data = {
            "content_analysis": results.get("content_analysis", {}),
            "curriculum": results.get("curriculum_planning", {}),
            "objectives": results.get("learning_objectives", {}),
            "assessments": results.get("assessment_framework", {}),
            "generation_time": time.time() - start_time
        }
        
        logger.info(f"Parallel course generation completed in {course_data['generation_time']:.2f} seconds")
        return course_data
    
    async def process_agent_communication_parallel(self, agent_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process multiple agent communications in parallel."""
        logger.info(f"Starting parallel agent communication for {len(agent_tasks)} tasks")
        
        # Submit agent tasks
        task_ids = []
        for i, agent_task in enumerate(agent_tasks):
            task_id = await self.submit_task(
                "agent_communication",
                agent_task,
                priority=agent_task.get("priority", 1)
            )
            task_ids.append(task_id)
        
        # Wait for completion
        results = await self.wait_for_tasks(task_ids)
        
        return {
            "agent_responses": results,
            "total_agents": len(agent_tasks),
            "successful_communications": len([r for r in results.values() if r.get("success", False)])
        }
    
    async def wait_for_tasks(self, task_ids: List[str], timeout: float = 300.0) -> Dict[str, Any]:
        """Wait for multiple tasks to complete."""
        start_time = time.time()
        results = {}
        
        while task_ids and (time.time() - start_time) < timeout:
            completed_tasks = []
            
            for task_id in task_ids:
                if task_id in self.completed_tasks:
                    task = self.completed_tasks[task_id]
                    results[task.task_type] = task.result
                    completed_tasks.append(task_id)
                    logger.info(f"Task {task_id} completed successfully")
            
            # Remove completed tasks from waiting list
            for task_id in completed_tasks:
                task_ids.remove(task_id)
            
            if task_ids:
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
        
        if task_ids:
            logger.warning(f"Timeout waiting for tasks: {task_ids}")
        
        return results
    
    async def execute_task(self, task: ProcessingTask) -> Any:
        """Execute a single task based on its type."""
        try:
            task.status = "processing"
            start_time = time.time()
            
            if task.task_type == "content_analysis":
                result = await self._analyze_content(task.payload)
            elif task.task_type == "curriculum_planning":
                result = await self._plan_curriculum(task.payload)
            elif task.task_type == "learning_objectives":
                result = await self._create_learning_objectives(task.payload)
            elif task.task_type == "assessment_framework":
                result = await self._create_assessment_framework(task.payload)
            elif task.task_type == "agent_communication":
                result = await self._communicate_with_agent(task.payload)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            processing_time = time.time() - start_time
            task.result = result
            task.status = "completed"
            
            # Update statistics
            self.processing_stats["completed_tasks"] += 1
            self.processing_stats["total_processing_time"] += processing_time
            self.processing_stats["average_processing_time"] = (
                self.processing_stats["total_processing_time"] / 
                self.processing_stats["completed_tasks"]
            )
            
            logger.info(f"Task {task.task_id} completed in {processing_time:.2f} seconds")
            return result
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            self.processing_stats["failed_tasks"] += 1
            logger.error(f"Task {task.task_id} failed: {e}")
            raise
    
    async def _analyze_content(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content for course generation."""
        # Simulate content analysis
        await asyncio.sleep(2)  # Simulate processing time
        return {
            "content_type": "business_english",
            "complexity_level": "intermediate",
            "key_topics": ["communication", "presentations", "meetings"],
            "estimated_hours": 20
        }
    
    async def _plan_curriculum(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Plan curriculum structure."""
        await asyncio.sleep(1.5)
        return {
            "modules": [
                {"title": "Business Communication", "hours": 8},
                {"title": "Presentation Skills", "hours": 6},
                {"title": "Meeting Management", "hours": 6}
            ],
            "total_hours": 20
        }
    
    async def _create_learning_objectives(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create learning objectives."""
        await asyncio.sleep(1)
        return {
            "objectives": [
                "Improve business communication skills",
                "Develop presentation confidence",
                "Master meeting facilitation"
            ],
            "assessment_criteria": ["participation", "presentation", "communication"]
        }
    
    async def _create_assessment_framework(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create assessment framework."""
        await asyncio.sleep(1.5)
        return {
            "assessments": [
                {"type": "quiz", "weight": 30},
                {"type": "presentation", "weight": 40},
                {"type": "participation", "weight": 30}
            ],
            "passing_score": 70
        }
    
    async def _communicate_with_agent(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Communicate with an AI agent."""
        await asyncio.sleep(0.5)
        return {
            "agent_id": payload.get("agent_id"),
            "response": f"Response from agent {payload.get('agent_id')}",
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def _estimate_duration(self, task_type: str, payload: Dict[str, Any]) -> float:
        """Estimate task duration based on type and payload."""
        base_durations = {
            "content_analysis": 2.0,
            "curriculum_planning": 1.5,
            "learning_objectives": 1.0,
            "assessment_framework": 1.5,
            "agent_communication": 0.5
        }
        return base_durations.get(task_type, 1.0)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            **self.processing_stats,
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len(self.task_queue),
            "completed_tasks_count": len(self.completed_tasks)
        }
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        task = self.active_tasks.get(task_id) or self.completed_tasks.get(task_id)
        if task:
            return {
                "task_id": task.task_id,
                "status": task.status,
                "type": task.task_type,
                "priority": task.priority,
                "created_at": task.created_at.isoformat(),
                "result": task.result,
                "error": task.error
            }
        return None
    
    async def cleanup(self):
        """Clean up resources."""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        logger.info("ParallelProcessingService cleanup completed")

# Global instance
parallel_processor = ParallelProcessingService() 