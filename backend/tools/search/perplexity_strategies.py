"""
Specialized search strategies for different research domains using Perplexity AI.
"""

from typing import Dict, List, Any, Optional, Literal
from langchain_core.tools import tool

from .perplexity_client import get_perplexity_client
from .perplexity_config import get_domain_filter_for_strategy, get_model_for_task


@tool
def academic_search(
    query: str,
    research_depth: Literal["quick", "comprehensive"] = "comprehensive",
    time_filter: Optional[Literal["day", "week", "month", "year"]] = "year",
    include_preprints: bool = True
) -> Dict[str, Any]:
    """
    Conduct academic and scientific research with focus on peer-reviewed sources.
    
    Args:
        query: The academic research question or topic
        research_depth: "quick" for overview, "comprehensive" for detailed analysis
        time_filter: How recent the research should be
        include_preprints: Whether to include preprint servers like arXiv
        
    Returns:
        Standardized research results with academic citations
    """
    
    # Configure for academic research
    model = "sonar-deep-research" if research_depth == "comprehensive" else "sonar-reasoning-pro"
    
    # Get academic domain filters
    domain_filter = get_domain_filter_for_strategy("academic")
    
    # Add preprint servers if requested
    if include_preprints:
        domain_filter.extend(["arxiv.org", "biorxiv.org", "medrxiv.org", "psyarxiv.com"])
    
    system_prompt = """You are an academic research specialist with expertise in scientific literature review and analysis.

Your approach:
1. Focus on peer-reviewed sources and authoritative academic publications
2. Synthesize findings from multiple studies and sources
3. Identify research gaps and conflicting findings
4. Provide proper academic citations and source quality assessment
5. Distinguish between established findings and emerging research

Structure your response with:
- Literature overview and key findings
- Methodological considerations
- Current consensus and debates
- Research implications and future directions
- Comprehensive source citations with quality indicators"""
    
    client = get_perplexity_client()
    
    return client.search(
        query=f"Academic research on: {query}",
        model=model,
        system_prompt=system_prompt,
        task_type="academic_research",
        search_domain_filter=domain_filter,
        search_recency_filter=time_filter,
        temperature=0.05  # Very analytical for academic work
    )


@tool
def technical_search(
    query: str,
    focus_area: Optional[Literal["documentation", "apis", "frameworks", "tools"]] = None,
    include_examples: bool = True,
    time_filter: Optional[Literal["day", "week", "month", "year"]] = "month"
) -> Dict[str, Any]:
    """
    Conduct technical research focused on documentation, APIs, and development resources.
    
    Args:
        query: The technical question or topic
        focus_area: Specific technical focus area
        include_examples: Whether to include code examples and implementations
        time_filter: How recent the technical information should be
        
    Returns:
        Standardized technical research results with implementation details
    """
    
    model = "sonar-reasoning-pro"
    
    # Get technical domain filters
    domain_filter = get_domain_filter_for_strategy("technical")
    
    # Enhance query based on focus area
    if focus_area:
        enhanced_query = f"{query} - focus on {focus_area}"
        if focus_area == "documentation":
            enhanced_query += " official documentation and guides"
        elif focus_area == "apis":
            enhanced_query += " API specifications and usage examples"
        elif focus_area == "frameworks":
            enhanced_query += " framework features and best practices"
        elif focus_area == "tools":
            enhanced_query += " tool usage and configuration"
    else:
        enhanced_query = query
    
    system_prompt = """You are a technical research specialist focused on providing accurate, practical technical information.

Your approach:
1. Prioritize official documentation and authoritative technical sources
2. Provide practical, actionable technical insights
3. Include relevant code examples and implementation details
4. Assess technical feasibility, compatibility, and best practices
5. Consider security, performance, and maintainability aspects

Structure your response with:
- Technical overview and key concepts
- Implementation details and examples (if applicable)
- Best practices and recommendations
- Compatibility and requirements
- Troubleshooting and common issues
- Authoritative source citations"""
    
    if include_examples:
        enhanced_query += " with code examples and implementation details"
    
    client = get_perplexity_client()
    
    return client.search(
        query=enhanced_query,
        model=model,
        system_prompt=system_prompt,
        task_type="technical_research",
        search_domain_filter=domain_filter,
        search_recency_filter=time_filter,
        temperature=0.1
    )


@tool
def market_research(
    query: str,
    analysis_type: Optional[Literal["trends", "competitive", "financial", "regulatory"]] = None,
    time_filter: Optional[Literal["day", "week", "month", "year"]] = "month",
    include_forecasts: bool = True
) -> Dict[str, Any]:
    """
    Conduct market research and business intelligence analysis.
    
    Args:
        query: The market research question or topic
        analysis_type: Specific type of market analysis
        time_filter: How recent the market data should be
        include_forecasts: Whether to include market forecasts and predictions
        
    Returns:
        Standardized market research results with business insights
    """
    
    model = "sonar-reasoning-pro"
    
    # Get business/market domain filters
    domain_filter = get_domain_filter_for_strategy("business")
    
    # Enhance query based on analysis type
    if analysis_type:
        enhanced_query = f"{query} - {analysis_type} analysis"
        if analysis_type == "trends":
            enhanced_query += " market trends and patterns"
        elif analysis_type == "competitive":
            enhanced_query += " competitive landscape and positioning"
        elif analysis_type == "financial":
            enhanced_query += " financial performance and metrics"
        elif analysis_type == "regulatory":
            enhanced_query += " regulatory environment and policy impacts"
    else:
        enhanced_query = query
    
    system_prompt = """You are a market research and business intelligence specialist focused on data-driven analysis.

Your approach:
1. Gather current market data from authoritative business sources
2. Analyze trends, patterns, and competitive dynamics
3. Provide quantitative insights with supporting data
4. Consider multiple market perspectives and stakeholder viewpoints
5. Assess risks, opportunities, and strategic implications

Structure your response with:
- Market overview and current conditions
- Key trends and driving factors
- Competitive landscape analysis
- Financial and performance metrics
- Risk assessment and opportunities
- Strategic recommendations
- Data sources and market intelligence citations"""
    
    if include_forecasts:
        enhanced_query += " including market forecasts and future outlook"
    
    client = get_perplexity_client()
    
    return client.search(
        query=enhanced_query,
        model=model,
        system_prompt=system_prompt,
        task_type="market_analysis",
        search_domain_filter=domain_filter,
        search_recency_filter=time_filter,
        temperature=0.1
    )


@tool
def deep_research(
    query: str,
    research_scope: Literal["narrow", "broad", "comprehensive"] = "comprehensive",
    validation_level: Literal["basic", "thorough", "rigorous"] = "thorough",
    max_sources: int = 10
) -> Dict[str, Any]:
    """
    Conduct deep, multi-source research with cross-validation and synthesis.
    
    Args:
        query: The research question or topic
        research_scope: How broad the research should be
        validation_level: Level of source validation and cross-referencing
        max_sources: Maximum number of sources to analyze
        
    Returns:
        Comprehensive research results with validated findings and synthesis
    """
    
    model = "sonar-deep-research"
    
    # Use broad domain allowlist for comprehensive research
    domain_filter = None  # Let the model choose the best sources
    
    # Enhance query based on research scope
    scope_guidance = {
        "narrow": "focused, specific analysis",
        "broad": "comprehensive overview with multiple perspectives", 
        "comprehensive": "exhaustive analysis with deep synthesis"
    }
    
    enhanced_query = f"{query} - conduct {scope_guidance[research_scope]}"
    
    system_prompt = f"""You are a senior research analyst specializing in comprehensive, multi-source research and synthesis.

Your approach for {validation_level} validation:
1. Gather information from multiple authoritative and diverse sources
2. Cross-reference findings across sources for accuracy and consistency
3. Identify areas of consensus and disagreement in the literature
4. Synthesize findings into coherent, well-structured analysis
5. Highlight knowledge gaps and areas requiring further investigation
6. Provide comprehensive source quality assessment

Validation requirements:
- Cross-check facts across at least 3 different sources when possible
- Note source reliability, bias, and limitations
- Distinguish between established facts and emerging claims
- Highlight conflicting information and provide balanced perspective

Structure your response with:
- Executive summary of key findings
- Detailed analysis with source validation
- Areas of consensus and disagreement
- Knowledge gaps and limitations
- Synthesis and implications
- Comprehensive citation list with quality indicators"""
    
    client = get_perplexity_client()
    
    return client.search(
        query=enhanced_query,
        model=model,
        system_prompt=system_prompt,
        task_type="deep_research",
        search_recency_filter="extended",  # Broader time range for comprehensive research
        temperature=0.05,  # Very analytical
        max_tokens=16000  # Allow for comprehensive analysis
    )
