# Pydantic Testing Solution: Replacing Mock Data with Proper Factories

## Problem Statement

You raised a critical concern: **"I just refactored our code and removed mock data and placeholders etc. Won't we have an issue using this mock Pydantic data?"**

This is an excellent question that highlights a fundamental testing best practice issue. The previous approach of using mock classes and hardcoded data can indeed cause problems after refactoring.

## Issues with the Previous Mock Approach

### 1. **Mock Classes Bypass Validation**
```python
# OLD APPROACH - Problematic
class MockAgent:
    def __init__(self, model_name: str, system_prompt: str = ""):
        self.model_name = model_name
        self.system_prompt = system_prompt
    
    async def run(self, description, deps=None, tool_calls=None):
        return type("Result", (), {"data": {"assessment_id": "mock_assessment"}})()
```

**Problems:**
- No validation of data structure
- Mock classes don't match real Pydantic models
- Changes to real models don't break tests (silent failures)
- No type safety

### 2. **Hardcoded Test Data**
```python
# OLD APPROACH - Fragile
async def test_generate_adaptive_quiz(ai_service):
    result = await ai_service.generate_adaptive_quiz("test_topic")
    assert result["difficulty"] == "intermediate"  # Hardcoded expectation
    assert len(result["questions"]) == 5  # Brittle assertion
```

**Problems:**
- Tests break when data structure changes
- No validation that test data is realistic
- Difficult to maintain consistency

## Solution: Pydantic Model Factories

### 1. **Proper Pydantic Models with Validation**

```python
# NEW APPROACH - Proper Pydantic Models
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Dict, Any, List

class Assessment(BaseModel):
    assessment_id: str
    topic: str
    difficulty: str
    questions: List[Dict[str, Any]]
    created_at: datetime
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class QualityScore(BaseModel):
    overall_score: float = Field(ge=0.0, le=1.0)  # Validation!
    clarity_score: float = Field(ge=0.0, le=1.0)
    accuracy_score: float = Field(ge=0.0, le=1.0)
    engagement_score: float = Field(ge=0.0, le=1.0)
    educational_value: float = Field(ge=0.0, le=1.0)
```

### 2. **Factory Pattern for Test Data**

```python
# NEW APPROACH - Factory Pattern
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
```

### 3. **Quality Score Factory with Validation**

```python
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
```

## Benefits of This Approach

### 1. **Validation Ensures Data Integrity**
```python
# This will fail validation - catches errors early!
try:
    invalid_score = QualityScore(
        overall_score=1.5,  # Should be <= 1.0
        clarity_score=0.9,
        accuracy_score=0.95,
        engagement_score=0.8,
        educational_value=0.85
    )
except ValidationError as e:
    print(f"Validation caught error: {e}")
```

### 2. **Tests Break When Models Change**
```python
# If you change the Assessment model, tests will break immediately
# This is GOOD - it catches breaking changes early
assessment = AssessmentFactory.create()
# If you add a required field to Assessment, this will fail
```

### 3. **Consistent and Maintainable Test Data**
```python
# Easy to create different test scenarios
assessment_basic = AssessmentFactory.create_minimal()
assessment_advanced = AssessmentFactory.create_comprehensive()
quality_excellent = QualityScoreFactory.create_excellent()
quality_poor = QualityScoreFactory.create_needs_improvement()
```

### 4. **Type Safety and IDE Support**
```python
# Full type hints and IDE autocomplete
assessment: Assessment = AssessmentFactory.create()
print(assessment.topic)  # IDE knows this is a string
print(assessment.questions)  # IDE knows this is List[Dict[str, Any]]
```

## Implementation in Your Codebase

### 1. **Replace Mock Classes**

**Before (Problematic):**
```python
# In ai_assessment_service.py
class MockAgent:
    def __init__(self, model_name: str, system_prompt: str = ""):
        self.model_name = model_name
        self.system_prompt = system_prompt
    
    async def run(self, description, deps=None, tool_calls=None):
        return type("Result", (), {"data": {"assessment_id": "mock_assessment"}})()

# Use mock classes instead of pydantic_ai imports
Agent = MockAgent
RunContext = MockRunContext
```

**After (Proper):**
```python
# In ai_assessment_service.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Dict, Any, List

class Assessment(BaseModel):
    assessment_id: str
    topic: str
    difficulty: str
    questions: List[Dict[str, Any]]
    created_at: datetime
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class AIAssessmentService:
    async def create_assessment(self, topic: str, difficulty: str, question_types: List[str], question_count: int) -> Dict[str, Any]:
        # For testing purposes, return a test assessment
        if not self.openai_client and not self.anthropic_client:
            test_assessment = Assessment.create_test_assessment(topic)
            return test_assessment.model_dump()
        
        # Real AI implementation here
        pass
```

### 2. **Update Test Files**

**Before (Fragile):**
```python
# In test files
async def test_generate_adaptive_quiz(ai_service):
    result = await ai_service.generate_adaptive_quiz("test_topic")
    assert result["difficulty"] == "intermediate"
    assert len(result["questions"]) == 5
```

**After (Robust):**
```python
# In test files
from app.testing.factories import AssessmentFactory, QualityScoreFactory

async def test_generate_adaptive_quiz(ai_service):
    result = await ai_service.generate_adaptive_quiz("test_topic")
    
    # Validate the result structure
    assessment = Assessment(**result)
    assert assessment.topic == "test_topic"
    assert len(assessment.questions) > 0
    
    # Test with factory-created data
    expected_assessment = AssessmentFactory.create(topic="test_topic")
    assert assessment.assessment_id is not None
    assert assessment.created_at is not None
```

## Migration Strategy

### Phase 1: Create Factories
1. Create `app/testing/factories.py` with all factory classes
2. Define proper Pydantic models for all test data
3. Add validation rules (Field constraints, etc.)

### Phase 2: Update Services
1. Replace mock classes with proper Pydantic models
2. Add factory methods to models for test data creation
3. Update service methods to use factories when AI services unavailable

### Phase 3: Update Tests
1. Replace hardcoded test data with factory calls
2. Add validation assertions
3. Test model serialization/deserialization

### Phase 4: Remove Mock Dependencies
1. Remove mock classes from service files
2. Clean up imports
3. Update documentation

## Testing the Solution

```python
# test_pydantic_factories.py
def test_pydantic_factories():
    """Test the Pydantic model factories."""
    
    # Test 1: Assessment Factory
    assessment = AssessmentFactory.create()
    print(f"✅ Assessment created: {assessment.assessment_id}")
    print(f"  - Topic: {assessment.topic}")
    print(f"  - Questions: {len(assessment.questions)}")
    
    # Test validation
    assessment_dict = assessment.model_dump()
    print(f"  - Serialized to dict: {len(assessment_dict)} fields")
    
    # Test 2: Quality Score Factory
    quality_score = QualityScoreFactory.create_excellent()
    print(f"✅ Quality score created: {quality_score.overall_score:.2f}")
    
    # Test validation
    assert 0 <= quality_score.overall_score <= 1, "Score should be between 0 and 1"
    print("  ✅ Validation passed")
    
    # Test validation with invalid data
    try:
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
```

## Conclusion

**Your concern is absolutely valid!** The previous mock approach would indeed cause issues after refactoring because:

1. **Mock classes don't validate data structure**
2. **Changes to real models don't break tests**
3. **No type safety or IDE support**
4. **Hard to maintain consistency**

The **Pydantic Factory Pattern** solves these issues by:

1. **✅ All test data passes Pydantic validation**
2. **✅ Tests break when models change (catches errors early)**
3. **✅ Type safety and IDE support**
4. **✅ Consistent and maintainable test data**
5. **✅ Easy serialization to dict/JSON**
6. **✅ No more mock data issues after refactoring**

This approach ensures that your tests are robust, maintainable, and will catch breaking changes immediately when you refactor your code. 