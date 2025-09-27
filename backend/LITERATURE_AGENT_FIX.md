# Literature Review Agent Error Fix

## Error Analysis

**Error Message**: `Found AIMessages with tool_calls that do not have a corresponding ToolMessage`

**Root Cause**: The literature review agent was configured with BOTH:
1. Individual tools (like `create_research_plan`, `refine_research_plan`, etc.)
2. Subagents that contain the same functionality

This created a conflict where:
- The agent tried to call subagents via the `task` tool
- But also had direct access to the individual tools
- The `task` tool call to `'planning_coordinator'` subagent failed to return a proper ToolMessage
- This left an incomplete tool call in the chat history, causing the validation error

## Specific Tool Causing Issue

**Tool**: `task` tool calling subagent `'planning_coordinator'`
**Subagent**: `planning_coordinator` (for creating research plans)
**Conflict**: Agent had both the subagent AND the individual `create_research_plan` tool

## Fix Applied

### 1. Removed Duplicate Individual Tools
Removed these individual tools from the agent configuration:
- `validate_literature_review_request`
- `assess_research_feasibility` 
- `create_research_plan`
- `refine_research_plan`
- `generate_search_keywords`
- `screen_papers`
- `generate_prisma_data`
- `analyze_full_paper`
- `extract_visual_data`
- `create_paper_summary`
- `identify_themes`
- `assess_evidence_strength`
- `identify_research_gaps`
- `generate_synthesis_report`

### 2. Updated Interrupt Configuration
Changed from individual tool interrupts to subagent task interrupts:
```python
# OLD (caused conflicts)
interrupt_config={
    "create_research_plan": True,
    "refine_research_plan": True,
    "generate_synthesis_report": True,
    "scroll_export_works": True,
}

# NEW (correct)
interrupt_config={
    "task": True,                    # Interrupts all subagent calls
    "scroll_export_works": True,     # Still interrupt large exports
}
```

## How It Works Now

1. **Agent receives request** → Uses subagents via `task` tool
2. **Task tool calls subagent** → `task(subagent_type='planning_coordinator', description='...')`
3. **Subagent executes** → Returns proper ToolMessage response
4. **Human approval** → Interrupt on `task` tool allows human review
5. **Continuation** → Agent proceeds with full context

## Expected Behavior

- Agent will use subagents properly via the `task` tool
- Human-in-the-loop interrupts will work on subagent calls
- No more "missing ToolMessage" errors
- Conversation memory will be maintained

## Files Modified

- ✅ `backend/agents/literature_review.py` - Removed duplicate tools, fixed interrupts

## Test Steps

1. Restart backend server
2. Send literature review request
3. Agent should call `planning_coordinator` subagent successfully
4. Should pause for human approval when calling subagents
5. Should continue with full context after approval
