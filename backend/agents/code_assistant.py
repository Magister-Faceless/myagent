"""
Code assistant agent implementation using the deep agents framework.
Specialized for software development, programming tasks, and technical problem solving.
"""

import os
from typing import Literal, Any
from src.deepagents import create_deep_agent
from src.deepagents.sub_agent import SubAgent

# Import coding-focused tools
from tools.search.tavily_search import tavily_search, tavily_qna_search
from tools.search.perplexity import perplexity_focused_research
from tools.search.perplexity_strategies import technical_search

# Import utility tools
from tools.subagent_tracker import get_active_subagents, get_subagent_summary

# Import coding-focused subagent creators
from subagents.general_agent import create_general_subagent
from subagents.reasoning_agent import create_reasoning_subagent
from subagents.technical_research_agent import create_technical_research_agent

# Import configuration
from config.prompts import CODING_AGENT_INSTRUCTIONS
from config.settings import get_settings

# Import model configuration
from models import get_default_model

# Import checkpointer configuration
from config.checkpointer import get_default_checkpointer


def create_code_assistant():
    """Create and configure the coding-specialized deep agent."""
    # Get application settings
    settings = get_settings()
    
    # Create coding-focused subagents
    general_subagent = create_general_subagent()
    reasoning_subagent = create_reasoning_subagent()
    technical_research_subagent = create_technical_research_agent()
    
    # Get the default model with fallback
    model = get_default_model()
    
    # Get persistent checkpointer for state storage
    checkpointer = get_default_checkpointer()
    
    # Create the coding deep agent with development-optimized tools
    agent = create_deep_agent(
        tools=[
            # General search tools for documentation and solutions
            tavily_search, 
            tavily_qna_search,
            # Focused research for technical problems
            perplexity_focused_research,
            # Technical search for programming solutions
            technical_search,
            # Utility tools for task and subagent management
            get_active_subagents,
            get_subagent_summary
        ],
        instructions=CODING_AGENT_INSTRUCTIONS,
        subagents=[
            general_subagent, 
            reasoning_subagent,
            technical_research_subagent  # Primary subagent for coding tasks
        ],
        model=model,
        checkpointer=checkpointer,
        # Configure for coding workflow
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
agent = create_code_assistant()
