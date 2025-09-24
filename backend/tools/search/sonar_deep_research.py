"""
Specialized tool for Perplexity's sonar-deep-research model.
This model is designed for exhaustive research with expert-level insights.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Literal
from langchain_core.tools import tool

from .perplexity_client import get_perplexity_client
from src.deepagents.decorators import handle_large_response


@tool
# Remove @handle_large_response - let the subagent handle file writing for better organization
def sonar_deep_research(
    research_query: str,
    reasoning_effort: Literal["low", "medium", "high"] = "high",
    focus_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    search_recency_filter: Optional[Literal["day", "week", "month", "year"]] = None,
    search_after_date_filter: Optional[str] = None,
    search_before_date_filter: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: float = 0.1,
    async_mode: bool = True
) -> Dict[str, Any]:
    """
    Conduct exhaustive research using Perplexity's sonar-deep-research model.
    
    This specialized model is designed for:
    - Exhaustive research across hundreds of sources
    - Expert-level subject analysis with 128K context length
    - Comprehensive report generation with detailed citations
    - Academic research and market analysis
    - Due diligence and investigative research
    
    Features:
    - Searches hundreds of sources automatically
    - Generates detailed reports (often 10,000+ words)
    - Provides comprehensive citations with quality scores
    - Expert-level analysis and synthesis
    - Handles complex, multi-faceted research questions
    
    Args:
        research_query: The comprehensive research question or topic to investigate
        reasoning_effort: Computational effort - "high" for most thorough analysis
        focus_domains: List of domains to prioritize (e.g., ["nature.com", "science.org"])
        exclude_domains: List of domains to exclude from research
        search_recency_filter: Filter by time period for recent information
        search_after_date_filter: Only include results after this date (format: "m/d/yyyy")
        search_before_date_filter: Only include results before this date (format: "m/d/yyyy")
        max_tokens: Maximum tokens in response (default: model maximum)
        temperature: Response creativity (0.0-1.0, default: 0.1 for analytical tasks)
        async_mode: Use async API for long-running research (recommended for complex queries)
    
    Returns:
        Comprehensive research report with:
        - Executive summary
        - Detailed analysis sections
        - Comprehensive citations with URLs
        - Source quality assessments
        - Key findings and recommendations
        
    Note: This tool returns comprehensive research data that should be processed
    and organized by the calling subagent. Reports are typically 10,000+ words.
    """
    
    client = get_perplexity_client()
    
    # Construct domain filters if provided
    search_domain_filter = []
    if focus_domains:
        search_domain_filter.extend(focus_domains)
    if exclude_domains:
        search_domain_filter.extend([f"-{domain}" for domain in exclude_domains])
    
    # Enhanced system prompt for sonar-deep-research
    system_prompt = f"""You are an expert research analyst conducting exhaustive, comprehensive research using the sonar-deep-research model. Your task is to produce a detailed, authoritative research report that demonstrates the full capabilities of this advanced model.

RESEARCH SCOPE: {research_query}

RESEARCH METHODOLOGY:
1. Conduct exhaustive searches across hundreds of authoritative sources
2. Analyze information with expert-level depth and insight
3. Synthesize findings into a comprehensive, structured report
4. Provide detailed citations with quality assessments
5. Include multiple perspectives and cross-validate information

REPORT STRUCTURE:
1. EXECUTIVE SUMMARY (500-750 words)
   - Key findings overview
   - Main conclusions and implications
   - Critical insights discovered

2. COMPREHENSIVE ANALYSIS (8,000-15,000 words)
   - Detailed examination of all aspects
   - Multiple sections covering different dimensions
   - In-depth analysis with supporting evidence
   - Cross-references between sources
   - Identification of patterns and trends

3. METHODOLOGY & SOURCES (1,000-2,000 words)
   - Research approach explanation
   - Source selection criteria
   - Quality assessment of sources
   - Limitations and potential biases

4. KEY FINDINGS & RECOMMENDATIONS (1,000-1,500 words)
   - Prioritized list of discoveries
   - Actionable recommendations
   - Future research directions
   - Strategic implications

5. COMPREHENSIVE CITATIONS
   - Full bibliography with URLs
   - Source quality scores and assessments
   - Publication dates and relevance notes
   - Access status and reliability indicators

QUALITY STANDARDS:
- Use authoritative, peer-reviewed, and official sources
- Cross-validate information across multiple sources
- Highlight conflicting information and uncertainty
- Provide context for time-sensitive information
- Maintain objectivity while acknowledging different perspectives
- Ensure all claims are properly cited

DEPTH REQUIREMENTS:
- Minimum 10,000 words for comprehensive coverage
- Multiple sub-topics and dimensions explored
- Expert-level analysis demonstrating deep understanding
- Synthesis of complex information into coherent insights
- Strategic and practical implications discussed

Generate a comprehensive, authoritative research report that showcases the full analytical power of the sonar-deep-research model."""

    # Prepare the request
    request_data = {
        "model": "sonar-deep-research",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": research_query}
        ],
        "reasoning_effort": reasoning_effort,
        "temperature": temperature,
        "enable_search_classifier": True,
        "disable_search": False
    }
    
    # Add optional parameters
    if search_domain_filter:
        request_data["search_domain_filter"] = search_domain_filter
    if search_recency_filter:
        request_data["search_recency_filter"] = search_recency_filter
    if search_after_date_filter:
        request_data["search_after_date_filter"] = search_after_date_filter
    if search_before_date_filter:
        request_data["search_before_date_filter"] = search_before_date_filter
    if max_tokens:
        request_data["max_tokens"] = max_tokens
    
    try:
        if async_mode:
            # Use async API for long-running research
            response = client.async_chat_completion(request_data)
            
            # Poll for completion
            request_id = response.get("id")
            if request_id:
                # Wait for completion with status updates
                final_response = client.poll_async_completion(request_id)
                if final_response and final_response.get("status") == "COMPLETED":
                    response = final_response.get("response", {})
                else:
                    return {
                        "error": "Async research request failed or timed out",
                        "request_id": request_id,
                        "status": final_response.get("status") if final_response else "unknown"
                    }
        else:
            # Use synchronous API
            response = client.chat_completion(request_data)
        
        # Extract the comprehensive research report
        if "choices" in response and response["choices"]:
            content = response["choices"][0]["message"]["content"]
            
            # Extract citations if available
            citations = response.get("citations", [])
            search_results = response.get("search_results", [])
            usage = response.get("usage", {})
            
            # Format comprehensive response
            result = {
                "research_report": content,
                "citations": citations,
                "search_results": search_results,
                "usage_statistics": {
                    "total_tokens": usage.get("total_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "citation_tokens": usage.get("citation_tokens", 0),
                    "reasoning_tokens": usage.get("reasoning_tokens", 0),
                    "search_queries": usage.get("num_search_queries", 0),
                    "estimated_cost": usage.get("cost", {}).get("total_cost", 0)
                },
                "research_metadata": {
                    "model": "sonar-deep-research",
                    "reasoning_effort": reasoning_effort,
                    "search_filters_applied": {
                        "domains": search_domain_filter,
                        "recency": search_recency_filter,
                        "date_range": {
                            "after": search_after_date_filter,
                            "before": search_before_date_filter
                        }
                    },
                    "async_mode": async_mode,
                    "report_length_words": len(content.split()) if content else 0,
                    "sources_analyzed": len(search_results)
                }
            }
            
            # Add formatted citations section to the report
            if citations:
                citations_section = "\n\n## COMPREHENSIVE CITATIONS\n\n"
                for i, citation in enumerate(citations, 1):
                    citations_section += f"{i}. {citation}\n"
                
                result["research_report"] += citations_section
            
            return result
            
        else:
            return {
                "error": "No response content received from sonar-deep-research model",
                "raw_response": response
            }
            
    except Exception as e:
        return {
            "error": f"Error during deep research: {str(e)}",
            "research_query": research_query,
            "model": "sonar-deep-research"
        }
