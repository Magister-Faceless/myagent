"""
Content creator agent implementation using the deep agents framework.
Specialized for writing, content creation, and creative tasks.
"""

import os
from typing import Literal, Any
from src.deepagents import create_deep_agent
from src.deepagents.sub_agent import SubAgent

# Import content creation-focused tools
from tools.search.tavily_search import tavily_search, tavily_qna_search
from tools.search.perplexity import perplexity_reasoning_search

# Import utility tools
from tools.subagent_tracker import get_active_subagents, get_subagent_summary

# Import creative-focused subagent creators
from subagents.general_agent import create_general_subagent
from subagents.reasoning_agent import create_reasoning_subagent

# Import configuration
from config.prompts import CREATIVE_AGENT_INSTRUCTIONS
from config.settings import get_settings

# Import model configuration
from models import get_default_model


def create_content_creator():
    """Create and configure the content creation-specialized deep agent."""
    # Get application settings
    settings = get_settings()
    
    # Create creative-focused subagents
    general_subagent = create_general_subagent()
    reasoning_subagent = create_reasoning_subagent()
    
    # Get the default model with fallback
    model = get_default_model()
    
    # Create the creative deep agent with content-optimized tools
    agent = create_deep_agent(
        tools=[
            # General search tools for research and inspiration
            tavily_search, 
            tavily_qna_search,
            # Reasoning search for creative ideation
            perplexity_reasoning_search,
            # Utility tools for task and subagent management
            get_active_subagents,
            get_subagent_summary
        ],
        instructions=CREATIVE_AGENT_INSTRUCTIONS,
        subagents=[
            general_subagent, 
            reasoning_subagent  # Primary subagents for creative tasks
        ],
        model=model,
        # Configure for creative workflow
        interrupt_config={
            "task": {
                "allow_ignore": False,
                "allow_respond": True,
                "allow_edit": True,
                "allow_accept": True,
            }
        }
    ).with_config({"recursion_limit": settings["recursion_limit"]})
    
    return agent


# Create the agent instance for LangGraph
agent = create_content_creator()
