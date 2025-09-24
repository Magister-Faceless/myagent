"""
Enhanced task tool that emits subagent events for UI tracking.
"""

from typing import Annotated, Dict, Any, Optional
from datetime import datetime
import uuid
import json

from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import ToolMessage, SystemMessage
from langgraph.types import Command

try:
    from langgraph.prebuilt import InjectedState
except ImportError:
    from typing import Any
    InjectedState = Any

from deepagents.state import DeepAgentState


class SubAgentTracker:
    """Tracks active subagents and their status."""
    
    def __init__(self):
        self.active_subagents: Dict[str, Dict[str, Any]] = {}
    
    def create_subagent_event(
        self, 
        event_type: str, 
        subagent_id: str, 
        subagent_type: str, 
        description: str,
        status: str = "active"
    ) -> Dict[str, Any]:
        """Create a subagent event for the frontend."""
        return {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "id": subagent_id,
                "name": subagent_type,
                "description": description,
                "status": status,
                "created_at": datetime.now().isoformat()
            }
        }
    
    def start_subagent(self, subagent_type: str, description: str) -> str:
        """Register a new subagent and return its ID."""
        subagent_id = f"subagent_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        self.active_subagents[subagent_id] = {
            "id": subagent_id,
            "type": subagent_type,
            "description": description,
            "status": "active",
            "started_at": datetime.now().isoformat()
        }
        
        return subagent_id
    
    def complete_subagent(self, subagent_id: str, result: str = "") -> None:
        """Mark a subagent as completed."""
        if subagent_id in self.active_subagents:
            self.active_subagents[subagent_id].update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "result": result
            })
    
    def error_subagent(self, subagent_id: str, error: str) -> None:
        """Mark a subagent as having an error."""
        if subagent_id in self.active_subagents:
            self.active_subagents[subagent_id].update({
                "status": "error",
                "completed_at": datetime.now().isoformat(),
                "error": error
            })
    
    def get_active_subagents(self) -> Dict[str, Dict[str, Any]]:
        """Get all currently active subagents."""
        return {k: v for k, v in self.active_subagents.items() if v["status"] == "active"}


# Global tracker instance
subagent_tracker = SubAgentTracker()


def create_enhanced_task_tool(original_task_tool):
    """
    Create an enhanced version of the task tool that emits subagent events.
    This wraps the original task tool from the framework.
    """
    
    @tool(description=original_task_tool.description)
    async def enhanced_task(
        description: str,
        subagent_type: str,
        state: Annotated[DeepAgentState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        # Start tracking the subagent
        subagent_id = subagent_tracker.start_subagent(subagent_type, description)
        
        # Create start event message
        start_event = subagent_tracker.create_subagent_event(
            "subagent_started", subagent_id, subagent_type, description
        )
        
        # Add system message about subagent starting
        start_message = SystemMessage(
            content=f"🚀 **Subagent Started**: {subagent_type}\n"
                   f"**Task**: {description}\n"
                   f"**ID**: {subagent_id}\n"
                   f"**Event Data**: {json.dumps(start_event, indent=2)}"
        )
        
        try:
            # Call the original task tool
            result = await original_task_tool.ainvoke({
                "description": description,
                "subagent_type": subagent_type,
                "state": state,
                "tool_call_id": tool_call_id
            })
            
            # Mark subagent as completed
            subagent_tracker.complete_subagent(subagent_id, str(result))
            
            # Create completion event
            completion_event = subagent_tracker.create_subagent_event(
                "subagent_completed", subagent_id, subagent_type, description, "completed"
            )
            
            # Add system message about completion
            completion_message = SystemMessage(
                content=f"✅ **Subagent Completed**: {subagent_type}\n"
                       f"**ID**: {subagent_id}\n"
                       f"**Event Data**: {json.dumps(completion_event, indent=2)}"
            )
            
            # If result is a Command, add our messages to it
            if isinstance(result, Command):
                existing_messages = result.update.get("messages", [])
                result.update["messages"] = [start_message] + existing_messages + [completion_message]
                return result
            else:
                # If it's a string result, wrap it in a Command
                return Command(
                    update={
                        "messages": [
                            start_message,
                            ToolMessage(str(result), tool_call_id=tool_call_id),
                            completion_message
                        ]
                    }
                )
                
        except Exception as e:
            # Mark subagent as error
            subagent_tracker.error_subagent(subagent_id, str(e))
            
            # Create error event
            error_event = subagent_tracker.create_subagent_event(
                "subagent_error", subagent_id, subagent_type, description, "error"
            )
            
            # Add system message about error
            error_message = SystemMessage(
                content=f"❌ **Subagent Error**: {subagent_type}\n"
                       f"**ID**: {subagent_id}\n"
                       f"**Error**: {str(e)}\n"
                       f"**Event Data**: {json.dumps(error_event, indent=2)}"
            )
            
            return Command(
                update={
                    "messages": [
                        start_message,
                        ToolMessage(f"Error in subagent {subagent_type}: {str(e)}", tool_call_id=tool_call_id),
                        error_message
                    ]
                }
            )
    
    return enhanced_task


@tool
def get_active_subagents() -> str:
    """Get information about currently active subagents."""
    active = subagent_tracker.get_active_subagents()
    
    if not active:
        return "No subagents are currently active."
    
    result = "**Active Subagents:**\n\n"
    for subagent_id, info in active.items():
        result += f"- **{info['type']}** (ID: {subagent_id})\n"
        result += f"  - Task: {info['description']}\n"
        result += f"  - Started: {info['started_at']}\n"
        result += f"  - Status: {info['status']}\n\n"
    
    return result


@tool 
def get_subagent_summary() -> str:
    """Get a summary of all subagent activity."""
    all_subagents = subagent_tracker.active_subagents
    
    if not all_subagents:
        return "No subagent activity recorded."
    
    summary = {
        "active": 0,
        "completed": 0,
        "error": 0,
        "total": len(all_subagents)
    }
    
    for info in all_subagents.values():
        status = info.get("status", "unknown")
        if status in summary:
            summary[status] += 1
    
    result = f"**Subagent Summary:**\n"
    result += f"- Total: {summary['total']}\n"
    result += f"- Active: {summary['active']}\n"
    result += f"- Completed: {summary['completed']}\n"
    result += f"- Errors: {summary['error']}\n"
    
    return result
