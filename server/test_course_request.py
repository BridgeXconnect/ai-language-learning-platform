#!/usr/bin/env python3
"""
Test script to create a dummy course request submission
"""

import requests
import json
import sys
import os

# Add the app directory to the path so we can import our models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.domains.sales.schemas import CourseRequestCreateRequest, CEFRLevelEnum, DeliveryMethodEnum, PriorityEnum

# API Configuration
API_BASE_URL = "http://127.0.0.1:8001"
SALES_ENDPOINT = f"{API_BASE_URL}/sales/course-requests"

def get_admin_token():
    """Get authentication token for admin user"""
    login_url = f"{API_BASE_URL}/auth/login"
    
    # Try common admin credentials (you may need to adjust these)
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def create_dummy_course_request():
    """Create a comprehensive dummy course request"""
    
    # Realistic business scenario data
    dummy_request = {
        # Client Information
        "company_name": "TechFlow Solutions Ltd",
        "industry": "Technology & Software Development",
        "contact_person": "Sarah Johnson",
        "contact_email": "sarah.johnson@techflow.com",
        "contact_phone": "+44 20 7123 4567",
        
        # Training Requirements
        "cohort_size": 25,
        "current_cefr": "B1",  # Intermediate level
        "target_cefr": "B2",   # Upper Intermediate (valid progression)
        "training_objectives": "Improve business communication skills for international client meetings, enhance technical documentation writing, develop presentation skills for product demos, and strengthen email communication with global teams. Focus on industry-specific vocabulary and cross-cultural communication competencies.",
        "pain_points": "Team struggles with technical explanations to non-technical clients, lacks confidence in presentations, and experiences miscommunication in written reports. Current English skills limit business expansion opportunities.",
        "specific_requirements": "Need focus on technical vocabulary, presentation skills, and client-facing communication. Prefer interactive learning with real-world scenarios.",
        
        # Course Structure Preferences  
        "course_length_hours": 40,
        "lessons_per_module": 8,
        "delivery_method": "BLENDED",  # Mix of in-person and virtual
        "preferred_schedule": "2 sessions per week, 2 hours each, Tuesday and Thursday evenings 6-8 PM GMT",
        
        # Request Management
        "priority": "NORMAL",
        "internal_notes": "Client is expanding to US market and needs team prepared for Q2 2024 launch. Budget approved, timeline flexible. Previously worked with external training providers but seeking more customized approach."
    }
    
    return dummy_request

def submit_course_request(token, request_data):
    """Submit the course request to the API"""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🚀 Submitting course request...")
        print(f"📡 Endpoint: {SALES_ENDPOINT}")
        print(f"🏢 Company: {request_data['company_name']}")
        print(f"👥 Cohort Size: {request_data['cohort_size']}")
        print(f"📈 CEFR: {request_data['current_cefr']} → {request_data['target_cefr']}")
        print(f"⏱️  Duration: {request_data['course_length_hours']} hours")
        print()
        
        response = requests.post(SALES_ENDPOINT, json=request_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Course request submitted successfully!")
            print(f"📋 Request ID: {result.get('id')}")
            print(f"📊 Status: {result.get('status')}")
            print(f"📅 Created: {result.get('created_at')}")
            print(f"👤 Sales User ID: {result.get('sales_user_id')}")
            print()
            print("🔍 Request Details:")
            print(f"   Company: {result.get('company_name')}")
            print(f"   Contact: {result.get('contact_person')} ({result.get('contact_email')})")
            print(f"   Participants: {result.get('cohort_size')}")
            print(f"   CEFR Level: {result.get('current_cefr')} → {result.get('target_cefr')}")
            print(f"   Priority: {result.get('priority')}")
            print(f"   Delivery: {result.get('delivery_method')}")
            print()
            print("📝 Training Objectives:")
            print(f"   {result.get('training_objectives', '')[:100]}...")
            print()
            print("🎯 Next steps:")
            print("   1. Upload SOP documents via the sales portal")
            print("   2. Review and approve the request")
            print("   3. Generate course content based on requirements")
            return result
            
        else:
            print(f"❌ Submission failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error submitting request: {e}")
        return None

def main():
    print("🧪 Course Request Test Submission")
    print("=" * 50)
    print()
    
    # Step 1: Get authentication token
    print("🔐 Authenticating...")
    token = get_admin_token()
    if not token:
        print("❌ Could not obtain authentication token")
        print("💡 Make sure:")
        print("   1. Backend server is running on port 8001")
        print("   2. Admin user exists with email 'admin@example.com'")
        print("   3. Admin password is 'admin123'")
        return
    
    print("✅ Authentication successful")
    print()
    
    # Step 2: Create dummy request data
    print("📋 Creating dummy course request data...")
    request_data = create_dummy_course_request()
    print("✅ Dummy data prepared")
    print()
    
    # Step 3: Submit the request
    result = submit_course_request(token, request_data)
    
    if result:
        print("🎉 Test completed successfully!")
        print(f"🔗 You can view this request in the sales portal at: http://localhost:3001/sales/requests")
    else:
        print("😞 Test failed - check error messages above")

if __name__ == "__main__":
    main()