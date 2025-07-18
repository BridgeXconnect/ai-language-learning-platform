#!/usr/bin/env python3
"""
Test script for AI course generation workflow.
Tests the complete pipeline from document processing to course generation.
"""

import asyncio
import sys
import os
import json
import time
from pathlib import Path

# Add the server directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db, SessionLocal
from app.domains.sales.models import CourseRequest, SOPDocument
from app.domains.courses.models import Course, Module, Lesson
from app.domains.ai.services.core import ai_service
from app.services.rag_service import rag_service
from app.services.document_service import document_processor
from app.services.course_generation_service import course_generation_service

class AIWorkflowTester:
    """Test the complete AI workflow."""
    
    def __init__(self):
        self.db = SessionLocal()
        self.test_results = {}
    
    async def run_all_tests(self):
        """Run all AI workflow tests."""
        
        print("🧪 AI Workflow Testing")
        print("=" * 50)
        
        # Test 1: Service Availability
        await self.test_service_availability()
        
        # Test 2: Document Processing
        await self.test_document_processing()
        
        # Test 3: RAG System
        await self.test_rag_system()
        
        # Test 4: AI Content Generation
        await self.test_ai_content_generation()
        
        # Test 5: Course Generation (if we have a test course request)
        await self.test_course_generation()
        
        # Print summary
        self.print_test_summary()
    
    async def test_service_availability(self):
        """Test if all AI services are available."""
        
        print("\n🔧 Testing Service Availability")
        print("-" * 30)
        
        try:
            # Test AI Service
            ai_available = ai_service.is_available()
            print(f"AI Service Available: {'✅' if ai_available else '❌'}")
            
            if ai_available:
                print(f"  - OpenAI Client: {'✅' if ai_service.openai_client else '❌'}")
                print(f"  - Anthropic Client: {'✅' if ai_service.anthropic_client else '❌'}")
            else:
                print("  ⚠️  No AI API keys configured")
            
            # Test RAG Service
            rag_available = rag_service.is_available()
            print(f"RAG Service Available: {'✅' if rag_available else '❌'}")
            
            if rag_available:
                stats = rag_service.vector_store.get_stats()
                print(f"  - Vector Store Dimension: {stats['dimension']}")
                print(f"  - Embedding Model: {stats['model']}")
            else:
                print("  ⚠️  Vector dependencies not installed")
            
            # Test Document Processor
            print(f"Document Processor Available: ✅")
            print(f"  - Supported formats: {document_processor.supported_formats}")
            
            self.test_results['services'] = {
                'ai_service': ai_available,
                'rag_service': rag_available,
                'document_processor': True
            }
            
        except Exception as e:
            print(f"❌ Service availability test failed: {e}")
            self.test_results['services'] = {'error': str(e)}
    
    async def test_document_processing(self):
        """Test document processing capabilities."""
        
        print("\n📄 Testing Document Processing")
        print("-" * 30)
        
        try:
            # Create a sample text document
            sample_content = """
            COMPANY STANDARD OPERATING PROCEDURES
            
            1. CUSTOMER SERVICE PROCEDURES
            
            1.1 Phone Call Handling
            When answering phone calls, staff must:
            - Greet the customer professionally
            - Identify yourself and the company
            - Listen actively to customer concerns
            - Provide clear and helpful responses
            - Follow up as needed
            
            1.2 Email Communication
            All email communications should:
            - Use professional language
            - Respond within 24 hours
            - Include proper greetings and closings
            - Check for spelling and grammar
            
            2. SAFETY PROCEDURES
            
            2.1 Emergency Protocols
            In case of emergency:
            - Call emergency services immediately
            - Evacuate the building if necessary
            - Report to designated assembly area
            - Wait for further instructions
            
            Key vocabulary: customer service, professional communication, emergency procedures, safety protocols
            """
            
            # Test text processing
            print("Testing text document processing...")
            result = await document_processor.process_file(
                "sample_sop.txt",
                sample_content.encode('utf-8')
            )
            
            print(f"✅ Document processed successfully:")
            print(f"  - Word count: {result['word_count']}")
            print(f"  - Character count: {result['char_count']}")
            print(f"  - Content hash: {result['content_hash'][:16]}...")
            
            # Test text chunking
            print("\nTesting text chunking...")
            chunks = document_processor.chunk_text(result['text'], chunk_size=200, overlap=50)
            print(f"✅ Created {len(chunks)} chunks")
            
            # Test key term extraction
            print("\nTesting key term extraction...")
            key_terms = await document_processor.extract_key_terms(result['text'], max_terms=10)
            print(f"✅ Extracted {len(key_terms)} key terms:")
            for term in key_terms[:5]:
                print(f"  - {term['term']} (freq: {term['frequency']})")
            
            self.test_results['document_processing'] = {
                'success': True,
                'word_count': result['word_count'],
                'chunks_created': len(chunks),
                'key_terms_extracted': len(key_terms)
            }
            
        except Exception as e:
            print(f"❌ Document processing test failed: {e}")
            self.test_results['document_processing'] = {'error': str(e)}
    
    async def test_rag_system(self):
        """Test RAG system functionality."""
        
        print("\n🔍 Testing RAG System")
        print("-" * 30)
        
        if not rag_service.is_available():
            print("⚠️ RAG service not available, skipping test")
            self.test_results['rag_system'] = {'skipped': 'Service not available'}
            return
        
        try:
            # Create sample document content
            sample_content = """
            Customer Service Excellence Manual
            
            Our company is committed to providing exceptional customer service.
            All employees must follow these communication guidelines:
            
            1. Professional Greetings
            - Always greet customers warmly
            - Use proper titles (Mr., Ms., Dr.)
            - Introduce yourself clearly
            
            2. Active Listening
            - Give customers your full attention
            - Ask clarifying questions
            - Summarize their concerns
            
            3. Problem Resolution
            - Acknowledge the customer's issue
            - Propose solutions quickly
            - Follow up to ensure satisfaction
            
            Key Business English vocabulary:
            - Acknowledge, clarify, resolve
            - Professional, courteous, efficient
            - Customer satisfaction, service excellence
            """
            
            # Index the document
            print("Indexing sample document...")
            index_result = await rag_service.index_document(
                file_path="customer_service_manual.txt",
                file_content=sample_content.encode('utf-8'),
                source_metadata={'test': True}
            )
            
            print(f"✅ Document indexed:")
            print(f"  - Source ID: {index_result['source_id'][:16]}...")
            print(f"  - Chunks indexed: {index_result['chunks_indexed']}")
            print(f"  - Key terms: {len(index_result['key_terms'])}")
            
            # Test content search
            print("\nTesting content search...")
            search_queries = [
                "customer service procedures",
                "professional communication",
                "business English vocabulary"
            ]
            
            for query in search_queries:
                results = await rag_service.search_relevant_content(
                    query=query,
                    max_results=3,
                    min_score=0.1
                )
                print(f"  Query: '{query}' -> {len(results)} results")
                if results:
                    print(f"    Best match score: {results[0]['similarity_score']:.3f}")
            
            # Test contextual content extraction
            print("\nTesting contextual content extraction...")
            context = await rag_service.get_contextual_content(
                topic="customer communication",
                content_type="procedures",
                max_chunks=2
            )
            print(f"✅ Retrieved contextual content: {len(context)} characters")
            
            self.test_results['rag_system'] = {
                'success': True,
                'chunks_indexed': index_result['chunks_indexed'],
                'search_queries_tested': len(search_queries),
                'contextual_content_length': len(context)
            }
            
        except Exception as e:
            print(f"❌ RAG system test failed: {e}")
            self.test_results['rag_system'] = {'error': str(e)}
    
    async def test_ai_content_generation(self):
        """Test AI content generation capabilities."""
        
        print("\n🤖 Testing AI Content Generation")
        print("-" * 30)
        
        if not ai_service.is_available():
            print("⚠️ AI service not available, skipping test")
            self.test_results['ai_generation'] = {'skipped': 'Service not available'}
            return
        
        try:
            # Test basic content generation
            print("Testing basic content generation...")
            
            basic_prompt = "Generate a brief business English lesson about email etiquette."
            content = await ai_service.generate_content(
                prompt=basic_prompt,
                max_tokens=500,
                temperature=0.3
            )
            
            print(f"✅ Generated content ({len(content)} characters)")
            print(f"  Preview: {content[:100]}...")
            
            # Test curriculum generation
            print("\nTesting curriculum generation...")
            
            curriculum = await ai_service.generate_course_curriculum(
                company_name="TechCorp",
                industry="Technology",
                sop_content="Standard operating procedures for technical support",
                cefr_level="B1",
                duration_weeks=4
            )
            
            print(f"✅ Generated curriculum:")
            print(f"  - Title: {curriculum.get('title', 'N/A')}")
            print(f"  - Modules: {len(curriculum.get('modules', []))}")
            print(f"  - Learning objectives: {len(curriculum.get('learning_objectives', []))}")
            
            # Test lesson content generation
            print("\nTesting lesson content generation...")
            
            lesson_content = await ai_service.generate_lesson_content(
                lesson_title="Email Communication",
                module_context="Professional communication skills",
                vocabulary_themes=["email", "business communication"],
                grammar_focus=["formal language", "polite requests"],
                cefr_level="B1",
                duration_minutes=60
            )
            
            print(f"✅ Generated lesson content")
            if isinstance(lesson_content, dict):
                print(f"  - Has structured format: ✅")
            else:
                print(f"  - Raw content: {len(str(lesson_content))} characters")
            
            self.test_results['ai_generation'] = {
                'success': True,
                'basic_content_length': len(content),
                'curriculum_modules': len(curriculum.get('modules', [])),
                'lesson_content_generated': True
            }
            
        except Exception as e:
            print(f"❌ AI content generation test failed: {e}")
            self.test_results['ai_generation'] = {'error': str(e)}
    
    async def test_course_generation(self):
        """Test end-to-end course generation."""
        
        print("\n🎓 Testing Course Generation")
        print("-" * 30)
        
        try:
            # Check if we have any existing course requests
            course_requests = self.db.query(CourseRequest).limit(1).all()
            
            if not course_requests:
                print("⚠️ No course requests found, creating test request...")
                
                # Create a test course request
                test_request = CourseRequest(
                    company_name="Test Company",
                    industry="Technology",
                    contact_name="Test Contact",
                    contact_email="test@example.com",
                    training_goals="Improve business English communication",
                    target_audience="Software developers",
                    current_english_level="B1",
                    timeline="8 weeks",
                    specific_needs="Technical communication, email writing",
                    sales_user_id=1  # Assuming admin user
                )
                
                self.db.add(test_request)
                self.db.commit()
                self.db.refresh(test_request)
                
                print(f"✅ Created test course request (ID: {test_request.id})")
                course_request_id = test_request.id
            else:
                course_request_id = course_requests[0].id
                print(f"Using existing course request (ID: {course_request_id})")
            
            # Check generation status
            print("\nChecking generation status...")
            status = await course_generation_service.get_generation_status(course_request_id, self.db)
            print(f"✅ Status retrieved:")
            print(f"  - Can generate: {status['can_generate']}")
            print(f"  - AI services available: {status['ai_services_available']}")
            print(f"  - SOP processing: {status['sop_processing']}")
            
            # Test course generation if AI is available
            if ai_service.is_available() and status['can_generate']:
                print("\nTesting course generation...")
                
                start_time = time.time()
                result = await course_generation_service.generate_course_from_request(
                    course_request_id=course_request_id,
                    db=self.db,
                    generation_config={
                        "duration_weeks": 2,  # Short test course
                        "lessons_per_week": 1,
                        "exercise_count_per_lesson": 2,
                        "include_assessments": False  # Skip for test
                    }
                )
                generation_time = time.time() - start_time
                
                print(f"✅ Course generation completed in {generation_time:.2f}s:")
                print(f"  - Course ID: {result['course_id']}")
                print(f"  - Modules created: {result.get('modules_created', 0)}")
                print(f"  - Indexed sources: {result.get('indexed_sources', 0)}")
                
                # Verify database records
                course = self.db.query(Course).filter(Course.id == result['course_id']).first()
                if course:
                    modules = self.db.query(Module).filter(Module.course_id == course.id).all()
                    lessons = self.db.query(Lesson).join(Module).filter(Module.course_id == course.id).all()
                    
                    print(f"  - Database verification:")
                    print(f"    - Course title: {course.title}")
                    print(f"    - Modules in DB: {len(modules)}")
                    print(f"    - Lessons in DB: {len(lessons)}")
                    print(f"    - AI generated: {course.ai_generated}")
                
                self.test_results['course_generation'] = {
                    'success': True,
                    'course_id': result['course_id'],
                    'generation_time': generation_time,
                    'modules_created': len(modules),
                    'lessons_created': len(lessons)
                }
            else:
                print("⚠️ Skipping course generation (AI not available or cannot generate)")
                self.test_results['course_generation'] = {'skipped': 'AI not available or preconditions not met'}
            
        except Exception as e:
            print(f"❌ Course generation test failed: {e}")
            self.test_results['course_generation'] = {'error': str(e)}
    
    def print_test_summary(self):
        """Print a summary of all test results."""
        
        print("\n" + "=" * 50)
        print("🎯 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results.values() if r.get('success')])
        skipped_tests = len([r for r in self.test_results.values() if 'skipped' in r])
        failed_tests = len([r for r in self.test_results.values() if 'error' in r])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"⚠️ Skipped: {skipped_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        print(f"\nSuccess Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        print(f"\nDetailed Results:")
        for test_name, result in self.test_results.items():
            if result.get('success'):
                print(f"  ✅ {test_name}: PASSED")
            elif 'skipped' in result:
                print(f"  ⚠️ {test_name}: SKIPPED ({result['skipped']})")
            elif 'error' in result:
                print(f"  ❌ {test_name}: FAILED ({result['error']})")
        
        # Recommendations
        print(f"\n📋 Recommendations:")
        
        if not self.test_results.get('services', {}).get('ai_service'):
            print("  • Configure OPENAI_API_KEY or ANTHROPIC_API_KEY for full AI functionality")
        
        if not self.test_results.get('services', {}).get('rag_service'):
            print("  • Install vector dependencies for RAG functionality")
        
        if failed_tests == 0 and skipped_tests <= 1:
            print("  🎉 All systems operational! Ready for production use.")
        
        print(f"\n💾 Test results saved to: {json.dumps(self.test_results, indent=2)}")
    
    def __del__(self):
        """Clean up database connection."""
        if hasattr(self, 'db'):
            self.db.close()

async def main():
    """Run the AI workflow tests."""
    
    tester = AIWorkflowTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())