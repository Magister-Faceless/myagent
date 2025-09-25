"""
CORE API Research Subagents

Specialized subagents for scientific research workflows using CORE API tools.
Each subagent is designed for a specific research task with optimized prompts.
"""

from src.deepagents.sub_agent import SubAgent
from config.prompts import (
    LITERATURE_SCREENER_PROMPT,
    TREND_ANALYZER_PROMPT,
    FULL_TEXT_ANALYZER_PROMPT,
    SYSTEMATIC_REVIEW_HELPER_PROMPT,
    META_ANALYSIS_COLLECTOR_PROMPT,
    VENUE_ANALYZER_PROMPT,
    RESEARCH_GAP_IDENTIFIER_PROMPT,
    CITATION_NETWORK_MAPPER_PROMPT
)

def create_literature_screener() -> SubAgent:
    """
    Create Literature Screener subagent for systematic literature search and screening
    
    Tools: search_works, scroll_export_works
    Purpose: Systematic literature search and initial screening for reviews/meta-analyses
    """
    return {
        "name": "literature_screener",
        "description": "Systematic literature search and screening for reviews and meta-analyses",
        "prompt": LITERATURE_SCREENER_PROMPT,
        # "tools": []  # Inherit tools from parent agent
    }

def create_trend_analyzer() -> SubAgent:
    """
    Create Trend Analyzer subagent for research trend analysis
    
    Tools: aggregate_works, time_trend_analysis
    Purpose: Analyze research trends and publication patterns over time
    """
    return {
        "name": "trend_analyzer",
        "description": "Research trend analysis and bibliometric insights",
        "prompt": TREND_ANALYZER_PROMPT,
        # "tools": []
    }

def create_full_text_analyzer() -> SubAgent:
    """
    Create Full Text Analyzer subagent for deep paper analysis
    
    Tools: get_work_by_id, search_works (for filtering)
    Purpose: Deep analysis of full-text research papers
    """
    return {
        "name": "full_text_analyzer",
        "description": "Deep analysis of full-text research papers with structured extraction",
        "prompt": FULL_TEXT_ANALYZER_PROMPT,
        # "tools": []
    }

def create_systematic_review_helper() -> SubAgent:
    """
    Create Systematic Review Helper subagent for PRISMA-compliant reviews
    
    Tools: search_works, scroll_export_works, aggregate_works
    Purpose: PRISMA-compliant systematic review support
    """
    return {
        "name": "systematic_review_helper",
        "description": "PRISMA-compliant systematic review methodology and execution",
        "prompt": SYSTEMATIC_REVIEW_HELPER_PROMPT,
        # "tools": []
    }

def create_meta_analysis_collector() -> SubAgent:
    """
    Create Meta-Analysis Collector subagent for data extraction
    
    Tools: batch_get_works_by_ids, get_work_by_id
    Purpose: Data extraction and preparation for meta-analysis
    """
    return {
        "name": "meta_analysis_collector",
        "description": "Data extraction and preparation for meta-analysis",
        "prompt": META_ANALYSIS_COLLECTOR_PROMPT,
        # "tools": []
    }

def create_venue_analyzer() -> SubAgent:
    """
    Create Venue Analyzer subagent for publication strategy
    
    Tools: search_journals, analyze_top_venues_for_topic
    Purpose: Journal and venue analysis for publication strategy
    """
    return {
        "name": "venue_analyzer",
        "description": "Journal and venue analysis for optimal publication strategy",
        "prompt": VENUE_ANALYZER_PROMPT,
        # "tools": []
    }

def create_research_gap_identifier() -> SubAgent:
    """
    Create Research Gap Identifier subagent for opportunity analysis
    
    Tools: aggregate_works, search_works
    Purpose: Identify underexplored research areas and opportunities
    """
    return {
        "name": "research_gap_identifier",
        "description": "Identification of underexplored research areas and opportunities",
        "prompt": RESEARCH_GAP_IDENTIFIER_PROMPT,
        # "tools": []
    }

def create_citation_network_mapper() -> SubAgent:
    """
    Create Citation Network Mapper subagent for influence analysis
    
    Tools: search_works, aggregate_works
    Purpose: Map citation networks and identify influential works/authors
    """
    return {
        "name": "citation_network_mapper",
        "description": "Citation network analysis and research influence mapping",
        "prompt": CITATION_NETWORK_MAPPER_PROMPT,
        # "tools": []
    }

# Registry of all CORE research subagents
CORE_RESEARCH_SUBAGENTS = {
    "literature_screener": create_literature_screener,
    "trend_analyzer": create_trend_analyzer,
    "full_text_analyzer": create_full_text_analyzer,
    "systematic_review_helper": create_systematic_review_helper,
    "meta_analysis_collector": create_meta_analysis_collector,
    "venue_analyzer": create_venue_analyzer,
    "research_gap_identifier": create_research_gap_identifier,
    "citation_network_mapper": create_citation_network_mapper
}

def get_all_core_research_subagents() -> list[SubAgent]:
    """
    Get all CORE research subagents for registration with main agent
    
    Returns:
        list: List of all CORE research subagents
    """
    return [creator() for creator in CORE_RESEARCH_SUBAGENTS.values()]
