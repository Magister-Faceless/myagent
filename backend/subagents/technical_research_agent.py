"""
Technical Research Agent - Technical documentation, API research, and developer-focused analysis.
"""

from src.deepagents.sub_agent import SubAgent
from config.prompts import TECHNICAL_RESEARCH_PROMPT


def create_technical_research_agent() -> SubAgent:
    """
    Create a technical research subagent specialized in technical documentation and API research.
    
    This subagent focuses on:
    - Technical documentation analysis
    - API and software library research
    - Development best practices and patterns
    - Technology stack evaluation
    
    Returns:
        SubAgent configured for technical research tasks
    """
    
    return SubAgent(
        name="technical-research",
        description="Technical documentation, API research, and developer-focused analysis", 
        prompt=TECHNICAL_RESEARCH_PROMPT,
        # tools=[]  # Let subagent inherit tools from main agent to avoid KeyError
    )
