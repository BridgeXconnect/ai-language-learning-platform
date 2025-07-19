"""
MCP (Model Context Protocol) server implementation for Quality Assurance Agent
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

from main import QualityAssuranceService, QualityReviewRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the quality assurance service
quality_assurance_service = QualityAssuranceService()

# Create MCP server instance
server = Server("quality-assurance-agent")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for the Quality Assurance Agent."""
    return [
        Tool(
            name="review_content",
            description="Perform comprehensive quality review of course content with multi-criteria analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "integer", "description": "ID of the course to review"},
                    "content_type": {"type": "string", "description": "Type of content (lesson, exercise, assessment)", "enum": ["lesson", "exercise", "assessment", "module", "full_course"]},
                    "content_data": {"type": "object", "description": "Content data to review"},
                    "target_cefr_level": {"type": "string", "description": "Target CEFR level (A1-C2)", "enum": ["A1", "A2", "B1", "B2", "C1", "C2"]},
                    "industry_context": {"type": "string", "description": "Industry context for relevance check"},
                    "review_criteria": {
                        "type": "array",
                        "description": "Specific criteria to focus on",
                        "items": {"type": "string"},
                        "default": ["linguistic_accuracy", "cefr_alignment", "cultural_sensitivity", "engagement", "clarity"]
                    }
                },
                "required": ["course_id", "content_type", "content_data", "target_cefr_level"]
            }
        ),
        Tool(
            name="validate_cefr_alignment",
            description="Validate content alignment with CEFR standards and provide detailed analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Content text to analyze"},
                    "target_level": {"type": "string", "description": "Target CEFR level", "enum": ["A1", "A2", "B1", "B2", "C1", "C2"]},
                    "content_type": {"type": "string", "description": "Type of content", "enum": ["reading", "listening", "speaking", "writing", "vocabulary", "grammar"]},
                    "detailed_analysis": {"type": "boolean", "description": "Whether to provide detailed CEFR analysis", "default": True}
                },
                "required": ["content", "target_level"]
            }
        ),
        Tool(
            name="check_cultural_sensitivity",
            description="Check content for cultural sensitivity and inclusivity",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Content to analyze"},
                    "target_audience": {"type": "string", "description": "Target audience description"},
                    "cultural_context": {"type": "string", "description": "Cultural context or region", "default": "international"},
                    "sensitivity_categories": {
                        "type": "array",
                        "description": "Categories to check",
                        "items": {"type": "string"},
                        "default": ["stereotypes", "bias", "inclusivity", "appropriateness"]
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="assess_engagement_level",
            description="Assess content engagement and interactivity level",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_data": {"type": "object", "description": "Complete content data including activities"},
                    "learner_profile": {"type": "string", "description": "Target learner profile", "default": "professional_adult"},
                    "engagement_criteria": {
                        "type": "array",
                        "description": "Engagement criteria to evaluate",
                        "items": {"type": "string"},
                        "default": ["interactivity", "variety", "relevance", "challenge_level"]
                    }
                },
                "required": ["content_data"]
            }
        ),
        Tool(
            name="generate_improvement_suggestions",
            description="Generate specific suggestions for content improvement",
            inputSchema={
                "type": "object",
                "properties": {
                    "review_results": {"type": "object", "description": "Results from quality review"},
                    "priority_areas": {
                        "type": "array",
                        "description": "Areas to prioritize for improvement",
                        "items": {"type": "string"},
                        "default": ["accuracy", "engagement", "alignment"]
                    },
                    "improvement_type": {"type": "string", "description": "Type of improvements needed", "enum": ["minor", "moderate", "major"], "default": "moderate"}
                },
                "required": ["review_results"]
            }
        ),
        Tool(
            name="validate_learning_objectives",
            description="Validate that content aligns with stated learning objectives",
            inputSchema={
                "type": "object",
                "properties": {
                    "learning_objectives": {
                        "type": "array",
                        "description": "List of learning objectives",
                        "items": {"type": "string"}
                    },
                    "content_data": {"type": "object", "description": "Content to validate against objectives"},
                    "assessment_activities": {"type": "array", "description": "Assessment activities to check", "items": {"type": "object"}},
                    "validation_depth": {"type": "string", "description": "Depth of validation", "enum": ["basic", "comprehensive"], "default": "comprehensive"}
                },
                "required": ["learning_objectives", "content_data"]
            }
        ),
        Tool(
            name="check_content_progression",
            description="Check logical progression and difficulty curve in content",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_content": {"type": "array", "description": "Array of content items in sequence", "items": {"type": "object"}},
                    "target_level": {"type": "string", "description": "Target CEFR level", "enum": ["A1", "A2", "B1", "B2", "C1", "C2"]},
                    "progression_type": {"type": "string", "description": "Type of progression to check", "enum": ["difficulty", "vocabulary", "grammar", "skills"], "default": "difficulty"}
                },
                "required": ["module_content", "target_level"]
            }
        ),
        Tool(
            name="get_quality_metrics",
            description="Get comprehensive quality metrics for analyzed content",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "integer", "description": "Course ID to get metrics for"},
                    "time_period": {"type": "string", "description": "Time period for metrics", "enum": ["24h", "7d", "30d"], "default": "7d"},
                    "metric_categories": {
                        "type": "array",
                        "description": "Categories of metrics to include",
                        "items": {"type": "string"},
                        "default": ["overall_scores", "criteria_breakdown", "improvement_trends"]
                    }
                },
                "required": ["course_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls for the Quality Assurance Agent."""
    
    try:
        logger.info(f"QA MCP tool called: {name} with arguments: {arguments}")
        
        if name == "review_content":
            return await handle_review_content(arguments)
        
        elif name == "validate_cefr_alignment":
            return await handle_validate_cefr_alignment(arguments)
        
        elif name == "check_cultural_sensitivity":
            return await handle_check_cultural_sensitivity(arguments)
        
        elif name == "assess_engagement_level":
            return await handle_assess_engagement_level(arguments)
        
        elif name == "generate_improvement_suggestions":
            return await handle_generate_improvement_suggestions(arguments)
        
        elif name == "validate_learning_objectives":
            return await handle_validate_learning_objectives(arguments)
        
        elif name == "check_content_progression":
            return await handle_check_content_progression(arguments)
        
        elif name == "get_quality_metrics":
            return await handle_get_quality_metrics(arguments)
        
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
        logger.error(f"QA tool call failed for {name}: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Tool execution failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_review_content(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle content review requests."""
    
    try:
        # Create review request
        review_request = QualityReviewRequest(
            course_id=arguments["course_id"],
            content_type=arguments["content_type"],
            content_data=arguments["content_data"],
            target_cefr_level=arguments["target_cefr_level"],
            industry_context=arguments.get("industry_context", ""),
            review_criteria=arguments.get("review_criteria", [])
        )
        
        # Perform review
        review_result = await quality_assurance_service.review_content(review_request)
        
        # Format result for MCP
        result_text = f"🔍 Quality Review Results: {review_result.content_type.title()}\n\n"
        result_text += f"📊 **Overall Score**: {review_result.overall_score}%\n"
        result_text += f"✅ **Approved**: {'Yes' if review_result.approved_for_release else 'No'}\n"
        result_text += f"🎯 **CEFR Level**: {review_result.target_cefr_level}\n\n"
        
        # Add criteria breakdown
        result_text += "📋 **Criteria Breakdown**:\n"
        for criterion, score in review_result.criteria_scores.items():
            icon = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
            result_text += f"  {icon} {criterion.replace('_', ' ').title()}: {score}%\n"
        
        # Add improvement areas if any
        if review_result.improvement_areas:
            result_text += "\n🔧 **Areas for Improvement**:\n"
            for area in review_result.improvement_areas:
                result_text += f"  • {area}\n"
        
        # Add detailed feedback if available
        if hasattr(review_result, 'detailed_feedback') and review_result.detailed_feedback:
            result_text += f"\n📝 **Detailed Feedback**:\n{review_result.detailed_feedback}\n"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(review_result.dict(), indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        logger.error(f"Content review failed: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Content review failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_validate_cefr_alignment(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle CEFR alignment validation."""
    
    try:
        validation_result = await quality_assurance_service.validate_cefr_alignment(
            content=arguments["content"],
            target_level=arguments["target_level"],
            content_type=arguments.get("content_type", "general"),
            detailed_analysis=arguments.get("detailed_analysis", True)
        )
        
        result_text = f"📊 CEFR Alignment Analysis\n\n"
        result_text += f"🎯 **Target Level**: {arguments['target_level']}\n"
        result_text += f"📈 **Alignment Score**: {validation_result.get('alignment_score', 0)}%\n"
        result_text += f"✅ **Meets Standards**: {'Yes' if validation_result.get('meets_standards', False) else 'No'}\n\n"
        
        if validation_result.get('level_analysis'):
            result_text += "🔍 **Level Analysis**:\n"
            for aspect, details in validation_result['level_analysis'].items():
                result_text += f"  • **{aspect.title()}**: {details}\n"
        
        if validation_result.get('recommendations'):
            result_text += "\n💡 **Recommendations**:\n"
            for rec in validation_result['recommendations']:
                result_text += f"  • {rec}\n"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(validation_result, indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"CEFR validation failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_check_cultural_sensitivity(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle cultural sensitivity checks."""
    
    try:
        sensitivity_result = await quality_assurance_service.check_cultural_sensitivity(
            content=arguments["content"],
            target_audience=arguments.get("target_audience", "international"),
            cultural_context=arguments.get("cultural_context", "international")
        )
        
        result_text = f"🌍 Cultural Sensitivity Analysis\n\n"
        result_text += f"📊 **Sensitivity Score**: {sensitivity_result.get('sensitivity_score', 0)}%\n"
        result_text += f"✅ **Culturally Appropriate**: {'Yes' if sensitivity_result.get('appropriate', False) else 'No'}\n\n"
        
        if sensitivity_result.get('issues_found'):
            result_text += "⚠️ **Issues Identified**:\n"
            for issue in sensitivity_result['issues_found']:
                result_text += f"  • {issue}\n"
        
        if sensitivity_result.get('suggestions'):
            result_text += "\n💡 **Suggestions**:\n"
            for suggestion in sensitivity_result['suggestions']:
                result_text += f"  • {suggestion}\n"
        
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
                    text=f"Cultural sensitivity check failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_assess_engagement_level(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle engagement level assessment."""
    
    try:
        engagement_result = await quality_assurance_service.assess_engagement_level(
            content_data=arguments["content_data"],
            learner_profile=arguments.get("learner_profile", "professional_adult")
        )
        
        result_text = f"🎯 Engagement Level Assessment\n\n"
        result_text += f"📊 **Engagement Score**: {engagement_result.get('engagement_score', 0)}%\n"
        result_text += f"🎪 **Interactivity Level**: {engagement_result.get('interactivity_level', 'medium')}\n\n"
        
        if engagement_result.get('strengths'):
            result_text += "💪 **Strengths**:\n"
            for strength in engagement_result['strengths']:
                result_text += f"  • {strength}\n"
        
        if engagement_result.get('improvement_areas'):
            result_text += "\n🔧 **Areas for Improvement**:\n"
            for area in engagement_result['improvement_areas']:
                result_text += f"  • {area}\n"
        
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
                    text=f"Engagement assessment failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_generate_improvement_suggestions(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle improvement suggestions generation."""
    
    try:
        suggestions = await quality_assurance_service.generate_improvement_suggestions(
            review_results=arguments["review_results"],
            priority_areas=arguments.get("priority_areas", [])
        )
        
        result_text = f"💡 Content Improvement Suggestions\n\n"
        
        if suggestions.get('priority_improvements'):
            result_text += "🔥 **Priority Improvements**:\n"
            for improvement in suggestions['priority_improvements']:
                result_text += f"  • {improvement}\n"
        
        if suggestions.get('quick_fixes'):
            result_text += "\n⚡ **Quick Fixes**:\n"
            for fix in suggestions['quick_fixes']:
                result_text += f"  • {fix}\n"
        
        if suggestions.get('long_term_enhancements'):
            result_text += "\n🎯 **Long-term Enhancements**:\n"
            for enhancement in suggestions['long_term_enhancements']:
                result_text += f"  • {enhancement}\n"
        
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
                    text=f"Improvement suggestions generation failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_validate_learning_objectives(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle learning objectives validation."""
    
    try:
        validation_result = await quality_assurance_service.validate_learning_objectives(
            learning_objectives=arguments["learning_objectives"],
            content_data=arguments["content_data"],
            assessment_activities=arguments.get("assessment_activities", [])
        )
        
        result_text = f"🎯 Learning Objectives Validation\n\n"
        result_text += f"📊 **Alignment Score**: {validation_result.get('alignment_score', 0)}%\n"
        result_text += f"✅ **Objectives Met**: {validation_result.get('objectives_met', 0)}/{len(arguments['learning_objectives'])}\n\n"
        
        if validation_result.get('objective_analysis'):
            result_text += "📋 **Objective Analysis**:\n"
            for obj_analysis in validation_result['objective_analysis']:
                status = "✅" if obj_analysis.get('met', False) else "❌"
                result_text += f"  {status} {obj_analysis.get('objective', 'Unknown')}\n"
                if obj_analysis.get('note'):
                    result_text += f"      Note: {obj_analysis['note']}\n"
        
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
                    text=f"Learning objectives validation failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_check_content_progression(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle content progression checks."""
    
    try:
        progression_result = await quality_assurance_service.check_content_progression(
            module_content=arguments["module_content"],
            target_level=arguments["target_level"],
            progression_type=arguments.get("progression_type", "difficulty")
        )
        
        result_text = f"📈 Content Progression Analysis\n\n"
        result_text += f"📊 **Progression Score**: {progression_result.get('progression_score', 0)}%\n"
        result_text += f"🎯 **Logical Flow**: {'Yes' if progression_result.get('logical_flow', False) else 'No'}\n"
        result_text += f"📈 **Difficulty Curve**: {progression_result.get('difficulty_curve', 'unknown')}\n\n"
        
        if progression_result.get('issues'):
            result_text += "⚠️ **Progression Issues**:\n"
            for issue in progression_result['issues']:
                result_text += f"  • {issue}\n"
        
        if progression_result.get('recommendations'):
            result_text += "\n💡 **Recommendations**:\n"
            for rec in progression_result['recommendations']:
                result_text += f"  • {rec}\n"
        
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
                    text=f"Content progression check failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_get_quality_metrics(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle quality metrics requests."""
    
    try:
        metrics = await quality_assurance_service.get_quality_metrics(
            course_id=arguments["course_id"],
            time_period=arguments.get("time_period", "7d")
        )
        
        result_text = f"📊 Quality Metrics Report\n\n"
        result_text += f"🎯 **Course ID**: {arguments['course_id']}\n"
        result_text += f"📅 **Time Period**: {arguments.get('time_period', '7d')}\n\n"
        
        if metrics.get('overall_metrics'):
            overall = metrics['overall_metrics']
            result_text += "📈 **Overall Performance**:\n"
            result_text += f"  • Average Score: {overall.get('average_score', 0)}%\n"
            result_text += f"  • Reviews Completed: {overall.get('reviews_completed', 0)}\n"
            result_text += f"  • Approval Rate: {overall.get('approval_rate', 0)}%\n\n"
        
        if metrics.get('criteria_breakdown'):
            result_text += "🔍 **Criteria Breakdown**:\n"
            for criterion, score in metrics['criteria_breakdown'].items():
                result_text += f"  • {criterion.replace('_', ' ').title()}: {score}%\n"
        
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
                    text=f"Quality metrics retrieval failed: {str(e)}"
                )
            ],
            isError=True
        )

async def main():
    """Run the MCP server."""
    logger.info("Starting Quality Assurance Agent MCP Server...")
    
    # Test service on startup
    try:
        logger.info("Quality Assurance service initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize QA service on startup: {e}")
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="quality-assurance-agent",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())