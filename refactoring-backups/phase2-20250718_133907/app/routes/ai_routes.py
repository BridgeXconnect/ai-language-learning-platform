"""
API routes for AI-powered course generation and content creation.
"""

import asyncio
import time
import logging
from typing import List, Dict, Any
import tempfile
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.ai_service import ai_service
from app.services.rag_service import rag_service
from app.services.document_service import document_processor
from app.services.course_generation_service import course_generation_service
from app.models.user import User
from app.models.sales import CourseRequest, SOPDocument
from app.schemas.ai import (
    CourseGenerationRequest, CourseGenerationResponse,
    RAGSearchRequest, RAGSearchResponse,
    ContentGenerationRequest, ContentGenerationResponse,
    CourseAnalysisRequest, CourseAnalysisResponse,
    AIServiceStatus, ComponentRegenerationRequest, ComponentRegenerationResponse,
    VocabularyExtractionRequest, VocabularyExtractionResponse,
    LessonPlanRequest, LessonPlanResponse,
    DocumentProcessingRequest, DocumentProcessingResponse
)

router = APIRouter(prefix="/ai", tags=["AI Services"])
logger = logging.getLogger(__name__)

@router.get("/status", response_model=AIServiceStatus)
async def get_ai_service_status():
    """Get the status of all AI services."""
    
    return AIServiceStatus(
        ai_service_available=ai_service.is_available(),
        rag_service_available=rag_service.is_available(),
        document_processor_available=True,  # Always available
        openai_configured=ai_service.openai_client is not None,
        anthropic_configured=ai_service.anthropic_client is not None,
        vector_store_stats=rag_service.vector_store.get_stats() if rag_service.is_available() else {}
    )

@router.post("/generate-course", response_model=CourseGenerationResponse)
async def generate_course(
    request: CourseGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a complete course from a course request using AI (with agent support)."""
    
    # Verify user has permission to generate courses
    if not any(role.name in ["admin", "sales", "course_manager"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Check if course request exists
    course_request = db.query(CourseRequest).filter(
        CourseRequest.id == request.course_request_id
    ).first()
    
    if not course_request:
        raise HTTPException(status_code=404, detail="Course request not found")
    
    # Check agent preference and availability
    use_agents = getattr(request, 'use_agents', True)  # Default to agents if available
    agents_enabled = os.getenv("AGENTS_ENABLED", "true").lower() == "true"
    
    if use_agents and agents_enabled:
        try:
            # Try agent-based generation first
            from app.routes.agent_routes import call_agent
            
            agent_request = {
                "course_request_id": course_request.id,
                "company_name": course_request.company_name,
                "industry": course_request.industry or "General Business",
                "training_goals": course_request.training_goals or "Improve English communication skills",
                "current_english_level": course_request.current_english_level or "B1",
                "duration_weeks": request.duration_weeks,
                "target_audience": course_request.target_audience or "Professional staff",
                "specific_needs": course_request.specific_needs
            }
            
            logger.info(f"Attempting agent-based course generation for request {request.course_request_id}")
            agent_result = await call_agent("orchestrator", "/orchestrate-course", agent_request)
            
            if agent_result.get("success", False):
                workflow_result = agent_result.get("workflow_result", {})
                
                if workflow_result.get("status") == "completed":
                    logger.info(f"Agent-based generation successful for request {request.course_request_id}")
                    
                    return CourseGenerationResponse(
                        success=True,
                        course_id=workflow_result.get("course_request_id"),
                        message="Course generated successfully using multi-agent system",
                        generation_method="multi_agent",
                        workflow_id=workflow_result.get("workflow_id"),
                        quality_score=workflow_result.get("quality_score"),
                        processing_time_seconds=agent_result.get("processing_time_seconds"),
                        modules_created=len(workflow_result.get("planning_result", {}).get("modules", [])),
                        indexed_sources=0  # Will be updated based on agent result
                    )
            
            # Agent generation failed, fall back to traditional
            logger.warning(f"Agent generation failed, falling back to traditional AI: {agent_result.get('error', 'Unknown error')}")
            
        except Exception as e:
            logger.warning(f"Agent generation failed with exception, falling back to traditional AI: {e}")
    
    # Traditional AI generation (fallback or by choice)
    if not ai_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="AI services not available. Please configure OPENAI_API_KEY or ANTHROPIC_API_KEY"
        )
    
    start_time = time.time()
    
    try:
        logger.info(f"Using traditional AI generation for request {request.course_request_id}")
        
        # Generate course using traditional service
        result = await course_generation_service.generate_course_from_request(
            course_request_id=request.course_request_id,
            db=db,
            generation_config={
                "duration_weeks": request.duration_weeks,
                "lessons_per_week": request.lessons_per_week,
                "exercise_count_per_lesson": request.exercise_count_per_lesson,
                "include_assessments": request.include_assessments,
                "ai_model": request.ai_model,
                "temperature": request.temperature,
                "use_agents": False  # Explicitly disable agents for traditional path
            }
        )
        
        generation_time = time.time() - start_time
        
        # Get course details for response
        from app.models.course import Course, Module, Lesson, Exercise, Assessment
        course = db.query(Course).filter(Course.id == result["course_id"]).first()
        
        modules_count = db.query(Module).filter(Module.course_id == course.id).count()
        lessons_count = db.query(Lesson).join(Module).filter(Module.course_id == course.id).count()
        exercises_count = db.query(Exercise).join(Lesson).join(Module).filter(Module.course_id == course.id).count()
        assessments_count = db.query(Assessment).filter(Assessment.course_id == course.id).count()
        
        return CourseGenerationResponse(
            success=True,
            course_id=course.id,
            course_title=course.title,
            modules_created=modules_count,
            lessons_created=lessons_count,
            exercises_created=exercises_count,
            assessments_created=assessments_count,
            indexed_sources=result.get("indexed_sources", 0),
            generation_time_seconds=generation_time
        )
        
    except Exception as e:
        logger.error(f"Course generation failed: {e}")
        return CourseGenerationResponse(
            success=False,
            generation_time_seconds=time.time() - start_time,
            error_message=str(e)
        )

@router.get("/generation-status/{course_request_id}")
async def get_generation_status(
    course_request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the status of course generation for a request."""
    
    status = await course_generation_service.get_generation_status(course_request_id, db)
    return status

@router.post("/search-content", response_model=RAGSearchResponse)
async def search_content(
    request: RAGSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Search for relevant content in indexed documents using RAG."""
    
    if not rag_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="RAG service not available. Please install required dependencies."
        )
    
    start_time = time.time()
    
    try:
        results = await rag_service.search_relevant_content(
            query=request.query,
            source_ids=request.source_ids,
            max_results=request.max_results,
            min_score=request.min_score
        )
        
        search_time = time.time() - start_time
        
        return RAGSearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            search_time_seconds=search_time
        )
        
    except Exception as e:
        logger.error(f"Content search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-document", response_model=DocumentProcessingResponse)
async def process_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Process and index a document for RAG."""
    
    # Check file type
    if not document_processor.is_supported_format(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported: {document_processor.supported_formats}"
        )
    
    start_time = time.time()
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Process document
        doc_result = await document_processor.process_file(file.filename, file_content)
        
        # Index with RAG if available
        chunks_created = 0
        if rag_service.is_available():
            index_result = await rag_service.index_document(
                file_path=file.filename,
                file_content=file_content,
                source_metadata={
                    "uploaded_by": current_user.id,
                    "uploaded_at": time.time()
                }
            )
            chunks_created = index_result['chunks_indexed']
        
        processing_time = time.time() - start_time
        
        return DocumentProcessingResponse(
            success=True,
            file_name=file.filename,
            word_count=doc_result['word_count'],
            char_count=doc_result['char_count'],
            chunks_created=chunks_created,
            key_terms=await document_processor.extract_key_terms(doc_result['text'], max_terms=10),
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        return DocumentProcessingResponse(
            success=False,
            file_name=file.filename,
            word_count=0,
            char_count=0,
            chunks_created=0,
            key_terms=[],
            processing_time_seconds=time.time() - start_time,
            error_message=str(e)
        )

@router.post("/generate-content", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate specific content using AI."""
    
    if not ai_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="AI services not available"
        )
    
    start_time = time.time()
    
    try:
        if request.content_type == "curriculum":
            content = await ai_service.generate_course_curriculum(
                company_name=request.context.get("company_name", "Company"),
                industry=request.context.get("industry", "General"),
                sop_content=request.context.get("sop_content", ""),
                cefr_level=request.context.get("cefr_level", "B1"),
                duration_weeks=request.parameters.get("duration_weeks", 8)
            )
        
        elif request.content_type == "lesson":
            content = await ai_service.generate_lesson_content(
                lesson_title=request.context.get("lesson_title", "Lesson"),
                module_context=request.context.get("module_context", ""),
                vocabulary_themes=request.context.get("vocabulary_themes", []),
                grammar_focus=request.context.get("grammar_focus", []),
                cefr_level=request.context.get("cefr_level", "B1"),
                duration_minutes=request.parameters.get("duration_minutes", 60)
            )
        
        elif request.content_type == "exercise":
            content = await ai_service.generate_exercises(
                lesson_context=request.context.get("lesson_context", ""),
                exercise_types=request.context.get("exercise_types", ["multiple-choice"]),
                cefr_level=request.context.get("cefr_level", "B1"),
                count=request.parameters.get("count", 5)
            )
        
        elif request.content_type == "assessment":
            content = await ai_service.generate_assessment(
                course_context=request.context.get("course_context", ""),
                assessment_type=request.context.get("assessment_type", "quiz"),
                cefr_level=request.context.get("cefr_level", "B1"),
                duration_minutes=request.parameters.get("duration_minutes", 30)
            )
        
        else:
            raise ValueError(f"Unsupported content type: {request.content_type}")
        
        generation_time = time.time() - start_time
        
        return ContentGenerationResponse(
            success=True,
            content_type=request.content_type,
            content=content,
            generation_time_seconds=generation_time
        )
        
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        return ContentGenerationResponse(
            success=False,
            content_type=request.content_type,
            content={},
            generation_time_seconds=time.time() - start_time,
            error_message=str(e)
        )

@router.post("/extract-vocabulary", response_model=VocabularyExtractionResponse)
async def extract_vocabulary(
    request: VocabularyExtractionRequest,
    current_user: User = Depends(get_current_user)
):
    """Extract vocabulary terms from text content."""
    
    start_time = time.time()
    
    try:
        key_terms = await document_processor.extract_key_terms(
            text=request.text,
            max_terms=request.max_terms
        )
        
        # Filter terms appropriate for CEFR level (basic implementation)
        filtered_terms = []
        for term in key_terms:
            # Simple filtering based on word length and complexity
            # In production, you'd use a CEFR word list
            if request.cefr_level in ["A1", "A2"]:
                if len(term["term"]) <= 8 and term["type"] == "word":
                    filtered_terms.append(term)
            elif request.cefr_level in ["B1", "B2"]:
                if len(term["term"]) <= 12:
                    filtered_terms.append(term)
            else:  # C1, C2
                filtered_terms.append(term)
        
        processing_time = time.time() - start_time
        
        return VocabularyExtractionResponse(
            cefr_level=request.cefr_level,
            vocabulary_terms=filtered_terms,
            total_terms=len(filtered_terms),
            phrases_included=request.include_phrases,
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        logger.error(f"Vocabulary extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-lesson-plan", response_model=LessonPlanResponse)
async def generate_lesson_plan(
    request: LessonPlanRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate a detailed lesson plan."""
    
    if not ai_service.is_available():
        raise HTTPException(status_code=503, detail="AI services not available")
    
    try:
        lesson_content = await ai_service.generate_lesson_content(
            lesson_title=request.lesson_title,
            module_context=request.module_context,
            vocabulary_themes=request.vocabulary_themes,
            grammar_focus=request.grammar_focus,
            cefr_level=request.cefr_level,
            duration_minutes=request.duration_minutes
        )
        
        return LessonPlanResponse(
            lesson_title=request.lesson_title,
            duration_minutes=request.duration_minutes,
            lesson_plan=lesson_content,
            activities=lesson_content.get("activities", []),
            materials_needed=lesson_content.get("materials_needed", []),
            learning_objectives=lesson_content.get("learning_objectives", []),
            assessment_criteria=lesson_content.get("assessment_criteria", [])
        )
        
    except Exception as e:
        logger.error(f"Lesson plan generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/regenerate-component", response_model=ComponentRegenerationResponse)
async def regenerate_component(
    request: ComponentRegenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate a specific course component."""
    
    # Verify user has permission
    if not any(role.name in ["admin", "course_manager"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        result = await course_generation_service.regenerate_course_component(
            course_id=request.course_id,
            component_type=request.component_type,
            component_id=request.component_id,
            config=request.config,
            db=db
        )
        
        return ComponentRegenerationResponse(
            success=result["success"],
            component_type=request.component_type,
            component_id=request.component_id,
            regenerated_at=datetime.utcnow(),
            changes_made=result.get("changes_made", [])
        )
        
    except Exception as e:
        logger.error(f"Component regeneration failed: {e}")
        return ComponentRegenerationResponse(
            success=False,
            component_type=request.component_type,
            component_id=request.component_id,
            regenerated_at=datetime.utcnow(),
            changes_made=[],
            error_message=str(e)
        )

@router.get("/indexed-sources")
async def get_indexed_sources(
    current_user: User = Depends(get_current_user)
):
    """Get information about indexed document sources."""
    
    if not rag_service.is_available():
        raise HTTPException(status_code=503, detail="RAG service not available")
    
    return rag_service.get_indexed_sources()

@router.delete("/indexed-sources/{source_id}")
async def remove_indexed_source(
    source_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove a document source from the index."""
    
    if not any(role.name in ["admin", "course_manager"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    if not rag_service.is_available():
        raise HTTPException(status_code=503, detail="RAG service not available")
    
    success = rag_service.remove_source(source_id)
    
    if success:
        return {"success": True, "message": f"Source {source_id} removed"}
    else:
        raise HTTPException(status_code=404, detail="Source not found")

@router.post("/clear-rag-index")
async def clear_rag_index(
    current_user: User = Depends(get_current_user)
):
    """Clear all RAG indexed content."""
    
    if not any(role.name in ["admin"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not rag_service.is_available():
        raise HTTPException(status_code=503, detail="RAG service not available")
    
    rag_service.clear_all()
    return {"success": True, "message": "RAG index cleared"}