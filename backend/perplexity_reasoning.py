import os
import requests
from typing import Literal, Optional, List, Dict, Any
from langchain_core.tools import tool
from datetime import datetime

# Perplexity API configuration
PERPLEXITY_API_KEY = os.environ["PERPLEXITY_API_KEY"]
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

@tool
def perplexity_reasoning_search(
    query: str,
    model: Literal["sonar", "sonar-pro", "sonar-reasoning", "sonar-reasoning-pro"] = "sonar-reasoning-pro",
    search_domain_filter: Optional[List[str]] = None,
    search_after_date_filter: Optional[str] = None,
    search_before_date_filter: Optional[str] = None,
    last_updated_after_filter: Optional[str] = None,
    last_updated_before_filter: Optional[str] = None,
    search_recency_filter: Optional[Literal["day", "week", "month", "year"]] = None,
    enable_search_classifier: bool = True,
    disable_search: bool = False,
    max_tokens: Optional[int] = None,
    temperature: float = 0.1
) -> Dict[str, Any]:
    """
    Perform advanced reasoning and analysis with real-time web search using Perplexity AI.
    
    This tool specializes in:
    - Multi-step problem solving and analysis
    - Strategic planning and decision making
    - Complex reasoning with current information
    - Detailed research with filtering capabilities
    
    Args:
        query: The question or problem to analyze
        model: Perplexity model to use (default: "sonar-reasoning-pro")
        search_domain_filter: List of domains to include (no prefix) or exclude (- prefix)
        search_after_date_filter: Only include results published after this date (format: "m/d/yyyy")
        search_before_date_filter: Only include results published before this date (format: "m/d/yyyy")
        last_updated_after_filter: Only include results last updated after this date (format: "m/d/yyyy")
        last_updated_before_filter: Only include results last updated before this date (format: "m/d/yyyy")
        search_recency_filter: Filter by time period ("day", "week", "month", "year")
        enable_search_classifier: Let AI decide when to search (default: True)
        disable_search: Disable web search completely (default: False)
        max_tokens: Maximum tokens in response
        temperature: Response creativity (0.0-1.0, default: 0.1 for analytical tasks)
    
    Returns:
        Dictionary containing the analysis, reasoning, and sources
    """
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Construct the reasoning prompt
    system_prompt = """You are an expert analyst and strategic thinker specializing in multi-step problem solving, analysis, planning, and decision making. 

Your approach should be:
1. Break down complex problems into clear, logical steps
2. Analyze each component thoroughly using current information
3. Consider multiple perspectives and potential outcomes
4. Provide structured reasoning and evidence-based conclusions
5. Include actionable insights and recommendations when appropriate

Structure your response with:
- Clear problem analysis
- Step-by-step reasoning process
- Key findings and insights
- Evidence from current sources
- Conclusions and recommendations

Be thorough, analytical, and precise in your reasoning."""
    
    # Build the request payload
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        "temperature": temperature,
        "enable_search_classifier": enable_search_classifier,
        "disable_search": disable_search
    }
    
    # Add optional parameters if provided
    if max_tokens:
        payload["max_tokens"] = max_tokens
    
    # Add search filters if provided
    if search_domain_filter:
        payload["search_domain_filter"] = search_domain_filter
    
    if search_after_date_filter:
        payload["search_after_date_filter"] = search_after_date_filter
    
    if search_before_date_filter:
        payload["search_before_date_filter"] = search_before_date_filter
        
    if last_updated_after_filter:
        payload["last_updated_after_filter"] = last_updated_after_filter
        
    if last_updated_before_filter:
        payload["last_updated_before_filter"] = last_updated_before_filter
    
    if search_recency_filter:
        payload["search_recency_filter"] = search_recency_filter
    
    try:
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract the analysis and citations
        analysis = result["choices"][0]["message"]["content"]
        
        # Parse citations if available (Perplexity includes them in the response)
        citations = []
        if "citations" in result:
            citations = result["citations"]
        
        return {
            "status": "success",
            "query": query,
            "analysis": analysis,
            "citations": citations,
            "model_used": model,
            "search_filters": {
                "domain_filter": search_domain_filter,
                "date_after": search_after_date_filter,
                "date_before": search_before_date_filter,
                "updated_after": last_updated_after_filter,
                "updated_before": last_updated_before_filter,
                "recency": search_recency_filter
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "temperature": temperature,
                "search_enabled": not disable_search
            }
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": f"API request failed: {str(e)}",
            "query": query,
            "analysis": "",
            "citations": []
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "query": query,
            "analysis": "",
            "citations": []
        }

@tool
def perplexity_focused_research(
    topic: str,
    focus_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    time_filter: Optional[Literal["day", "week", "month", "year"]] = "month",
    research_depth: Literal["quick", "comprehensive"] = "comprehensive"
) -> Dict[str, Any]:
    """
    Conduct focused research on a specific topic with domain and time filtering.
    
    Args:
        topic: The research topic or question
        focus_domains: List of trusted domains to focus research on
        exclude_domains: List of domains to exclude from research
        time_filter: How recent the information should be
        research_depth: "quick" for fast overview, "comprehensive" for detailed analysis
    
    Returns:
        Dictionary containing structured research findings
    """
    
    # Determine model and temperature based on research depth
    if research_depth == "comprehensive":
        model = "sonar-reasoning-pro"
        temperature = 0.05  # Very analytical
    else:
        model = "sonar-pro"
        temperature = 0.1
    
    # Build domain filter
    domain_filter = []
    if focus_domains:
        domain_filter.extend(focus_domains)
    if exclude_domains:
        domain_filter.extend([f"-{domain}" for domain in exclude_domains])
    
    research_prompt = f"""Conduct a {research_depth} research analysis on: {topic}

Please provide:
1. Executive Summary
2. Key Findings (with current data and trends)
3. Important Developments (recent changes or updates)
4. Analysis and Implications
5. Sources and References

Focus on factual, current information with proper citations."""
    
    return perplexity_reasoning_search(
        query=research_prompt,
        model=model,
        search_domain_filter=domain_filter if domain_filter else None,
        search_recency_filter=time_filter,
        temperature=temperature
    )
