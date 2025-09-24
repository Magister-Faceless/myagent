"""
Task management utilities for better todo list handling.
"""

from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
import uuid


def create_task_id(prefix: str = "task") -> str:
    """Generate a unique task ID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{short_uuid}"


def update_todo_list(
    todos: List[Dict[str, Any]],
    task_id: str,
    status: Literal["pending", "in_progress", "completed", "error"],
    content: Optional[str] = None,
    details: Optional[str] = None,
    priority: Literal["low", "medium", "high"] = "medium"
) -> List[Dict[str, Any]]:
    """
    Update a todo item in the list or create a new one if it doesn't exist.
    
    Args:
        todos: Current list of todo items
        task_id: Unique identifier for the task
        status: New status for the task
        content: Task description (required for new tasks)
        details: Additional details about the task progress
        priority: Task priority level
    
    Returns:
        Updated list of todo items
    """
    # Make a copy to avoid mutating the original
    updated_todos = todos.copy() if todos else []
    
    # Find existing task
    task_found = False
    for i, todo in enumerate(updated_todos):
        if todo.get("id") == task_id:
            # Update existing task
            updated_todos[i] = {
                **todo,
                "status": status,
                "updatedAt": datetime.now().isoformat(),
            }
            
            # Update content if provided
            if content is not None:
                updated_todos[i]["content"] = content
            
            # Add details if provided
            if details is not None:
                updated_todos[i]["details"] = details
                
            task_found = True
            break
    
    # If task not found, create new one
    if not task_found:
        if content is None:
            raise ValueError("Content is required when creating a new task")
            
        new_task = {
            "id": task_id,
            "content": content,
            "status": status,
            "priority": priority,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
        }
        
        if details is not None:
            new_task["details"] = details
            
        updated_todos.append(new_task)
    
    return updated_todos


def mark_task_in_progress(
    todos: List[Dict[str, Any]], 
    task_id: str, 
    content: str,
    details: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Mark a task as in progress."""
    return update_todo_list(todos, task_id, "in_progress", content, details)


def mark_task_completed(
    todos: List[Dict[str, Any]], 
    task_id: str, 
    details: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Mark a task as completed."""
    return update_todo_list(todos, task_id, "completed", details=details)


def mark_task_error(
    todos: List[Dict[str, Any]], 
    task_id: str, 
    error_details: str
) -> List[Dict[str, Any]]:
    """Mark a task as having an error."""
    return update_todo_list(todos, task_id, "error", details=f"Error: {error_details}")


def get_task_summary(todos: List[Dict[str, Any]]) -> Dict[str, int]:
    """Get a summary of task statuses."""
    summary = {"pending": 0, "in_progress": 0, "completed": 0, "error": 0}
    
    for todo in todos:
        status = todo.get("status", "pending")
        if status in summary:
            summary[status] += 1
    
    return summary


def format_task_update_message(task_id: str, status: str, details: Optional[str] = None) -> str:
    """Format a user-friendly message about task updates."""
    status_emoji = {
        "pending": "⏳",
        "in_progress": "🔄", 
        "completed": "✅",
        "error": "❌"
    }
    
    emoji = status_emoji.get(status, "📋")
    message = f"{emoji} Task {task_id}: {status.replace('_', ' ').title()}"
    
    if details:
        message += f"\n{details}"
    
    return message
