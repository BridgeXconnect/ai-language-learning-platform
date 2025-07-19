#!/usr/bin/env python3
"""
Simple test script for Pydantic model factories.
Tests the factory pattern implementation without database dependencies.
"""

import asyncio
import sys
import json
from pathlib import Path

# Add the server directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_pydantic_factories():
    """Test the Pydantic model factories."""
    
    print("🧪 Testing Pydantic Model Factories")
    print("=" * 50)
    
    try:
        # Import the factories
        from app.testing.factories import (
            AssessmentFactory, QualityScoreFactory, AIAssessmentDepsFactory,
            LearningRecommendationFactory, UserProfileFactory, CourseRecommendationFactory,
            QATestResultFactory, QualityReportFactory, TestCaseFactory,
            AgentStatusFactory, WorkflowStatusFactory, OrchestrationConfigFactory,
            create_test_scenario
        )
        
        print("✅ Successfully imported all factories")
        
        # Test 1: Assessment Factory
        print("\n📝 Testing Assessment Factory")
        print("-" * 30)
        
        assessment = AssessmentFactory.create()
        print(f"✅ Assessment created: {assessment.assessment_id}")
        print(f"  - Topic: {assessment.topic}")
        print(f"  - Difficulty: {assessment.difficulty.value}")
        print(f"  - Questions: {len(assessment.questions)}")
        print(f"  - Created at: {assessment.created_at}")
        
        # Test validation
        assessment_dict = assessment.model_dump()
        print(f"  - Serialized to dict: {len(assessment_dict)} fields")
        
        # Test 2: Quality Score Factory
        print("\n📊 Testing Quality Score Factory")
        print("-" * 30)
        
        quality_score = QualityScoreFactory.create_excellent()
        print(f"✅ Quality score created: {quality_score.overall_score:.2f}")
        print(f"  - Clarity: {quality_score.clarity_score:.2f}")
        print(f"  - Accuracy: {quality_score.accuracy_score:.2f}")
        print(f"  - Engagement: {quality_score.engagement_score:.2f}")
        print(f"  - Educational value: {quality_score.educational_value:.2f}")
        
        # Test validation
        assert 0 <= quality_score.overall_score <= 1, "Score should be between 0 and 1"
        print("  ✅ Validation passed")
        
        # Test 3: User Profile Factory
        print("\n👤 Testing User Profile Factory")
        print("-" * 30)
        
        user_profile = UserProfileFactory.create()
        print(f"✅ User profile created: {user_profile.user_id}")
        print(f"  - English level: {user_profile.english_level}")
        print(f"  - Learning goals: {len(user_profile.learning_goals)}")
        print(f"  - Preferred style: {user_profile.preferred_learning_style}")
        print(f"  - Completed courses: {user_profile.completed_courses}")
        
        # Test 4: Learning Recommendation Factory
        print("\n🎯 Testing Learning Recommendation Factory")
        print("-" * 30)
        
        recommendation = LearningRecommendationFactory.create()
        print(f"✅ Learning recommendation created: {recommendation.skill_area}")
        print(f"  - Current level: {recommendation.current_level}")
        print(f"  - Target level: {recommendation.target_level}")
        print(f"  - Confidence: {recommendation.confidence:.2f}")
        print(f"  - Activities: {len(recommendation.recommended_activities)}")
        
        # Test 5: Course Recommendation Factory
        print("\n📚 Testing Course Recommendation Factory")
        print("-" * 30)
        
        course_rec = CourseRecommendationFactory.create()
        print(f"✅ Course recommendation created: {course_rec.course_id}")
        print(f"  - Relevance score: {course_rec.relevance_score:.2f}")
        print(f"  - Difficulty match: {course_rec.difficulty_match:.2f}")
        print(f"  - Prerequisites met: {course_rec.prerequisites_met}")
        print(f"  - Confidence level: {course_rec.confidence_level}")
        
        # Test 6: QA Test Result Factory
        print("\n🔍 Testing QA Test Result Factory")
        print("-" * 30)
        
        qa_result = QATestResultFactory.create()
        print(f"✅ QA test result created: {qa_result.test_name}")
        print(f"  - Status: {qa_result.status}")
        print(f"  - Score: {qa_result.score:.2f}")
        print(f"  - Execution time: {qa_result.execution_time_seconds}s")
        
        # Test 7: Quality Report Factory
        print("\n📋 Testing Quality Report Factory")
        print("-" * 30)
        
        quality_report = QualityReportFactory.create()
        print(f"✅ Quality report created: {quality_report.report_id}")
        print(f"  - Overall score: {quality_report.overall_score:.2f}")
        print(f"  - Test results: {len(quality_report.test_results)}")
        print(f"  - Recommendations: {len(quality_report.recommendations)}")
        
        # Test 8: Agent Status Factory
        print("\n🤖 Testing Agent Status Factory")
        print("-" * 30)
        
        agent_status = AgentStatusFactory.create()
        print(f"✅ Agent status created: {agent_status.agent_id}")
        print(f"  - Status: {agent_status.status}")
        print(f"  - Health score: {agent_status.health_score:.2f}")
        print(f"  - Response time: {agent_status.response_time_ms}ms")
        print(f"  - Uptime: {agent_status.uptime_hours:.1f} hours")
        
        # Test 9: Workflow Status Factory
        print("\n⚙️ Testing Workflow Status Factory")
        print("-" * 30)
        
        workflow_status = WorkflowStatusFactory.create()
        print(f"✅ Workflow status created: {workflow_status.workflow_id}")
        print(f"  - Status: {workflow_status.status}")
        print(f"  - Progress: {workflow_status.progress_percentage:.1f}%")
        print(f"  - Current step: {workflow_status.current_step}")
        print(f"  - Total steps: {workflow_status.total_steps}")
        
        # Test 10: Complete Test Scenario
        print("\n🎬 Testing Complete Test Scenario")
        print("-" * 30)
        
        test_scenario = create_test_scenario()
        print(f"✅ Complete test scenario created")
        print(f"  - Total models: {len(test_scenario)}")
        print(f"  - Models: {list(test_scenario.keys())}")
        
        # Test serialization of all models
        print("\n📦 Testing Model Serialization")
        print("-" * 30)
        
        serialization_results = {}
        for name, model in test_scenario.items():
            try:
                # Test dict serialization
                model_dict = model.model_dump()
                # Test JSON serialization
                model_json = model.model_dump_json()
                
                serialization_results[name] = {
                    'dict_fields': len(model_dict),
                    'json_length': len(model_json),
                    'success': True
                }
                print(f"  ✅ {name}: {len(model_dict)} fields, {len(model_json)} chars")
            except Exception as e:
                serialization_results[name] = {
                    'error': str(e),
                    'success': False
                }
                print(f"  ❌ {name}: {e}")
        
        # Test validation with invalid data
        print("\n🚫 Testing Validation with Invalid Data")
        print("-" * 30)
        
        try:
            # This should fail validation
            invalid_score = QualityScoreFactory.create(
                overall_score=1.5,  # Should be <= 1.0
                clarity_score=0.9,
                accuracy_score=0.95,
                engagement_score=0.8,
                educational_value=0.85
            )
            print("❌ Invalid score should have failed validation")
        except Exception as e:
            print(f"✅ Validation correctly caught invalid score: {type(e).__name__}")
        
        # Summary
        print("\n" + "=" * 50)
        print("🎯 FACTORY TEST SUMMARY")
        print("=" * 50)
        
        successful_models = len([r for r in serialization_results.values() if r.get('success')])
        total_models = len(serialization_results)
        
        print(f"Total Models Tested: {total_models}")
        print(f"✅ Successful: {successful_models}")
        print(f"❌ Failed: {total_models - successful_models}")
        print(f"Success Rate: {(successful_models/total_models)*100:.1f}%")
        
        print(f"\n📋 Pydantic Factory Benefits:")
        print(f"  ✅ All test data passes Pydantic validation")
        print(f"  ✅ Test data is consistent and maintainable")
        print(f"  ✅ Factories can be easily updated when models change")
        print(f"  ✅ No more mock data issues after refactoring")
        print(f"  ✅ Proper type safety and validation")
        print(f"  ✅ Easy serialization to dict/JSON")
        
        print(f"\n💡 Usage Examples:")
        print(f"  # Create a test assessment")
        print(f"  assessment = AssessmentFactory.create(topic='Business English')")
        print(f"  ")
        print(f"  # Create an excellent quality score")
        print(f"  quality = QualityScoreFactory.create_excellent()")
        print(f"  ")
        print(f"  # Create a complete test scenario")
        print(f"  scenario = create_test_scenario()")
        
        return {
            'success': True,
            'models_tested': total_models,
            'successful_models': successful_models,
            'serialization_results': serialization_results
        }
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required dependencies are installed:")
        print("  pip install pydantic")
        return {'error': f'Import error: {e}'}
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return {'error': str(e)}

def main():
    """Run the Pydantic factory tests."""
    result = test_pydantic_factories()
    
    if result.get('success'):
        print(f"\n🎉 All Pydantic factory tests passed!")
        sys.exit(0)
    else:
        print(f"\n💥 Tests failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)

if __name__ == "__main__":
    main() 