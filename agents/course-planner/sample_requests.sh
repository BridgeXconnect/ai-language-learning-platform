#!/bin/bash
# Sample API requests for Course Planner Agent
# Server should be running on http://localhost:8101

echo "🚀 Course Planner Agent - Sample API Requests"
echo "=============================================="
echo ""

# Health check
echo "1. 🏥 Health Check:"
echo "curl http://localhost:8101/health"
echo ""

# Get capabilities
echo "2. 📊 Get Capabilities:"
echo "curl http://localhost:8101/capabilities"
echo ""

# Sample course planning request for Tech Company
echo "3. 🎯 Plan Course for Tech Company:"
echo 'curl -X POST http://localhost:8101/plan-course \
  -H "Content-Type: application/json" \
  -d '"'"'{
    "course_request_id": 1,
    "company_name": "TechCorp Solutions",
    "industry": "Technology",
    "training_goals": "Improve business communication skills for software development team",
    "current_english_level": "B1",
    "duration_weeks": 6,
    "target_audience": "Software developers and project managers",
    "specific_needs": "Focus on technical presentations and client communication"
  }'"'"''
echo ""

# Sample course planning request for Healthcare
echo "4. 🏥 Plan Course for Healthcare Company:"
echo 'curl -X POST http://localhost:8101/plan-course \
  -H "Content-Type: application/json" \
  -d '"'"'{
    "course_request_id": 2,
    "company_name": "MedLife Hospital",
    "industry": "Healthcare",
    "training_goals": "Enhance patient communication and medical terminology usage",
    "current_english_level": "A2",
    "duration_weeks": 8,
    "target_audience": "Nurses and medical staff",
    "specific_needs": "Focus on patient interaction and medical documentation"
  }'"'"''
echo ""

# Sample validation request with errors
echo "5. ❌ Test Validation (Invalid Request):"
echo 'curl -X POST http://localhost:8101/validate-request \
  -H "Content-Type: application/json" \
  -d '"'"'{
    "course_request_id": 3,
    "company_name": "",
    "industry": "Technology",
    "training_goals": "",
    "current_english_level": "X1",
    "duration_weeks": 0
  }'"'"''
echo ""

# Sample manufacturing company request
echo "6. 🏭 Plan Course for Manufacturing Company:"
echo 'curl -X POST http://localhost:8101/plan-course \
  -H "Content-Type: application/json" \
  -d '"'"'{
    "course_request_id": 4,
    "company_name": "AutoParts Manufacturing",
    "industry": "Manufacturing",
    "training_goals": "Improve safety communication and quality control discussions",
    "current_english_level": "B2",
    "duration_weeks": 4,
    "target_audience": "Floor supervisors and quality control staff",
    "specific_needs": "Focus on safety protocols and quality standards communication"
  }'"'"''
echo ""

echo "💡 Usage:"
echo "1. Copy any command above"
echo "2. Paste it in your terminal"
echo "3. Add '| python -m json.tool' for pretty JSON formatting"
echo ""
echo "Example: curl http://localhost:8101/health | python -m json.tool"
echo ""
echo "🔧 Server Status:"
curl -s http://localhost:8101/status | python -m json.tool 2>/dev/null || echo "Server not responding - make sure it's running" 