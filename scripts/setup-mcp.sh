#!/bin/bash

# MCP (Model Context Protocol) Setup Script
# Configures MCP servers for each agent to enable IDE integration

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

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

# Function to install MCP dependencies
install_mcp_dependencies() {
    print_status "Installing MCP dependencies..."
    
    for agent in "orchestrator" "course-planner" "content-creator" "quality-assurance"; do
        local agent_dir="$PROJECT_ROOT/agents/$agent"
        
        if [ -d "$agent_dir" ]; then
            print_status "Installing MCP for $agent..."
            cd "$agent_dir"
            
            # Install MCP server package if not already installed
            pip install mcp >/dev/null 2>&1 || {
                print_error "Failed to install MCP for $agent"
                return 1
            }
            
            print_success "MCP installed for $agent"
        else
            print_warning "Agent directory not found: $agent_dir"
        fi
    done
}

# Function to create MCP configuration for Claude Desktop
create_mcp_config() {
    print_status "Creating MCP configuration for Claude Desktop..."
    
    local config_dir="$HOME/.config/claude-desktop"
    local config_file="$config_dir/mcp_servers.json"
    
    # Create config directory if it doesn't exist
    mkdir -p "$config_dir"
    
    # Create MCP configuration
    cat > "$config_file" << EOF
{
  "mcpServers": {
    "agent-orchestrator": {
      "command": "python",
      "args": ["$PROJECT_ROOT/agents/orchestrator/mcp_server.py"],
      "env": {
        "PYTHONPATH": "$PROJECT_ROOT/agents/orchestrator",
        "OPENAI_API_KEY": "\${OPENAI_API_KEY}",
        "ANTHROPIC_API_KEY": "\${ANTHROPIC_API_KEY}",
        "DATABASE_URL": "\${DATABASE_URL}"
      }
    },
    "course-planner": {
      "command": "python",
      "args": ["$PROJECT_ROOT/agents/course-planner/mcp_server.py"],
      "env": {
        "PYTHONPATH": "$PROJECT_ROOT/agents/course-planner",
        "OPENAI_API_KEY": "\${OPENAI_API_KEY}",
        "ANTHROPIC_API_KEY": "\${ANTHROPIC_API_KEY}",
        "DATABASE_URL": "\${DATABASE_URL}"
      }
    },
    "content-creator": {
      "command": "python",
      "args": ["$PROJECT_ROOT/agents/content-creator/mcp_server.py"],
      "env": {
        "PYTHONPATH": "$PROJECT_ROOT/agents/content-creator",
        "OPENAI_API_KEY": "\${OPENAI_API_KEY}",
        "ANTHROPIC_API_KEY": "\${ANTHROPIC_API_KEY}",
        "DATABASE_URL": "\${DATABASE_URL}"
      }
    },
    "quality-assurance": {
      "command": "python",
      "args": ["$PROJECT_ROOT/agents/quality-assurance/mcp_server.py"],
      "env": {
        "PYTHONPATH": "$PROJECT_ROOT/agents/quality-assurance",
        "OPENAI_API_KEY": "\${OPENAI_API_KEY}",
        "ANTHROPIC_API_KEY": "\${ANTHROPIC_API_KEY}",
        "DATABASE_URL": "\${DATABASE_URL}"
      }
    }
  }
}
EOF

    print_success "MCP configuration created at $config_file"
}

# Function to test MCP server functionality
test_mcp_servers() {
    print_status "Testing MCP server functionality..."
    
    for agent in "orchestrator" "course-planner" "content-creator" "quality-assurance"; do
        local agent_dir="$PROJECT_ROOT/agents/$agent"
        local mcp_server="$agent_dir/mcp_server.py"
        
        if [ -f "$mcp_server" ]; then
            print_status "Testing MCP server for $agent..."
            
            # Test if the MCP server can be imported
            cd "$agent_dir"
            python -c "import mcp_server; print('MCP server import successful')" 2>/dev/null && {
                print_success "$agent MCP server is working"
            } || {
                print_error "$agent MCP server has issues"
            }
        else
            print_warning "MCP server not found for $agent: $mcp_server"
        fi
    done
}

# Function to create launch scripts for individual MCP servers
create_mcp_launch_scripts() {
    print_status "Creating MCP launch scripts..."
    
    local scripts_dir="$PROJECT_ROOT/scripts/mcp"
    mkdir -p "$scripts_dir"
    
    for agent in "orchestrator" "course-planner" "content-creator" "quality-assurance"; do
        local launch_script="$scripts_dir/start-$agent-mcp.sh"
        
        cat > "$launch_script" << EOF
#!/bin/bash

# MCP Server Launch Script for $agent
# Run this to start the MCP server for IDE integration

set -e

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="\$(dirname "\$(dirname "\$SCRIPT_DIR")")"
AGENT_DIR="\$PROJECT_ROOT/agents/$agent"

# Load environment variables
if [ -f "\$PROJECT_ROOT/.env" ]; then
    export \$(grep -v '^#' "\$PROJECT_ROOT/.env" | xargs)
fi

# Change to agent directory
cd "\$AGENT_DIR"

# Set Python path
export PYTHONPATH="\$AGENT_DIR:\$PYTHONPATH"

# Start MCP server
echo "Starting MCP server for $agent..."
echo "Agent directory: \$AGENT_DIR"
echo "Python path: \$PYTHONPATH"

python mcp_server.py
EOF

        chmod +x "$launch_script"
        print_success "Created launch script for $agent: $launch_script"
    done
}

# Function to show MCP setup instructions
show_setup_instructions() {
    print_status "📋 MCP Setup Instructions"
    print_status "=========================="
    echo ""
    
    print_status "1. Claude Desktop Configuration:"
    echo "   MCP configuration has been created at: $HOME/.config/claude-desktop/mcp_servers.json"
    echo ""
    
    print_status "2. Environment Variables:"
    echo "   Make sure your .env file contains:"
    echo "   - OPENAI_API_KEY=your_key_here"
    echo "   - ANTHROPIC_API_KEY=your_key_here"
    echo "   - DATABASE_URL=your_database_url_here"
    echo ""
    
    print_status "3. Restart Claude Desktop:"
    echo "   Restart Claude Desktop to load the new MCP servers"
    echo ""
    
    print_status "4. Verify MCP Integration:"
    echo "   In Claude Desktop, you should see the following tools available:"
    echo "   - Agent Orchestrator tools (orchestrate_course_generation, check_agents_health, etc.)"
    echo "   - Course Planner tools (plan_course, analyze_sop, etc.)"
    echo "   - Content Creator tools (create_lesson_content, generate_exercises, etc.)"
    echo "   - Quality Assurance tools (review_content, validate_cefr_alignment, etc.)"
    echo ""
    
    print_status "5. Manual MCP Server Testing:"
    echo "   You can test individual MCP servers using:"
    echo "   - ./scripts/mcp/start-orchestrator-mcp.sh"
    echo "   - ./scripts/mcp/start-course-planner-mcp.sh"
    echo "   - ./scripts/mcp/start-content-creator-mcp.sh"
    echo "   - ./scripts/mcp/start-quality-assurance-mcp.sh"
    echo ""
    
    print_success "MCP setup complete! 🎉"
}

# Main execution
main() {
    print_status "🔗 MCP (Model Context Protocol) Setup"
    print_status "AI Language Learning Platform"
    print_status "====================================="
    
    case "${1:-setup}" in
        "setup")
            install_mcp_dependencies || exit 1
            create_mcp_config
            create_mcp_launch_scripts
            test_mcp_servers
            show_setup_instructions
            ;;
            
        "test")
            test_mcp_servers
            ;;
            
        "config")
            create_mcp_config
            print_success "MCP configuration updated"
            ;;
            
        "clean")
            print_status "Cleaning MCP configuration..."
            rm -f "$HOME/.config/claude-desktop/mcp_servers.json"
            rm -rf "$PROJECT_ROOT/scripts/mcp"
            print_success "MCP configuration cleaned"
            ;;
            
        *)
            print_status "Usage: $0 [setup|test|config|clean]"
            print_status ""
            print_status "Commands:"
            print_status "  setup  - Complete MCP setup (default)"
            print_status "  test   - Test MCP server functionality"
            print_status "  config - Update MCP configuration only"
            print_status "  clean  - Remove MCP configuration"
            ;;
    esac
}

main "$@"