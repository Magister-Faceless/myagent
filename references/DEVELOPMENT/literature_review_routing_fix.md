# Literature Review Agent Routing Fix

## 🔍 **Problem Identified**

The literature review agent was not following the new instructions and workflow because of a **routing configuration issue**.

### **Root Cause**

The `langgraph.json` file was pointing to the **wrong agent implementation**:

**Before (Incorrect):**
```json
"literature-review": "agents.dynamic_agents:literature_review"
```

This was loading the agent through the **agent factory system** (`create_agent_by_id("literature-review")`), which reads configuration from `config/agents.json`.

### **What Was Wrong in agents.json**

The `agents.json` configuration (lines 157-193) had **outdated settings**:

1. ❌ **Old Instructions:**
   ```json
   "instructions": "You are a literature review specialist who orchestrates planning, screening, analysis, and synthesis across dedicated subagents. Follow PRISMA principles..."
   ```
   - NOT using the new `LITERATURE_REVIEW_AGENT_INSTRUCTIONS` from `config/prompts.py`
   - Missing file structure requirements
   - Missing citation verification step

2. ❌ **Wrong Tools:**
   ```json
   "tools": [
     "search_works",
     "scroll_export_works",
     "get_work_by_id",
     ...
   ]
   ```
   - Should be `"tools": []` (empty - only built-in tools)

3. ❌ **Wrong Subagents:**
   ```json
   "subagents": [
     "request_validator",
     "planning_coordinator",
     "literature_screener",
     "content_analyzer",
     "synthesis_engine"
   ]
   ```
   - Missing `"specialist-agent"` (general subagent)
   - Missing `"work_reviewer"`
   - Missing `"literature_review_reviewer"` (new citation verifier)

4. ❌ **Old Interrupt Config:**
   ```json
   "interrupt_config": {
     "planning_coordinator": true,
     "synthesis_engine": true
   }
   ```
   - Non-functional interrupt config (we removed this)

## ✅ **Solution Applied**

Updated `langgraph.json` to point directly to your custom implementation:

**After (Correct):**
```json
{
  "graphs": {
    "main-agent": "agents.main_agent:agent",
    "literature-review": "agents.literature_review:agent"
  }
}
```

### **What This Does**

- ✅ **Bypasses the agent factory** - No longer reads from `agents.json`
- ✅ **Uses your custom file** - Loads from `agents/literature_review.py`
- ✅ **Correct prompt** - Uses `LITERATURE_REVIEW_AGENT_INSTRUCTIONS` from `config/prompts.py`
- ✅ **Correct architecture** - CustomSubAgent pattern with proper tools/subagents
- ✅ **All new features** - File structures, citation verification, etc.

## 📊 **Comparison**

### **Old Flow (via agents.json):**
```
Frontend → langgraph.json → dynamic_agents.py → agent_factory.py → agents.json → OLD CONFIG
```

### **New Flow (direct):**
```
Frontend → langgraph.json → literature_review.py → YOUR CUSTOM AGENT
```

## 🎯 **What Will Work Now**

1. ✅ **Correct Workflow:**
   - Capture Request → Plan → Search → Screen → Analyze → Synthesize → Verify → Deliver

2. ✅ **File Creation:**
   - request.md
   - literature_review_plan.md
   - initial_list.csv
   - refined_list.csv
   - literature_analysis.md (with structured format)
   - literature_review.md (with citations)

3. ✅ **Structured Formats:**
   - literature_analysis.md follows the exact structure
   - literature_review.md has [N] citations and References section

4. ✅ **Citation Verification:**
   - literature_review_reviewer subagent will verify citations
   - Cross-references with literature_analysis.md

5. ✅ **Correct Subagents:**
   - specialist-agent (general with ALL tools)
   - literature_screener
   - content_analyzer
   - synthesis_engine
   - work_reviewer
   - literature_review_reviewer (new)

6. ✅ **Human-in-the-Loop:**
   - Conversational checkpoints at each phase
   - No interrupt_config (natural pauses)

## 🚀 **Next Steps**

1. **Restart the backend server** for changes to take effect
2. **Test the literature review agent** from the frontend
3. **Verify it follows the new workflow:**
   - Creates request.md first
   - Asks for plan approval
   - Creates files with correct structures
   - Runs citation verification

## 📝 **Note on Agent Factory System**

If you want to use the agent factory system in the future, you would need to update `config/agents.json` with the correct configuration. However, for now, the **direct routing approach** is simpler and ensures your custom implementation is used.

## ✨ **Summary**

**Problem:** Frontend was loading old agent configuration from `agents.json`
**Solution:** Updated `langgraph.json` to point directly to your custom `literature_review.py`
**Result:** Agent now uses correct prompt, workflow, and features

The literature review agent should now work as intended! 🎉
