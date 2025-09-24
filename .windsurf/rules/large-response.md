---
trigger: model_decision
description: use this rule when creating tool. it contains rule and guideline for handling tools that may overflow model context window. 
---

# Rule: Mandatory Large Response Handling for Tools

## Purpose
Ensure tools that may generate responses exceeding 50,000 tokens (or user-specified limits) automatically write to files to prevent context window overflows.

## When to Use `@handle_large_response`

**MANDATORY** for any tool that:
1. **Exceeds 50K Tokens**: Any response likely to exceed 50,000 tokens
2. **User Request**: When explicitly requested by the user
3. **Documentation Indicates**: If API/function documentation mentions:
   - Returns "full papers" or "complete articles"
   - Returns "comprehensive lists" or "detailed reports"
   - Returns "raw data" or "complete datasets"
   - Has parameters like `full_text=True` or `complete_results=True`

## Implementation

### Basic Usage
```python
from deepagents.decorators import handle_large_response

@tool(description="Tool description")
@handle_large_response(max_length=50000)  # 50K token threshold
def potentially_large_tool():
    # Implementation
    return large_data
```

### Source Code Location
- **Decorator**: [backend/src/deepagents/decorators.py](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/decorators.py:0:0-0:0)
- **Utilities**: [backend/src/deepagents/utils.py](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/utils.py:0:0-0:0)

## Implementation Requirements

1. **Always Review Documentation**:
   - Check if the tool's documentation mentions large returns
   - Look for parameters that control response size
   - Note any examples showing large outputs

2. **When in Doubt**:
   - Use the decorator if the tool processes:
     - Full documents/papers
     - Raw data exports
     - Comprehensive search results
     - Bulk operations

3. **Documentation**:
   - Add a note in the tool's docstring about large response handling
   - Include example of expected output size

## Example

```python
@tool(description="Fetches and returns complete research papers")
@handle_large_response()  # Uses default 50K threshold
def get_research_paper(paper_id: str, include_supplementary: bool = False):
    """
    Returns the complete text of a research paper, which may include:
    - Full paper content (typically 5K-50K+ tokens)
    - Supplementary materials
    - Citations and references
    
    Note: Automatically handles large responses by writing to files
    to prevent context window overflows.
    """
    # Implementation
    return paper_content
```