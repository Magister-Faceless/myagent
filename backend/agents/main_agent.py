"""
Main agent implementation using the deep agents framework.
"""

import os
from typing import Literal, Any
from deepagents import create_deep_agent, SubAgent

# Import tools from the tools module
from tools.search.tavily_search import tavily_search, tavily_qna_search
from tools.search.perplexity import perplexity_reasoning_search, perplexity_focused_research

# Import subagent creators
from subagents.general_agent import create_general_subagent
from subagents.reasoning_agent import create_reasoning_subagent

# Import configuration
from config.prompts import MAIN_AGENT_INSTRUCTIONS
from config.settings import get_settings

# Import model configuration
from models import get_default_model


def create_main_agent():
    """Create and configure the main deep agent."""
    # Get application settings
    settings = get_settings()
    
    # Create subagents
    general_subagent = create_general_subagent()
    reasoning_subagent = create_reasoning_subagent()
    
    # Get the default model with fallback
    model = get_default_model()
    
    # Create the main deep agent
    agent = create_deep_agent(
        tools=[
            tavily_search, 
            tavily_qna_search, 
            perplexity_reasoning_search, 
            perplexity_focused_research
        ],
        instructions=MAIN_AGENT_INSTRUCTIONS,
        subagents=[general_subagent, reasoning_subagent],
        model=model,
    ).with_config({"recursion_limit": settings["recursion_limit"]})
    
    return agent


# Create the agent instance for LangGraph
agent = create_main_agent()
