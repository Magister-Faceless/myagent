"""
Main agent implementation using the deep agents framework.
"""

import os
from typing import Literal, Any
from src.deepagents import create_deep_agent
from src.deepagents.sub_agent import SubAgent

# Import essential tools only - lean approach for generalist agent
from tools.search.tavily_search import tavily_search  # Basic web search capability

# Import memory-enhanced tools for file management
from tools.memory_enhanced_tools import (
    enhanced_write_file,
    enhanced_read_file,
    intelligent_file_search,
    get_thread_memory_context,
    get_shared_context_summary,
)

# Import essential utility tools
from tools.subagent_tracker import get_active_subagents, get_subagent_summary

# Import core subagent creators - lean approach
from subagents.planning_coordinator import create_planning_coordinator
from subagents.general_agent import create_general_subagent
from subagents.qa_reviewer import create_qa_reviewer

# Import configuration
from config.prompts import MAIN_AGENT_INSTRUCTIONS
from config.settings import get_settings

# Import model configuration
from models import get_default_model

# Import checkpointer configuration
from config.checkpointer import get_default_checkpointer

# Utilities
from utils.subagent_tracking import enable_subagent_tracking


def create_main_agent():
    """Create and configure the lean generalist main agent.
    
    This agent is designed to be a generalist that can handle most tasks directly,
    but can dynamically spawn specialized subagents when complex domain-specific
    work is required. It uses minimal tools to avoid context window bloat.
    """
    # Get application settings
    settings = get_settings()
    
    # Create essential subagents only
    general_subagent = create_general_subagent()
    planning_coordinator = create_planning_coordinator()
    qa_reviewer = create_qa_reviewer()
    
    # Get the default model with fallback
    model = get_default_model()
    
    # Get persistent checkpointer for state storage
    checkpointer = get_default_checkpointer()
    
    # Create the lean main deep agent with adaptive specialization capability
    with enable_subagent_tracking():
        agent = create_deep_agent(
            tools=[
                # Essential search capability
                tavily_search,
                # Memory-enhanced file management (essential for all tasks)
                enhanced_write_file,
                enhanced_read_file,
                intelligent_file_search,
                get_thread_memory_context,
                get_shared_context_summary,
                # Subagent management tools
                get_active_subagents,
                get_subagent_summary,
            ],
            instructions=MAIN_AGENT_INSTRUCTIONS,
            subagents=[
                planning_coordinator,  # Enhanced for specialization decisions
                general_subagent,      # For general task delegation
                qa_reviewer,           # For quality assurance
            ],
            model=model,
            checkpointer=checkpointer,
            # Configure human-in-the-loop for specialization decisions
            interrupt_config={
                "task": {  # Interrupt when spawning specialized subagents
                    "allow_ignore": False,
                    "allow_respond": True,
                    "allow_edit": True,
                    "allow_accept": True,
                }
            },
        ).with_config({"recursion_limit": settings["recursion_limit"]})

    return agent


# Create the agent instance for LangGraph
agent = create_main_agent()
