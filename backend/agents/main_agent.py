"""
Main agent implementation using the deep agents framework.

Architecture:
- Main agent: Uses essential tools directly (search, memory tools)
- Subagents: CustomSubAgent graphs with their own specific tools
- Minimizes context window usage while maintaining flexibility
"""

import os
from typing import Literal, Any
from src.deepagents import create_deep_agent
from langgraph.prebuilt import create_react_agent

# Import essential tools for main agent
from tools.search.tavily_search import tavily_search, tavily_qna_search
from tools.search.perplexity import perplexity_reasoning_search, perplexity_focused_research
from tools.search.sonar_deep_research import sonar_deep_research

# Import tools for specialized subagents
from tools.core_api import (
    search_works, scroll_export_works, get_work_by_id, batch_get_works_by_ids,
    aggregate_works, time_trend_analysis, search_journals, get_journal_by_id,
    analyze_top_venues_for_topic,
)
from tools.literature.extract_paper_metadata import extract_paper_metadata
from tools.literature.generate_prisma_diagram import generate_prisma_diagram
from tools.literature.export_citations import export_citations
from tools.literature.quality_assessment import quality_assessment

# Import memory-enhanced tools for file management
from tools.memory_enhanced_tools import (
    enhanced_write_file,
    enhanced_read_file,
    intelligent_file_search,
    get_thread_memory_context,
    get_shared_context_summary,
)

# Import essential utility tools
from tools.subagent_tracker import get_active_subagents, get_subagent_summary

# Import configuration
from config.prompts import (
    MAIN_AGENT_INSTRUCTIONS,
    PLANNING_COORDINATOR_PROMPT,
    GENERAL_SUBAGENT_PROMPT,
    QA_REVIEWER_PROMPT,
)
from config.settings import get_settings
from models import get_default_model
from config.checkpointer import get_default_checkpointer
from utils.subagent_tracking import enable_subagent_tracking


def create_main_agent():
    """Create and configure the lean generalist main agent with CustomSubAgent pattern.
    
    Architecture:
    - Main agent: Essential tools only (search, memory, tracking)
    - Subagents: Independent graphs with specific tool sets
    - Minimizes main agent's context window usage
    """
    settings = get_settings()
    model = get_default_model()
    checkpointer = get_default_checkpointer()
    
    # Create CustomSubAgent: Planning coordinator (no external tools)
    planning_coordinator_graph = create_react_agent(
        model=model,
        tools=[],  # Only uses built-in tools
        prompt=PLANNING_COORDINATOR_PROMPT,
        checkpointer=checkpointer,
    )
    
    # Create CustomSubAgent: General specialist with ALL tools
    general_subagent_graph = create_react_agent(
        model=model,
        tools=[
            # Search tools
            tavily_search, tavily_qna_search, perplexity_reasoning_search,
            perplexity_focused_research, sonar_deep_research,
            # CORE API tools
            search_works, scroll_export_works, get_work_by_id, batch_get_works_by_ids,
            aggregate_works, time_trend_analysis, search_journals, get_journal_by_id,
            analyze_top_venues_for_topic,
            # Literature tools
            extract_paper_metadata, generate_prisma_diagram, export_citations, quality_assessment,
            # Memory tools
            enhanced_write_file, enhanced_read_file, intelligent_file_search,
            get_thread_memory_context, get_shared_context_summary,
        ],
        prompt=GENERAL_SUBAGENT_PROMPT,
        checkpointer=checkpointer,
    )
    
    # Create CustomSubAgent: QA reviewer with memory tools
    qa_reviewer_graph = create_react_agent(
        model=model,
        tools=[
            get_thread_memory_context,
            get_shared_context_summary,
        ],
        prompt=QA_REVIEWER_PROMPT,
        checkpointer=checkpointer,
    )
    
    # Create main agent with essential tools only
    with enable_subagent_tracking():
        agent = create_deep_agent(
            tools=[
                # Essential search tools (main agent uses these directly)
                tavily_search,
                perplexity_reasoning_search,
                
                # Memory-enhanced file management (essential for all tasks)
                enhanced_write_file,
                enhanced_read_file,
                intelligent_file_search,
                get_thread_memory_context,
                get_shared_context_summary,
                
                # Subagent management tools
                get_active_subagents,
                get_subagent_summary,
            ],
            instructions=MAIN_AGENT_INSTRUCTIONS,
            subagents=[
                {
                    "name": "planning_coordinator",
                    "description": "Enhanced planning coordinator for task assessment and specialization planning.",
                    "graph": planning_coordinator_graph,
                },
                {
                    "name": "specialist-agent",
                    "description": "General-purpose specialist with access to ALL tools for flexible task delegation.",
                    "graph": general_subagent_graph,
                },
                {
                    "name": "qa_reviewer",
                    "description": "Quality assurance reviewer for completion verification before final delivery.",
                    "graph": qa_reviewer_graph,
                },
            ],
            model=model,
            checkpointer=checkpointer,
            # Configure human-in-the-loop for specialization decisions
            interrupt_config={
                "task": {  # Interrupt when spawning specialized subagents
                    "allow_ignore": False,
                    "allow_respond": True,
                    "allow_edit": True,
                    "allow_accept": True,
                }
            },
        ).with_config({"recursion_limit": settings["recursion_limit"]})

    return agent


# Create the agent instance for LangGraph
agent = create_main_agent()
