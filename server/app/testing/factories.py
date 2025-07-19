"""
Pydantic Model Factories for Testing

This module provides factory classes for creating test instances of Pydantic models
with proper validation and realistic test data. These factories ensure that:

1. All test data passes Pydantic validation
2. Test data is consistent and maintainable
3. Factories can be easily updated when models change
4. Test data is realistic but clearly identifiable as test data
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# Import all the models we need to create factories for
from ..services.ai_assessment_service import Assessment, QualityScore, AIAssessmentDeps, QuestionType, DifficultyLevel
from ..services.ai_recommendation_engine import LearningRecommendation, UserProfile, CourseRecommendation
from ..services.qa_automation_service import QATestResult, QualityReport, TestCase
from ..services.agent_orchestration_service import AgentStatus, WorkflowStatus, OrchestrationConfig

class AssessmentFactory:
    """Factory for creating test Assessment instances."""
    
    @staticmethod
    def create(
        topic: str = "Test Customer Service",
        difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
        question_count: int = 3
    ) -> Assessment:
        """Create a test assessment with realistic data."""
        
        questions = []
        for i in range(question_count):
            question_type = QuestionType.MULTIPLE_CHOICE if i % 2 == 0 else QuestionType.TRUE_FALSE
            question = {
                "id": i + 1,
                "type": question_type.value,
                "question": f"Test question {i + 1} about {topic}?",
                "options": ["Option A", "Option B", "Option C", "Option D"] if question_type == QuestionType.MULTIPLE_CHOICE else None,
                "correct_answer": 0 if question_type == QuestionType.MULTIPLE_CHOICE else "True",
                "explanation": f"This is a test explanation for question {i + 1}",
                "difficulty": difficulty.value,
                "cognitive_level": "understand"
            }
            questions.append(question)
        
        return Assessment(
            assessment_id=f"test_assessment_{uuid.uuid4().hex[:8]}",
            topic=topic,
            difficulty=difficulty,
            questions=questions,
            metadata={
                "question_count": len(questions),
                "difficulty_distribution": {"beginner": 0.0, "intermediate": 1.0, "advanced": 0.0},
                "cognitive_levels": {"remember": 0, "understand": len(questions), "apply": 0, "analyze": 0, "evaluate": 0, "create": 0},
                "estimated_duration": len(questions) * 60,
                "test_data": True
            },
            created_at=datetime.now()
        )
    
    @staticmethod
    def create_minimal() -> Assessment:
        """Create a minimal test assessment."""
        return AssessmentFactory.create(topic="Minimal Test", question_count=1)
    
    @staticmethod
    def create_comprehensive() -> Assessment:
        """Create a comprehensive test assessment with multiple question types."""
        return AssessmentFactory.create(
            topic="Comprehensive Test",
            difficulty=DifficultyLevel.ADVANCED,
            question_count=5
        )

class QualityScoreFactory:
    """Factory for creating test QualityScore instances."""
    
    @staticmethod
    def create(
        overall_score: float = 0.85,
        clarity_score: float = 0.90,
        accuracy_score: float = 0.95,
        engagement_score: float = 0.80,
        educational_value: float = 0.85
    ) -> QualityScore:
        """Create a test quality score."""
        return QualityScore(
            overall_score=overall_score,
            clarity_score=clarity_score,
            accuracy_score=accuracy_score,
            engagement_score=engagement_score,
            educational_value=educational_value
        )
    
    @staticmethod
    def create_excellent() -> QualityScore:
        """Create an excellent quality score."""
        return QualityScoreFactory.create(
            overall_score=0.95,
            clarity_score=0.95,
            accuracy_score=0.98,
            engagement_score=0.90,
            educational_value=0.95
        )
    
    @staticmethod
    def create_needs_improvement() -> QualityScore:
        """Create a quality score that needs improvement."""
        return QualityScoreFactory.create(
            overall_score=0.65,
            clarity_score=0.70,
            accuracy_score=0.80,
            engagement_score=0.60,
            educational_value=0.70
        )

class AIAssessmentDepsFactory:
    """Factory for creating test AIAssessmentDeps instances."""
    
    @staticmethod
    def create(
        openai_client: Optional[Any] = None,
        anthropic_client: Optional[Any] = None,
        assessment_generator: Optional[Any] = None,
        quality_analyzer: Optional[Any] = None
    ) -> AIAssessmentDeps:
        """Create test dependencies."""
        return AIAssessmentDeps(
            openai_client=openai_client,
            anthropic_client=anthropic_client,
            assessment_generator=assessment_generator,
            quality_analyzer=quality_analyzer
        )
    
    @staticmethod
    def create_empty() -> AIAssessmentDeps:
        """Create empty dependencies for testing without AI services."""
        return AIAssessmentDepsFactory.create()

class LearningRecommendationFactory:
    """Factory for creating test LearningRecommendation instances."""
    
    @staticmethod
    def create(
        user_id: str = "test_user_123",
        skill_area: str = "Business Communication",
        current_level: str = "B1",
        target_level: str = "B2",
        confidence: float = 0.85
    ) -> LearningRecommendation:
        """Create a test learning recommendation."""
        return LearningRecommendation(
            user_id=user_id,
            skill_area=skill_area,
            current_level=current_level,
            target_level=target_level,
            confidence=confidence,
            recommended_activities=[
                {"type": "practice", "description": "Email writing exercises"},
                {"type": "assessment", "description": "Grammar quiz"}
            ],
            estimated_duration_hours=10,
            priority="high",
            created_at=datetime.now()
        )

class UserProfileFactory:
    """Factory for creating test UserProfile instances."""
    
    @staticmethod
    def create(
        user_id: str = "test_user_123",
        english_level: str = "B1",
        learning_goals: List[str] = None,
        preferred_learning_style: str = "visual"
    ) -> UserProfile:
        """Create a test user profile."""
        if learning_goals is None:
            learning_goals = ["Business Communication", "Technical Writing"]
        
        return UserProfile(
            user_id=user_id,
            english_level=english_level,
            learning_goals=learning_goals,
            preferred_learning_style=preferred_learning_style,
            completed_courses=2,
            total_study_hours=25.5,
            strengths=["Grammar", "Reading"],
            areas_for_improvement=["Speaking", "Listening"],
            last_activity=datetime.now() - timedelta(days=2)
        )

class CourseRecommendationFactory:
    """Factory for creating test CourseRecommendation instances."""
    
    @staticmethod
    def create(
        user_id: str = "test_user_123",
        course_id: str = "test_course_456",
        relevance_score: float = 0.92,
        difficulty_match: float = 0.85
    ) -> CourseRecommendation:
        """Create a test course recommendation."""
        return CourseRecommendation(
            user_id=user_id,
            course_id=course_id,
            relevance_score=relevance_score,
            difficulty_match=difficulty_match,
            estimated_completion_time_hours=15,
            prerequisites_met=True,
            learning_objectives_alignment=0.88,
            recommended_start_date=datetime.now() + timedelta(days=1),
            confidence_level="high"
        )

class QATestResultFactory:
    """Factory for creating test QATestResult instances."""
    
    @staticmethod
    def create(
        test_name: str = "Content Quality Test",
        status: str = "passed",
        score: float = 0.95,
        details: Dict[str, Any] = None
    ) -> QATestResult:
        """Create a test QA result."""
        if details is None:
            details = {
                "clarity_score": 0.95,
                "accuracy_score": 0.98,
                "engagement_score": 0.90
            }
        
        return QATestResult(
            test_name=test_name,
            status=status,
            score=score,
            details=details,
            execution_time_seconds=2.5,
            timestamp=datetime.now()
        )

class QualityReportFactory:
    """Factory for creating test QualityReport instances."""
    
    @staticmethod
    def create(
        report_id: str = None,
        content_id: str = "test_content_789",
        overall_score: float = 0.88
    ) -> QualityReport:
        """Create a test quality report."""
        if report_id is None:
            report_id = f"qr_{uuid.uuid4().hex[:8]}"
        
        return QualityReport(
            report_id=report_id,
            content_id=content_id,
            overall_score=overall_score,
            test_results=[
                QATestResultFactory.create("Grammar Check", "passed", 0.95),
                QATestResultFactory.create("Content Relevance", "passed", 0.85),
                QATestResultFactory.create("Readability", "passed", 0.90)
            ],
            recommendations=[
                "Consider adding more examples",
                "Improve transition sentences"
            ],
            generated_at=datetime.now()
        )

class TestCaseFactory:
    """Factory for creating test TestCase instances."""
    
    @staticmethod
    def create(
        name: str = "Test Case 1",
        description: str = "Test case for content validation",
        test_type: str = "automated"
    ) -> TestCase:
        """Create a test case."""
        return TestCase(
            name=name,
            description=description,
            test_type=test_type,
            parameters={
                "min_score": 0.8,
                "max_duration": 5.0
            },
            expected_result="pass",
            created_at=datetime.now()
        )

class AgentStatusFactory:
    """Factory for creating test AgentStatus instances."""
    
    @staticmethod
    def create(
        agent_id: str = "test_agent_123",
        status: str = "active",
        health_score: float = 0.95
    ) -> AgentStatus:
        """Create a test agent status."""
        return AgentStatus(
            agent_id=agent_id,
            status=status,
            health_score=health_score,
            last_heartbeat=datetime.now(),
            response_time_ms=150,
            error_count=0,
            uptime_hours=24.5
        )

class WorkflowStatusFactory:
    """Factory for creating test WorkflowStatus instances."""
    
    @staticmethod
    def create(
        workflow_id: str = "test_workflow_456",
        status: str = "completed",
        progress_percentage: float = 100.0
    ) -> WorkflowStatus:
        """Create a test workflow status."""
        return WorkflowStatus(
            workflow_id=workflow_id,
            status=status,
            progress_percentage=progress_percentage,
            current_step="final_validation",
            total_steps=5,
            started_at=datetime.now() - timedelta(minutes=10),
            estimated_completion=datetime.now() + timedelta(minutes=2),
            error_message=None
        )

class OrchestrationConfigFactory:
    """Factory for creating test OrchestrationConfig instances."""
    
    @staticmethod
    def create(
        max_concurrent_agents: int = 5,
        timeout_seconds: int = 300,
        retry_attempts: int = 3
    ) -> OrchestrationConfig:
        """Create a test orchestration config."""
        return OrchestrationConfig(
            max_concurrent_agents=max_concurrent_agents,
            timeout_seconds=timeout_seconds,
            retry_attempts=retry_attempts,
            health_check_interval=30,
            load_balancing_strategy="round_robin",
            fallback_agents=["backup_agent_1", "backup_agent_2"]
        )

# Convenience function to create all test data for a complete test scenario
def create_test_scenario() -> Dict[str, Any]:
    """Create a complete test scenario with all model instances."""
    return {
        "assessment": AssessmentFactory.create(),
        "quality_score": QualityScoreFactory.create_excellent(),
        "user_profile": UserProfileFactory.create(),
        "learning_recommendation": LearningRecommendationFactory.create(),
        "course_recommendation": CourseRecommendationFactory.create(),
        "qa_test_result": QATestResultFactory.create(),
        "quality_report": QualityReportFactory.create(),
        "agent_status": AgentStatusFactory.create(),
        "workflow_status": WorkflowStatusFactory.create(),
        "orchestration_config": OrchestrationConfigFactory.create()
    } 