"""
Quality Assurance Agent
Reviews and improves generated course content for quality and effectiveness
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio

from pydantic_ai import Agent, RunContext
from pydantic_ai.models import OpenAIModel
from pydantic import BaseModel, Field

from tools import (
    ContentQualityAnalyzer,
    CEFRLevelValidator,
    GrammarChecker,
    CulturalSensitivityChecker
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for structured input/output
class QualityReviewRequest(BaseModel):
    content_id: str
    content_type: str  # lesson, exercise, assessment, module
    content_data: Dict[str, Any]
    target_cefr_level: str
    review_criteria: List[str] = ["grammar", "cefr_alignment", "cultural_sensitivity", "engagement"]
    company_context: Optional[Dict[str, Any]] = None

class QualityReport(BaseModel):
    content_id: str
    overall_score: float  # 0-100
    review_date: str
    review_criteria_scores: Dict[str, float]
    issues_found: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    approved_for_release: bool
    reviewer_notes: Optional[str] = None

class ContentImprovement(BaseModel):
    original_content: Dict[str, Any]
    improved_content: Dict[str, Any]
    changes_made: List[Dict[str, Any]]
    improvement_score: float
    justification: str

class QualityAssuranceDeps(BaseModel):
    quality_analyzer: ContentQualityAnalyzer
    cefr_validator: CEFRLevelValidator
    grammar_checker: GrammarChecker
    cultural_checker: CulturalSensitivityChecker

# Agent system prompt
SYSTEM_PROMPT = """
You are an expert Quality Assurance Agent specializing in English language learning content review and improvement. Your mission is to ensure that all generated content meets the highest standards of pedagogical quality, linguistic accuracy, and cultural appropriateness.

Core Responsibilities:
1. Review content for CEFR level appropriateness and accuracy
2. Check grammatical accuracy and linguistic clarity
3. Validate exercise effectiveness and pedagogical soundness
4. Ensure cultural sensitivity and inclusivity in all materials
5. Provide specific, actionable improvement recommendations
6. Maintain consistency across all content within a course

Quality Assessment Framework:
- **Linguistic Accuracy** (25%): Grammar, vocabulary usage, language level appropriateness
- **Pedagogical Effectiveness** (25%): Learning objective alignment, activity design, progressive difficulty
- **Cultural Sensitivity** (20%): Inclusive language, diverse perspectives, cultural appropriateness
- **Engagement & Relevance** (20%): Workplace applicability, learner motivation, practical value
- **Technical Quality** (10%): Formatting, instructions clarity, assessment validity

Review Standards:
- Content must score ≥80% overall to be approved for release
- All critical issues must be resolved before approval
- Recommendations should be specific, actionable, and prioritized
- Cultural sensitivity issues require immediate attention
- CEFR misalignment must be corrected to ensure learner success

Improvement Philosophy:
- Preserve the original pedagogical intent while enhancing quality
- Suggest evidence-based improvements rooted in SLA research
- Balance thoroughness with practical implementation constraints
- Prioritize learner experience and outcome effectiveness
"""

# Initialize the AI model
model = OpenAIModel('gpt-4o', api_key=os.getenv('OPENAI_API_KEY'))

# Create the agent
quality_assurance_agent = Agent(
    model,
    system_prompt=SYSTEM_PROMPT,
    deps_type=QualityAssuranceDeps,
    result_type=QualityReport
)

@quality_assurance_agent.tool
async def analyze_content_quality(ctx: RunContext[QualityAssuranceDeps], content: Dict[str, Any], criteria: List[str]) -> Dict[str, Any]:
    """Analyze overall content quality across multiple criteria."""
    result = await ctx.deps.quality_analyzer.analyze_comprehensive_quality(content, criteria)
    logger.info(f"Quality analysis completed with score: {result.get('overall_score', 'N/A')}")
    return result

@quality_assurance_agent.tool
async def validate_cefr_alignment(ctx: RunContext[QualityAssuranceDeps], content: Dict[str, Any], target_level: str) -> Dict[str, Any]:
    """Validate content alignment with specified CEFR level."""
    result = await ctx.deps.cefr_validator.validate_level_alignment(content, target_level)
    logger.info(f"CEFR validation completed for level {target_level}")
    return result

@quality_assurance_agent.tool
async def check_grammar_accuracy(ctx: RunContext[QualityAssuranceDeps], content: Dict[str, Any]) -> Dict[str, Any]:
    """Check grammatical accuracy and language quality."""
    result = await ctx.deps.grammar_checker.comprehensive_grammar_check(content)
    logger.info(f"Grammar check found {len(result.get('issues', []))} issues")
    return result

@quality_assurance_agent.tool
async def assess_cultural_sensitivity(ctx: RunContext[QualityAssuranceDeps], content: Dict[str, Any]) -> Dict[str, Any]:
    """Assess cultural sensitivity and inclusivity."""
    result = await ctx.deps.cultural_checker.analyze_cultural_appropriateness(content)
    logger.info(f"Cultural sensitivity check completed")
    return result

@quality_assurance_agent.tool
async def improve_content_quality(ctx: RunContext[QualityAssuranceDeps], content: Dict[str, Any], issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate improved content based on identified issues."""
    result = await ctx.deps.quality_analyzer.generate_improvements(content, issues)
    logger.info("Content improvements generated")
    return result

class QualityAssuranceService:
    """Main service class for the Quality Assurance Agent."""
    
    def __init__(self):
        self.agent = quality_assurance_agent
        self.deps = QualityAssuranceDeps(
            quality_analyzer=ContentQualityAnalyzer(),
            cefr_validator=CEFRLevelValidator(),
            grammar_checker=GrammarChecker(),
            cultural_checker=CulturalSensitivityChecker()
        )
    
    async def review_content(self, request: QualityReviewRequest) -> QualityReport:
        """Conduct comprehensive content review."""
        
        try:
            logger.info(f"Starting quality review for {request.content_type}: {request.content_id}")
            
            # Create the review prompt
            review_prompt = f"""
            Conduct a comprehensive quality review of this {request.content_type} content:
            
            Content ID: {request.content_id}
            Target CEFR Level: {request.target_cefr_level}
            Review Criteria: {', '.join(request.review_criteria)}
            
            Content to Review:
            {json.dumps(request.content_data, indent=2)}
            
            Company Context: {request.company_context or 'General business environment'}
            
            Please analyze this content across all specified criteria:
            
            1. **Linguistic Accuracy**: Check grammar, vocabulary appropriateness, language level
            2. **CEFR Alignment**: Verify content matches target level requirements
            3. **Pedagogical Effectiveness**: Assess learning design and activity quality
            4. **Cultural Sensitivity**: Ensure inclusive and appropriate content
            5. **Engagement & Relevance**: Evaluate workplace applicability and motivation
            
            For each issue found:
            - Specify the exact location/section
            - Describe the problem clearly
            - Assess severity (critical/major/minor)
            - Provide specific improvement recommendation
            
            Generate an overall quality score (0-100) and approval recommendation.
            """
            
            # Run the agent
            result = await self.agent.run(review_prompt, deps=self.deps)
            
            logger.info(f"Quality review completed for {request.content_id}")
            return result.data
            
        except Exception as e:
            logger.error(f"Quality review failed: {e}")
            raise
    
    async def improve_content(self, content: Dict[str, Any], quality_issues: List[Dict[str, Any]]) -> ContentImprovement:
        """Generate improved content based on quality issues."""
        
        try:
            logger.info("Generating content improvements")
            
            improvement_prompt = f"""
            Improve this content based on the identified quality issues:
            
            Original Content:
            {json.dumps(content, indent=2)}
            
            Quality Issues to Address:
            {json.dumps(quality_issues, indent=2)}
            
            Generate improved content that:
            1. Addresses all identified issues
            2. Maintains the original pedagogical intent
            3. Enhances overall quality and effectiveness
            4. Preserves content structure and organization
            5. Improves learner experience
            
            For each change made:
            - Specify what was changed
            - Explain why the change was made
            - Reference the original issue it addresses
            
            Provide a justification for the improvements and an estimated quality improvement score.
            """
            
            # For improvements, we'll use the quality analyzer
            improvement_result = await self.deps.quality_analyzer.generate_improvements(
                content, quality_issues
            )
            
            # Structure the result
            content_improvement = ContentImprovement(
                original_content=content,
                improved_content=improvement_result["improved_content"],
                changes_made=improvement_result["changes_made"],
                improvement_score=improvement_result["improvement_score"],
                justification=improvement_result["justification"]
            )
            
            logger.info("Content improvements generated successfully")
            return content_improvement
            
        except Exception as e:
            logger.error(f"Content improvement failed: {e}")
            raise
    
    async def batch_review(self, content_items: List[Dict[str, Any]], criteria: List[str]) -> List[QualityReport]:
        """Review multiple content items in batch."""
        
        try:
            logger.info(f"Starting batch review of {len(content_items)} items")
            
            review_results = []
            for item in content_items:
                request = QualityReviewRequest(
                    content_id=item.get("id", f"item_{len(review_results)}"),
                    content_type=item.get("type", "unknown"),
                    content_data=item.get("data", {}),
                    target_cefr_level=item.get("cefr_level", "B1"),
                    review_criteria=criteria
                )
                
                review_result = await self.review_content(request)
                review_results.append(review_result)
            
            logger.info(f"Batch review completed: {len(review_results)} items processed")
            return review_results
            
        except Exception as e:
            logger.error(f"Batch review failed: {e}")
            raise
    
    async def get_qa_capabilities(self) -> Dict[str, Any]:
        """Get information about QA agent capabilities."""
        return {
            "agent_name": "Quality Assurance Agent",
            "version": "1.0.0",
            "capabilities": [
                "Comprehensive content quality analysis",
                "CEFR level validation and alignment",
                "Grammar and linguistic accuracy checking",
                "Cultural sensitivity assessment",
                "Pedagogical effectiveness evaluation",
                "Content improvement generation",
                "Batch content review processing"
            ],
            "review_criteria": [
                "linguistic_accuracy",
                "cefr_alignment", 
                "pedagogical_effectiveness",
                "cultural_sensitivity",
                "engagement_relevance",
                "technical_quality"
            ],
            "supported_content_types": [
                "lesson", "exercise", "assessment", "module", "course"
            ],
            "quality_standards": {
                "minimum_approval_score": 80,
                "critical_issue_threshold": "Must be resolved",
                "review_turnaround": "< 30 seconds per item"
            },
            "status": "active"
        }
    
    async def validate_review_request(self, request: QualityReviewRequest) -> Dict[str, Any]:
        """Validate a quality review request."""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check CEFR level
        valid_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        if request.target_cefr_level not in valid_levels:
            validation_results["errors"].append(f"Invalid CEFR level: {request.target_cefr_level}")
            validation_results["valid"] = False
        
        # Check content data
        if not request.content_data:
            validation_results["errors"].append("Content data is required")
            validation_results["valid"] = False
        
        # Check review criteria
        valid_criteria = [
            "linguistic_accuracy", "cefr_alignment", "pedagogical_effectiveness",
            "cultural_sensitivity", "engagement_relevance", "technical_quality"
        ]
        invalid_criteria = [c for c in request.review_criteria if c not in valid_criteria]
        if invalid_criteria:
            validation_results["warnings"].append(f"Unknown criteria: {', '.join(invalid_criteria)}")
        
        # Check content type
        valid_types = ["lesson", "exercise", "assessment", "module", "course"]
        if request.content_type not in valid_types:
            validation_results["warnings"].append(f"Unusual content type: {request.content_type}")
        
        return validation_results
    
    async def generate_quality_metrics(self, review_results: List[QualityReport]) -> Dict[str, Any]:
        """Generate quality metrics from review results."""
        
        if not review_results:
            return {"error": "No review results provided"}
        
        total_items = len(review_results)
        approved_items = len([r for r in review_results if r.approved_for_release])
        
        # Calculate average scores
        avg_overall_score = sum(r.overall_score for r in review_results) / total_items
        
        # Criteria-specific averages
        criteria_averages = {}
        for criteria in review_results[0].review_criteria_scores.keys():
            scores = [r.review_criteria_scores.get(criteria, 0) for r in review_results]
            criteria_averages[criteria] = sum(scores) / len(scores) if scores else 0
        
        # Issue analysis
        all_issues = []
        for result in review_results:
            all_issues.extend(result.issues_found)
        
        issue_types = {}
        for issue in all_issues:
            issue_type = issue.get("type", "unknown")
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        return {
            "summary": {
                "total_items_reviewed": total_items,
                "items_approved": approved_items,
                "approval_rate": (approved_items / total_items) * 100,
                "average_quality_score": round(avg_overall_score, 2)
            },
            "criteria_performance": criteria_averages,
            "common_issues": issue_types,
            "quality_distribution": {
                "excellent": len([r for r in review_results if r.overall_score >= 90]),
                "good": len([r for r in review_results if 80 <= r.overall_score < 90]),
                "needs_improvement": len([r for r in review_results if r.overall_score < 80])
            },
            "generated_at": datetime.utcnow().isoformat()
        }

# Global service instance
quality_assurance_service = QualityAssuranceService()

# Main execution for testing
async def main():
    """Test the quality assurance agent."""
    test_request = QualityReviewRequest(
        content_id="test_lesson_001",
        content_type="lesson",
        content_data={
            "title": "Business Email Writing",
            "learning_objectives": ["Write professional emails", "Use appropriate tone"],
            "activities": [
                {"type": "reading", "description": "Read sample business emails"},
                {"type": "writing", "description": "Compose formal email responses"}
            ],
            "vocabulary": ["formal language", "email structure", "professional tone"],
            "grammar_focus": ["modal verbs", "conditional sentences"]
        },
        target_cefr_level="B1",
        review_criteria=["linguistic_accuracy", "cefr_alignment", "cultural_sensitivity"]
    )
    
    try:
        quality_report = await quality_assurance_service.review_content(test_request)
        print("Quality Review Report:")
        print(json.dumps(quality_report.dict(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())