# Subagent Cleanup Plan

## Issue
Multiple subagent files contain both:
1. Individual `@tool` decorated functions
2. Subagent configurations that reference these tools

This creates redundancy and confusion since:
- The subagents handle the logic internally via the `task` tool
- Individual tools are no longer needed
- Having both creates conflicts in the literature review agent

## Files to Clean Up

### ✅ Already Fixed
- `planning_coordinator.py` - Removed `@tool` decorators, made functions internal helpers

### 🔧 Need to Fix
- `request_validator.py` - Has `validate_literature_review_request` and `assess_research_feasibility` tools
- `literature_screener.py` - Likely has screening-related tools
- `content_analyzer.py` - Likely has analysis tools  
- `synthesis_engine.py` - Likely has synthesis tools

## Cleanup Strategy

For each subagent file:
1. **Remove `@tool` decorators** from functions
2. **Convert to internal helper functions** (prefix with `_`)
3. **Remove tool references** from subagent configuration
4. **Update descriptions** to clarify internal handling
5. **Keep helper functions** for internal subagent logic

## Benefits After Cleanup

1. **No more tool conflicts** - Clear separation between tools and subagents
2. **Simplified architecture** - Subagents handle logic internally
3. **Better human-in-the-loop** - Interrupts work on `task` calls, not individual tools
4. **Reduced confusion** - One way to do things (subagents via `task` tool)
5. **Easier maintenance** - Less duplicate code

## Implementation Order

1. ✅ `planning_coordinator.py` - DONE
2. `request_validator.py` - Remove validation tools
3. `literature_screener.py` - Remove screening tools
4. `content_analyzer.py` - Remove analysis tools
5. `synthesis_engine.py` - Remove synthesis tools

This will make the literature review agent much cleaner and eliminate the tool conflicts.
