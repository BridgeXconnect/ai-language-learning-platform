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