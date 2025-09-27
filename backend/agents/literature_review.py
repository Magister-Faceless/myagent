"""
Literature Review Agent - DeepAgents v1.1 Implementation

A specialized agent for conducting systematic literature reviews following
the deepagents framework patterns.
"""

from src.deepagents import create_deep_agent

# Import existing research tools
from tools.search.core_api import (
    search_works,
    scroll_export_works,
    get_work_by_id,
    aggregate_works,
    time_trend_analysis,
    search_journals,
    get_journal_by_id,
    analyze_top_venues_for_topic
)

# Import literature review tools
from tools.literature.extract_paper_metadata import extract_paper_metadata
from tools.literature.generate_prisma_diagram import generate_prisma_diagram
from tools.literature.export_citations import export_citations
from tools.literature.quality_assessment import quality_assessment

# Import subagent creators
from subagents.literature_screener import create_literature_screener
from subagents.data_extractor import create_data_extractor
from subagents.synthesis_engine import create_synthesis_engine

# Import utility tools
from tools.subagent_tracker import get_active_subagents, get_subagent_summary

# Import configuration
from config.prompts import LITERATURE_REVIEW_AGENT_PROMPT
from config.settings import get_settings
from models import get_default_model
from config.checkpointer import get_default_checkpointer


def create_literature_review_agent():
    """Create and configure the literature review specialized deep agent."""
    # Get application settings
    settings = get_settings()
    
    # Create literature review subagents
    literature_screener = create_literature_screener()
    data_extractor = create_data_extractor()
    synthesis_engine = create_synthesis_engine()
    
    # Get the default model with fallback
    model = get_default_model()
    
    # Get persistent checkpointer for state storage
    checkpointer = get_default_checkpointer()
    
    # Create the literature review deep agent
    agent = create_deep_agent(
        tools=[
            # CORE API tools for scientific research
            search_works,
            scroll_export_works,
            get_work_by_id,
            aggregate_works,
            time_trend_analysis,
            search_journals,
            get_journal_by_id,
            analyze_top_venues_for_topic,
            
            # Literature review specific tools
            extract_paper_metadata,
            generate_prisma_diagram,
            export_citations,
            quality_assessment,
            
            # Utility tools for task and subagent management
            get_active_subagents,
            get_subagent_summary,
        ],
        subagents=[
            literature_screener,
            data_extractor,
            synthesis_engine,
        ],
        instructions=LITERATURE_REVIEW_AGENT_PROMPT,
        model=model,
        checkpointer=checkpointer,
        recursion_limit=settings.recursion_limit,
    )
    
    return agent


# Create the agent instance for LangGraph
agent = create_literature_review_agent()
