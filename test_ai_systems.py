#!/usr/bin/env python3
"""
Comprehensive AI Systems Test Script
Tests all AI components including Pydantic-AI agents, LangGraph workflows, and mock servers
"""

import asyncio
import logging
import sys
import time
from typing import Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our AI components
try:
    from agents.orchestrator.workflow import CourseGenerationWorkflow, WorkflowState
    from agents.orchestrator.agent_client import AgentClient
    from agents.mock_agent_server import (
        create_mock_course_planner,
        create_mock_content_creator,
        create_mock_quality_assurance
    )
    logger.info("✅ Successfully imported AI components")
except ImportError as e:
    logger.error(f"❌ Failed to import AI components: {e}")
    sys.exit(1)

class AISystemsTester:
    """Comprehensive tester for all AI systems."""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.utcnow()
        
        # Test configuration
        self.config = {
            "mock_server_ports": {
                "course_planner": 8001,
                "content_creator": 8002,
                "quality_assurance": 8003
            },
            "test_timeout": 30,  # seconds
            "max_retries": 3
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all AI system tests."""
        
        logger.info("🚀 Starting comprehensive AI systems test")
        
        test_suite = [
            ("Dependency Check", self.test_dependencies),
            ("Mock Server Creation", self.test_mock_server_creation),
            ("Agent Client Initialization", self.test_agent_client),
            ("Workflow Initialization", self.test_workflow_initialization),
            ("End-to-End Workflow", self.test_end_to_end_workflow),
            ("Error Handling", self.test_error_handling),
            ("Performance Test", self.test_performance)
        ]
        
        for test_name, test_func in test_suite:
            try:
                logger.info(f"🧪 Running test: {test_name}")
                result = await test_func()
                self.test_results[test_name] = {
                    "status": "PASS" if result else "FAIL",
                    "details": result if result else "Test failed"
                }
                logger.info(f"✅ {test_name}: PASS")
            except Exception as e:
                logger.error(f"❌ {test_name}: FAIL - {e}")
                self.test_results[test_name] = {
                    "status": "FAIL",
                    "details": str(e)
                }
        
        return self._compile_test_report()
    
    async def test_dependencies(self) -> bool:
        """Test that all required dependencies are available."""
        
        required_packages = [
            "pydantic_ai",
            "langgraph",
            "langchain",
            "fastapi",
            "uvicorn",
            "httpx"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"Missing packages: {missing_packages}")
            return False
        
        logger.info("✅ All required dependencies are available")
        return True
    
    async def test_mock_server_creation(self) -> bool:
        """Test that mock servers can be created successfully."""
        
        try:
            # Test course planner server creation
            course_planner = create_mock_course_planner()
            assert course_planner.config.agent_name == "Course Planning Specialist"
            assert course_planner.config.agent_type == "course_planner"
            
            # Test content creator server creation
            content_creator = create_mock_content_creator()
            assert content_creator.config.agent_name == "Content Creator Agent"
            assert content_creator.config.agent_type == "content_creator"
            
            # Test quality assurance server creation
            quality_assurance = create_mock_quality_assurance()
            assert quality_assurance.config.agent_name == "Quality Assurance Agent"
            assert quality_assurance.config.agent_type == "quality_assurance"
            
            logger.info("✅ All mock servers created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Mock server creation failed: {e}")
            return False
    
    async def test_agent_client(self) -> bool:
        """Test agent client initialization and basic functionality."""
        
        try:
            # Test agent client initialization
            config = {
                "course_planner_url": f"http://localhost:{self.config['mock_server_ports']['course_planner']}",
                "content_creator_url": f"http://localhost:{self.config['mock_server_ports']['content_creator']}",
                "quality_assurance_url": f"http://localhost:{self.config['mock_server_ports']['quality_assurance']}",
                "openai_api_key": "test-key",
                "anthropic_api_key": "test-key"
            }
            
            agent_client = AgentClient(config)
            
            # Test that agents were initialized
            assert hasattr(agent_client, 'course_planner_agent')
            assert hasattr(agent_client, 'content_creator_agent')
            assert hasattr(agent_client, 'quality_assurance_agent')
            
            # Test that dependencies were set up
            assert agent_client.deps is not None
            assert agent_client.deps.base_urls is not None
            assert agent_client.deps.api_keys is not None
            
            logger.info("✅ Agent client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Agent client test failed: {e}")
            return False
    
    async def test_workflow_initialization(self) -> bool:
        """Test workflow initialization and graph building."""
        
        try:
            # Test workflow initialization
            workflow = CourseGenerationWorkflow()
            
            # Test that graph was built
            assert workflow.graph is not None
            
            # Test configuration
            assert workflow.config is not None
            assert "max_retries" in workflow.config
            assert "quality_threshold" in workflow.config
            
            # Test agent client
            assert workflow.agent_client is not None
            
            logger.info("✅ Workflow initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Workflow initialization failed: {e}")
            return False
    
    async def test_end_to_end_workflow(self) -> bool:
        """Test a complete end-to-end workflow execution."""
        
        try:
            # Create workflow
            workflow = CourseGenerationWorkflow()
            
            # Create test request
            test_request = type('TestRequest', (), {
                'course_request_id': 'test_001',
                'company_name': 'Test Company',
                'industry': 'Technology',
                'training_goals': ['Improve communication', 'Enhance presentation skills'],
                'current_english_level': 'B1',
                'duration_weeks': 8,
                'target_audience': 'Professional staff',
                'specific_needs': 'Focus on technical documentation'
            })()
            
            # Execute workflow (this will use mock agents)
            logger.info("🔄 Executing end-to-end workflow...")
            result = await workflow.execute_complete_workflow(test_request)
            
            # Validate result structure
            assert result is not None
            assert "workflow_id" in result
            assert "status" in result
            assert "course_request_id" in result
            
            logger.info(f"✅ End-to-end workflow completed with status: {result['status']}")
            return True
            
        except Exception as e:
            logger.error(f"End-to-end workflow test failed: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling in various scenarios."""
        
        try:
            # Test with invalid request
            workflow = CourseGenerationWorkflow()
            
            # Create invalid request (missing required fields)
            invalid_request = type('InvalidRequest', (), {
                'course_request_id': 'test_002',
                # Missing required fields
            })()
            
            # This should handle the error gracefully
            result = await workflow.execute_complete_workflow(invalid_request)
            
            # Should return error result
            assert result is not None
            assert "errors" in result
            
            logger.info("✅ Error handling test passed")
            return True
            
        except Exception as e:
            logger.error(f"Error handling test failed: {e}")
            return False
    
    async def test_performance(self) -> bool:
        """Test performance characteristics."""
        
        try:
            workflow = CourseGenerationWorkflow()
            
            # Test multiple concurrent requests
            test_requests = []
            for i in range(3):
                request = type('TestRequest', (), {
                    'course_request_id': f'perf_test_{i}',
                    'company_name': f'Company {i}',
                    'industry': 'Technology',
                    'training_goals': ['Improve communication'],
                    'current_english_level': 'B1',
                    'duration_weeks': 4,
                    'target_audience': 'Professional staff'
                })()
                test_requests.append(request)
            
            # Execute concurrent workflows
            start_time = time.time()
            tasks = [workflow.execute_complete_workflow(req) for req in test_requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Check performance
            total_time = end_time - start_time
            avg_time = total_time / len(test_requests)
            
            logger.info(f"✅ Performance test completed:")
            logger.info(f"   - Total time: {total_time:.2f}s")
            logger.info(f"   - Average time per request: {avg_time:.2f}s")
            logger.info(f"   - Successful requests: {sum(1 for r in results if not isinstance(r, Exception))}")
            
            return True
            
        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            return False
    
    def _compile_test_report(self) -> Dict[str, Any]:
        """Compile comprehensive test report."""
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["status"] == "PASS")
        failed_tests = total_tests - passed_tests
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.utcnow().isoformat(),
                "duration": (datetime.utcnow() - self.start_time).total_seconds()
            },
            "test_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        
        recommendations = []
        
        if any(result["status"] == "FAIL" for result in self.test_results.values()):
            recommendations.append("Some tests failed. Review the error details above.")
        
        if self.test_results.get("Performance Test", {}).get("status") == "PASS":
            recommendations.append("Performance is acceptable for development.")
        else:
            recommendations.append("Consider optimizing performance for production use.")
        
        if self.test_results.get("Dependency Check", {}).get("status") == "PASS":
            recommendations.append("All dependencies are properly installed.")
        else:
            recommendations.append("Install missing dependencies before proceeding.")
        
        return recommendations

async def main():
    """Main test execution function."""
    
    print("🤖 AI Language Learning Platform - Systems Test")
    print("=" * 50)
    
    tester = AISystemsTester()
    report = await tester.run_all_tests()
    
    # Print summary
    print("\n📊 Test Summary")
    print("-" * 30)
    summary = report["test_summary"]
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Duration: {summary['duration']:.2f}s")
    
    # Print detailed results
    print("\n📋 Detailed Results")
    print("-" * 30)
    for test_name, result in report["test_results"].items():
        status_icon = "✅" if result["status"] == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {result['status']}")
        if result["status"] == "FAIL":
            print(f"   Error: {result['details']}")
    
    # Print recommendations
    if report["recommendations"]:
        print("\n💡 Recommendations")
        print("-" * 30)
        for rec in report["recommendations"]:
            print(f"• {rec}")
    
    # Exit with appropriate code
    if summary["failed"] > 0:
        print(f"\n❌ {summary['failed']} test(s) failed. Please review the errors above.")
        sys.exit(1)
    else:
        print(f"\n🎉 All {summary['total_tests']} tests passed! AI systems are ready.")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main()) 