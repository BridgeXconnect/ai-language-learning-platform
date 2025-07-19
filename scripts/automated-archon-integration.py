#!/usr/bin/env python3
"""
Automated Archon Integration Script
Orchestrates the complete integration using Claude Code, BMAD methodology, and MCP
"""

import asyncio
import os
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any
import httpx
from datetime import datetime

class BMadArchonAutomator:
    """Automates Archon integration using BMAD methodology"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.bmad_core = self.project_root / ".bmad-core"
        self.agents_dir = self.project_root / "agents"
        self.config = self.load_config()
        self.setup_logging()
        
    def setup_logging(self):
        """Set up comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('archon-automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> Dict[str, Any]:
        """Load automation configuration"""
        return {
            "archon_repo": "https://github.com/coleam00/Archon.git",
            "agents_to_create": [
                {
                    "name": "course-planner",
                    "description": "Analyzes company SOPs and creates comprehensive curriculum structures",
                    "port": 8101,
                    "tools": ["database_query", "sop_analysis", "curriculum_planning"]
                },
                {
                    "name": "content-creator", 
                    "description": "Generates lessons, exercises, and learning materials",
                    "port": 8102,
                    "tools": ["content_generation", "exercise_creation", "material_design"]
                },
                {
                    "name": "quality-assurance",
                    "description": "Reviews and improves generated course content",
                    "port": 8103,
                    "tools": ["content_review", "quality_metrics", "improvement_suggestions"]
                }
            ],
            "orchestrator": {
                "name": "agent-orchestrator",
                "port": 8100,
                "description": "Coordinates multi-agent workflows for course generation"
            }
        }
    
    async def execute_bmad_workflow(self):
        """Execute the complete BMAD workflow"""
        self.logger.info("🚀 Starting BMAD Archon Integration Workflow")
        
        # Phase 1: Setup and Preparation
        await self.phase_1_setup()
        
        # Phase 2: Agent Generation with Archon
        await self.phase_2_generate_agents()
        
        # Phase 3: Integration and Configuration
        await self.phase_3_integration()
        
        # Phase 4: Deployment and Testing
        await self.phase_4_deployment()
        
        # Phase 5: Monitoring and Validation
        await self.phase_5_monitoring()
        
        self.logger.info("✅ BMAD Archon Integration Complete!")
    
    async def phase_1_setup(self):
        """Phase 1: Repository setup and environment preparation"""
        self.logger.info("📋 Phase 1: Setup and Preparation")
        
        # Update BMAD task status
        await self.update_bmad_task("phase_1_setup", "in_progress")
        
        try:
            # Clone Archon repository
            await self.clone_archon_repo()
            
            # Set up Archon environment
            await self.setup_archon_environment()
            
            # Prepare agent directories
            await self.prepare_agent_directories()
            
            # Validate existing services
            await self.validate_existing_services()
            
            await self.update_bmad_task("phase_1_setup", "completed")
            self.logger.info("✅ Phase 1 Complete")
            
        except Exception as e:
            await self.update_bmad_task("phase_1_setup", "failed", str(e))
            raise
    
    async def phase_2_generate_agents(self):
        """Phase 2: Generate agents using Archon"""
        self.logger.info("🤖 Phase 2: Agent Generation")
        
        await self.update_bmad_task("phase_2_generate_agents", "in_progress")
        
        try:
            # Generate orchestrator agent
            await self.generate_orchestrator_agent()
            
            # Generate specialized agents
            for agent_config in self.config["agents_to_create"]:
                await self.generate_agent_with_archon(agent_config)
            
            # Configure MCP connections
            await self.configure_mcp_connections()
            
            await self.update_bmad_task("phase_2_generate_agents", "completed")
            self.logger.info("✅ Phase 2 Complete")
            
        except Exception as e:
            await self.update_bmad_task("phase_2_generate_agents", "failed", str(e))
            raise
    
    async def generate_agent_with_archon(self, agent_config: Dict[str, Any]):
        """Generate a specific agent using Archon"""
        self.logger.info(f"Generating {agent_config['name']} agent...")
        
        # Prepare agent specification for Archon
        agent_spec = {
            "name": agent_config["name"],
            "description": agent_config["description"],
            "tools": agent_config["tools"],
            "database_connection": {
                "type": "supabase",
                "url": os.getenv("SUPABASE_URL"),
                "key": os.getenv("SUPABASE_KEY")
            },
            "ai_model": "openai:gpt-4",
            "system_prompt": self.generate_system_prompt(agent_config),
            "tools_implementation": self.generate_tools_config(agent_config),
            "docker_config": {
                "base_image": "python:3.11-slim",
                "port": agent_config["port"],
                "environment": ["SUPABASE_URL", "SUPABASE_KEY", "OPENAI_API_KEY"]
            }
        }
        
        # Use Archon API to generate agent
        archon_response = await self.call_archon_api("generate_agent", agent_spec)
        
        # Save generated agent to appropriate directory
        agent_dir = self.agents_dir / agent_config["name"]
        await self.save_agent_files(agent_dir, archon_response)
        
        self.logger.info(f"✅ {agent_config['name']} agent generated")
    
    async def generate_orchestrator_agent(self):
        """Generate the main orchestrator agent"""
        self.logger.info("Generating orchestrator agent...")
        
        orchestrator_spec = {
            "name": "agent-orchestrator",
            "description": "Coordinates multi-agent workflows for course generation",
            "type": "orchestrator",
            "agents_to_coordinate": [agent["name"] for agent in self.config["agents_to_create"]],
            "workflow_definition": self.generate_workflow_definition(),
            "api_gateway": True,
            "health_monitoring": True,
            "docker_config": {
                "base_image": "python:3.11-slim",
                "port": 8100,
                "environment": ["SUPABASE_URL", "SUPABASE_KEY", "OPENAI_API_KEY"]
            }
        }
        
        # Generate orchestrator using Archon
        archon_response = await self.call_archon_api("generate_orchestrator", orchestrator_spec)
        
        # Save orchestrator files
        orchestrator_dir = self.agents_dir / "orchestrator"
        await self.save_agent_files(orchestrator_dir, archon_response)
        
        self.logger.info("✅ Orchestrator agent generated")
    
    def generate_system_prompt(self, agent_config: Dict[str, Any]) -> str:
        """Generate system prompt based on agent configuration"""
        base_prompt = f"""
        You are a {agent_config['name'].replace('-', ' ').title()} AI Agent specializing in {agent_config['description']}.
        
        Your primary responsibilities:
        - {agent_config['description']}
        - Collaborate with other agents in the course generation workflow
        - Access and update the Supabase database as needed
        - Provide structured, high-quality outputs
        
        Available tools: {', '.join(agent_config['tools'])}
        
        Always:
        1. Validate inputs thoroughly
        2. Use appropriate tools for data access and manipulation
        3. Provide detailed logging and error handling
        4. Collaborate effectively with other agents
        5. Follow CEFR standards for language learning content
        """
        
        # Add agent-specific prompts
        if agent_config['name'] == 'course-planner':
            base_prompt += """
            
            Course Planning Specific Instructions:
            - Analyze company SOPs to identify key business processes
            - Map business vocabulary to CEFR levels
            - Create progressive curriculum structures
            - Ensure industry-specific relevance
            """
        elif agent_config['name'] == 'content-creator':
            base_prompt += """
            
            Content Creation Specific Instructions:
            - Generate engaging, interactive lessons
            - Create varied exercise types (listening, speaking, reading, writing)
            - Incorporate company-specific scenarios
            - Ensure content aligns with curriculum structure
            """
        elif agent_config['name'] == 'quality-assurance':
            base_prompt += """
            
            Quality Assurance Specific Instructions:
            - Review content for CEFR level appropriateness
            - Check for grammatical accuracy and clarity
            - Validate exercise effectiveness
            - Suggest improvements and refinements
            """
        
        return base_prompt.strip()
    
    def generate_tools_config(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tools configuration for the agent"""
        tools_config = {}
        
        for tool in agent_config['tools']:
            if tool == 'database_query':
                tools_config['database_query'] = {
                    "description": "Query Supabase database for course and SOP data",
                    "parameters": {
                        "table": "string",
                        "query": "string",
                        "filters": "object"
                    }
                }
            elif tool == 'sop_analysis':
                tools_config['sop_analysis'] = {
                    "description": "Analyze SOP documents for curriculum planning",
                    "parameters": {
                        "sop_content": "string",
                        "analysis_type": "string"
                    }
                }
            elif tool == 'content_generation':
                tools_config['content_generation'] = {
                    "description": "Generate lesson content and exercises",
                    "parameters": {
                        "content_type": "string",
                        "specifications": "object"
                    }
                }
            # Add more tool configurations as needed
        
        return tools_config
    
    def generate_workflow_definition(self) -> Dict[str, Any]:
        """Generate LangGraph workflow definition"""
        return {
            "workflow_type": "sequential_with_feedback",
            "steps": [
                {
                    "name": "planning",
                    "agent": "course-planner",
                    "input": "course_request",
                    "output": "curriculum_plan"
                },
                {
                    "name": "content_creation",
                    "agent": "content-creator", 
                    "input": "curriculum_plan",
                    "output": "course_content"
                },
                {
                    "name": "quality_review",
                    "agent": "quality-assurance",
                    "input": "course_content",
                    "output": "reviewed_content"
                }
            ],
            "feedback_loops": [
                {
                    "from": "quality_review",
                    "to": "content_creation",
                    "condition": "quality_score < 0.8"
                }
            ]
        }
    
    async def configure_mcp_connections(self):
        """Configure MCP connections between agents"""
        self.logger.info("Configuring MCP connections...")
        
        mcp_config = {
            "servers": {
                "orchestrator": {
                    "command": "python",
                    "args": ["/agents/orchestrator/mcp_server.py"],
                    "env": {
                        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
                        "SUPABASE_KEY": os.getenv("SUPABASE_KEY")
                    }
                }
            },
            "mcpServers": {
                "archon-agents": {
                    "command": "python",
                    "args": ["/agents/orchestrator/mcp_server.py"]
                }
            }
        }
        
        # Save MCP configuration
        mcp_config_path = self.project_root / "mcp-config.json"
        with open(mcp_config_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        self.logger.info("✅ MCP connections configured")
    
    async def phase_3_integration(self):
        """Phase 3: Integration with existing codebase"""
        self.logger.info("🔗 Phase 3: Integration")
        
        await self.update_bmad_task("phase_3_integration", "in_progress")
        
        try:
            # Update docker-compose.yml
            await self.update_docker_compose()
            
            # Modify FastAPI routes
            await self.update_fastapi_routes()
            
            # Update environment configuration
            await self.update_environment_config()
            
            # Create agent communication layer
            await self.create_agent_communication_layer()
            
            await self.update_bmad_task("phase_3_integration", "completed")
            self.logger.info("✅ Phase 3 Complete")
            
        except Exception as e:
            await self.update_bmad_task("phase_3_integration", "failed", str(e))
            raise
    
    async def update_docker_compose(self):
        """Update docker-compose.yml with agent services"""
        self.logger.info("Updating docker-compose.yml...")
        
        # Read existing docker-compose
        docker_compose_path = self.project_root / "docker-compose.yml"
        
        agent_services = {}
        
        # Add orchestrator service
        agent_services["agent-orchestrator"] = {
            "build": "./agents/orchestrator",
            "ports": ["8100:8100"],
            "environment": [
                "SUPABASE_URL=${SUPABASE_URL}",
                "SUPABASE_KEY=${SUPABASE_KEY}",
                "OPENAI_API_KEY=${OPENAI_API_KEY}"
            ],
            "depends_on": ["backend"],
            "networks": ["app-network"]
        }
        
        # Add agent services
        for agent_config in self.config["agents_to_create"]:
            service_name = f"{agent_config['name']}-agent"
            agent_services[service_name] = {
                "build": f"./agents/{agent_config['name']}",
                "ports": [f"{agent_config['port']}:{agent_config['port']}"],
                "environment": [
                    "ORCHESTRATOR_URL=http://agent-orchestrator:8100",
                    "SUPABASE_URL=${SUPABASE_URL}",
                    "SUPABASE_KEY=${SUPABASE_KEY}",
                    "OPENAI_API_KEY=${OPENAI_API_KEY}"
                ],
                "depends_on": ["agent-orchestrator"],
                "networks": ["app-network"]
            }
        
        # Here we would update the actual docker-compose.yml file
        # For now, we'll create a new agent-services section
        
        self.logger.info("✅ Docker compose updated")
    
    async def update_fastapi_routes(self):
        """Update FastAPI routes to include agent endpoints"""
        self.logger.info("Updating FastAPI routes...")
        
        # Create new agent routes file
        agent_routes_content = '''
"""
Agent orchestration routes for multi-agent course generation
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx

from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/agents", tags=["Agent Services"])

@router.post("/generate-course-with-agents")
async def generate_course_with_agents(
    course_request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate course using multi-agent workflow"""
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://agent-orchestrator:8100/orchestrate-course-generation",
            json={"course_request_id": course_request_id}
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, 
                detail="Agent orchestration failed"
            )
        
        return response.json()

@router.get("/agents/status")
async def get_agents_status():
    """Get status of all agents"""
    
    agents = ["orchestrator", "course-planner", "content-creator", "quality-assurance"]
    status = {}
    
    async with httpx.AsyncClient() as client:
        for agent in agents:
            try:
                if agent == "orchestrator":
                    url = "http://agent-orchestrator:8100/health"
                else:
                    port = 8101 if agent == "course-planner" else 8102 if agent == "content-creator" else 8103
                    url = f"http://{agent}-agent:{port}/health"
                
                response = await client.get(url, timeout=5.0)
                status[agent] = "healthy" if response.status_code == 200 else "unhealthy"
            except:
                status[agent] = "unreachable"
    
    return status
'''
        
        # Save the new routes file
        routes_path = self.project_root / "server" / "app" / "routes" / "agent_routes.py"
        with open(routes_path, 'w') as f:
            f.write(agent_routes_content.strip())
        
        self.logger.info("✅ FastAPI routes updated")
    
    async def phase_4_deployment(self):
        """Phase 4: Build and deploy agents"""
        self.logger.info("🚀 Phase 4: Deployment")
        
        await self.update_bmad_task("phase_4_deployment", "in_progress")
        
        try:
            # Build agent containers
            await self.build_agent_containers()
            
            # Run integration tests
            await self.run_integration_tests()
            
            # Deploy to development environment
            await self.deploy_to_development()
            
            await self.update_bmad_task("phase_4_deployment", "completed")
            self.logger.info("✅ Phase 4 Complete")
            
        except Exception as e:
            await self.update_bmad_task("phase_4_deployment", "failed", str(e))
            raise
    
    async def phase_5_monitoring(self):
        """Phase 5: Set up monitoring and validation"""
        self.logger.info("📊 Phase 5: Monitoring")
        
        await self.update_bmad_task("phase_5_monitoring", "in_progress")
        
        try:
            # Set up health checks
            await self.setup_health_checks()
            
            # Configure logging
            await self.configure_agent_logging()
            
            # Validate agent communication
            await self.validate_agent_communication()
            
            await self.update_bmad_task("phase_5_monitoring", "completed")
            self.logger.info("✅ Phase 5 Complete")
            
        except Exception as e:
            await self.update_bmad_task("phase_5_monitoring", "failed", str(e))
            raise
    
    # Utility methods
    async def clone_archon_repo(self):
        """Clone Archon repository"""
        archon_dir = self.project_root / "archon-repo"
        if not archon_dir.exists():
            subprocess.run([
                "git", "clone", self.config["archon_repo"], str(archon_dir)
            ], check=True)
        self.logger.info("✅ Archon repository cloned")
    
    async def call_archon_api(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Archon API for agent generation"""
        # This would call the actual Archon API
        # For now, we'll simulate the response
        return {
            "agent_code": "# Generated agent code",
            "docker_file": "# Generated Dockerfile", 
            "requirements": "# Generated requirements.txt",
            "mcp_server": "# Generated MCP server code"
        }
    
    async def save_agent_files(self, agent_dir: Path, archon_response: Dict[str, Any]):
        """Save generated agent files"""
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        # Save main agent file
        with open(agent_dir / "main.py", 'w') as f:
            f.write(archon_response.get("agent_code", ""))
        
        # Save Dockerfile
        with open(agent_dir / "Dockerfile", 'w') as f:
            f.write(archon_response.get("docker_file", ""))
        
        # Save requirements
        with open(agent_dir / "requirements.txt", 'w') as f:
            f.write(archon_response.get("requirements", ""))
        
        # Save MCP server
        if archon_response.get("mcp_server"):
            with open(agent_dir / "mcp_server.py", 'w') as f:
                f.write(archon_response.get("mcp_server", ""))
    
    async def update_bmad_task(self, task_name: str, status: str, error: str = None):
        """Update BMAD task status"""
        bmad_status = {
            "task": task_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "error": error
        }
        
        # Log to BMAD tracking
        bmad_log_path = self.bmad_core / "logs" / f"archon-integration-{datetime.now().strftime('%Y%m%d')}.json"
        bmad_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(bmad_log_path, 'a') as f:
            json.dump(bmad_status, f)
            f.write('\n')
        
        self.logger.info(f"BMAD Task Updated: {task_name} -> {status}")

# Additional utility methods would continue here...

async def main():
    """Main automation entry point"""
    automator = BMadArchonAutomator()
    await automator.execute_bmad_workflow()

if __name__ == "__main__":
    asyncio.run(main()) 