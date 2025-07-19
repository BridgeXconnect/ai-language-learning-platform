"""
LangGraph-based workflow implementation for multi-agent course generation
Manages the sequential execution of Course Planner → Content Creator → Quality Assurance
"""

import logging
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from datetime import datetime
from enum import Enum
import asyncio
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, AIMessage

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
    errors: Annotated[List[Dict[str, Any]], operator.add]
    retry_count: int
    start_time: str
    messages: Annotated[List[Any], operator.add]

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
    """LangGraph-based workflow for course generation."""
    
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
        
        # Build the workflow graph
        self.graph = self._build_workflow_graph()
    
    def _build_workflow_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("init", self._init_node)
        workflow.add_node("planning", self._planning_node)
        workflow.add_node("content_creation", self._content_creation_node)
        workflow.add_node("quality_review", self._quality_review_node)
        workflow.add_node("improvement", self._improvement_node)
        workflow.add_node("finalization", self._finalization_node)
        
        # Set entry point
        workflow.set_entry_point("init")
        
        # Add edges
        workflow.add_edge("init", "planning")
        workflow.add_conditional_edges(
            "planning",
            self._route_after_planning,
            {
                "continue": "content_creation",
                "retry": "planning",
                "fail": END
            }
        )
        workflow.add_edge("content_creation", "quality_review")
        workflow.add_conditional_edges(
            "quality_review",
            self._route_after_quality_review,
            {
                "continue": "finalization",
                "improve": "improvement",
                "retry": "content_creation",
                "fail": END
            }
        )
        workflow.add_edge("improvement", "quality_review")
        workflow.add_edge("finalization", END)
        
        return workflow.compile()
    
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
            start_time=datetime.utcnow().isoformat(),
            messages=[]
        )
        
        self.workflow_history[workflow_id] = []
        
        try:
            logger.info(f"Starting workflow {workflow_id} for {request.company_name}")
            
            # Execute workflow using LangGraph
            final_state = await self.graph.ainvoke(state)
            
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
        
        planning_result = state["planning_result"]
        course_request = state["course_request"]
        
        # Prepare content creation request
        content_request = {
            "course_request_id": course_request["course_request_id"],
            "curriculum": planning_result,
            "company_name": course_request["company_name"],
            "industry": course_request["industry"],
            "current_english_level": course_request["current_english_level"]
        }
        
        # Call content creator agent
        result = await self.agent_client.call_content_creator("create_content", content_request)
        
        if not result.get("success", False):
            raise Exception(f"Content creation failed: {result.get('error', 'Unknown error')}")
        
        # Validate content result
        content_result = result["content"]
        if not self._validate_content_result(content_result):
            raise Exception("Content creation produced invalid result")
        
        state["content_result"] = content_result
        logger.info("Content creation completed successfully")
        
        return state
    
    async def _quality_review_node(self, state: WorkflowState) -> WorkflowState:
        """Execute quality assurance stage."""
        
        logger.info("Executing quality assurance stage")
        
        content_result = state["content_result"]
        course_request = state["course_request"]
        
        # Prepare QA request
        qa_request = {
            "course_request_id": course_request["course_request_id"],
            "content": content_result,
            "company_name": course_request["company_name"],
            "industry": course_request["industry"],
            "current_english_level": course_request["current_english_level"]
        }
        
        # Call quality assurance agent
        result = await self.agent_client.call_quality_assurance("review_content", qa_request)
        
        if not result.get("success", False):
            raise Exception(f"Quality review failed: {result.get('error', 'Unknown error')}")
        
        # Validate QA result
        qa_result = result["qa_report"]
        quality_score = qa_result.get("overall_score", 0)
        
        if quality_score < self.config["quality_threshold"]:
            logger.warning(f"Quality score {quality_score}% below threshold {self.config['quality_threshold']}%")
        
        state["quality_result"] = qa_result
        logger.info(f"Quality review completed with score: {quality_score}%")
        
        return state
    
    async def _improvement_node(self, state: WorkflowState) -> WorkflowState:
        """Execute content improvement stage."""
        
        logger.info("Executing content improvement stage")
        
        content_result = state["content_result"]
        qa_result = state["quality_result"]
        course_request = state["course_request"]
        
        # Prepare improvement request
        improvement_request = {
            "course_request_id": course_request["course_request_id"],
            "content": content_result,
            "qa_report": qa_result,
            "company_name": course_request["company_name"],
            "industry": course_request["industry"]
        }
        
        # Call content creator for improvements
        result = await self.agent_client.call_content_creator("improve_content", improvement_request)
        
        if not result.get("success", False):
            raise Exception(f"Content improvement failed: {result.get('error', 'Unknown error')}")
        
        # Update content result
        improved_content = result["improved_content"]
        state["content_result"] = improved_content
        logger.info("Content improvement completed")
        
        return state
    
    async def _finalization_node(self, state: WorkflowState) -> WorkflowState:
        """Execute finalization stage."""
        
        logger.info("Executing finalization stage")
        
        # Compile final course
        final_course = self._compile_final_course(state)
        state["final_course"] = final_course
        state["current_stage"] = WorkflowStage.COMPLETED
        
        logger.info("Workflow finalization completed")
        
        return state
    
    def _route_after_planning(self, state: WorkflowState) -> str:
        """Route after planning stage."""
        
        if state["retry_count"] >= self.config["max_retries"]:
            return "fail"
        
        planning_result = state["planning_result"]
        if not planning_result:
            return "retry"
        
        planning_score = self._calculate_planning_score(planning_result)
        if planning_score >= self.config["planning_threshold"]:
            return "continue"
        else:
            return "retry"
    
    def _route_after_quality_review(self, state: WorkflowState) -> str:
        """Route after quality review stage."""
        
        if state["retry_count"] >= self.config["max_retries"]:
            return "fail"
        
        qa_result = state["quality_result"]
        if not qa_result:
            return "retry"
        
        quality_score = qa_result.get("overall_score", 0)
        
        if quality_score >= self.config["quality_threshold"]:
            return "continue"
        elif quality_score >= 60:  # Threshold for improvement vs retry
            return "improve"
        else:
            return "retry"
    
    def _calculate_planning_score(self, planning_result: Dict[str, Any]) -> float:
        """Calculate planning quality score."""
        
        if not planning_result:
            return 0.0
        
        score = 0.0
        total_checks = 0
        
        # Check for required curriculum components
        required_components = ["modules", "learning_objectives", "assessment_strategy"]
        for component in required_components:
            total_checks += 1
            if component in planning_result and planning_result[component]:
                score += 1.0
        
        # Check module completeness
        modules = planning_result.get("modules", [])
        if modules:
            total_checks += 1
            avg_module_completeness = sum(
                1.0 for module in modules 
                if module.get("title") and module.get("lessons")
            ) / len(modules)
            score += avg_module_completeness
        
        return (score / total_checks) * 100 if total_checks > 0 else 0.0
    
    def _validate_content_result(self, content_result: Dict[str, Any]) -> bool:
        """Validate content creation result."""
        
        if not content_result:
            return False
        
        # Check for required content components
        required_components = ["lessons", "exercises", "assessments"]
        for component in required_components:
            if component not in content_result or not content_result[component]:
                return False
        
        return True
    
    def _compile_final_course(self, state: WorkflowState) -> Dict[str, Any]:
        """Compile the final course from all results."""
        
        return {
            "workflow_id": state["workflow_id"],
            "course_request_id": state["course_request_id"],
            "company_name": state["course_request"]["company_name"],
            "curriculum": state["planning_result"],
            "content": state["content_result"],
            "quality_report": state["quality_result"],
            "metadata": {
                "created_at": state["start_time"],
                "total_duration": None,  # Would be calculated
                "quality_score": state["quality_result"].get("overall_score", 0) if state["quality_result"] else 0
            }
        }
    
    def _compile_workflow_result(self, state: WorkflowState) -> Dict[str, Any]:
        """Compile the final workflow result."""
        
        return {
            "workflow_id": state["workflow_id"],
            "status": state["current_stage"],
            "course_request_id": state["course_request_id"],
            "start_time": state["start_time"],
            "completion_time": datetime.utcnow().isoformat(),
            "planning_result": state.get("planning_result"),
            "content_result": state.get("content_result"),
            "quality_result": state.get("quality_result"),
            "final_course": state.get("final_course"),
            "errors": state["errors"],
            "retry_count": state["retry_count"]
        }
    
    async def retry_stage(self, workflow_id: str, stage: str) -> Dict[str, Any]:
        """Retry a failed workflow stage."""
        
        # This would need to be implemented with proper state management
        # For now, return a placeholder
        return {
            "success": False,
            "error": "Retry functionality not yet implemented"
        }
    
    def get_workflow_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get workflow execution history."""
        
        return self.workflow_history.get(workflow_id, [])