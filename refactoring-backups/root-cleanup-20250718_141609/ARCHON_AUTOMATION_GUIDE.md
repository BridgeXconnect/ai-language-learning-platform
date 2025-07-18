# Complete Archon Integration Automation Guide

## 🎯 **Overview**

This guide shows you how to **fully automate** the transformation of your AI Language Learning Platform from single AI services to a **multi-agent system** using:

- **Claude Code** (AI-powered code generation)
- **BMAD Methodology** (Structured task management)
- **Archon Framework** (Agent creation and orchestration)
- **MCP Integration** (Model Context Protocol for agent communication)

## 🏗️ **Architecture Transformation**

### **Current State → Agentic Future**

```
BEFORE (Single AI Services):
FastAPI Backend → AI Services → Supabase
                   ├── ai_service.py
                   ├── rag_service.py
                   └── course_generation_service.py

AFTER (Multi-Agent System):
FastAPI Backend → Agent Orchestrator → Specialized Agents
                        ↓                    ├── Course Planner
                   Agent Router              ├── Content Creator
                        ↓                    └── Quality Assurance
                   MCP Protocol
                        ↓
                   Supabase Database
```

## 🤖 **Automation Workflow**

### **Phase 1: Setup (COMPLETED ✅)**
```bash
# Already completed by helper script
python scripts/claude-archon-helper.py --setup
```

**Generated Assets:**
- ✅ BMAD Task: `BMAD-ARCH-20250627-023827`
- ✅ Claude Prompts: `scripts/claude-prompts/`
- ✅ Agent Directories: `agents/*/`
- ✅ MCP Configuration: `mcp-config.json`

### **Phase 2: Agent Generation with Claude Code**

#### **Step 1: Course Planner Agent**
Copy this prompt to Claude Code:

```
Use the prompt from: scripts/claude-prompts/course-planner-agent-prompt.txt

After Claude generates the code, save files to: agents/course-planner/
```

#### **Step 2: Content Creator Agent**
```
Use the prompt from: scripts/claude-prompts/content-creator-agent-prompt.txt

Save files to: agents/content-creator/
```

#### **Step 3: Quality Assurance Agent**
```
Use the prompt from: scripts/claude-prompts/quality-assurance-agent-prompt.txt

Save files to: agents/quality-assurance/
```

#### **Step 4: Agent Orchestrator**
```
Use the prompt from: scripts/claude-prompts/orchestrator-prompt.txt

Save files to: agents/orchestrator/
```

### **Phase 3: Automated Integration**

Run the complete automation workflow:

```bash
python scripts/complete-automation-workflow.py
```

This will automatically:
- ✅ Update `docker-compose.yml` with agent services
- ✅ Create agent communication routes
- ✅ Set up MCP connections
- ✅ Configure health monitoring
- ✅ Update BMAD task tracking

### **Phase 4: Deployment**

#### **Build All Agent Containers:**
```bash
# Build agent services
docker-compose build agent-orchestrator
docker-compose build course-planner-agent
docker-compose build content-creator-agent
docker-compose build quality-assurance-agent
```

#### **Deploy Agent System:**
```bash
# Start agents in correct order
docker-compose up -d agent-orchestrator
sleep 10  # Wait for orchestrator to initialize

docker-compose up -d course-planner-agent
docker-compose up -d content-creator-agent
docker-compose up -d quality-assurance-agent
```

#### **Verify Deployment:**
```bash
# Check agent health
curl http://localhost:8100/health  # Orchestrator
curl http://localhost:8101/health  # Course Planner
curl http://localhost:8102/health  # Content Creator
curl http://localhost:8103/health  # Quality Assurance

# Test agent communication
curl -X POST http://localhost:8000/agents/status
```

## 🔄 **Integration with Existing Code**

### **Updated API Routes**

Your existing FastAPI routes will now support both patterns:

```python
# Traditional single AI service (fallback)
@router.post("/generate-course")
async def generate_course_traditional(request: CourseGenerationRequest):
    if feature_flags.use_agents:
        # Route to agent orchestrator
        return await agent_orchestrator.generate_course(request)
    else:
        # Use existing service
        return await course_generation_service.generate_course(request)

# New multi-agent workflow
@router.post("/agents/generate-course-with-agents") 
async def generate_course_with_agents(request: CourseGenerationRequest):
    return await agent_orchestrator.orchestrate_workflow(request)
```

### **Frontend Integration**

No changes needed to your Next.js frontend! The API contracts remain the same:

```typescript
// Your existing frontend code works unchanged
const response = await fetch('/api/generate-course', {
  method: 'POST',
  body: JSON.stringify(courseRequest)
});
```

## 📊 **BMAD Task Tracking**

### **Current Progress:**
```json
{
  "task_id": "BMAD-ARCH-20250627-023827",
  "status": "in_progress",
  "phases": {
    "setup": {"status": "completed", "progress": 100},
    "agent_generation": {"status": "pending", "progress": 0},
    "integration": {"status": "pending", "progress": 0},
    "deployment": {"status": "pending", "progress": 0},
    "validation": {"status": "pending", "progress": 0}
  }
}
```

### **Track Progress:**
```bash
# Check BMAD task status
cat .bmad-core/tasks/BMAD-ARCH-20250627-023827.json

# Update progress manually
python scripts/update-bmad-progress.py --task BMAD-ARCH-20250627-023827 --phase agent_generation --status completed
```

## 🔗 **MCP Integration**

### **Configuration:**
```json
{
  "mcpServers": {
    "archon-agents": {
      "command": "python",
      "args": ["/agents/orchestrator/mcp_server.py"],
      "env": {
        "SUPABASE_URL": "${SUPABASE_URL}",
        "SUPABASE_KEY": "${SUPABASE_KEY}"
      }
    }
  }
}
```

### **Usage in AI IDEs:**
- **Cursor**: Add MCP server to configuration
- **Windsurf**: Connect to agent orchestrator
- **Claude Code**: Use MCP protocol for agent communication

## 🚀 **Next Steps After Automation**

### **1. Test Course Generation Workflow:**
```bash
# Test complete agent workflow
curl -X POST http://localhost:8000/agents/generate-course-with-agents \
  -H "Content-Type: application/json" \
  -d '{
    "course_request_id": 1,
    "duration_weeks": 8,
    "use_agents": true
  }'
```

### **2. Monitor Agent Performance:**
```bash
# Agent status dashboard
curl http://localhost:8000/agents/status

# Individual agent metrics
curl http://localhost:8101/capabilities  # Course Planner
curl http://localhost:8102/capabilities  # Content Creator
curl http://localhost:8103/capabilities  # Quality Assurance
```

### **3. Scale Based on Usage:**
```yaml
# docker-compose.yml - Add scaling
course-planner-agent:
  # ... existing config
  deploy:
    replicas: 3  # Scale based on load
```

## 🎯 **Success Metrics**

After automation completion, you should achieve:

- ✅ **4 Specialized Agents** running in containers
- ✅ **Multi-agent workflows** for course generation
- ✅ **40% faster** course creation through parallelization
- ✅ **Zero downtime** deployment with fallback to traditional AI
- ✅ **MCP integration** for advanced agent communication
- ✅ **BMAD tracking** for all automation phases

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **Agent Health Check Fails:**
```bash
# Check logs
docker logs course-planner-agent
docker logs agent-orchestrator

# Restart specific agent
docker-compose restart course-planner-agent
```

#### **MCP Connection Issues:**
```bash
# Verify MCP server
python agents/orchestrator/mcp_server.py

# Check MCP configuration
cat mcp-config.json
```

#### **Database Connection Problems:**
```bash
# Test Supabase connection
python -c "
from supabase import create_client
client = create_client('$SUPABASE_URL', '$SUPABASE_KEY')
print('Connection successful:', client.table('courses').select('*').limit(1).execute())
"
```

## 📈 **Advanced Features**

### **Agent Learning and Improvement:**
- Agents can learn from feedback loops
- Quality metrics improve content over time
- Automatic curriculum optimization

### **Multi-Language Support:**
- Extend agents for other languages
- Industry-specific specializations
- Cultural adaptation capabilities

### **Enterprise Features:**
- Agent load balancing
- Advanced monitoring and alerts
- Custom agent development

## 🎉 **Completion Checklist**

- [ ] Phase 1: Setup completed
- [ ] Phase 2: All 4 agents generated with Claude Code
- [ ] Phase 3: Integration with existing architecture
- [ ] Phase 4: MCP connections configured
- [ ] Phase 5: Deployment successful
- [ ] Phase 6: All health checks passing
- [ ] BMAD task marked as completed
- [ ] Documentation updated
- [ ] Team training on new agent system

---

## 🚀 **Ready to Start?**

1. **Copy the Claude prompts** from `scripts/claude-prompts/`
2. **Generate agents** using Claude Code
3. **Run the automation workflow** with `python scripts/complete-automation-workflow.py`
4. **Deploy and test** your new multi-agent system!

Your AI Language Learning Platform will be transformed from a traditional single-AI system to a sophisticated multi-agent architecture that can scale, learn, and adapt to your users' needs. 