"""
MCP (Model Context Protocol) server implementation for Content Creator Agent
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

from main import ContentCreatorService, ContentCreationRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the content creator service
content_creator_service = ContentCreatorService()

# Create MCP server instance
server = Server("content-creator-agent")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for the Content Creator Agent."""
    return [
        Tool(
            name="create_lesson_content",
            description="Create comprehensive lesson content with activities, exercises, and materials",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "integer", "description": "ID of the course"},
                    "lesson_title": {"type": "string", "description": "Title of the lesson"},
                    "module_context": {"type": "string", "description": "Context of the module"},
                    "vocabulary_themes": {"type": "array", "items": {"type": "string"}, "description": "Vocabulary themes to cover"},
                    "grammar_focus": {"type": "array", "items": {"type": "string"}, "description": "Grammar points to focus on"},
                    "cefr_level": {"type": "string", "description": "CEFR level (A1-C2)"},
                    "duration_minutes": {"type": "integer", "description": "Lesson duration in minutes", "default": 60},
                    "company_context": {"type": "object", "description": "Company-specific context", "default": {}}
                },
                "required": ["course_id", "lesson_title", "module_context", "vocabulary_themes", "grammar_focus", "cefr_level"]
            }
        ),
        Tool(
            name="create_exercises",
            description="Create varied exercises for a lesson or topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "lesson_context": {"type": "object", "description": "Context of the lesson"},
                    "exercise_types": {"type": "array", "items": {"type": "string"}, "description": "Types of exercises to create"},
                    "exercise_count": {"type": "integer", "description": "Number of exercises to create", "default": 5},
                    "cefr_level": {"type": "string", "description": "CEFR level for exercises"}
                },
                "required": ["lesson_context", "exercise_types", "cefr_level"]
            }
        ),
        Tool(
            name="create_assessment",
            description="Create comprehensive assessments with varied question types",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_context": {"type": "object", "description": "Context of the course or lesson"},
                    "assessment_type": {"type": "string", "description": "Type of assessment", "default": "lesson"},
                    "duration_minutes": {"type": "integer", "description": "Assessment duration", "default": 30}
                },
                "required": ["course_context"]
            }
        ),
        Tool(
            name="adapt_content_for_level",
            description="Adapt existing content for a different CEFR level",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "object", "description": "Content to adapt"},
                    "target_level": {"type": "string", "description": "Target CEFR level (A1-C2)"}
                },
                "required": ["content", "target_level"]
            }
        ),
        Tool(
            name="get_content_capabilities",
            description="Get information about the Content Creator Agent's capabilities",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="suggest_multimedia_content",
            description="Generate multimedia content suggestions for lessons",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_type": {"type": "string", "description": "Type of content (lesson, exercise, assessment)"},
                    "context": {"type": "object", "description": "Content context and requirements"}
                },
                "required": ["content_type", "context"]
            }
        ),
        Tool(
            name="validate_content_request",
            description="Validate a content creation request before processing",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "integer"},
                    "lesson_title": {"type": "string"},
                    "module_context": {"type": "string"},
                    "vocabulary_themes": {"type": "array", "items": {"type": "string"}},
                    "grammar_focus": {"type": "array", "items": {"type": "string"}},
                    "cefr_level": {"type": "string"},
                    "duration_minutes": {"type": "integer", "default": 60}
                },
                "required": ["course_id", "lesson_title", "module_context", "vocabulary_themes", "grammar_focus", "cefr_level"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls for the Content Creator Agent."""
    
    try:
        logger.info(f"MCP tool called: {name} with arguments: {arguments}")
        
        if name == "create_lesson_content":
            return await handle_create_lesson_content(arguments)
        
        elif name == "create_exercises":
            return await handle_create_exercises(arguments)
        
        elif name == "create_assessment":
            return await handle_create_assessment(arguments)
        
        elif name == "adapt_content_for_level":
            return await handle_adapt_content(arguments)
        
        elif name == "get_content_capabilities":
            return await handle_get_capabilities()
        
        elif name == "suggest_multimedia_content":
            return await handle_suggest_multimedia(arguments)
        
        elif name == "validate_content_request":
            return await handle_validate_request(arguments)
        
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

async def handle_create_lesson_content(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle lesson content creation."""
    
    try:
        # Create content request object
        content_request = ContentCreationRequest(**arguments)
        
        # Validate the request
        validation = await content_creator_service.validate_content_request(content_request)
        if not validation["valid"]:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Invalid content request: {', '.join(validation['errors'])}"
                    )
                ],
                isError=True
            )
        
        # Create lesson content
        start_time = datetime.utcnow()
        lesson_content = await content_creator_service.create_lesson_content(content_request)
        creation_time = (datetime.utcnow() - start_time).total_seconds()
        
        result_text = f"📚 Lesson Content Created: {lesson_content.title}\n\n"
        result_text += f"⏱️ Duration: {lesson_content.duration_minutes} minutes\n"
        result_text += f"📊 CEFR Level: {arguments['cefr_level']}\n"
        result_text += f"🎯 Learning Objectives: {len(lesson_content.learning_objectives)}\n"
        result_text += f"📝 Vocabulary Themes: {', '.join(arguments['vocabulary_themes'])}\n"
        result_text += f"🔤 Grammar Focus: {', '.join(arguments['grammar_focus'])}\n"
        result_text += f"⚡ Creation Time: {creation_time:.2f} seconds\n\n"
        
        result_text += "📋 Lesson Structure:\n"
        result_text += f"• Warm-up: {lesson_content.warm_up.get('time', 5)} minutes\n"
        result_text += f"• Vocabulary: {lesson_content.vocabulary_section.get('time', 15)} minutes\n"
        result_text += f"• Grammar: {lesson_content.grammar_section.get('time', 20)} minutes\n"
        result_text += f"• Practice: {len(lesson_content.practice_activities)} activities\n"
        result_text += f"• Production: {lesson_content.production_activity.get('time', 10)} minutes\n"
        result_text += f"• Wrap-up: {lesson_content.wrap_up.get('time', 5)} minutes\n\n"
        
        result_text += f"🎒 Materials: {', '.join(lesson_content.materials_needed[:3])}..."
        
        if lesson_content.homework_assignment:
            result_text += f"\n📖 Homework: {lesson_content.homework_assignment.get('title', 'Assignment included')}"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(lesson_content.dict(), indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        logger.error(f"Lesson content creation failed: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Lesson content creation failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_create_exercises(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle exercise creation."""
    
    try:
        lesson_context = arguments["lesson_context"]
        exercise_types = arguments["exercise_types"]
        count = arguments.get("exercise_count", 5)
        
        # Create exercises
        start_time = datetime.utcnow()
        exercises = await content_creator_service.create_exercise_set(
            lesson_context=lesson_context,
            exercise_types=exercise_types,
            count=count
        )
        creation_time = (datetime.utcnow() - start_time).total_seconds()
        
        result_text = f"📝 Created {len(exercises)} Exercises\n\n"
        result_text += f"🎯 Exercise Types: {', '.join(exercise_types)}\n"
        result_text += f"📊 CEFR Level: {arguments['cefr_level']}\n"
        result_text += f"⚡ Creation Time: {creation_time:.2f} seconds\n\n"
        
        result_text += "📋 Exercise Summary:\n"
        for i, exercise in enumerate(exercises[:5], 1):
            result_text += f"{i}. {exercise.title} ({exercise.exercise_type})\n"
            result_text += f"   ⏱️ {exercise.estimated_time_minutes} min | 🎯 {exercise.points} pts\n"
        
        if len(exercises) > 5:
            result_text += f"   ... and {len(exercises) - 5} more exercises\n"
        
        total_time = sum(ex.estimated_time_minutes for ex in exercises)
        total_points = sum(ex.points for ex in exercises)
        result_text += f"\n⏱️ Total Exercise Time: {total_time} minutes\n"
        result_text += f"🎯 Total Points: {total_points}"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps([ex.dict() for ex in exercises], indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        logger.error(f"Exercise creation failed: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Exercise creation failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_create_assessment(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle assessment creation."""
    
    try:
        course_context = arguments["course_context"]
        assessment_type = arguments.get("assessment_type", "lesson")
        
        # Create assessment
        start_time = datetime.utcnow()
        assessment = await content_creator_service.create_assessment(
            course_context=course_context,
            assessment_type=assessment_type
        )
        creation_time = (datetime.utcnow() - start_time).total_seconds()
        
        result_text = f"📊 Assessment Created: {assessment.get('title', f'{assessment_type.title()} Assessment')}\n\n"
        result_text += f"📝 Type: {assessment_type.title()}\n"
        result_text += f"⏱️ Duration: {assessment.get('total_time_minutes', 30)} minutes\n"
        result_text += f"🎯 Total Points: {assessment.get('total_points', 100)}\n"
        result_text += f"✅ Passing Score: {assessment.get('passing_score', 70)}%\n"
        result_text += f"⚡ Creation Time: {creation_time:.2f} seconds\n\n"
        
        if "sections" in assessment:
            result_text += "📋 Assessment Sections:\n"
            for section in assessment["sections"]:
                result_text += f"• {section.get('name', 'Section')}: {section.get('points', 0)} pts"
                result_text += f" ({section.get('time_minutes', 0)} min)\n"
        
        if assessment.get("question_types"):
            result_text += f"\n❓ Question Types: {', '.join(assessment['question_types'])}"
        
        result_text += f"\n📈 Assessment Features:\n"
        result_text += f"• Randomized: {assessment.get('randomized', True)}\n"
        result_text += f"• Attempt Limit: {assessment.get('attempt_limit', 3)}\n"
        result_text += f"• Immediate Feedback: Yes"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(assessment, indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        logger.error(f"Assessment creation failed: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Assessment creation failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_adapt_content(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle content adaptation."""
    
    try:
        content = arguments["content"]
        target_level = arguments["target_level"]
        
        # Adapt content
        from tools import LessonContentGenerator
        generator = LessonContentGenerator()
        adapted_content = await generator.adapt_for_cefr_level(content, target_level)
        
        result_text = f"🔄 Content Adapted for {target_level} Level\n\n"
        result_text += f"📚 Original Content: {content.get('title', 'Unknown')}\n"
        result_text += f"🎯 Target Level: {target_level}\n"
        result_text += f"📅 Adapted: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        if adapted_content.get("adaptation_notes"):
            result_text += "📝 Adaptation Changes:\n"
            for note in adapted_content["adaptation_notes"][:3]:
                result_text += f"• {note}\n"
        
        result_text += f"\n✅ Content successfully adapted for {target_level} level learners"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(adapted_content, indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        logger.error(f"Content adaptation failed: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Content adaptation failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_get_capabilities() -> CallToolResult:
    """Handle capabilities request."""
    
    try:
        capabilities = await content_creator_service.get_content_capabilities()
        
        result_text = f"🤖 {capabilities['agent_name']} v{capabilities['version']}\n\n"
        result_text += "🎯 Capabilities:\n"
        result_text += "\n".join([f"• {cap}" for cap in capabilities['capabilities']])
        result_text += "\n\n📝 Supported Exercise Types:\n"
        result_text += "\n".join([f"• {ex_type}" for ex_type in capabilities['supported_exercise_types'][:5]])
        result_text += f"\n... and {len(capabilities['supported_exercise_types']) - 5} more types"
        result_text += "\n\n📊 Supported CEFR Levels:\n"
        result_text += " | ".join(capabilities['supported_cefr_levels'])
        result_text += "\n\n📄 Content Formats:\n"
        result_text += "\n".join([f"• {fmt}" for fmt in capabilities['content_formats']])
        result_text += f"\n\n🟢 Status: {capabilities['status']}"
        
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

async def handle_suggest_multimedia(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle multimedia content suggestions."""
    
    try:
        content_type = arguments["content_type"]
        context = arguments["context"]
        
        # Generate multimedia suggestions
        from tools import MultimediaContentGenerator
        generator = MultimediaContentGenerator()
        suggestions = await generator.suggest_multimedia(content_type, context)
        
        result_text = f"🎬 Multimedia Suggestions for {content_type.title()}\n\n"
        
        if suggestions.get("visual_aids"):
            result_text += "🖼️ Visual Aids:\n"
            result_text += "\n".join([f"• {aid}" for aid in suggestions["visual_aids"][:3]])
            result_text += "\n\n"
        
        if suggestions.get("audio_content"):
            result_text += "🔊 Audio Content:\n"
            result_text += "\n".join([f"• {audio}" for audio in suggestions["audio_content"][:3]])
            result_text += "\n\n"
        
        if suggestions.get("interactive_elements"):
            result_text += "🎮 Interactive Elements:\n"
            result_text += "\n".join([f"• {element}" for element in suggestions["interactive_elements"][:3]])
            result_text += "\n\n"
        
        result_text += "💡 Implementation Tips:\n"
        result_text += "• Start with low-budget options\n"
        result_text += "• Ensure accessibility compliance\n"
        result_text += "• Test with target audience\n"
        result_text += "• Consider technical requirements"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                ),
                TextContent(
                    type="text",
                    text=f"```json\n{json.dumps(suggestions, indent=2)}\n```"
                )
            ]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Multimedia suggestions failed: {str(e)}"
                )
            ],
            isError=True
        )

async def handle_validate_request(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle request validation."""
    
    try:
        content_request = ContentCreationRequest(**arguments)
        validation = await content_creator_service.validate_content_request(content_request)
        
        status = "✅ Valid" if validation["valid"] else "❌ Invalid"
        result_text = f"Content Request Validation: {status}\n\n"
        
        if validation["errors"]:
            result_text += "🚫 Errors:\n"
            result_text += "\n".join([f"• {error}" for error in validation["errors"]])
            result_text += "\n\n"
        
        if validation["warnings"]:
            result_text += "⚠️ Warnings:\n"
            result_text += "\n".join([f"• {warning}" for warning in validation["warnings"]])
            result_text += "\n\n"
        
        if validation["valid"]:
            result_text += "✨ Request is ready for content creation!"
        
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

async def main():
    """Run the MCP server."""
    logger.info("Starting Content Creator Agent MCP Server...")
    
    # Get agent capabilities on startup
    try:
        capabilities = await content_creator_service.get_content_capabilities()
        logger.info(f"Agent capabilities loaded: {capabilities['agent_name']} v{capabilities['version']}")
    except Exception as e:
        logger.warning(f"Could not load agent capabilities: {e}")
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="content-creator-agent",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())