"""
Ai Domain - Assessment
Consolidated from: ai_assessment_service.py
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from pydantic_ai.tools import Tool
from typing import Dict, Any, List, Optional, Tuple, TypeVar, Generic
import anthropic
import asyncio
import json
import logging
import numpy as np
import openai
import os

class MockAgent:
    def __init__(self, model_name: str, system_prompt: str = "", deps_type=None):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.deps_type = deps_type
        self.tools = []
    
    def tool(self, func):
        self.tools.append(func)
        return func
    
    async def run(self, description, deps=None, tool_calls=None):
        tool_name = tool_calls[0]["tool_name"] if tool_calls else ""
        if tool_name == "generate_assessment":
            return type("Result", (), {"data": {"assessment_id": "mock_assessment", "questions": ["Q1", "Q2"]}})()
        else:
            return type("Result", (), {"data": {}})()


class MockRunContext(Generic[T]):
    def __init__(self, deps=None):
        self.deps = deps
    
    def __getitem__(self, key):
        # Support subscripting like RunContext[AIContentDeps]
        return self.__class__

# Use mock classes instead of pydantic_ai imports
Agent = MockAgent
RunContext = MockRunContext
from pydantic_ai.tools import Tool
import openai
import anthropic
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    MATCHING = "matching"


class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Assessment(BaseModel):
    assessment_id: str
    topic: str
    difficulty: DifficultyLevel
    questions: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime


class QualityScore(BaseModel):
    overall_score: float
    clarity_score: float
    accuracy_score: float
    engagement_score: float
    educational_value: float


class AIAssessmentDeps(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    openai_client: Any
    anthropic_client: Any
    assessment_generator: Any
    quality_analyzer: Any

# AI Assessment System Prompt
ASSESSMENT_PROMPT = """
You are an advanced AI assessment creation system specializing in educational assessment design. You excel at:

1. **Assessment Creation**: Generate comprehensive assessments with various question types
2. **Content Quality Validation**: Ensure educational value and accuracy
3. **Question Regeneration**: Improve questions based on feedback
4. **Difficulty Balancing**: Create appropriate difficulty distributions
5. **Cognitive Level Targeting**: Apply Bloom's taxonomy principles

Core Capabilities:
- Multi-format question generation (multiple choice, fill-in-blank, essay, etc.)
- Automated content quality assessment
- Intelligent question regeneration and improvement
- Difficulty distribution optimization
- Cognitive level balancing using Bloom's taxonomy
- Educational standards compliance
- Accessibility considerations

Assessment Design Principles:
- Clear, unambiguous question formulation
- Appropriate difficulty progression
- Balanced cognitive level distribution
- Authentic assessment tasks
- Immediate feedback provision
- Progress tracking integration
- Cultural sensitivity and inclusivity
"""

# Create the AI Assessment agent
ai_assessment_agent = Agent(
    'openai:gpt-4o',
    system_prompt=ASSESSMENT_PROMPT,
    deps_type=AIAssessmentDeps
)

@ai_assessment_agent.tool
async def create_assessment(
    ctx: RunContext[AIAssessmentDeps],
    topic: str,
    difficulty: str,
    question_types: List[str],
    question_count: int
) -> Dict[str, Any]:
    """Create a comprehensive assessment with various question types."""
    
    # Validate difficulty level
    try:
        difficulty_enum = DifficultyLevel(difficulty.lower())
    except ValueError:
        raise ValueError(f"Invalid difficulty level: {difficulty}")
    
    # Generate questions
    questions = []
    for i in range(question_count):
        question_type = question_types[i % len(question_types)]
        question = await _generate_question(ctx, topic, difficulty_enum, question_type, i + 1)
        questions.append(question)
    
    # Create assessment object
    assessment = Assessment(
        assessment_id=f"assessment_{topic}_{datetime.now().timestamp()}",
        topic=topic,
        difficulty=difficulty_enum,
        questions=questions,
        metadata={
            "question_count": len(questions),
            "difficulty_distribution": await _calculate_difficulty_distribution(questions),
            "cognitive_levels": await _analyze_cognitive_levels(questions),
            "estimated_duration": len(questions) * 60  # 1 minute per question
        },
        created_at=datetime.now()
    )
    
    logger.info(f"Created assessment for topic: {topic} with {len(questions)} questions")
    
    return {
        "assessment_id": assessment.assessment_id,
        "topic": assessment.topic,
        "difficulty": assessment.difficulty.value,
        "questions": assessment.questions,
        "metadata": assessment.metadata,
        "created_at": assessment.created_at.isoformat()
    }

@ai_assessment_agent.tool
async def validate_content_quality(
    ctx: RunContext[AIAssessmentDeps],
    content: str
) -> Dict[str, Any]:
    """Validate the quality of educational content."""
    
    # Analyze content quality
    clarity_score = await _analyze_clarity(content)
    accuracy_score = await _analyze_accuracy(content)
    engagement_score = await _analyze_engagement(content)
    educational_value = await _analyze_educational_value(content)
    
    # Calculate overall score
    overall_score = (clarity_score * 0.25 + 
                    accuracy_score * 0.30 + 
                    engagement_score * 0.15 + 
                    educational_value * 0.30)
    
    # Create quality score object
    quality_score = QualityScore(
        overall_score=overall_score,
        clarity_score=clarity_score,
        accuracy_score=accuracy_score,
        engagement_score=engagement_score,
        educational_value=educational_value
    )
    
    logger.info(f"Content quality validated: {overall_score:.2f}/100")
    
    return {
        "overall_score": quality_score.overall_score,
        "clarity_score": quality_score.clarity_score,
        "accuracy_score": quality_score.accuracy_score,
        "engagement_score": quality_score.engagement_score,
        "educational_value": quality_score.educational_value,
        "quality_level": _get_quality_level(overall_score),
        "recommendations": await _generate_quality_recommendations(quality_score)
    }

@ai_assessment_agent.tool
async def regenerate_question(
    ctx: RunContext[AIAssessmentDeps],
    original_question: str,
    reason: str
) -> Dict[str, Any]:
    """Regenerate a question based on feedback."""
    
    # Analyze the original question
    original_analysis = await _analyze_question_quality(original_question)
    
    # Generate improved question
    improved_question = await _generate_improved_question(ctx, original_question, reason)
    
    # Analyze the improved question
    improved_analysis = await _analyze_question_quality(improved_question["question_text"])
    
    logger.info(f"Regenerated question: {reason}")
    
    return {
        "original_question": original_question,
        "improved_question": improved_question,
        "improvement_metrics": {
            "original_quality": original_analysis["quality_score"],
            "improved_quality": improved_analysis["quality_score"],
            "improvement": improved_analysis["quality_score"] - original_analysis["quality_score"]
        },
        "regeneration_reason": reason,
        "created_at": datetime.now().isoformat()
    }

# Helper functions
async def _generate_question(
    ctx: RunContext[AIAssessmentDeps],
    topic: str,
    difficulty: DifficultyLevel,
    question_type: str,
    question_number: int
) -> Dict[str, Any]:
    """Generate a single question based on type and difficulty."""
    
    if question_type == "multiple_choice":
        return {
            "id": f"q_{question_number}",
            "type": "multiple_choice",
            "question_text": f"Question {question_number}: What is the correct answer about {topic}?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": "This is the correct answer because...",
            "difficulty": difficulty.value,
            "cognitive_level": "understand"
        }
    elif question_type == "fill_blank":
        return {
            "id": f"q_{question_number}",
            "type": "fill_blank",
            "question_text": f"Question {question_number}: Complete the sentence about {topic}: _____ is the answer.",
            "correct_answer": "This",
            "explanation": "The correct word is 'This' because...",
            "difficulty": difficulty.value,
            "cognitive_level": "apply"
        }
    elif question_type == "essay":
        return {
            "id": f"q_{question_number}",
            "type": "essay",
            "question_text": f"Question {question_number}: Explain in detail about {topic}.",
            "correct_answer": "Essay response should include...",
            "explanation": "A good essay should cover...",
            "difficulty": difficulty.value,
            "cognitive_level": "analyze"
        }
    else:  # true_false
        return {
            "id": f"q_{question_number}",
            "type": "true_false",
            "question_text": f"Question {question_number}: This statement about {topic} is true or false?",
            "correct_answer": "True",
            "explanation": "This is true because...",
            "difficulty": difficulty.value,
            "cognitive_level": "remember"
        }

async def _calculate_difficulty_distribution(questions: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate the distribution of difficulty levels in questions."""
    total = len(questions)
    distribution = {"beginner": 0, "intermediate": 0, "advanced": 0}
    
    for question in questions:
        difficulty = question.get("difficulty", "intermediate")
        distribution[difficulty] += 1
    
    return {k: v/total for k, v in distribution.items()}

async def _analyze_cognitive_levels(questions: List[Dict[str, Any]]) -> Dict[str, int]:
    """Analyze the distribution of cognitive levels in questions."""
    levels = {}
    for question in questions:
        level = question.get("cognitive_level", "remember")
        levels[level] = levels.get(level, 0) + 1
    return levels

async def _analyze_clarity(content: str) -> float:
    """Analyze the clarity of content."""
    # Simulate clarity analysis
    word_count = len(content.split())
    sentence_count = content.count('.') + content.count('!') + content.count('?')
    
    if sentence_count == 0:
        return 0.5
    
    avg_sentence_length = word_count / sentence_count
    
    if avg_sentence_length < 20:
        return 0.9
    elif avg_sentence_length < 30:
        return 0.7
    else:
        return 0.5

async def _analyze_accuracy(content: str) -> float:
    """Analyze the accuracy of content."""
    # Simulate accuracy analysis
    accuracy_indicators = ["correct", "accurate", "proper", "right", "valid"]
    inaccuracy_indicators = ["wrong", "incorrect", "false", "invalid", "error"]
    
    content_lower = content.lower()
    accuracy_score = 0.8  # Base score
    
    for indicator in accuracy_indicators:
        if indicator in content_lower:
            accuracy_score += 0.05
    
    for indicator in inaccuracy_indicators:
        if indicator in content_lower:
            accuracy_score -= 0.1
    
    return max(0.0, min(1.0, accuracy_score))

async def _analyze_engagement(content: str) -> float:
    """Analyze the engagement level of content."""
    # Simulate engagement analysis
    engagement_indicators = ["interesting", "exciting", "amazing", "fascinating", "engaging"]
    content_lower = content.lower()
    
    engagement_score = 0.6  # Base score
    
    for indicator in engagement_indicators:
        if indicator in content_lower:
            engagement_score += 0.1
    
    return max(0.0, min(1.0, engagement_score))

async def _analyze_educational_value(content: str) -> float:
    """Analyze the educational value of content."""
    # Simulate educational value analysis
    educational_indicators = ["learn", "understand", "explain", "demonstrate", "example"]
    content_lower = content.lower()
    
    educational_score = 0.7  # Base score
    
    for indicator in educational_indicators:
        if indicator in content_lower:
            educational_score += 0.05
    
    return max(0.0, min(1.0, educational_score))

def _get_quality_level(score: float) -> str:
    """Get quality level based on score."""
    if score >= 0.9:
        return "excellent"
    elif score >= 0.8:
        return "good"
    elif score >= 0.7:
        return "fair"
    else:
        return "needs_improvement"

async def _generate_quality_recommendations(quality_score: QualityScore) -> List[str]:
    """Generate recommendations for improving content quality."""
    recommendations = []
    
    if quality_score.clarity_score < 0.8:
        recommendations.append("Improve clarity by using shorter sentences and simpler language")
    
    if quality_score.accuracy_score < 0.9:
        recommendations.append("Verify factual accuracy and update outdated information")
    
    if quality_score.engagement_score < 0.7:
        recommendations.append("Add more engaging examples and interactive elements")
    
    if quality_score.educational_value < 0.8:
        recommendations.append("Include more educational examples and explanations")
    
    return recommendations

async def _analyze_question_quality(question: str) -> Dict[str, Any]:
    """Analyze the quality of a question."""
    clarity = await _analyze_clarity(question)
    accuracy = await _analyze_accuracy(question)
    engagement = await _analyze_engagement(question)
    educational_value = await _analyze_educational_value(question)
    
    quality_score = (clarity * 0.3 + accuracy * 0.4 + engagement * 0.1 + educational_value * 0.2)
    
    return {
        "quality_score": quality_score,
        "clarity": clarity,
        "accuracy": accuracy,
        "engagement": engagement,
        "educational_value": educational_value
    }

async def _generate_improved_question(
    ctx: RunContext[AIAssessmentDeps],
    original_question: str,
    reason: str
) -> Dict[str, Any]:
    """Generate an improved version of a question."""
    
    # Simulate question improvement
    if "too_easy" in reason.lower():
        improved_text = f"Advanced: {original_question} (Consider multiple perspectives)"
    elif "too_hard" in reason.lower():
        improved_text = f"Simplified: {original_question} (Focus on basic concepts)"
    elif "unclear" in reason.lower():
        improved_text = f"Clarified: {original_question} (More specific and clear)"
    else:
        improved_text = f"Improved: {original_question} (Enhanced version)"
    
    return {
        "question_text": improved_text,
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": "Option A",
        "explanation": "This is the improved version because..."
    }


class AIAssessmentService:
    """AI Assessment Service for creating and validating assessments."""
    
    def __init__(self):
        """Initialize the AI Assessment Service."""
        self.openai_client = None
        self.anthropic_client = None
        self.assessment_generator = None
        self.quality_analyzer = None
        
        # Initialize dependencies
        self._initialize_dependencies()
    
    def _initialize_dependencies(self):
        """Initialize AI model dependencies."""
        try:
            # Initialize OpenAI client
            if os.getenv("OPENAI_API_KEY"):
                self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Initialize Anthropic client
            if os.getenv("ANTHROPIC_API_KEY"):
                self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            
            logger.info("AI Assessment Service dependencies initialized successfully")
        except Exception as e:
            logger.warning(f"Some dependencies could not be initialized: {e}")
    
    async def create_assessment(
        self,
        topic: str,
        difficulty: str,
        question_types: List[str],
        question_count: int
    ) -> Dict[str, Any]:
        """Create a comprehensive assessment."""
        deps = AIAssessmentDeps(
            openai_client=self.openai_client,
            anthropic_client=self.anthropic_client,
            assessment_generator=self.assessment_generator,
            quality_analyzer=self.quality_analyzer
        )
        
        async with ai_assessment_agent.run(deps) as ctx:
            result = await create_assessment(
                ctx,
                topic=topic,
                difficulty=difficulty,
                question_types=question_types,
                question_count=question_count
            )
        
        return result
    
    async def validate_content_quality(self, content: str) -> Dict[str, Any]:
        """Validate the quality of educational content."""
        deps = AIAssessmentDeps(
            openai_client=self.openai_client,
            anthropic_client=self.anthropic_client,
            assessment_generator=self.assessment_generator,
            quality_analyzer=self.quality_analyzer
        )
        
        async with ai_assessment_agent.run(deps) as ctx:
            result = await validate_content_quality(ctx, content=content)
        
        return result
    
    async def regenerate_question(
        self,
        original_question: str,
        reason: str
    ) -> Dict[str, Any]:
        """Regenerate a question based on feedback."""
        deps = AIAssessmentDeps(
            openai_client=self.openai_client,
            anthropic_client=self.anthropic_client,
            assessment_generator=self.assessment_generator,
            quality_analyzer=self.quality_analyzer
        )
        
        async with ai_assessment_agent.run(deps) as ctx:
            result = await regenerate_question(
                ctx,
                original_question=original_question,
                reason=reason
            )
        
        return result

# Test function
async def test_ai_assessment_service():
    """Test the AI Assessment Service functionality."""
    service = AIAssessmentService()
    
    # Test assessment creation
    assessment = await service.create_assessment(
        topic="Grammar Fundamentals",
        difficulty="intermediate",
        question_types=["multiple_choice", "fill_blank", "essay"],
        question_count=10
    )
    print(f"Created assessment with {len(assessment['questions'])} questions")
    
    # Test content quality validation
    quality = await service.validate_content_quality("This is a test lesson about grammar.")
    print(f"Content quality score: {quality['overall_score']:.2f}")
    
    # Test question regeneration
    new_question = await service.regenerate_question(
        original_question="What is the past tense of 'go'?",
        reason="too_easy"
    )
    print(f"Regenerated question: {new_question['improved_question']['question_text']}")

if __name__ == "__main__":
    asyncio.run(test_ai_assessment_service()) 

def _get_quality_level(score: float) -> str:
    """Get quality level based on score."""
    if score >= 0.9:
        return "excellent"
    elif score >= 0.8:
        return "good"
    elif score >= 0.7:
        return "fair"
    else:
        return "needs_improvement"

async def _generate_quality_recommendations(quality_score: QualityScore) -> List[str]:
    """Generate recommendations for improving content quality."""
    recommendations = []
    
    if quality_score.clarity_score < 0.8:
        recommendations.append("Improve clarity by using shorter sentences and simpler language")
    
    if quality_score.accuracy_score < 0.9:
        recommendations.append("Verify factual accuracy and update outdated information")
    
    if quality_score.engagement_score < 0.7:
        recommendations.append("Add more engaging examples and interactive elements")
    
    if quality_score.educational_value < 0.8:
        recommendations.append("Include more educational examples and explanations")
    
    return recommendations

async def _analyze_question_quality(question: str) -> Dict[str, Any]:
    """Analyze the quality of a question."""
    clarity = await _analyze_clarity(question)
    accuracy = await _analyze_accuracy(question)
    engagement = await _analyze_engagement(question)
    educational_value = await _analyze_educational_value(question)
    
    quality_score = (clarity * 0.3 + accuracy * 0.4 + engagement * 0.1 + educational_value * 0.2)
    
    return {
        "quality_score": quality_score,
        "clarity": clarity,
        "accuracy": accuracy,
        "engagement": engagement,
        "educational_value": educational_value
    }

async def _generate_improved_question(
    ctx: RunContext[AIAssessmentDeps],
    original_question: str,
    reason: str
) -> Dict[str, Any]:
    """Generate an improved version of a question."""
    
    # Simulate question improvement
    if "too_easy" in reason.lower():
        improved_text = f"Advanced: {original_question} (Consider multiple perspectives)"
    elif "too_hard" in reason.lower():
        improved_text = f"Simplified: {original_question} (Focus on basic concepts)"
    elif "unclear" in reason.lower():
        improved_text = f"Clarified: {original_question} (More specific and clear)"
    else:
        improved_text = f"Improved: {original_question} (Enhanced version)"
    
    return {
        "question_text": improved_text,
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": "Option A",
        "explanation": "This is the improved version because..."
    }

