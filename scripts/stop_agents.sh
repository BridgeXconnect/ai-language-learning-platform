#!/bin/bash

# Stop Agent System
# This script stops all agent services

echo "🛑 Stopping AI Language Learning Platform - Agent System"
echo "======================================================="

# Function to stop processes on a specific port
stop_port() {
    local port=$1
    local service_name=$2
    
    echo "🔧 Stopping $service_name on port $port..."
    
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo $pids | xargs kill -9 2>/dev/null
        echo "   ✅ Stopped $service_name"
    else
        echo "   ℹ️  No process found on port $port"
    fi
}

# Stop services by PID file if it exists
if [ -f .agent_pids ]; then
    echo "📋 Stopping services by PID..."
    echo ""
    
    while read pid; do
        if kill -0 $pid 2>/dev/null; then
            kill $pid 2>/dev/null
            echo "   ✅ Stopped process $pid"
        else
            echo "   ℹ️  Process $pid already stopped"
        fi
    done < .agent_pids
    
    rm -f .agent_pids
    echo ""
fi

# Stop services by port (backup method)
echo "🔍 Checking and stopping services by port..."
echo ""

stop_port 8000 "Backend API Server"
stop_port 8100 "Agent Orchestrator"
stop_port 8101 "Course Planner Agent"
stop_port 8102 "Content Creator Agent"
stop_port 8103 "Quality Assurance Agent"

# Also check for common Node.js frontend port
stop_port 3000 "Frontend Development Server"

echo ""
echo "🧹 Cleaning up..."

# Remove any remaining PID files
rm -f .agent_pids

# Kill any remaining Python processes that might be agents
pkill -f "mock_agent_server.py" 2>/dev/null || true
pkill -f "agents/orchestrator/server.py" 2>/dev/null || true
pkill -f "uvicorn.*app.main:app" 2>/dev/null || true

echo ""
echo "✅ All agent services stopped successfully!"
echo ""
echo "💡 To start the services again, run:"
echo "   ./scripts/start_agents.sh"
echo ""

# Verify all ports are free
echo "🔍 Verifying ports are free..."
for port in 8000 8100 8101 8102 8103; do
    if lsof -ti:$port >/dev/null 2>&1; then
        echo "   ⚠️  Port $port still has processes running"
    else
        echo "   ✅ Port $port is free"
    fi
done

echo ""
echo "🎯 All done!"