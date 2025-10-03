"""
Literature Review Agent - DeepAgents v1.1 Implementation

A sophisticated orchestrator for conducting comprehensive, human-in-the-loop systematic 
literature reviews through conversational dialogue and strategic subagent delegation.

Architecture:
- Main agent: Pure orchestrator with ONLY built-in tools
- Subagents: CustomSubAgent graphs with their own specific tools
- Each subagent is independent with its own tool set
- Minimizes main agent's context window usage
"""

from src.deepagents import create_deep_agent
from langgraph.prebuilt import create_react_agent

# Import tools for each specialized subagent
from tools.core_api import (
    search_works,
    scroll_export_works,
    get_work_by_id,
    batch_get_works_by_ids,
    aggregate_works,
    time_trend_analysis,
    search_journals,
    get_journal_by_id,
    analyze_top_venues_for_topic,
)
from tools.literature.extract_paper_metadata import extract_paper_metadata
from tools.literature.generate_prisma_diagram import generate_prisma_diagram
from tools.literature.export_citations import export_citations
from tools.literature.quality_assessment import quality_assessment
from tools.search.tavily_search import tavily_search, tavily_qna_search
from tools.search.perplexity import perplexity_reasoning_search, perplexity_focused_research
from tools.search.sonar_deep_research import sonar_deep_research

# Import configuration
from config.prompts import (
    LITERATURE_REVIEW_AGENT_INSTRUCTIONS,
    GENERAL_SUBAGENT_PROMPT,
    LITERATURE_SCREENER_PROMPT,
    CONTENT_ANALYZER_PROMPT,
    SYNTHESIS_ENGINE_PROMPT,
    WORK_REVIEWER_PROMPT,
    LITERATURE_REVIEW_REVIEWER_PROMPT,
)
from config.settings import get_settings
from models import get_default_model
from config.checkpointer import get_default_checkpointer


def create_literature_review_agent():
    """
    Create literature review orchestrator with CustomSubAgent pattern.
    
    Each subagent is a pre-built graph with its own specific tools,
    minimizing the main agent's tool count and context window usage.
    
    Architecture:
    - Main agent: ONLY built-in tools (write_file, read_file, edit_file, write_todos, ls, task)
    - Subagents: Independent graphs with specific tool sets
    - Human-in-the-loop: Conversational checkpoints
    """
    settings = get_settings()
    model = get_default_model()
    checkpointer = get_default_checkpointer()
    
    # Create CustomSubAgent: General specialist with ALL tools
    general_subagent_graph = create_react_agent(
        model=model,
        tools=[
            # CORE API tools
            search_works, scroll_export_works, get_work_by_id, batch_get_works_by_ids,
            aggregate_works, time_trend_analysis, search_journals, get_journal_by_id,
            analyze_top_venues_for_topic,
            # Literature tools
            extract_paper_metadata, generate_prisma_diagram, export_citations, quality_assessment,
            # Search tools
            tavily_search, tavily_qna_search, perplexity_reasoning_search,
            perplexity_focused_research, sonar_deep_research,
        ],
        prompt=GENERAL_SUBAGENT_PROMPT,
        checkpointer=checkpointer,
    )
    
    # Create CustomSubAgent: Literature screener with screening tools
    literature_screener_graph = create_react_agent(
        model=model,
        tools=[
            search_works, scroll_export_works, get_work_by_id,
            generate_prisma_diagram, extract_paper_metadata,
        ],
        prompt=LITERATURE_SCREENER_PROMPT,
        checkpointer=checkpointer,
    )
    
    # Create CustomSubAgent: Content analyzer with analysis tools
    content_analyzer_graph = create_react_agent(
        model=model,
        tools=[
            get_work_by_id, batch_get_works_by_ids,
            extract_paper_metadata, quality_assessment,
        ],
        prompt=CONTENT_ANALYZER_PROMPT,
        checkpointer=checkpointer,
    )
    
    # Create CustomSubAgent: Synthesis engine with synthesis tools
    synthesis_engine_graph = create_react_agent(
        model=model,
        tools=[
            sonar_deep_research, export_citations,
            perplexity_focused_research,
        ],
        prompt=SYNTHESIS_ENGINE_PROMPT,
        checkpointer=checkpointer,
    )
    
    # Create CustomSubAgent: Work reviewer (no external tools needed)
    work_reviewer_graph = create_react_agent(
        model=model,
        tools=[],  # Only uses built-in tools (ls, read_file)
        prompt=WORK_REVIEWER_PROMPT,
        checkpointer=checkpointer,
    )
    
    # Create CustomSubAgent: Literature review citation reviewer (no external tools needed)
    literature_review_reviewer_graph = create_react_agent(
        model=model,
        tools=[],  # Only uses built-in tools (ls, read_file)
        prompt=LITERATURE_REVIEW_REVIEWER_PROMPT,
        checkpointer=checkpointer,
    )
    
    # Create main agent with ONLY built-in tools
    agent = create_deep_agent(
        tools=[],  # NO external tools - only built-in tools (write_file, read_file, etc.)
        subagents=[
            # CustomSubAgent pattern: each is an independent graph
            {
                "name": "specialist-agent",
                "description": "General-purpose specialist with access to ALL tools. Use for any task requiring searches, retrievals, analyses, or specialized operations.",
                "graph": general_subagent_graph,
            },
            {
                "name": "literature_screener",
                "description": "Specialized in screening papers based on inclusion/exclusion criteria. Returns screening results.",
                "graph": literature_screener_graph,
            },
            {
                "name": "content_analyzer",
                "description": "Specialized in analyzing papers and extracting key information. Returns structured analysis.",
                "graph": content_analyzer_graph,
            },
            {
                "name": "synthesis_engine",
                "description": "Specialized in synthesizing findings across multiple papers. Returns comprehensive literature review.",
                "graph": synthesis_engine_graph,
            },
            {
                "name": "work_reviewer",
                "description": "Quality assurance specialist. Reviews all deliverables for completeness and quality.",
                "graph": work_reviewer_graph,
            },
            {
                "name": "literature_review_reviewer",
                "description": "Citation verification specialist. Verifies all [N] citations in literature_review.md match the References section and cross-references with literature_analysis.md.",
                "graph": literature_review_reviewer_graph,
            },
        ],
        instructions=LITERATURE_REVIEW_AGENT_INSTRUCTIONS,
        model=model,
        checkpointer=checkpointer,
    ).with_config({"recursion_limit": settings["recursion_limit"]})
    
    return agent


# Create the agent instance for LangGraph
agent = create_literature_review_agent()
