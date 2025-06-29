"""
Course Planning Specialist Agent
Analyzes company SOPs and creates comprehensive curriculum structures
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic import BaseModel, Field

from tools import (
    SOPDocumentAnalyzer,
    CEFRLevelMapper,
    CurriculumStructureGenerator,
    DatabaseQueryTool
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for structured input/output
class CourseRequest(BaseModel):
    course_request_id: int
    company_name: str
    industry: str
    training_goals: str
    current_english_level: str
    duration_weeks: int = 8
    target_audience: str = "Professional staff"
    specific_needs: Optional[str] = None

class CurriculumPlan(BaseModel):
    title: str
    description: str
    cefr_level: str
    duration_weeks: int
    learning_objectives: List[str]
    modules: List[Dict[str, Any]]
    vocabulary_themes: List[str]
    grammar_progression: List[str]
    assessment_strategy: Dict[str, Any]
    company_specific_content: Dict[str, Any]

class CoursePlannerDeps(BaseModel):
    sop_analyzer: SOPDocumentAnalyzer
    cefr_mapper: CEFRLevelMapper
    curriculum_generator: CurriculumStructureGenerator
    db_tool: DatabaseQueryTool

# Agent system prompt
SYSTEM_PROMPT = """
You are a specialist Course Planning Agent for corporate English language training. Your expertise lies in analyzing company Standard Operating Procedures (SOPs) and creating comprehensive, industry-specific curriculum structures that align with CEFR standards.

Key Responsibilities:
1. Analyze uploaded SOP documents to extract key business processes, vocabulary, and communication scenarios
2. Map content appropriateness to CEFR levels (A1-C2)
3. Create progressive curriculum structures that build from foundational to advanced skills
4. Generate detailed module and lesson outlines with clear learning objectives
5. Ensure content relevance to specific industries and company contexts

Approach:
- Start by thoroughly analyzing available SOP documents to understand company-specific language needs
- Map identified content to appropriate CEFR levels considering the target audience's current proficiency
- Structure curriculum progressively, building complexity while maintaining practical workplace relevance
- Integrate industry-specific vocabulary and scenarios throughout the curriculum
- Design assessments that reflect real workplace communication challenges

Quality Standards:
- All content must align with CEFR descriptors for the target level
- Curriculum should be achievable within the specified timeframe
- Learning objectives should be specific, measurable, and workplace-relevant
- Module progression should be logical and scaffolded appropriately
- Include diverse language skills: reading, writing, listening, speaking
"""

# Initialize the AI model
model = OpenAIModel('gpt-4o', api_key=os.getenv('OPENAI_API_KEY'))

# Create the agent
course_planner_agent = Agent(
    model,
    system_prompt=SYSTEM_PROMPT,
    deps_type=CoursePlannerDeps,
    result_type=CurriculumPlan
)

@course_planner_agent.tool
async def analyze_sop_documents(ctx: RunContext[CoursePlannerDeps], course_request_id: int) -> Dict[str, Any]:
    """Analyze SOP documents for course planning."""
    result = await ctx.deps.sop_analyzer.analyze_documents(course_request_id)
    logger.info(f"SOP analysis completed for request {course_request_id}")
    return result

@course_planner_agent.tool  
async def map_content_to_cefr(ctx: RunContext[CoursePlannerDeps], content: Dict[str, Any], target_level: str) -> Dict[str, Any]:
    """Map content complexity to CEFR levels."""
    result = await ctx.deps.cefr_mapper.map_content_level(content, target_level)
    logger.info(f"CEFR mapping completed for level {target_level}")
    return result

@course_planner_agent.tool
async def generate_curriculum_structure(ctx: RunContext[CoursePlannerDeps], analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate progressive curriculum structure."""
    result = await ctx.deps.curriculum_generator.create_structure(analysis_data)
    logger.info("Curriculum structure generated")
    return result

@course_planner_agent.tool
async def query_existing_templates(ctx: RunContext[CoursePlannerDeps], industry: str, level: str) -> List[Dict[str, Any]]:
    """Query existing curriculum templates for reference."""
    result = await ctx.deps.db_tool.get_curriculum_templates(industry, level)
    logger.info(f"Retrieved {len(result)} templates for {industry} industry, {level} level")
    return result

@course_planner_agent.tool
async def save_curriculum_plan(ctx: RunContext[CoursePlannerDeps], course_request_id: int, curriculum: Dict[str, Any]) -> Dict[str, Any]:
    """Save generated curriculum plan to database."""
    result = await ctx.deps.db_tool.save_curriculum(course_request_id, curriculum)
    logger.info(f"Curriculum saved for course request {course_request_id}")
    return result

class CoursePlannerService:
    """Main service class for the Course Planner Agent."""
    
    def __init__(self):
        self.agent = course_planner_agent
        self.deps = CoursePlannerDeps(
            sop_analyzer=SOPDocumentAnalyzer(),
            cefr_mapper=CEFRLevelMapper(),
            curriculum_generator=CurriculumStructureGenerator(),
            db_tool=DatabaseQueryTool()
        )
    
    async def plan_course(self, request: CourseRequest) -> CurriculumPlan:
        """Plan a complete course curriculum based on the request."""
        
        try:
            logger.info(f"Starting course planning for {request.company_name}")
            
            # Create the planning prompt
            planning_prompt = f"""
            Plan a comprehensive {request.duration_weeks}-week English language course for {request.company_name} in the {request.industry} industry.
            
            Course Requirements:
            - Target CEFR Level: {request.current_english_level}
            - Duration: {request.duration_weeks} weeks
            - Target Audience: {request.target_audience}
            - Training Goals: {request.training_goals}
            - Specific Needs: {request.specific_needs or 'General business English'}
            
            Please:
            1. Analyze available SOP documents to understand company-specific needs
            2. Map content to appropriate CEFR level
            3. Create a progressive curriculum structure
            4. Generate detailed module outlines
            5. Include industry-specific vocabulary and scenarios
            6. Plan appropriate assessments
            
            Course Request ID: {request.course_request_id}
            """
            
            # Run the agent
            result = await self.agent.run(planning_prompt, deps=self.deps)
            
            logger.info(f"Course planning completed for {request.company_name}")
            return result.data
            
        except Exception as e:
            logger.error(f"Course planning failed: {e}")
            raise
    
    async def get_planning_capabilities(self) -> Dict[str, Any]:
        """Get information about agent capabilities."""
        return {
            "agent_name": "Course Planning Specialist",
            "version": "1.0.0",
            "capabilities": [
                "SOP document analysis",
                "CEFR level mapping",
                "Curriculum structure generation",
                "Industry-specific content planning",
                "Progressive learning design"
            ],
            "supported_industries": [
                "Technology", "Healthcare", "Manufacturing", "Finance",
                "Hospitality", "Retail", "Logistics", "General Business"
            ],
            "supported_cefr_levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
            "max_duration_weeks": 24,
            "status": "active"
        }
    
    async def validate_course_request(self, request: CourseRequest) -> Dict[str, Any]:
        """Validate a course planning request."""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check CEFR level
        valid_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        if request.current_english_level not in valid_levels:
            validation_results["errors"].append(f"Invalid CEFR level: {request.current_english_level}")
            validation_results["valid"] = False
        
        # Check duration
        if request.duration_weeks < 1 or request.duration_weeks > 24:
            validation_results["errors"].append(f"Duration must be between 1-24 weeks, got: {request.duration_weeks}")
            validation_results["valid"] = False
        
        # Check for missing required fields
        if not request.company_name.strip():
            validation_results["errors"].append("Company name is required")
            validation_results["valid"] = False
        
        if not request.industry.strip():
            validation_results["warnings"].append("Industry not specified - will use generic business content")
        
        return validation_results

# Global service instance
course_planner_service = CoursePlannerService()

# Main execution for testing
async def main():
    """Test the course planner agent."""
    test_request = CourseRequest(
        course_request_id=1,
        company_name="TechCorp Solutions",
        industry="Technology",
        training_goals="Improve technical communication and client presentations",
        current_english_level="B1",
        duration_weeks=8,
        target_audience="Software developers and project managers"
    )
    
    try:
        curriculum = await course_planner_service.plan_course(test_request)
        print("Generated Curriculum:")
        print(json.dumps(curriculum.dict(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())