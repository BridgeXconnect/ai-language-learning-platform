"""
Tools for Course Planning Agent
Implements specialized tools for SOP analysis, CEFR mapping, and curriculum generation
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

# Database and external service imports
import asyncpg
from supabase import create_client, Client

# AI and document processing
import openai
from sentence_transformers import SentenceTransformer
import PyPDF2
import docx
import pandas as pd

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Shared database connection for all tools."""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase: Optional[Client] = None
        
        # Skip actual connection for mock/test environments
        if (self.supabase_url and self.supabase_key and 
            not self.supabase_url.startswith('https://mock-') and
            not self.supabase_key.startswith('mock-')):
            try:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
            except Exception as e:
                logger.warning(f"Failed to connect to Supabase: {e}")
        else:
            logger.info("Using mock database connection for testing")
    
    def is_connected(self) -> bool:
        return self.supabase is not None

# Global database connection
db_connection = DatabaseConnection()

# Global tool instances
rag_context_retriever = RAGContextRetriever()
performance_metrics = PerformanceMetrics()

class SOPDocumentAnalyzer:
    """Analyzes SOP documents to extract key business processes and vocabulary."""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def analyze_documents(self, course_request_id: int) -> Dict[str, Any]:
        """Analyze all SOP documents for a course request."""
        
        try:
            # Get SOP documents from database
            sop_docs = await self._get_sop_documents(course_request_id)
            
            if not sop_docs:
                logger.warning(f"No SOP documents found for course request {course_request_id}")
                return {
                    "documents_analyzed": 0,
                    "key_processes": [],
                    "vocabulary_themes": [],
                    "communication_scenarios": [],
                    "analysis_status": "no_documents"
                }
            
            # Process each document
            analysis_results = []
            for doc in sop_docs:
                doc_analysis = await self._analyze_single_document(doc)
                analysis_results.append(doc_analysis)
            
            # Consolidate results
            consolidated = await self._consolidate_analyses(analysis_results)
            
            logger.info(f"Analyzed {len(sop_docs)} SOP documents for course request {course_request_id}")
            return consolidated
            
        except Exception as e:
            logger.error(f"SOP analysis failed: {e}")
            return {
                "documents_analyzed": 0,
                "error": str(e),
                "analysis_status": "failed"
            }
    
    async def _get_sop_documents(self, course_request_id: int) -> List[Dict[str, Any]]:
        """Retrieve SOP documents from database."""
        
        if not db_connection.is_connected():
            return []
        
        try:
            response = db_connection.supabase.table('sop_documents').select('*').eq(
                'course_request_id', course_request_id
            ).eq('processing_status', 'completed').execute()
            
            return response.data
        except Exception as e:
            logger.error(f"Failed to retrieve SOP documents: {e}")
            return []
    
    async def _analyze_single_document(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single SOP document."""
        
        try:
            # Extract text content
            content = await self._extract_document_content(doc['file_path'])
            
            if not content:
                return {"error": "Failed to extract content", "document_id": doc['id']}
            
            # Use AI to analyze content
            analysis_prompt = f"""
            Analyze this Standard Operating Procedure document and extract:
            
            1. Key business processes and workflows
            2. Important vocabulary and terminology
            3. Common communication scenarios
            4. Required language skills (reading, writing, speaking, listening)
            5. Complexity level of language used
            
            Document content:
            {content[:4000]}  # Truncate to avoid token limits
            
            Return analysis in JSON format:
            {{
                "key_processes": ["process1", "process2"],
                "vocabulary_themes": ["theme1", "theme2"],
                "communication_scenarios": ["scenario1", "scenario2"],
                "language_skills_required": ["skill1", "skill2"],
                "complexity_level": "intermediate|advanced|basic",
                "industry_specific_terms": ["term1", "term2"]
            }}
            """
            
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in business process analysis and language learning curriculum design."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            # Parse AI response
            ai_analysis = json.loads(response.choices[0].message.content)
            
            return {
                "document_id": doc['id'],
                "file_path": doc['file_path'],
                "analysis": ai_analysis,
                "content_length": len(content),
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze document {doc['id']}: {e}")
            return {
                "document_id": doc['id'],
                "error": str(e)
            }
    
    async def _extract_document_content(self, file_path: str) -> str:
        """Extract text content from various document formats."""
        
        try:
            if not os.path.exists(file_path):
                return ""
            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return self._extract_pdf_content(file_path)
            elif file_ext in ['.docx', '.doc']:
                return self._extract_docx_content(file_path)
            elif file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"Unsupported file format: {file_ext}")
                return ""
                
        except Exception as e:
            logger.error(f"Content extraction failed for {file_path}: {e}")
            return ""
    
    def _extract_pdf_content(self, file_path: str) -> str:
        """Extract text from PDF files."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
                return content
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return ""
    
    def _extract_docx_content(self, file_path: str) -> str:
        """Extract text from Word documents."""
        try:
            doc = docx.Document(file_path)
            content = ""
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
            return content
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            return ""
    
    async def _consolidate_analyses(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolidate multiple document analyses into a unified result."""
        
        # Filter successful analyses
        successful_analyses = [a for a in analyses if 'analysis' in a]
        
        if not successful_analyses:
            return {
                "documents_analyzed": len(analyses),
                "key_processes": [],
                "vocabulary_themes": [],
                "communication_scenarios": [],
                "analysis_status": "all_failed"
            }
        
        # Consolidate results
        all_processes = []
        all_vocabulary = []
        all_scenarios = []
        all_skills = []
        all_terms = []
        
        for analysis in successful_analyses:
            data = analysis['analysis']
            all_processes.extend(data.get('key_processes', []))
            all_vocabulary.extend(data.get('vocabulary_themes', []))
            all_scenarios.extend(data.get('communication_scenarios', []))
            all_skills.extend(data.get('language_skills_required', []))
            all_terms.extend(data.get('industry_specific_terms', []))
        
        # Remove duplicates and prioritize
        return {
            "documents_analyzed": len(successful_analyses),
            "key_processes": list(set(all_processes)),
            "vocabulary_themes": list(set(all_vocabulary)),
            "communication_scenarios": list(set(all_scenarios)),
            "language_skills_required": list(set(all_skills)),
            "industry_specific_terms": list(set(all_terms)),
            "analysis_status": "completed",
            "complexity_levels": [a['analysis'].get('complexity_level', 'intermediate') 
                                for a in successful_analyses]
        }

class CEFRLevelMapper:
    """Maps content complexity to appropriate CEFR levels."""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.cefr_descriptors = self._load_cefr_descriptors()
    
    def _load_cefr_descriptors(self) -> Dict[str, Dict[str, str]]:
        """Load CEFR level descriptors for accurate mapping."""
        return {
            "A1": {
                "vocabulary": "Basic everyday expressions and very basic phrases",
                "grammar": "Simple present, basic word order, limited vocabulary",
                "communication": "Simple interactions with help from others"
            },
            "A2": {
                "vocabulary": "Frequently used expressions, basic personal and family information",
                "grammar": "Simple past, future with going to, basic comparisons",
                "communication": "Direct exchange of information on familiar topics"
            },
            "B1": {
                "vocabulary": "Main points on familiar work, school, leisure topics",
                "grammar": "Present perfect, conditionals, passive voice basics",
                "communication": "Deal with most situations while traveling, describe experiences"
            },
            "B2": {
                "vocabulary": "Complex text on concrete and abstract topics",
                "grammar": "Advanced conditionals, reported speech, complex sentence structures",
                "communication": "Interact with fluency, argue a viewpoint on topical issues"
            },
            "C1": {
                "vocabulary": "Wide range of demanding, longer texts with implicit meaning",
                "grammar": "Full range of grammar structures used accurately",
                "communication": "Express fluently without obvious searching for expressions"
            },
            "C2": {
                "vocabulary": "Virtually everything heard or read with ease",
                "grammar": "All grammar structures used naturally and accurately",
                "communication": "Express precisely, distinguishing finer shades of meaning"
            }
        }
    
    async def map_content_level(self, content: Dict[str, Any], target_level: str) -> Dict[str, Any]:
        """Map content complexity to CEFR levels."""
        
        try:
            mapping_prompt = f"""
            Analyze the following content and map it to appropriate CEFR levels (A1-C2).
            Target level for this course: {target_level}
            
            Content to analyze:
            - Key processes: {content.get('key_processes', [])}
            - Vocabulary themes: {content.get('vocabulary_themes', [])}
            - Communication scenarios: {content.get('communication_scenarios', [])}
            - Industry terms: {content.get('industry_specific_terms', [])}
            
            CEFR Descriptors:
            {json.dumps(self.cefr_descriptors, indent=2)}
            
            Provide mapping for:
            1. Which content is appropriate for each CEFR level
            2. How to adapt content for the target level
            3. Progression pathway from current to target level
            4. Skills emphasis for each level
            
            Return as JSON:
            {{
                "level_mapping": {{
                    "A1": {{"vocabulary": [], "scenarios": [], "grammar_focus": []}},
                    "A2": {{"vocabulary": [], "scenarios": [], "grammar_focus": []}},
                    // ... for all levels
                }},
                "target_level_content": {{
                    "appropriate_vocabulary": [],
                    "suitable_scenarios": [],
                    "recommended_adaptations": []
                }},
                "progression_pathway": []
            }}
            """
            
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a CEFR expert specializing in content level mapping for language learning."},
                    {"role": "user", "content": mapping_prompt}
                ],
                max_tokens=2000,
                temperature=0.2
            )
            
            mapping_result = json.loads(response.choices[0].message.content)
            
            return {
                "target_level": target_level,
                "mapping_result": mapping_result,
                "content_analysis": content,
                "mapped_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"CEFR mapping failed: {e}")
            return {
                "target_level": target_level,
                "error": str(e),
                "fallback_mapping": self._create_fallback_mapping(content, target_level)
            }
    
    def _create_fallback_mapping(self, content: Dict[str, Any], target_level: str) -> Dict[str, Any]:
        """Create a basic fallback mapping if AI processing fails."""
        level_index = ["A1", "A2", "B1", "B2", "C1", "C2"].index(target_level)
        
        return {
            "target_level_content": {
                "appropriate_vocabulary": content.get('vocabulary_themes', [])[:3 + level_index],
                "suitable_scenarios": content.get('communication_scenarios', [])[:2 + level_index],
                "complexity_note": f"Basic mapping for {target_level} level"
            }
        }

class CurriculumStructureGenerator:
    """Generates progressive curriculum structures based on analyzed content."""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    async def create_structure(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete curriculum structure."""
        
        try:
            structure_prompt = f"""
            Create a comprehensive curriculum structure based on this analysis:
            
            {json.dumps(analysis_data, indent=2)}
            
            Generate a detailed curriculum with:
            1. Course title and description
            2. Overall learning objectives
            3. Weekly modules with progression
            4. Learning objectives for each module
            5. Vocabulary themes per module
            6. Grammar progression
            7. Skills focus (reading, writing, speaking, listening)
            8. Assessment points
            9. Company-specific integration points
            
            Ensure:
            - Logical progression from basic to advanced
            - Practical workplace application
            - Industry-specific content integration
            - CEFR alignment throughout
            - Engaging variety in content types
            
            Return as detailed JSON structure.
            """
            
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert curriculum designer specializing in corporate English language training."},
                    {"role": "user", "content": structure_prompt}
                ],
                max_tokens=3000,
                temperature=0.4
            )
            
            curriculum_structure = json.loads(response.choices[0].message.content)
            
            return {
                "curriculum": curriculum_structure,
                "analysis_source": analysis_data,
                "generated_at": datetime.utcnow().isoformat(),
                "generator_version": "1.0.0"
            }
            
        except Exception as e:
            logger.error(f"Curriculum generation failed: {e}")
            return {
                "error": str(e),
                "fallback_structure": self._create_basic_structure(analysis_data)
            }
    
    def _create_basic_structure(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic curriculum structure as fallback."""
        return {
            "title": f"English Training Course",
            "description": "Corporate English language training based on company requirements",
            "duration_weeks": 8,
            "modules": [
                {
                    "week": i + 1,
                    "title": f"Week {i + 1}: Business Communication",
                    "description": f"Module {i + 1} content",
                    "vocabulary_themes": analysis_data.get('vocabulary_themes', [])[:2],
                    "duration_hours": 4
                }
                for i in range(8)
            ]
        }

class DatabaseQueryTool:
    """Handles database queries for curriculum templates and data persistence."""
    
    def __init__(self):
        self.db = db_connection
    
    async def get_curriculum_templates(self, industry: str, level: str) -> List[Dict[str, Any]]:
        """Retrieve existing curriculum templates for reference."""
        
        if not self.db.is_connected():
            return []
        
        try:
            # Query for similar courses
            response = self.db.supabase.table('courses').select(
                'id, title, description, cefr_level, generation_metadata'
            ).eq('cefr_level', level).execute()
            
            templates = []
            for course in response.data:
                if industry.lower() in course.get('description', '').lower():
                    templates.append({
                        "course_id": course['id'],
                        "title": course['title'],
                        "description": course['description'],
                        "cefr_level": course['cefr_level'],
                        "metadata": course.get('generation_metadata', {})
                    })
            
            return templates[:5]  # Return top 5 matches
            
        except Exception as e:
            logger.error(f"Template query failed: {e}")
            return []
    
    async def save_curriculum(self, course_request_id: int, curriculum: Dict[str, Any]) -> Dict[str, Any]:
        """Save generated curriculum plan to database."""
        
        if not self.db.is_connected():
            return {"error": "Database not connected"}
        
        try:
            # Create course record
            course_data = {
                "title": curriculum.get('title', 'Generated Course'),
                "description": curriculum.get('description', ''),
                "cefr_level": curriculum.get('cefr_level', 'B1'),
                "status": "draft",
                "course_request_id": course_request_id,
                "ai_generated": True,
                "generation_metadata": json.dumps(curriculum),
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.db.supabase.table('courses').insert(course_data).execute()
            course_id = response.data[0]['id']
            
            # Create module records
            modules = curriculum.get('modules', [])
            for module_data in modules:
                module_record = {
                    "course_id": course_id,
                    "title": module_data.get('title', f"Module {module_data.get('week', 1)}"),
                    "description": module_data.get('description', ''),
                    "sequence_number": module_data.get('week', 1),
                    "duration_hours": module_data.get('duration_hours', 4),
                    "learning_objectives": json.dumps(module_data.get('learning_objectives', [])),
                    "vocabulary_themes": json.dumps(module_data.get('vocabulary_themes', [])),
                    "grammar_focus": json.dumps(module_data.get('grammar_focus', []))
                }
                
                self.db.supabase.table('modules').insert(module_record).execute()
            
            return {
                "success": True,
                "course_id": course_id,
                "modules_created": len(modules)
            }
            
        except Exception as e:
            logger.error(f"Curriculum save failed: {e}")
            return {"error": str(e)}

class RAGContextRetriever:
    """Enhanced tool for retrieving contextual information using RAG service."""
    
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
    
    async def get_contextual_insights(self, processes: List[str], vocabulary_themes: List[str], course_request_id: int) -> Dict[str, Any]:
        """Retrieve contextual insights for business processes and vocabulary."""
        
        if not self.rag_service or not self.rag_service.is_available():
            return {"status": "rag_not_available", "insights": []}
        
        try:
            insights = {}
            
            # Get context for each process
            for process in processes[:5]:  # Limit to top 5 processes
                process_context = await self.rag_service.get_contextual_content(
                    topic=process,
                    content_type="procedures",
                    max_chunks=3
                )
                if process_context:
                    insights[f"process_{process}"] = process_context
            
            # Get context for vocabulary themes
            for theme in vocabulary_themes[:5]:  # Limit to top 5 themes
                vocab_context = await self.rag_service.get_contextual_content(
                    topic=theme,
                    content_type="vocabulary",
                    max_chunks=2
                )
                if vocab_context:
                    insights[f"vocabulary_{theme}"] = vocab_context
            
            # Analyze coverage of identified topics
            all_topics = processes + vocabulary_themes
            coverage_analysis = await self.rag_service.analyze_document_coverage(all_topics)
            
            return {
                "status": "success",
                "contextual_insights": insights,
                "coverage_analysis": coverage_analysis,
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"RAG context retrieval failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_company_context(self, company_name: str, industry: str, course_request_id: int) -> Dict[str, Any]:
        """Retrieve company and industry-specific context."""
        
        if not self.rag_service or not self.rag_service.is_available():
            return {"status": "rag_not_available", "context": {}}
        
        try:
            # Search for company-specific information
            company_context = await self.rag_service.search_relevant_content(
                query=f"{company_name} company procedures processes",
                max_results=5
            )
            
            # Search for industry-specific information
            industry_context = await self.rag_service.search_relevant_content(
                query=f"{industry} industry communication requirements",
                max_results=5
            )
            
            return {
                "status": "success",
                "company_context": company_context,
                "industry_context": industry_context,
                "context_summary": {
                    "company_documents_found": len(company_context),
                    "industry_documents_found": len(industry_context),
                    "total_context_chunks": len(company_context) + len(industry_context)
                },
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Company context retrieval failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def assess_curriculum_relevance(self, curriculum: Dict[str, Any], course_request_id: int) -> float:
        """Assess how relevant the curriculum is to available company documents."""
        
        if not self.rag_service or not self.rag_service.is_available():
            return 0.5  # Default moderate relevance
        
        try:
            # Extract key topics from curriculum
            topics = []
            topics.extend(curriculum.get('vocabulary_themes', []))
            topics.extend([module.get('title', '') for module in curriculum.get('modules', [])])
            topics = [topic for topic in topics if topic]  # Remove empty strings
            
            if not topics:
                return 0.0
            
            # Analyze coverage
            coverage_analysis = await self.rag_service.analyze_document_coverage(topics)
            
            # Calculate relevance score
            overall_score = coverage_analysis.get('overall_score', 0.0)
            
            # Adjust based on coverage quality
            coverage_data = coverage_analysis.get('coverage', {})
            excellent_count = sum(1 for topic_data in coverage_data.values() 
                                if topic_data.get('coverage_level') == 'excellent')
            good_count = sum(1 for topic_data in coverage_data.values() 
                           if topic_data.get('coverage_level') == 'good')
            
            # Boost score for high-quality coverage
            quality_boost = (excellent_count * 0.2 + good_count * 0.1) / len(topics)
            
            final_score = min(overall_score + quality_boost, 1.0)
            
            return final_score
            
        except Exception as e:
            logger.error(f"Curriculum relevance assessment failed: {e}")
            return 0.5
    
    async def get_topic_insights(self, topic: str, course_request_id: int) -> Dict[str, Any]:
        """Get detailed insights for a specific topic."""
        
        if not self.rag_service or not self.rag_service.is_available():
            return {"status": "rag_not_available"}
        
        try:
            # Get contextual content for different aspects
            insights = {}
            
            content_types = ["vocabulary", "procedures", "guidelines", "examples"]
            
            for content_type in content_types:
                context = await self.rag_service.get_contextual_content(
                    topic=topic,
                    content_type=content_type,
                    max_chunks=2
                )
                if context:
                    insights[content_type] = context
            
            return {
                "status": "success",
                "topic": topic,
                "insights": insights,
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Topic insights retrieval failed: {e}")
            return {"status": "error", "error": str(e)}

class PerformanceMetrics:
    """Tool for tracking and analyzing agent performance metrics."""
    
    def __init__(self):
        self.metrics_data = {
            "analysis_metrics": [],
            "curriculum_saves": [],
            "planning_failures": [],
            "quality_scores": [],
            "optimization_events": []
        }
    
    async def record_analysis_metrics(self, course_request_id: int, processing_time: float, 
                                    documents_analyzed: int, success: bool, error: str = None) -> None:
        """Record SOP analysis performance metrics."""
        
        metric_entry = {
            "course_request_id": course_request_id,
            "processing_time": processing_time,
            "documents_analyzed": documents_analyzed,
            "success": success,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.metrics_data["analysis_metrics"].append(metric_entry)
        
        # Keep only last 100 entries
        if len(self.metrics_data["analysis_metrics"]) > 100:
            self.metrics_data["analysis_metrics"] = self.metrics_data["analysis_metrics"][-100:]
    
    async def record_curriculum_save(self, course_request_id: int, success: bool, 
                                   quality_score: float = None, error: str = None) -> None:
        """Record curriculum save metrics."""
        
        save_entry = {
            "course_request_id": course_request_id,
            "success": success,
            "quality_score": quality_score,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.metrics_data["curriculum_saves"].append(save_entry)
        
        if quality_score is not None:
            self.metrics_data["quality_scores"].append(quality_score)
    
    async def record_planning_failure(self, course_request_id: int, error: str, processing_time: float) -> None:
        """Record planning failure for analysis."""
        
        failure_entry = {
            "course_request_id": course_request_id,
            "error": error,
            "processing_time": processing_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.metrics_data["planning_failures"].append(failure_entry)
    
    async def calculate_curriculum_quality_score(self, curriculum: Dict[str, Any]) -> float:
        """Calculate a quality score for the curriculum."""
        
        try:
            score = 0.0
            max_score = 100.0
            
            # Check basic structure (20 points)
            if curriculum.get('title'):
                score += 5
            if curriculum.get('description'):
                score += 5
            if curriculum.get('learning_objectives'):
                score += 10
            
            # Check modules (30 points)
            modules = curriculum.get('modules', [])
            if modules:
                score += 10  # Has modules
                if len(modules) >= 4:
                    score += 10  # Adequate number
                if all(module.get('learning_objectives') for module in modules):
                    score += 10  # All modules have objectives
            
            # Check vocabulary integration (20 points)
            if curriculum.get('vocabulary_themes'):
                score += 10
                if len(curriculum.get('vocabulary_themes', [])) >= 5:
                    score += 10
            
            # Check grammar progression (15 points)
            if curriculum.get('grammar_progression'):
                score += 15
            
            # Check assessment strategy (15 points)
            if curriculum.get('assessment_strategy'):
                score += 15
            
            return min(score, max_score)
            
        except Exception as e:
            logger.error(f"Quality score calculation failed: {e}")
            return 50.0  # Default moderate score
    
    async def calculate_completeness_score(self, curriculum: Dict[str, Any]) -> float:
        """Calculate curriculum completeness score."""
        
        try:
            required_fields = [
                'title', 'description', 'cefr_level', 'duration_weeks',
                'learning_objectives', 'modules', 'vocabulary_themes',
                'grammar_progression', 'assessment_strategy'
            ]
            
            present_fields = sum(1 for field in required_fields if curriculum.get(field))
            completeness = (present_fields / len(required_fields)) * 100
            
            # Bonus for module completeness
            modules = curriculum.get('modules', [])
            if modules:
                module_completeness = sum(
                    1 for module in modules 
                    if all(module.get(field) for field in ['title', 'description', 'learning_objectives'])
                ) / len(modules) * 10
                completeness += module_completeness
            
            return min(completeness, 100.0)
            
        except Exception as e:
            logger.error(f"Completeness score calculation failed: {e}")
            return 60.0
    
    async def optimize_curriculum(self, curriculum: Dict[str, Any], optimization_criteria: List[str]) -> Dict[str, Any]:
        """Optimize curriculum based on criteria and performance data."""
        
        optimized_curriculum = curriculum.copy()
        optimization_log = []
        
        try:
            for criterion in optimization_criteria:
                if criterion == "vocabulary_balance":
                    # Ensure balanced vocabulary distribution
                    modules = optimized_curriculum.get('modules', [])
                    vocab_themes = optimized_curriculum.get('vocabulary_themes', [])
                    
                    if modules and vocab_themes:
                        themes_per_module = len(vocab_themes) // len(modules)
                        for i, module in enumerate(modules):
                            start_idx = i * themes_per_module
                            end_idx = start_idx + themes_per_module
                            module['vocabulary_themes'] = vocab_themes[start_idx:end_idx]
                        
                        optimization_log.append("Balanced vocabulary distribution across modules")
                
                elif criterion == "progression_smoothing":
                    # Ensure smooth progression in difficulty
                    modules = optimized_curriculum.get('modules', [])
                    if len(modules) > 1:
                        for i, module in enumerate(modules):
                            module['difficulty_level'] = (i + 1) / len(modules)
                            module['prerequisite_completion'] = i > 0
                        
                        optimization_log.append("Applied smooth difficulty progression")
                
                elif criterion == "assessment_integration":
                    # Integrate assessments throughout curriculum
                    modules = optimized_curriculum.get('modules', [])
                    for i, module in enumerate(modules):
                        if i % 2 == 1:  # Every other module
                            module['formative_assessment'] = True
                        if i == len(modules) - 1:  # Last module
                            module['summative_assessment'] = True
                    
                    optimization_log.append("Integrated assessment points")
            
            # Record optimization event
            optimization_entry = {
                "criteria": optimization_criteria,
                "changes_made": optimization_log,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.metrics_data["optimization_events"].append(optimization_entry)
            
            return {
                "optimized_curriculum": optimized_curriculum,
                "optimization_log": optimization_log,
                "optimization_score": await self.calculate_curriculum_quality_score(optimized_curriculum)
            }
            
        except Exception as e:
            logger.error(f"Curriculum optimization failed: {e}")
            return {
                "optimized_curriculum": curriculum,
                "optimization_log": ["Optimization failed"],
                "error": str(e)
            }
    
    async def get_improvement_recommendations(self, curriculum: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on curriculum analysis."""
        
        recommendations = []
        
        try:
            # Check for missing elements
            if not curriculum.get('learning_objectives'):
                recommendations.append("Add specific, measurable learning objectives")
            
            if not curriculum.get('assessment_strategy'):
                recommendations.append("Develop comprehensive assessment strategy")
            
            modules = curriculum.get('modules', [])
            if len(modules) < 4:
                recommendations.append("Increase number of modules for better content distribution")
            
            # Check module quality
            incomplete_modules = [i for i, module in enumerate(modules) 
                                if not module.get('learning_objectives')]
            if incomplete_modules:
                recommendations.append(f"Add learning objectives to modules: {incomplete_modules}")
            
            # Check vocabulary coverage
            vocab_themes = curriculum.get('vocabulary_themes', [])
            if len(vocab_themes) < 5:
                recommendations.append("Expand vocabulary themes for comprehensive coverage")
            
            # Check CEFR alignment
            if not curriculum.get('cefr_level'):
                recommendations.append("Specify clear CEFR level alignment")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Unable to generate recommendations - review curriculum manually"]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of agent performance metrics."""
        
        try:
            analysis_metrics = self.metrics_data["analysis_metrics"]
            curriculum_saves = self.metrics_data["curriculum_saves"]
            quality_scores = self.metrics_data["quality_scores"]
            
            summary = {
                "total_analyses": len(analysis_metrics),
                "successful_analyses": sum(1 for m in analysis_metrics if m["success"]),
                "total_saves": len(curriculum_saves),
                "successful_saves": sum(1 for s in curriculum_saves if s["success"]),
                "average_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
                "total_failures": len(self.metrics_data["planning_failures"]),
                "optimization_events": len(self.metrics_data["optimization_events"])
            }
            
            if analysis_metrics:
                processing_times = [m["processing_time"] for m in analysis_metrics]
                summary["average_processing_time"] = sum(processing_times) / len(processing_times)
            
            return summary
            
        except Exception as e:
            logger.error(f"Performance summary generation failed: {e}")
            return {"error": "Unable to generate performance summary"}