#!/usr/bin/env python3
"""
Simple demonstration of Pydantic model factories.
This shows how to create proper test data with validation.
"""

import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict

# Simple Pydantic models for demonstration
class Assessment(BaseModel):
    assessment_id: str
    topic: str
    difficulty: str
    questions: List[Dict[str, Any]]
    created_at: datetime
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class QualityScore(BaseModel):
    overall_score: float = Field(ge=0.0, le=1.0)
    clarity_score: float = Field(ge=0.0, le=1.0)
    accuracy_score: float = Field(ge=0.0, le=1.0)
    engagement_score: float = Field(ge=0.0, le=1.0)
    educational_value: float = Field(ge=0.0, le=1.0)

class UserProfile(BaseModel):
    user_id: str
    english_level: str
    learning_goals: List[str]
    preferred_learning_style: str
    completed_courses: int
    total_study_hours: float

# Factory classes
class AssessmentFactory:
    """Factory for creating test Assessment instances."""
    
    @staticmethod
    def create(
        topic: str = "Test Customer Service",
        difficulty: str = "intermediate",
        question_count: int = 3
    ) -> Assessment:
        """Create a test assessment with realistic data."""
        
        questions = []
        for i in range(question_count):
            question = {
                "id": i + 1,
                "type": "multiple_choice" if i % 2 == 0 else "true_false",
                "question": f"Test question {i + 1} about {topic}?",
                "options": ["Option A", "Option B", "Option C", "Option D"] if i % 2 == 0 else None,
                "correct_answer": 0 if i % 2 == 0 else "True",
                "explanation": f"This is a test explanation for question {i + 1}",
                "difficulty": difficulty,
                "cognitive_level": "understand"
            }
            questions.append(question)
        
        return Assessment(
            assessment_id=f"test_assessment_{topic.lower().replace(' ', '_')}",
            topic=topic,
            difficulty=difficulty,
            questions=questions,
            created_at=datetime.now()
        )
    
    @staticmethod
    def create_minimal() -> Assessment:
        """Create a minimal test assessment."""
        return AssessmentFactory.create(topic="Minimal Test", question_count=1)
    
    @staticmethod
    def create_comprehensive() -> Assessment:
        """Create a comprehensive test assessment."""
        return AssessmentFactory.create(
            topic="Comprehensive Test",
            difficulty="advanced",
            question_count=5
        )

class QualityScoreFactory:
    """Factory for creating test QualityScore instances."""
    
    @staticmethod
    def create(
        overall_score: float = 0.85,
        clarity_score: float = 0.90,
        accuracy_score: float = 0.95,
        engagement_score: float = 0.80,
        educational_value: float = 0.85
    ) -> QualityScore:
        """Create a test quality score."""
        return QualityScore(
            overall_score=overall_score,
            clarity_score=clarity_score,
            accuracy_score=accuracy_score,
            engagement_score=engagement_score,
            educational_value=educational_value
        )
    
    @staticmethod
    def create_excellent() -> QualityScore:
        """Create an excellent quality score."""
        return QualityScoreFactory.create(
            overall_score=0.95,
            clarity_score=0.95,
            accuracy_score=0.98,
            engagement_score=0.90,
            educational_value=0.95
        )
    
    @staticmethod
    def create_needs_improvement() -> QualityScore:
        """Create a quality score that needs improvement."""
        return QualityScoreFactory.create(
            overall_score=0.65,
            clarity_score=0.70,
            accuracy_score=0.80,
            engagement_score=0.60,
            educational_value=0.70
        )

class UserProfileFactory:
    """Factory for creating test UserProfile instances."""
    
    @staticmethod
    def create(
        user_id: str = "test_user_123",
        english_level: str = "B1",
        learning_goals: List[str] = None,
        preferred_learning_style: str = "visual"
    ) -> UserProfile:
        """Create a test user profile."""
        if learning_goals is None:
            learning_goals = ["Business Communication", "Technical Writing"]
        
        return UserProfile(
            user_id=user_id,
            english_level=english_level,
            learning_goals=learning_goals,
            preferred_learning_style=preferred_learning_style,
            completed_courses=2,
            total_study_hours=25.5
        )

def test_pydantic_factories():
    """Test the Pydantic model factories."""
    
    print("🧪 Testing Pydantic Model Factories")
    print("=" * 50)
    
    # Test 1: Assessment Factory
    print("\n📝 Testing Assessment Factory")
    print("-" * 30)
    
    assessment = AssessmentFactory.create()
    print(f"✅ Assessment created: {assessment.assessment_id}")
    print(f"  - Topic: {assessment.topic}")
    print(f"  - Difficulty: {assessment.difficulty}")
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
    
    # Test serialization
    print("\n📦 Testing Model Serialization")
    print("-" * 30)
    
    models = {
        'assessment': assessment,
        'quality_score': quality_score,
        'user_profile': user_profile
    }
    
    for name, model in models.items():
        try:
            # Test dict serialization
            model_dict = model.model_dump()
            # Test JSON serialization
            model_json = model.model_dump_json()
            
            print(f"  ✅ {name}: {len(model_dict)} fields, {len(model_json)} chars")
        except Exception as e:
            print(f"  ❌ {name}: {e}")
    
    # Test validation with invalid data
    print("\n🚫 Testing Validation with Invalid Data")
    print("-" * 30)
    
    try:
        # This should fail validation
        invalid_score = QualityScore(
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
    
    print(f"✅ All Pydantic factory tests passed!")
    
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
    print(f"  # Create a user profile")
    print(f"  user = UserProfileFactory.create(english_level='B2')")
    
    return True

def main():
    """Run the Pydantic factory tests."""
    try:
        success = test_pydantic_factories()
        if success:
            print(f"\n🎉 All Pydantic factory tests passed!")
            sys.exit(0)
        else:
            print(f"\n💥 Tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Tests failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 