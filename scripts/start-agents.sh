#!/bin/bash

# Multi-Agent System Startup Script
# Starts all agent services with proper health checks and dependencies

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"

# Load environment variables
if [ -f "$ENV_FILE" ]; then
    echo -e "${GREEN}Loading environment from $ENV_FILE${NC}"
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo -e "${YELLOW}Warning: .env file not found. Using defaults.${NC}"
    export AGENTS_ENABLED=${AGENTS_ENABLED:-true}
    export OPENAI_API_KEY=${OPENAI_API_KEY:-""}
    export ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-""}
fi

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

# Function to check if service is healthy
check_service_health() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1

    print_status "Checking health of $service_name on port $port..."

    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "http://localhost:$port/health" >/dev/null 2>&1; then
            print_success "$service_name is healthy"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    print_error "$service_name failed health check after $max_attempts attempts"
    return 1
}

# Function to start a single agent
start_agent() {
    local agent_name=$1
    local port=$2
    local agent_dir="$PROJECT_ROOT/agents/$agent_name"

    print_status "Starting $agent_name agent on port $port..."

    if [ ! -d "$agent_dir" ]; then
        print_error "Agent directory not found: $agent_dir"
        return 1
    fi

    cd "$agent_dir"

    # Check if requirements are installed
    if [ -f "requirements.txt" ]; then
        print_status "Installing dependencies for $agent_name..."
        pip install -r requirements.txt >/dev/null 2>&1 || {
            print_error "Failed to install dependencies for $agent_name"
            return 1
        }
    fi

    # Start the agent in background
    AGENT_NAME=$agent_name PORT=$port python server.py > logs/"$agent_name.log" 2>&1 &
    local pid=$!
    echo $pid > ".$agent_name.pid"

    # Wait a moment for startup
    sleep 3

    # Check if process is still running
    if ! kill -0 $pid 2>/dev/null; then
        print_error "$agent_name failed to start (process died)"
        return 1
    fi

    # Check health endpoint
    if check_service_health "$agent_name" "$port"; then
        print_success "$agent_name started successfully (PID: $pid)"
        return 0
    else
        print_error "$agent_name health check failed"
        kill $pid 2>/dev/null || true
        return 1
    fi
}

# Function to stop all agents
stop_agents() {
    print_status "Stopping all agent services..."

    for agent in "orchestrator" "course-planner" "content-creator" "quality-assurance"; do
        local pid_file="$PROJECT_ROOT/agents/$agent/.$agent.pid"
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                print_status "Stopping $agent (PID: $pid)..."
                kill "$pid"
                sleep 2
                if kill -0 "$pid" 2>/dev/null; then
                    print_warning "Force killing $agent..."
                    kill -9 "$pid"
                fi
            fi
            rm -f "$pid_file"
        fi
    done

    print_success "All agents stopped"
}

# Function to show agent status
show_status() {
    print_status "Agent Service Status:"
    
    local agents=("orchestrator:8100" "course-planner:8101" "content-creator:8102" "quality-assurance:8103")
    
    for agent_port in "${agents[@]}"; do
        IFS=':' read -r agent port <<< "$agent_port"
        local pid_file="$PROJECT_ROOT/agents/$agent/.$agent.pid"
        
        printf "%-20s" "$agent:"
        
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                if curl -f -s "http://localhost:$port/health" >/dev/null 2>&1; then
                    echo -e "${GREEN}✅ Running (PID: $pid, Port: $port)${NC}"
                else
                    echo -e "${YELLOW}⚠️  Running but unhealthy (PID: $pid)${NC}"
                fi
            else
                echo -e "${RED}❌ Dead (stale PID file)${NC}"
                rm -f "$pid_file"
            fi
        else
            echo -e "${RED}❌ Not running${NC}"
        fi
    done
}

# Function to create log directories
setup_logging() {
    for agent in "orchestrator" "course-planner" "content-creator" "quality-assurance"; do
        local log_dir="$PROJECT_ROOT/agents/$agent/logs"
        mkdir -p "$log_dir"
    done
}

# Main execution
main() {
    print_status "🎭 Multi-Agent System Management Script"
    print_status "Project: AI Language Learning Platform"
    print_status "========================================="

    case "${1:-start}" in
        "start")
            if [ "${AGENTS_ENABLED:-true}" != "true" ]; then
                print_warning "Agents are disabled in configuration"
                exit 0
            fi

            # Validate API keys
            if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
                print_error "No AI API keys configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY"
                exit 1
            fi

            setup_logging

            print_status "Starting multi-agent system..."

            # Start agents in dependency order
            start_agent "course-planner" "8101" || exit 1
            start_agent "content-creator" "8102" || exit 1
            start_agent "quality-assurance" "8103" || exit 1
            start_agent "orchestrator" "8100" || exit 1

            print_success "🎉 All agents started successfully!"
            print_status "Agent endpoints:"
            print_status "  - Orchestrator:      http://localhost:8100"
            print_status "  - Course Planner:    http://localhost:8101"
            print_status "  - Content Creator:   http://localhost:8102"
            print_status "  - Quality Assurance: http://localhost:8103"
            ;;

        "stop")
            stop_agents
            ;;

        "restart")
            stop_agents
            sleep 3
            main start
            ;;

        "status")
            show_status
            ;;

        "logs")
            local agent=${2:-orchestrator}
            local log_file="$PROJECT_ROOT/agents/$agent/logs/$agent.log"
            if [ -f "$log_file" ]; then
                tail -f "$log_file"
            else
                print_error "Log file not found: $log_file"
            fi
            ;;

        "test")
            print_status "Testing agent connectivity..."
            
            for agent_port in "orchestrator:8100" "course-planner:8101" "content-creator:8102" "quality-assurance:8103"; do
                IFS=':' read -r agent port <<< "$agent_port"
                printf "%-20s" "$agent:"
                
                if curl -f -s "http://localhost:$port/health" >/dev/null 2>&1; then
                    echo -e "${GREEN}✅ Healthy${NC}"
                else
                    echo -e "${RED}❌ Unhealthy${NC}"
                fi
            done
            ;;

        *)
            print_status "Usage: $0 [start|stop|restart|status|logs [agent]|test]"
            print_status ""
            print_status "Commands:"
            print_status "  start    - Start all agent services"
            print_status "  stop     - Stop all agent services"
            print_status "  restart  - Restart all agent services"
            print_status "  status   - Show agent status"
            print_status "  logs     - Show logs for specific agent (default: orchestrator)"
            print_status "  test     - Test agent connectivity"
            ;;
    esac
}

# Handle Ctrl+C gracefully
trap 'print_warning "Received SIGINT, stopping agents..."; stop_agents; exit 0' INT

# Run main function
main "$@"