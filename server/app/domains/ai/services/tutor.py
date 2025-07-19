"""
Ai Domain - Tutor
Consolidated from: ai_tutor_service.py
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from pydantic_ai.tools import Tool
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
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
        if tool_name == "tutor_response":
            return type("Result", (), {"data": {"response": "Mock tutor response"}})()
        else:
            return type("Result", (), {"data": {}})()


class MockRunContext(Generic[T]):
    def __init__(self, deps=None):
        self.deps = deps
    
    def __getitem__(self, key):
        # Support subscripting like RunContext[AIContentDeps]
        return self.__class

# Use mock classes instead of pydantic_ai imports
Agent = MockAgent
RunContext = MockRunContext
from pydantic_ai.tools import Tool
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import openai
import anthropic
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LearningStyle(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    MIXED = "mixed"


class ProficiencyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class SentimentType(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ComprehensionLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LearningProfile(BaseModel):
    user_id: int
    learning_style: LearningStyle
    proficiency_level: ProficiencyLevel
    preferences: Dict[str, Any] = {}
    learning_patterns: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class StudentResponse(BaseModel):
    response_id: str
    user_id: int
    response_text: str
    context: str
    timestamp: datetime
    lesson_id: Optional[int] = None


class ResponseAnalysis(BaseModel):
    response_id: str
    sentiment: SentimentType
    sentiment_score: float
    comprehension_level: ComprehensionLevel
    confidence_score: float
    learning_gaps: List[str] = []
    suggested_feedback: str
    next_steps: List[str] = []
    analysis_metadata: Dict[str, Any] = {}


class PersonalizedFeedback(BaseModel):
    feedback_id: str
    user_id: int
    response_id: str
    message: str
    suggestions: List[str]
    next_steps: List[str]
    personalized: bool
    context: str
    created_at: datetime


class PerformanceData(BaseModel):
    correct_answers: int
    total_questions: int
    time_spent: int  # seconds
    confidence_level: float
    engagement_score: float
    error_patterns: List[str] = []


class AITutorDeps(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    openai_client: Any
    anthropic_client: Any
    sentiment_analyzer: Any
    comprehension_analyzer: Any
    feedback_generator: Any

# AI Tutor System Prompt
AI_TUTOR_PROMPT = """
You are an advanced AI language tutor specializing in personalized language learning. You excel at:

1. **Student Response Analysis**: Analyze student responses for comprehension, sentiment, and learning gaps
2. **Personalized Feedback Generation**: Provide tailored feedback based on individual learning styles and needs
3. **Adaptive Difficulty Adjustment**: Dynamically adjust content difficulty based on student performance
4. **Learning Pattern Recognition**: Identify and adapt to individual learning patterns
5. **Progress Tracking**: Monitor and analyze student progress over time

Core Capabilities:
- Real-time sentiment analysis and emotion detection
- Comprehension level assessment using advanced NLP
- Personalized feedback generation with cultural context
- Adaptive difficulty adjustment using performance analytics
- Learning pattern recognition and optimization
- Multi-language support with cultural sensitivity
- Progress tracking and predictive analytics

Tutoring Principles:
- Encourage and motivate students through positive reinforcement
- Provide specific, actionable feedback that addresses learning gaps
- Adapt teaching style to individual learning preferences
- Use real-world examples and cultural context
- Maintain appropriate challenge levels to prevent boredom or frustration
- Track progress and celebrate achievements
- Provide clear next steps for continued learning

Response Analysis Framework:
- Sentiment Analysis: Assess emotional state and engagement
- Comprehension Assessment: Evaluate understanding level
- Confidence Scoring: Measure student certainty in responses
- Learning Gap Identification: Identify areas needing improvement
- Cultural Context Integration: Consider cultural background and context
- Progress Tracking: Monitor improvement over time
"""

# Create the AI Tutor agent
ai_tutor_agent = Agent(
    'openai:gpt-4o',
    system_prompt=AI_TUTOR_PROMPT,
    deps_type=AITutorDeps
)

@ai_tutor_agent.tool
async def create_learning_profile(
    ctx: RunContext[AITutorDeps],
    user_id: int,
    learning_style: str,
    proficiency_level: str,
    preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a personalized learning profile for a student."""
    
    # Validate inputs
    try:
        learning_style_enum = LearningStyle(learning_style.lower())
        proficiency_enum = ProficiencyLevel(proficiency_level.lower())
    except ValueError as e:
        raise ValueError(f"Invalid learning style or proficiency level: {e}")
    
    # Create learning profile
    profile = LearningProfile(
        user_id=user_id,
        learning_style=learning_style_enum,
        proficiency_level=proficiency_enum,
        preferences=preferences or {},
        learning_patterns={},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Initialize learning patterns
    profile.learning_patterns = {
        "preferred_session_length": 30,  # minutes
        "optimal_study_times": ["morning", "evening"],
        "engagement_patterns": {},
        "strength_areas": [],
        "weakness_areas": [],
        "learning_pace": "moderate"
    }
    
    logger.info(f"Created learning profile for user {user_id}")
    
    return {
        "profile_id": f"profile_{user_id}_{datetime.now().timestamp()}",
        "user_id": profile.user_id,
        "learning_style": profile.learning_style.value,
        "proficiency_level": profile.proficiency_level.value,
        "preferences": profile.preferences,
        "learning_patterns": profile.learning_patterns,
        "created_at": profile.created_at.isoformat(),
        "status": "active"
    }

@ai_tutor_agent.tool
async def analyze_student_response(
    ctx: RunContext[AITutorDeps],
    response_text: str,
    context: str,
    user_id: int
) -> Dict[str, Any]:
    """Analyze a student's response for sentiment, comprehension, and learning insights."""
    
    # Perform sentiment analysis
    sentiment_result = await _analyze_sentiment(ctx, response_text)
    
    # Analyze comprehension level
    comprehension_result = await _analyze_comprehension(ctx, response_text, context)
    
    # Calculate confidence score
    confidence_score = await _calculate_confidence_score(ctx, response_text, context)
    
    # Identify learning gaps
    learning_gaps = await _identify_learning_gaps(ctx, response_text, context)
    
    # Generate suggested feedback
    suggested_feedback = await _generate_suggested_feedback(
        ctx, response_text, sentiment_result, comprehension_result, learning_gaps
    )
    
    # Create response analysis
    analysis = ResponseAnalysis(
        response_id=f"response_{user_id}_{datetime.now().timestamp()}",
        sentiment=SentimentType(sentiment_result["sentiment"]),
        sentiment_score=sentiment_result["score"],
        comprehension_level=ComprehensionLevel(comprehension_result["level"]),
        confidence_score=confidence_score,
        learning_gaps=learning_gaps,
        suggested_feedback=suggested_feedback,
        next_steps=comprehension_result.get("next_steps", []),
        analysis_metadata={
            "context": context,
            "response_length": len(response_text),
            "analysis_timestamp": datetime.now().isoformat()
        }
    )
    
    logger.info(f"Analyzed response for user {user_id}: {analysis.comprehension_level.value} comprehension")
    
    return {
        "response_id": analysis.response_id,
        "sentiment": analysis.sentiment.value,
        "sentiment_score": analysis.sentiment_score,
        "comprehension_level": analysis.comprehension_level.value,
        "confidence_score": analysis.confidence_score,
        "learning_gaps": analysis.learning_gaps,
        "suggested_feedback": analysis.suggested_feedback,
        "next_steps": analysis.next_steps,
        "analysis_metadata": analysis.analysis_metadata
    }

@ai_tutor_agent.tool
async def generate_personalized_feedback(
    ctx: RunContext[AITutorDeps],
    user_id: int,
    response_text: str,
    context: str,
    learning_profile: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate personalized feedback based on student response and learning profile."""
    
    # Analyze the response first
    analysis = await analyze_student_response(ctx, response_text, context, user_id)
    
    # Get learning profile if not provided
    if not learning_profile:
        learning_profile = {
            "learning_style": "mixed",
            "proficiency_level": "intermediate",
            "preferences": {}
        }
    
    # Generate personalized feedback message
    feedback_message = await _create_personalized_message(
        ctx, analysis, learning_profile, context
    )
    
    # Generate specific suggestions
    suggestions = await _generate_suggestions(ctx, analysis, learning_profile)
    
    # Determine next steps
    next_steps = await _determine_next_steps(ctx, analysis, learning_profile, context)
    
    # Create feedback object
    feedback = PersonalizedFeedback(
        feedback_id=f"feedback_{user_id}_{datetime.now().timestamp()}",
        user_id=user_id,
        response_id=analysis["response_id"],
        message=feedback_message,
        suggestions=suggestions,
        next_steps=next_steps,
        personalized=True,
        context=context,
        created_at=datetime.now()
    )
    
    logger.info(f"Generated personalized feedback for user {user_id}")
    
    return {
        "feedback_id": feedback.feedback_id,
        "message": feedback.message,
        "suggestions": feedback.suggestions,
        "next_steps": feedback.next_steps,
        "personalized": feedback.personalized,
        "context": feedback.context,
        "created_at": feedback.created_at.isoformat()
    }

@ai_tutor_agent.tool
async def adapt_difficulty(
    ctx: RunContext[AITutorDeps],
    user_id: int,
    current_difficulty: str,
    performance_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Adapt content difficulty based on student performance."""
    
    # Validate current difficulty
    try:
        current_level = ProficiencyLevel(current_difficulty.lower())
    except ValueError:
        raise ValueError(f"Invalid difficulty level: {current_difficulty}")
    
    # Analyze performance data
    performance = PerformanceData(**performance_data)
    
    # Calculate performance metrics
    accuracy_rate = performance.correct_answers / performance.total_questions
    time_efficiency = performance.time_spent / performance.total_questions
    overall_score = (accuracy_rate * 0.6) + (performance.confidence_level * 0.3) + (performance.engagement_score * 0.1)
    
    # Determine new difficulty level
    new_difficulty = await _calculate_new_difficulty(
        current_level, overall_score, accuracy_rate, time_efficiency
    )
    
    # Generate adaptation reasoning
    adaptation_reason = await _generate_adaptation_reason(
        current_level, new_difficulty, performance_data
    )
    
    logger.info(f"Adapted difficulty for user {user_id}: {current_level.value} -> {new_difficulty.value}")
    
    return {
        "user_id": user_id,
        "previous_difficulty": current_level.value,
        "new_difficulty": new_difficulty.value,
        "adaptation_reason": adaptation_reason,
        "performance_metrics": {
            "accuracy_rate": accuracy_rate,
            "time_efficiency": time_efficiency,
            "overall_score": overall_score,
            "confidence_level": performance.confidence_level,
            "engagement_score": performance.engagement_score
        },
        "adaptation_timestamp": datetime.now().isoformat()
    }

# Helper functions
async def _analyze_sentiment(ctx: RunContext[AITutorDeps], text: str) -> Dict[str, Any]:
    """Analyze sentiment of student response."""
    # Simulate sentiment analysis
    sentiment_words = {
        "positive": ["good", "great", "excellent", "love", "enjoy", "understand", "clear"],
        "negative": ["bad", "difficult", "confused", "hate", "hard", "unclear", "wrong"]
    }
    
    text_lower = text.lower()
    positive_count = sum(1 for word in sentiment_words["positive"] if word in text_lower)
    negative_count = sum(1 for word in sentiment_words["negative"] if word in text_lower)
    
    if positive_count > negative_count:
        sentiment = "positive"
        score = min(0.9, 0.5 + (positive_count * 0.1))
    elif negative_count > positive_count:
        sentiment = "negative"
        score = min(0.9, 0.5 + (negative_count * 0.1))
    else:
        sentiment = "neutral"
        score = 0.5
    
    return {"sentiment": sentiment, "score": score}

async def _analyze_comprehension(ctx: RunContext[AITutorDeps], text: str, context: str) -> Dict[str, Any]:
    """Analyze comprehension level of student response."""
    # Simulate comprehension analysis
    text_length = len(text)
    word_count = len(text.split())
    
    # Simple heuristics for comprehension level
    if word_count > 20 and text_length > 100:
        level = "high"
        next_steps = ["Practice advanced concepts", "Try more complex exercises"]
    elif word_count > 10 and text_length > 50:
        level = "medium"
        next_steps = ["Review key concepts", "Practice with examples"]
    else:
        level = "low"
        next_steps = ["Review basic concepts", "Ask for clarification"]
    
    return {"level": level, "next_steps": next_steps}

async def _calculate_confidence_score(ctx: RunContext[AITutorDeps], text: str, context: str) -> float:
    """Calculate confidence score based on response characteristics."""
    # Simulate confidence calculation
    word_count = len(text.split())
    has_qualifiers = any(word in text.lower() for word in ["maybe", "perhaps", "I think", "not sure"])
    has_definitive = any(word in text.lower() for word in ["definitely", "certainly", "absolutely"])
    
    base_score = min(0.9, word_count * 0.02)
    
    if has_definitive:
        base_score += 0.1
    if has_qualifiers:
        base_score -= 0.1
    
    return max(0.1, min(0.9, base_score))

async def _identify_learning_gaps(ctx: RunContext[AITutorDeps], text: str, context: str) -> List[str]:
    """Identify learning gaps in student response."""
    # Simulate learning gap identification
    gaps = []
    
    if len(text) < 20:
        gaps.append("Need more detailed explanations")
    
    if "don't know" in text.lower() or "confused" in text.lower():
        gaps.append("Concept understanding needs improvement")
    
    if "grammar" in context.lower() and any(word in text.lower() for word in ["wrong", "error", "mistake"]):
        gaps.append("Grammar rules need review")
    
    return gaps

async def _generate_suggested_feedback(
    ctx: RunContext[AITutorDeps],
    text: str,
    sentiment: Dict[str, Any],
    comprehension: Dict[str, Any],
    gaps: List[str]
) -> str:
    """Generate suggested feedback based on analysis."""
    if sentiment["sentiment"] == "negative":
        return "I understand this concept can be challenging. Let me help you break it down step by step."
    elif comprehension["level"] == "low":
        return "Let's review the basics first. Can you tell me what you understand about this topic?"
    elif gaps:
        return f"I see you're working on this. Let's focus on: {', '.join(gaps)}"
    else:
        return "Great work! You're making good progress. Let's try something a bit more challenging."

async def _create_personalized_message(
    ctx: RunContext[AITutorDeps],
    analysis: Dict[str, Any],
    profile: Dict[str, Any],
    context: str
) -> str:
    """Create personalized feedback message."""
    style = profile.get("learning_style", "mixed")
    
    if style == "visual":
        return f"Great work! I can see you're understanding the concept. Let me show you a visual example to reinforce this."
    elif style == "auditory":
        return f"Excellent! You're getting the hang of this. Let's practice saying it out loud to really cement it in your mind."
    else:
        return f"Good progress! You're on the right track. Let's practice this a bit more to make sure it sticks."

async def _generate_suggestions(ctx: RunContext[AITutorDeps], analysis: Dict[str, Any], profile: Dict[str, Any]) -> List[str]:
    """Generate specific suggestions for improvement."""
    suggestions = []
    
    if analysis["comprehension_level"] == "low":
        suggestions.append("Review the basic concepts before moving forward")
        suggestions.append("Ask questions when something isn't clear")
    
    if analysis["confidence_score"] < 0.6:
        suggestions.append("Practice with simpler examples first")
        suggestions.append("Take your time to think through each step")
    
    return suggestions

async def _determine_next_steps(
    ctx: RunContext[AITutorDeps],
    analysis: Dict[str, Any],
    profile: Dict[str, Any],
    context: str
) -> List[str]:
    """Determine next steps for learning."""
    next_steps = []
    
    if analysis["comprehension_level"] == "high":
        next_steps.append("Try more advanced exercises")
        next_steps.append("Practice with real-world examples")
    else:
        next_steps.append("Review the current lesson")
        next_steps.append("Practice with similar examples")
    
    return next_steps

async def _calculate_new_difficulty(
    current: ProficiencyLevel,
    overall_score: float,
    accuracy_rate: float,
    time_efficiency: float
) -> ProficiencyLevel:
    """Calculate new difficulty level based on performance."""
    if overall_score > 0.8 and accuracy_rate > 0.8:
        # Student is performing well, increase difficulty
        if current == ProficiencyLevel.BEGINNER:
            return ProficiencyLevel.INTERMEDIATE
        elif current == ProficiencyLevel.INTERMEDIATE:
            return ProficiencyLevel.ADVANCED
        else:
            return current
    elif overall_score < 0.4 or accuracy_rate < 0.4:
        # Student is struggling, decrease difficulty
        if current == ProficiencyLevel.ADVANCED:
            return ProficiencyLevel.INTERMEDIATE
        elif current == ProficiencyLevel.INTERMEDIATE:
            return ProficiencyLevel.BEGINNER
        else:
            return current
    else:
        # Keep current difficulty
        return current

async def _generate_adaptation_reason(
    current: ProficiencyLevel,
    new: ProficiencyLevel,
    performance: Dict[str, Any]
) -> str:
    """Generate reasoning for difficulty adaptation."""
    if new.value == current.value:
        return "Maintaining current difficulty level based on performance"
    elif new.value == "advanced" and current.value == "intermediate":
        return "Increasing difficulty due to strong performance and high accuracy"
    elif new.value == "intermediate" and current.value == "beginner":
        return "Progressing to intermediate level based on consistent performance"
    elif new.value == "intermediate" and current.value == "advanced":
        return "Adjusting to intermediate level to build stronger foundation"
    elif new.value == "beginner" and current.value == "intermediate":
        return "Returning to beginner level to strengthen basic concepts"
    else:
        return "Adapting difficulty based on performance analysis"


class AITutorService:
    """AI Tutor Service for personalized language learning."""
    
    def __init__(self):
        """Initialize the AI Tutor Service."""
        self.openai_client = None
        self.anthropic_client = None
        self.sentiment_analyzer = None
        self.comprehension_analyzer = None
        self.feedback_generator = None
        
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
            
            # Initialize sentiment analyzer
            self.sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
            
            logger.info("AI Tutor Service dependencies initialized successfully")
        except Exception as e:
            logger.warning(f"Some dependencies could not be initialized: {e}")
    
    async def create_learning_profile(self, user) -> Dict[str, Any]:
        """Create a learning profile for a user."""
        deps = AITutorDeps(
            openai_client=self.openai_client,
            anthropic_client=self.anthropic_client,
            sentiment_analyzer=self.sentiment_analyzer,
            comprehension_analyzer=self.comprehension_analyzer,
            feedback_generator=self.feedback_generator
        )
        
        async with ai_tutor_agent.run(deps) as ctx:
            result = await create_learning_profile(
                ctx,
                user_id=user.id,
                learning_style=getattr(user, 'learning_style', 'mixed'),
                proficiency_level=getattr(user, 'proficiency_level', 'intermediate'),
                preferences={}
            )
        
        return result
    
    async def analyze_student_response(self, response: str) -> Dict[str, Any]:
        """Analyze a student's response."""
        deps = AITutorDeps(
            openai_client=self.openai_client,
            anthropic_client=self.anthropic_client,
            sentiment_analyzer=self.sentiment_analyzer,
            comprehension_analyzer=self.comprehension_analyzer,
            feedback_generator=self.feedback_generator
        )
        
        async with ai_tutor_agent.run(deps) as ctx:
            result = await analyze_student_response(
                ctx,
                response_text=response,
                context="general",
                user_id=1  # Default user ID for testing
            )
        
        return result
    
    async def generate_personalized_feedback(
        self,
        user,
        response: str,
        context: str
    ) -> Dict[str, Any]:
        """Generate personalized feedback for a user."""
        deps = AITutorDeps(
            openai_client=self.openai_client,
            anthropic_client=self.anthropic_client,
            sentiment_analyzer=self.sentiment_analyzer,
            comprehension_analyzer=self.comprehension_analyzer,
            feedback_generator=self.feedback_generator
        )
        
        async with ai_tutor_agent.run(deps) as ctx:
            result = await generate_personalized_feedback(
                ctx,
                user_id=user.id,
                response_text=response,
                context=context
            )
        
        return result
    
    async def adapt_difficulty(
        self,
        user,
        current_difficulty: str,
        performance_data: Dict[str, Any]
    ) -> str:
        """Adapt difficulty based on user performance."""
        deps = AITutorDeps(
            openai_client=self.openai_client,
            anthropic_client=self.anthropic_client,
            sentiment_analyzer=self.sentiment_analyzer,
            comprehension_analyzer=self.comprehension_analyzer,
            feedback_generator=self.feedback_generator
        )
        
        async with ai_tutor_agent.run(deps) as ctx:
            result = await adapt_difficulty(
                ctx,
                user_id=user.id,
                current_difficulty=current_difficulty,
                performance_data=performance_data
            )
        
        return result["new_difficulty"]

# Test function
async def test_ai_tutor_service():
    """Test the AI Tutor Service functionality."""
    service = AITutorService()
    
    # Test learning profile creation
    mock_user = type('User', (), {'id': 1, 'learning_style': 'visual', 'proficiency_level': 'intermediate'})()
    profile = await service.create_learning_profile(mock_user)
    print(f"Created learning profile: {profile}")
    
    # Test response analysis
    analysis = await service.analyze_student_response("I understand the concept of past tense now.")
    print(f"Response analysis: {analysis}")
    
    # Test personalized feedback
    feedback = await service.generate_personalized_feedback(mock_user, "I think past tense is for future events.", "past_tense_lesson")
    print(f"Personalized feedback: {feedback}")
    
    # Test difficulty adaptation
    performance_data = {
        "correct_answers": 3,
        "total_questions": 5,
        "time_spent": 120,
        "confidence_level": 0.7,
        "engagement_score": 0.8
    }
    new_difficulty = await service.adapt_difficulty(mock_user, "intermediate", performance_data)
    print(f"New difficulty: {new_difficulty}")

if __name__ == "__main__":
    asyncio.run(test_ai_tutor_service()) 
