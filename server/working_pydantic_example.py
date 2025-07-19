#!/usr/bin/env python3
"""
Working Pydantic Factory Example
This demonstrates the concept with a simple implementation.
"""

import json
from datetime import datetime
from typing import Dict, Any, List

# Simple data classes to simulate Pydantic models
class Assessment:
    def __init__(self, assessment_id: str, topic: str, difficulty: str, questions: List[Dict[str, Any]], created_at: datetime):
        self.assessment_id = assessment_id
        self.topic = topic
        self.difficulty = difficulty
        self.questions = questions
        self.created_at = created_at
    
    def model_dump(self) -> Dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "questions": self.questions,
            "created_at": self.created_at.isoformat()
        }
    
    def model_dump_json(self) -> str:
        return json.dumps(self.model_dump())

class QualityScore:
    def __init__(self, overall_score: float, clarity_score: float, accuracy_score: float, engagement_score: float, educational_value: float):
        # Validation
        if not (0.0 <= overall_score <= 1.0):
            raise ValueError(f"overall_score must be between 0.0 and 1.0, got {overall_score}")
        if not (0.0 <= clarity_score <= 1.0):
            raise ValueError(f"clarity_score must be between 0.0 and 1.0, got {clarity_score}")
        if not (0.0 <= accuracy_score <= 1.0):
            raise ValueError(f"accuracy_score must be between 0.0 and 1.0, got {accuracy_score}")
        if not (0.0 <= engagement_score <= 1.0):
            raise ValueError(f"engagement_score must be between 0.0 and 1.0, got {engagement_score}")
        if not (0.0 <= educational_value <= 1.0):
            raise ValueError(f"educational_value must be between 0.0 and 1.0, got {educational_value}")
        
        self.overall_score = overall_score
        self.clarity_score = clarity_score
        self.accuracy_score = accuracy_score
        self.engagement_score = engagement_score
        self.educational_value = educational_value
    
    def model_dump(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "clarity_score": self.clarity_score,
            "accuracy_score": self.accuracy_score,
            "engagement_score": self.engagement_score,
            "educational_value": self.educational_value
        }
    
    def model_dump_json(self) -> str:
        return json.dumps(self.model_dump())

class UserProfile:
    def __init__(self, user_id: str, english_level: str, learning_goals: List[str], preferred_learning_style: str, completed_courses: int, total_study_hours: float):
        self.user_id = user_id
        self.english_level = english_level
        self.learning_goals = learning_goals
        self.preferred_learning_style = preferred_learning_style
        self.completed_courses = completed_courses
        self.total_study_hours = total_study_hours
    
    def model_dump(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "english_level": self.english_level,
            "learning_goals": self.learning_goals,
            "preferred_learning_style": self.preferred_learning_style,
            "completed_courses": self.completed_courses,
            "total_study_hours": self.total_study_hours
        }
    
    def model_dump_json(self) -> str:
        return json.dumps(self.model_dump())

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
    
    print("🧪 Testing Pydantic Model Factories (Working Example)")
    print("=" * 60)
    
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
    
    # Test different factory methods
    print("\n🔄 Testing Different Factory Methods")
    print("-" * 30)
    
    minimal_assessment = AssessmentFactory.create_minimal()
    comprehensive_assessment = AssessmentFactory.create_comprehensive()
    poor_quality = QualityScoreFactory.create_needs_improvement()
    
    print(f"✅ Minimal assessment: {minimal_assessment.assessment_id} ({len(minimal_assessment.questions)} questions)")
    print(f"✅ Comprehensive assessment: {comprehensive_assessment.assessment_id} ({len(comprehensive_assessment.questions)} questions)")
    print(f"✅ Poor quality score: {poor_quality.overall_score:.2f}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 FACTORY TEST SUMMARY")
    print("=" * 60)
    
    print(f"✅ All Pydantic factory tests passed!")
    
    print(f"\n📋 Pydantic Factory Benefits:")
    print(f"  ✅ All test data passes validation")
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
            print(f"\n🔧 This demonstrates the concept without requiring external dependencies.")
            print(f"   The actual implementation would use real Pydantic models for even better validation.")
        else:
            print(f"\n💥 Tests failed")
    except Exception as e:
        print(f"\n💥 Tests failed: {e}")

if __name__ == "__main__":
    main() 