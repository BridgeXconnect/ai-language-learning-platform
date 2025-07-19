"""
Mock Agent Server for Development and Testing
Provides realistic mock responses for Course Planner, Content Creator, and Quality Assurance agents
"""

import asyncio
import logging
import random
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

logger = logging.getLogger(__name__)

# Pydantic models for requests and responses
class CoursePlanningRequest(BaseModel):
    course_request_id: str
    company_name: str
    industry: str
    training_goals: List[str]
    current_english_level: str
    duration_weeks: int = Field(default=8, ge=1, le=52)
    target_audience: str = "Professional staff"
    specific_needs: Optional[str] = None

class ContentCreationRequest(BaseModel):
    course_request_id: str
    curriculum: Dict[str, Any]
    company_name: str
    industry: str
    current_english_level: str

class QualityReviewRequest(BaseModel):
    course_request_id: str
    content: Dict[str, Any]
    company_name: str
    industry: str
    current_english_level: str

class HealthResponse(BaseModel):
    status: str
    agent_name: str
    version: str
    uptime: str
    capabilities: List[str]

class CoursePlanningResponse(BaseModel):
    success: bool
    curriculum: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float

class ContentCreationResponse(BaseModel):
    success: bool
    content: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float

class QualityReviewResponse(BaseModel):
    success: bool
    qa_report: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float

@dataclass
class MockAgentConfig:
    """Configuration for mock agent behavior."""
    agent_name: str
    agent_type: str
    response_delay_range: tuple = (1, 3)  # seconds
    success_rate: float = 0.95
    realistic_responses: bool = True

class MockAgentServer:
    """Mock agent server that provides realistic responses for development and testing."""
    
    def __init__(self, config: MockAgentConfig):
        self.config = config
        self.app = FastAPI(title=f"Mock {config.agent_name}", version="1.0.0")
        self.start_time = datetime.utcnow()
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self._register_routes()
        
        # Initialize mock data generators
        self._init_mock_data()
    
    def _register_routes(self):
        """Register FastAPI routes."""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            uptime = (datetime.utcnow() - self.start_time).total_seconds()
            return HealthResponse(
                status="healthy",
                agent_name=self.config.agent_name,
                version="1.0.0",
                uptime=f"{uptime:.2f}s",
                capabilities=self._get_capabilities()
            )
        
        @self.app.post("/plan_course")
        async def plan_course(request: CoursePlanningRequest, background_tasks: BackgroundTasks):
            """Mock course planning endpoint."""
            start_time = datetime.utcnow()
            
            try:
                # Simulate processing delay
                await asyncio.sleep(random.uniform(*self.config.response_delay_range))
                
                # Simulate occasional failures
                if random.random() > self.config.success_rate:
                    raise HTTPException(status_code=500, detail="Simulated agent failure")
                
                curriculum = self._generate_mock_curriculum(request)
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                
                return CoursePlanningResponse(
                    success=True,
                    curriculum=curriculum,
                    processing_time=processing_time
                )
                
            except Exception as e:
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                return CoursePlanningResponse(
                    success=False,
                    error=str(e),
                    processing_time=processing_time
                )
        
        @self.app.post("/create_content")
        async def create_content(request: ContentCreationRequest, background_tasks: BackgroundTasks):
            """Mock content creation endpoint."""
            start_time = datetime.utcnow()
            
            try:
                # Simulate processing delay
                await asyncio.sleep(random.uniform(*self.config.response_delay_range))
                
                # Simulate occasional failures
                if random.random() > self.config.success_rate:
                    raise HTTPException(status_code=500, detail="Simulated agent failure")
                
                content = self._generate_mock_content(request)
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                
                return ContentCreationResponse(
                    success=True,
                    content=content,
                    processing_time=processing_time
                )
                
            except Exception as e:
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                return ContentCreationResponse(
                    success=False,
                    error=str(e),
                    processing_time=processing_time
                )
        
        @self.app.post("/review_content")
        async def review_content(request: QualityReviewRequest, background_tasks: BackgroundTasks):
            """Mock quality review endpoint."""
            start_time = datetime.utcnow()
            
            try:
                # Simulate processing delay
                await asyncio.sleep(random.uniform(*self.config.response_delay_range))
                
                # Simulate occasional failures
                if random.random() > self.config.success_rate:
                    raise HTTPException(status_code=500, detail="Simulated agent failure")
                
                qa_report = self._generate_mock_qa_report(request)
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                
                return QualityReviewResponse(
                    success=True,
                    qa_report=qa_report,
                    processing_time=processing_time
                )
                
            except Exception as e:
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                return QualityReviewResponse(
                    success=False,
                    error=str(e),
                    processing_time=processing_time
                )
        
        @self.app.get("/capabilities")
        async def get_capabilities():
            """Get agent capabilities."""
            return {
                "agent_name": self.config.agent_name,
                "agent_type": self.config.agent_type,
                "capabilities": self._get_capabilities(),
                "version": "1.0.0"
            }
    
    def _get_capabilities(self) -> List[str]:
        """Get agent capabilities based on type."""
        capabilities_map = {
            "course_planner": [
                "curriculum_design",
                "learning_objective_definition",
                "module_structure_planning",
                "assessment_strategy_development",
                "cefr_level_alignment"
            ],
            "content_creator": [
                "lesson_content_generation",
                "exercise_creation",
                "assessment_material_development",
                "multimedia_content_integration",
                "interactive_activity_design"
            ],
            "quality_assurance": [
                "content_quality_review",
                "linguistic_accuracy_assessment",
                "pedagogical_effectiveness_evaluation",
                "cefr_level_validation",
                "cultural_sensitivity_review"
            ]
        }
        return capabilities_map.get(self.config.agent_type, ["basic_operations"])
    
    def _init_mock_data(self):
        """Initialize mock data generators."""
        
        self.vocabulary_themes = [
            "Business Communication", "Customer Service", "Project Management",
            "Sales and Marketing", "Technical Documentation", "Team Collaboration",
            "Presentations and Public Speaking", "Email and Written Communication",
            "Meeting Management", "Negotiation Skills"
        ]
        
        self.grammar_focus_areas = [
            "Present Simple vs Present Continuous", "Past Simple and Past Perfect",
            "Future Forms and Predictions", "Conditionals (Zero, First, Second)",
            "Modal Verbs for Business", "Passive Voice", "Reported Speech",
            "Relative Clauses", "Articles and Determiners", "Prepositions"
        ]
        
        self.exercise_types = [
            "Multiple Choice", "Fill in the Blanks", "Role Play", "Writing Tasks",
            "Listening Comprehension", "Speaking Practice", "Reading Comprehension",
            "Grammar Practice", "Vocabulary Building", "Case Studies"
        ]
    
    def _generate_mock_curriculum(self, request: CoursePlanningRequest) -> Dict[str, Any]:
        """Generate realistic mock curriculum."""
        
        # Determine number of modules based on duration
        num_modules = max(4, min(12, request.duration_weeks // 2))
        
        modules = []
        for i in range(num_modules):
            module = {
                "id": f"module_{i+1}",
                "title": f"Module {i+1}: {random.choice(self.vocabulary_themes)}",
                "description": f"Comprehensive training on {random.choice(self.vocabulary_themes).lower()} for {request.industry} professionals.",
                "duration_hours": random.randint(4, 8),
                "learning_objectives": [
                    f"Master key vocabulary for {random.choice(self.vocabulary_themes).lower()}",
                    f"Practice {random.choice(self.grammar_focus_areas).lower()}",
                    f"Develop confidence in {random.choice(['speaking', 'writing', 'listening', 'reading'])}"
                ],
                "vocabulary_themes": random.sample(self.vocabulary_themes, 2),
                "grammar_focus": [random.choice(self.grammar_focus_areas)],
                "lessons": [
                    {
                        "id": f"lesson_{i+1}_{j+1}",
                        "title": f"Lesson {j+1}: {random.choice(self.vocabulary_themes)}",
                        "duration_minutes": random.randint(45, 90),
                        "content_type": random.choice(["vocabulary", "grammar", "communication", "culture"])
                    }
                    for j in range(random.randint(3, 6))
                ]
            }
            modules.append(module)
        
        return {
            "course_id": f"course_{request.course_request_id}",
            "title": f"English for {request.industry} Professionals",
            "description": f"Comprehensive English language training program tailored for {request.company_name} in the {request.industry} industry.",
            "company_name": request.company_name,
            "industry": request.industry,
            "target_cefr_level": request.current_english_level,
            "duration_weeks": request.duration_weeks,
            "total_hours": sum(module["duration_hours"] for module in modules),
            "modules": modules,
            "learning_objectives": [
                f"Improve {request.current_english_level} level English proficiency",
                f"Develop industry-specific vocabulary for {request.industry}",
                f"Enhance professional communication skills",
                f"Build confidence in workplace English interactions"
            ],
            "assessment_strategy": {
                "formative_assessments": "Weekly progress checks and feedback",
                "summative_assessments": "End-of-module tests and final evaluation",
                "practical_assessments": "Role-play scenarios and real-world tasks"
            },
            "vocabulary_themes": random.sample(self.vocabulary_themes, 5),
            "grammar_focus": random.sample(self.grammar_focus_areas, 4),
            "created_at": datetime.utcnow().isoformat()
        }
    
    def _generate_mock_content(self, request: ContentCreationRequest) -> Dict[str, Any]:
        """Generate realistic mock content."""
        
        curriculum = request.curriculum
        modules = curriculum.get("modules", [])
        
        lessons = []
        exercises = []
        assessments = []
        
        for module in modules:
            # Generate lesson content
            for lesson in module.get("lessons", []):
                lesson_content = {
                    "id": lesson["id"],
                    "title": lesson["title"],
                    "module_id": module["id"],
                    "content": {
                        "introduction": f"Welcome to {lesson['title']}. This lesson focuses on {lesson.get('content_type', 'vocabulary')}.",
                        "main_content": f"Detailed content for {lesson['title']} including examples, explanations, and practice activities.",
                        "summary": f"Key takeaways from {lesson['title']}.",
                        "homework": f"Practice exercises for {lesson['title']}."
                    },
                    "duration_minutes": lesson.get("duration_minutes", 60),
                    "difficulty_level": request.current_english_level,
                    "learning_objectives": module.get("learning_objectives", [])
                }
                lessons.append(lesson_content)
            
            # Generate exercises
            module_exercises = [
                {
                    "id": f"exercise_{module['id']}_{i+1}",
                    "module_id": module["id"],
                    "type": random.choice(self.exercise_types),
                    "title": f"{random.choice(self.exercise_types)} Exercise",
                    "description": f"Practice exercise for {module['title']}",
                    "content": f"Exercise content for {module['title']}",
                    "difficulty": request.current_english_level,
                    "estimated_time_minutes": random.randint(10, 30)
                }
                for i in range(random.randint(2, 4))
            ]
            exercises.extend(module_exercises)
        
        # Generate assessments
        assessments = [
            {
                "id": f"assessment_{i+1}",
                "type": "module_test",
                "title": f"Module {i+1} Assessment",
                "description": f"Comprehensive assessment for Module {i+1}",
                "questions": [
                    {
                        "id": f"q_{i+1}_{j+1}",
                        "type": random.choice(["multiple_choice", "fill_blank", "essay"]),
                        "question": f"Sample question {j+1} for Module {i+1}",
                        "options": ["Option A", "Option B", "Option C", "Option D"] if random.choice(["multiple_choice", "fill_blank", "essay"]) == "multiple_choice" else None,
                        "correct_answer": "Option A" if random.choice(["multiple_choice", "fill_blank", "essay"]) == "multiple_choice" else None,
                        "points": random.randint(1, 5)
                    }
                    for j in range(random.randint(5, 10))
                ],
                "total_points": 50,
                "time_limit_minutes": 60
            }
            for i in range(len(modules))
        ]
        
        return {
            "course_id": curriculum.get("course_id"),
            "company_name": request.company_name,
            "industry": request.industry,
            "lessons": lessons,
            "exercises": exercises,
            "assessments": assessments,
            "supplementary_materials": {
                "vocabulary_lists": [f"Vocabulary list for {theme}" for theme in curriculum.get("vocabulary_themes", [])],
                "grammar_guides": [f"Grammar guide for {focus}" for focus in curriculum.get("grammar_focus", [])],
                "practice_activities": ["Role-play scenarios", "Case studies", "Group discussions"]
            },
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "total_lessons": len(lessons),
                "total_exercises": len(exercises),
                "total_assessments": len(assessments),
                "target_level": request.current_english_level
            }
        }
    
    def _generate_mock_qa_report(self, request: QualityReviewRequest) -> Dict[str, Any]:
        """Generate realistic mock QA report."""
        
        content = request.content
        lessons = content.get("lessons", [])
        exercises = content.get("exercises", [])
        assessments = content.get("assessments", [])
        
        # Calculate quality scores
        linguistic_score = random.randint(85, 98)
        pedagogical_score = random.randint(80, 95)
        cefr_alignment_score = random.randint(85, 100)
        cultural_sensitivity_score = random.randint(90, 100)
        
        overall_score = (linguistic_score + pedagogical_score + cefr_alignment_score + cultural_sensitivity_score) // 4
        
        # Generate issues (if any)
        issues = []
        if overall_score < 90:
            issues = [
                {
                    "type": "linguistic",
                    "severity": "minor",
                    "description": "Minor grammatical inconsistencies found in lesson content",
                    "recommendation": "Review and standardize grammar usage across lessons"
                }
            ]
        
        if overall_score < 85:
            issues.append({
                "type": "pedagogical",
                "severity": "moderate",
                "description": "Some exercises may be too challenging for target level",
                "recommendation": "Adjust difficulty levels to better match CEFR standards"
            })
        
        return {
            "course_id": content.get("course_id"),
            "company_name": request.company_name,
            "review_date": datetime.utcnow().isoformat(),
            "overall_score": overall_score,
            "quality_breakdown": {
                "linguistic_accuracy": linguistic_score,
                "pedagogical_effectiveness": pedagogical_score,
                "cefr_level_alignment": cefr_alignment_score,
                "cultural_sensitivity": cultural_sensitivity_score
            },
            "content_analysis": {
                "lessons_reviewed": len(lessons),
                "exercises_reviewed": len(exercises),
                "assessments_reviewed": len(assessments),
                "total_content_items": len(lessons) + len(exercises) + len(assessments)
            },
            "issues_found": issues,
            "strengths": [
                "Clear learning objectives",
                "Appropriate difficulty progression",
                "Engaging exercise variety",
                "Relevant industry context"
            ],
            "recommendations": [
                "Consider adding more interactive elements",
                "Include additional cultural context",
                "Provide more detailed feedback mechanisms"
            ],
            "approved_for_release": overall_score >= 80,
            "requires_revision": len(issues) > 0,
            "revision_priority": "low" if overall_score >= 90 else "medium" if overall_score >= 80 else "high"
        }
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the mock agent server."""
        logger.info(f"Starting mock {self.config.agent_name} server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port, log_level="info")

def create_mock_course_planner():
    """Create a mock course planner server."""
    config = MockAgentConfig(
        agent_name="Course Planning Specialist",
        agent_type="course_planner",
        response_delay_range=(2, 5),
        success_rate=0.98
    )
    return MockAgentServer(config)

def create_mock_content_creator():
    """Create a mock content creator server."""
    config = MockAgentConfig(
        agent_name="Content Creator Agent",
        agent_type="content_creator",
        response_delay_range=(3, 8),
        success_rate=0.95
    )
    return MockAgentServer(config)

def create_mock_quality_assurance():
    """Create a mock quality assurance server."""
    config = MockAgentConfig(
        agent_name="Quality Assurance Agent",
        agent_type="quality_assurance",
        response_delay_range=(1, 3),
        success_rate=0.99
    )
    return MockAgentServer(config)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python mock_agent_server.py <agent_type> [port]")
        print("Agent types: course_planner, content_creator, quality_assurance")
        sys.exit(1)
    
    agent_type = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    
    agent_creators = {
        "course_planner": create_mock_course_planner,
        "content_creator": create_mock_content_creator,
        "quality_assurance": create_mock_quality_assurance
    }
    
    if agent_type not in agent_creators:
        print(f"Unknown agent type: {agent_type}")
        sys.exit(1)
    
    server = agent_creators[agent_type]()
    server.run(port=port)