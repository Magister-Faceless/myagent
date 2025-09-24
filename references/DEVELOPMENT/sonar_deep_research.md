# Sonar Deep Research System

## Overview
The Sonar Deep Research System is a sophisticated AI-powered research assistant that combines the capabilities of Perplexity's sonar-deep-research model with the DeepAgents framework to deliver exhaustive, expert-level research capabilities. This document outlines the architecture, components, and usage of this powerful research system.

## System Architecture

### Core Components

1. **Sonar Deep Research Tool**
   - Direct interface to Perplexity's sonar-deep-research model
   - Handles API communication and response processing
   - Configured for exhaustive research with advanced parameters

2. **Deep Research Subagent**
   - Orchestrates multi-phase research workflows
   - Manages file operations and documentation
   - Implements human-in-the-loop approval system
   - Leverages built-in tools for comprehensive research management

## Implementation Details

### Tool: sonar_deep_research

**Location**: `backend/tools/search/sonar_deep_research.py`

**Key Features**:
- Direct integration with Perplexity's API
- Configurable research parameters (reasoning effort, domain filtering, etc.)
- Support for both synchronous and asynchronous operations
- Comprehensive error handling and response formatting

**Parameters**:
- `research_query`: Primary research question or topic
- `reasoning_effort`: Level of computational effort (low/medium/high)
- `focus_domains`: List of domains to prioritize
- `exclude_domains`: List of domains to exclude
- `search_recency_filter`: Time-based filtering of sources
- `async_mode`: Enable/disable asynchronous processing

### Subagent: sonar-deep-research

**Location**: `backend/subagents/deep_research_agent.py`

**Capabilities**:
- Multi-phase research planning and execution
- Systematic documentation of findings
- Integration with built-in tools for file operations
- Progress tracking and reporting

**Included Tools**:
- `sonar_deep_research`: Primary research tool
- `write_file`: For saving research outputs
- `read_file`: For reviewing previous findings
- `edit_file`: For updating research documents
- `ls`: For file management
- `write_todos`: For research planning and tracking

## Research Workflow

1. **Initial Planning**
   - Create comprehensive research plan using `write_todos`
   - Define research phases and success criteria
   - Set up file structure for documentation

2. **Research Execution**
   - Execute `sonar_deep_research` with optimized parameters
   - Apply domain filtering and search constraints
   - Use async mode for complex queries

3. **Progressive Documentation**
   - Save findings to structured files
   - Maintain separate files for different research aspects
   - Use timestamps for version control

4. **Synthesis & Analysis**
   - Cross-reference findings
   - Identify patterns and insights
   - Validate information across multiple sources

5. **Final Delivery**
   - Generate comprehensive final report
   - Include executive summary
   - Provide complete citations and references

## File Structure

Research outputs are organized in the following structure:

```
research/
  ├── summaries/
  │   └── research_summary_YYYYMMDD_HHMMSS.md
  ├── analysis/
  │   └── detailed_analysis_YYYYMMDD_HHMMSS.md
  ├── methodology/
  │   └── methodology_YYYYMMDD_HHMMSS.md
  └── references/
      └── citations_YYYYMMDD_HHMMSS.md
```

## Best Practices

1. **For Optimal Results**:
   - Always start with a clear research question
   - Use appropriate reasoning_effort level
   - Apply domain filtering to improve relevance
   - Enable async_mode for complex queries

2. **For Large Research Projects**:
   - Break down into smaller, focused queries
   - Use the todo system to track progress
   - Save interim results frequently
   - Document methodology and decisions

3. **For Technical Research**:
   - Include technical domains in focus_domains
   - Use appropriate technical terminology
   - Pay attention to implementation details

## Integration with CORE API

The Sonar Deep Research system can be integrated with CORE API for academic research by combining it with the following subagents:

1. **LiteratureScreener**: For initial paper discovery
2. **TrendAnalyzer**: For identifying research trends
3. **VenueAnalyzer**: For finding relevant publication venues

## Performance Considerations

- **Cost**: Sonar Deep Research is a premium service with higher API costs
- **Rate Limiting**: Be mindful of API rate limits
- **Response Time**: Complex queries may take several minutes to complete
- **Token Usage**: Responses can be large (100K+ tokens)

## Example Usage

```python
# Example of using the sonar_deep_research tool
result = sonar_deep_research(
    research_query="Recent advances in quantum computing applications for drug discovery",
    reasoning_effort="high",
    focus_domains=["nature.com", "sciencedirect.com", "arxiv.org"],
    exclude_domains=["wikipedia.org"],
    search_recency_filter="year",
    async_mode=True
)
```

## Troubleshooting

- **API Errors**: Check API key and rate limits
- **Timeout Issues**: Increase timeout or reduce query complexity
- **Incomplete Results**: Check for error messages in the response
- **File Permission Issues**: Verify write permissions in the output directory

## Future Enhancements

1. **Automated Source Validation**: Cross-verify facts across multiple sources
2. **Interactive Research**: Real-time collaboration features
3. **Advanced Analytics**: Integration with data visualization tools
4. **Custom Research Templates**: Domain-specific research methodologies

## Conclusion

The Sonar Deep Research System represents a significant advancement in AI-assisted research, combining the power of Perplexity's sonar-deep-research model with the flexibility of the DeepAgents framework. By following the structured approach outlined in this document, researchers can leverage this system to conduct exhaustive, high-quality research across a wide range of domains.
