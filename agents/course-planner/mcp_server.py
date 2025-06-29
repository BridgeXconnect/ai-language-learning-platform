"""
MCP (Model Context Protocol) server implementation for Course Planner Agent
Enables communication with AI IDEs and other MCP-compatible tools
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

from main import CoursePlannerService, CourseRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the course planner service
course_planner_service = CoursePlannerService()

# Create MCP server instance
server = Server("course-planner-agent")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for the Course Planner Agent."""
    return [
        Tool(
            name="plan_course",
            description="Create a comprehensive course curriculum based on company requirements and SOP analysis",
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
            name="validate_course_request",
            description="Validate a course planning request before processing",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_request_id": {"type": "integer"},
                    "company_name": {"type": "string"},
                    "industry": {"type": "string"},
                    "training_goals": {"type": "string"},
                    "current_english_level": {"type": "string"},
                    "duration_weeks": {"type": "integer", "default": 8}
                },
                "required": ["course_request_id", "company_name", "industry", "training_goals", "current_english_level"]
            }
        ),
        Tool(
            name="get_agent_capabilities",
            description="Get information about the Course Planner Agent's capabilities and supported features",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="analyze_sop_documents",
            description="Analyze SOP documents for a specific course request to extract key business processes and vocabulary",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_request_id": {"type": "integer", "description": "ID of the course request to analyze SOPs for"}
                },
                "required": ["course_request_id"]
            }
        ),
        Tool(
            name="map_content_to_cefr",
            description="Map analyzed content to appropriate CEFR levels",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "object", "description": "Analyzed content from SOP documents"},
                    "target_level": {"type": "string", "description": "Target CEFR level (A1-C2)"}
                },
                "required": ["content", "target_level"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls for the Course Planner Agent."""
    
    try:
        logger.info(f"MCP tool called: {name} with arguments: {arguments}")
        
        if name == "plan_course":
            return await handle_plan_course(arguments)
        
        elif name == "validate_course_request":
            return await handle_validate_request(arguments)
        
        elif name == "get_agent_capabilities":
            return await handle_get_capabilities()
        
        elif name == "analyze_sop_documents":
            return await handle_analyze_sop_documents(arguments)
        
        elif name == "map_content_to_cefr":
            return await handle_map_content_to_cefr(arguments)
        
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

async def handle_plan_course(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle course planning requests."""
    
    try:
        # Create course request object
        course_request = CourseRequest(**arguments)
        
        # Validate the request
        validation = await course_planner_service.validate_course_request(course_request)
        if not validation["valid"]:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Invalid course request: {', '.join(validation['errors'])}"
                    )
                ],
                isError=True
            )
        
        # Plan the course
        start_time = datetime.utcnow()
        curriculum = await course_planner_service.plan_course(course_request)
        planning_time = (datetime.utcnow() - start_time).total_seconds()
        
        result = {
            "success": True,
            "curriculum": curriculum.dict(),
            "planning_time_seconds": planning_time,
            "company": arguments["company_name"],
            "industry": arguments["industry"],
            "cefr_level": arguments["current_english_level"]
        }
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Course curriculum successfully planned for {arguments['company_name']}\n\n" +
                         f"📚 Course Title: {curriculum.title}\n" +
                         f"🏢 Company: {arguments['company_name']}\n" +
                         f"🏭 Industry: {arguments['industry']}\n" +
                         f"📊 CEFR Level: {curriculum.cefr_level}\n" +
                         f"⏱️ Duration: {curriculum.duration_weeks} weeks\n" +
                         f"📖 Modules: {len(curriculum.modules)}\n" +
                         f"⚡ Planning Time: {planning_time:.2f} seconds\n\n" +
                         f"📋 Learning Objectives:\n" +
                         "\n".join([f"• {obj}" for obj in curriculum.learning_objectives[:5]]) +
                         f"\n\n📝 Vocabulary Themes:\n" +
                         "\n".join([f"• {theme}" for theme in curriculum.vocabulary_themes[:5]]) +
                         f"\n\n🔗 Full curriculum data available in JSON format."
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(result, indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        logger.error(f"Course planning failed: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Course planning failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_validate_request(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle request validation."""
    
    try:
        course_request = CourseRequest(**arguments)
        validation = await course_planner_service.validate_course_request(course_request)
        
        status = "✅ Valid" if validation["valid"] else "❌ Invalid"
        result_text = f"Course Request Validation: {status}\n\n"
        
        if validation["errors"]:
            result_text += "🚫 Errors:\n"
            result_text += "\n".join([f"• {error}" for error in validation["errors"]])
            result_text += "\n\n"
        
        if validation["warnings"]:
            result_text += "⚠️ Warnings:\n"
            result_text += "\n".join([f"• {warning}" for warning in validation["warnings"]])
            result_text += "\n\n"
        
        if validation["valid"]:
            result_text += "✨ Request is ready for processing!"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(validation, indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Validation failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_get_capabilities() -> CallToolResult:
    """Handle capabilities request."""
    
    try:
        capabilities = await course_planner_service.get_planning_capabilities()
        
        result_text = f"🤖 {capabilities['agent_name']} v{capabilities['version']}\n\n"
        result_text += "🎯 Capabilities:\n"
        result_text += "\n".join([f"• {cap}" for cap in capabilities['capabilities']])
        result_text += "\n\n🏭 Supported Industries:\n"
        result_text += "\n".join([f"• {industry}" for industry in capabilities['supported_industries']])
        result_text += "\n\n📊 Supported CEFR Levels:\n"
        result_text += " | ".join(capabilities['supported_cefr_levels'])
        result_text += f"\n\n⏱️ Max Duration: {capabilities['max_duration_weeks']} weeks"
        result_text += f"\n🟢 Status: {capabilities['status']}"
        
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

async def handle_analyze_sop_documents(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle SOP document analysis."""
    
    try:
        course_request_id = arguments["course_request_id"]
        
        # Use the SOP analyzer tool
        from tools import SOPDocumentAnalyzer
        analyzer = SOPDocumentAnalyzer()
        analysis = await analyzer.analyze_documents(course_request_id)
        
        result_text = f"📄 SOP Document Analysis for Course Request {course_request_id}\n\n"
        result_text += f"📊 Documents Analyzed: {analysis.get('documents_analyzed', 0)}\n"
        result_text += f"📈 Status: {analysis.get('analysis_status', 'unknown')}\n\n"
        
        if analysis.get('key_processes'):
            result_text += "🔧 Key Business Processes:\n"
            result_text += "\n".join([f"• {process}" for process in analysis['key_processes'][:5]])
            result_text += "\n\n"
        
        if analysis.get('vocabulary_themes'):
            result_text += "📚 Vocabulary Themes:\n"
            result_text += "\n".join([f"• {theme}" for theme in analysis['vocabulary_themes'][:5]])
            result_text += "\n\n"
        
        if analysis.get('communication_scenarios'):
            result_text += "💬 Communication Scenarios:\n"
            result_text += "\n".join([f"• {scenario}" for scenario in analysis['communication_scenarios'][:5]])
            result_text += "\n\n"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(analysis, indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"SOP analysis failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_map_content_to_cefr(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle CEFR level mapping."""
    
    try:
        content = arguments["content"]
        target_level = arguments["target_level"]
        
        # Use the CEFR mapper tool
        from tools import CEFRLevelMapper
        mapper = CEFRLevelMapper()
        mapping = await mapper.map_content_level(content, target_level)
        
        result_text = f"📊 CEFR Level Mapping for {target_level}\n\n"
        
        if mapping.get('mapping_result'):
            mapping_result = mapping['mapping_result']
            
            if mapping_result.get('target_level_content'):
                target_content = mapping_result['target_level_content']
                result_text += f"🎯 Content for {target_level} Level:\n\n"
                
                if target_content.get('appropriate_vocabulary'):
                    result_text += "📚 Appropriate Vocabulary:\n"
                    result_text += "\n".join([f"• {vocab}" for vocab in target_content['appropriate_vocabulary'][:5]])
                    result_text += "\n\n"
                
                if target_content.get('suitable_scenarios'):
                    result_text += "💼 Suitable Scenarios:\n"
                    result_text += "\n".join([f"• {scenario}" for scenario in target_content['suitable_scenarios'][:5]])
                    result_text += "\n\n"
                
                if target_content.get('recommended_adaptations'):
                    result_text += "🔧 Recommended Adaptations:\n"
                    result_text += "\n".join([f"• {adaptation}" for adaptation in target_content['recommended_adaptations'][:3]])
                    result_text += "\n\n"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(mapping, indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"CEFR mapping failed: {str(e)}"
                )
            ],
            isError=True
        )

async def main():
    """Run the MCP server."""
    logger.info("Starting Course Planner Agent MCP Server...")
    
    # Get agent capabilities on startup
    try:
        capabilities = await course_planner_service.get_planning_capabilities()
        logger.info(f"Agent capabilities loaded: {capabilities['agent_name']} v{capabilities['version']}")
    except Exception as e:
        logger.warning(f"Could not load agent capabilities: {e}")
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="course-planner-agent",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())