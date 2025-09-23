from typing import Literal, Optional, List, Dict, Any
from langchain_core.tools import tool

from .perplexity_client import get_perplexity_client
from .perplexity_config import get_model_for_task, get_domain_filter_for_strategy

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
        Standardized dictionary with analysis, citations, and metadata
    """
    
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
    
    # Use the centralized client
    client = get_perplexity_client()
    
    return client.search(
        query=query,
        model=model,
        system_prompt=system_prompt,
        task_type="reasoning",
        search_domain_filter=search_domain_filter,
        search_after_date_filter=search_after_date_filter,
        search_before_date_filter=search_before_date_filter,
        last_updated_after_filter=last_updated_after_filter,
        last_updated_before_filter=last_updated_before_filter,
        search_recency_filter=search_recency_filter,
        enable_search_classifier=enable_search_classifier,
        disable_search=disable_search,
        max_tokens=max_tokens,
        temperature=temperature
    )

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
        Standardized dictionary containing structured research findings with citations
    """
    
    # Determine model and temperature based on research depth
    if research_depth == "comprehensive":
        model = "sonar-reasoning-pro"
        temperature = 0.05  # Very analytical
        task_type = "deep_research"
    else:
        model = "sonar-pro"
        temperature = 0.1
        task_type = "general_qa"
    
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
    
    system_prompt = """You are a research specialist focused on comprehensive information gathering and analysis. 

Your approach should be:
1. Gather information from multiple authoritative sources
2. Synthesize findings into clear, structured insights
3. Highlight recent developments and trends
4. Provide balanced analysis with supporting evidence
5. Include proper citations and source references

Structure your research report with clear sections and evidence-based conclusions."""
    
    # Use the centralized client
    client = get_perplexity_client()
    
    return client.search(
        query=research_prompt,
        model=model,
        system_prompt=system_prompt,
        task_type=task_type,
        search_domain_filter=domain_filter if domain_filter else None,
        search_recency_filter=time_filter,
        temperature=temperature
    )
