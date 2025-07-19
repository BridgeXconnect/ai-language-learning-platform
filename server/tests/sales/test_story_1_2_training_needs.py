"""
Integration tests for Story 1.2: Training Needs Assessment

Tests cover:
- CEFR level progression validation
- Training objectives and pain points character limits
- Integration with existing client information step
- API endpoint functionality
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db
from app.domains.auth.models import User
from app.domains.sales.models import CourseRequest, CEFRLevel
from app.domains.auth.services import AuthService
import json

client = TestClient(app)

@pytest.fixture
def test_user(db: Session):
    """Create a test user for authentication"""
    user = User(
        username="test_sales_user",
        first_name="Test",
        last_name="Sales",
        email="test@sales.com",
        password_hash="test_password_hash"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers"""
    token = AuthService.create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_course_request_data():
    """Base course request data"""
    return {
        "company_name": "TechCorp Inc",
        "industry": "Technology", 
        "contact_person": "John Doe",
        "contact_email": "john@techcorp.com",
        "contact_phone": "+1-555-123-4567",
        "project_title": "Business English Training Project",
        "project_description": "Comprehensive business English training program for international communication",
        "participant_count": 15,
        "current_english_level": "A2",
        "target_english_level": "B1",
        "training_goals": "Improve business English communication skills for international meetings and presentations",
        "specific_challenges": "Difficulty with technical vocabulary and presentation confidence",
        # Legacy fields for backwards compatibility
        "cohort_size": 15,
        "current_cefr": "A2",
        "target_cefr": "B1",
        "training_objectives": "Improve business English communication skills for international meetings and presentations",
        "pain_points": "Difficulty with technical vocabulary and presentation confidence",
        "specific_requirements": "Sales team and customer service representatives",
        "delivery_method": "BLENDED",
        "preferred_schedule": "8-weeks"
    }

class TestCEFRProgressionValidation:
    """Test CEFR level progression validation logic"""
    
    def test_valid_cefr_progression_same_level(self, auth_headers, sample_course_request_data):
        """Test valid CEFR progression - same level (reinforcement)"""
        data = sample_course_request_data.copy()
        data.update({
            "current_cefr": "B1",
            "target_cefr": "B1"
        })
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 201
        assert response.json()["current_cefr"] == "B1"
        assert response.json()["target_cefr"] == "B1"
    
    def test_valid_cefr_progression_one_level_up(self, auth_headers, sample_course_request_data):
        """Test valid CEFR progression - one level up"""
        data = sample_course_request_data.copy()
        data.update({
            "current_cefr": "A1",
            "target_cefr": "A2"
        })
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 201
        assert response.json()["current_cefr"] == "A1"
        assert response.json()["target_cefr"] == "A2"
    
    def test_valid_cefr_progression_two_levels_up(self, auth_headers, sample_course_request_data):
        """Test valid CEFR progression - two levels up (accelerated)"""
        data = sample_course_request_data.copy()
        data.update({
            "current_cefr": "A1",
            "target_cefr": "B1"
        })
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 201
        assert response.json()["current_cefr"] == "A1"
        assert response.json()["target_cefr"] == "B1"
    
    def test_invalid_cefr_progression_regression(self, auth_headers, sample_course_request_data):
        """Test invalid CEFR progression - regression not allowed"""
        data = sample_course_request_data.copy()
        data.update({
            "current_cefr": "B2",
            "target_cefr": "B1"
        })
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 422
        assert "must be same or higher than current level" in response.json()["detail"][0]["msg"]
    
    def test_invalid_cefr_progression_too_many_levels(self, auth_headers, sample_course_request_data):
        """Test invalid CEFR progression - more than 2 levels jump"""
        data = sample_course_request_data.copy()
        data.update({
            "current_cefr": "A1",
            "target_cefr": "C1"
        })
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 422
        assert "max 2 levels progression" in response.json()["detail"][0]["msg"]

class TestTrainingObjectivesValidation:
    """Test training objectives character limit validation"""
    
    def test_valid_training_objectives_length(self, auth_headers, sample_course_request_data):
        """Test valid training objectives within character limit"""
        data = sample_course_request_data.copy()
        data["training_objectives"] = "A" * 500  # Exactly 500 characters
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 201
        assert len(response.json()["training_objectives"]) == 500
    
    def test_invalid_training_objectives_too_long(self, auth_headers, sample_course_request_data):
        """Test invalid training objectives exceeding character limit"""
        data = sample_course_request_data.copy()
        data["training_objectives"] = "A" * 501  # 501 characters - too long
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 422
        assert "at most 500 characters" in response.json()["detail"][0]["msg"]
    
    def test_minimum_training_objectives_length(self, auth_headers, sample_course_request_data):
        """Test minimum training objectives length requirement"""
        data = sample_course_request_data.copy()
        data["training_objectives"] = "Short"  # Less than 10 characters
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 422

class TestPainPointsValidation:
    """Test pain points character limit validation"""
    
    def test_valid_pain_points_length(self, auth_headers, sample_course_request_data):
        """Test valid pain points within character limit"""
        data = sample_course_request_data.copy()
        data["pain_points"] = "B" * 300  # Exactly 300 characters
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 201
        assert len(response.json()["pain_points"]) == 300
    
    def test_invalid_pain_points_too_long(self, auth_headers, sample_course_request_data):
        """Test invalid pain points exceeding character limit"""
        data = sample_course_request_data.copy()
        data["pain_points"] = "B" * 301  # 301 characters - too long
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 422
        assert "at most 300 characters" in response.json()["detail"][0]["msg"]
    
    def test_optional_pain_points(self, auth_headers, sample_course_request_data):
        """Test that pain points are optional"""
        data = sample_course_request_data.copy()
        data["pain_points"] = None
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 201
        assert response.json()["pain_points"] is None

class TestParticipantCountValidation:
    """Test participant count validation"""
    
    def test_valid_participant_count_range(self, auth_headers, sample_course_request_data):
        """Test valid participant count within range"""
        for count in [1, 50, 100]:
            data = sample_course_request_data.copy()
            data["cohort_size"] = count
            
            response = client.post("/api/sales/course-requests", 
                                 json=data, 
                                 headers=auth_headers)
            
            assert response.status_code == 201
            assert response.json()["cohort_size"] == count
    
    def test_invalid_participant_count_too_low(self, auth_headers, sample_course_request_data):
        """Test invalid participant count - too low"""
        data = sample_course_request_data.copy()
        data["cohort_size"] = 0
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 422
        assert "must be between 1 and 1000" in response.json()["detail"][0]["msg"]
    
    def test_invalid_participant_count_too_high(self, auth_headers, sample_course_request_data):
        """Test invalid participant count - too high"""
        data = sample_course_request_data.copy()
        data["cohort_size"] = 1001
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 422
        assert "must be between 1 and 1000" in response.json()["detail"][0]["msg"]

class TestSpecificRolesField:
    """Test specific roles field functionality"""
    
    def test_specific_roles_optional(self, auth_headers, sample_course_request_data):
        """Test that specific roles field is optional"""
        data = sample_course_request_data.copy()
        data["specific_requirements"] = None
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 201
        assert response.json()["specific_requirements"] is None
    
    def test_specific_roles_with_content(self, auth_headers, sample_course_request_data):
        """Test specific roles field with content"""
        data = sample_course_request_data.copy()
        data["specific_requirements"] = "Sales team, Customer service, Marketing department"
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 201
        assert "Sales team" in response.json()["specific_requirements"]

class TestDeliveryMethodOptions:
    """Test delivery method options"""
    
    def test_valid_delivery_methods(self, auth_headers, sample_course_request_data):
        """Test all valid delivery methods"""
        valid_methods = ["IN_PERSON", "VIRTUAL", "BLENDED"]
        
        for method in valid_methods:
            data = sample_course_request_data.copy()
            data["delivery_method"] = method
            
            response = client.post("/api/sales/course-requests", 
                                 json=data, 
                                 headers=auth_headers)
            
            assert response.status_code == 201
            assert response.json()["delivery_method"] == method
    
    def test_invalid_delivery_method(self, auth_headers, sample_course_request_data):
        """Test invalid delivery method"""
        data = sample_course_request_data.copy()
        data["delivery_method"] = "INVALID_METHOD"
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 422

class TestIntegrationWithClientInformation:
    """Test integration with client information from Story 1.1"""
    
    def test_complete_request_with_client_and_training_info(self, auth_headers, sample_course_request_data):
        """Test complete request with both client and training information"""
        response = client.post("/api/sales/course-requests", 
                             json=sample_course_request_data, 
                             headers=auth_headers)
        
        assert response.status_code == 201
        result = response.json()
        
        # Verify client information fields
        assert result["company_name"] == "TechCorp Inc"
        assert result["contact_person"] == "John Doe"
        assert result["contact_email"] == "john@techcorp.com"
        
        # Verify training needs fields
        assert result["current_cefr"] == "A2"
        assert result["target_cefr"] == "B1"
        assert result["training_objectives"] == sample_course_request_data["training_objectives"]
        assert result["pain_points"] == sample_course_request_data["pain_points"]
        assert result["cohort_size"] == 15
    
    def test_request_update_training_needs(self, auth_headers, sample_course_request_data, db: Session):
        """Test updating training needs information"""
        # Create initial request
        response = client.post("/api/sales/course-requests", 
                             json=sample_course_request_data, 
                             headers=auth_headers)
        
        assert response.status_code == 201
        request_id = response.json()["id"]
        
        # Update training needs
        update_data = {
            "current_cefr": "B1",
            "target_cefr": "B2",
            "training_objectives": "Advanced business English for executive presentations",
            "cohort_size": 20
        }
        
        response = client.put(f"/api/sales/course-requests/{request_id}", 
                            json=update_data, 
                            headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify updates
        assert result["current_cefr"] == "B1"
        assert result["target_cefr"] == "B2"
        assert result["training_objectives"] == "Advanced business English for executive presentations"
        assert result["cohort_size"] == 20
        
        # Verify client info unchanged
        assert result["company_name"] == "TechCorp Inc"
        assert result["contact_person"] == "John Doe"

class TestErrorHandling:
    """Test error handling and validation messages"""
    
    def test_missing_required_fields(self, auth_headers):
        """Test missing required fields"""
        incomplete_data = {
            "company_name": "Test Company",
            # Missing required fields
        }
        
        response = client.post("/api/sales/course-requests", 
                             json=incomplete_data, 
                             headers=auth_headers)
        
        assert response.status_code == 422
        assert "detail" in response.json()
    
    def test_invalid_email_format(self, auth_headers, sample_course_request_data):
        """Test invalid email format"""
        data = sample_course_request_data.copy()
        data["contact_email"] = "invalid-email"
        
        response = client.post("/api/sales/course-requests", 
                             json=data, 
                             headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_comprehensive_validation_error_response(self, auth_headers):
        """Test comprehensive validation error response"""
        invalid_data = {
            "company_name": "A",  # Too short
            "contact_email": "invalid-email",  # Invalid format
            "cohort_size": 0,  # Too low
            "current_cefr": "B2",
            "target_cefr": "A1",  # Invalid progression
            "training_objectives": "Short",  # Too short
            "pain_points": "X" * 301,  # Too long
        }
        
        response = client.post("/api/sales/course-requests", 
                             json=invalid_data, 
                             headers=auth_headers)
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert len(errors) > 1  # Multiple validation errors 