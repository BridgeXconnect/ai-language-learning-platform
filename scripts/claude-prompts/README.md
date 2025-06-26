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
curl -X POST http://localhost:8000/agents/generate-course-with-agents \
  -H "Content-Type: application/json" \
  -d '{"course_request_id": 1}'
```

## BMAD Tracking
- Task progress is tracked in `.bmad-core/tasks/`
- Use `update_bmad_progress()` after each phase
- Review checkpoints for debugging and optimization