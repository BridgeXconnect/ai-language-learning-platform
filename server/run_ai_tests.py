#!/usr/bin/env python3
"""
AI Enhancement Test Runner
Executes comprehensive tests for all AI enhancement features
"""
import asyncio
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_ai_tests():
    """Run all AI enhancement tests and generate report"""
    print("🧪 AI Enhancement Test Suite")
    print("=" * 50)
    
    start_time = time.time()
    
    # Test categories
    test_categories = {
        "AI Tutor Service": "test_ai_tutor_service",
        "AI Content Service": "test_ai_content_service", 
        "AI Assessment Service": "test_ai_assessment_service",
        "AI Recommendation Engine": "test_ai_recommendation_engine",
        "Agent Orchestration": "test_agent_orchestration_service",
        "Advanced NLP Service": "test_advanced_nlp_service",
        "QA Automation Service": "test_qa_automation_service",
        "Integration Tests": "test_integration_tests"
    }
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_duration": 0,
        "categories": {},
        "overall_status": "PENDING"
    }
    
    try:
        # Import and run tests
        import pytest
        from tests.test_ai_enhancements import (
            TestAITutorService,
            TestAIContentService,
            TestAIAssessmentService,
            TestAIRecommendationEngine,
            TestAgentOrchestrationService,
            TestAdvancedNLPService,
            TestQAAutomationService,
            TestIntegrationTests
        )
        
        print("📋 Running AI Enhancement Tests...")
        print()
        
        # Run each test category
        for category_name, test_class_name in test_categories.items():
            print(f"🔍 Testing {category_name}...")
            
            category_start = time.time()
            
            try:
                # Run tests for this category
                if category_name == "AI Tutor Service":
                    test_class = TestAITutorService()
                elif category_name == "AI Content Service":
                    test_class = TestAIContentService()
                elif category_name == "AI Assessment Service":
                    test_class = TestAIAssessmentService()
                elif category_name == "AI Recommendation Engine":
                    test_class = TestAIRecommendationEngine()
                elif category_name == "Agent Orchestration":
                    test_class = TestAgentOrchestrationService()
                elif category_name == "Advanced NLP Service":
                    test_class = TestAdvancedNLPService()
                elif category_name == "QA Automation Service":
                    test_class = TestQAAutomationService()
                elif category_name == "Integration Tests":
                    test_class = TestIntegrationTests()
                
                # Run async tests
                loop = asyncio.get_event_loop()
                
                # Get test methods
                test_methods = [method for method in dir(test_class) 
                              if method.startswith('test_') and callable(getattr(test_class, method))]
                
                category_results = {
                    "total": len(test_methods),
                    "passed": 0,
                    "failed": 0,
                    "errors": []
                }
                
                for test_method in test_methods:
                    try:
                        test_func = getattr(test_class, test_method)
                        if asyncio.iscoroutinefunction(test_func):
                            loop.run_until_complete(test_func())
                        else:
                            test_func()
                        category_results["passed"] += 1
                        print(f"  ✅ {test_method}")
                    except Exception as e:
                        category_results["failed"] += 1
                        error_msg = f"{test_method}: {str(e)}"
                        category_results["errors"].append(error_msg)
                        print(f"  ❌ {test_method}: {str(e)}")
                
                category_duration = time.time() - category_start
                category_results["duration"] = category_duration
                
                results["categories"][category_name] = category_results
                results["total_tests"] += category_results["total"]
                results["passed_tests"] += category_results["passed"]
                results["failed_tests"] += category_results["failed"]
                
                status = "✅ PASSED" if category_results["failed"] == 0 else "❌ FAILED"
                print(f"  {status} - {category_results['passed']}/{category_results['total']} tests passed")
                print(f"  ⏱️  Duration: {category_duration:.2f}s")
                print()
                
            except Exception as e:
                print(f"  ❌ Error running {category_name}: {str(e)}")
                results["categories"][category_name] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 1,
                    "errors": [str(e)],
                    "duration": 0
                }
                results["failed_tests"] += 1
                print()
        
        # Calculate overall results
        total_duration = time.time() - start_time
        results["test_duration"] = total_duration
        
        if results["failed_tests"] == 0:
            results["overall_status"] = "PASSED"
        else:
            results["overall_status"] = "FAILED"
        
        # Print summary
        print("📊 Test Summary")
        print("=" * 50)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(f"Success Rate: {(results['passed_tests']/results['total_tests']*100):.1f}%" if results['total_tests'] > 0 else "0%")
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Overall Status: {results['overall_status']}")
        
        # Save results to file
        results_file = "ai_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        # Generate HTML report
        generate_html_report(results)
        
        return results["overall_status"] == "PASSED"
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        return False

def generate_html_report(results):
    """Generate HTML test report"""
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Enhancement Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
        .summary {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .category {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }}
        .passed {{ border-left: 5px solid #28a745; }}
        .failed {{ border-left: 5px solid #dc3545; }}
        .status {{ font-weight: bold; padding: 5px 10px; border-radius: 5px; }}
        .status.passed {{ background: #d4edda; color: #155724; }}
        .status.failed {{ background: #f8d7da; color: #721c24; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .metric {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 2em; font-weight: bold; }}
        .error {{ background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI Enhancement Test Report</h1>
        <p>Generated on: {results['timestamp']}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Overall Summary</h2>
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{results['total_tests']}</div>
                <div>Total Tests</div>
            </div>
            <div class="metric">
                <div class="metric-value" style="color: #28a745;">{results['passed_tests']}</div>
                <div>Passed</div>
            </div>
            <div class="metric">
                <div class="metric-value" style="color: #dc3545;">{results['failed_tests']}</div>
                <div>Failed</div>
            </div>
            <div class="metric">
                <div class="metric-value">{results['test_duration']:.2f}s</div>
                <div>Duration</div>
            </div>
        </div>
        <div class="status {'passed' if results['overall_status'] == 'PASSED' else 'failed'}">
            Overall Status: {results['overall_status']}
        </div>
    </div>
    
    <h2>📋 Test Categories</h2>
"""
    
    for category_name, category_results in results['categories'].items():
        status_class = "passed" if category_results['failed'] == 0 else "failed"
        html_content += f"""
    <div class="category {status_class}">
        <h3>{category_name}</h3>
        <div class="status {status_class}">
            {category_results['passed']}/{category_results['total']} tests passed
        </div>
        <p><strong>Duration:</strong> {category_results['duration']:.2f}s</p>
"""
        
        if category_results['errors']:
            html_content += "<h4>Errors:</h4>"
            for error in category_results['errors']:
                html_content += f'<div class="error">{error}</div>'
        
        html_content += "</div>"
    
    html_content += """
</body>
</html>
"""
    
    with open("ai_test_report.html", 'w') as f:
        f.write(html_content)
    
    print("📄 HTML report generated: ai_test_report.html")

def main():
    """Main function"""
    print("🚀 Starting AI Enhancement Test Suite...")
    
    success = run_ai_tests()
    
    if success:
        print("\n🎉 All tests passed! AI enhancement features are working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 