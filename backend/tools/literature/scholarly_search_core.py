"""
Enhanced Scholarly Search Tool - CORE API Integration

Leverages existing CORE API tools for comprehensive academic paper discovery
with enhanced filtering and search strategy capabilities.
"""

from langchain_core.tools import tool
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

# Import existing CORE API tools
from tools.core_api import search_works, aggregate_works


@tool
def enhanced_scholarly_search(
    query: str,
    filters: Dict[str, Any] = None,
    limit: int = 100,
    search_strategy: str = "comprehensive"
) -> Dict[str, Any]:
    """
    Enhanced scholarly search using CORE API with advanced filtering.
    
    Args:
        query: Search query string
        filters: Additional filters (year_range, field_of_study, etc.)
        limit: Maximum number of results
        search_strategy: Search approach (comprehensive, focused, recent)
        
    Returns:
        Dictionary with search results and metadata
    """
    try:
        if filters is None:
            filters = {}
        
        # Enhance query based on search strategy
        enhanced_query = _enhance_query_by_strategy(query, search_strategy)
        
        # Apply temporal filters if specified
        if "year_range" in filters:
            year_filter = f"year:[{filters['year_range']['start']} TO {filters['year_range']['end']}]"
            enhanced_query = f"({enhanced_query}) AND {year_filter}"
        
        # Apply field of study filters
        if "field_of_study" in filters:
            field_filter = f"fieldOfStudy:{filters['field_of_study']}"
            enhanced_query = f"({enhanced_query}) AND {field_filter}"
        
        # Execute search using existing CORE API tool
        search_results = search_works(enhanced_query, limit=limit)
        
        # Enhance results with additional metadata
        enhanced_results = {
            "query": query,
            "enhanced_query": enhanced_query,
            "strategy": search_strategy,
            "filters_applied": filters,
            "total_results": len(search_results.get("results", [])),
            "results": search_results.get("results", []),
            "search_metadata": {
                "timestamp": datetime.now().isoformat(),
                "api_source": "CORE",
                "enhancement_applied": True
            }
        }
        
        return enhanced_results
        
    except Exception as e:
        return {
            "error": f"Enhanced search failed: {str(e)}",
            "query": query,
            "results": [],
            "timestamp": datetime.now().isoformat()
        }


@tool
def multi_strategy_search(
    base_query: str,
    strategies: List[str] = None,
    combine_results: bool = True
) -> Dict[str, Any]:
    """
    Execute multiple search strategies and optionally combine results.
    
    Args:
        base_query: Base search query
        strategies: List of strategies to apply
        combine_results: Whether to merge results from all strategies
        
    Returns:
        Dictionary with results from each strategy
    """
    try:
        if strategies is None:
            strategies = ["comprehensive", "focused", "recent"]
        
        strategy_results = {}
        all_results = []
        
        for strategy in strategies:
            result = enhanced_scholarly_search(
                query=base_query,
                search_strategy=strategy,
                limit=50
            )
            
            strategy_results[strategy] = result
            
            if combine_results and "results" in result:
                all_results.extend(result["results"])
        
        # Remove duplicates if combining results
        if combine_results:
            seen_ids = set()
            unique_results = []
            for paper in all_results:
                paper_id = paper.get("id", paper.get("title", ""))
                if paper_id not in seen_ids:
                    seen_ids.add(paper_id)
                    unique_results.append(paper)
            
            return {
                "base_query": base_query,
                "strategies_used": strategies,
                "individual_results": strategy_results,
                "combined_results": unique_results,
                "total_unique_papers": len(unique_results),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "base_query": base_query,
                "strategies_used": strategies,
                "results_by_strategy": strategy_results,
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        return {
            "error": f"Multi-strategy search failed: {str(e)}",
            "base_query": base_query,
            "timestamp": datetime.now().isoformat()
        }


@tool
def search_trend_analysis(
    topic: str,
    year_range: Dict[str, int] = None,
    interval: str = "yearly"
) -> Dict[str, Any]:
    """
    Analyze publication trends for a topic over time using CORE API.
    
    Args:
        topic: Research topic to analyze
        year_range: Dictionary with 'start' and 'end' years
        interval: Analysis interval (yearly, bi-yearly)
        
    Returns:
        Dictionary with trend analysis data
    """
    try:
        if year_range is None:
            year_range = {"start": 2019, "end": 2024}
        
        # Use existing aggregate_works tool for trend analysis
        trend_data = aggregate_works(
            query=topic,
            aggregate_by="yearPublished",
            limit=1000
        )
        
        # Process and filter trend data
        processed_trends = []
        if "aggregations" in trend_data:
            for item in trend_data["aggregations"]:
                year = item.get("key")
                count = item.get("doc_count", 0)
                
                if (year and 
                    year_range["start"] <= int(year) <= year_range["end"]):
                    processed_trends.append({
                        "year": int(year),
                        "publication_count": count,
                        "topic": topic
                    })
        
        # Sort by year
        processed_trends.sort(key=lambda x: x["year"])
        
        # Calculate trend metrics
        trend_analysis = {
            "topic": topic,
            "year_range": year_range,
            "trend_data": processed_trends,
            "total_publications": sum(item["publication_count"] for item in processed_trends),
            "peak_year": max(processed_trends, key=lambda x: x["publication_count"]) if processed_trends else None,
            "trend_direction": _calculate_trend_direction(processed_trends),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return trend_analysis
        
    except Exception as e:
        return {
            "error": f"Trend analysis failed: {str(e)}",
            "topic": topic,
            "analysis_timestamp": datetime.now().isoformat()
        }


def _enhance_query_by_strategy(query: str, strategy: str) -> str:
    """Enhance query based on search strategy."""
    
    if strategy == "comprehensive":
        # Broad search with synonyms and related terms
        return f"({query}) OR (title:{query}) OR (abstract:{query})"
    
    elif strategy == "focused":
        # Precise search in title and key fields
        return f"title:({query}) OR (title:{query} AND abstract:{query})"
    
    elif strategy == "recent":
        # Recent publications with relevance boost
        current_year = datetime.now().year
        recent_years = f"year:[{current_year-3} TO {current_year}]"
        return f"({query}) AND {recent_years}"
    
    else:
        # Default: return original query
        return query


def _calculate_trend_direction(trend_data: List[Dict[str, Any]]) -> str:
    """Calculate overall trend direction from publication data."""
    
    if len(trend_data) < 2:
        return "insufficient_data"
    
    # Simple linear trend calculation
    first_half = trend_data[:len(trend_data)//2]
    second_half = trend_data[len(trend_data)//2:]
    
    first_avg = sum(item["publication_count"] for item in first_half) / len(first_half)
    second_avg = sum(item["publication_count"] for item in second_half) / len(second_half)
    
    if second_avg > first_avg * 1.1:
        return "increasing"
    elif second_avg < first_avg * 0.9:
        return "decreasing"
    else:
        return "stable"
