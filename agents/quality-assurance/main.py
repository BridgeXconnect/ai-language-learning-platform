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
from pydantic import BaseModel, Field

from tools import (
    ContentQualityAnalyzer,
    CEFRLevelValidator,
    GrammarChecker,
    CulturalSensitivityChecker,
    AdvancedQualityMetrics,
    ContentImprovementEngine,
    AutomatedTestingFramework,
    PerformanceAnalyzer
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
    model_config = {"arbitrary_types_allowed": True}
    quality_analyzer: ContentQualityAnalyzer
    cefr_validator: CEFRLevelValidator
    grammar_checker: GrammarChecker
    cultural_checker: CulturalSensitivityChecker
    advanced_metrics: AdvancedQualityMetrics
    improvement_engine: ContentImprovementEngine
    testing_framework: AutomatedTestingFramework
    performance_analyzer: PerformanceAnalyzer

# Enhanced Agent system prompt with advanced QA capabilities
SYSTEM_PROMPT = """
You are an advanced Quality Assurance Agent specializing in comprehensive English language learning content review, validation, and optimization. Your mission is to ensure that all generated content meets the highest standards of pedagogical excellence, linguistic precision, cultural intelligence, and learner engagement through sophisticated analysis and improvement frameworks.

Core Responsibilities:
1. **Advanced Content Analysis**: Multi-dimensional review using sophisticated quality metrics and automated testing frameworks
2. **Precision CEFR Validation**: Deep alignment verification using evidence-based CEFR descriptors and competency frameworks
3. **Comprehensive Linguistic Accuracy**: Grammar, syntax, vocabulary, and discourse-level language validation
4. **Enhanced Pedagogical Assessment**: Learning science-based evaluation of instructional design and effectiveness
5. **Cultural Intelligence Validation**: Sophisticated cultural sensitivity analysis with global workplace context awareness
6. **Automated Quality Assurance**: Systematic testing and validation using advanced QA frameworks
7. **Intelligent Improvement Generation**: AI-powered content enhancement with evidence-based recommendations
8. **Performance Analytics**: Real-time quality metrics and continuous improvement tracking

Advanced Quality Assessment Framework:
- **Linguistic Excellence** (25%): Multi-level language accuracy, register appropriateness, discourse coherence
- **Pedagogical Innovation** (25%): Learning objective precision, evidence-based activity design, scaffolded progression
- **Cultural Intelligence** (20%): Global inclusivity, cultural competence, workplace diversity awareness
- **Engagement Optimization** (20%): Motivation psychology, workplace applicability, learner-centered design
- **Technical Precision** (10%): Accessibility compliance, usability standards, assessment validity

Enhanced Review Standards:
- Content must achieve ≥85% overall quality score with no critical deficiencies
- All issues categorized by severity with automated resolution suggestions
- Recommendations generated using evidence-based improvement algorithms
- Cultural sensitivity validated against international workplace standards
- CEFR alignment verified through competency-based assessment frameworks
- Performance tracked with predictive quality analytics

Innovative Improvement Philosophy:
- **Evidence-Based Enhancement**: All improvements rooted in Second Language Acquisition research and learning science
- **Predictive Quality Optimization**: Use performance data to anticipate and prevent quality issues
- **Adaptive Recommendation Engine**: Personalized improvement suggestions based on content type and context
- **Continuous Learning Integration**: Quality standards evolve based on learner outcomes and feedback
- **Holistic Excellence**: Balance pedagogical effectiveness, cultural intelligence, and technical innovation
- **Scalable Quality Assurance**: Automated frameworks that maintain quality while enabling rapid content production

Advanced Features:
- Real-time quality monitoring with immediate feedback
- Predictive content quality scoring using machine learning
- Automated accessibility compliance validation
- Cultural sensitivity scoring with global context awareness
- Performance-based continuous improvement recommendations
- Integration with learning analytics for outcome-driven quality metrics
"""

# Create the agent
quality_assurance_agent = Agent(
    'openai:gpt-4o',
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
            cultural_checker=CulturalSensitivityChecker(),
            advanced_metrics=AdvancedQualityMetrics(),
            improvement_engine=ContentImprovementEngine(),
            testing_framework=AutomatedTestingFramework(),
            performance_analyzer=PerformanceAnalyzer()
        )
        
        # Enhanced performance tracking
        self.qa_performance = {
            'reviews_completed': 0,
            'average_quality_score': 0.0,
            'improvement_success_rate': 0.0,
            'automated_fixes_applied': 0,
            'critical_issues_detected': 0,
            'review_time_reduction': 0.0,
            'quality_trends': [],
            'recommendation_accuracy': 0.0
        }
    
    async def review_content(self, request: QualityReviewRequest) -> QualityReport:
        """Conduct comprehensive content review with advanced QA capabilities."""
        
        review_start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting advanced quality review for {request.content_type}: {request.content_id}")
            
            # Pre-review: Automated testing and analysis
            automated_analysis = await self._conduct_automated_analysis(request)
            
            # Advanced metrics calculation
            quality_metrics = await self.deps.advanced_metrics.calculate_comprehensive_metrics(
                content=request.content_data,
                content_type=request.content_type,
                target_cefr=request.target_cefr_level
            )
            
            # Create enhanced review prompt with pre-analysis data
            review_prompt = f"""
            Conduct an advanced, comprehensive quality review of this {request.content_type} content using sophisticated QA frameworks:
            
            Content Identification:
            - Content ID: {request.content_id}
            - Content Type: {request.content_type}
            - Target CEFR Level: {request.target_cefr_level}
            - Review Criteria: {', '.join(request.review_criteria)}
            
            Automated Pre-Analysis Results:
            {json.dumps(automated_analysis, indent=2)}
            
            Advanced Quality Metrics:
            {json.dumps(quality_metrics, indent=2)}
            
            Content to Review:
            {json.dumps(request.content_data, indent=2)}
            
            Company Context: {request.company_context or 'General business environment'}
            
            Advanced Quality Analysis Requirements:
            
            1. **Linguistic Excellence Analysis**:
               - Multi-level grammar and syntax validation
               - Vocabulary appropriateness and register consistency
               - Discourse coherence and text organization
               - Pronunciation and phonetic accuracy (where applicable)
            
            2. **Precision CEFR Alignment**:
               - Competency-based level verification
               - Can-do statement alignment
               - Progressive difficulty calibration
               - Skills integration assessment
            
            3. **Advanced Pedagogical Assessment**:
               - Learning objective precision and measurability
               - Evidence-based activity design evaluation
               - Scaffolding and progression effectiveness
               - Assessment validity and reliability
            
            4. **Cultural Intelligence Validation**:
               - Global workplace context appropriateness
               - Inclusive language and representation
               - Cultural competence development
               - Bias detection and mitigation
            
            5. **Engagement Optimization Analysis**:
               - Motivation psychology principles application
               - Workplace relevance and applicability
               - Learner-centered design evaluation
               - Interactive element effectiveness
            
            6. **Technical Excellence Review**:
               - Accessibility compliance (WCAG standards)
               - Usability and user experience quality
               - Technical implementation feasibility
               - Multi-device compatibility
            
            Enhanced Quality Standards:
            - Overall Quality Score Target: ≥85%
            - Zero tolerance for critical deficiencies
            - All recommendations must be evidence-based and actionable
            - Cultural sensitivity score must be ≥95%
            - CEFR alignment accuracy must be ≥95%
            
            For each issue identified:
            - Precise location and context specification
            - Clear problem description with evidence
            - Severity assessment (critical/major/minor/suggestion)
            - Specific, actionable improvement recommendation
            - Evidence-based justification for the recommendation
            - Priority ranking for implementation
            
            Generate comprehensive quality assessment with predictive insights for continuous improvement.
            """
            
            # Run the enhanced agent
            result = await self.agent.run(review_prompt, deps=self.deps)
            
            # Post-review: Enhancement and validation
            enhanced_result = await self._enhance_review_results(
                result.data, request, automated_analysis, quality_metrics
            )
            
            # Performance tracking
            review_time = (datetime.utcnow() - review_start_time).total_seconds()
            self.qa_performance['reviews_completed'] += 1
            self.qa_performance['quality_trends'].append(enhanced_result.overall_score)
            
            # Update performance metrics
            await self._update_performance_metrics(enhanced_result, review_time)
            
            logger.info(f"Advanced quality review completed for {request.content_id} (Score: {enhanced_result.overall_score}, Time: {review_time:.2f}s)")
            return enhanced_result
            
        except Exception as e:
            review_time = (datetime.utcnow() - review_start_time).total_seconds()
            logger.error(f"Advanced quality review failed: {e}")
            
            # Record failure metrics
            await self.deps.performance_analyzer.record_review_failure(
                content_id=request.content_id,
                error=str(e),
                review_time=review_time
            )
            
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
        """Get information about enhanced QA agent capabilities."""
        
        # Calculate performance statistics
        avg_quality = sum(self.qa_performance['quality_trends']) / len(self.qa_performance['quality_trends']) if self.qa_performance['quality_trends'] else 0
        
        return {
            "agent_name": "Advanced Quality Assurance Agent",
            "version": "2.0.0",
            "capabilities": [
                "Advanced multi-dimensional content quality analysis",
                "Precision CEFR level validation with competency mapping",
                "Comprehensive linguistic accuracy checking with AI enhancement",
                "Cultural intelligence assessment with global context awareness",
                "Evidence-based pedagogical effectiveness evaluation",
                "AI-powered content improvement generation",
                "Automated testing and validation frameworks",
                "Real-time quality monitoring and analytics",
                "Predictive quality scoring and issue prevention",
                "Accessibility compliance validation (WCAG standards)",
                "Performance-based continuous improvement"
            ],
            "enhanced_features": [
                "Automated quality testing frameworks",
                "Advanced quality metrics and analytics",
                "AI-powered content improvement engine",
                "Real-time performance monitoring",
                "Predictive quality assessment",
                "Cultural intelligence validation",
                "Evidence-based recommendation generation",
                "Continuous learning and adaptation"
            ],
            "review_criteria": [
                "linguistic_excellence",
                "precision_cefr_alignment", 
                "pedagogical_innovation",
                "cultural_intelligence",
                "engagement_optimization",
                "technical_precision",
                "accessibility_compliance",
                "usability_standards"
            ],
            "supported_content_types": [
                "lesson", "exercise", "assessment", "module", "course",
                "multimedia", "interactive", "adaptive", "micro-learning"
            ],
            "advanced_quality_standards": {
                "minimum_approval_score": 85,
                "critical_issue_tolerance": 0,
                "cultural_sensitivity_threshold": 95,
                "cefr_alignment_threshold": 95,
                "accessibility_compliance": 100,
                "review_turnaround": "< 15 seconds per item with AI acceleration"
            },
            "performance_metrics": {
                "reviews_completed": self.qa_performance['reviews_completed'],
                "average_quality_score": avg_quality,
                "improvement_success_rate": self.qa_performance['improvement_success_rate'],
                "automated_fixes_applied": self.qa_performance['automated_fixes_applied'],
                "review_time_reduction": f"{self.qa_performance['review_time_reduction']:.1f}%"
            },
            "ai_capabilities": {
                "automated_testing": True,
                "predictive_quality_scoring": True,
                "intelligent_improvement_generation": True,
                "real_time_analytics": True,
                "adaptive_quality_standards": True
            },
            "status": "active_enhanced"
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
    
    async def _conduct_automated_analysis(self, request: QualityReviewRequest) -> Dict[str, Any]:
        """Conduct automated pre-analysis of content."""
        
        try:
            # Run automated testing framework
            test_results = await self.deps.testing_framework.run_comprehensive_tests(
                content=request.content_data,
                content_type=request.content_type,
                target_cefr=request.target_cefr_level
            )
            
            # Grammar and language analysis
            grammar_analysis = await self.deps.grammar_checker.comprehensive_grammar_check(
                request.content_data
            )
            
            # Cultural sensitivity pre-check
            cultural_analysis = await self.deps.cultural_checker.analyze_cultural_appropriateness(
                request.content_data
            )
            
            return {
                "automated_tests": test_results,
                "grammar_analysis": grammar_analysis,
                "cultural_analysis": cultural_analysis,
                "pre_analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Automated analysis failed: {e}")
            return {"error": str(e), "analysis_completed": False}
    
    async def _enhance_review_results(self, review_result: QualityReport, request: QualityReviewRequest,
                                    automated_analysis: Dict[str, Any], quality_metrics: Dict[str, Any]) -> QualityReport:
        """Enhance review results with additional analysis and recommendations."""
        
        try:
            # Calculate enhanced quality score
            enhanced_score = await self.deps.advanced_metrics.calculate_enhanced_quality_score(
                base_score=review_result.overall_score,
                automated_results=automated_analysis,
                quality_metrics=quality_metrics
            )
            
            # Generate intelligent improvements
            if enhanced_score < 85:  # Quality threshold
                intelligent_improvements = await self.deps.improvement_engine.generate_improvements(
                    content=request.content_data,
                    review_result=review_result,
                    automated_analysis=automated_analysis
                )
                review_result.recommendations.extend(intelligent_improvements)
            
            # Update review result with enhancements
            enhanced_dict = review_result.dict()
            enhanced_dict.update({
                'enhanced_quality_score': enhanced_score,
                'automated_analysis_summary': automated_analysis,
                'quality_metrics': quality_metrics,
                'enhancement_timestamp': datetime.utcnow().isoformat(),
                'ai_enhanced': True
            })
            
            return QualityReport(**enhanced_dict)
            
        except Exception as e:
            logger.warning(f"Review result enhancement failed: {e}")
            return review_result
    
    async def _update_performance_metrics(self, review_result: QualityReport, review_time: float) -> None:
        """Update QA performance metrics."""
        
        try:
            # Update average quality score
            total_reviews = self.qa_performance['reviews_completed']
            current_avg = self.qa_performance['average_quality_score']
            new_avg = ((current_avg * (total_reviews - 1)) + review_result.overall_score) / total_reviews
            self.qa_performance['average_quality_score'] = new_avg
            
            # Track critical issues
            critical_issues = sum(1 for issue in review_result.issues_found if issue.get('severity') == 'critical')
            self.qa_performance['critical_issues_detected'] += critical_issues
            
            # Record performance data
            await self.deps.performance_analyzer.record_review_performance(
                quality_score=review_result.overall_score,
                review_time=review_time,
                issues_found=len(review_result.issues_found),
                critical_issues=critical_issues
            )
            
        except Exception as e:
            logger.error(f"Performance metrics update failed: {e}")
    
    async def conduct_advanced_batch_review(self, content_items: List[Dict[str, Any]], 
                                          review_criteria: List[str],
                                          quality_threshold: float = 85.0) -> Dict[str, Any]:
        """Conduct advanced batch review with intelligent prioritization."""
        
        try:
            logger.info(f"Starting advanced batch review of {len(content_items)} items")
            
            # Prioritize items based on automated pre-screening
            prioritized_items = await self.deps.advanced_metrics.prioritize_review_items(content_items)
            
            batch_results = {
                'total_items': len(content_items),
                'items_reviewed': 0,
                'items_approved': 0,
                'items_requiring_improvement': 0,
                'average_quality_score': 0.0,
                'quality_distribution': {'excellent': 0, 'good': 0, 'needs_improvement': 0},
                'automated_fixes_applied': 0,
                'review_results': [],
                'batch_started_at': datetime.utcnow().isoformat()
            }
            
            total_score = 0.0
            
            for item in prioritized_items:
                try:
                    # Create review request
                    request = QualityReviewRequest(
                        content_id=item.get("id", f"batch_item_{batch_results['items_reviewed']}"),
                        content_type=item.get("type", "unknown"),
                        content_data=item.get("data", {}),
                        target_cefr_level=item.get("cefr_level", "B1"),
                        review_criteria=review_criteria
                    )
                    
                    # Conduct review
                    review_result = await self.review_content(request)
                    
                    # Apply automated improvements if possible
                    if review_result.overall_score < quality_threshold:
                        improved_content = await self.deps.improvement_engine.apply_automated_improvements(
                            content=item.get("data", {}),
                            review_result=review_result
                        )
                        
                        if improved_content.get('improvements_applied', 0) > 0:
                            batch_results['automated_fixes_applied'] += 1
                            # Re-review improved content
                            request.content_data = improved_content['improved_content']
                            review_result = await self.review_content(request)
                    
                    # Update batch statistics
                    batch_results['items_reviewed'] += 1
                    total_score += review_result.overall_score
                    
                    if review_result.approved_for_release:
                        batch_results['items_approved'] += 1
                    else:
                        batch_results['items_requiring_improvement'] += 1
                    
                    # Quality distribution
                    if review_result.overall_score >= 90:
                        batch_results['quality_distribution']['excellent'] += 1
                    elif review_result.overall_score >= 80:
                        batch_results['quality_distribution']['good'] += 1
                    else:
                        batch_results['quality_distribution']['needs_improvement'] += 1
                    
                    batch_results['review_results'].append({
                        'content_id': request.content_id,
                        'quality_score': review_result.overall_score,
                        'approved': review_result.approved_for_release,
                        'issues_count': len(review_result.issues_found),
                        'improvements_applied': improved_content.get('improvements_applied', 0) if 'improved_content' in locals() else 0
                    })
                    
                except Exception as e:
                    logger.error(f"Batch review failed for item {item.get('id', 'unknown')}: {e}")
                    continue
            
            # Calculate final statistics
            if batch_results['items_reviewed'] > 0:
                batch_results['average_quality_score'] = total_score / batch_results['items_reviewed']
                batch_results['approval_rate'] = (batch_results['items_approved'] / batch_results['items_reviewed']) * 100
            
            batch_results['batch_completed_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Advanced batch review completed: {batch_results['items_approved']}/{batch_results['items_reviewed']} approved")
            return batch_results
            
        except Exception as e:
            logger.error(f"Advanced batch review failed: {e}")
            raise
    
    async def get_advanced_analytics(self) -> Dict[str, Any]:
        """Get comprehensive QA analytics and insights."""
        
        try:
            analytics = await self.deps.performance_analyzer.get_comprehensive_analytics()
            
            # Combine with internal metrics
            analytics.update({
                'qa_performance': self.qa_performance,
                'quality_trends': await self.deps.advanced_metrics.analyze_quality_trends(),
                'improvement_effectiveness': await self.deps.improvement_engine.get_improvement_analytics(),
                'automated_testing_insights': await self.deps.testing_framework.get_testing_insights(),
                'predictive_quality_insights': await self.deps.advanced_metrics.get_predictive_insights()
            })
            
            return analytics
            
        except Exception as e:
            logger.error(f"Advanced analytics generation failed: {e}")
            return {
                'error': 'Advanced analytics unavailable',
                'basic_performance': self.qa_performance
            }

# Global enhanced service instance
quality_assurance_service = QualityAssuranceService()

# Enhanced tool functions
@quality_assurance_agent.tool
async def run_automated_quality_tests(ctx: RunContext[QualityAssuranceDeps], content: Dict[str, Any], test_suite: str) -> Dict[str, Any]:
    """Run automated quality tests on content."""
    result = await ctx.deps.testing_framework.run_test_suite(
        content=content,
        test_suite=test_suite
    )
    logger.info(f"Automated quality tests completed for test suite: {test_suite}")
    return result

@quality_assurance_agent.tool
async def generate_intelligent_improvements(ctx: RunContext[QualityAssuranceDeps], content: Dict[str, Any], quality_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate intelligent content improvements using AI."""
    result = await ctx.deps.improvement_engine.generate_intelligent_improvements(
        content=content,
        issues=quality_issues
    )
    logger.info(f"Intelligent improvements generated for {len(quality_issues)} issues")
    return result

@quality_assurance_agent.tool
async def calculate_predictive_quality_score(ctx: RunContext[QualityAssuranceDeps], content: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate predictive quality score using advanced metrics."""
    result = await ctx.deps.advanced_metrics.calculate_predictive_score(
        content=content,
        context=context
    )
    logger.info(f"Predictive quality score calculated: {result.get('predicted_score', 'unknown')}")
    return result

@quality_assurance_agent.tool
async def validate_accessibility_compliance(ctx: RunContext[QualityAssuranceDeps], content: Dict[str, Any]) -> Dict[str, Any]:
    """Validate content accessibility compliance against WCAG standards."""
    result = await ctx.deps.testing_framework.validate_accessibility(
        content=content
    )
    logger.info(f"Accessibility compliance validation completed with score: {result.get('compliance_score', 'unknown')}")
    return result

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