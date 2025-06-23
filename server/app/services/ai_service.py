"""
AI Service for course generation and content creation.
Supports both OpenAI and Anthropic APIs.
"""

import os
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import logging

try:
    import openai
    from anthropic import Anthropic
    import tiktoken
except ImportError as e:
    logging.warning(f"AI dependencies not fully installed: {e}")
    openai = None
    Anthropic = None
    tiktoken = None

from app.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered content generation."""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.tokenizer = None
        
        # Initialize OpenAI if API key is available
        if settings.OPENAI_API_KEY and openai:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_client = openai
            if tiktoken:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Initialize Anthropic if API key is available
        if settings.ANTHROPIC_API_KEY and Anthropic:
            self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def is_available(self) -> bool:
        """Check if AI services are available."""
        return self.openai_client is not None or self.anthropic_client is not None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        return len(text.split()) * 1.3  # Rough estimation
    
    async def generate_content(
        self,
        prompt: str,
        model: str = "gpt-4o-mini",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate content using AI."""
        
        if not self.is_available():
            raise ValueError("No AI services configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        
        try:
            # Try OpenAI first
            if self.openai_client and model.startswith(("gpt-", "o1-")):
                return await self._generate_openai(prompt, model, max_tokens, temperature, system_prompt)
            
            # Try Anthropic
            elif self.anthropic_client and model.startswith("claude-"):
                return await self._generate_anthropic(prompt, model, max_tokens, temperature, system_prompt)
            
            # Fallback to available service
            elif self.openai_client:
                return await self._generate_openai(prompt, "gpt-4o-mini", max_tokens, temperature, system_prompt)
            
            elif self.anthropic_client:
                return await self._generate_anthropic(prompt, "claude-3-haiku-20240307", max_tokens, temperature, system_prompt)
            
            else:
                raise ValueError("No compatible AI service available")
                
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            raise
    
    async def _generate_openai(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> str:
        """Generate content using OpenAI."""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.openai_client.chat.completions.acreate(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content.strip()
    
    async def _generate_anthropic(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> str:
        """Generate content using Anthropic."""
        
        message = await self.anthropic_client.messages.acreate(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text.strip()
    
    async def generate_course_curriculum(
        self,
        company_name: str,
        industry: str,
        sop_content: str,
        cefr_level: str,
        duration_weeks: int = 8
    ) -> Dict[str, Any]:
        """Generate a complete course curriculum based on SOP content."""
        
        system_prompt = """You are an expert English language curriculum designer for corporate training. 
        Create comprehensive, industry-specific course curriculums that align with CEFR standards."""
        
        prompt = f"""
        Create a {duration_weeks}-week English language course curriculum for {company_name} in the {industry} industry.
        
        CEFR Level: {cefr_level}
        Company SOPs: {sop_content[:3000]}  # Truncate to avoid token limits
        
        Generate a structured curriculum with:
        1. Course title and description
        2. Learning objectives aligned with CEFR {cefr_level}
        3. {duration_weeks} weekly modules with titles and descriptions
        4. Key vocabulary themes for each module
        5. Grammar focus areas
        6. Assessment methods
        
        Format as JSON with this structure:
        {{
            "title": "Course title",
            "description": "Course description",
            "learning_objectives": ["objective1", "objective2", ...],
            "modules": [
                {{
                    "week": 1,
                    "title": "Module title",
                    "description": "Module description",
                    "vocabulary_themes": ["theme1", "theme2"],
                    "grammar_focus": ["grammar_point1", "grammar_point2"],
                    "duration_hours": 4
                }}
            ],
            "assessment_methods": ["method1", "method2"]
        }}
        """
        
        content = await self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=3000,
            temperature=0.3  # Lower temperature for structured output
        )
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback: extract JSON from response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(content[start:end])
            
            # If JSON parsing fails, return structured data
            return {
                "title": f"English for {company_name} - {cefr_level}",
                "description": "AI-generated corporate English training course",
                "error": "Failed to parse AI response as JSON",
                "raw_content": content
            }
    
    async def generate_lesson_content(
        self,
        lesson_title: str,
        module_context: str,
        vocabulary_themes: List[str],
        grammar_focus: List[str],
        cefr_level: str,
        duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """Generate detailed lesson content."""
        
        system_prompt = f"""You are an expert ESL lesson designer. Create engaging, practical lessons 
        for {cefr_level} level corporate English learners."""
        
        prompt = f"""
        Create a {duration_minutes}-minute lesson plan for: "{lesson_title}"
        
        Context: {module_context}
        Vocabulary themes: {', '.join(vocabulary_themes)}
        Grammar focus: {', '.join(grammar_focus)}
        CEFR Level: {cefr_level}
        
        Generate comprehensive lesson content with:
        1. Learning objectives (specific to this lesson)
        2. Warm-up activity (5-10 minutes)
        3. Vocabulary introduction (10-15 minutes)
        4. Grammar presentation (15-20 minutes)
        5. Practice activities (20-25 minutes)
        6. Production/speaking activity (10-15 minutes)
        7. Wrap-up and assessment (5 minutes)
        
        For each section, provide specific activities, examples, and materials needed.
        Include workplace scenarios relevant to the vocabulary themes.
        
        Format as JSON.
        """
        
        content = await self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2500,
            temperature=0.4
        )
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "lesson_title": lesson_title,
                "duration_minutes": duration_minutes,
                "content": content,
                "error": "Failed to parse lesson content as JSON"
            }
    
    async def generate_exercises(
        self,
        lesson_context: str,
        exercise_types: List[str],
        cefr_level: str,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate interactive exercises for a lesson."""
        
        system_prompt = f"""Create engaging, interactive exercises for {cefr_level} level English learners 
        in corporate settings. Focus on practical workplace applications."""
        
        prompt = f"""
        Create {count} exercises based on this lesson context:
        {lesson_context}
        
        Exercise types to include: {', '.join(exercise_types)}
        CEFR Level: {cefr_level}
        
        For each exercise, provide:
        1. Exercise type (multiple-choice, fill-in-blank, matching, drag-drop, etc.)
        2. Instructions
        3. Question/content
        4. Correct answers
        5. Feedback for correct/incorrect responses
        6. Points value
        
        Make exercises practical and workplace-relevant.
        Format as JSON array.
        """
        
        content = await self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000,
            temperature=0.5
        )
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Return fallback exercises
            return [
                {
                    "type": "multiple-choice",
                    "title": f"Exercise {i+1}",
                    "content": f"AI-generated exercise based on: {lesson_context[:100]}...",
                    "error": "Failed to parse exercise content"
                }
                for i in range(count)
            ]
    
    async def generate_assessment(
        self,
        course_context: str,
        assessment_type: str,
        cefr_level: str,
        duration_minutes: int = 30
    ) -> Dict[str, Any]:
        """Generate course assessments."""
        
        system_prompt = f"""Design comprehensive assessments for {cefr_level} level corporate English courses.
        Focus on practical skills evaluation in workplace contexts."""
        
        prompt = f"""
        Create a {duration_minutes}-minute {assessment_type} assessment for:
        {course_context}
        
        CEFR Level: {cefr_level}
        
        Include:
        1. Assessment objectives
        2. Instructions for learners
        3. Questions/tasks (mix of question types)
        4. Scoring rubric
        5. Time allocation per section
        6. Pass/fail criteria
        
        Focus on practical workplace English skills.
        Format as JSON.
        """
        
        content = await self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000,
            temperature=0.3
        )
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "type": assessment_type,
                "duration_minutes": duration_minutes,
                "content": content,
                "error": "Failed to parse assessment content"
            }

# Global instance
ai_service = AIService()