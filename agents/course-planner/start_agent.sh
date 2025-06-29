#!/bin/bash
# Easy script to start the Course Planner Agent

echo "🚀 Course Planner Agent Startup Script"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -f "minimal_server.py" ]; then
    echo "❌ Error: minimal_server.py not found"
    echo "Please run this script from the agents/course-planner directory"
    echo ""
    echo "To fix this, run:"
    echo "cd agents/course-planner"
    echo "./start_agent.sh"
    exit 1
fi

# Check if server is already running
if pgrep -f "minimal_server.py" > /dev/null; then
    echo "⚠️  Agent is already running!"
    echo ""
    echo "To test it, try:"
    echo "curl http://localhost:8101/health"
    echo ""
    echo "To stop it, run:"
    echo "pkill -f minimal_server.py"
    exit 0
fi

echo "🔧 Starting Course Planner Agent..."
echo "Server will be available at: http://localhost:8101"
echo ""

# Start the server
python minimal_server.py &
SERVER_PID=$!

echo "✅ Agent started with PID: $SERVER_PID"
echo ""
echo "🧪 Quick Test Commands:"
echo "======================"
echo ""
echo "1. Health Check:"
echo "   curl http://localhost:8101/health | python -m json.tool"
echo ""
echo "2. Test Course Planning:"
echo "   curl -X POST http://localhost:8101/plan-course -H \"Content-Type: application/json\" -d @test_request.json | python -m json.tool"
echo ""
echo "3. Stop the Agent:"
echo "   pkill -f minimal_server.py"
echo ""
echo "🎯 Agent is ready for testing!" 