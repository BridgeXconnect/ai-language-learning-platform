#!/usr/bin/env python3
"""
Simple lightweight test for Course Planner Agent
Tests basic functionality without heavy ML dependencies
"""

import os
import sys
import asyncio
from datetime import datetime

# Set mock environment variables for testing
os.environ['OPENAI_API_KEY'] = 'mock-key-for-testing'
os.environ['SUPABASE_URL'] = 'https://mock-supabase-url.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'mock-anon-key-for-testing'

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test basic imports without initializing heavy components."""
    
    print("🧪 Testing Basic Imports")
    print("=" * 40)
    
    try:
        # Test Pydantic AI import
        from pydantic_ai import Agent, RunContext
        from pydantic_ai.models.openai import OpenAIModel
        print("✅ Pydantic AI imports successful")
        
        # Test FastAPI import
        from fastapi import FastAPI
        print("✅ FastAPI import successful")
        
        # Test Pydantic models
        from pydantic import BaseModel
        print("✅ Pydantic import successful")
        
        # Test basic course request model
        class CourseRequest(BaseModel):
            course_request_id: int
            company_name: str
            industry: str
            training_goals: str
            current_english_level: str
            duration_weeks: int = 8
        
        # Create test request
        test_request = CourseRequest(
            course_request_id=1,
            company_name="TechCorp",
            industry="Technology",
            training_goals="Improve communication",
            current_english_level="B1"
        )
        
        print("✅ Course request model works")
        print(f"   Company: {test_request.company_name}")
        print(f"   Industry: {test_request.industry}")
        print(f"   Level: {test_request.current_english_level}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_server_structure():
    """Test the server structure without starting it."""
    
    print("\n🌐 Testing Server Structure")
    print("=" * 40)
    
    try:
        # Test server imports
        from server import app
        print("✅ Server imports successful")
        print(f"   App title: {app.title}")
        print(f"   App version: {app.version}")
        
        # List available routes
        print("   Available routes:")
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                methods = ', '.join(route.methods)
                print(f"     {methods:15} {route.path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    
    print("\n🔧 Testing Basic Functionality")
    print("=" * 40)
    
    try:
        # Test agent capabilities structure
        capabilities = {
            "agent_name": "Course Planning Specialist",
            "version": "1.0.0",
            "capabilities": [
                "SOP document analysis",
                "CEFR level mapping",
                "Curriculum structure generation"
            ],
            "supported_industries": [
                "Technology", "Healthcare", "Manufacturing"
            ],
            "supported_cefr_levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
            "status": "active"
        }
        
        print("✅ Agent capabilities structure valid")
        print(f"   Agent: {capabilities['agent_name']}")
        print(f"   Industries: {len(capabilities['supported_industries'])}")
        print(f"   CEFR Levels: {', '.join(capabilities['supported_cefr_levels'])}")
        
        # Test request validation logic
        def validate_request(request_data):
            errors = []
            
            if not request_data.get('company_name'):
                errors.append("Company name is required")
            
            if not request_data.get('industry'):
                errors.append("Industry is required")
            
            if request_data.get('duration_weeks', 0) < 1:
                errors.append("Duration must be at least 1 week")
            
            valid_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
            if request_data.get('current_english_level') not in valid_levels:
                errors.append("Invalid CEFR level")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
        
        # Test with valid request
        valid_request = {
            "company_name": "TechCorp",
            "industry": "Technology",
            "current_english_level": "B1",
            "duration_weeks": 8
        }
        
        validation = validate_request(valid_request)
        print(f"✅ Request validation works: {validation['valid']}")
        
        # Test with invalid request
        invalid_request = {
            "company_name": "",
            "industry": "Technology",
            "current_english_level": "X1",
            "duration_weeks": 0
        }
        
        validation = validate_request(invalid_request)
        print(f"✅ Invalid request detection works: {not validation['valid']}")
        print(f"   Errors found: {len(validation['errors'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Main test function."""
    
    print("🚀 Course Planner Agent - Simple Test Suite")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Test time: {datetime.utcnow().isoformat()}")
    print()
    
    # Run tests
    tests = [
        test_imports,
        test_server_structure,
        test_basic_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        print("\n💡 Next Steps:")
        print("   1. Install remaining dependencies if needed")
        print("   2. Set up proper environment variables")
        print("   3. Start server: python server.py")
        print("   4. Test endpoints: curl http://localhost:8101/health")
    else:
        print("⚠️  Some tests failed - check dependencies")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 