"""
Sonar Deep Research Agent - Elite research specialist using Perplexity's sonar-deep-research model.
"""

from src.deepagents.sub_agent import SubAgent
from config.prompts import SONAR_DEEP_RESEARCH_PROMPT
from models import get_perplexity_model


def create_deep_research_agent() -> SubAgent:
    """
    Create an elite deep research subagent powered by Perplexity's sonar-deep-research model.
    
    This subagent represents the pinnacle of AI research capability, featuring:
    - Exhaustive research across hundreds of sources
    - Expert-level analysis with 128K context length
    - Comprehensive report generation (10,000+ words)
    - Advanced reasoning with configurable computational effort
    - Automatic file-based output to prevent context overflow
    
    IMPORTANT: This agent requires human approval before execution due to:
    - High computational cost and resource usage
    - Long execution time (potentially 5-15 minutes)
    - Comprehensive analysis that may consume significant API credits
    - Generation of extensive reports that require file storage
    
    The agent will:
    1. Plan comprehensive research methodology
    2. Execute exhaustive research using sonar-deep-research model
    3. Generate detailed reports (typically 10,000+ words)
    4. Save all findings to files to preserve full analysis
    5. Provide executive summary for immediate review
    
    Returns:
        SubAgent configured for elite-level deep research tasks
    """
    
    return SubAgent(
        name="sonar-deep-research",
        description="""🔬 ELITE RESEARCH SPECIALIST - Powered by Perplexity's sonar-deep-research model

⚠️  HIGH-INTENSITY RESEARCH AGENT ⚠️
This agent conducts exhaustive, expert-level research using the most advanced model available.

CAPABILITIES:
• Exhaustive research across hundreds of authoritative sources
• Expert-level analysis with 128K context length  
• Comprehensive reports (typically 10,000+ words)
• Advanced reasoning with maximum computational effort
• Real-time access to current information and developments

RESOURCE REQUIREMENTS:
• High computational cost (typically $0.50-$2.00+ per research session)
• Extended execution time (5-15 minutes for comprehensive analysis)
• Significant API credit consumption
• Large file generation for report storage

USE CASES:
• Academic research requiring comprehensive literature review
• Market analysis with deep competitive intelligence
• Due diligence and investigative research
• Strategic planning with exhaustive background research
• Complex topics requiring expert-level synthesis

OUTPUT:
• Comprehensive research reports saved to files
• Executive summaries for immediate review
• Detailed citations with quality assessments
• Structured analysis with actionable insights

⚠️  REQUIRES HUMAN APPROVAL: Due to high resource usage and cost""",
        prompt=SONAR_DEEP_RESEARCH_PROMPT,
        tools=[
            "sonar_deep_research",
            "write_file",
            "read_file", 
            "edit_file",
            "ls",
            "write_todos"
        ],
        model=get_perplexity_model()  # Use the configured Perplexity sonar-deep-research model
    )
