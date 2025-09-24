# CORE API Implementation Plan for DeepAgents

## Overview
This document outlines the implementation plan for CORE API tools and subagents optimized for the deepagents framework, focusing on scientific research workflows.

## Phase 1: Core Tool Implementation (Priority 1)

### Essential Tools (Implement First)
1. **SearchWorks** - Foundation for all search operations
2. **GetWorkById** - Individual paper retrieval with @handle_large_response
3. **AggregateWorks** - Statistical analysis and trend identification
4. **ScrollExportWorks** - Large dataset handling with @handle_large_response

### Implementation Structure
```
backend/tools/core_api/
├── __init__.py
├── search_tools.py          # SearchWorks, ScrollExportWorks
├── retrieval_tools.py       # GetWorkById, BatchGetWorksByIds
├── aggregation_tools.py     # AggregateWorks, TimeTrendAnalysis
├── journal_tools.py         # SearchJournals, GetJournalById
├── utils.py                 # Common utilities, rate limiting
└── config.py               # API keys, endpoints, defaults
```

### Tool Implementation Requirements
- All tools use `@handle_large_response` decorator where specified
- Implement exponential backoff for rate limiting
- Use structured output formats (CSV, JSON, MD)
- Include comprehensive error handling
- Add progress tracking for long operations

## Phase 2: Subagent Implementation (Priority 2)

### Subagent Registration Structure
```python
# backend/subagents/core_research_subagents.py
from deepagents.types import SubAgent

def create_literature_screener() -> SubAgent:
    return {
        "name": "literature_screener",
        "description": "Systematic literature search and screening for reviews",
        "prompt": LITERATURE_SCREENER_PROMPT,
        "tools": ["search_works", "scroll_export_works"]
    }

def create_trend_analyzer() -> SubAgent:
    return {
        "name": "trend_analyzer", 
        "description": "Research trend analysis and bibliometric insights",
        "prompt": TREND_ANALYZER_PROMPT,
        "tools": ["aggregate_works", "time_trend_analysis"]
    }
# ... additional subagent creators
```

### Prompt Storage
```python
# backend/config/prompts.py - Add CORE research prompts
LITERATURE_SCREENER_PROMPT = """
You are an expert literature screener specialized in systematic reviews...
[Full optimized prompt from CORE_subagents.md]
"""

TREND_ANALYZER_PROMPT = """
You are a research trend analyst specializing in bibliometric analysis...
[Full optimized prompt from CORE_subagents.md]
"""
# ... additional prompts
```

## Phase 3: Main Agent Integration (Priority 3)

### Update Main Agent Configuration
```python
# backend/agents/main_agent.py
from subagents.core_research_subagents import (
    create_literature_screener,
    create_trend_analyzer,
    create_full_text_analyzer,
    create_systematic_review_helper,
    create_meta_analysis_collector,
    create_venue_analyzer,
    create_research_gap_identifier,
    create_citation_network_mapper
)

from tools.core_api import (
    search_works,
    get_work_by_id,
    aggregate_works,
    scroll_export_works,
    # ... other tools
)

def create_main_agent():
    return create_deep_agent(
        tools=[
            # Existing tools...
            search_works,
            get_work_by_id,
            aggregate_works,
            scroll_export_works,
            # ... other CORE tools
        ],
        instructions=MAIN_AGENT_INSTRUCTIONS,
        subagents=[
            create_literature_screener(),
            create_trend_analyzer(),
            create_full_text_analyzer(),
            create_systematic_review_helper(),
            create_meta_analysis_collector(),
            create_venue_analyzer(),
            create_research_gap_identifier(),
            create_citation_network_mapper(),
        ]
    )
```

## Phase 4: Environment Configuration

### Required Environment Variables
```bash
# backend/.env
CORE_API_KEY=your_core_api_key_here
CORE_API_BASE_URL=https://api.core.ac.uk/v3
CORE_API_RATE_LIMIT=100  # requests per minute
CORE_API_TIMEOUT=30      # seconds
```

### Settings Configuration
```python
# backend/config/settings.py
import os

CORE_API_CONFIG = {
    "api_key": os.getenv("CORE_API_KEY"),
    "base_url": os.getenv("CORE_API_BASE_URL", "https://api.core.ac.uk/v3"),
    "rate_limit": int(os.getenv("CORE_API_RATE_LIMIT", "100")),
    "timeout": int(os.getenv("CORE_API_TIMEOUT", "30")),
    "max_retries": 3,
    "backoff_factor": 2
}
```

## Implementation Details

### Large Response Handling Implementation
```python
# Example tool with @handle_large_response
from deepagents.decorators import handle_large_response
from deepagents.tools import tool

@tool(description="Search CORE API for academic works")
@handle_large_response(max_length=50000)
async def scroll_export_works(
    query: str,
    limit: int = 1000,
    include_full_text: bool = False
) -> dict:
    """
    Performs comprehensive search and exports results to files.
    
    Args:
        query: CORE API query string
        limit: Maximum number of results
        include_full_text: Whether to include full text in results
        
    Returns:
        dict: Summary with file paths and statistics
        
    Note: Large result sets automatically saved to CSV files
    """
    # Implementation handles pagination, rate limiting, file output
    pass
```

### Error Handling Pattern
```python
import asyncio
from typing import Optional, Dict, Any

async def core_api_request(
    endpoint: str, 
    params: Optional[Dict[str, Any]] = None,
    retries: int = 3
) -> Dict[str, Any]:
    """Standard CORE API request with error handling"""
    for attempt in range(retries):
        try:
            # Make API request
            response = await make_request(endpoint, params)
            return response
        except RateLimitError:
            wait_time = (2 ** attempt) * 60  # Exponential backoff
            await asyncio.sleep(wait_time)
        except APIError as e:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(5)
    
    raise Exception(f"Failed after {retries} attempts")
```

## Testing Strategy

### Unit Tests
```python
# tests/test_core_tools.py
import pytest
from tools.core_api.search_tools import search_works

@pytest.mark.asyncio
async def test_search_works_basic():
    result = await search_works("machine learning", limit=10)
    assert "results" in result
    assert len(result["results"]) <= 10

@pytest.mark.asyncio  
async def test_search_works_large_response():
    # Test @handle_large_response decorator
    result = await search_works("covid", limit=5000)
    assert "file_path" in result  # Should return file path, not data
```

### Integration Tests
```python
# tests/test_subagents.py
import pytest
from agents.main_agent import create_main_agent

@pytest.mark.asyncio
async def test_literature_screener_subagent():
    agent = create_main_agent()
    result = await agent.run("Please screen literature on 'systematic reviews'")
    # Verify subagent was spawned and files were created
```

## Deployment Checklist

### Pre-deployment
- [ ] All tools implement @handle_large_response where specified
- [ ] Rate limiting and error handling tested
- [ ] Environment variables configured
- [ ] Subagent prompts optimized and tested
- [ ] File output formats validated
- [ ] API key permissions verified

### Post-deployment Monitoring
- [ ] API usage tracking
- [ ] File storage monitoring
- [ ] Error rate monitoring
- [ ] Performance metrics collection
- [ ] User feedback collection

## Usage Examples

### Literature Review Workflow
```python
# User request: "Conduct a systematic review on machine learning in healthcare"
# Main agent spawns: LiteratureScreener -> SystematicReviewHelper -> MetaAnalysisCollector

# 1. Literature screening
screener_result = await task("literature_screener", {
    "query": "machine learning AND healthcare",
    "include_full_text": True,
    "date_range": "2020-2024"
})

# 2. Systematic review protocol
review_result = await task("systematic_review_helper", {
    "research_question": "Effectiveness of ML in healthcare diagnostics",
    "study_types": ["RCT", "cohort", "case-control"]
})

# 3. Data extraction for meta-analysis
meta_result = await task("meta_analysis_collector", {
    "study_ids": review_result["included_studies"],
    "outcomes": ["sensitivity", "specificity", "accuracy"]
})
```

### Research Gap Analysis
```python
# User request: "Identify research gaps in quantum computing applications"
gap_result = await task("research_gap_identifier", {
    "field": "quantum computing applications",
    "comparison_fields": ["classical computing", "machine learning"],
    "time_window": "2015-2024"
})
```

## Success Metrics

### Technical Metrics
- API response time < 5 seconds (95th percentile)
- Error rate < 1%
- File processing success rate > 99%
- Rate limit compliance 100%

### Research Workflow Metrics
- Literature screening time reduction: 80%
- Systematic review protocol generation: 90% automation
- Meta-analysis data extraction accuracy: 95%
- Research gap identification comprehensiveness: 85%

## Future Enhancements

### Phase 5: Advanced Features
- Real-time literature monitoring
- Automated citation network updates
- Integration with reference managers
- Collaborative research workflows
- Advanced visualization tools

### Phase 6: AI Enhancement
- Semantic search improvements
- Automated quality assessment
- Predictive trend analysis
- Personalized research recommendations
- Cross-domain knowledge discovery
