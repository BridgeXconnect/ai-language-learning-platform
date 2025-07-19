"""
Pydantic-AI based agent client for orchestrating multi-agent course generation
Provides structured communication with Course Planner, Content Creator, and Quality Assurance agents
"""

import logging
import asyncio
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel, Field

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIResponsesModel

logger = logging.getLogger(__name__)

# Pydantic models for structured communication
class CourseRequest(BaseModel):
    """Structured course request model."""
    course_request_id: str
    company_name: str
    industry: str
    training_goals: List[str]
    current_english_level: str
    duration_weeks: int = Field(default=8, ge=1, le=52)
    target_audience: str = "Professional staff"
    specific_needs: Optional[str] = None

class PlanningRequest(BaseModel):
    """Structured planning request model."""
    course_request_id: str
    company_name: str
    industry: str
    training_goals: List[str]
    current_english_level: str
    duration_weeks: int
    target_audience: str
    specific_needs: Optional[str] = None

class ContentRequest(BaseModel):
    """Structured content creation request model."""
    course_request_id: str
    curriculum: Dict[str, Any]
    company_name: str
    industry: str
    current_english_level: str

class QualityRequest(BaseModel):
    """Structured quality assurance request model."""
    course_request_id: str
    content: Dict[str, Any]
    company_name: str
    industry: str
    current_english_level: str

class ImprovementRequest(BaseModel):
    """Structured content improvement request model."""
    course_request_id: str
    content: Dict[str, Any]
    qa_report: Dict[str, Any]
    company_name: str
    industry: str

@dataclass
class AgentDependencies:
    """Dependencies for agent operations."""
    http_client: httpx.AsyncClient
    base_urls: Dict[str, str]
    api_keys: Dict[str, str]

class AgentClient:
    """Pydantic-AI based client for orchestrating multi-agent course generation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the agent client."""
        
        self.config = config or {}
        self.base_urls = {
            "course_planner": self.config.get("course_planner_url", "http://localhost:8001"),
            "content_creator": self.config.get("content_creator_url", "http://localhost:8002"),
            "quality_assurance": self.config.get("quality_assurance_url", "http://localhost:8003"),
            "ai_tutor": self.config.get("ai_tutor_url", "http://localhost:8004")
        }
        
        self.api_keys = {
            "openai": self.config.get("openai_api_key"),
            "anthropic": self.config.get("anthropic_api_key")
        }
        
        # Initialize Pydantic-AI agents
        self._init_agents()
        
        # HTTP client for direct API calls
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Agent dependencies
        self.deps = AgentDependencies(
            http_client=self.http_client,
            base_urls=self.base_urls,
            api_keys=self.api_keys
        )
    
    def _init_agents(self):
        """Initialize Pydantic-AI agents for each role."""
        
        # Course Planner Agent
        self.course_planner_agent = Agent(
            'openai:gpt-4o',
            deps_type=AgentDependencies,
            output_type=Dict[str, Any],
            system_prompt=(
                "You are a course planning specialist. Create comprehensive curriculum plans "
                "for English language training programs tailored to specific companies and industries. "
                "Focus on practical, business-oriented content that addresses real workplace needs."
            )
        )
        
        # Content Creator Agent
        self.content_creator_agent = Agent(
            'openai:gpt-4o',
            deps_type=AgentDependencies,
            output_type=Dict[str, Any],
            system_prompt=(
                "You are a content creation specialist. Generate high-quality educational content "
                "including lessons, exercises, and assessments based on curriculum plans. "
                "Ensure content is engaging, practical, and aligned with learning objectives."
            )
        )
        
        # Quality Assurance Agent
        self.quality_assurance_agent = Agent(
            'openai:gpt-4o',
            deps_type=AgentDependencies,
            output_type=Dict[str, Any],
            system_prompt=(
                "You are a quality assurance specialist. Review educational content for accuracy, "
                "effectiveness, and alignment with learning objectives. Provide detailed feedback "
                "and quality scores with specific improvement recommendations."
            )
        )
        
        # Register tools for each agent
        self._register_course_planner_tools()
        self._register_content_creator_tools()
        self._register_quality_assurance_tools()
    
    def _register_course_planner_tools(self):
        """Register tools for the course planner agent."""
        
        @self.course_planner_agent.tool
        async def call_course_planner_api(ctx: RunContext[AgentDependencies], request: Dict[str, Any]) -> Dict[str, Any]:
            """Call the course planner API directly."""
            try:
                response = await ctx.deps.http_client.post(
                    f"{ctx.deps.base_urls['course_planner']}/plan_course",
                    json=request,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Course planner API call failed: {e}")
                return {"success": False, "error": str(e)}
        
        @self.course_planner_agent.tool
        async def validate_planning_request(ctx: RunContext[AgentDependencies], request: Dict[str, Any]) -> Dict[str, Any]:
            """Validate the planning request structure."""
            try:
                planning_request = PlanningRequest(**request)
                return {"success": True, "validated_request": planning_request.dict()}
            except Exception as e:
                return {"success": False, "error": f"Validation failed: {e}"}
    
    def _register_content_creator_tools(self):
        """Register tools for the content creator agent."""
        
        @self.content_creator_agent.tool
        async def call_content_creator_api(ctx: RunContext[AgentDependencies], request: Dict[str, Any]) -> Dict[str, Any]:
            """Call the content creator API directly."""
            try:
                response = await ctx.deps.http_client.post(
                    f"{ctx.deps.base_urls['content_creator']}/create_content",
                    json=request,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Content creator API call failed: {e}")
                return {"success": False, "error": str(e)}
        
        @self.content_creator_agent.tool
        async def validate_content_request(ctx: RunContext[AgentDependencies], request: Dict[str, Any]) -> Dict[str, Any]:
            """Validate the content creation request structure."""
            try:
                content_request = ContentRequest(**request)
                return {"success": True, "validated_request": content_request.dict()}
            except Exception as e:
                return {"success": False, "error": f"Validation failed: {e}"}
    
    def _register_quality_assurance_tools(self):
        """Register tools for the quality assurance agent."""
        
        @self.quality_assurance_agent.tool
        async def call_quality_assurance_api(ctx: RunContext[AgentDependencies], request: Dict[str, Any]) -> Dict[str, Any]:
            """Call the quality assurance API directly."""
            try:
                response = await ctx.deps.http_client.post(
                    f"{ctx.deps.base_urls['quality_assurance']}/review_content",
                    json=request,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Quality assurance API call failed: {e}")
                return {"success": False, "error": str(e)}
        
        @self.quality_assurance_agent.tool
        async def validate_quality_request(ctx: RunContext[AgentDependencies], request: Dict[str, Any]) -> Dict[str, Any]:
            """Validate the quality assurance request structure."""
            try:
                quality_request = QualityRequest(**request)
                return {"success": True, "validated_request": quality_request.dict()}
            except Exception as e:
                return {"success": False, "error": f"Validation failed: {e}"}
    
    async def call_course_planner(self, action: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Call the course planner agent."""
        
        try:
            logger.info(f"Calling course planner agent for action: {action}")
            
            # Prepare the prompt based on action
            if action == "plan_course":
                prompt = f"""
                Create a comprehensive course plan for the following request:
                
                Company: {request.get('company_name')}
                Industry: {request.get('industry')}
                Training Goals: {request.get('training_goals')}
                Current English Level: {request.get('current_english_level')}
                Duration: {request.get('duration_weeks')} weeks
                Target Audience: {request.get('target_audience')}
                Specific Needs: {request.get('specific_needs', 'None specified')}
                
                Please create a detailed curriculum plan including:
                1. Course overview and objectives
                2. Module breakdown with learning outcomes
                3. Assessment strategy
                4. Vocabulary themes and grammar focus areas
                5. Practical exercises and activities
                """
            else:
                prompt = f"Execute action '{action}' with the provided request data."
            
            # Call the Pydantic-AI agent
            result = await self.course_planner_agent.run(prompt, deps=self.deps)
            
            # Process the result
            if result.output:
                return {
                    "success": True,
                    "curriculum": result.output,
                    "usage": result.usage().dict() if result.usage() else None
                }
            else:
                return {"success": False, "error": "No output from course planner agent"}
                
        except Exception as e:
            logger.error(f"Course planner agent call failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def call_content_creator(self, action: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Call the content creator agent."""
        
        try:
            logger.info(f"Calling content creator agent for action: {action}")
            
            # Prepare the prompt based on action
            if action == "create_content":
                curriculum = request.get('curriculum', {})
                prompt = f"""
                Create educational content based on the following curriculum:
                
                Company: {request.get('company_name')}
                Industry: {request.get('industry')}
                English Level: {request.get('current_english_level')}
                
                Curriculum Overview:
                {curriculum.get('title', 'No title')}
                {curriculum.get('description', 'No description')}
                
                Modules: {len(curriculum.get('modules', []))}
                
                Please create:
                1. Detailed lesson content for each module
                2. Interactive exercises and activities
                3. Assessment materials
                4. Supplementary resources
                
                Ensure content is engaging, practical, and aligned with the curriculum objectives.
                """
            elif action == "improve_content":
                prompt = f"""
                Improve the following content based on the quality assurance report:
                
                Content to improve: {request.get('content', {})}
                QA Report: {request.get('qa_report', {})}
                
                Address the issues identified in the QA report and enhance the content quality.
                """
            else:
                prompt = f"Execute action '{action}' with the provided request data."
            
            # Call the Pydantic-AI agent
            result = await self.content_creator_agent.run(prompt, deps=self.deps)
            
            # Process the result
            if result.output:
                return {
                    "success": True,
                    "content": result.output,
                    "usage": result.usage().dict() if result.usage() else None
                }
            else:
                return {"success": False, "error": "No output from content creator agent"}
                
        except Exception as e:
            logger.error(f"Content creator agent call failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def call_quality_assurance(self, action: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Call the quality assurance agent."""
        
        try:
            logger.info(f"Calling quality assurance agent for action: {action}")
            
            # Prepare the prompt based on action
            if action == "review_content":
                content = request.get('content', {})
                prompt = f"""
                Review the following educational content for quality and effectiveness:
                
                Company: {request.get('company_name')}
                Industry: {request.get('industry')}
                Target English Level: {request.get('current_english_level')}
                
                Content to review:
                {content}
                
                Please provide a comprehensive quality assessment including:
                1. Overall quality score (0-100)
                2. Linguistic accuracy assessment
                3. Pedagogical effectiveness evaluation
                4. CEFR level alignment check
                5. Cultural sensitivity review
                6. Specific issues and recommendations
                7. Approval status for release
                """
            else:
                prompt = f"Execute action '{action}' with the provided request data."
            
            # Call the Pydantic-AI agent
            result = await self.quality_assurance_agent.run(prompt, deps=self.deps)
            
            # Process the result
            if result.output:
                return {
                    "success": True,
                    "qa_report": result.output,
                    "usage": result.usage().dict() if result.usage() else None
                }
            else:
                return {"success": False, "error": "No output from quality assurance agent"}
                
        except Exception as e:
            logger.error(f"Quality assurance agent call failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_all_agents_health(self) -> Dict[str, Dict[str, Any]]:
        """Check the health status of all agents."""
        
        health_status = {}
        
        for agent_name, base_url in self.base_urls.items():
            try:
                response = await self.http_client.get(f"{base_url}/health", timeout=5.0)
                health_status[agent_name] = {
                    "healthy": response.status_code == 200,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "last_check": datetime.utcnow().isoformat()
                }
            except Exception as e:
                health_status[agent_name] = {
                    "healthy": False,
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
        
        return health_status
    
    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()