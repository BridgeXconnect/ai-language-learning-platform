"""
Content Creator Agent
Creates engaging lessons, exercises, and learning materials based on curriculum structure
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from pydantic_ai import Agent, RunContext
from pydantic_ai.models import OpenAIModel
from pydantic import BaseModel, Field

from tools import (
    LessonContentGenerator,
    ExerciseCreator,
    AssessmentBuilder,
    MultimediaContentGenerator
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for structured input/output
class ContentCreationRequest(BaseModel):
    course_id: int
    module_id: Optional[int] = None
    lesson_title: str
    module_context: str
    vocabulary_themes: List[str]
    grammar_focus: List[str]
    cefr_level: str
    duration_minutes: int = 60
    content_type: str = "lesson"  # lesson, exercise, assessment
    company_context: Optional[Dict[str, Any]] = None

class LessonContent(BaseModel):
    lesson_id: str
    title: str
    duration_minutes: int
    learning_objectives: List[str]
    warm_up: Dict[str, Any]
    vocabulary_section: Dict[str, Any]
    grammar_section: Dict[str, Any]
    practice_activities: List[Dict[str, Any]]
    production_activity: Dict[str, Any]
    wrap_up: Dict[str, Any]
    materials_needed: List[str]
    homework_assignment: Optional[Dict[str, Any]] = None

class ExerciseContent(BaseModel):
    exercise_id: str
    title: str
    exercise_type: str
    instructions: str
    content: Dict[str, Any]
    correct_answers: Dict[str, Any]
    feedback: Dict[str, Any]
    points: int
    estimated_time_minutes: int

class ContentCreatorDeps(BaseModel):
    lesson_generator: LessonContentGenerator
    exercise_creator: ExerciseCreator
    assessment_builder: AssessmentBuilder
    multimedia_generator: MultimediaContentGenerator

# Agent system prompt
SYSTEM_PROMPT = """
You are an expert Content Creator Agent specializing in corporate English language training materials. Your role is to transform curriculum structures into engaging, practical, and effective learning content.

Key Responsibilities:
1. Generate detailed lesson content based on curriculum frameworks
2. Create varied and engaging exercise types (reading, writing, listening, speaking)
3. Incorporate company-specific scenarios and vocabulary naturally
4. Ensure all content aligns with specified CEFR standards
5. Design assessments that measure real workplace communication skills
6. Create multimedia content suggestions and interactive elements

Content Creation Principles:
- **Workplace Relevance**: All content should reflect real business scenarios
- **Progressive Difficulty**: Build complexity appropriately for the CEFR level
- **Engagement**: Use varied activities and interactive elements
- **Practical Application**: Focus on skills learners can immediately use
- **Cultural Sensitivity**: Consider diverse workplace environments
- **Accessibility**: Design for different learning styles and abilities

Quality Standards:
- Content must be linguistically accurate and appropriate for the CEFR level
- Activities should be clearly structured with specific time allocations
- Include comprehensive instructor guidance and learner feedback
- Provide multiple assessment methods (formative and summative)
- Ensure content scalability and reusability across similar contexts
"""

# Initialize the AI model
model = OpenAIModel('gpt-4o', api_key=os.getenv('OPENAI_API_KEY'))

# Create the agent
content_creator_agent = Agent(
    model,
    system_prompt=SYSTEM_PROMPT,
    deps_type=ContentCreatorDeps,
    result_type=LessonContent
)

@content_creator_agent.tool
async def generate_lesson_content(ctx: RunContext[ContentCreatorDeps], request: ContentCreationRequest) -> Dict[str, Any]:
    """Generate comprehensive lesson content."""
    result = await ctx.deps.lesson_generator.create_lesson(request)
    logger.info(f"Lesson content generated for: {request.lesson_title}")
    return result

@content_creator_agent.tool
async def create_exercises(ctx: RunContext[ContentCreatorDeps], lesson_context: Dict[str, Any], exercise_count: int = 5) -> List[Dict[str, Any]]:
    """Create varied exercises for a lesson."""
    result = await ctx.deps.exercise_creator.generate_exercises(lesson_context, exercise_count)
    logger.info(f"Generated {len(result)} exercises")
    return result

@content_creator_agent.tool
async def build_assessment(ctx: RunContext[ContentCreatorDeps], content_context: Dict[str, Any]) -> Dict[str, Any]:
    """Build comprehensive assessments."""
    result = await ctx.deps.assessment_builder.create_assessment(content_context)
    logger.info("Assessment built successfully")
    return result

@content_creator_agent.tool
async def generate_multimedia_content(ctx: RunContext[ContentCreatorDeps], content_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate multimedia content suggestions."""
    result = await ctx.deps.multimedia_generator.suggest_multimedia(content_type, context)
    logger.info(f"Multimedia content generated for {content_type}")
    return result

@content_creator_agent.tool
async def adapt_content_for_level(ctx: RunContext[ContentCreatorDeps], content: Dict[str, Any], target_level: str) -> Dict[str, Any]:
    """Adapt existing content for different CEFR levels."""
    result = await ctx.deps.lesson_generator.adapt_for_cefr_level(content, target_level)
    logger.info(f"Content adapted for {target_level} level")
    return result

class ContentCreatorService:
    """Main service class for the Content Creator Agent."""
    
    def __init__(self):
        self.agent = content_creator_agent
        self.deps = ContentCreatorDeps(
            lesson_generator=LessonContentGenerator(),
            exercise_creator=ExerciseCreator(),
            assessment_builder=AssessmentBuilder(),
            multimedia_generator=MultimediaContentGenerator()
        )
    
    async def create_lesson_content(self, request: ContentCreationRequest) -> LessonContent:
        """Create comprehensive lesson content."""
        
        try:
            logger.info(f"Creating lesson content: {request.lesson_title}")
            
            # Create the content generation prompt
            content_prompt = f"""
            Create comprehensive lesson content for: "{request.lesson_title}"
            
            Context:
            - Module Context: {request.module_context}
            - Vocabulary Themes: {', '.join(request.vocabulary_themes)}
            - Grammar Focus: {', '.join(request.grammar_focus)}
            - CEFR Level: {request.cefr_level}
            - Duration: {request.duration_minutes} minutes
            - Company Context: {request.company_context or 'General business environment'}
            
            Generate a complete lesson with:
            1. Clear learning objectives aligned with CEFR {request.cefr_level}
            2. Engaging warm-up activity (5-10 minutes)
            3. Structured vocabulary introduction with company-specific terms
            4. Grammar presentation with practical examples
            5. Varied practice activities (individual, pair, group work)
            6. Meaningful production/speaking activity
            7. Effective wrap-up and assessment
            8. Appropriate homework assignment
            
            Ensure all activities are:
            - Relevant to workplace scenarios
            - Appropriate for {request.cefr_level} level
            - Engaging and interactive
            - Clearly timed and structured
            """
            
            # Run the agent
            result = await self.agent.run(content_prompt, deps=self.deps)
            
            logger.info(f"Lesson content created: {request.lesson_title}")
            return result.data
            
        except Exception as e:
            logger.error(f"Lesson content creation failed: {e}")
            raise
    
    async def create_exercise_set(self, lesson_context: Dict[str, Any], exercise_types: List[str], count: int = 5) -> List[ExerciseContent]:
        """Create a set of varied exercises."""
        
        try:
            logger.info(f"Creating {count} exercises of types: {exercise_types}")
            
            exercises = []
            for i, exercise_type in enumerate(exercise_types[:count]):
                exercise_prompt = f"""
                Create a {exercise_type} exercise based on this lesson context:
                {json.dumps(lesson_context, indent=2)}
                
                Exercise requirements:
                - Type: {exercise_type}
                - Appropriate for the lesson's CEFR level
                - Uses vocabulary and grammar from the lesson
                - Includes clear instructions
                - Provides immediate feedback
                - Takes 5-10 minutes to complete
                
                Exercise {i+1} of {count}
                """
                
                # For exercises, we'll use a simpler direct approach
                exercise_data = await self.deps.exercise_creator.generate_single_exercise(
                    exercise_type, lesson_context
                )
                
                exercises.append(ExerciseContent(**exercise_data))
            
            logger.info(f"Created {len(exercises)} exercises")
            return exercises
            
        except Exception as e:
            logger.error(f"Exercise creation failed: {e}")
            raise
    
    async def create_assessment(self, course_context: Dict[str, Any], assessment_type: str = "lesson") -> Dict[str, Any]:
        """Create comprehensive assessment content."""
        
        try:
            logger.info(f"Creating {assessment_type} assessment")
            
            assessment_prompt = f"""
            Create a comprehensive {assessment_type} assessment based on:
            {json.dumps(course_context, indent=2)}
            
            Assessment requirements:
            - Mixed question types (multiple choice, fill-in-blank, short answer, speaking tasks)
            - Clear scoring rubric
            - Time allocation for each section
            - Appropriate difficulty for the CEFR level
            - Practical workplace scenarios
            - Immediate feedback mechanisms
            
            Include formative and summative assessment elements.
            """
            
            assessment_data = await self.deps.assessment_builder.create_assessment(course_context)
            
            logger.info(f"{assessment_type.title()} assessment created")
            return assessment_data
            
        except Exception as e:
            logger.error(f"Assessment creation failed: {e}")
            raise
    
    async def get_content_capabilities(self) -> Dict[str, Any]:
        """Get information about content creator capabilities."""
        return {
            "agent_name": "Content Creator Agent",
            "version": "1.0.0",
            "capabilities": [
                "Lesson content generation",
                "Exercise creation (multiple types)",
                "Assessment building",
                "Multimedia content planning",
                "CEFR-level adaptation",
                "Company-specific content integration"
            ],
            "supported_exercise_types": [
                "multiple-choice", "fill-in-blank", "matching", "drag-drop",
                "reading-comprehension", "listening-exercise", "speaking-prompt",
                "writing-task", "role-play", "case-study"
            ],
            "supported_cefr_levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
            "content_formats": [
                "structured-lessons", "interactive-exercises", "assessments",
                "multimedia-suggestions", "homework-assignments"
            ],
            "status": "active"
        }
    
    async def validate_content_request(self, request: ContentCreationRequest) -> Dict[str, Any]:
        """Validate a content creation request."""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check CEFR level
        valid_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        if request.cefr_level not in valid_levels:
            validation_results["errors"].append(f"Invalid CEFR level: {request.cefr_level}")
            validation_results["valid"] = False
        
        # Check duration
        if request.duration_minutes < 5 or request.duration_minutes > 240:
            validation_results["errors"].append(f"Duration must be 5-240 minutes, got: {request.duration_minutes}")
            validation_results["valid"] = False
        
        # Check required fields
        if not request.lesson_title.strip():
            validation_results["errors"].append("Lesson title is required")
            validation_results["valid"] = False
        
        if not request.vocabulary_themes:
            validation_results["warnings"].append("No vocabulary themes specified")
        
        if not request.grammar_focus:
            validation_results["warnings"].append("No grammar focus specified")
        
        return validation_results

# Global service instance
content_creator_service = ContentCreatorService()

# Main execution for testing
async def main():
    """Test the content creator agent."""
    test_request = ContentCreationRequest(
        course_id=1,
        lesson_title="Business Email Communication",
        module_context="Professional email writing and etiquette",
        vocabulary_themes=["email vocabulary", "formal language", "business terminology"],
        grammar_focus=["conditional sentences", "polite requests", "future tense"],
        cefr_level="B1",
        duration_minutes=60,
        company_context={
            "industry": "Technology",
            "company_name": "TechCorp Solutions",
            "communication_style": "professional but friendly"
        }
    )
    
    try:
        lesson_content = await content_creator_service.create_lesson_content(test_request)
        print("Generated Lesson Content:")
        print(json.dumps(lesson_content.dict(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())