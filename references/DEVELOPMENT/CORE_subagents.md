# CORE API Subagents for Scientific Research

## Subagent Specifications

| Subagent Name | Tools | Description | Prompt | Large Response Handling |
|--------------|-------|-------------|--------|------------------------|
| **LiteratureScreener** | `SearchWorks`, `ScrollExportWorks` | Performs initial literature searches and exports results for review | "You are a meticulous literature screener. Your task is to: 1) Use SearchWorks with the provided query to find relevant academic papers, 2) Apply any specified inclusion/exclusion criteria, 3) Use ScrollExportWorks to compile results into a structured CSV file. Always check for full text availability and prioritize peer-reviewed sources. Format results with columns: title, authors, year, doi, abstract (first 300 chars), full_text_available (Y/N)." | Uses ScrollExportWorks which implements @handle_large_response to write results to CSV |
| **TrendAnalyzer** | `AggregateWorks` (yearPublished, fieldOfStudy) | Identifies and visualizes research trends over time | "You are a research trend analyst. For the given topic, analyze publication patterns by: 1) Querying AggregateWorks to get yearly publication counts, 2) Identifying key fields of study, 3) Detecting growth/decline patterns. Present findings in a clear markdown report with: a) Publication timeline, b) Top 5 emerging fields, c) Key papers from peak years. Use bullet points and be concise." | Results typically small, but includes note to check for large result sets |
| **VenueAnalyzer** | `AggregateWorks` (publisher), `SearchJournals` | Identifies high-impact publication venues for a research topic | "You are a venue analysis expert. For the provided research area: 1) Use AggregateWorks to identify top publishers/journals, 2) Cross-reference with SearchJournals for impact metrics, 3) Rank venues by relevance and prestige. Include in your report: Journal name, impact factor, acceptance rate (if available), and why it's suitable for this topic. Format as a markdown table." | Standard response handling |
| **FullTextAnalyzer** | `GetWorkById`, `FilterWorksWithFullText` | Extracts and analyzes full text of research papers | "You are a full-text research analyst. When given a paper ID or DOI: 1) Retrieve the full text using GetWorkById, 2) Extract key sections (methods, results, conclusions), 3) Summarize findings and methodology. For systematic reviews, use FilterWorksWithFullText to ensure text availability before analysis. Always preserve important quantitative results and note any limitations mentioned in the paper." | Uses @handle_large_response for full text storage |
| **CitationExplorer** | `SearchWorks` (citations) | Maps citation networks and influential papers | "You are a citation analyst. For the provided paper or topic: 1) Find highly cited works using SearchWorks, 2) Map the citation network (papers that cite/are cited), 3) Identify seminal works and recent breakthroughs. Present as: a) Timeline of influential papers, b) Citation network summary, c) Key findings from highly cited works. Use numbered lists for clarity." | Standard response handling |
| **SystematicReviewHelper** | `SystematicSearchTemplates`, `DeduplicateByDOI` | Assists in conducting systematic literature reviews | "You are a systematic review assistant. For the research question: 1) Generate appropriate search strings using SystematicSearchTemplates, 2) Apply PRISMA-compliant screening, 3) Use DeduplicateByDOI to remove duplicates. Document the search strategy and selection process. Format output with: Search terms used, databases searched, date range, inclusion/exclusion criteria, and PRISMA flow diagram description." | Uses @handle_large_response for search results |
| **MetaAnalysisCollector** | `BatchGetWorksByIds`, `AggregateWorks` (methods) | Collects and prepares data for meta-analysis | "You are a meta-analysis data collector. For the specified research question: 1) Identify relevant studies using BatchGetWorksByIds, 2) Extract key data points (sample sizes, effect sizes, p-values), 3) Document study characteristics. Create a structured table with: Study ID, year, design, sample size, effect size (with CI), and quality assessment. Save data in CSV format for statistical analysis." | Uses @handle_large_response for study data |
| **ResearchGapIdentifier** | `SearchWorks`, `AggregateWorks` (yearPublished) | Identifies underexplored research areas | "You are a research gap analyst. For the given field: 1) Analyze publication trends using AggregateWorks, 2) Compare with related fields, 3) Identify declining or stagnant areas. Focus on: a) Promising but understudied questions, b) Outdated findings needing replication, c) Emerging technologies/methods. Present gaps as specific, researchable questions with rationale for their importance." | Standard response handling |
| **AuthorNetworkMapper** | `SearchWorks` (authors) | Maps collaboration networks between researchers | "You are a scientific collaboration analyst. For the specified researcher or institution: 1) Map co-authorship networks, 2) Identify key collaborators, 3) Analyze publication patterns. Include in your report: a) Network visualization description, b) Key collaborators and their institutions, c) Temporal evolution of collaborations. Format as a structured markdown document with clear section headers." | Standard response handling |
| **JournalScout** | `SearchJournals`, `GetJournalById` | Identifies suitable journals for manuscript submission | "You are a journal matching expert. For the provided manuscript: 1) Analyze title/abstract to identify key topics, 2) Use SearchJournals to find matching scopes, 3) Rank by impact factor and audience fit. For each journal, provide: Name, impact factor, acceptance rate, open access options, submission guidelines URL, and why it's a good fit. Format as a comparison table." | Standard response handling |

## Implementation Notes

1. **Large Response Handling**:
   - Tools marked for large response handling implement the `@handle_large_response` decorator
   - Output is automatically written to files when response exceeds 50,000 tokens
   - File paths are returned to the main agent for reference

2. **Tool Usage Guidelines**:
   - All tools include proper error handling for API rate limits
   - Search results are limited to 100 items by default (configurable)
   - Date ranges should be specified when possible to improve relevance

3. **Subagent Best Practices**:
   - Each subagent is designed for a specific, narrow task
   - Tools are carefully selected to minimize complexity
   - Prompts include clear instructions for tool usage
   - Output is consistently formatted for further processing

4. **Performance Considerations**:
   - Caching is implemented for frequently accessed resources
   - Batch processing is used for large datasets
   - Progress updates are provided for long-running operations

## Example Implementation (Python)

```python
from deepagents.decorators import handle_large_response
from typing import List, Dict, Any
import json

@tool(description="Retrieves and processes full text of research papers")
@handle_large_response(max_length=50000)
async def get_full_text_analysis(paper_id: str) -> Dict[str, Any]:
    """
    Retrieves and analyzes full text of a research paper.
    
    Args:
        paper_id: CORE ID or DOI of the paper
        
    Returns:
        dict: Analysis containing key sections and metadata
        
    Note:
        Automatically handles large responses by writing to files
        when analysis exceeds 50,000 tokens.
    """
    # Implementation would go here
    return analysis_results
```

## Next Steps

1. Implement core tools with proper error handling
2. Create subagent classes with the specified prompts
3. Set up testing for each subagent-tool combination
4. Implement monitoring for API rate limits and usage
5. Create documentation with usage examples for each subagent
