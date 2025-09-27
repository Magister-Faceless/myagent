"""
Literature Review Agent - DeepAgents v1.1 Implementation

A sophisticated agent for conducting comprehensive, human-in-the-loop systematic 
literature reviews. Follows the refined plan with Grok-4-Fast and Perplexity 
Sonar Deep Research model integration.
"""

from src.deepagents import create_deep_agent

# Import existing CORE API research tools
from tools.core_api import (
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

# Import enhanced subagent creators following refined plan
from subagents.request_validator import (
    create_request_validator,
)
from subagents.planning_coordinator import (
    create_planning_coordinator,
)
from subagents.literature_screener import (
    create_literature_screener,
)
from subagents.content_analyzer import (
    create_content_analyzer,
)
from subagents.synthesis_engine import (
    create_synthesis_engine,
)

# Import utility tools
from tools.subagent_tracker import get_active_subagents, get_subagent_summary
from utils.subagent_tracking import enable_subagent_tracking

# Import configuration
from config.prompts import LITERATURE_REVIEW_AGENT_INSTRUCTIONS
from config.settings import get_settings
from models import get_default_model
from config.checkpointer import get_default_checkpointer


def create_literature_review_agent():
    """
    Create and configure the literature review specialized deep agent.
    
    Implements the refined human-in-the-loop workflow with:
    - Grok-4-Fast for most coordination and analysis tasks
    - Perplexity Sonar Deep Research for synthesis
    - CORE API integration for academic paper discovery
    - Comprehensive file management across subagents
    """
    # Get application settings
    settings = get_settings()
    
    # Create literature review subagents following refined plan
    request_validator = create_request_validator()
    planning_coordinator = create_planning_coordinator()
    literature_screener = create_literature_screener()
    content_analyzer = create_content_analyzer()
    synthesis_engine = create_synthesis_engine()
    
    # Get the default model (Grok-4-Fast) for main coordination
    model = get_default_model()
    
    # Get persistent checkpointer for state storage
    checkpointer = get_default_checkpointer()
    
    # Create the literature review deep agent with human-in-the-loop workflow
    with enable_subagent_tracking():
        agent = create_deep_agent(
            tools=[
                # CORE API tools for academic paper discovery and analysis
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

                # Note: Subagent-specific tools are handled via the task tool and subagents
                # Individual tools removed to prevent conflicts with subagent calls

                # Utility tools for task and subagent management
                get_active_subagents,
                get_subagent_summary,
            ],
            subagents=[
                # Human-in-the-loop validation and planning (Grok-4-Fast)
                request_validator,
                planning_coordinator,
                literature_screener,
                content_analyzer,
                
                # Deep research and synthesis (Perplexity Sonar)
                synthesis_engine,
            ],
            instructions=LITERATURE_REVIEW_AGENT_INSTRUCTIONS,
            model=model,
            checkpointer=checkpointer,
            # Human-in-the-loop at Planning Coordinator level as per design document
            interrupt_config={
                "planning_coordinator": {
                    "allow_ignore": False,
                    "allow_respond": True,
                    "allow_edit": True,
                    "allow_accept": True,
                }
            }
        ).with_config({"recursion_limit": settings["recursion_limit"]})
    
    return agent


# Create the agent instance for LangGraph
agent = create_literature_review_agent()
