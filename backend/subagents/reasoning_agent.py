"""
Perplexity reasoning subagent for advanced analysis and research.
"""

from config.prompts import REASONING_SUBAGENT_PROMPT
from models import get_deep_research_model


def create_reasoning_subagent():
    """Create a Perplexity reasoning subagent configuration."""
    return {
        "name": "perplexity-reasoning-agent",
        "description": """Advanced reasoning and analysis specialist with real-time web search capabilities. Use this agent for:
        - Multi-step problem solving and complex analysis
        - Strategic planning and decision making
        - Detailed research with filtering (by domain, date, recency)
        - Tasks requiring deep reasoning with current information
        - When users specifically request advanced reasoning or analysis
        
        This agent can filter search results by domain, publication date, last updated date, and recency.""",
        "prompt": REASONING_SUBAGENT_PROMPT,
        # "tools": [],  # Let subagent inherit tools from main agent to avoid KeyError
        "model": get_deep_research_model(),
    }
