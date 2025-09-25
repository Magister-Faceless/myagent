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


def create_enhanced_task_tool(original_task_tool, *, is_async: bool = True):
    """
    Create an enhanced version of the task tool that emits subagent events.
    This wraps the original task tool from the framework.
    """

    description = getattr(original_task_tool, "description", "Task delegation tool")
    tool_name = getattr(original_task_tool, "name", "task")

    def _start_tracking(subagent_type: str, task_description: str):
        subagent_id = subagent_tracker.start_subagent(subagent_type, task_description)
        start_event = subagent_tracker.create_subagent_event(
            "subagent_started", subagent_id, subagent_type, task_description
        )
        start_message = SystemMessage(
            content=(
                f"🚀 **Subagent Started**: {subagent_type}\n"
                f"**Task**: {task_description}\n"
                f"**ID**: {subagent_id}\n"
                f"**Event Data**: {json.dumps(start_event, indent=2)}"
            )
        )
        return subagent_id, start_message

    def _complete_tracking(
        subagent_id: str,
        subagent_type: str,
        task_description: str,
        result: Any,
    ) -> SystemMessage:
        subagent_tracker.complete_subagent(subagent_id, str(result))
        completion_event = subagent_tracker.create_subagent_event(
            "subagent_completed", subagent_id, subagent_type, task_description, "completed"
        )
        return SystemMessage(
            content=(
                f"✅ **Subagent Completed**: {subagent_type}\n"
                f"**ID**: {subagent_id}\n"
                f"**Event Data**: {json.dumps(completion_event, indent=2)}"
            )
        )

    def _handle_success(
        result: Any,
        start_message: SystemMessage,
        completion_message: Optional[SystemMessage],
        tool_call_id: str,
        fallback_content: str,
    ) -> Command:
        prefix = [start_message]
        suffix = [completion_message] if completion_message is not None else []

        if isinstance(result, Command):
            existing_messages = list(result.update.get("messages", []) or [])
            has_tool_message = any(isinstance(msg, ToolMessage) for msg in existing_messages)

            if not has_tool_message:
                existing_messages.append(
                    ToolMessage(fallback_content, tool_call_id=tool_call_id)
                )

            result.update.setdefault("messages", [])
            result.update["messages"] = prefix + existing_messages + suffix
            return result

        message_content = (
            fallback_content if result is None or result == "" else str(result)
        )

        return Command(
            update={
                "messages": prefix
                + [ToolMessage(message_content, tool_call_id=tool_call_id)]
                + suffix
            }
        )

    def _handle_error(
        error: Exception,
        start_message: SystemMessage,
        subagent_id: str,
        subagent_type: str,
        task_description: str,
        tool_call_id: str,
    ) -> Command:
        subagent_tracker.error_subagent(subagent_id, str(error))
        error_event = subagent_tracker.create_subagent_event(
            "subagent_error", subagent_id, subagent_type, task_description, "error"
        )
        error_message = SystemMessage(
            content=(
                f"❌ **Subagent Error**: {subagent_type}\n"
                f"**ID**: {subagent_id}\n"
                f"**Error**: {str(error)}\n"
                f"**Event Data**: {json.dumps(error_event, indent=2)}"
            )
        )
        return Command(
            update={
                "messages": [
                    start_message,
                    ToolMessage(
                        f"Error in subagent {subagent_type}: {str(error)}",
                        tool_call_id=tool_call_id,
                    ),
                    error_message,
                ]
            }
        )

    if is_async:

        @tool(name=tool_name, description=description)
        async def enhanced_task(
            description: str,
            subagent_type: str,
            state: Annotated[DeepAgentState, InjectedState],
            tool_call_id: Annotated[str, InjectedToolCallId],
        ):
            subagent_id, start_message = _start_tracking(subagent_type, description)

            try:
                result = await original_task_tool.ainvoke(
                    {
                        "description": description,
                        "subagent_type": subagent_type,
                        "state": state,
                        "tool_call_id": tool_call_id,
                    }
                )
                resume_pending = isinstance(result, Command) and getattr(
                    result, "resume", None
                )

                if resume_pending:
                    completion_message: Optional[SystemMessage] = SystemMessage(
                        content=(
                            f"⏳ **Subagent Pending**: {subagent_type}\n"
                            f"**ID**: {subagent_id}\n"
                            "The subagent accepted the task and is still running."
                            " Resume the run once the subagent signals completion."
                        )
                    )
                    fallback_content = (
                        "Subagent acknowledged the task and is still running."
                        " Await further updates."
                    )
                else:
                    completion_message = _complete_tracking(
                        subagent_id, subagent_type, description, result
                    )
                    fallback_content = "Subagent completed without additional output."

                return _handle_success(
                    result,
                    start_message,
                    completion_message,
                    tool_call_id,
                    fallback_content,
                )
            except Exception as error:  # pragma: no cover - surfaces to UI
                return _handle_error(
                    error,
                    start_message,
                    subagent_id,
                    subagent_type,
                    description,
                    tool_call_id,
                )

        return enhanced_task

    @tool(description=description)
    def enhanced_task(
        description: str,
        subagent_type: str,
        state: Annotated[DeepAgentState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        subagent_id, start_message = _start_tracking(subagent_type, description)

        try:
            result = original_task_tool.invoke(
                {
                    "description": description,
                    "subagent_type": subagent_type,
                    "state": state,
                    "tool_call_id": tool_call_id,
                }
            )
            resume_pending = isinstance(result, Command) and getattr(
                result, "resume", None
            )

            if resume_pending:
                completion_message: Optional[SystemMessage] = None
                fallback_content = (
                    "Subagent acknowledged the task and is still running."
                    " Await further updates."
                )
            else:
                completion_message = _complete_tracking(
                    subagent_id, subagent_type, description, result
                )
                fallback_content = "Subagent completed without additional output."

            return _handle_success(
                result,
                start_message,
                completion_message,
                tool_call_id,
                fallback_content,
            )
        except Exception as error:  # pragma: no cover - surfaces to UI
            return _handle_error(
                error,
                start_message,
                subagent_id,
                subagent_type,
                description,
                tool_call_id,
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
