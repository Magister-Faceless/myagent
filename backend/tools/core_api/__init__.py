"""
CORE API Tools for Scientific Research

This package provides tools for interacting with the CORE API v3
to support scientific research workflows including literature reviews,
meta-analyses, and research trend analysis.
"""

from .search_tools import search_works, scroll_export_works
from .retrieval_tools import get_work_by_id, batch_get_works_by_ids
from .aggregation_tools import aggregate_works, time_trend_analysis
from .journal_tools import search_journals, get_journal_by_id, analyze_top_venues_for_topic
from .utils import validate_doi, format_authors, handle_api_error

__all__ = [
    # Search tools
    "search_works",
    "scroll_export_works",
    
    # Retrieval tools
    "get_work_by_id", 
    "batch_get_works_by_ids",
    
    # Aggregation tools
    "aggregate_works",
    "time_trend_analysis",
    
    # Journal tools
    "search_journals",
    "get_journal_by_id",
    "analyze_top_venues_for_topic",
    
    # Utilities
    "validate_doi",
    "format_authors", 
    "handle_api_error"
]
