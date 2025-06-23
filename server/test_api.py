import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code} - {response.json()}")
    return response.status_code == 200

def test_user_registration():
    """Test user registration"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"User Registration: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200

def test_user_login():
    """Test user login"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"User Login: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Login successful, token received")
        return data["access_token"]
    else:
        print(f"Error: {response.text}")
    return None

def test_course_creation(token):
    """Test course creation"""
    headers = {"Authorization": f"Bearer {token}"}
    course_data = {
        "title": "Test Course",
        "description": "A test course for API testing",
        "cefr_level": "B1"
    }
    
    response = requests.post(f"{BASE_URL}/courses/", json=course_data, headers=headers)
    print(f"Course Creation: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Course created with ID: {data['id']}")
        return data["id"]
    else:
        print(f"Error: {response.text}")
    return None

def test_get_courses(token):
    """Test getting courses"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/courses/", headers=headers)
    print(f"Get Courses: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} courses")
        for course in data:
            print(f"  - {course['title']} (ID: {course['id']}, Status: {course['status']})")
    else:
        print(f"Error: {response.text}")

def test_course_module_creation(token, course_id):
    """Test module creation"""
    headers = {"Authorization": f"Bearer {token}"}
    module_data = {
        "title": "Test Module",
        "description": "A test module",
        "sequence_number": 1
    }
    
    response = requests.post(f"{BASE_URL}/courses/{course_id}/modules", json=module_data, headers=headers)
    print(f"Module Creation: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Module created with ID: {data['id']}")
        return data["id"]
    else:
        print(f"Error: {response.text}")
    return None

def test_sales_course_request_creation(token):
    """Test creating a course request"""
    print("\n=== Testing Sales Course Request Creation ===")
    
    request_data = {
        "company_name": "Test Company Inc",
        "industry": "Technology",
        "contact_person": "Jane Doe",
        "contact_email": "jane.doe@testcompany.com",
        "contact_phone": "+1-555-1234",
        "cohort_size": 20,
        "current_cefr": "A2",
        "target_cefr": "B1",
        "training_objectives": "Improve business communication skills for the sales team",
        "pain_points": "Team struggles with client presentations and email communication",
        "specific_requirements": "Focus on presentation skills and formal writing",
        "course_length_hours": 50,
        "lessons_per_module": 5,
        "delivery_method": "blended",
        "preferred_schedule": "2 sessions per week, 2 hours each",
        "priority": "high"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/sales/course-requests",
        json=request_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Created course request ID: {data['id']}")
        print(f"Company: {data['company_name']}")
        print(f"Status: {data['status']}")
        return data['id']
    else:
        print(f"Error: {response.text}")
        return None

def test_sales_get_course_requests(token):
    """Test getting course requests"""
    print("\n=== Testing Get Course Requests ===")
    
    response = requests.get(
        f"{BASE_URL}/api/sales/course-requests",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} course requests")
        for request in data[:3]:  # Show first 3
            print(f"- ID: {request['id']}, Company: {request['company_name']}, Status: {request['status']}")
        return data
    else:
        print(f"Error: {response.text}")
        return []

def test_sales_dashboard_stats(token):
    """Test getting sales dashboard statistics"""
    print("\n=== Testing Sales Dashboard Stats ===")
    
    response = requests.get(
        f"{BASE_URL}/api/sales/dashboard-stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Requests: {data['total_requests']}")
        print(f"Active Requests: {data['active_requests']}")
        print(f"Completed Requests: {data['completed_requests']}")
        print(f"Conversion Rate: {data['conversion_rate']}%")
        print(f"Avg Processing Time: {data['avg_processing_time_days']} days")
        print(f"Priority Breakdown: {data['priority_breakdown']}")
        return data
    else:
        print(f"Error: {response.text}")
        return None

def test_sales_submit_request(token, request_id):
    """Test submitting a course request"""
    print(f"\n=== Testing Submit Course Request {request_id} ===")
    
    response = requests.post(
        f"{BASE_URL}/api/sales/course-requests/{request_id}/submit",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Message: {data['message']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_sales_client_feedback(token, request_id):
    """Test creating client feedback"""
    print(f"\n=== Testing Client Feedback for Request {request_id} ===")
    
    feedback_data = {
        "feedback_type": "initial",
        "rating": 4,
        "feedback_text": "The proposed curriculum looks comprehensive. We'd like to add more focus on technical writing.",
        "areas_of_concern": "Technical documentation, report writing",
        "suggestions": "Include more hands-on writing exercises and templates",
        "feedback_by": "Jane Doe",
        "feedback_email": "jane.doe@testcompany.com"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/sales/course-requests/{request_id}/feedback",
        json=feedback_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Created feedback ID: {data['id']}")
        print(f"Rating: {data['rating']}/5")
        print(f"Feedback: {data['feedback_text'][:100]}...")
        return data['id']
    else:
        print(f"Error: {response.text}")
        return None

def run_tests():
    """Run all API tests"""
    print("Starting API Tests...")
    
    # Test health check
    test_health_check()
    
    # Test user registration and login
    test_user_registration()
    token = test_user_login()
    
    if not token:
        print("Failed to get authentication token. Stopping tests.")
        return
    
    # Test course operations
    course_id = test_course_creation(token)
    test_get_courses(token)
    
    if course_id:
        module_id = test_course_module_creation(token, course_id)
    
    # Test sales operations
    request_id = test_sales_course_request_creation(token)
    test_sales_get_course_requests(token)
    test_sales_dashboard_stats(token)
    
    if request_id:
        test_sales_submit_request(token, request_id)
        test_sales_client_feedback(token, request_id)
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    run_tests() 