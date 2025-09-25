"""
Market Analysis Agent - Specialized in market trends, competitive analysis, and business intelligence.
"""

from src.deepagents.sub_agent import SubAgent
from config.prompts import MARKET_ANALYSIS_PROMPT


def create_market_analysis_agent() -> SubAgent:
    """
    Create a market analysis subagent specialized in business intelligence and market research.
    
    This subagent focuses on:
    - Market trend identification and analysis
    - Competitive landscape assessment
    - Business intelligence gathering
    - Financial and economic analysis
    
    Returns:
        SubAgent configured for market analysis tasks
    """
    
    return SubAgent(
        name="market-analysis", 
        description="Specialized in market trends, competitive analysis, and business intelligence",
        prompt=MARKET_ANALYSIS_PROMPT,
        # tools=[]  # Let subagent inherit tools from main agent to avoid KeyError
    )
