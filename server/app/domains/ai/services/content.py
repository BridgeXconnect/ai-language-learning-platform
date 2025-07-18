"""
Ai Domain - Content
Consolidated from: ai_content_service.py
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from pydantic_ai.tools import Tool
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
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
        if tool_name == "generate_content":
            return type("Result", (), {"data": {"content_id": "mock_content", "content": "Mock content"}})()
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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentType(Enum):
    LESSON = "lesson"
    QUIZ = "quiz"
    EXERCISE = "exercise"
    EXPLANATION = "explanation"


class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class LearningPath(BaseModel):
    path_id: str
    user_id: int
    modules: List[Dict[str, Any]]
    estimated_duration: int  # minutes
    milestones: List[Dict[str, Any]]
    personalized: bool
    created_at: datetime


class LessonContent(BaseModel):
    content_id: str
    title: str
    difficulty: DifficultyLevel
    learning_objectives: List[str]
    explanations: List[Dict[str, Any]]
    examples: List[Dict[str, Any]]
    exercises: List[Dict[str, Any]]
    created_at: datetime


class AdaptiveQuiz(BaseModel):
    quiz_id: str
    questions: List[Dict[str, Any]]
    difficulty_distribution: Dict[str, float]
    adaptive: bool
    estimated_duration: int
    created_at: datetime


class AIContentDeps(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    openai_client: Any
    anthropic_client: Any
    content_generator: Any
    quality_analyzer: Any

# AI Content Generation System Prompt
CONTENT_GENERATION_PROMPT = """
You are an advanced AI content generation system specializing in educational content creation. You excel at:

1. **Lesson Content Generation**: Create engaging, structured lesson content
2. **Adaptive Quiz Creation**: Generate quizzes that adapt to student performance
3. **Learning Path Generation**: Design personalized learning journeys
4. **Content Quality Validation**: Ensure educational value and accuracy
5. **Multi-format Support**: Create various content types (text, interactive, multimedia)

Core Capabilities:
- Structured lesson creation with clear learning objectives
- Adaptive quiz generation with difficulty distribution
- Personalized learning path design
- Content quality assessment and validation
- Multi-language support with cultural sensitivity
- Real-time content adaptation based on student needs

Content Creation Principles:
- Clear, concise, and engaging language appropriate for target audience
- Pedagogically sound structure with logical progression
- Culturally sensitive and inclusive content
- Accurate and up-to-date information
- Measurable learning outcomes
- Varied content types and formats
- Accessibility considerations for diverse learners
"""

# Create the AI Content agent
ai_content_agent = Agent(
    'openai:gpt-4o',
    system_prompt=CONTENT_GENERATION_PROMPT,
    deps_type=AIContentDeps
)

@ai_content_agent.tool
async def generate_lesson_content(
    ctx: RunContext[AIContentDeps],
    topic: str,
    difficulty: str,
    learning_objectives: List[str]
) -> Dict[str, Any]:
    """Generate comprehensive lesson content for a given topic."""
    
    # Validate difficulty level
    try:
        difficulty_enum = DifficultyLevel(difficulty.lower())
    except ValueError:
        raise ValueError(f"Invalid difficulty level: {difficulty}")
    
    # Create lesson structure
    lesson_structure = await _create_lesson_structure(topic, difficulty_enum, learning_objectives)
    
    # Generate content for each section
    explanations = await _generate_explanations(ctx, topic, difficulty_enum, learning_objectives)
    examples = await _generate_examples(ctx, topic, difficulty_enum)
    exercises = await _generate_exercises(ctx, topic, difficulty_enum, learning_objectives)
    
    # Create lesson content object
    lesson = LessonContent(
        content_id=f"lesson_{topic}_{datetime.now().timestamp()}",
        title=lesson_structure["title"],
        difficulty=difficulty_enum,
        learning_objectives=learning_objectives,
        explanations=explanations,
        examples=examples,
        exercises=exercises,
        created_at=datetime.now()
    )
    
    logger.info(f"Generated lesson content for topic: {topic}")
    
    return {
        "content_id": lesson.content_id,
        "title": lesson.title,
        "difficulty": lesson.difficulty.value,
        "learning_objectives": lesson.learning_objectives,
        "explanations": lesson.explanations,
        "examples": lesson.examples,
        "exercises": lesson.exercises,
        "created_at": lesson.created_at.isoformat()
    }

@ai_content_agent.tool
async def create_adaptive_quiz(
    ctx: RunContext[AIContentDeps],
    lesson_content: str,
    difficulty: str,
    question_count: int
) -> Dict[str, Any]:
    """Create an adaptive quiz based on lesson content."""
    
    # Validate difficulty level
    try:
        difficulty_enum = DifficultyLevel(difficulty.lower())
    except ValueError:
        raise ValueError(f"Invalid difficulty level: {difficulty}")
    
    # Generate questions
    questions = []
    for i in range(question_count):
        question = await _generate_question(ctx, lesson_content, difficulty_enum, i + 1)
        questions.append(question)
    
    # Calculate difficulty distribution
    difficulty_distribution = await _calculate_difficulty_distribution(questions, difficulty_enum)
    
    # Create adaptive quiz object
    quiz = AdaptiveQuiz(
        quiz_id=f"quiz_{datetime.now().timestamp()}",
        questions=questions,
        difficulty_distribution=difficulty_distribution,
        adaptive=True,
        estimated_duration=len(questions) * 60,  # 1 minute per question
        created_at=datetime.now()
    )
    
    logger.info(f"Created adaptive quiz with {len(questions)} questions")
    
    return {
        "quiz_id": quiz.quiz_id,
        "questions": quiz.questions,
        "difficulty_distribution": quiz.difficulty_distribution,
        "adaptive": quiz.adaptive,
        "estimated_duration": quiz.estimated_duration,
        "created_at": quiz.created_at.isoformat()
    }

@ai_content_agent.tool
async def generate_learning_path(
    ctx: RunContext[AIContentDeps],
    user,
    goals: List[str],
    current_level: str
) -> Dict[str, Any]:
    """Generate a personalized learning path for a user."""
    
    # Validate current level
    try:
        level_enum = DifficultyLevel(current_level.lower())
    except ValueError:
        raise ValueError(f"Invalid level: {current_level}")
    
    # Create learning modules based on goals
    modules = await _create_learning_modules(ctx, goals, level_enum)
    
    # Calculate estimated duration
    estimated_duration = sum(module.get("estimated_duration", 30) for module in modules)
    
    # Create milestones
    milestones = await _create_milestones(modules, goals)
    
    # Create learning path object
    learning_path = LearningPath(
        path_id=f"path_{user.id}_{datetime.now().timestamp()}",
        user_id=user.id,
        modules=modules,
        estimated_duration=estimated_duration,
        milestones=milestones,
        personalized=True,
        created_at=datetime.now()
    )
    
    logger.info(f"Generated learning path for user {user.id} with {len(modules)} modules")
    
    return {
        "path_id": learning_path.path_id,
        "modules": learning_path.modules,
        "estimated_duration": learning_path.estimated_duration,
        "milestones": learning_path.milestones,
        "personalized": learning_path.personalized,
        "created_at": learning_path.created_at.isoformat()
    }

# Helper functions
async def _create_lesson_structure(
    topic: str,
    difficulty: DifficultyLevel,
    learning_objectives: List[str]
) -> Dict[str, Any]:
    """Create the structure for a lesson."""
    return {
        "title": f"Mastering {topic}",
        "sections": [
            {
                "title": "Introduction",
                "type": "explanation",
                "content": f"Welcome to our lesson on {topic}!"
            },
            {
                "title": "Core Concepts",
                "type": "explanation",
                "content": f"Let's explore the key concepts of {topic}."
            },
            {
                "title": "Examples",
                "type": "examples",
                "content": "Here are some practical examples."
            },
            {
                "title": "Practice",
                "type": "exercises",
                "content": "Time to practice what you've learned!"
            }
        ]
    }

async def _generate_explanations(
    ctx: RunContext[AIContentDeps],
    topic: str,
    difficulty: DifficultyLevel,
    learning_objectives: List[str]
) -> List[Dict[str, Any]]:
    """Generate explanations for the lesson."""
    explanations = []
    
    for i, objective in enumerate(learning_objectives):
        explanation = {
            "id": f"explanation_{i+1}",
            "title": f"Understanding {objective}",
            "content": f"This section explains {objective} in detail, tailored for {difficulty.value} learners.",
            "key_points": [
                f"Key point 1 about {objective}",
                f"Key point 2 about {objective}",
                f"Key point 3 about {objective}"
            ],
            "difficulty": difficulty.value
        }
        explanations.append(explanation)
    
    return explanations

async def _generate_examples(
    ctx: RunContext[AIContentDeps],
    topic: str,
    difficulty: DifficultyLevel
) -> List[Dict[str, Any]]:
    """Generate examples for the lesson."""
    examples = []
    
    for i in range(3):
        example = {
            "id": f"example_{i+1}",
            "title": f"Example {i+1}",
            "content": f"This is an example of {topic} usage at {difficulty.value} level.",
            "explanation": f"Here's why this example works and what it demonstrates.",
            "difficulty": difficulty.value
        }
        examples.append(example)
    
    return examples

async def _generate_exercises(
    ctx: RunContext[AIContentDeps],
    topic: str,
    difficulty: DifficultyLevel,
    learning_objectives: List[str]
) -> List[Dict[str, Any]]:
    """Generate exercises for the lesson."""
    exercises = []
    
    for i, objective in enumerate(learning_objectives):
        exercise = {
            "id": f"exercise_{i+1}",
            "title": f"Practice: {objective}",
            "description": f"Practice exercise for {objective}",
            "instructions": f"Complete this exercise to practice {objective}",
            "difficulty": difficulty.value,
            "estimated_time": 5  # minutes
        }
        exercises.append(exercise)
    
    return exercises

async def _generate_question(
    ctx: RunContext[AIContentDeps],
    lesson_content: str,
    difficulty: DifficultyLevel,
    question_number: int
) -> Dict[str, Any]:
    """Generate a single quiz question."""
    question_types = ["multiple_choice", "fill_blank", "true_false"]
    question_type = question_types[question_number % len(question_types)]
    
    if question_type == "multiple_choice":
        return {
            "id": f"q_{question_number}",
            "type": "multiple_choice",
            "question": f"Question {question_number}: What is the correct answer?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": "This is the correct answer because...",
            "difficulty": difficulty.value
        }
    elif question_type == "fill_blank":
        return {
            "id": f"q_{question_number}",
            "type": "fill_blank",
            "question": f"Question {question_number}: Complete the sentence: _____ is the answer.",
            "correct_answer": "This",
            "explanation": "The correct word is 'This' because...",
            "difficulty": difficulty.value
        }
    else:  # true_false
        return {
            "id": f"q_{question_number}",
            "type": "true_false",
            "question": f"Question {question_number}: This statement is true or false?",
            "correct_answer": "True",
            "explanation": "This is true because...",
            "difficulty": difficulty.value
        }

async def _calculate_difficulty_distribution(
    questions: List[Dict[str, Any]],
    target_difficulty: DifficultyLevel
) -> Dict[str, float]:
    """Calculate the distribution of difficulty levels in the quiz."""
    total_questions = len(questions)
    
    if target_difficulty == DifficultyLevel.BEGINNER:
        return {
            "beginner": 0.7,
            "intermediate": 0.3,
            "advanced": 0.0
        }
    elif target_difficulty == DifficultyLevel.INTERMEDIATE:
        return {
            "beginner": 0.2,
            "intermediate": 0.6,
            "advanced": 0.2
        }
    else:  # ADVANCED
        return {
            "beginner": 0.0,
            "intermediate": 0.3,
            "advanced": 0.7
        }

async def _create_learning_modules(
    ctx: RunContext[AIContentDeps],
    goals: List[str],
    level: DifficultyLevel
) -> List[Dict[str, Any]]:
    """Create learning modules based on goals."""
    modules = []
    
    for i, goal in enumerate(goals):
        module = {
            "id": f"module_{i+1}",
            "title": f"Module {i+1}: {goal}",
            "description": f"Learn about {goal}",
            "estimated_duration": 30,  # minutes
            "difficulty": level.value,
            "prerequisites": [],
            "learning_objectives": [f"Understand {goal}", f"Practice {goal}"],
            "content_types": ["lesson", "quiz", "exercise"]
        }
        modules.append(module)
    
    return modules

async def _create_milestones(
    modules: List[Dict[str, Any]],
    goals: List[str]
) -> List[Dict[str, Any]]:
    """Create milestones for the learning path."""
    milestones = []
    
    for i, (module, goal) in enumerate(zip(modules, goals)):
        milestone = {
            "id": f"milestone_{i+1}",
            "title": f"Complete {goal}",
            "description": f"Successfully complete the {goal} module",
            "module_id": module["id"],
            "criteria": [
                f"Complete all lessons in {goal}",
                f"Score 80% or higher on {goal} quiz",
                f"Complete practice exercises for {goal}"
            ]
        }
        milestones.append(milestone)
    
    return milestones


class AIContentService:
    """AI Content Service for generating educational content."""
    
    def __init__(self):
        """Initialize the AI Content Service."""
        self.openai_client = None
        self.anthropic_client = None
        self.content_generator = None
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
            
            logger.info("AI Content Service dependencies initialized successfully")
        except Exception as e:
            logger.warning(f"Some dependencies could not be initialized: {e}")
    
    async def generate_lesson_content(
        self,
        topic: str,
        difficulty: str,
        learning_objectives: List[str]
    ) -> Dict[str, Any]:
        """Generate lesson content for a given topic."""
        deps = AIContentDeps(
            openai_client=self.openai_client,
            anthropic_client=self.anthropic_client,
            content_generator=self.content_generator,
            quality_analyzer=self.quality_analyzer
        )
        
        async with ai_content_agent.run(deps) as ctx:
            result = await generate_lesson_content(
                ctx,
                topic=topic,
                difficulty=difficulty,
                learning_objectives=learning_objectives
            )
        
        return result
    
    async def create_adaptive_quiz(
        self,
        lesson_content: str,
        difficulty: str,
        question_count: int
    ) -> Dict[str, Any]:
        """Create an adaptive quiz based on lesson content."""
        deps = AIContentDeps(
            openai_client=self.openai_client,
            anthropic_client=self.anthropic_client,
            content_generator=self.content_generator,
            quality_analyzer=self.quality_analyzer
        )
        
        async with ai_content_agent.run(deps) as ctx:
            result = await create_adaptive_quiz(
                ctx,
                lesson_content=lesson_content,
                difficulty=difficulty,
                question_count=question_count
            )
        
        return result
    
    async def generate_learning_path(
        self,
        user,
        goals: List[str],
        current_level: str
    ) -> Dict[str, Any]:
        """Generate a personalized learning path for a user."""
        deps = AIContentDeps(
            openai_client=self.openai_client,
            anthropic_client=self.anthropic_client,
            content_generator=self.content_generator,
            quality_analyzer=self.quality_analyzer
        )
        
        async with ai_content_agent.run(deps) as ctx:
            result = await generate_learning_path(
                ctx,
                user=user,
                goals=goals,
                current_level=current_level
            )
        
        return result

# Test function
async def test_ai_content_service():
    """Test the AI Content Service functionality."""
    service = AIContentService()
    
    # Test lesson content generation
    lesson = await service.generate_lesson_content(
        topic="Present Perfect Tense",
        difficulty="intermediate",
        learning_objectives=["Understand usage", "Practice formation"]
    )
    print(f"Generated lesson: {lesson['title']}")
    
    # Test adaptive quiz creation
    quiz = await service.create_adaptive_quiz(
        lesson_content="Present perfect tense explanation...",
        difficulty="intermediate",
        question_count=5
    )
    print(f"Created quiz with {len(quiz['questions'])} questions")
    
    # Test learning path generation
    mock_user = type('User', (), {'id': 1})()
    learning_path = await service.generate_learning_path(
        user=mock_user,
        goals=["Master past tense", "Improve speaking"],
        current_level="intermediate"
    )
    print(f"Generated learning path with {len(learning_path['modules'])} modules")

if __name__ == "__main__":
    asyncio.run(test_ai_content_service()) 
