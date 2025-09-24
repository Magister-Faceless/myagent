"""Utility functions for DeepAgents."""
import json
import hashlib
import datetime
from typing import Any, Dict, Optional, Union
from pathlib import Path
from langgraph.types import Command
from langchain_core.messages import ToolMessage

def should_write_to_file(content: Any, max_length: int = 2000) -> bool:
    """Determine if content should be written to a file based on its length."""
    if content is None:
        return False
    if isinstance(content, (dict, list)):
        content = json.dumps(content, indent=2)
    return len(str(content)) > max_length

def generate_filename(tool_name: str, extension: str = 'txt') -> str:
    """Generate a unique filename based on tool name and timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name_hash = hashlib.md5(tool_name.encode()).hexdigest()[:8]
    return f"tool_outputs/{tool_name}_{name_hash}_{timestamp}.{extension}"

def write_large_response(
    content: Any, 
    tool_name: str, 
    state: Dict,
    tool_call_id: str,
    file_extension: str = 'txt'
) -> Command:
    """Write large response to a file and return a command to update the state.
    
    Args:
        content: The content to write to file
        tool_name: Name of the tool that generated the content
        state: The current agent state
        tool_call_id: The ID of the tool call
        file_extension: File extension for the output file
        
    Returns:
        A Command object that updates the state with the file and a notification message
    """
    try:
        # Validate inputs
        if not tool_name:
            raise ValueError("tool_name cannot be empty")
        if not tool_call_id:
            raise ValueError("tool_call_id cannot be empty")
        if not isinstance(state, dict):
            raise ValueError("state must be a dictionary")
        
        # Convert content to string if it's a dict or list
        if isinstance(content, (dict, list)):
            content_str = json.dumps(content, indent=2)
            file_extension = 'json' if file_extension == 'txt' else file_extension
        else:
            content_str = str(content)
        
        # Generate a filename
        file_path = generate_filename(tool_name, file_extension)
        
        # Get existing files or initialize empty dict
        files = state.get("files", {})
        files[file_path] = content_str
        
        # Create a notification message
        message = f"[Large output from {tool_name} was written to {file_path}]"
        
        # Return the command to update the state
        return Command(
            update={
                "files": files,
                "messages": [
                    ToolMessage(
                        content=message,
                        tool_call_id=tool_call_id,
                        additional_kwargs={
                            "file_reference": file_path,
                            "tool_name": tool_name,
                            "is_large_output": True
                        }
                    )
                ]
            }
        )
    except Exception as e:
        # Return error message if file writing fails
        error_message = f"Error writing large response to file: {str(e)}"
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=error_message,
                        tool_call_id=tool_call_id,
                        additional_kwargs={
                            "error": True,
                            "tool_name": tool_name
                        }
                    )
                ]
            }
        )
