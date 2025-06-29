"""
MCP (Model Context Protocol) server implementation for Agent Orchestrator
Enables AI IDE integration and external workflow management
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from main import AgentOrchestrator, CourseGenerationRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the orchestrator
orchestrator = AgentOrchestrator()

# Create MCP server instance
server = Server("agent-orchestrator")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for the Agent Orchestrator."""
    return [
        Tool(
            name="orchestrate_course_generation",
            description="Orchestrate the complete multi-agent course generation workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_request_id": {"type": "integer", "description": "ID of the course request"},
                    "company_name": {"type": "string", "description": "Name of the company"},
                    "industry": {"type": "string", "description": "Industry sector"},
                    "training_goals": {"type": "string", "description": "Specific training objectives"},
                    "current_english_level": {"type": "string", "description": "Current CEFR level (A1-C2)"},
                    "duration_weeks": {"type": "integer", "description": "Course duration in weeks", "default": 8},
                    "target_audience": {"type": "string", "description": "Target learner group", "default": "Professional staff"},
                    "specific_needs": {"type": "string", "description": "Additional specific requirements", "default": null}
                },
                "required": ["course_request_id", "company_name", "industry", "training_goals", "current_english_level"]
            }
        ),
        Tool(
            name="get_workflow_status",
            description="Get the current status of a workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string", "description": "ID of the workflow to check"}
                },
                "required": ["workflow_id"]
            }
        ),
        Tool(
            name="check_agents_health",
            description="Check the health status of all managed agents",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_orchestrator_metrics",
            description="Get performance metrics and statistics for the orchestrator",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="list_active_workflows",
            description="List all currently active workflows",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="cancel_workflow",
            description="Cancel an active workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string", "description": "ID of the workflow to cancel"}
                },
                "required": ["workflow_id"]
            }
        ),
        Tool(
            name="test_agents",
            description="Test basic functionality of all managed agents",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_agent_capabilities",
            description="Get capabilities of all managed agents",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls for the Agent Orchestrator."""
    
    try:
        logger.info(f"MCP tool called: {name} with arguments: {arguments}")
        
        if name == "orchestrate_course_generation":
            return await handle_orchestrate_course(arguments)
        
        elif name == "get_workflow_status":
            return await handle_get_workflow_status(arguments)
        
        elif name == "check_agents_health":
            return await handle_check_agents_health()
        
        elif name == "get_orchestrator_metrics":
            return await handle_get_metrics()
        
        elif name == "list_active_workflows":
            return await handle_list_workflows()
        
        elif name == "cancel_workflow":
            return await handle_cancel_workflow(arguments)
        
        elif name == "test_agents":
            return await handle_test_agents()
        
        elif name == "get_agent_capabilities":
            return await handle_get_capabilities()
        
        else:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )
                ],
                isError=True
            )
    
    except Exception as e:
        logger.error(f"Tool call failed for {name}: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Tool execution failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_orchestrate_course(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle course generation orchestration."""
    
    try:
        # Create course generation request
        course_request = CourseGenerationRequest(**arguments)
        
        # Execute workflow
        start_time = datetime.utcnow()
        workflow_result = await orchestrator.orchestrate_workflow(course_request)
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Determine success
        success = workflow_result.status == "completed"
        
        # Create result summary
        result_text = f"🎭 Course Generation Workflow: {workflow_result.status.title()}\n\n"
        result_text += f"🏢 Company: {arguments['company_name']}\n"
        result_text += f"🏭 Industry: {arguments['industry']}\n"
        result_text += f"📊 CEFR Level: {arguments['current_english_level']}\n"
        result_text += f"⏱️ Duration: {arguments.get('duration_weeks', 8)} weeks\n"
        result_text += f"🔄 Workflow ID: {workflow_result.workflow_id}\n"
        result_text += f"⚡ Execution Time: {execution_time:.2f} seconds\n\n"
        
        if success:
            result_text += "✅ **Workflow Completed Successfully**\n\n"
            
            # Add stage results
            if workflow_result.planning_result:
                modules = workflow_result.planning_result.get("modules", [])
                result_text += f"📋 Planning: {len(modules)} modules created\n"
            
            if workflow_result.content_result:
                content_stats = workflow_result.content_result.get("metadata", {}).get("content_stats", {})
                lessons = content_stats.get("total_lessons", 0)
                exercises = content_stats.get("total_exercises", 0)
                assessments = content_stats.get("total_assessments", 0)
                result_text += f"📚 Content: {lessons} lessons, {exercises} exercises, {assessments} assessments\n"
            
            if workflow_result.quality_result:
                quality_score = workflow_result.quality_result.get("overall_score", 0)
                approved = workflow_result.quality_result.get("approved_for_release", False)
                result_text += f"🔍 Quality: {quality_score}% score, {'Approved' if approved else 'Needs Review'}\n"
        else:
            result_text += "❌ **Workflow Failed**\n\n"
            if workflow_result.error_message:
                result_text += f"Error: {workflow_result.error_message}\n"
            if workflow_result.failed_stage:
                result_text += f"Failed Stage: {workflow_result.failed_stage}\n"
            result_text += f"Retry Count: {workflow_result.retry_count}\n"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(workflow_result.dict(), indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        logger.error(f"Course orchestration failed: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Course generation orchestration failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_get_workflow_status(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle workflow status requests."""
    
    try:
        workflow_id = arguments["workflow_id"]
        workflow_result = await orchestrator.get_workflow_status(workflow_id)
        
        if not workflow_result:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Workflow {workflow_id} not found"
                    )
                ],
                isError=True
            )
        
        result_text = f"📊 Workflow Status: {workflow_id}\n\n"
        result_text += f"🔄 Status: {workflow_result.status.title()}\n"
        result_text += f"📅 Started: {workflow_result.start_time}\n"
        
        if workflow_result.completion_time:
            result_text += f"✅ Completed: {workflow_result.completion_time}\n"
            result_text += f"⏱️ Duration: {workflow_result.total_duration_seconds:.2f} seconds\n"
        
        if workflow_result.quality_score:
            result_text += f"🎯 Quality Score: {workflow_result.quality_score}%\n"
        
        if workflow_result.approved_for_release is not None:
            status = "Approved" if workflow_result.approved_for_release else "Needs Review"
            result_text += f"✨ Release Status: {status}\n"
        
        # Add stage progress
        result_text += "\n📋 Stage Progress:\n"
        result_text += f"• Planning: {'✅' if workflow_result.planning_result else '⏳'}\n"
        result_text += f"• Content Creation: {'✅' if workflow_result.content_result else '⏳'}\n"
        result_text += f"• Quality Review: {'✅' if workflow_result.quality_result else '⏳'}\n"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(workflow_result.dict(), indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Failed to get workflow status: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_check_agents_health() -> CallToolResult:
    """Handle agent health check requests."""
    
    try:
        health_status = await orchestrator.agent_client.check_all_agents_health()
        
        result_text = "🏥 Agent Health Status\n\n"
        
        all_healthy = True
        for agent_name, status in health_status.items():
            is_healthy = status.get("healthy", False)
            all_healthy &= is_healthy
            
            icon = "✅" if is_healthy else "❌"
            result_text += f"{icon} **{agent_name.replace('_', ' ').title()}**\n"
            
            if is_healthy:
                result_text += f"   Status: Healthy\n"
                if status.get("response", {}).get("version"):
                    result_text += f"   Version: {status['response']['version']}\n"
            else:
                result_text += f"   Status: Unhealthy\n"
                if status.get("error"):
                    result_text += f"   Error: {status['error']}\n"
            
            result_text += f"   Checked: {status.get('checked_at', 'Unknown')}\n\n"
        
        # Overall system status
        system_status = "🟢 Operational" if all_healthy else "🟡 Degraded"
        result_text += f"🔧 **System Status**: {system_status}\n"
        result_text += f"📊 **Healthy Agents**: {sum(1 for s in health_status.values() if s.get('healthy', False))}/{len(health_status)}"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(health_status, indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Failed to check agent health: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_get_metrics() -> CallToolResult:
    """Handle metrics requests."""
    
    try:
        metrics = await orchestrator.get_orchestrator_metrics()
        
        orch_metrics = metrics.get("orchestrator_metrics", {})
        
        result_text = "📊 Orchestrator Performance Metrics\n\n"
        result_text += f"🔄 **Workflow Statistics**\n"
        result_text += f"• Total Workflows: {orch_metrics.get('total_workflows', 0)}\n"
        result_text += f"• Successful: {orch_metrics.get('successful_workflows', 0)}\n"
        result_text += f"• Failed: {orch_metrics.get('failed_workflows', 0)}\n"
        result_text += f"• Active: {metrics.get('active_workflows', 0)}\n"
        result_text += f"• Average Duration: {orch_metrics.get('average_duration', 0):.2f}s\n\n"
        
        success_rate = 0
        total = orch_metrics.get('total_workflows', 0)
        if total > 0:
            success_rate = (orch_metrics.get('successful_workflows', 0) / total) * 100
        
        result_text += f"📈 **Success Rate**: {success_rate:.1f}%\n\n"
        
        # Agent health summary
        agent_health = metrics.get("agent_health", {})
        healthy_agents = sum(1 for status in agent_health.values() if status.get("healthy", False))
        total_agents = len(agent_health)
        
        result_text += f"🤖 **Agent Status**: {healthy_agents}/{total_agents} healthy\n"
        result_text += f"🔧 **System Status**: {metrics.get('system_status', 'unknown').title()}"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(metrics, indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Failed to get metrics: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_list_workflows() -> CallToolResult:
    """Handle list workflows requests."""
    
    try:
        active_workflows = orchestrator.active_workflows
        completed_workflows = orchestrator.completed_workflows[-10:]  # Last 10
        
        result_text = f"📋 Workflow Overview\n\n"
        result_text += f"🔄 **Active Workflows** ({len(active_workflows)})\n"
        
        if active_workflows:
            for wf_id, workflow in active_workflows.items():
                result_text += f"• {wf_id}\n"
                result_text += f"  Status: {workflow.status}\n"
                result_text += f"  Company: Course Request {workflow.course_request_id}\n"
                result_text += f"  Started: {workflow.start_time}\n\n"
        else:
            result_text += "No active workflows\n\n"
        
        result_text += f"✅ **Recent Completed** ({len(completed_workflows)})\n"
        
        if completed_workflows:
            for workflow in completed_workflows:
                result_text += f"• {workflow.workflow_id}\n"
                result_text += f"  Status: {workflow.status}\n"
                result_text += f"  Duration: {workflow.total_duration_seconds:.1f}s\n"
                if workflow.quality_score:
                    result_text += f"  Quality: {workflow.quality_score}%\n"
                result_text += "\n"
        else:
            result_text += "No completed workflows\n"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                )
            ]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Failed to list workflows: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_cancel_workflow(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle workflow cancellation requests."""
    
    try:
        workflow_id = arguments["workflow_id"]
        cancelled = await orchestrator.cancel_workflow(workflow_id)
        
        if cancelled:
            result_text = f"✅ Workflow {workflow_id} cancelled successfully"
        else:
            result_text = f"❌ Workflow {workflow_id} not found or not cancellable"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                )
            ]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Failed to cancel workflow: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_test_agents() -> CallToolResult:
    """Handle agent testing requests."""
    
    try:
        test_results = await orchestrator.agent_client.test_all_agents()
        
        result_text = "🧪 Agent Functionality Tests\n\n"
        
        all_passed = test_results.get("overall_success", False)
        tests_passed = test_results.get("tests_passed", 0)
        tests_run = test_results.get("tests_run", 0)
        
        result_text += f"📊 **Overall Result**: {'✅ All Passed' if all_passed else '❌ Some Failed'}\n"
        result_text += f"📈 **Test Results**: {tests_passed}/{tests_run} passed\n\n"
        
        # Individual agent results
        agent_tests = test_results.get("agent_tests", {})
        for agent_name, test_result in agent_tests.items():
            success = test_result.get("success", False)
            icon = "✅" if success else "❌"
            
            result_text += f"{icon} **{agent_name.replace('_', ' ').title()}**\n"
            result_text += f"   Test: {test_result.get('test', 'unknown')}\n"
            
            if success:
                result_text += f"   Status: Passed\n"
            else:
                result_text += f"   Status: Failed\n"
                if test_result.get("error"):
                    result_text += f"   Error: {test_result['error']}\n"
            
            result_text += "\n"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(test_results, indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Failed to test agents: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_get_capabilities() -> CallToolResult:
    """Handle get capabilities requests."""
    
    try:
        capabilities = await orchestrator.agent_client.get_all_agent_capabilities()
        
        result_text = "🎯 Agent Capabilities Overview\n\n"
        
        for agent_name, caps in capabilities.items():
            result_text += f"🤖 **{agent_name.replace('_', ' ').title()}**\n"
            
            if caps.get("error"):
                result_text += f"   Error: {caps['error']}\n\n"
                continue
            
            if caps.get("agent_name"):
                result_text += f"   Name: {caps['agent_name']}\n"
            if caps.get("version"):
                result_text += f"   Version: {caps['version']}\n"
            
            if caps.get("capabilities"):
                result_text += f"   Capabilities:\n"
                for cap in caps["capabilities"][:3]:  # Show first 3
                    result_text += f"   • {cap}\n"
                if len(caps["capabilities"]) > 3:
                    result_text += f"   • ... and {len(caps['capabilities']) - 3} more\n"
            
            result_text += "\n"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(capabilities, indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Failed to get capabilities: {str(e)}"
                )
            ],
            isError=True
        )

async def main():
    """Run the MCP server."""
    logger.info("Starting Agent Orchestrator MCP Server...")
    
    # Test orchestrator on startup
    try:
        health_status = await orchestrator.agent_client.check_all_agents_health()
        healthy_agents = sum(1 for status in health_status.values() if status.get("healthy", False))
        logger.info(f"Orchestrator initialized: {healthy_agents}/{len(health_status)} agents healthy")
    except Exception as e:
        logger.warning(f"Could not check agent health on startup: {e}")
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="agent-orchestrator",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())