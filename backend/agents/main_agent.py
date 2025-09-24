"""
Main agent implementation using the deep agents framework.
"""

import os
from typing import Literal, Any
from src.deepagents import create_deep_agent
from src.deepagents.sub_agent import SubAgent

# Import tools from the tools module
from tools.search.tavily_search import tavily_search, tavily_qna_search
from tools.search.perplexity import perplexity_reasoning_search, perplexity_focused_research
from tools.search.perplexity_strategies import academic_search, technical_search, market_research, deep_research
from tools.search.sonar_deep_research import sonar_deep_research

# Import utility tools
from tools.subagent_tracker import get_active_subagents, get_subagent_summary

# Import subagent creators
from subagents.general_agent import create_general_subagent
from subagents.reasoning_agent import create_reasoning_subagent
from subagents.deep_research_agent import create_deep_research_agent
from subagents.market_analysis_agent import create_market_analysis_agent
from subagents.technical_research_agent import create_technical_research_agent

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
    deep_research_subagent = create_deep_research_agent()
    market_analysis_subagent = create_market_analysis_agent()
    technical_research_subagent = create_technical_research_agent()
    
    # Get the default model with fallback
    model = get_default_model()
    
    # Create the main deep agent with human-in-the-loop for high-cost operations
    agent = create_deep_agent(
        tools=[
            # General search tools
            tavily_search, 
            tavily_qna_search, 
            # Perplexity reasoning tools
            perplexity_reasoning_search, 
            perplexity_focused_research,
            # Specialized research strategy tools
            academic_search,
            technical_search,
            market_research,
            deep_research,
            # Elite sonar deep research tool
            sonar_deep_research,
            # Utility tools for task and subagent management
            get_active_subagents,
            get_subagent_summary
        ],
        instructions=MAIN_AGENT_INSTRUCTIONS,
        subagents=[
            general_subagent, 
            reasoning_subagent,
            deep_research_subagent,
            market_analysis_subagent,
            technical_research_subagent
        ],
        model=model,
        # Configure human-in-the-loop for task spawning when using sonar-deep-research agent
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
agent = create_main_agent()
