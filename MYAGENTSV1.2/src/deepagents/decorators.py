"""Decorators for DeepAgents tools."""
import inspect
from typing import Callable, Any, Dict, Optional, get_type_hints, get_origin, get_args
from functools import wraps
from .utils import should_write_to_file, write_large_response


def handle_large_response(
    max_length: int = 2000,
    file_extension: str = 'txt',
    always_write: bool = False
):
    """Decorator to automatically write large tool responses to files.
    
    Args:
        max_length: Maximum length of response before writing to file
        file_extension: File extension for the output file
        always_write: If True, always write to file regardless of response size
    """
    def decorator(tool_func):
        @wraps(tool_func)
        def wrapper(*args, **kwargs):
            # Call the original function
            result = tool_func(*args, **kwargs)
            
            # Extract state and tool_call_id using function signature
            state = None
            tool_call_id = None
            
            # Get function signature and parameter names
            sig = inspect.signature(tool_func)
            param_names = list(sig.parameters.keys())
            
            # Map positional args to parameter names
            bound_args = sig.bind_partial(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Look for state parameter (should be annotated with DeepAgentState or InjectedState)
            for param_name, param_value in bound_args.arguments.items():
                param_info = sig.parameters[param_name]
                
                # Check if this is a state parameter
                if hasattr(param_value, 'get') and isinstance(param_value, dict):
                    # Additional check: see if it has 'files' key or looks like agent state
                    if 'files' in param_value or 'messages' in param_value:
                        state = param_value
                
                # Check if this is a tool_call_id parameter
                if param_name == 'tool_call_id' or (
                    isinstance(param_value, str) and 
                    (param_value.startswith('call_') or param_value.startswith('toolu_'))
                ):
                    tool_call_id = param_value
            
            # Also check kwargs directly for common parameter names
            state = kwargs.get('state', state)
            tool_call_id = kwargs.get('tool_call_id', tool_call_id)
            
            # If we have state and tool_call_id, handle large responses
            if state is not None and tool_call_id is not None:
                # Check if we should write to file
                if always_write or should_write_to_file(result, max_length):
                    tool_name = tool_func.__name__
                    return write_large_response(
                        result, 
                        tool_name, 
                        state, 
                        tool_call_id,
                        file_extension=file_extension
                    )
            
            # Otherwise return the result as-is
            return result
        return wrapper
    return decorator
