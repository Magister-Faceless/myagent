import os
from typing import Literal, Optional, List
from tavily import TavilyClient
from langchain_core.tools import tool

# Initialize Tavily client
tavily_client = None

def get_tavily_client():
    global tavily_client
    if tavily_client is None:
        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY environment variable is required")
        tavily_client = TavilyClient(api_key=api_key)
    return tavily_client

@tool
def tavily_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    include_answer: bool = True,
    include_images: bool = False,
    search_depth: Literal["basic", "advanced"] = "basic"
) -> dict:
    """
    Perform a comprehensive web search using Tavily API.
    
    Args:
        query: The search query string
        max_results: Maximum number of search results to return (default: 5)
        topic: Search topic category - "general", "news", or "finance" (default: "general")
        include_raw_content: Whether to include full raw content of pages (default: False)
        include_domains: List of domains to include in search (allowlist)
        exclude_domains: List of domains to exclude from search (denylist)
        include_answer: Whether to include a direct answer summary (default: True)
        include_images: Whether to include images in results (default: False)
        search_depth: Search depth - "basic" for quick results, "advanced" for comprehensive (default: "basic")
    
    Returns:
        Dictionary containing search results with URLs, titles, content, and optional answer
    """
    try:
        # Prepare search parameters
        search_params = {
            "query": query,
            "max_results": max_results,
            "topic": topic,
            "include_raw_content": include_raw_content,
            "include_answer": include_answer,
            "include_images": include_images,
            "search_depth": search_depth
        }
        
        # Add domain filtering if specified
        if include_domains:
            search_params["include_domains"] = include_domains
        if exclude_domains:
            search_params["exclude_domains"] = exclude_domains
        
        # Perform the search
        client = get_tavily_client()
        results = client.search(**search_params)
        
        # Extract references from Tavily results
        references = []
        for result in results.get("results", []):
            references.append({
                "url": result.get("url", ""),
                "title": result.get("title", "Untitled"),
                "score": result.get("score", 0.0),
                "published_date": result.get("published_date", None)
            })
        
        return {
            "status": "success",
            "query": query,
            "results": results.get("results", []),
            "answer": results.get("answer", ""),
            "images": results.get("images", []) if include_images else [],
            "references": references,
            "search_metadata": {
                "max_results": max_results,
                "topic": topic,
                "search_depth": search_depth,
                "total_results": len(results.get("results", []))
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "query": query,
            "results": [],
            "answer": "",
            "images": [],
            "references": []
        }

@tool
def tavily_qna_search(
    query: str,
    search_depth: Literal["basic", "advanced"] = "advanced"
) -> dict:
    """
    Get a direct answer to a question using Tavily's Q&A search.
    
    Args:
        query: The question to get an answer for
        search_depth: Search depth - "basic" for quick answer, "advanced" for comprehensive (default: "advanced")
    
    Returns:
        Dictionary containing the answer and supporting information
    """
    try:
        # Use Tavily's Q&A search for direct answers
        client = get_tavily_client()
        answer = client.qna_search(
            query=query,
            search_depth=search_depth
        )
        
        return {
            "status": "success",
            "query": query,
            "answer": answer,
            "search_depth": search_depth
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "query": query,
            "answer": "",
            "references": []
        }
