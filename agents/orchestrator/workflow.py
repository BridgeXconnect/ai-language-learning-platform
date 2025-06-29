"""
LangGraph-style workflow implementation for multi-agent course generation
Manages the sequential execution of Course Planner → Content Creator → Quality Assurance
"""

import logging
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
from enum import Enum
import asyncio

from agent_client import AgentClient

logger = logging.getLogger(__name__)

class WorkflowState(TypedDict):
    """State object passed between workflow nodes."""
    workflow_id: str
    course_request: Dict[str, Any]
    planning_result: Optional[Dict[str, Any]]
    content_result: Optional[Dict[str, Any]]
    quality_result: Optional[Dict[str, Any]]
    current_stage: str
    errors: List[Dict[str, Any]]
    retry_count: int
    start_time: str

class WorkflowStage(str, Enum):
    """Workflow stage enumeration."""
    INIT = "init"
    PLANNING = "planning"
    CONTENT_CREATION = "content_creation"
    QUALITY_REVIEW = "quality_review"
    IMPROVEMENT = "improvement"
    FINALIZATION = "finalization"
    COMPLETED = "completed"
    FAILED = "failed"

class CourseGenerationWorkflow:
    """LangGraph-style workflow for course generation."""
    
    def __init__(self):
        self.agent_client = AgentClient()
        self.workflow_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Workflow configuration
        self.config = {
            "max_retries": 3,
            "retry_delay": 5,  # seconds
            "quality_threshold": 80,
            "planning_threshold": 75,
            "timeout_seconds": 300  # 5 minutes
        }
    
    async def execute_complete_workflow(self, request) -> Dict[str, Any]:
        """Execute the complete course generation workflow."""
        
        workflow_id = f"workflow_{request.course_request_id}_{int(datetime.utcnow().timestamp())}"
        
        # Initialize workflow state
        state = WorkflowState(
            workflow_id=workflow_id,
            course_request=request.dict(),
            planning_result=None,
            content_result=None,
            quality_result=None,
            current_stage=WorkflowStage.INIT,
            errors=[],
            retry_count=0,
            start_time=datetime.utcnow().isoformat()
        )
        
        self.workflow_history[workflow_id] = []
        
        try:
            logger.info(f"Starting workflow {workflow_id} for {request.company_name}")
            
            # Execute workflow graph
            final_state = await self._execute_workflow_graph(state)
            
            # Return final result
            return self._compile_workflow_result(final_state)
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}")
            state["current_stage"] = WorkflowStage.FAILED
            state["errors"].append({
                "stage": state["current_stage"],
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            return self._compile_workflow_result(state)
    
    async def _execute_workflow_graph(self, state: WorkflowState) -> WorkflowState:
        """Execute the workflow graph with conditional routing."""
        
        # Define workflow graph
        graph = {
            WorkflowStage.INIT: self._init_node,
            WorkflowStage.PLANNING: self._planning_node,
            WorkflowStage.CONTENT_CREATION: self._content_creation_node,
            WorkflowStage.QUALITY_REVIEW: self._quality_review_node,
            WorkflowStage.IMPROVEMENT: self._improvement_node,
            WorkflowStage.FINALIZATION: self._finalization_node
        }
        
        current_stage = WorkflowStage.INIT
        
        while current_stage not in [WorkflowStage.COMPLETED, WorkflowStage.FAILED]:
            try:
                state["current_stage"] = current_stage
                self._log_stage_entry(state, current_stage)
                
                # Execute current node
                node_func = graph.get(current_stage)
                if not node_func:
                    raise Exception(f"Unknown workflow stage: {current_stage}")
                
                state = await node_func(state)
                
                # Determine next stage
                current_stage = self._route_next_stage(state, current_stage)
                
                self._log_stage_completion(state, current_stage)
                
            except Exception as e:
                logger.error(f"Stage {current_stage} failed: {e}")
                state = await self._handle_stage_error(state, current_stage, str(e))
                
                # Check if we should retry or fail
                if state["retry_count"] >= self.config["max_retries"]:
                    current_stage = WorkflowStage.FAILED
                else:
                    # Retry current stage
                    await asyncio.sleep(self.config["retry_delay"])
                    state["retry_count"] += 1
        
        state["current_stage"] = current_stage
        return state
    
    async def _init_node(self, state: WorkflowState) -> WorkflowState:
        """Initialize the workflow."""
        
        logger.info(f"Initializing workflow {state['workflow_id']}")
        
        # Validate input
        course_request = state["course_request"]
        required_fields = ["course_request_id", "company_name", "industry", "current_english_level"]
        
        for field in required_fields:
            if not course_request.get(field):
                raise Exception(f"Missing required field: {field}")
        
        # Check agent availability
        health_status = await self.agent_client.check_all_agents_health()
        unhealthy_agents = [name for name, status in health_status.items() if not status.get("healthy", False)]
        
        if unhealthy_agents:
            raise Exception(f"Unhealthy agents: {', '.join(unhealthy_agents)}")
        
        logger.info("Workflow initialization completed")
        return state
    
    async def _planning_node(self, state: WorkflowState) -> WorkflowState:
        """Execute course planning stage."""
        
        logger.info("Executing course planning stage")
        
        course_request = state["course_request"]
        
        # Prepare planning request
        planning_request = {
            "course_request_id": course_request["course_request_id"],
            "company_name": course_request["company_name"],
            "industry": course_request["industry"],
            "training_goals": course_request["training_goals"],
            "current_english_level": course_request["current_english_level"],
            "duration_weeks": course_request.get("duration_weeks", 8),
            "target_audience": course_request.get("target_audience", "Professional staff"),
            "specific_needs": course_request.get("specific_needs")
        }
        
        # Call course planner agent
        result = await self.agent_client.call_course_planner("plan_course", planning_request)
        
        if not result.get("success", False):
            raise Exception(f"Course planning failed: {result.get('error', 'Unknown error')}")
        
        # Validate planning result
        planning_result = result["curriculum"]
        planning_score = self._calculate_planning_score(planning_result)
        
        if planning_score < self.config["planning_threshold"]:
            raise Exception(f"Planning quality too low: {planning_score}% < {self.config['planning_threshold']}%")
        
        state["planning_result"] = planning_result
        logger.info(f"Course planning completed with score: {planning_score}%")
        
        return state
    
    async def _content_creation_node(self, state: WorkflowState) -> WorkflowState:
        """Execute content creation stage."""
        
        logger.info("Executing content creation stage")
        
        course_request = state["course_request"]
        planning_result = state["planning_result"]
        
        if not planning_result:
            raise Exception("No planning result available for content creation")
        
        # Create content for each module
        lessons = []
        exercises = []
        assessments = []
        
        modules = planning_result.get("modules", [])
        
        for i, module in enumerate(modules):
            try:
                logger.info(f"Creating content for module {i+1}/{len(modules)}: {module.get('title', 'Unnamed')}")
                
                # Create lesson content
                lesson_request = {
                    "course_id": course_request["course_request_id"],
                    "lesson_title": module.get("title", f"Module {i+1} Lesson"),
                    "module_context": module.get("description", ""),
                    "vocabulary_themes": module.get("vocabulary_themes", []),
                    "grammar_focus": module.get("grammar_focus", []),
                    "cefr_level": course_request["current_english_level"],
                    "duration_minutes": module.get("duration_hours", 4) * 60,
                    "company_context": {
                        "company_name": course_request["company_name"],
                        "industry": course_request["industry"]
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
                        "cefr_level": course_request["current_english_level"]
                    }
                    
                    exercise_result = await self.agent_client.call_content_creator("create_exercises", exercise_request)
                    
                    if exercise_result.get("success", False):
                        exercises.extend(exercise_result["content"]["exercises"])
                    
            except Exception as e:
                logger.warning(f"Content creation failed for module {i+1}: {e}")
                # Continue with other modules
        
        # Create course assessment
        try:
            assessment_request = {
                "course_context": {
                    "curriculum": planning_result,
                    "lessons": lessons,
                    "cefr_level": course_request["current_english_level"]
                },
                "assessment_type": "final",
                "duration_minutes": 60
            }
            
            assessment_result = await self.agent_client.call_content_creator("create_assessment", assessment_request)
            
            if assessment_result.get("success", False):
                assessments.append(assessment_result["content"])
                
        except Exception as e:
            logger.warning(f"Assessment creation failed: {e}")
        
        # Compile content package
        content_package = {
            "curriculum": planning_result,
            "lessons": lessons,
            "exercises": exercises,
            "assessments": assessments,
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "course_request_id": course_request["course_request_id"],
                "content_stats": {
                    "total_lessons": len(lessons),
                    "total_exercises": len(exercises),
                    "total_assessments": len(assessments)
                }
            }
        }
        
        # Validate content creation
        if len(lessons) == 0:
            raise Exception("No lessons were successfully created")
        
        state["content_result"] = content_package
        logger.info(f"Content creation completed: {len(lessons)} lessons, {len(exercises)} exercises, {len(assessments)} assessments")
        
        return state
    
    async def _quality_review_node(self, state: WorkflowState) -> WorkflowState:
        """Execute quality review stage."""
        
        logger.info("Executing quality review stage")
        
        content_result = state["content_result"]
        course_request = state["course_request"]
        
        if not content_result:
            raise Exception("No content result available for quality review")
        
        # Prepare QA request
        qa_request = {
            "content_id": f"course_{course_request['course_request_id']}",
            "content_type": "course",
            "content_data": content_result,
            "target_cefr_level": course_request["current_english_level"],
            "review_criteria": ["linguistic_accuracy", "cefr_alignment", "pedagogical_effectiveness", "cultural_sensitivity"],
            "company_context": {
                "company_name": course_request["company_name"],
                "industry": course_request["industry"]
            }
        }
        
        # Call quality assurance agent
        result = await self.agent_client.call_quality_assurance("review_content", qa_request)
        
        if not result.get("success", False):
            raise Exception(f"Quality review failed: {result.get('error', 'Unknown error')}")
        
        qa_result = result["result"]
        overall_score = qa_result.get("overall_score", 0)
        
        state["quality_result"] = qa_result
        logger.info(f"Quality review completed with score: {overall_score}%")
        
        return state
    
    async def _improvement_node(self, state: WorkflowState) -> WorkflowState:
        """Execute content improvement stage."""
        
        logger.info("Executing content improvement stage")
        
        content_result = state["content_result"]
        quality_result = state["quality_result"]
        
        if not content_result or not quality_result:
            raise Exception("Missing content or quality result for improvement")
        
        issues = quality_result.get("issues_found", [])
        critical_issues = [issue for issue in issues if issue.get("severity") in ["critical", "major"]]
        
        if not critical_issues:
            logger.info("No critical issues found, skipping improvement")
            return state
        
        # Attempt content improvement
        improvement_request = {
            "content": content_result,
            "quality_issues": critical_issues
        }
        
        try:
            result = await self.agent_client.call_quality_assurance("improve_content", improvement_request)
            
            if result.get("success", False):
                improved_content = result["result"]["improved_content"]
                state["content_result"] = improved_content
                
                # Re-run quality check on improved content
                qa_request = {
                    "content_id": f"course_{state['course_request']['course_request_id']}_improved",
                    "content_type": "course",
                    "content_data": improved_content,
                    "target_cefr_level": state["course_request"]["current_english_level"],
                    "review_criteria": ["linguistic_accuracy", "cefr_alignment", "pedagogical_effectiveness", "cultural_sensitivity"]
                }
                
                qa_result = await self.agent_client.call_quality_assurance("review_content", qa_request)
                
                if qa_result.get("success", False):
                    state["quality_result"] = qa_result["result"]
                    logger.info(f"Content improved and re-reviewed: {qa_result['result'].get('overall_score', 0)}%")
                
        except Exception as e:
            logger.warning(f"Content improvement failed: {e}")
            # Continue with original content
        
        return state
    
    async def _finalization_node(self, state: WorkflowState) -> WorkflowState:
        """Finalize the workflow."""
        
        logger.info("Finalizing workflow")
        
        # Final validation
        if not state["planning_result"]:
            raise Exception("Missing planning result in finalization")
        
        if not state["content_result"]:
            raise Exception("Missing content result in finalization")
        
        if not state["quality_result"]:
            raise Exception("Missing quality result in finalization")
        
        # Check final quality score
        overall_score = state["quality_result"].get("overall_score", 0)
        approved = state["quality_result"].get("approved_for_release", False)
        
        if overall_score < self.config["quality_threshold"]:
            logger.warning(f"Final quality score {overall_score}% below threshold {self.config['quality_threshold']}%")
        
        if not approved:
            logger.warning("Content not approved for release by QA agent")
        
        logger.info(f"Workflow finalization completed with quality score: {overall_score}%")
        return state
    
    def _route_next_stage(self, state: WorkflowState, current_stage: WorkflowStage) -> WorkflowStage:
        """Determine the next stage based on current state."""
        
        stage_routing = {
            WorkflowStage.INIT: WorkflowStage.PLANNING,
            WorkflowStage.PLANNING: WorkflowStage.CONTENT_CREATION,
            WorkflowStage.CONTENT_CREATION: WorkflowStage.QUALITY_REVIEW,
            WorkflowStage.QUALITY_REVIEW: self._route_after_quality_review(state),
            WorkflowStage.IMPROVEMENT: WorkflowStage.FINALIZATION,
            WorkflowStage.FINALIZATION: WorkflowStage.COMPLETED
        }
        
        return stage_routing.get(current_stage, WorkflowStage.FAILED)
    
    def _route_after_quality_review(self, state: WorkflowState) -> WorkflowStage:
        """Route after quality review based on results."""
        
        quality_result = state.get("quality_result", {})
        overall_score = quality_result.get("overall_score", 0)
        issues = quality_result.get("issues_found", [])
        
        # Check for critical issues that need improvement
        critical_issues = [issue for issue in issues if issue.get("severity") in ["critical", "major"]]
        
        if overall_score < self.config["quality_threshold"] and critical_issues and state["retry_count"] < 2:
            return WorkflowStage.IMPROVEMENT
        else:
            return WorkflowStage.FINALIZATION
    
    async def _handle_stage_error(self, state: WorkflowState, stage: WorkflowStage, error: str) -> WorkflowState:
        """Handle stage execution errors."""
        
        error_info = {
            "stage": stage.value,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
            "retry_count": state["retry_count"]
        }
        
        state["errors"].append(error_info)
        
        # Log error details
        logger.error(f"Stage {stage.value} error (attempt {state['retry_count'] + 1}): {error}")
        
        return state
    
    def _calculate_planning_score(self, planning_result: Dict[str, Any]) -> float:
        """Calculate a quality score for the planning result."""
        
        score = 0
        max_score = 100
        
        # Check required fields (40 points)
        required_fields = ["title", "description", "modules", "learning_objectives"]
        for field in required_fields:
            if field in planning_result and planning_result[field]:
                score += 10
        
        # Check modules quality (30 points)
        modules = planning_result.get("modules", [])
        if modules:
            module_score = min(30, len(modules) * 5)  # 5 points per module, max 30
            score += module_score
        
        # Check learning objectives (15 points)
        objectives = planning_result.get("learning_objectives", [])
        if objectives and len(objectives) >= 3:
            score += 15
        
        # Check vocabulary themes (15 points)
        vocab_themes = planning_result.get("vocabulary_themes", [])
        if vocab_themes and len(vocab_themes) >= 2:
            score += 15
        
        return min(score, max_score)
    
    def _compile_workflow_result(self, state: WorkflowState) -> Dict[str, Any]:
        """Compile the final workflow result."""
        
        return {
            "workflow_id": state["workflow_id"],
            "status": state["current_stage"],
            "course_request_id": state["course_request"]["course_request_id"],
            "start_time": state["start_time"],
            "completion_time": datetime.utcnow().isoformat(),
            "planning_result": state.get("planning_result"),
            "content_result": state.get("content_result"),
            "quality_result": state.get("quality_result"),
            "errors": state["errors"],
            "retry_count": state["retry_count"],
            "success": state["current_stage"] == WorkflowStage.COMPLETED,
            "final_course": self._compile_final_course(state) if state["current_stage"] == WorkflowStage.COMPLETED else None
        }
    
    def _compile_final_course(self, state: WorkflowState) -> Dict[str, Any]:
        """Compile the final course package."""
        
        return {
            "course_metadata": {
                "workflow_id": state["workflow_id"],
                "course_request_id": state["course_request"]["course_request_id"],
                "created_at": state["start_time"],
                "completed_at": datetime.utcnow().isoformat(),
                "quality_score": state["quality_result"].get("overall_score", 0) if state["quality_result"] else 0
            },
            "curriculum": state["planning_result"],
            "content": state["content_result"],
            "quality_report": state["quality_result"],
            "status": "approved" if state["quality_result"].get("approved_for_release", False) else "needs_review"
        }
    
    def _log_stage_entry(self, state: WorkflowState, stage: WorkflowStage):
        """Log stage entry."""
        
        workflow_id = state["workflow_id"]
        self.workflow_history[workflow_id].append({
            "stage": stage.value,
            "action": "entered",
            "timestamp": datetime.utcnow().isoformat(),
            "retry_count": state["retry_count"]
        })
        
        logger.info(f"Workflow {workflow_id} entering stage: {stage.value}")
    
    def _log_stage_completion(self, state: WorkflowState, next_stage: WorkflowStage):
        """Log stage completion."""
        
        workflow_id = state["workflow_id"]
        self.workflow_history[workflow_id].append({
            "stage": state["current_stage"],
            "action": "completed",
            "next_stage": next_stage.value,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Workflow {workflow_id} completed stage: {state['current_stage']} → {next_stage.value}")
    
    async def retry_stage(self, workflow_id: str, stage: str) -> Dict[str, Any]:
        """Retry a specific workflow stage."""
        
        # This would be implemented to retry specific stages
        # For now, return a placeholder
        return {
            "workflow_id": workflow_id,
            "stage": stage,
            "retry_status": "not_implemented",
            "message": "Stage retry functionality to be implemented"
        }
    
    def get_workflow_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get the execution history for a workflow."""
        
        return self.workflow_history.get(workflow_id, [])