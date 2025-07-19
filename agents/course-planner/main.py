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
from pydantic import BaseModel, Field

from tools import (
    SOPDocumentAnalyzer,
    CEFRLevelMapper,
    CurriculumStructureGenerator,
    DatabaseQueryTool,
    RAGContextRetriever,
    PerformanceMetrics
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
    model_config = {"arbitrary_types_allowed": True}
    sop_analyzer: SOPDocumentAnalyzer
    cefr_mapper: CEFRLevelMapper
    curriculum_generator: CurriculumStructureGenerator
    db_tool: DatabaseQueryTool
    rag_retriever: RAGContextRetriever
    performance_metrics: PerformanceMetrics

# Enhanced Agent system prompt with RAG integration
SYSTEM_PROMPT = """
You are an advanced Course Planning Agent for corporate English language training, enhanced with Retrieval-Augmented Generation (RAG) capabilities. Your expertise combines deep analysis of company Standard Operating Procedures (SOPs) with contextual knowledge retrieval to create highly personalized, industry-specific curriculum structures.

Core Capabilities:
1. **Advanced SOP Analysis**: Leverage RAG to extract and contextualize key business processes, vocabulary, and communication patterns from company documents
2. **Intelligent CEFR Mapping**: Use contextual understanding to map content appropriateness across CEFR levels (A1-C2) with precision
3. **Adaptive Curriculum Design**: Create progressive, data-driven curriculum structures that evolve based on company-specific language needs
4. **Context-Aware Content Planning**: Generate detailed module and lesson outlines informed by actual workplace communication requirements
5. **Industry-Specific Customization**: Ensure deep relevance to specific industries and company contexts through contextual data analysis

Enhanced Approach:
- **RAG-Powered Analysis**: Use retrieved contextual information to understand nuanced company-specific language needs
- **Data-Driven Mapping**: Apply intelligent content mapping to CEFR levels based on analyzed workplace communication patterns
- **Contextual Progression**: Structure curriculum progressively using insights from actual workplace scenarios and communication requirements
- **Integrated Vocabulary Planning**: Incorporate industry-specific terminology and scenarios derived from real company documents
- **Authentic Assessment Design**: Create assessments that reflect genuine workplace communication challenges identified through document analysis

Quality Excellence Standards:
- All content must demonstrate clear alignment with CEFR descriptors and workplace communication needs
- Curriculum achievability verified against realistic workplace language requirements
- Learning objectives must be specific, measurable, and directly applicable to workplace scenarios
- Module progression follows logical scaffolding based on actual communication complexity patterns
- Comprehensive integration of all four language skills in authentic workplace contexts
- Performance metrics and continuous improvement tracking

Innovative Features:
- Real-time adaptation based on retrieved contextual information
- Predictive content recommendations using pattern analysis
- Quality assurance through multi-level validation
- Performance optimization through continuous learning
"""

# Create the agent
course_planner_agent = Agent(
    'openai:gpt-4o',
    system_prompt=SYSTEM_PROMPT,
    deps_type=CoursePlannerDeps,
    result_type=CurriculumPlan
)

@course_planner_agent.tool
async def analyze_sop_documents(ctx: RunContext[CoursePlannerDeps], course_request_id: int) -> Dict[str, Any]:
    """Enhanced SOP document analysis with RAG integration."""
    start_time = datetime.utcnow()
    
    try:
        # Perform comprehensive SOP analysis
        analysis_result = await ctx.deps.sop_analyzer.analyze_documents(course_request_id)
        
        # Enhance with RAG contextual retrieval
        if analysis_result.get('key_processes'):
            context_data = await ctx.deps.rag_retriever.get_contextual_insights(
                processes=analysis_result['key_processes'],
                vocabulary_themes=analysis_result.get('vocabulary_themes', []),
                course_request_id=course_request_id
            )
            analysis_result['contextual_insights'] = context_data
        
        # Record performance metrics
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        await ctx.deps.performance_metrics.record_analysis_metrics(
            course_request_id=course_request_id,
            processing_time=processing_time,
            documents_analyzed=analysis_result.get('documents_analyzed', 0),
            success=True
        )
        
        logger.info(f"Enhanced SOP analysis completed for request {course_request_id} in {processing_time:.2f}s")
        return analysis_result
        
    except Exception as e:
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        await ctx.deps.performance_metrics.record_analysis_metrics(
            course_request_id=course_request_id,
            processing_time=processing_time,
            success=False,
            error=str(e)
        )
        logger.error(f"Enhanced SOP analysis failed for request {course_request_id}: {e}")
        raise

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
    """Save generated curriculum plan with enhanced metadata and validation."""
    try:
        # Add enhanced metadata
        enhanced_curriculum = curriculum.copy()
        enhanced_curriculum.update({
            'generation_method': 'rag_enhanced_planning',
            'quality_score': await ctx.deps.performance_metrics.calculate_curriculum_quality_score(curriculum),
            'completeness_score': await ctx.deps.performance_metrics.calculate_completeness_score(curriculum),
            'contextual_relevance': await ctx.deps.rag_retriever.assess_curriculum_relevance(curriculum, course_request_id),
            'generated_at': datetime.utcnow().isoformat(),
            'agent_version': '2.0.0'
        })
        
        # Save with enhanced data
        result = await ctx.deps.db_tool.save_curriculum(course_request_id, enhanced_curriculum)
        
        # Record success metrics
        await ctx.deps.performance_metrics.record_curriculum_save(
            course_request_id=course_request_id,
            success=True,
            quality_score=enhanced_curriculum['quality_score']
        )
        
        logger.info(f"Enhanced curriculum saved for course request {course_request_id} with quality score {enhanced_curriculum['quality_score']}")
        return result
        
    except Exception as e:
        await ctx.deps.performance_metrics.record_curriculum_save(
            course_request_id=course_request_id,
            success=False,
            error=str(e)
        )
        logger.error(f"Enhanced curriculum save failed for request {course_request_id}: {e}")
        raise

class CoursePlannerService:
    """Main service class for the Course Planner Agent."""
    
    def __init__(self):
        self.agent = course_planner_agent
        self.deps = CoursePlannerDeps(
            sop_analyzer=SOPDocumentAnalyzer(),
            cefr_mapper=CEFRLevelMapper(),
            curriculum_generator=CurriculumStructureGenerator(),
            db_tool=DatabaseQueryTool(),
            rag_retriever=RAGContextRetriever(),
            performance_metrics=PerformanceMetrics()
        )
        
        # Initialize performance tracking
        self.performance_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'average_processing_time': 0.0,
            'quality_scores': [],
            'error_count': 0
        }
    
    async def plan_course(self, request: CourseRequest) -> CurriculumPlan:
        """Plan a complete course curriculum with enhanced RAG-powered analysis."""
        
        planning_start_time = datetime.utcnow()
        self.performance_stats['total_requests'] += 1
        
        try:
            logger.info(f"Starting enhanced course planning for {request.company_name}")
            
            # Pre-planning: Retrieve contextual information
            contextual_data = await self.deps.rag_retriever.get_company_context(
                company_name=request.company_name,
                industry=request.industry,
                course_request_id=request.course_request_id
            )
            
            # Create enhanced planning prompt with contextual information
            planning_prompt = f"""
            Plan a comprehensive {request.duration_weeks}-week English language course for {request.company_name} in the {request.industry} industry using advanced RAG-enhanced analysis.
            
            Course Requirements:
            - Target CEFR Level: {request.current_english_level}
            - Duration: {request.duration_weeks} weeks
            - Target Audience: {request.target_audience}
            - Training Goals: {request.training_goals}
            - Specific Needs: {request.specific_needs or 'General business English'}
            
            Contextual Information Retrieved:
            {json.dumps(contextual_data, indent=2)}
            
            Enhanced Planning Process:
            1. **Deep SOP Analysis**: Analyze available SOP documents with contextual understanding
            2. **Intelligent Content Mapping**: Map content to appropriate CEFR level using retrieved insights
            3. **Adaptive Curriculum Structure**: Create progressive structure informed by real workplace needs
            4. **Contextual Module Design**: Generate detailed module outlines based on actual communication patterns
            5. **Industry-Specific Integration**: Include vocabulary and scenarios derived from company documents
            6. **Authentic Assessment Planning**: Design assessments reflecting genuine workplace challenges
            7. **Quality Optimization**: Ensure curriculum meets enhanced quality standards
            
            Success Criteria:
            - Curriculum quality score ≥ 85%
            - Content completeness score ≥ 90%
            - Contextual relevance score ≥ 80%
            - CEFR alignment accuracy ≥ 95%
            
            Course Request ID: {request.course_request_id}
            """
            
            # Run the enhanced agent
            result = await self.agent.run(planning_prompt, deps=self.deps)
            
            # Post-processing: Validate and enhance results
            validated_result = await self._validate_and_enhance_curriculum(result.data, request)
            
            # Update performance metrics
            processing_time = (datetime.utcnow() - planning_start_time).total_seconds()
            self.performance_stats['successful_requests'] += 1
            self.performance_stats['average_processing_time'] = (
                (self.performance_stats['average_processing_time'] * (self.performance_stats['successful_requests'] - 1) + processing_time) / 
                self.performance_stats['successful_requests']
            )
            
            logger.info(f"Enhanced course planning completed for {request.company_name} in {processing_time:.2f}s")
            return validated_result
            
        except Exception as e:
            self.performance_stats['error_count'] += 1
            processing_time = (datetime.utcnow() - planning_start_time).total_seconds()
            
            # Log detailed error information
            logger.error(f"Enhanced course planning failed for {request.company_name}: {e}")
            
            # Record failure metrics
            await self.deps.performance_metrics.record_planning_failure(
                course_request_id=request.course_request_id,
                error=str(e),
                processing_time=processing_time
            )
            
            raise
    
    async def get_planning_capabilities(self) -> Dict[str, Any]:
        """Get information about enhanced agent capabilities."""
        return {
            "agent_name": "Enhanced Course Planning Specialist",
            "version": "2.0.0",
            "capabilities": [
                "RAG-enhanced SOP document analysis",
                "Intelligent CEFR level mapping",
                "Adaptive curriculum structure generation",
                "Context-aware industry-specific content planning",
                "Progressive learning design with workplace integration",
                "Real-time performance monitoring",
                "Quality assurance and validation",
                "Contextual content retrieval",
                "Predictive content recommendations"
            ],
            "enhanced_features": [
                "Retrieval-Augmented Generation (RAG) integration",
                "Advanced prompt engineering",
                "Multi-level quality validation",
                "Performance metrics tracking",
                "Contextual relevance assessment",
                "Adaptive curriculum optimization"
            ],
            "supported_industries": [
                "Technology", "Healthcare", "Manufacturing", "Finance",
                "Hospitality", "Retail", "Logistics", "General Business",
                "Education", "Legal", "Consulting", "Energy"
            ],
            "supported_cefr_levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
            "max_duration_weeks": 24,
            "quality_standards": {
                "curriculum_quality_threshold": 85,
                "completeness_threshold": 90,
                "contextual_relevance_threshold": 80,
                "cefr_alignment_threshold": 95
            },
            "performance_metrics": self.performance_stats,
            "status": "active_enhanced"
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
    
    async def _validate_and_enhance_curriculum(self, curriculum: CurriculumPlan, request: CourseRequest) -> CurriculumPlan:
        """Validate and enhance the generated curriculum with quality checks."""
        
        try:
            # Calculate quality metrics
            quality_score = await self.deps.performance_metrics.calculate_curriculum_quality_score(curriculum.dict())
            completeness_score = await self.deps.performance_metrics.calculate_completeness_score(curriculum.dict())
            
            # Assess contextual relevance
            contextual_relevance = await self.deps.rag_retriever.assess_curriculum_relevance(
                curriculum.dict(), request.course_request_id
            )
            
            # Add quality metadata to curriculum
            enhanced_dict = curriculum.dict()
            enhanced_dict.update({
                'quality_metrics': {
                    'quality_score': quality_score,
                    'completeness_score': completeness_score,
                    'contextual_relevance': contextual_relevance,
                    'validation_timestamp': datetime.utcnow().isoformat()
                },
                'enhancement_version': '2.0.0'
            })
            
            # Track quality scores for performance monitoring
            self.performance_stats['quality_scores'].append(quality_score)
            
            # Return enhanced curriculum
            return CurriculumPlan(**enhanced_dict)
            
        except Exception as e:
            logger.warning(f"Curriculum validation failed, returning original: {e}")
            return curriculum
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics for the course planner."""
        
        avg_quality = sum(self.performance_stats['quality_scores']) / len(self.performance_stats['quality_scores']) if self.performance_stats['quality_scores'] else 0
        
        return {
            'agent_performance': self.performance_stats,
            'quality_statistics': {
                'average_quality_score': avg_quality,
                'min_quality_score': min(self.performance_stats['quality_scores']) if self.performance_stats['quality_scores'] else 0,
                'max_quality_score': max(self.performance_stats['quality_scores']) if self.performance_stats['quality_scores'] else 0,
                'quality_trend': 'improving' if len(self.performance_stats['quality_scores']) >= 2 and self.performance_stats['quality_scores'][-1] > self.performance_stats['quality_scores'][-2] else 'stable'
            },
            'success_rate': (self.performance_stats['successful_requests'] / self.performance_stats['total_requests'] * 100) if self.performance_stats['total_requests'] > 0 else 0,
            'error_rate': (self.performance_stats['error_count'] / self.performance_stats['total_requests'] * 100) if self.performance_stats['total_requests'] > 0 else 0,
            'last_updated': datetime.utcnow().isoformat()
        }

# Global enhanced service instance
course_planner_service = CoursePlannerService()

# Enhanced tool implementations
@course_planner_agent.tool
async def get_contextual_insights(ctx: RunContext[CoursePlannerDeps], topic: str, course_request_id: int) -> Dict[str, Any]:
    """Retrieve contextual insights for specific topics using RAG."""
    result = await ctx.deps.rag_retriever.get_topic_insights(topic, course_request_id)
    logger.info(f"Retrieved contextual insights for topic: {topic}")
    return result

@course_planner_agent.tool
async def optimize_curriculum_structure(ctx: RunContext[CoursePlannerDeps], curriculum: Dict[str, Any], optimization_criteria: List[str]) -> Dict[str, Any]:
    """Optimize curriculum structure based on performance data and criteria."""
    result = await ctx.deps.performance_metrics.optimize_curriculum(
        curriculum, optimization_criteria
    )
    logger.info(f"Optimized curriculum structure based on criteria: {optimization_criteria}")
    return result

@course_planner_agent.tool
async def validate_curriculum_quality(ctx: RunContext[CoursePlannerDeps], curriculum: Dict[str, Any]) -> Dict[str, Any]:
    """Validate curriculum quality against enhanced standards."""
    quality_score = await ctx.deps.performance_metrics.calculate_curriculum_quality_score(curriculum)
    completeness_score = await ctx.deps.performance_metrics.calculate_completeness_score(curriculum)
    
    validation_result = {
        'quality_score': quality_score,
        'completeness_score': completeness_score,
        'meets_standards': quality_score >= 85 and completeness_score >= 90,
        'recommendations': await ctx.deps.performance_metrics.get_improvement_recommendations(curriculum),
        'validated_at': datetime.utcnow().isoformat()
    }
    
    logger.info(f"Curriculum validation completed with quality score: {quality_score}")
    return validation_result

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