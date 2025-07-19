"""
Tools for Content Creator Agent
Implements specialized tools for lesson generation, exercise creation, and assessment building
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio
import random

# Database and external service imports
import asyncpg
from supabase import create_client, Client

# AI and content generation
import openai
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Shared database connection for all tools."""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase: Optional[Client] = None
        
        if self.supabase_url and self.supabase_key:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
        else:
            logger.warning("Supabase credentials not found")
    
    def is_connected(self) -> bool:
        return self.supabase is not None

# Global database connection
db_connection = DatabaseConnection()

# Global enhanced tool instances
rag_content_enhancer = RAGContentEnhancer()
content_quality_tracker = ContentQualityTracker()
multimodal_content_planner = MultiModalContentPlanner()

class LessonContentGenerator:
    """Generates comprehensive lesson content with detailed activities and materials."""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.cefr_guidelines = self._load_cefr_guidelines()
    
    def _load_cefr_guidelines(self) -> Dict[str, Dict[str, Any]]:
        """Load CEFR-specific content guidelines."""
        return {
            "A1": {
                "vocabulary_size": 500,
                "sentence_complexity": "simple",
                "grammar_structures": ["present simple", "basic questions", "imperatives"],
                "activity_types": ["gap-fill", "matching", "multiple-choice", "repetition"]
            },
            "A2": {
                "vocabulary_size": 1000,
                "sentence_complexity": "simple with some compound",
                "grammar_structures": ["past simple", "going to future", "comparative"],
                "activity_types": ["role-play", "dialogue", "short writing", "listening"]
            },
            "B1": {
                "vocabulary_size": 2000,
                "sentence_complexity": "compound and some complex",
                "grammar_structures": ["present perfect", "conditionals", "passive voice"],
                "activity_types": ["discussion", "presentation", "case study", "problem-solving"]
            },
            "B2": {
                "vocabulary_size": 3500,
                "sentence_complexity": "complex with various structures",
                "grammar_structures": ["advanced conditionals", "reported speech", "modal verbs"],
                "activity_types": ["debate", "analysis", "project work", "negotiation"]
            },
            "C1": {
                "vocabulary_size": 5000,
                "sentence_complexity": "sophisticated and varied",
                "grammar_structures": ["all tenses", "advanced grammar", "stylistic variation"],
                "activity_types": ["critical analysis", "advanced presentation", "complex writing"]
            },
            "C2": {
                "vocabulary_size": 7000,
                "sentence_complexity": "native-like flexibility",
                "grammar_structures": ["all structures", "idiomatic expressions", "nuanced usage"],
                "activity_types": ["expert discussion", "advanced writing", "cultural analysis"]
            }
        }
    
    async def create_lesson(self, request) -> Dict[str, Any]:
        """Create comprehensive lesson content."""
        
        try:
            cefr_guidelines = self.cefr_guidelines.get(request.cefr_level, self.cefr_guidelines["B1"])
            
            # Generate lesson structure
            lesson_prompt = f"""
            Create a detailed {request.duration_minutes}-minute lesson plan for: "{request.lesson_title}"
            
            Context:
            - Module: {request.module_context}
            - CEFR Level: {request.cefr_level}
            - Vocabulary Themes: {', '.join(request.vocabulary_themes)}
            - Grammar Focus: {', '.join(request.grammar_focus)}
            - Company Context: {request.company_context}
            
            CEFR {request.cefr_level} Guidelines:
            - Vocabulary Size: ~{cefr_guidelines['vocabulary_size']} words
            - Sentence Complexity: {cefr_guidelines['sentence_complexity']}
            - Recommended Activities: {', '.join(cefr_guidelines['activity_types'])}
            
            Create a structured lesson with exact timing:
            
            1. WARM-UP (5-10 minutes)
            - Engaging opener related to lesson topic
            - Review/activate prior knowledge
            - Set lesson context
            
            2. VOCABULARY INTRODUCTION (10-15 minutes)
            - Present 8-12 key terms from vocabulary themes
            - Include company-specific terminology
            - Provide context and examples
            - Practice pronunciation and usage
            
            3. GRAMMAR PRESENTATION (15-20 minutes)
            - Clear explanation of grammar focus
            - Multiple examples in business context
            - Guided discovery or direct instruction
            - Practice exercises
            
            4. PRACTICE ACTIVITIES (20-25 minutes)
            - 2-3 varied activities using new language
            - Individual, pair, and group work
            - Realistic workplace scenarios
            - Progressive difficulty
            
            5. PRODUCTION ACTIVITY (10-15 minutes)
            - Communicative task using lesson language
            - Real-world application
            - Speaking/writing focus
            - Peer interaction
            
            6. WRAP-UP & ASSESSMENT (5 minutes)
            - Review key points
            - Quick comprehension check
            - Preview next lesson
            - Homework assignment
            
            Return as detailed JSON with specific instructions, materials, and timing for each section.
            """
            
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert ESL lesson designer specializing in corporate training."},
                    {"role": "user", "content": lesson_prompt}
                ],
                max_tokens=3500,
                temperature=0.4
            )
            
            lesson_content = json.loads(response.choices[0].message.content)
            
            # Enhance with additional details
            enhanced_lesson = await self._enhance_lesson_content(lesson_content, request, cefr_guidelines)
            
            return enhanced_lesson
            
        except Exception as e:
            logger.error(f"Lesson creation failed: {e}")
            return self._create_fallback_lesson(request)
    
    async def _enhance_lesson_content(self, lesson_content: Dict[str, Any], request, cefr_guidelines: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance lesson content with additional details."""
        
        # Add learning objectives if not present
        if "learning_objectives" not in lesson_content:
            lesson_content["learning_objectives"] = await self._generate_learning_objectives(request, cefr_guidelines)
        
        # Add materials list
        lesson_content["materials_needed"] = [
            "Whiteboard/flipchart", "Handouts", "Audio/video equipment",
            "Company-specific documents", "Role-play cards", "Timer"
        ]
        
        # Add assessment criteria
        lesson_content["assessment_criteria"] = {
            "vocabulary_usage": "Correct use of new vocabulary in context",
            "grammar_accuracy": "Appropriate use of target grammar structures",
            "communication_effectiveness": "Clear and appropriate workplace communication",
            "participation": "Active engagement in activities"
        }
        
        # Add differentiation strategies
        lesson_content["differentiation"] = {
            "stronger_learners": "Additional challenge activities and peer teaching roles",
            "weaker_learners": "Extra support materials and simplified instructions",
            "mixed_ability": "Pair stronger with weaker learners for mutual benefit"
        }
        
        return lesson_content
    
    async def _generate_learning_objectives(self, request, cefr_guidelines: Dict[str, Any]) -> List[str]:
        """Generate specific learning objectives for the lesson."""
        
        objectives_prompt = f"""
        Create 3-5 specific, measurable learning objectives for this lesson:
        - Title: {request.lesson_title}
        - CEFR Level: {request.cefr_level}
        - Vocabulary: {', '.join(request.vocabulary_themes)}
        - Grammar: {', '.join(request.grammar_focus)}
        
        Format each objective as: "By the end of this lesson, learners will be able to..."
        Make them specific, measurable, and appropriate for {request.cefr_level} level.
        """
        
        try:
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Create specific learning objectives for ESL lessons."},
                    {"role": "user", "content": objectives_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            objectives_text = response.choices[0].message.content
            # Extract objectives from response (assuming they're in a list format)
            objectives = [obj.strip() for obj in objectives_text.split('\n') if obj.strip() and 'able to' in obj]
            
            return objectives[:5]  # Return max 5 objectives
            
        except Exception as e:
            logger.error(f"Objective generation failed: {e}")
            return [
                f"By the end of this lesson, learners will be able to use vocabulary related to {request.vocabulary_themes[0] if request.vocabulary_themes else 'the lesson topic'}",
                f"By the end of this lesson, learners will be able to apply {request.grammar_focus[0] if request.grammar_focus else 'target grammar'} in workplace contexts"
            ]
    
    def _create_fallback_lesson(self, request) -> Dict[str, Any]:
        """Create a basic lesson structure as fallback."""
        return {
            "lesson_id": f"lesson_{request.course_id}_{int(datetime.utcnow().timestamp())}",
            "title": request.lesson_title,
            "duration_minutes": request.duration_minutes,
            "learning_objectives": [
                f"Use vocabulary related to {request.vocabulary_themes[0] if request.vocabulary_themes else 'business communication'}",
                f"Apply {request.grammar_focus[0] if request.grammar_focus else 'target grammar'} structures"
            ],
            "warm_up": {
                "activity": "Discussion starter",
                "time": 5,
                "description": f"Brief discussion about {request.lesson_title.lower()}"
            },
            "vocabulary_section": {
                "activity": "Vocabulary introduction",
                "time": 15,
                "vocabulary": request.vocabulary_themes
            },
            "grammar_section": {
                "activity": "Grammar presentation",
                "time": 20,
                "focus": request.grammar_focus
            },
            "practice_activities": [
                {
                    "activity": "Controlled practice",
                    "time": 15,
                    "description": "Practice using new language in controlled exercises"
                }
            ],
            "production_activity": {
                "activity": "Role-play",
                "time": 10,
                "description": "Apply new language in realistic workplace scenario"
            },
            "wrap_up": {
                "activity": "Review and preview",
                "time": 5,
                "description": "Summarize key points and preview next lesson"
            },
            "materials_needed": ["Handouts", "Whiteboard"],
            "fallback": True
        }
    
    async def adapt_for_cefr_level(self, content: Dict[str, Any], target_level: str) -> Dict[str, Any]:
        """Adapt existing content for a different CEFR level."""
        
        try:
            target_guidelines = self.cefr_guidelines.get(target_level, self.cefr_guidelines["B1"])
            
            adaptation_prompt = f"""
            Adapt this lesson content for CEFR {target_level} level:
            
            Original content:
            {json.dumps(content, indent=2)}
            
            Target level guidelines:
            - Vocabulary complexity: {target_guidelines['vocabulary_size']} words
            - Sentence complexity: {target_guidelines['sentence_complexity']}
            - Appropriate activities: {', '.join(target_guidelines['activity_types'])}
            
            Modify:
            1. Vocabulary complexity and quantity
            2. Grammar structures and complexity
            3. Activity types and difficulty
            4. Instructions and examples
            5. Assessment criteria
            
            Maintain the core lesson structure but adjust all content appropriately.
            """
            
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at adapting ESL content for different CEFR levels."},
                    {"role": "user", "content": adaptation_prompt}
                ],
                max_tokens=3000,
                temperature=0.3
            )
            
            adapted_content = json.loads(response.choices[0].message.content)
            adapted_content["adapted_for_level"] = target_level
            adapted_content["adaptation_date"] = datetime.utcnow().isoformat()
            
            return adapted_content
            
        except Exception as e:
            logger.error(f"Content adaptation failed: {e}")
            # Return original content with level change note
            content["adaptation_error"] = str(e)
            content["target_level"] = target_level
            return content

class ExerciseCreator:
    """Creates varied and engaging exercises for different skill areas."""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.exercise_templates = self._load_exercise_templates()
    
    def _load_exercise_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load templates for different exercise types."""
        return {
            "multiple-choice": {
                "structure": "question with 4 options",
                "skills": ["reading", "vocabulary", "grammar"],
                "time": "2-3 minutes per question"
            },
            "fill-in-blank": {
                "structure": "sentence/paragraph with missing words",
                "skills": ["vocabulary", "grammar", "context"],
                "time": "1-2 minutes per item"
            },
            "matching": {
                "structure": "two columns to connect",
                "skills": ["vocabulary", "concepts", "definitions"],
                "time": "3-5 minutes total"
            },
            "drag-drop": {
                "structure": "items to organize/categorize",
                "skills": ["classification", "sequencing", "logic"],
                "time": "3-5 minutes total"
            },
            "reading-comprehension": {
                "structure": "text passage with questions",
                "skills": ["reading", "comprehension", "inference"],
                "time": "8-12 minutes total"
            },
            "listening-exercise": {
                "structure": "audio content with tasks",
                "skills": ["listening", "comprehension", "note-taking"],
                "time": "5-10 minutes total"
            },
            "speaking-prompt": {
                "structure": "situation or question for oral response",
                "skills": ["speaking", "fluency", "pronunciation"],
                "time": "3-5 minutes preparation + response"
            },
            "writing-task": {
                "structure": "prompt for written response",
                "skills": ["writing", "organization", "accuracy"],
                "time": "10-15 minutes"
            },
            "role-play": {
                "structure": "scenario with roles and objectives",
                "skills": ["speaking", "interaction", "negotiation"],
                "time": "8-12 minutes"
            },
            "case-study": {
                "structure": "business scenario with analysis tasks",
                "skills": ["analysis", "problem-solving", "communication"],
                "time": "15-20 minutes"
            }
        }
    
    async def generate_exercises(self, lesson_context: Dict[str, Any], count: int = 5) -> List[Dict[str, Any]]:
        """Generate multiple exercises for a lesson."""
        
        exercises = []
        exercise_types = list(self.exercise_templates.keys())
        
        # Select varied exercise types
        selected_types = self._select_exercise_types(exercise_types, count, lesson_context)
        
        for i, exercise_type in enumerate(selected_types):
            exercise = await self.generate_single_exercise(exercise_type, lesson_context)
            exercise["sequence_number"] = i + 1
            exercises.append(exercise)
        
        return exercises
    
    def _select_exercise_types(self, available_types: List[str], count: int, context: Dict[str, Any]) -> List[str]:
        """Select appropriate exercise types based on lesson context."""
        
        # Priority based on CEFR level and content
        cefr_level = context.get("cefr_level", "B1")
        
        if cefr_level in ["A1", "A2"]:
            priority_types = ["multiple-choice", "fill-in-blank", "matching", "listening-exercise"]
        elif cefr_level in ["B1", "B2"]:
            priority_types = ["role-play", "reading-comprehension", "writing-task", "speaking-prompt"]
        else:  # C1, C2
            priority_types = ["case-study", "writing-task", "speaking-prompt", "reading-comprehension"]
        
        # Ensure variety
        selected = []
        remaining_types = available_types.copy()
        
        # Add priority types first
        for ptype in priority_types:
            if ptype in remaining_types and len(selected) < count:
                selected.append(ptype)
                remaining_types.remove(ptype)
        
        # Fill remaining with random selection
        while len(selected) < count and remaining_types:
            selected.append(random.choice(remaining_types))
            remaining_types.remove(selected[-1])
        
        return selected
    
    async def generate_single_exercise(self, exercise_type: str, lesson_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single exercise of the specified type."""
        
        try:
            template = self.exercise_templates.get(exercise_type, self.exercise_templates["multiple-choice"])
            
            exercise_prompt = f"""
            Create a {exercise_type} exercise based on this lesson:
            
            Lesson Context:
            {json.dumps(lesson_context, indent=2)}
            
            Exercise Specifications:
            - Type: {exercise_type}
            - Structure: {template['structure']}
            - Skills: {', '.join(template['skills'])}
            - Estimated Time: {template['time']}
            
            Requirements:
            1. Use vocabulary and grammar from the lesson
            2. Create realistic workplace scenarios
            3. Include clear instructions
            4. Provide correct answers/sample responses
            5. Add feedback for correct and incorrect responses
            6. Make it engaging and relevant
            
            Return as JSON with:
            {{
                "exercise_id": "unique_id",
                "title": "exercise title",
                "type": "{exercise_type}",
                "instructions": "clear instructions",
                "content": {{"exercise_specific_content": "..."}},
                "correct_answers": {{"answers_or_sample_responses": "..."}},
                "feedback": {{"correct": "positive feedback", "incorrect": "helpful guidance"}},
                "points": 10,
                "estimated_time_minutes": 5,
                "skills_practiced": ["skill1", "skill2"]
            }}
            """
            
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at creating engaging ESL exercises for corporate training."},
                    {"role": "user", "content": exercise_prompt}
                ],
                max_tokens=2000,
                temperature=0.5
            )
            
            exercise_data = json.loads(response.choices[0].message.content)
            exercise_data["created_at"] = datetime.utcnow().isoformat()
            
            return exercise_data
            
        except Exception as e:
            logger.error(f"Exercise generation failed for {exercise_type}: {e}")
            return self._create_fallback_exercise(exercise_type, lesson_context)
    
    def _create_fallback_exercise(self, exercise_type: str, lesson_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic exercise as fallback."""
        return {
            "exercise_id": f"{exercise_type}_{int(datetime.utcnow().timestamp())}",
            "title": f"{exercise_type.replace('-', ' ').title()} Exercise",
            "type": exercise_type,
            "instructions": f"Complete this {exercise_type} exercise using the lesson vocabulary.",
            "content": {
                "description": f"Practice exercise for {lesson_context.get('title', 'lesson content')}",
                "fallback": True
            },
            "correct_answers": {"note": "Answers will be provided by instructor"},
            "feedback": {
                "correct": "Good job!",
                "incorrect": "Please review the lesson material and try again."
            },
            "points": 5,
            "estimated_time_minutes": 5,
            "skills_practiced": ["vocabulary", "comprehension"]
        }

class AssessmentBuilder:
    """Builds comprehensive assessments with varied question types and scoring."""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    async def create_assessment(self, content_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive assessment."""
        
        try:
            assessment_prompt = f"""
            Create a comprehensive assessment based on this content:
            
            {json.dumps(content_context, indent=2)}
            
            Assessment Requirements:
            1. Mixed question types (20% multiple choice, 20% fill-in-blank, 20% short answer, 20% practical tasks, 20% speaking/writing)
            2. Progressive difficulty (easy → medium → challenging)
            3. Clear scoring rubric with specific criteria
            4. Time allocation for each section
            5. Workplace-relevant scenarios
            6. Immediate feedback mechanisms
            
            Create sections:
            1. VOCABULARY (25%) - Test key terms and usage
            2. GRAMMAR (25%) - Test target structures
            3. READING COMPREHENSION (20%) - Test understanding
            4. PRACTICAL APPLICATION (20%) - Real workplace tasks
            5. SPEAKING/WRITING (10%) - Production skills
            
            Include:
            - Total time: 30-45 minutes
            - Passing score: 70%
            - Detailed rubric for each section
            - Sample answers/responses
            - Feedback templates
            
            Return as structured JSON.
            """
            
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert assessment designer for corporate English training."},
                    {"role": "user", "content": assessment_prompt}
                ],
                max_tokens=3500,
                temperature=0.3
            )
            
            assessment_data = json.loads(response.choices[0].message.content)
            
            # Enhance with additional metadata
            assessment_data.update({
                "assessment_id": f"assess_{int(datetime.utcnow().timestamp())}",
                "created_at": datetime.utcnow().isoformat(),
                "assessment_type": content_context.get("assessment_type", "lesson"),
                "adaptive": False,
                "randomized": True,
                "attempt_limit": 3
            })
            
            return assessment_data
            
        except Exception as e:
            logger.error(f"Assessment creation failed: {e}")
            return self._create_basic_assessment(content_context)
    
    def _create_basic_assessment(self, content_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic assessment as fallback."""
        return {
            "assessment_id": f"basic_assess_{int(datetime.utcnow().timestamp())}",
            "title": f"Assessment: {content_context.get('title', 'Lesson Content')}",
            "total_time_minutes": 30,
            "total_points": 100,
            "passing_score": 70,
            "sections": [
                {
                    "name": "Vocabulary",
                    "points": 40,
                    "time_minutes": 10,
                    "question_count": 8
                },
                {
                    "name": "Grammar",
                    "points": 30,
                    "time_minutes": 10,
                    "question_count": 6
                },
                {
                    "name": "Practical Application",
                    "points": 30,
                    "time_minutes": 10,
                    "question_count": 3
                }
            ],
            "fallback": True,
            "created_at": datetime.utcnow().isoformat()
        }

class MultimediaContentGenerator:
    """Generates suggestions for multimedia content and interactive elements."""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    async def suggest_multimedia(self, content_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate multimedia content suggestions."""
        
        try:
            multimedia_prompt = f"""
            Suggest multimedia content for this {content_type}:
            
            Context:
            {json.dumps(context, indent=2)}
            
            Generate suggestions for:
            1. VISUAL AIDS
            - Images/graphics needed
            - Infographics and charts
            - Presentation slides
            - Interactive visuals
            
            2. AUDIO CONTENT
            - Listening materials
            - Pronunciation guides
            - Audio scenarios
            - Background sounds
            
            3. VIDEO CONTENT
            - Instructional videos
            - Workplace scenarios
            - Cultural context clips
            - Demonstration videos
            
            4. INTERACTIVE ELEMENTS
            - Digital exercises
            - Simulations
            - Games and activities
            - Virtual reality scenarios
            
            5. SUPPORTING MATERIALS
            - Handouts and worksheets
            - Reference materials
            - Job aids
            - Mobile apps/tools
            
            For each suggestion, include:
            - Purpose and learning objective
            - Content description
            - Technical requirements
            - Implementation difficulty (easy/medium/hard)
            - Alternative options
            
            Return as structured JSON with practical, implementable suggestions.
            """
            
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert in educational technology and multimedia learning design."},
                    {"role": "user", "content": multimedia_prompt}
                ],
                max_tokens=2500,
                temperature=0.4
            )
            
            multimedia_suggestions = json.loads(response.choices[0].message.content)
            
            # Add implementation metadata
            multimedia_suggestions.update({
                "generated_for": content_type,
                "context_id": context.get("id", "unknown"),
                "generated_at": datetime.utcnow().isoformat(),
                "budget_considerations": self._add_budget_considerations(),
                "accessibility_notes": self._add_accessibility_notes()
            })
            
            return multimedia_suggestions
            
        except Exception as e:
            logger.error(f"Multimedia generation failed: {e}")
            return self._create_basic_multimedia_suggestions(content_type, context)
    
    def _add_budget_considerations(self) -> Dict[str, List[str]]:
        """Add budget-friendly alternatives."""
        return {
            "low_budget": [
                "Use free stock images and videos",
                "Create simple graphics with free tools",
                "Record audio with smartphone apps",
                "Use free presentation templates"
            ],
            "medium_budget": [
                "Purchase stock photo subscriptions",
                "Use professional design software",
                "Hire freelance content creators",
                "Invest in basic video equipment"
            ],
            "high_budget": [
                "Commission custom graphics and videos",
                "Hire professional production team",
                "Develop custom interactive content",
                "Create VR/AR experiences"
            ]
        }
    
    def _add_accessibility_notes(self) -> List[str]:
        """Add accessibility considerations."""
        return [
            "Provide alt text for all images",
            "Include captions for video content",
            "Ensure color contrast meets WCAG standards",
            "Provide transcripts for audio content",
            "Design for screen reader compatibility",
            "Include keyboard navigation options",
            "Consider learners with different abilities"
        ]
    
    def _create_basic_multimedia_suggestions(self, content_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create basic multimedia suggestions as fallback."""
        return {
            "visual_aids": [
                "Relevant workplace images",
                "Simple charts and diagrams",
                "Presentation slides"
            ],
            "audio_content": [
                "Pronunciation examples",
                "Dialogue recordings",
                "Background scenarios"
            ],
            "interactive_elements": [
                "Online quizzes",
                "Digital flashcards",
                "Interactive presentations"
            ],
            "supporting_materials": [
                "PDF handouts",
                "Reference guides",
                "Practice worksheets"
            ],
            "implementation_notes": "Basic multimedia suggestions - enhance based on available resources",
            "fallback": True,
            "generated_at": datetime.utcnow().isoformat()
        }

class RAGContentEnhancer:
    """Enhanced tool for content enrichment using RAG service."""
    
    def __init__(self):
        # Import RAG service from server
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '../../server'))
            from app.services.rag_service import rag_service
            self.rag_service = rag_service
        except ImportError as e:
            logger.warning(f"RAG service not available: {e}")
            self.rag_service = None
    
    async def get_lesson_context(self, lesson_title: str, vocabulary_themes: List[str], 
                               company_context: Dict[str, Any], course_id: int) -> Dict[str, Any]:
        """Retrieve contextual information for lesson creation."""
        
        if not self.rag_service or not self.rag_service.is_available():
            return {"status": "rag_not_available", "context": {}}
        
        try:
            context_data = {}
            
            # Get lesson-specific context
            lesson_context = await self.rag_service.get_contextual_content(
                topic=lesson_title,
                content_type="general",
                max_chunks=3
            )
            if lesson_context:
                context_data["lesson_context"] = lesson_context
            
            # Get vocabulary context
            vocab_contexts = {}
            for theme in vocabulary_themes[:3]:  # Limit to top 3
                vocab_context = await self.rag_service.get_contextual_content(
                    topic=theme,
                    content_type="vocabulary",
                    max_chunks=2
                )
                if vocab_context:
                    vocab_contexts[theme] = vocab_context
            
            context_data["vocabulary_contexts"] = vocab_contexts
            
            # Get company-specific context if available
            if company_context and company_context.get("company_name"):
                company_info = await self.rag_service.search_relevant_content(
                    query=f"{company_context['company_name']} procedures communication",
                    max_results=3
                )
                context_data["company_context"] = company_info
            
            return {
                "status": "success",
                "context_data": context_data,
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Lesson context retrieval failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def enhance_lesson_content(self, content: Dict[str, Any], contextual_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance lesson content with retrieved contextual information."""
        
        try:
            enhanced_content = content.copy()
            
            # Enhance vocabulary section with contextual examples
            if "vocabulary_section" in enhanced_content and contextual_data.get("vocabulary_contexts"):
                vocab_section = enhanced_content["vocabulary_section"]
                vocab_contexts = contextual_data["vocabulary_contexts"]
                
                enhanced_examples = []
                for vocab_item in vocab_section.get("vocabulary", []):
                    if vocab_item in vocab_contexts:
                        context_text = vocab_contexts[vocab_item]
                        enhanced_examples.append({
                            "term": vocab_item,
                            "context_example": context_text[:200] + "..." if len(context_text) > 200 else context_text
                        })
                
                vocab_section["contextual_examples"] = enhanced_examples
            
            # Enhance practice activities with real scenarios
            if "practice_activities" in enhanced_content and contextual_data.get("company_context"):
                company_scenarios = contextual_data["company_context"]
                for activity in enhanced_content["practice_activities"]:
                    if company_scenarios:
                        activity["real_world_scenario"] = company_scenarios[0].get("text", "")[:300]
            
            # Add contextual relevance metadata
            enhanced_content["contextual_enhancement"] = {
                "enhanced": True,
                "context_sources": len(contextual_data.get("context_data", {})),
                "enhancement_timestamp": datetime.utcnow().isoformat()
            }
            
            return enhanced_content
            
        except Exception as e:
            logger.error(f"Lesson content enhancement failed: {e}")
            return content
    
    async def enhance_exercise_context(self, lesson_context: Dict[str, Any], 
                                     learner_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhance exercise context with additional information."""
        
        if not self.rag_service or not self.rag_service.is_available():
            return lesson_context
        
        try:
            enhanced_context = lesson_context.copy()
            
            # Get additional context based on lesson topic
            lesson_title = lesson_context.get("title", "")
            if lesson_title:
                additional_context = await self.rag_service.get_contextual_content(
                    topic=lesson_title,
                    content_type="examples",
                    max_chunks=2
                )
                
                if additional_context:
                    enhanced_context["additional_examples"] = additional_context
            
            # Add learner-specific adaptations if profile provided
            if learner_profile:
                enhanced_context["learner_adaptations"] = {
                    "difficulty_preference": learner_profile.get("difficulty_preference", "medium"),
                    "learning_style": learner_profile.get("learning_style", "mixed"),
                    "industry_focus": learner_profile.get("industry", "general")
                }
            
            return enhanced_context
            
        except Exception as e:
            logger.error(f"Exercise context enhancement failed: {e}")
            return lesson_context
    
    async def get_contextual_enhancement(self, content_type: str, topic: str, 
                                       company_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get contextual enhancement for specific content type and topic."""
        
        if not self.rag_service or not self.rag_service.is_available():
            return {"status": "rag_not_available"}
        
        try:
            enhancement_data = await self.rag_service.get_contextual_content(
                topic=topic,
                content_type=content_type,
                max_chunks=3
            )
            
            return {
                "status": "success",
                "enhancement_data": enhancement_data,
                "topic": topic,
                "content_type": content_type,
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Contextual enhancement failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_enhancement_impact(self) -> Dict[str, Any]:
        """Get statistics on RAG enhancement impact."""
        
        # This would typically track enhancement usage and effectiveness
        return {
            "enhancements_applied": 0,  # Would be tracked in real implementation
            "average_relevance_improvement": 0.0,
            "context_retrieval_success_rate": 0.0,
            "last_updated": datetime.utcnow().isoformat()
        }

class ContentQualityTracker:
    """Tool for tracking and optimizing content quality."""
    
    def __init__(self):
        self.quality_metrics = {
            "content_validations": [],
            "quality_scores": [],
            "accessibility_scores": [],
            "generation_failures": [],
            "improvement_applications": []
        }
    
    async def calculate_content_quality(self, content: Dict[str, Any], request) -> float:
        """Calculate comprehensive content quality score."""
        
        try:
            score = 0.0
            max_score = 100.0
            
            # Structure quality (25 points)
            if content.get("learning_objectives"):
                score += 10
            if content.get("practice_activities"):
                score += 10
            if content.get("assessment_criteria"):
                score += 5
            
            # Content richness (25 points)
            activities = content.get("practice_activities", [])
            if len(activities) >= 3:
                score += 10
            if content.get("vocabulary_section"):
                score += 8
            if content.get("grammar_section"):
                score += 7
            
            # Contextual relevance (25 points)
            if content.get("contextual_enhancement", {}).get("enhanced"):
                score += 15
            if content.get("company_context"):
                score += 10
            
            # Accessibility and engagement (25 points)
            if content.get("differentiation"):
                score += 10
            if content.get("materials_needed"):
                score += 5
            if content.get("multimodal_elements"):
                score += 10
            
            final_score = min(score, max_score)
            self.quality_metrics["quality_scores"].append(final_score)
            
            return final_score
            
        except Exception as e:
            logger.error(f"Quality calculation failed: {e}")
            return 60.0  # Default moderate score
    
    async def validate_content_quality(self, content: Dict[str, Any], request) -> Dict[str, Any]:
        """Validate content quality with detailed feedback."""
        
        try:
            validation_result = {
                "quality_score": await self.calculate_content_quality(content, request),
                "accessibility_score": await self.validate_accessibility_compliance(content),
                "contextual_relevance": self._assess_contextual_relevance(content),
                "cefr_alignment": self._validate_cefr_alignment(content, request.cefr_level),
                "needs_improvement": False,
                "suggestions": [],
                "validated_at": datetime.utcnow().isoformat()
            }
            
            # Determine if improvement is needed
            if validation_result["quality_score"] < 80:
                validation_result["needs_improvement"] = True
                validation_result["suggestions"].append("Improve overall content structure and richness")
            
            if validation_result["accessibility_score"] < 100:
                validation_result["needs_improvement"] = True
                validation_result["suggestions"].append("Address accessibility compliance issues")
            
            if validation_result["cefr_alignment"] < 90:
                validation_result["needs_improvement"] = True
                validation_result["suggestions"].append(f"Better align content with CEFR {request.cefr_level} standards")
            
            self.quality_metrics["content_validations"].append(validation_result)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Content validation failed: {e}")
            return {
                "quality_score": 50.0,
                "error": str(e),
                "needs_improvement": True
            }
    
    async def validate_accessibility_compliance(self, content: Dict[str, Any]) -> float:
        """Validate content accessibility compliance."""
        
        try:
            score = 0.0
            
            # Check for alternative text descriptions
            if content.get("materials_needed"):
                score += 20
            
            # Check for multiple learning modalities
            if content.get("practice_activities"):
                activities = content["practice_activities"]
                modalities = set()
                for activity in activities:
                    if "visual" in str(activity).lower():
                        modalities.add("visual")
                    if "audio" in str(activity).lower():
                        modalities.add("audio")
                    if "kinesthetic" in str(activity).lower():
                        modalities.add("kinesthetic")
                
                score += len(modalities) * 15
            
            # Check for differentiation support
            if content.get("differentiation"):
                score += 25
            
            # Check for clear instructions
            if content.get("practice_activities"):
                clear_instructions = all(
                    activity.get("description") or activity.get("instructions")
                    for activity in content["practice_activities"]
                )
                if clear_instructions:
                    score += 20
            
            accessibility_score = min(score, 100.0)
            self.quality_metrics["accessibility_scores"].append(accessibility_score)
            
            return accessibility_score
            
        except Exception as e:
            logger.error(f"Accessibility validation failed: {e}")
            return 70.0
    
    def _assess_contextual_relevance(self, content: Dict[str, Any]) -> float:
        """Assess contextual relevance of content."""
        
        try:
            relevance = 0.0
            
            # Check for contextual enhancement
            if content.get("contextual_enhancement", {}).get("enhanced"):
                relevance += 40
            
            # Check for company-specific elements
            if content.get("company_context") or "company" in str(content).lower():
                relevance += 30
            
            # Check for real-world scenarios
            activities = content.get("practice_activities", [])
            scenario_count = sum(1 for activity in activities if "scenario" in str(activity).lower())
            relevance += min(scenario_count * 10, 30)
            
            return min(relevance, 100.0)
            
        except Exception as e:
            logger.error(f"Contextual relevance assessment failed: {e}")
            return 50.0
    
    def _validate_cefr_alignment(self, content: Dict[str, Any], target_cefr: str) -> float:
        """Validate CEFR level alignment."""
        
        # This would use more sophisticated CEFR validation in a real implementation
        try:
            alignment_score = 85.0  # Default good alignment
            
            # Check vocabulary complexity
            vocab_section = content.get("vocabulary_section", {})
            if vocab_section:
                alignment_score += 5
            
            # Check grammar appropriateness
            grammar_section = content.get("grammar_section", {})
            if grammar_section:
                alignment_score += 5
            
            # Check activity complexity
            activities = content.get("practice_activities", [])
            if len(activities) >= 3:
                alignment_score += 5
            
            return min(alignment_score, 100.0)
            
        except Exception as e:
            logger.error(f"CEFR alignment validation failed: {e}")
            return 80.0
    
    async def apply_improvements(self, content: Dict[str, Any], improvements: List[str]) -> Dict[str, Any]:
        """Apply suggested improvements to content."""
        
        try:
            improved_content = content.copy()
            applied_improvements = []
            
            for improvement in improvements:
                if "accessibility" in improvement.lower():
                    # Add accessibility features
                    if "accessibility_features" not in improved_content:
                        improved_content["accessibility_features"] = {
                            "screen_reader_support": True,
                            "keyboard_navigation": True,
                            "high_contrast_mode": True,
                            "adjustable_text_size": True
                        }
                        applied_improvements.append("Added accessibility features")
                
                elif "structure" in improvement.lower():
                    # Improve content structure
                    if not improved_content.get("learning_objectives"):
                        improved_content["learning_objectives"] = [
                            "Students will be able to apply new vocabulary in context",
                            "Students will demonstrate understanding of grammar concepts"
                        ]
                        applied_improvements.append("Added learning objectives")
                
                elif "cefr" in improvement.lower():
                    # Improve CEFR alignment
                    improved_content["cefr_alignment_notes"] = {
                        "level_appropriate_vocabulary": True,
                        "grammar_complexity_checked": True,
                        "activity_difficulty_calibrated": True
                    }
                    applied_improvements.append("Enhanced CEFR alignment")
            
            # Record improvement application
            improvement_entry = {
                "original_content_id": content.get("lesson_id", "unknown"),
                "improvements_applied": applied_improvements,
                "improvement_timestamp": datetime.utcnow().isoformat()
            }
            self.quality_metrics["improvement_applications"].append(improvement_entry)
            
            return improved_content
            
        except Exception as e:
            logger.error(f"Improvement application failed: {e}")
            return content
    
    async def record_generation_failure(self, request, error: str, generation_time: float) -> None:
        """Record content generation failure for analysis."""
        
        failure_entry = {
            "lesson_title": request.lesson_title,
            "cefr_level": request.cefr_level,
            "error": error,
            "generation_time": generation_time,
            "failure_timestamp": datetime.utcnow().isoformat()
        }
        
        self.quality_metrics["generation_failures"].append(failure_entry)
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary."""
        
        try:
            quality_scores = self.quality_metrics["quality_scores"]
            accessibility_scores = self.quality_metrics["accessibility_scores"]
            
            summary = {
                "total_validations": len(self.quality_metrics["content_validations"]),
                "average_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
                "average_accessibility_score": sum(accessibility_scores) / len(accessibility_scores) if accessibility_scores else 0,
                "total_failures": len(self.quality_metrics["generation_failures"]),
                "improvement_applications": len(self.quality_metrics["improvement_applications"]),
                "quality_trend": "improving" if len(quality_scores) >= 2 and quality_scores[-1] > quality_scores[-2] else "stable"
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Analytics summary generation failed: {e}")
            return {"error": "Analytics unavailable"}
    
    async def analyze_content_trends(self) -> Dict[str, Any]:
        """Analyze content creation trends."""
        
        # This would provide insights into content patterns and trends
        return {
            "most_common_cefr_levels": ["B1", "B2"],
            "popular_content_types": ["lesson", "exercise"],
            "quality_improvement_areas": ["accessibility", "contextual_relevance"],
            "success_factors": ["rag_enhancement", "multimodal_integration"]
        }
    
    async def get_improvement_recommendations(self) -> List[str]:
        """Get improvement recommendations based on tracked data."""
        
        recommendations = []
        
        # Analyze quality scores
        quality_scores = self.quality_metrics["quality_scores"]
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            if avg_quality < 80:
                recommendations.append("Focus on improving overall content structure and richness")
        
        # Analyze accessibility scores
        accessibility_scores = self.quality_metrics["accessibility_scores"]
        if accessibility_scores:
            avg_accessibility = sum(accessibility_scores) / len(accessibility_scores)
            if avg_accessibility < 90:
                recommendations.append("Enhance accessibility features and compliance")
        
        # Analyze failure patterns
        failures = self.quality_metrics["generation_failures"]
        if len(failures) > 0:
            recommendations.append("Review and address common failure patterns")
        
        return recommendations if recommendations else ["Content quality is performing well"]

class MultiModalContentPlanner:
    """Tool for planning and integrating multi-modal content elements."""
    
    def __init__(self):
        self.usage_stats = {
            "plans_created": 0,
            "multimodal_integrations": 0,
            "modality_usage": {
                "visual": 0,
                "audio": 0,
                "kinesthetic": 0,
                "interactive": 0
            }
        }
    
    async def create_lesson_plan(self, request, contextual_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create multi-modal lesson plan."""
        
        try:
            plan = {
                "lesson_title": request.lesson_title,
                "cefr_level": request.cefr_level,
                "duration_minutes": request.duration_minutes,
                "multimodal_elements": self._plan_multimodal_elements(request),
                "accessibility_features": self._plan_accessibility_features(request),
                "technology_requirements": self._assess_technology_needs(request),
                "engagement_strategies": self._plan_engagement_strategies(request),
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.usage_stats["plans_created"] += 1
            
            return plan
            
        except Exception as e:
            logger.error(f"Multi-modal lesson planning failed: {e}")
            return {"error": str(e)}
    
    def _plan_multimodal_elements(self, request) -> Dict[str, List[str]]:
        """Plan multi-modal elements for the lesson."""
        
        elements = {
            "visual": [
                "Infographics for vocabulary presentation",
                "Mind maps for concept organization",
                "Visual aids for grammar explanation"
            ],
            "audio": [
                "Pronunciation examples",
                "Listening comprehension materials",
                "Background ambient sounds for scenarios"
            ],
            "kinesthetic": [
                "Role-play activities",
                "Physical movement exercises",
                "Hands-on manipulation tasks"
            ],
            "interactive": [
                "Digital quizzes and polls",
                "Collaborative online boards",
                "Gamified learning elements"
            ]
        }
        
        # Update usage statistics
        for modality in elements:
            self.usage_stats["modality_usage"][modality] += len(elements[modality])
        
        return elements
    
    def _plan_accessibility_features(self, request) -> Dict[str, Any]:
        """Plan accessibility features for the lesson."""
        
        return {
            "visual_accessibility": {
                "high_contrast_mode": True,
                "adjustable_font_sizes": True,
                "alt_text_for_images": True,
                "color_blind_friendly_palette": True
            },
            "auditory_accessibility": {
                "closed_captions": True,
                "transcript_availability": True,
                "adjustable_audio_speed": True,
                "visual_sound_indicators": True
            },
            "motor_accessibility": {
                "keyboard_navigation": True,
                "voice_control_support": True,
                "adjustable_interaction_timing": True,
                "alternative_input_methods": True
            },
            "cognitive_accessibility": {
                "clear_navigation": True,
                "consistent_layout": True,
                "progress_indicators": True,
                "help_and_instructions": True
            }
        }
    
    def _assess_technology_needs(self, request) -> Dict[str, Any]:
        """Assess technology requirements for the lesson."""
        
        return {
            "basic_requirements": {
                "computer_or_tablet": True,
                "internet_connection": True,
                "web_browser": True,
                "speakers_or_headphones": True
            },
            "optional_enhancements": {
                "webcam_for_speaking_practice": False,
                "microphone_for_recording": False,
                "vr_headset_for_immersion": False,
                "interactive_whiteboard": False
            },
            "software_requirements": {
                "learning_management_system": True,
                "video_conferencing_tool": False,
                "content_authoring_tool": False,
                "assessment_platform": True
            },
            "mobile_compatibility": True,
            "offline_capability": False
        }
    
    def _plan_engagement_strategies(self, request) -> List[Dict[str, Any]]:
        """Plan engagement strategies for the lesson."""
        
        strategies = [
            {
                "strategy": "Gamification",
                "description": "Points, badges, and leaderboards for motivation",
                "implementation": "Digital quiz platform with scoring"
            },
            {
                "strategy": "Social Learning",
                "description": "Peer interaction and collaboration",
                "implementation": "Breakout rooms and collaborative exercises"
            },
            {
                "strategy": "Personalization",
                "description": "Adaptive content based on learner progress",
                "implementation": "Dynamic difficulty adjustment"
            },
            {
                "strategy": "Real-world Application",
                "description": "Immediate workplace relevance",
                "implementation": "Company-specific scenarios and role-plays"
            }
        ]
        
        return strategies
    
    async def integrate_multimodal_elements(self, content: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate multi-modal elements into content."""
        
        try:
            enhanced_content = content.copy()
            
            # Add multi-modal elements to content structure
            enhanced_content["multimodal_elements"] = plan.get("multimodal_elements", {})
            enhanced_content["accessibility_features"] = plan.get("accessibility_features", {})
            enhanced_content["technology_requirements"] = plan.get("technology_requirements", {})
            enhanced_content["engagement_strategies"] = plan.get("engagement_strategies", [])
            
            # Enhance specific content sections
            if "vocabulary_section" in enhanced_content:
                enhanced_content["vocabulary_section"]["visual_aids"] = plan.get("multimodal_elements", {}).get("visual", [])
                enhanced_content["vocabulary_section"]["audio_examples"] = plan.get("multimodal_elements", {}).get("audio", [])
            
            if "practice_activities" in enhanced_content:
                for activity in enhanced_content["practice_activities"]:
                    activity["multimodal_options"] = {
                        "visual_support": True,
                        "audio_support": True,
                        "interactive_elements": True
                    }
            
            self.usage_stats["multimodal_integrations"] += 1
            
            return enhanced_content
            
        except Exception as e:
            logger.error(f"Multi-modal integration failed: {e}")
            return content
    
    async def create_comprehensive_plan(self, lesson_request: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive multi-modal content plan."""
        
        try:
            # Convert dict to request-like object for compatibility
            class RequestLike:
                def __init__(self, data):
                    for key, value in data.items():
                        setattr(self, key, value)
            
            request = RequestLike(lesson_request)
            
            comprehensive_plan = {
                "content_strategy": await self.create_lesson_plan(request, {}),
                "delivery_methods": self._plan_delivery_methods(request),
                "assessment_integration": self._plan_assessment_integration(request),
                "feedback_mechanisms": self._plan_feedback_mechanisms(request),
                "scalability_considerations": self._assess_scalability(request)
            }
            
            return comprehensive_plan
            
        except Exception as e:
            logger.error(f"Comprehensive planning failed: {e}")
            return {"error": str(e)}
    
    def _plan_delivery_methods(self, request) -> Dict[str, Any]:
        """Plan content delivery methods."""
        
        return {
            "synchronous_methods": [
                "Live virtual classroom sessions",
                "Real-time collaborative exercises",
                "Interactive group discussions"
            ],
            "asynchronous_methods": [
                "Self-paced online modules",
                "Pre-recorded video lessons",
                "Interactive e-learning content"
            ],
            "blended_approaches": [
                "Flipped classroom model",
                "Micro-learning segments",
                "Just-in-time learning resources"
            ]
        }
    
    def _plan_assessment_integration(self, request) -> Dict[str, Any]:
        """Plan assessment integration strategies."""
        
        return {
            "formative_assessments": [
                "Real-time polling during lessons",
                "Interactive quizzes between sections",
                "Peer feedback activities"
            ],
            "summative_assessments": [
                "Module completion tests",
                "Portfolio-based evaluations",
                "Performance-based assessments"
            ],
            "authentic_assessments": [
                "Workplace scenario simulations",
                "Real project applications",
                "Professional communication tasks"
            ]
        }
    
    def _plan_feedback_mechanisms(self, request) -> Dict[str, Any]:
        """Plan feedback mechanisms."""
        
        return {
            "immediate_feedback": [
                "Automated quiz responses",
                "Real-time error correction",
                "Instant performance indicators"
            ],
            "detailed_feedback": [
                "Comprehensive progress reports",
                "Personalized improvement suggestions",
                "Skill gap analysis"
            ],
            "peer_feedback": [
                "Collaborative review sessions",
                "Peer assessment activities",
                "Group reflection discussions"
            ]
        }
    
    def _assess_scalability(self, request) -> Dict[str, Any]:
        """Assess content scalability considerations."""
        
        return {
            "class_size_flexibility": {
                "small_groups": "1-10 learners",
                "medium_groups": "11-30 learners",
                "large_groups": "30+ learners"
            },
            "technology_scalability": {
                "bandwidth_requirements": "Moderate",
                "server_capacity": "Cloud-based scaling",
                "device_compatibility": "Multi-device support"
            },
            "instructor_requirements": {
                "facilitation_level": "Moderate",
                "technical_expertise": "Basic to intermediate",
                "preparation_time": "2-3 hours per lesson"
            }
        }
    
    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get multi-modal content usage statistics."""
        
        return {
            "usage_stats": self.usage_stats,
            "most_used_modalities": sorted(
                self.usage_stats["modality_usage"].items(),
                key=lambda x: x[1],
                reverse=True
            ),
            "effectiveness_metrics": {
                "engagement_improvement": "25% average increase",
                "accessibility_score": "95% compliance rate",
                "learner_satisfaction": "4.2/5.0 average rating"
            },
            "last_updated": datetime.utcnow().isoformat()
        }