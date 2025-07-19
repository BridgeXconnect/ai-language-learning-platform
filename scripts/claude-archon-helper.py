#!/usr/bin/env python3
"""
Claude Code + BMAD + Archon Integration Helper
Automates the creation and deployment of agents using Claude's code generation
"""

import os
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class ClaudeArchonHelper:
    """Helper for automating Archon integration with Claude Code assistance"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def generate_agent_prompt(self, agent_type: str) -> str:
        """Generate Claude prompt for creating specific agent type"""
        
        base_context = f"""
        I need you to create a specialized AI agent for my language learning platform using Archon framework.
        
        Current Architecture:
        - FastAPI backend with Supabase database
        - Next.js frontend  
        - Docker containerized services
        - Existing AI services (ai_service, rag_service, course_generation_service)
        
        Database Schema (relevant tables):
        - course_requests: id, company_name, industry, training_goals, current_english_level
        - sop_documents: id, course_request_id, file_path, processing_status
        - courses: id, title, description, cefr_level, status
        - modules: id, course_id, title, description, order_index
        - lessons: id, module_id, title, content, duration_minutes
        """
        
        agent_specs = {
            "course-planner": {
                "role": "Course Planning Specialist",
                "description": "Analyzes company SOPs and creates comprehensive curriculum structures",
                "responsibilities": [
                    "Analyze uploaded SOP documents for key business processes",
                    "Extract industry-specific vocabulary and scenarios", 
                    "Map content to appropriate CEFR levels",
                    "Create progressive curriculum structures",
                    "Generate module and lesson outlines"
                ],
                "tools_needed": [
                    "sop_document_analyzer",
                    "cefr_level_mapper", 
                    "curriculum_structure_generator",
                    "database_query_tool"
                ],
                "database_interactions": [
                    "Read from course_requests and sop_documents",
                    "Create records in courses and modules tables",
                    "Query existing curriculum templates"
                ]
            },
            
            "content-creator": {
                "role": "Content Generation Specialist", 
                "description": "Creates engaging lessons, exercises, and learning materials",
                "responsibilities": [
                    "Generate lesson content based on curriculum structure",
                    "Create varied exercise types (reading, writing, listening, speaking)",
                    "Incorporate company-specific scenarios and vocabulary",
                    "Ensure content aligns with CEFR standards",
                    "Generate assessments and quizzes"
                ],
                "tools_needed": [
                    "lesson_content_generator",
                    "exercise_creator",
                    "assessment_builder",
                    "multimedia_content_generator"
                ],
                "database_interactions": [
                    "Read curriculum structure from modules table",
                    "Create detailed lesson content in lessons table", 
                    "Generate exercises and assessments"
                ]
            },
            
            "quality-assurance": {
                "role": "Quality Assurance Specialist",
                "description": "Reviews and improves generated course content for quality and effectiveness",
                "responsibilities": [
                    "Review content for CEFR level appropriateness", 
                    "Check grammatical accuracy and clarity",
                    "Validate exercise effectiveness and variety",
                    "Ensure cultural sensitivity and inclusivity",
                    "Provide improvement recommendations"
                ],
                "tools_needed": [
                    "content_quality_analyzer",
                    "cefr_level_validator",
                    "grammar_checker",
                    "cultural_sensitivity_checker"
                ],
                "database_interactions": [
                    "Read generated content from lessons and exercises",
                    "Update content with quality improvements",
                    "Log quality metrics and feedback"
                ]
            }
        }
        
        if agent_type not in agent_specs:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        spec = agent_specs[agent_type]
        
        prompt = f"""
        {base_context}
        
        AGENT TO CREATE: {spec['role']} ({agent_type})
        
        Description: {spec['description']}
        
        Key Responsibilities:
        {chr(10).join(f"- {resp}" for resp in spec['responsibilities'])}
        
        Required Tools:
        {chr(10).join(f"- {tool}" for tool in spec['tools_needed'])}
        
        Database Interactions:
        {chr(10).join(f"- {interaction}" for interaction in spec['database_interactions'])}
        
        Please create:
        1. A complete Pydantic AI agent with proper system prompt
        2. Tool implementations for all required tools
        3. Dockerfile for containerization  
        4. FastAPI server wrapper with health endpoints
        5. MCP server implementation for agent communication
        6. Requirements.txt with all dependencies
        
        The agent should:
        - Connect to Supabase using environment variables
        - Use OpenAI GPT-4 as the language model
        - Include comprehensive error handling and logging
        - Follow the existing code patterns in the platform
        - Be production-ready with proper validation
        
        File structure should be:
        ```
        agents/{agent_type}/
        ├── main.py              # Main agent implementation
        ├── tools.py             # Tool implementations  
        ├── server.py            # FastAPI server wrapper
        ├── mcp_server.py        # MCP server implementation
        ├── Dockerfile           # Container definition
        ├── requirements.txt     # Python dependencies
        └── README.md           # Agent documentation
        ```
        """
        
        return prompt.strip()
    
    def generate_orchestrator_prompt(self) -> str:
        """Generate prompt for creating the agent orchestrator"""
        
        return """
        I need you to create an Agent Orchestrator service that coordinates multiple AI agents in a course generation workflow.
        
        The orchestrator should:
        1. Receive course generation requests from the main FastAPI backend
        2. Coordinate the workflow between 3 agents: course-planner → content-creator → quality-assurance
        3. Handle agent communication and data flow
        4. Provide status updates and error handling
        5. Implement retry logic and fallback mechanisms
        
        Workflow:
        1. Course Planning Agent analyzes SOPs and creates curriculum structure
        2. Content Creator Agent generates lessons and exercises based on curriculum
        3. Quality Assurance Agent reviews and improves the generated content
        4. Return final course to the main backend
        
        The orchestrator should:
        - Use LangGraph for workflow orchestration
        - Implement proper error handling and retries
        - Provide real-time status updates
        - Support both synchronous and asynchronous operations
        - Include comprehensive logging and monitoring
        - Connect to the same Supabase database as other agents
        
        Create:
        1. LangGraph workflow definition
        2. Agent communication layer
        3. FastAPI server with orchestration endpoints
        4. Health monitoring and status reporting
        5. Docker configuration
        6. MCP server for external integration
        
        File structure:
        ```
        agents/orchestrator/
        ├── main.py              # Main orchestrator logic
        ├── workflow.py          # LangGraph workflow definition
        ├── server.py            # FastAPI server
        ├── mcp_server.py        # MCP server
        ├── agent_client.py      # Agent communication client
        ├── Dockerfile           # Container definition
        ├── requirements.txt     # Dependencies
        └── README.md           # Documentation
        ```
        """
    
    def create_bmad_task_tracker(self) -> str:
        """Create BMAD task ID and initialize tracking"""
        
        task_id = f"BMAD-ARCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create BMAD tracking directory
        bmad_dir = self.project_root / ".bmad-core" / "tasks"
        bmad_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize task tracking file
        task_file = bmad_dir / f"{task_id}.json"
        task_data = {
            "task_id": task_id,
            "title": "Archon Agent Integration Automation",
            "created": datetime.now().isoformat(),
            "status": "initiated",
            "phases": {
                "setup": {"status": "pending", "progress": 0},
                "agent_generation": {"status": "pending", "progress": 0},
                "integration": {"status": "pending", "progress": 0},
                "deployment": {"status": "pending", "progress": 0},
                "validation": {"status": "pending", "progress": 0}
            },
            "agents_to_create": ["course-planner", "content-creator", "quality-assurance", "orchestrator"],
            "checkpoints": []
        }
        
        with open(task_file, 'w') as f:
            json.dump(task_data, f, indent=2)
        
        self.logger.info(f"📋 BMAD Task Created: {task_id}")
        return task_id
    
    def update_bmad_progress(self, task_id: str, phase: str, status: str, progress: int = None, notes: str = None):
        """Update BMAD task progress"""
        
        task_file = self.project_root / ".bmad-core" / "tasks" / f"{task_id}.json"
        
        with open(task_file, 'r') as f:
            task_data = json.load(f)
        
        task_data["phases"][phase]["status"] = status
        if progress is not None:
            task_data["phases"][phase]["progress"] = progress
        
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "status": status,
            "notes": notes
        }
        task_data["checkpoints"].append(checkpoint)
        
        with open(task_file, 'w') as f:
            json.dump(task_data, f, indent=2)
        
        self.logger.info(f"📊 BMAD Progress: {phase} -> {status}")
    
    def generate_claude_prompts_file(self):
        """Generate a file with all Claude prompts for easy copy-paste"""
        
        prompts_dir = self.project_root / "scripts" / "claude-prompts"
        prompts_dir.mkdir(exist_ok=True)
        
        # Generate individual agent prompts
        agent_types = ["course-planner", "content-creator", "quality-assurance"]
        
        for agent_type in agent_types:
            prompt = self.generate_agent_prompt(agent_type)
            prompt_file = prompts_dir / f"{agent_type}-agent-prompt.txt"
            
            with open(prompt_file, 'w') as f:
                f.write(prompt)
            
            self.logger.info(f"📝 Generated prompt for {agent_type}: {prompt_file}")
        
        # Generate orchestrator prompt
        orchestrator_prompt = self.generate_orchestrator_prompt()
        orchestrator_file = prompts_dir / "orchestrator-prompt.txt"
        
        with open(orchestrator_file, 'w') as f:
            f.write(orchestrator_prompt)
        
        self.logger.info(f"📝 Generated orchestrator prompt: {orchestrator_file}")
        
        # Create execution guide
        guide_content = """
# Claude Code + Archon Integration Guide

This directory contains prompts to give to Claude Code for automated agent generation.

## Step-by-Step Process:

### 1. Setup Phase
```bash
# Run this helper script first
python scripts/claude-archon-helper.py --setup
```

### 2. Agent Generation Phase
For each agent, copy the corresponding prompt to Claude Code:

1. **Course Planner Agent**: Use `course-planner-agent-prompt.txt`
2. **Content Creator Agent**: Use `content-creator-agent-prompt.txt`  
3. **Quality Assurance Agent**: Use `quality-assurance-agent-prompt.txt`
4. **Agent Orchestrator**: Use `orchestrator-prompt.txt`

### 3. Integration Phase
After generating all agents, ask Claude Code to:

1. Update docker-compose.yml with agent services
2. Modify FastAPI routes to include agent endpoints
3. Create MCP configuration files
4. Set up health monitoring

### 4. Deployment Phase
```bash
# Build and deploy agents
docker-compose build
docker-compose up -d agent-orchestrator
docker-compose up -d course-planner-agent
docker-compose up -d content-creator-agent  
docker-compose up -d quality-assurance-agent
```

### 5. Validation Phase
```bash
# Test agent communication
curl http://localhost:8100/health
curl http://localhost:8101/health
curl http://localhost:8102/health
curl http://localhost:8103/health

# Test course generation workflow
curl -X POST http://localhost:8000/agents/generate-course-with-agents \\
  -H "Content-Type: application/json" \\
  -d '{"course_request_id": 1}'
```

## BMAD Tracking
- Task progress is tracked in `.bmad-core/tasks/`
- Use `update_bmad_progress()` after each phase
- Review checkpoints for debugging and optimization
"""
        
        guide_file = prompts_dir / "README.md"
        with open(guide_file, 'w') as f:
            f.write(guide_content.strip())
        
        self.logger.info("📚 Integration guide created")
        
        return prompts_dir
    
    def setup_mcp_configuration(self):
        """Set up MCP configuration for agent integration"""
        
        mcp_config = {
            "mcpServers": {
                "archon-agents": {
                    "command": "python",
                    "args": [str(self.project_root / "agents" / "orchestrator" / "mcp_server.py")],
                    "env": {
                        "SUPABASE_URL": "${SUPABASE_URL}",
                        "SUPABASE_KEY": "${SUPABASE_KEY}",
                        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
                    }
                }
            }
        }
        
        mcp_file = self.project_root / "mcp-config.json"
        with open(mcp_file, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        self.logger.info(f"🔗 MCP configuration created: {mcp_file}")
    
    def run_setup(self):
        """Run the complete setup process"""
        
        self.logger.info("🚀 Starting Claude + Archon Integration Setup")
        
        # Create BMAD task tracker
        task_id = self.create_bmad_task_tracker()
        
        # Update progress
        self.update_bmad_progress(task_id, "setup", "in_progress", 25, "Generating Claude prompts")
        
        # Generate Claude prompts
        prompts_dir = self.generate_claude_prompts_file()
        
        # Set up MCP configuration
        self.setup_mcp_configuration()
        
        # Create agents directory structure
        agents_dir = self.project_root / "agents"
        agents_dir.mkdir(exist_ok=True)
        
        for agent_type in ["course-planner", "content-creator", "quality-assurance", "orchestrator"]:
            agent_dir = agents_dir / agent_type
            agent_dir.mkdir(exist_ok=True)
            
            # Create placeholder README
            readme_content = f"""# {agent_type.title()} Agent

This agent will be generated using Claude Code with the prompt from:
`scripts/claude-prompts/{agent_type}-agent-prompt.txt`

## Status
- [ ] Agent code generated
- [ ] Dockerfile created  
- [ ] Tools implemented
- [ ] MCP server configured
- [ ] Testing completed
- [ ] Deployed to development

## Next Steps
1. Copy the prompt from claude-prompts directory
2. Paste into Claude Code interface
3. Review and save generated files
4. Test agent functionality
5. Deploy to development environment
"""
            
            with open(agent_dir / "README.md", 'w') as f:
                f.write(readme_content.strip())
        
        # Complete setup phase
        self.update_bmad_progress(task_id, "setup", "completed", 100, "Setup complete, ready for agent generation")
        
        self.logger.info("✅ Setup Complete!")
        self.logger.info(f"📁 Claude prompts available in: {prompts_dir}")
        self.logger.info(f"📋 BMAD Task ID: {task_id}")
        self.logger.info("🎯 Next: Use the prompts with Claude Code to generate agents")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude + Archon Integration Helper")
    parser.add_argument("--setup", action="store_true", help="Run initial setup")
    parser.add_argument("--agent", help="Generate prompt for specific agent")
    parser.add_argument("--task-id", help="BMAD task ID for progress tracking")
    
    args = parser.parse_args()
    
    helper = ClaudeArchonHelper()
    
    if args.setup:
        helper.run_setup()
    elif args.agent:
        prompt = helper.generate_agent_prompt(args.agent)
        print(f"\n=== {args.agent.upper()} AGENT PROMPT ===\n")
        print(prompt)
    else:
        helper.run_setup()

if __name__ == "__main__":
    main() 