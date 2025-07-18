"""
Mock Agent Server
Simple implementation for testing the orchestrator without requiring full agent infrastructure
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockAgentResponse(BaseModel):
    success: bool = True
    result: Dict[str, Any] = {}
    processing_time: float = 0.0
    agent_name: str
    timestamp: str


def create_mock_agent_app(agent_name: str, port: int):
    """Create a mock agent FastAPI application."""
    
    app = FastAPI(
        title=f"Mock {agent_name} Agent",
        description=f"Mock implementation of {agent_name} for testing",
        version="1.0.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "agent_name": agent_name,
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "port": port
        }
    
    @app.get("/capabilities")
    async def get_capabilities():
        capabilities = {
            "Course Planning Specialist": {
                "agent_name": "Course Planning Specialist",
                "capabilities": [
                    "SOP document analysis",
                    "Curriculum structure generation",
                    "Learning objective creation",
                    "CEFR level alignment",
                    "Module sequencing"
                ],
                "supported_formats": ["PDF", "DOCX", "TXT"],
                "max_document_size": "10MB",
                "processing_time": "30-60 seconds"
            },
            "Content Creator Agent": {
                "agent_name": "Content Creator Agent",
                "capabilities": [
                    "Lesson content generation",
                    "Exercise creation",
                    "Assessment development",
                    "Interactive content",
                    "Multimedia integration"
                ],
                "content_types": ["lessons", "exercises", "assessments", "multimedia"],
                "exercise_types": ["multiple-choice", "fill-in-blank", "role-play", "writing-task"],
                "processing_time": "60-120 seconds"
            },
            "Quality Assurance Agent": {
                "agent_name": "Quality Assurance Agent",
                "capabilities": [
                    "Content quality review",
                    "CEFR level validation",
                    "Linguistic accuracy check",
                    "Pedagogical effectiveness analysis",
                    "Cultural sensitivity review"
                ],
                "quality_criteria": ["accuracy", "effectiveness", "alignment", "sensitivity"],
                "scoring_system": "0-100 scale",
                "processing_time": "45-90 seconds"
            }
        }
        return capabilities.get(agent_name, {"agent_name": agent_name, "capabilities": []})
    
    if agent_name == "Course Planning Specialist":
        @app.post("/plan-course")
        async def plan_course(request: Dict[str, Any]):
            # Simulate processing time
            await asyncio.sleep(2)
            
            company_name = request.get("company_name", "Test Company")
            industry = request.get("industry", "Business")
            training_goals = request.get("training_goals", "Improve communication")
            current_level = request.get("current_english_level", "B1")
            
            mock_curriculum = {
                "title": f"English Communication Course for {company_name}",
                "description": f"Customized English training program for {industry} professionals",
                "cefr_level": current_level,
                "duration_weeks": request.get("duration_weeks", 8),
                "learning_objectives": [
                    f"Improve {industry.lower()}-specific communication skills",
                    "Enhance professional presentation abilities",
                    "Develop effective meeting participation skills",
                    "Master written communication in professional contexts"
                ],
                "modules": [
                    {
                        "id": 1,
                        "title": "Business Communication Fundamentals",
                        "description": "Core communication skills for professional environments",
                        "duration_hours": 8,
                        "learning_outcomes": [
                            "Use appropriate professional language",
                            "Understand formal vs informal communication",
                            "Apply email etiquette and structure"
                        ],
                        "vocabulary_themes": ["business_terminology", "professional_expressions"],
                        "grammar_focus": ["present_perfect", "modal_verbs", "reported_speech"]
                    },
                    {
                        "id": 2,
                        "title": f"{industry} Industry Communication",
                        "description": f"Specialized communication for {industry.lower()} professionals",
                        "duration_hours": 12,
                        "learning_outcomes": [
                            f"Use {industry.lower()}-specific terminology effectively",
                            "Participate in industry-relevant discussions",
                            "Present technical information clearly"
                        ],
                        "vocabulary_themes": [f"{industry.lower()}_terminology", "technical_vocabulary"],
                        "grammar_focus": ["passive_voice", "conditionals", "complex_sentences"]
                    },
                    {
                        "id": 3,
                        "title": "Presentation and Meeting Skills",
                        "description": "Advanced communication for presentations and meetings",
                        "duration_hours": 8,
                        "learning_outcomes": [
                            "Deliver clear and engaging presentations",
                            "Participate effectively in meetings",
                            "Handle questions and feedback professionally"
                        ],
                        "vocabulary_themes": ["presentation_language", "meeting_phrases"],
                        "grammar_focus": ["future_forms", "opinion_expressions", "linking_words"]
                    }
                ],
                "total_hours": 28,
                "assessment_strategy": "Continuous assessment with final presentation project",
                "prerequisites": f"Minimum {current_level} English level",
                "created_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "curriculum": mock_curriculum,
                "agent_name": "Course Planning Specialist",
                "processing_time": 2.0,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    elif agent_name == "Content Creator Agent":
        @app.post("/create-lesson")
        async def create_lesson(request: Dict[str, Any]):
            await asyncio.sleep(1.5)
            
            lesson_title = request.get("lesson_title", "Sample Lesson")
            module_context = request.get("module_context", "")
            cefr_level = request.get("cefr_level", "B1")
            
            mock_lesson = {
                "lesson_id": f"lesson_{datetime.utcnow().timestamp()}",
                "title": lesson_title,
                "cefr_level": cefr_level,
                "duration_minutes": request.get("duration_minutes", 60),
                "objectives": [
                    "Understand key vocabulary and phrases",
                    "Practice target grammar structures",
                    "Apply knowledge in practical scenarios"
                ],
                "content_sections": [
                    {
                        "section": "warm_up",
                        "title": "Warm-up Activity",
                        "duration": 10,
                        "content": "Discussion questions to activate prior knowledge and introduce the topic"
                    },
                    {
                        "section": "vocabulary",
                        "title": "Vocabulary Introduction",
                        "duration": 15,
                        "content": "Key terms and expressions with examples and practice activities"
                    },
                    {
                        "section": "grammar",
                        "title": "Grammar Focus",
                        "duration": 20,
                        "content": "Target grammar structures with clear explanations and guided practice"
                    },
                    {
                        "section": "practice",
                        "title": "Communicative Practice",
                        "duration": 10,
                        "content": "Real-world application activities and role-plays"
                    },
                    {
                        "section": "wrap_up",
                        "title": "Wrap-up and Review",
                        "duration": 5,
                        "content": "Summary of key points and assignment of homework/follow-up tasks"
                    }
                ],
                "materials": ["presentation_slides", "handouts", "audio_files", "activity_sheets"],
                "homework": "Complete vocabulary exercises and prepare for next lesson",
                "created_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "content": mock_lesson,
                "agent_name": "Content Creator Agent",
                "processing_time": 1.5,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @app.post("/create-exercises")
        async def create_exercises(request: Dict[str, Any]):
            await asyncio.sleep(1)
            
            exercise_types = request.get("exercise_types", ["multiple-choice", "fill-in-blank"])
            exercise_count = request.get("exercise_count", 4)
            
            mock_exercises = []
            for i in range(exercise_count):
                exercise_type = exercise_types[i % len(exercise_types)]
                mock_exercises.append({
                    "exercise_id": f"ex_{i+1}_{datetime.utcnow().timestamp()}",
                    "type": exercise_type,
                    "title": f"Exercise {i+1}: {exercise_type.replace('-', ' ').title()}",
                    "instructions": f"Complete this {exercise_type} exercise",
                    "difficulty": request.get("cefr_level", "B1"),
                    "estimated_time": 5,
                    "content": f"Sample {exercise_type} exercise content",
                    "answer_key": f"Sample answer for exercise {i+1}"
                })
            
            return {
                "success": True,
                "content": {
                    "exercises": mock_exercises,
                    "total_exercises": len(mock_exercises),
                    "estimated_completion_time": len(mock_exercises) * 5
                },
                "agent_name": "Content Creator Agent",
                "processing_time": 1.0,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @app.post("/create-assessment")
        async def create_assessment(request: Dict[str, Any]):
            await asyncio.sleep(1.2)
            
            assessment_type = request.get("assessment_type", "final")
            duration = request.get("duration_minutes", 60)
            
            mock_assessment = {
                "assessment_id": f"assess_{datetime.utcnow().timestamp()}",
                "type": assessment_type,
                "title": f"{assessment_type.title()} Assessment",
                "duration_minutes": duration,
                "total_points": 100,
                "sections": [
                    {
                        "section": "listening",
                        "title": "Listening Comprehension",
                        "points": 25,
                        "questions": 10
                    },
                    {
                        "section": "vocabulary",
                        "title": "Vocabulary and Grammar",
                        "points": 30,
                        "questions": 15
                    },
                    {
                        "section": "reading",
                        "title": "Reading Comprehension",
                        "points": 25,
                        "questions": 8
                    },
                    {
                        "section": "writing",
                        "title": "Written Communication",
                        "points": 20,
                        "questions": 2
                    }
                ],
                "pass_score": 70,
                "created_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "content": mock_assessment,
                "agent_name": "Content Creator Agent",
                "processing_time": 1.2,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    elif agent_name == "Quality Assurance Agent":
        @app.post("/review-content")
        async def review_content(request: Dict[str, Any]):
            await asyncio.sleep(2.5)
            
            content_data = request.get("content_data", {})
            review_criteria = request.get("review_criteria", ["accuracy", "effectiveness"])
            
            # Simulate quality scoring
            scores = {
                "linguistic_accuracy": 88,
                "cefr_alignment": 92,
                "pedagogical_effectiveness": 85,
                "cultural_sensitivity": 90,
                "overall_score": 89
            }
            
            mock_qa_result = {
                "content_id": request.get("content_id", "unknown"),
                "review_date": datetime.utcnow().isoformat(),
                "reviewer": "Quality Assurance Agent",
                "scores": scores,
                "overall_score": scores["overall_score"],
                "approved_for_release": scores["overall_score"] >= 80,
                "review_criteria": review_criteria,
                "feedback": {
                    "strengths": [
                        "Clear learning objectives",
                        "Appropriate CEFR level alignment",
                        "Good variety of exercise types"
                    ],
                    "improvements": [
                        "Consider adding more interactive elements",
                        "Include cultural context examples",
                        "Expand vocabulary practice activities"
                    ]
                },
                "issues_found": [
                    {
                        "severity": "minor",
                        "category": "content",
                        "description": "Some vocabulary could be more industry-specific",
                        "suggested_fix": "Add more technical terminology relevant to the industry"
                    }
                ],
                "certification": {
                    "quality_assured": True,
                    "certification_level": "Production Ready",
                    "valid_until": "2025-12-31"
                }
            }
            
            return {
                "success": True,
                "result": mock_qa_result,
                "agent_name": "Quality Assurance Agent",
                "processing_time": 2.5,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    return app


def start_mock_agents():
    """Start all mock agent servers."""
    
    agents = [
        ("Course Planning Specialist", 8101),
        ("Content Creator Agent", 8102),
        ("Quality Assurance Agent", 8103)
    ]
    
    async def run_agent(agent_name: str, port: int):
        app = create_mock_agent_app(agent_name, port)
        config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    
    async def run_all_agents():
        tasks = []
        for agent_name, port in agents:
            logger.info(f"Starting mock {agent_name} on port {port}")
            task = asyncio.create_task(run_agent(agent_name, port))
            tasks.append(task)
        
        # Run all agents concurrently
        await asyncio.gather(*tasks)
    
    return asyncio.run(run_all_agents())


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Start specific agent
        agent_map = {
            "planner": ("Course Planning Specialist", 8101),
            "creator": ("Content Creator Agent", 8102), 
            "qa": ("Quality Assurance Agent", 8103)
        }
        
        agent_key = sys.argv[1]
        if agent_key in agent_map:
            agent_name, port = agent_map[agent_key]
            logger.info(f"Starting single mock agent: {agent_name} on port {port}")
            app = create_mock_agent_app(agent_name, port)
            uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
        else:
            print(f"Unknown agent: {agent_key}")
            print("Available agents: planner, creator, qa")
    else:
        # Start all agents
        logger.info("Starting all mock agents...")
        start_mock_agents()