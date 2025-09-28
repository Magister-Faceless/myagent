"""
Memory Integration Helper for Existing Agents

This module provides utilities to add memory capabilities to existing agents
without requiring major restructuring.
"""

from typing import List, Dict, Any, Optional
from langchain_core.tools import tool

from core.memory.memory_agent import get_memory_agent
from core.memory.cross_agent_manager import get_cross_agent_manager
from tools.memory_enhanced_tools import (
    get_shared_context_summary,
    get_thread_memory_context,
    enhanced_read_file,
    enhanced_write_file,
    intelligent_file_search
)


def add_memory_tools_to_agent(existing_tools: List) -> List:
    """
    Add essential memory tools to an existing agent's tool list
    
    Args:
        existing_tools: List of existing tools
        
    Returns:
        Enhanced tool list with memory capabilities
    """
    memory_tools = [
        get_shared_context_summary,
        get_thread_memory_context,
        enhanced_read_file,
        enhanced_write_file,
        intelligent_file_search
    ]
    
    return existing_tools + memory_tools


@tool
def enable_memory_for_agent(
    agent_name: str,
    thread_id: str,
    user_input: str = "",
    ai_output: str = ""
) -> str:
    """
    Enable memory processing for any agent
    
    Args:
        agent_name: Name of the agent
        thread_id: Thread ID for context
        user_input: User's input to process
        ai_output: Agent's output to process
        
    Returns:
        Success message
    """
    try:
        if user_input and ai_output:
            memory_agent = get_memory_agent()
            memory = memory_agent.process_conversation(
                thread_id=thread_id,
                user_input=user_input,
                ai_output=ai_output,
                agent_name=agent_name
            )
            
            return f"✅ Memory processed for {agent_name}: {memory.classification}"
        else:
            return f"✅ Memory system enabled for {agent_name}"
            
    except Exception as e:
        return f"⚠️ Memory processing failed for {agent_name}: {e}"


def create_memory_aware_agent_wrapper(original_agent_creator, agent_name: str):
    """
    Create a wrapper that adds memory capabilities to any existing agent
    
    Args:
        original_agent_creator: Original agent creation function
        agent_name: Name of the agent for memory tracking
        
    Returns:
        Memory-enhanced agent
    """
    def memory_enhanced_creator():
        # Create the original agent
        agent = original_agent_creator()
        
        # Add memory processing hook
        original_invoke = agent.invoke
        
        def memory_aware_invoke(input_data, config=None):
            """Enhanced invoke with memory processing"""
            try:
                # Call original invoke
                result = original_invoke(input_data, config)
                
                # Process for memory if thread context available
                if config and "configurable" in config:
                    thread_id = config["configurable"].get("thread_id")
                    if thread_id:
                        try:
                            # Extract conversation data
                            user_input = ""
                            ai_output = ""
                            
                            if isinstance(input_data, dict) and "messages" in input_data:
                                messages = input_data["messages"]
                                if messages and isinstance(messages[-1], dict):
                                    user_input = messages[-1].get("content", "")
                            
                            if isinstance(result, dict) and "messages" in result:
                                ai_messages = result["messages"]
                                if ai_messages and isinstance(ai_messages[-1], dict):
                                    ai_output = ai_messages[-1].get("content", "")
                            
                            # Process memory
                            if user_input and ai_output:
                                memory_agent = get_memory_agent()
                                memory_agent.process_conversation(
                                    thread_id=thread_id,
                                    user_input=user_input,
                                    ai_output=ai_output,
                                    agent_name=agent_name
                                )
                                
                        except Exception as e:
                            print(f"⚠️ Memory processing failed for {agent_name}: {e}")
                
                return result
                
            except Exception as e:
                print(f"❌ Enhanced invoke failed for {agent_name}: {e}")
                return original_invoke(input_data, config)
        
        # Replace invoke method
        agent.invoke = memory_aware_invoke
        return agent
    
    return memory_enhanced_creator


# Export for easy import
__all__ = [
    "add_memory_tools_to_agent",
    "enable_memory_for_agent", 
    "create_memory_aware_agent_wrapper"
]
