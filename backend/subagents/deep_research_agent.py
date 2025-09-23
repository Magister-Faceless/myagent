"""
Deep Research Agent - Comprehensive multi-source research with citation validation.
"""

from src.deepagents.sub_agent import SubAgent
from config.prompts import DEEP_RESEARCH_PROMPT


def create_deep_research_agent() -> SubAgent:
    """
    Create a deep research subagent specialized in comprehensive research with citations.
    
    This subagent focuses on:
    - Multi-source research and validation
    - Comprehensive citation management
    - Cross-referencing information for accuracy
    - Synthesizing findings from authoritative sources
    
    Returns:
        SubAgent configured for deep research tasks
    """
    
    return SubAgent(
        name="deep-research",
        description="Conducts long-horizon, source-backed web research with citations and synthesis",
        prompt=DEEP_RESEARCH_PROMPT,
        tools=[
            "perplexity_reasoning_search",
            "perplexity_focused_research"
        ]
    )
