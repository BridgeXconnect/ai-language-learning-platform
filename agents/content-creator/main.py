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
from pydantic import BaseModel, Field

from tools import (
    LessonContentGenerator,
    ExerciseCreator,
    AssessmentBuilder,
    MultimediaContentGenerator,
    RAGContentEnhancer,
    ContentQualityTracker,
    MultiModalContentPlanner
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
    model_config = {"arbitrary_types_allowed": True}
    lesson_generator: LessonContentGenerator
    exercise_creator: ExerciseCreator
    assessment_builder: AssessmentBuilder
    multimedia_generator: MultimediaContentGenerator
    rag_enhancer: RAGContentEnhancer
    quality_tracker: ContentQualityTracker
    multimodal_planner: MultiModalContentPlanner

# Enhanced Agent system prompt with RAG integration and multi-modal capabilities
SYSTEM_PROMPT = """
You are an advanced Content Creator Agent specializing in corporate English language training materials, enhanced with Retrieval-Augmented Generation (RAG) and multi-modal content capabilities. Your role is to transform curriculum structures into highly engaging, contextually-relevant, and effective learning experiences.

Core Responsibilities:
1. **RAG-Enhanced Content Generation**: Create detailed lesson content using retrieved contextual information from company documents and industry best practices
2. **Multi-Modal Exercise Creation**: Develop varied and engaging exercises across all modalities (reading, writing, listening, speaking, visual, interactive)
3. **Context-Aware Scenario Integration**: Incorporate company-specific scenarios and vocabulary based on actual workplace communication patterns
4. **Precision CEFR Alignment**: Ensure all content precisely aligns with specified CEFR standards using enhanced validation
5. **Authentic Assessment Design**: Create assessments that measure real workplace communication skills using retrieved contextual examples
6. **Advanced Multimedia Planning**: Generate comprehensive multimedia content strategies with accessibility considerations
7. **Quality Optimization**: Continuously improve content quality through performance tracking and feedback integration

Advanced Content Creation Principles:
- **Contextual Authenticity**: All content reflects genuine workplace scenarios derived from analyzed company documents
- **Adaptive Complexity**: Build complexity dynamically based on learner progress and CEFR requirements
- **Multi-Sensory Engagement**: Utilize varied activities, interactive elements, and multimedia integration
- **Immediate Applicability**: Focus on skills learners can apply immediately in their work environment
- **Cultural Intelligence**: Consider diverse workplace environments and cultural communication patterns
- **Universal Design**: Create accessible content for different learning styles, abilities, and technical environments
- **Data-Driven Optimization**: Use performance metrics to continuously refine content effectiveness

Enhanced Quality Standards:
- Content demonstrates linguistic accuracy verified through multiple validation layers
- Activities feature clear structure, precise timing, and measurable outcomes
- Comprehensive instructor guidance includes differentiation strategies and troubleshooting
- Multi-level assessment methods provide immediate and longitudinal feedback
- Content scalability and reusability validated across diverse organizational contexts
- Real-time quality tracking ensures continuous improvement
- Accessibility compliance meets international standards

Innovative Features:
- Context-aware content adaptation using RAG insights
- Predictive exercise difficulty calibration
- Multi-modal learning path optimization
- Real-time relevance assessment
- Automated quality assurance and improvement suggestions
"""

# Create the agent
content_creator_agent = Agent(
    'openai:gpt-4o',
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
            multimedia_generator=MultimediaContentGenerator(),
            rag_enhancer=RAGContentEnhancer(),
            quality_tracker=ContentQualityTracker(),
            multimodal_planner=MultiModalContentPlanner()
        )
        
        # Enhanced performance tracking
        self.performance_metrics = {
            'content_created': 0,
            'quality_scores': [],
            'generation_times': [],
            'rag_enhancement_success_rate': 0.0,
            'user_engagement_scores': [],
            'accessibility_compliance_rate': 0.0
        }
    
    async def create_lesson_content(self, request: ContentCreationRequest) -> LessonContent:
        """Create comprehensive lesson content with RAG enhancement and multi-modal planning."""
        
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Creating enhanced lesson content: {request.lesson_title}")
            
            # Pre-generation: Retrieve contextual content using RAG
            contextual_data = await self.deps.rag_enhancer.get_lesson_context(
                lesson_title=request.lesson_title,
                vocabulary_themes=request.vocabulary_themes,
                company_context=request.company_context,
                course_id=request.course_id
            )
            
            # Plan multi-modal content integration
            multimodal_plan = await self.deps.multimodal_planner.create_lesson_plan(
                request=request,
                contextual_data=contextual_data
            )
            
            # Create enhanced content generation prompt
            content_prompt = f"""
            Create comprehensive, RAG-enhanced lesson content for: "{request.lesson_title}"
            
            Core Context:
            - Module Context: {request.module_context}
            - Vocabulary Themes: {', '.join(request.vocabulary_themes)}
            - Grammar Focus: {', '.join(request.grammar_focus)}
            - CEFR Level: {request.cefr_level}
            - Duration: {request.duration_minutes} minutes
            - Company Context: {request.company_context or 'General business environment'}
            
            Retrieved Contextual Information:
            {json.dumps(contextual_data, indent=2)}
            
            Multi-Modal Content Plan:
            {json.dumps(multimodal_plan, indent=2)}
            
            Generate an enhanced lesson with:
            1. **Context-Informed Learning Objectives**: Align with CEFR {request.cefr_level} and real workplace needs
            2. **Engaging Multi-Modal Warm-up**: 5-10 minutes with visual/interactive elements
            3. **RAG-Enhanced Vocabulary Introduction**: Company-specific terms with authentic context
            4. **Practical Grammar Presentation**: Real workplace examples from retrieved content
            5. **Diverse Practice Activities**: Individual, pair, group work with multi-modal elements
            6. **Authentic Production Activity**: Speaking/writing tasks based on real scenarios
            7. **Comprehensive Assessment**: Multiple methods with immediate feedback
            8. **Contextual Homework Assignment**: Workplace application tasks
            9. **Accessibility Features**: Support for different learning styles and abilities
            10. **Quality Assurance Checkpoints**: Built-in validation and improvement points
            
            Enhanced Requirements:
            - All activities must demonstrate authentic workplace relevance
            - Content appropriate for {request.cefr_level} with verification points
            - Multi-modal engagement throughout the lesson
            - Clear accessibility and differentiation support
            - Real-time quality tracking integration
            - Scalable and adaptable design
            
            Quality Targets:
            - Content Relevance Score: ≥ 85%
            - CEFR Alignment Score: ≥ 95%
            - Engagement Factor: ≥ 4.0/5.0
            - Accessibility Compliance: 100%
            """
            
            # Run the enhanced agent
            result = await self.agent.run(content_prompt, deps=self.deps)
            
            # Post-generation enhancement and validation
            enhanced_content = await self._enhance_and_validate_content(
                content=result.data,
                request=request,
                contextual_data=contextual_data,
                multimodal_plan=multimodal_plan
            )
            
            # Track performance metrics
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            self.performance_metrics['content_created'] += 1
            self.performance_metrics['generation_times'].append(generation_time)
            
            # Calculate and track quality score
            quality_score = await self.deps.quality_tracker.calculate_content_quality(
                enhanced_content.dict(), request
            )
            self.performance_metrics['quality_scores'].append(quality_score)
            
            logger.info(f"Enhanced lesson content created: {request.lesson_title} (Quality: {quality_score}, Time: {generation_time:.2f}s)")
            return enhanced_content
            
        except Exception as e:
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Enhanced lesson content creation failed: {e}")
            
            # Track failure metrics
            await self.deps.quality_tracker.record_generation_failure(
                request=request,
                error=str(e),
                generation_time=generation_time
            )
            
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
        """Get information about enhanced content creator capabilities."""
        
        avg_quality = sum(self.performance_metrics['quality_scores']) / len(self.performance_metrics['quality_scores']) if self.performance_metrics['quality_scores'] else 0
        avg_generation_time = sum(self.performance_metrics['generation_times']) / len(self.performance_metrics['generation_times']) if self.performance_metrics['generation_times'] else 0
        
        return {
            "agent_name": "Enhanced Content Creator Agent",
            "version": "2.0.0",
            "capabilities": [
                "RAG-enhanced lesson content generation",
                "Multi-modal exercise creation (10+ types)",
                "Adaptive assessment building",
                "Advanced multimedia content planning",
                "Dynamic CEFR-level adaptation",
                "Context-aware company-specific integration",
                "Real-time quality tracking and optimization",
                "Accessibility compliance assurance",
                "Performance analytics and insights"
            ],
            "enhanced_features": [
                "Retrieval-Augmented Generation (RAG) integration",
                "Multi-modal content planning and optimization",
                "Advanced quality tracking and metrics",
                "Contextual content enhancement",
                "Real-time accessibility validation",
                "Predictive difficulty calibration",
                "Automated content improvement suggestions"
            ],
            "supported_exercise_types": [
                "multiple-choice", "fill-in-blank", "matching", "drag-drop",
                "reading-comprehension", "listening-exercise", "speaking-prompt",
                "writing-task", "role-play", "case-study", "simulation",
                "gamified-learning", "video-interaction", "ar-vr-scenarios"
            ],
            "supported_cefr_levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
            "content_formats": [
                "structured-lessons", "interactive-exercises", "adaptive-assessments",
                "multimedia-experiences", "contextual-homework", "micro-learning",
                "mobile-friendly", "accessibility-compliant", "multi-device"
            ],
            "quality_standards": {
                "content_relevance_threshold": 85,
                "cefr_alignment_threshold": 95,
                "engagement_threshold": 4.0,
                "accessibility_compliance": 100
            },
            "performance_metrics": {
                "content_created": self.performance_metrics['content_created'],
                "average_quality_score": avg_quality,
                "average_generation_time": avg_generation_time,
                "rag_enhancement_success_rate": self.performance_metrics['rag_enhancement_success_rate']
            },
            "status": "active_enhanced"
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
    
    async def _enhance_and_validate_content(self, content: LessonContent, request: ContentCreationRequest, 
                                          contextual_data: Dict[str, Any], multimodal_plan: Dict[str, Any]) -> LessonContent:
        """Enhance and validate generated content with additional features."""
        
        try:
            # Enhance content with RAG insights
            enhanced_content = await self.deps.rag_enhancer.enhance_lesson_content(
                content=content.dict(),
                contextual_data=contextual_data
            )
            
            # Integrate multi-modal elements
            multimodal_enhanced = await self.deps.multimodal_planner.integrate_multimodal_elements(
                content=enhanced_content,
                plan=multimodal_plan
            )
            
            # Validate quality and accessibility
            validation_result = await self.deps.quality_tracker.validate_content_quality(
                content=multimodal_enhanced,
                request=request
            )
            
            # Apply improvements if needed
            if validation_result.get('needs_improvement', False):
                improved_content = await self.deps.quality_tracker.apply_improvements(
                    content=multimodal_enhanced,
                    improvements=validation_result.get('suggestions', [])
                )
                multimodal_enhanced = improved_content
            
            # Add enhancement metadata
            multimodal_enhanced.update({
                'enhancement_metadata': {
                    'rag_enhanced': True,
                    'multimodal_integrated': True,
                    'quality_validated': True,
                    'accessibility_compliant': validation_result.get('accessibility_score', 0) >= 100,
                    'enhancement_timestamp': datetime.utcnow().isoformat(),
                    'quality_score': validation_result.get('quality_score', 0),
                    'contextual_relevance': validation_result.get('contextual_relevance', 0)
                }
            })
            
            return LessonContent(**multimodal_enhanced)
            
        except Exception as e:
            logger.warning(f"Content enhancement failed, returning original: {e}")
            return content
    
    async def create_adaptive_exercise_set(self, lesson_context: Dict[str, Any], 
                                         learner_profile: Dict[str, Any] = None,
                                         difficulty_target: float = None) -> List[ExerciseContent]:
        """Create adaptive exercise set based on learner profile and difficulty targets."""
        
        try:
            # Enhance lesson context with RAG data
            enhanced_context = await self.deps.rag_enhancer.enhance_exercise_context(
                lesson_context=lesson_context,
                learner_profile=learner_profile
            )
            
            # Generate adaptive exercises
            adaptive_exercises = await self.deps.exercise_creator.generate_adaptive_exercises(
                enhanced_context=enhanced_context,
                difficulty_target=difficulty_target,
                count=6  # Generate more exercises for better selection
            )
            
            # Apply quality tracking
            validated_exercises = []
            for exercise in adaptive_exercises:
                quality_score = await self.deps.quality_tracker.validate_exercise_quality(exercise)
                if quality_score >= 80:  # Quality threshold
                    validated_exercises.append(exercise)
            
            logger.info(f"Created {len(validated_exercises)} adaptive exercises")
            return validated_exercises[:5]  # Return top 5
            
        except Exception as e:
            logger.error(f"Adaptive exercise creation failed: {e}")
            # Fallback to standard exercise creation
            return await self.create_exercise_set(lesson_context, ["multiple-choice", "fill-in-blank", "role-play"])
    
    async def get_content_analytics(self) -> Dict[str, Any]:
        """Get comprehensive content creation analytics."""
        
        try:
            analytics = await self.deps.quality_tracker.get_analytics_summary()
            
            # Combine with internal metrics
            analytics.update({
                'internal_metrics': self.performance_metrics,
                'content_trends': await self.deps.quality_tracker.analyze_content_trends(),
                'improvement_recommendations': await self.deps.quality_tracker.get_improvement_recommendations(),
                'rag_enhancement_impact': await self.deps.rag_enhancer.get_enhancement_impact(),
                'multimodal_usage_stats': await self.deps.multimodal_planner.get_usage_statistics()
            })
            
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics generation failed: {e}")
            return {
                'error': 'Analytics unavailable',
                'basic_metrics': self.performance_metrics
            }

# Global enhanced service instance
content_creator_service = ContentCreatorService()

# Enhanced tool functions
@content_creator_agent.tool
async def enhance_with_rag_context(ctx: RunContext[ContentCreatorDeps], content_type: str, topic: str, company_context: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance content creation with RAG-retrieved contextual information."""
    result = await ctx.deps.rag_enhancer.get_contextual_enhancement(
        content_type=content_type,
        topic=topic,
        company_context=company_context
    )
    logger.info(f"RAG enhancement retrieved for {content_type}: {topic}")
    return result

@content_creator_agent.tool
async def create_multimodal_content_plan(ctx: RunContext[ContentCreatorDeps], lesson_request: Dict[str, Any]) -> Dict[str, Any]:
    """Create comprehensive multi-modal content plan."""
    result = await ctx.deps.multimodal_planner.create_comprehensive_plan(lesson_request)
    logger.info(f"Multi-modal content plan created for: {lesson_request.get('lesson_title', 'unknown')}")
    return result

@content_creator_agent.tool
async def validate_content_accessibility(ctx: RunContext[ContentCreatorDeps], content: Dict[str, Any]) -> Dict[str, Any]:
    """Validate content for accessibility compliance."""
    result = await ctx.deps.quality_tracker.validate_accessibility_compliance(content)
    logger.info(f"Accessibility validation completed with score: {result.get('accessibility_score', 'unknown')}")
    return result

@content_creator_agent.tool
async def optimize_content_difficulty(ctx: RunContext[ContentCreatorDeps], content: Dict[str, Any], target_cefr: str, learner_data: Dict[str, Any]) -> Dict[str, Any]:
    """Optimize content difficulty based on CEFR level and learner data."""
    result = await ctx.deps.quality_tracker.optimize_difficulty_level(
        content=content,
        target_cefr=target_cefr,
        learner_data=learner_data
    )
    logger.info(f"Content difficulty optimized for CEFR {target_cefr}")
    return result

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