#!/bin/bash

# Start Agent System
# This script starts all the agent services for local testing

echo "🚀 Starting AI Language Learning Platform - Agent System"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "server/app/main.py" ]; then
    echo "❌ Error: Please run this script from the root directory of the project"
    exit 1
fi

# Function to start a service in the background
start_service() {
    local service_name=$1
    local command=$2
    local port=$3
    
    echo "🔧 Starting $service_name on port $port..."
    
    # Kill any existing process on the port
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    
    # Start the service
    eval "$command" &
    local pid=$!
    echo "   ✅ $service_name started (PID: $pid)"
    
    # Store PID for cleanup
    echo $pid >> .agent_pids
}

# Create/clear PID file
rm -f .agent_pids
touch .agent_pids

echo ""
echo "📋 Starting services..."
echo ""

# Start Mock Agents (for testing when real agents aren't available)
start_service "Course Planner Agent (Mock)" "cd agents && python mock_agent_server.py planner" 8101
sleep 2

start_service "Content Creator Agent (Mock)" "cd agents && python mock_agent_server.py creator" 8102
sleep 2

start_service "Quality Assurance Agent (Mock)" "cd agents && python mock_agent_server.py qa" 8103
sleep 2

# Start Orchestrator
start_service "Agent Orchestrator" "cd agents/orchestrator && python server.py" 8100
sleep 3

# Start Backend Server
start_service "Backend API Server" "cd server && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" 8000
sleep 3

echo ""
echo "🎉 All services started successfully!"
echo ""
echo "🌐 Service Endpoints:"
echo "   • Backend API:           http://localhost:8000"
echo "   • API Documentation:     http://localhost:8000/docs"
echo "   • Agent Orchestrator:    http://localhost:8100"
echo "   • Course Planner:        http://localhost:8101"
echo "   • Content Creator:       http://localhost:8102"
echo "   • Quality Assurance:     http://localhost:8103"
echo ""
echo "🔧 Frontend Development:"
echo "   In a new terminal, run:"
echo "   cd client && npm run dev"
echo "   Then visit: http://localhost:3000"
echo ""
echo "⚠️  To stop all services, run:"
echo "   ./scripts/stop_agents.sh"
echo ""

# Health check function
health_check() {
    echo "🏥 Performing health checks..."
    echo ""
    
    local services=(
        "Backend API:8000:/health"
        "Orchestrator:8100:/health"
        "Course Planner:8101:/health"
        "Content Creator:8102:/health"
        "Quality Assurance:8103:/health"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r name port endpoint <<< "$service"
        
        echo -n "   Checking $name... "
        
        # Wait a moment for service to be ready
        sleep 1
        
        if curl -s "http://localhost:$port$endpoint" > /dev/null 2>&1; then
            echo "✅ Healthy"
        else
            echo "❌ Not responding"
        fi
    done
    
    echo ""
    echo "💡 If any services show as 'Not responding', they may still be starting up."
    echo "   Wait a few seconds and check manually at the URLs above."
}

# Wait a moment for services to start, then do health check
echo "⏳ Waiting for services to initialize..."
sleep 5
health_check

echo ""
echo "🎯 Quick Test Commands:"
echo "   • Test orchestrator: curl http://localhost:8100/health"
echo "   • Test backend:      curl http://localhost:8000/health"
echo "   • View agent status: curl http://localhost:8100/agents/health"
echo ""
echo "📝 Logs are available in the terminal where you started this script."
echo "📝 Agent PIDs are stored in .agent_pids for cleanup."

# Keep script running to monitor services
echo ""
echo "🔍 Monitoring services... (Press Ctrl+C to stop all services)"
echo ""

cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    
    if [ -f .agent_pids ]; then
        while read pid; do
            if kill -0 $pid 2>/dev/null; then
                kill $pid 2>/dev/null
                echo "   Stopped process $pid"
            fi
        done < .agent_pids
        rm -f .agent_pids
    fi
    
    # Kill any remaining processes on our ports
    for port in 8000 8100 8101 8102 8103; do
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    done
    
    echo "✅ All services stopped"
    exit 0
}

# Set up cleanup on script exit
trap cleanup EXIT

# Monitor services
while true; do
    sleep 10
    
    # Check if any service died unexpectedly
    if [ -f .agent_pids ]; then
        while read pid; do
            if ! kill -0 $pid 2>/dev/null; then
                echo "⚠️  Warning: Service with PID $pid has stopped unexpectedly"
            fi
        done < .agent_pids
    fi
done