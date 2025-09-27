"""
Operation Monitor Tool - Enhanced error handling and retry mechanism for long-running operations
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Callable, Annotated
from datetime import datetime, timedelta
import json

from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command

try:
    from langgraph.prebuilt import InjectedState
except ImportError:
    from typing import Any
    InjectedState = Any

from deepagents.state import DeepAgentState


class OperationMonitor:
    """Monitor and manage long-running operations with timeout and retry capabilities."""
    
    def __init__(self):
        self.operations: Dict[str, Dict[str, Any]] = {}
        self.timeout_threshold = 300  # 5 minutes default timeout
        self.retry_attempts = 3
    
    def start_operation(self, operation_id: str, operation_type: str, description: str, timeout: int = None) -> None:
        """Start monitoring an operation."""
        self.operations[operation_id] = {
            "id": operation_id,
            "type": operation_type,
            "description": description,
            "status": "running",
            "started_at": datetime.now(),
            "timeout": timeout or self.timeout_threshold,
            "retry_count": 0,
            "last_update": datetime.now(),
            "progress_messages": []
        }
    
    def update_operation(self, operation_id: str, message: str, progress: Optional[float] = None) -> None:
        """Update operation progress."""
        if operation_id in self.operations:
            self.operations[operation_id]["last_update"] = datetime.now()
            self.operations[operation_id]["progress_messages"].append({
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "progress": progress
            })
    
    def complete_operation(self, operation_id: str, result: Any = None) -> None:
        """Mark operation as completed."""
        if operation_id in self.operations:
            self.operations[operation_id].update({
                "status": "completed",
                "completed_at": datetime.now(),
                "result": result
            })
    
    def fail_operation(self, operation_id: str, error: str) -> None:
        """Mark operation as failed."""
        if operation_id in self.operations:
            self.operations[operation_id].update({
                "status": "failed",
                "completed_at": datetime.now(),
                "error": error,
                "retry_count": self.operations[operation_id].get("retry_count", 0) + 1
            })
    
    def check_timeouts(self) -> List[str]:
        """Check for timed out operations."""
        timed_out = []
        now = datetime.now()
        
        for op_id, op_info in self.operations.items():
            if op_info["status"] == "running":
                elapsed = (now - op_info["started_at"]).total_seconds()
                if elapsed > op_info["timeout"]:
                    timed_out.append(op_id)
                    self.fail_operation(op_id, f"Operation timed out after {elapsed:.1f} seconds")
        
        return timed_out
    
    def get_stalled_operations(self, stall_threshold: int = 60) -> List[str]:
        """Get operations that haven't been updated recently."""
        stalled = []
        now = datetime.now()
        
        for op_id, op_info in self.operations.items():
            if op_info["status"] == "running":
                time_since_update = (now - op_info["last_update"]).total_seconds()
                if time_since_update > stall_threshold:
                    stalled.append(op_id)
        
        return stalled
    
    def can_retry(self, operation_id: str) -> bool:
        """Check if operation can be retried."""
        if operation_id not in self.operations:
            return False
        
        op_info = self.operations[operation_id]
        return (op_info["status"] == "failed" and 
                op_info.get("retry_count", 0) < self.retry_attempts)


# Global monitor instance
operation_monitor = OperationMonitor()


@tool(description="Monitor long-running operations and provide status updates")
def check_operation_status(
    operation_id: Optional[str] = None,
    state: Annotated[DeepAgentState, InjectedState] = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
) -> Command:
    """
    Check the status of long-running operations and detect issues.
    
    Args:
        operation_id: Specific operation to check (optional)
        state: Agent state (injected automatically)
        tool_call_id: Tool call ID (injected automatically)
    
    Returns:
        Command with operation status information
    """
    messages = []
    
    # Check for timeouts
    timed_out = operation_monitor.check_timeouts()
    if timed_out:
        for op_id in timed_out:
            op_info = operation_monitor.operations[op_id]
            messages.append(
                ToolMessage(
                    content=f"⏰ **Operation Timeout**: {op_info['type']}\n"
                           f"**ID**: {op_id}\n"
                           f"**Description**: {op_info['description']}\n"
                           f"**Duration**: {(datetime.now() - op_info['started_at']).total_seconds():.1f}s\n"
                           f"**Status**: Operation has been marked as failed due to timeout.",
                    tool_call_id=tool_call_id,
                    additional_kwargs={"timeout": True, "operation_id": op_id}
                )
            )
    
    # Check for stalled operations
    stalled = operation_monitor.get_stalled_operations()
    if stalled:
        for op_id in stalled:
            op_info = operation_monitor.operations[op_id]
            time_since_update = (datetime.now() - op_info['last_update']).total_seconds()
            messages.append(
                ToolMessage(
                    content=f"🐌 **Operation Stalled**: {op_info['type']}\n"
                           f"**ID**: {op_id}\n"
                           f"**Description**: {op_info['description']}\n"
                           f"**Last Update**: {time_since_update:.1f}s ago\n"
                           f"**Status**: Operation may be stuck or experiencing issues.",
                    tool_call_id=tool_call_id,
                    additional_kwargs={"stalled": True, "operation_id": op_id}
                )
            )
    
    # Get specific operation status if requested
    if operation_id and operation_id in operation_monitor.operations:
        op_info = operation_monitor.operations[operation_id]
        elapsed = (datetime.now() - op_info['started_at']).total_seconds()
        
        status_emoji = {
            "running": "🔄",
            "completed": "✅",
            "failed": "❌"
        }.get(op_info['status'], "❓")
        
        progress_summary = ""
        if op_info.get('progress_messages'):
            recent_messages = op_info['progress_messages'][-3:]  # Last 3 messages
            progress_summary = "\n**Recent Progress:**\n" + "\n".join([
                f"- {msg['message']}" for msg in recent_messages
            ])
        
        messages.append(
            ToolMessage(
                content=f"{status_emoji} **Operation Status**: {op_info['type']}\n"
                       f"**ID**: {operation_id}\n"
                       f"**Description**: {op_info['description']}\n"
                       f"**Status**: {op_info['status'].title()}\n"
                       f"**Duration**: {elapsed:.1f}s\n"
                       f"**Retry Count**: {op_info.get('retry_count', 0)}/{operation_monitor.retry_attempts}\n"
                       f"{progress_summary}",
                tool_call_id=tool_call_id,
                additional_kwargs={"operation_status": op_info['status'], "operation_id": operation_id}
            )
        )
    
    # General status if no specific operation requested
    if not operation_id:
        running_ops = [op for op in operation_monitor.operations.values() if op['status'] == 'running']
        
        if not running_ops and not timed_out and not stalled:
            messages.append(
                ToolMessage(
                    content="✅ **All Operations Normal**: No long-running operations detected.",
                    tool_call_id=tool_call_id,
                    additional_kwargs={"all_clear": True}
                )
            )
        elif running_ops:
            op_list = "\n".join([
                f"- {op['type']}: {op['description']} (Running for {(datetime.now() - op['started_at']).total_seconds():.1f}s)"
                for op in running_ops
            ])
            messages.append(
                ToolMessage(
                    content=f"🔄 **Active Operations** ({len(running_ops)}):\n{op_list}",
                    tool_call_id=tool_call_id,
                    additional_kwargs={"active_operations": len(running_ops)}
                )
            )
    
    return Command(update={"messages": messages})


@tool(description="Suggest alternative approaches when operations fail or stall")
def suggest_alternatives(
    failed_operation_type: str,
    error_description: str = "",
    state: Annotated[DeepAgentState, InjectedState] = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
) -> Command:
    """
    Suggest alternative approaches when operations fail or encounter issues.
    
    Args:
        failed_operation_type: Type of operation that failed
        error_description: Description of the error or issue
        state: Agent state (injected automatically)
        tool_call_id: Tool call ID (injected automatically)
    
    Returns:
        Command with suggested alternatives
    """
    alternatives = {
        "scroll_export_works": [
            "Try using search_works with smaller batch sizes (limit=50)",
            "Use search_works with pagination (offset parameter) to retrieve results in chunks",
            "Reduce the max_results parameter to a smaller number (e.g., 100-500)",
            "Try different output formats (json instead of csv)",
            "Check if the query is too broad and narrow it down",
            "Use time_trend_analysis for a quick overview before full export"
        ],
        "literature_review": [
            "Break down the review into smaller, focused searches",
            "Use the planning_coordinator subagent to create a more structured approach",
            "Try manual search_works calls instead of automated export",
            "Focus on specific years or document types first",
            "Use quality_assessment tool on a smaller subset first"
        ],
        "subagent_task": [
            "Try spawning subagents with more specific, focused tasks",
            "Use get_active_subagents to check current subagent status",
            "Break complex tasks into multiple simpler subagent calls",
            "Check subagent prompts for clarity and specificity",
            "Use direct tool calls instead of subagent delegation for simple tasks"
        ]
    }
    
    suggestions = alternatives.get(failed_operation_type, [
        "Try breaking the task into smaller components",
        "Check for network connectivity issues",
        "Verify API credentials and rate limits",
        "Use alternative tools or approaches",
        "Contact support if the issue persists"
    ])
    
    suggestion_text = "\n".join([f"• {suggestion}" for suggestion in suggestions])
    
    message_content = f"💡 **Alternative Approaches for {failed_operation_type}**\n\n"
    
    if error_description:
        message_content += f"**Error Context**: {error_description}\n\n"
    
    message_content += f"**Suggested Alternatives**:\n{suggestion_text}\n\n"
    message_content += "**General Troubleshooting**:\n"
    message_content += "• Check operation_monitor for timeout/stall detection\n"
    message_content += "• Use get_active_subagents to monitor subagent status\n"
    message_content += "• Consider using smaller batch sizes or simpler queries\n"
    message_content += "• Try alternative tools that accomplish similar goals"
    
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=message_content,
                    tool_call_id=tool_call_id,
                    additional_kwargs={
                        "alternatives_provided": True,
                        "operation_type": failed_operation_type,
                        "suggestion_count": len(suggestions)
                    }
                )
            ]
        }
    )


def create_monitored_operation(operation_type: str, description: str, timeout: int = 300):
    """
    Decorator to automatically monitor long-running operations.
    
    Args:
        operation_type: Type of operation (e.g., "export", "search", "analysis")
        description: Human-readable description of the operation
        timeout: Timeout in seconds (default: 5 minutes)
    
    Returns:
        Decorator function
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            operation_id = f"{operation_type}_{int(time.time())}"
            operation_monitor.start_operation(operation_id, operation_type, description, timeout)
            
            try:
                # Update progress at start
                operation_monitor.update_operation(operation_id, "Operation started")
                
                result = await func(*args, **kwargs)
                
                operation_monitor.complete_operation(operation_id, result)
                return result
                
            except Exception as e:
                operation_monitor.fail_operation(operation_id, str(e))
                raise
        
        def sync_wrapper(*args, **kwargs):
            operation_id = f"{operation_type}_{int(time.time())}"
            operation_monitor.start_operation(operation_id, operation_type, description, timeout)
            
            try:
                operation_monitor.update_operation(operation_id, "Operation started")
                
                result = func(*args, **kwargs)
                
                operation_monitor.complete_operation(operation_id, result)
                return result
                
            except Exception as e:
                operation_monitor.fail_operation(operation_id, str(e))
                raise
        
        # Return appropriate wrapper based on whether function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
