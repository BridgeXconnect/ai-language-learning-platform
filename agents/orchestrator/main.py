"""
Agent Orchestrator - Central coordination service for multi-agent course generation workflow
Coordinates Course Planner → Content Creator → Quality Assurance agents
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio
import aiohttp
from enum import Enum
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from workflow import CourseGenerationWorkflow
from agent_client import AgentClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    CONTENT_CREATION = "content_creation"
    QUALITY_REVIEW = "quality_review"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CourseGenerationRequest(BaseModel):
    course_request_id: int
    company_name: str
    industry: str
    training_goals: str
    current_english_level: str
    duration_weeks: int = 8
    target_audience: str = "Professional staff"
    specific_needs: Optional[str] = None
    workflow_config: Optional[Dict[str, Any]] = None

class WorkflowResult(BaseModel):
    workflow_id: str
    status: WorkflowStatus
    course_request_id: int
    start_time: str
    completion_time: Optional[str] = None
    total_duration_seconds: Optional[float] = None
    
    # Agent results
    planning_result: Optional[Dict[str, Any]] = None
    content_result: Optional[Dict[str, Any]] = None
    quality_result: Optional[Dict[str, Any]] = None
    
    # Final output
    final_course: Optional[Dict[str, Any]] = None
    quality_score: Optional[float] = None
    approved_for_release: Optional[bool] = None
    
    # Error handling
    error_message: Optional[str] = None
    failed_stage: Optional[str] = None
    retry_count: int = 0

class OrchestrationDeps(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    workflow: CourseGenerationWorkflow
    agent_client: AgentClient

# Agent system prompt
SYSTEM_PROMPT = """
You are the Agent Orchestrator for a sophisticated multi-agent course generation system. Your role is to coordinate three specialized AI agents to transform course requests into high-quality, complete English language training courses.

Workflow Overview:
1. **Course Planner Agent**: Analyzes SOPs and creates curriculum structures
2. **Content Creator Agent**: Generates detailed lessons, exercises, and assessments
3. **Quality Assurance Agent**: Reviews and improves content for quality and effectiveness

Your Responsibilities:
- Coordinate the sequential workflow between agents
- Handle error recovery and retry logic
- Ensure data consistency across agent interactions
- Monitor workflow progress and provide status updates
- Optimize workflow performance and reliability
- Maintain audit trails for all agent interactions

Orchestration Principles:
- **Reliability**: Implement robust error handling and recovery mechanisms
- **Efficiency**: Optimize agent interactions and minimize redundant processing
- **Quality**: Ensure each stage produces high-quality outputs before proceeding
- **Transparency**: Provide clear status updates and detailed logging
- **Scalability**: Support concurrent workflow execution and load management

Quality Gates:
- Planning stage must achieve >80% completeness score
- Content creation must generate all required components
- Quality review must achieve >80% overall quality score
- Final approval requires QA agent sign-off

Error Handling Strategy:
- Automatic retry with exponential backoff for transient failures
- Intelligent error recovery based on failure type and stage
- Graceful degradation with fallback mechanisms
- Comprehensive error logging and alerting
"""

# Create the orchestrator agent
orchestrator_agent = Agent(
    'openai:gpt-4o',
    system_prompt=SYSTEM_PROMPT,
    deps_type=OrchestrationDeps
)

@orchestrator_agent.tool
async def execute_workflow(ctx: RunContext[OrchestrationDeps], request: CourseGenerationRequest) -> Dict[str, Any]:
    """Execute the complete course generation workflow."""
    result = await ctx.deps.workflow.execute_complete_workflow(request)
    logger.info(f"Workflow execution completed for course request {request.course_request_id}")
    return result

@orchestrator_agent.tool
async def check_agent_health(ctx: RunContext[OrchestrationDeps]) -> Dict[str, Any]:
    """Check health status of all agents."""
    result = await ctx.deps.agent_client.check_all_agents_health()
    logger.info("Agent health check completed")
    return result

@orchestrator_agent.tool
async def retry_failed_stage(ctx: RunContext[OrchestrationDeps], workflow_id: str, failed_stage: str) -> Dict[str, Any]:
    """Retry a failed workflow stage."""
    result = await ctx.deps.workflow.retry_stage(workflow_id, failed_stage)
    logger.info(f"Stage retry completed for workflow {workflow_id}, stage {failed_stage}")
    return result

class AgentOrchestrator:
    """Main orchestrator service for multi-agent course generation."""
    
    def __init__(self):
        self.agent = orchestrator_agent
        self.workflow = CourseGenerationWorkflow()
        self.agent_client = AgentClient()
        self.deps = OrchestrationDeps(
            workflow=self.workflow,
            agent_client=self.agent_client
        )
        
        # Active workflows tracking
        self.active_workflows: Dict[str, WorkflowResult] = {}
        self.completed_workflows: List[WorkflowResult] = []
        
        # Performance metrics
        self.metrics = {
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "average_duration": 0.0,
            "agent_response_times": {},
            "error_rates": {}
        }
    
    async def orchestrate_workflow(self, request: CourseGenerationRequest) -> WorkflowResult:
        """Orchestrate the complete course generation workflow."""
        
        workflow_id = f"workflow_{request.course_request_id}_{int(datetime.utcnow().timestamp())}"
        start_time = datetime.utcnow()
        
        # Initialize workflow result
        workflow_result = WorkflowResult(
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            course_request_id=request.course_request_id,
            start_time=start_time.isoformat()
        )
        
        self.active_workflows[workflow_id] = workflow_result
        self.metrics["total_workflows"] += 1
        
        try:
            logger.info(f"Starting workflow {workflow_id} for {request.company_name}")
            
            # Pre-flight checks
            await self._perform_preflight_checks()
            
            # Execute workflow stages
            workflow_result = await self._execute_workflow_stages(workflow_result, request)
            
            # Final processing
            if workflow_result.status == WorkflowStatus.COMPLETED:
                await self._finalize_successful_workflow(workflow_result)
                self.metrics["successful_workflows"] += 1
            else:
                self.metrics["failed_workflows"] += 1
            
            # Update metrics
            completion_time = datetime.utcnow()
            duration = (completion_time - start_time).total_seconds()
            workflow_result.completion_time = completion_time.isoformat()
            workflow_result.total_duration_seconds = duration
            
            self._update_performance_metrics(duration)
            
            # Move to completed workflows
            self.completed_workflows.append(workflow_result)
            del self.active_workflows[workflow_id]
            
            logger.info(f"Workflow {workflow_id} completed with status: {workflow_result.status}")
            return workflow_result
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed with error: {e}")
            workflow_result.status = WorkflowStatus.FAILED
            workflow_result.error_message = str(e)
            workflow_result.completion_time = datetime.utcnow().isoformat()
            
            self.metrics["failed_workflows"] += 1
            self.completed_workflows.append(workflow_result)
            
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            return workflow_result
    
    async def _perform_preflight_checks(self):
        """Perform pre-flight checks before starting workflow."""
        
        logger.info("Performing pre-flight checks...")
        
        # Check agent health
        health_status = await self.agent_client.check_all_agents_health()
        
        unhealthy_agents = [agent for agent, status in health_status.items() if not status.get("healthy", False)]
        if unhealthy_agents:
            raise Exception(f"Unhealthy agents detected: {', '.join(unhealthy_agents)}")
        
        logger.info("Pre-flight checks completed successfully")
    
    async def _execute_workflow_stages(self, workflow_result: WorkflowResult, request: CourseGenerationRequest) -> WorkflowResult:
        """Execute all workflow stages sequentially."""
        
        try:
            # Stage 1: Course Planning
            workflow_result.status = WorkflowStatus.PLANNING
            workflow_result.planning_result = await self._execute_planning_stage(request)
            
            if not self._validate_planning_result(workflow_result.planning_result):
                raise Exception("Planning stage validation failed")
            
            # Stage 2: Content Creation
            workflow_result.status = WorkflowStatus.CONTENT_CREATION
            workflow_result.content_result = await self._execute_content_creation_stage(
                request, workflow_result.planning_result
            )
            
            if not self._validate_content_result(workflow_result.content_result):
                raise Exception("Content creation stage validation failed")
            
            # Stage 3: Quality Assurance
            workflow_result.status = WorkflowStatus.QUALITY_REVIEW
            workflow_result.quality_result = await self._execute_quality_assurance_stage(
                workflow_result.content_result
            )
            
            if not self._validate_quality_result(workflow_result.quality_result):
                # Attempt content improvement
                improved_content = await self._attempt_content_improvement(
                    workflow_result.content_result, workflow_result.quality_result
                )
                
                if improved_content:
                    workflow_result.content_result = improved_content
                    # Re-run quality check
                    workflow_result.quality_result = await self._execute_quality_assurance_stage(improved_content)
            
            # Final validation
            if self._validate_final_workflow(workflow_result):
                workflow_result.status = WorkflowStatus.COMPLETED
                workflow_result.final_course = self._compile_final_course(workflow_result)
                workflow_result.quality_score = workflow_result.quality_result.get("overall_score", 0)
                workflow_result.approved_for_release = workflow_result.quality_result.get("approved_for_release", False)
            else:
                workflow_result.status = WorkflowStatus.FAILED
                workflow_result.error_message = "Final workflow validation failed"
            
            return workflow_result
            
        except Exception as e:
            workflow_result.status = WorkflowStatus.FAILED
            workflow_result.error_message = str(e)
            workflow_result.failed_stage = workflow_result.status.value
            raise
    
    async def _execute_planning_stage(self, request: CourseGenerationRequest) -> Dict[str, Any]:
        """Execute the course planning stage."""
        
        logger.info("Executing course planning stage...")
        
        planning_request = {
            "course_request_id": request.course_request_id,
            "company_name": request.company_name,
            "industry": request.industry,
            "training_goals": request.training_goals,
            "current_english_level": request.current_english_level,
            "duration_weeks": request.duration_weeks,
            "target_audience": request.target_audience,
            "specific_needs": request.specific_needs
        }
        
        result = await self.agent_client.call_course_planner("plan_course", planning_request)
        
        if not result.get("success", False):
            raise Exception(f"Course planning failed: {result.get('error', 'Unknown error')}")
        
        logger.info("Course planning stage completed successfully")
        return result["curriculum"]
    
    async def _execute_content_creation_stage(self, request: CourseGenerationRequest, planning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the content creation stage."""
        
        logger.info("Executing content creation stage...")
        
        # Create lessons for each module
        lessons = []
        exercises = []
        assessments = []
        
        modules = planning_result.get("modules", [])
        
        for module in modules:
            # Create lesson content
            lesson_request = {
                "course_id": request.course_request_id,
                "lesson_title": module.get("title", "Module Lesson"),
                "module_context": module.get("description", ""),
                "vocabulary_themes": module.get("vocabulary_themes", []),
                "grammar_focus": module.get("grammar_focus", []),
                "cefr_level": request.current_english_level,
                "duration_minutes": module.get("duration_hours", 4) * 60,
                "company_context": {
                    "company_name": request.company_name,
                    "industry": request.industry
                }
            }
            
            lesson_result = await self.agent_client.call_content_creator("create_lesson_content", lesson_request)
            
            if lesson_result.get("success", False):
                lessons.append(lesson_result["content"])
                
                # Create exercises for this lesson
                exercise_request = {
                    "lesson_context": lesson_result["content"],
                    "exercise_types": ["multiple-choice", "fill-in-blank", "role-play", "writing-task"],
                    "exercise_count": 4,
                    "cefr_level": request.current_english_level
                }
                
                exercise_result = await self.agent_client.call_content_creator("create_exercises", exercise_request)
                
                if exercise_result.get("success", False):
                    exercises.extend(exercise_result["content"]["exercises"])
        
        # Create course assessment
        assessment_request = {
            "course_context": {
                "curriculum": planning_result,
                "lessons": lessons,
                "cefr_level": request.current_english_level
            },
            "assessment_type": "final",
            "duration_minutes": 60
        }
        
        assessment_result = await self.agent_client.call_content_creator("create_assessment", assessment_request)
        
        if assessment_result.get("success", False):
            assessments.append(assessment_result["content"])
        
        content_package = {
            "curriculum": planning_result,
            "lessons": lessons,
            "exercises": exercises,
            "assessments": assessments,
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "course_request_id": request.course_request_id,
                "content_stats": {
                    "total_lessons": len(lessons),
                    "total_exercises": len(exercises),
                    "total_assessments": len(assessments)
                }
            }
        }
        
        logger.info(f"Content creation completed: {len(lessons)} lessons, {len(exercises)} exercises, {len(assessments)} assessments")
        return content_package
    
    async def _execute_quality_assurance_stage(self, content_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the quality assurance stage."""
        
        logger.info("Executing quality assurance stage...")
        
        # Review the complete content package
        qa_request = {
            "content_id": f"course_{content_result['metadata']['course_request_id']}",
            "content_type": "course",
            "content_data": content_result,
            "target_cefr_level": content_result["curriculum"].get("cefr_level", "B1"),
            "review_criteria": ["linguistic_accuracy", "cefr_alignment", "pedagogical_effectiveness", "cultural_sensitivity"],
            "company_context": content_result.get("company_context", {})
        }
        
        result = await self.agent_client.call_quality_assurance("review_content", qa_request)
        
        if not result.get("success", False):
            raise Exception(f"Quality assurance failed: {result.get('error', 'Unknown error')}")
        
        qa_result = result["result"]
        
        logger.info(f"Quality assurance completed with score: {qa_result.get('overall_score', 'N/A')}")
        return qa_result
    
    async def _attempt_content_improvement(self, content_result: Dict[str, Any], qa_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Attempt to improve content based on QA feedback."""
        
        logger.info("Attempting content improvement based on QA feedback...")
        
        issues = qa_result.get("issues_found", [])
        if not issues:
            return None
        
        # Focus on critical and major issues
        critical_issues = [issue for issue in issues if issue.get("severity") in ["critical", "major"]]
        
        if not critical_issues:
            return None
        
        improvement_request = {
            "content": content_result,
            "quality_issues": critical_issues
        }
        
        try:
            result = await self.agent_client.call_quality_assurance("improve_content", improvement_request)
            
            if result.get("success", False):
                logger.info("Content improvement completed successfully")
                return result["result"]["improved_content"]
            else:
                logger.warning(f"Content improvement failed: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"Content improvement attempt failed: {e}")
            return None
    
    def _validate_planning_result(self, planning_result: Dict[str, Any]) -> bool:
        """Validate the planning stage result."""
        
        required_fields = ["title", "description", "modules", "learning_objectives"]
        
        for field in required_fields:
            if field not in planning_result or not planning_result[field]:
                logger.error(f"Planning validation failed: missing {field}")
                return False
        
        modules = planning_result.get("modules", [])
        if len(modules) < 1:
            logger.error("Planning validation failed: no modules generated")
            return False
        
        logger.info("Planning stage validation passed")
        return True
    
    def _validate_content_result(self, content_result: Dict[str, Any]) -> bool:
        """Validate the content creation stage result."""
        
        lessons = content_result.get("lessons", [])
        exercises = content_result.get("exercises", [])
        
        if len(lessons) < 1:
            logger.error("Content validation failed: no lessons generated")
            return False
        
        if len(exercises) < 1:
            logger.error("Content validation failed: no exercises generated")
            return False
        
        logger.info("Content creation stage validation passed")
        return True
    
    def _validate_quality_result(self, qa_result: Dict[str, Any]) -> bool:
        """Validate the quality assurance stage result."""
        
        overall_score = qa_result.get("overall_score", 0)
        approved = qa_result.get("approved_for_release", False)
        
        if overall_score < 80:
            logger.warning(f"Quality validation warning: score {overall_score} below threshold")
            return False
        
        if not approved:
            logger.warning("Quality validation failed: not approved for release")
            return False
        
        logger.info("Quality assurance stage validation passed")
        return True
    
    def _validate_final_workflow(self, workflow_result: WorkflowResult) -> bool:
        """Validate the complete workflow result."""
        
        if not workflow_result.planning_result:
            return False
        
        if not workflow_result.content_result:
            return False
        
        if not workflow_result.quality_result:
            return False
        
        return workflow_result.quality_result.get("approved_for_release", False)
    
    def _compile_final_course(self, workflow_result: WorkflowResult) -> Dict[str, Any]:
        """Compile the final course package."""
        
        return {
            "course_metadata": {
                "workflow_id": workflow_result.workflow_id,
                "course_request_id": workflow_result.course_request_id,
                "created_at": workflow_result.start_time,
                "completed_at": workflow_result.completion_time,
                "quality_score": workflow_result.quality_result.get("overall_score", 0)
            },
            "curriculum": workflow_result.planning_result,
            "content": workflow_result.content_result,
            "quality_report": workflow_result.quality_result,
            "status": "approved" if workflow_result.quality_result.get("approved_for_release", False) else "needs_review"
        }
    
    def _finalize_successful_workflow(self, workflow_result: WorkflowResult):
        """Finalize a successful workflow."""
        
        logger.info(f"Finalizing successful workflow {workflow_result.workflow_id}")
        
        # Here you could:
        # - Save to database
        # - Send notifications
        # - Update external systems
        # - Generate reports
        
    def _update_performance_metrics(self, duration: float):
        """Update performance metrics."""
        
        # Update average duration
        total = self.metrics["total_workflows"]
        current_avg = self.metrics["average_duration"]
        new_avg = ((current_avg * (total - 1)) + duration) / total
        self.metrics["average_duration"] = new_avg
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowResult]:
        """Get the status of a specific workflow."""
        
        # Check active workflows
        if workflow_id in self.active_workflows:
            return self.active_workflows[workflow_id]
        
        # Check completed workflows
        for workflow in self.completed_workflows:
            if workflow.workflow_id == workflow_id:
                return workflow
        
        return None
    
    async def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """Get orchestrator performance metrics."""
        
        agent_health = await self.agent_client.check_all_agents_health()
        
        return {
            "orchestrator_metrics": self.metrics,
            "active_workflows": len(self.active_workflows),
            "completed_workflows": len(self.completed_workflows),
            "agent_health": agent_health,
            "system_status": "operational" if all(status.get("healthy", False) for status in agent_health.values()) else "degraded"
        }
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow."""
        
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completion_time = datetime.utcnow().isoformat()
            
            self.completed_workflows.append(workflow)
            del self.active_workflows[workflow_id]
            
            logger.info(f"Workflow {workflow_id} cancelled")
            return True
        
        return False

# Global orchestrator instance
agent_orchestrator = AgentOrchestrator()

# Main execution for testing
async def main():
    """Test the agent orchestrator."""
    test_request = CourseGenerationRequest(
        course_request_id=1,
        company_name="TechCorp Solutions",
        industry="Technology",
        training_goals="Improve technical communication and client presentations",
        current_english_level="B1",
        duration_weeks=8,
        target_audience="Software developers and project managers"
    )
    
    try:
        workflow_result = await agent_orchestrator.orchestrate_workflow(test_request)
        print("Workflow Result:")
        print(json.dumps(workflow_result.dict(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())