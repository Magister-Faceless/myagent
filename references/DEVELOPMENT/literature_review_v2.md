I'll analyze the sample agent structure and help you redesign the literature review agent with proper agentic agency while maintaining structured output.

Let me first examine the referenced files:



Now let me check the prompts configuration to understand the current setup:



Let me check the LITERATURE_REVIEW_AGENT_INSTRUCTIONS and look at available tools:



Let me check what tools are available and understand the deepagents framework better:



Now let me check the tools available and understand interrupt capabilities:



Now let me read the deepagents documentation about interrupts and understand the framework better:



Perfect! Now I have a comprehensive understanding. Let me create a detailed analysis and plan:



# Analysis & Recommendations for Literature Review Agent Redesign

## 📊 Key Findings from Sample Agent Analysis

### **Sample Agent Structure (What Works Well)**

1. **Main Agent Role**: Pure orchestrator with minimal tools
   - Only has `internet_search` tool (domain-specific)
   - Uses built-in tools (`write_file`, `read_file`, `edit_file`, `write_todos`)
   - Focuses on planning and delegation

2. **Subagent Distribution**:
   - `research-agent`: Handles actual research with `internet_search` tool
   - `critique-agent`: Reviews output, has NO tools (reads files only)
   - Each subagent has ONE focused responsibility

3. **File Management Pattern**:
   - Main agent writes `question.txt` immediately (preserves user request)
   - Main agent writes `final_report.md` (owns the output)
   - Subagents read files but don't write them
   - Clear file ownership and responsibility

4. **Prompt Strategy**:
   - Main agent prompt is comprehensive but focused on workflow
   - Subagent prompts are minimal and task-specific
   - No tool usage instructions in prompts (framework handles this)

## 🔍 Interrupt Configuration Analysis

### **How Interrupts Work in DeepAgents**

Based on the framework code and documentation:

1. **`interrupt_config` Parameter**:
   ```python
   interrupt_config={
       "tool_name": {
           "allow_ignore": False,      # Currently NOT supported
           "allow_respond": True,       # Allow custom response
           "allow_edit": True,          # Allow editing tool args
           "allow_accept": True,        # Allow accepting tool call
       }
   }
   ```

2. **Current Limitations**:
   - ❌ **Cannot interrupt at arbitrary points** - only on tool calls
   - ❌ **Cannot interrupt subagent spawning** - `task` tool interrupts not supported
   - ❌ **Only ONE tool can be interrupted at a time** (parallel interrupts fail)
   - ❌ **`allow_ignore` is NOT supported** in current implementation

3. **What IS Possible**:
   - ✅ Interrupt specific tool calls (e.g., expensive API calls)
   - ✅ Edit tool arguments before execution
   - ✅ Provide custom responses instead of executing tool
   - ✅ Accept/approve tool execution

### **Your Current Implementation Issue**

The `interrupt_config` at line 131 in your literature review agent:
```python
interrupt_config={
    "planning_coordinator": {  # This is a SUBAGENT name, not a tool!
        "allow_ignore": False,
        "allow_respond": True,
        "allow_edit": True,
        "allow_accept": True,
    }
}
```

**❌ This won't work as intended because**:
- `planning_coordinator` is a subagent, not a tool
- Subagents are spawned via the built-in `task` tool
- You cannot interrupt subagent spawning directly
- The framework doesn't support interrupting the `task` tool

## 🎯 Recommended Architecture for Literature Review Agent

### **Design Philosophy**

Based on the sample agent and your requirements, here's the optimal structure:

### **1. Literature Review Agent (Main Orchestrator)**

**Tools**: ONLY built-in tools
- `write_todos` - Planning
- `write_file` - Document creation
- `read_file` - Document reading
- `edit_file` - Document editing
- [ls](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/tools:0:0-0:0) - File discovery
- `task` - Subagent spawning (built-in)

**Responsibilities**:
1. ✅ Write `request.md` immediately (preserve user request)
2. ✅ Plan literature review process using `write_todos`
3. ✅ Create and refine `literature_review_plan.md` through dialogue
4. ✅ Spawn subagents for specific tasks
5. ✅ Write all final documents (owns the outputs)
6. ✅ Orchestrate the workflow

**Does NOT**:
- ❌ Use search tools directly
- ❌ Use CORE API tools directly
- ❌ Use analysis tools directly

### **2. Subagent Structure**

#### **General Subagent** (Already exists)
- **Purpose**: Miscellaneous tasks, flexible helper
- **Tools**: ALL available tools (search, CORE API, literature tools, etc.)
- **Usage**: When literature review agent needs something done that doesn't fit other subagents

#### **Search Subagent** (New or use existing)
- **Purpose**: Conduct literature searches
- **Tools**: CORE API search tools, Perplexity search
- **Output**: Returns results to main agent (doesn't write files)

#### **Analysis Subagent** (New or use existing)
- **Purpose**: Analyze papers, extract metadata
- **Tools**: Literature analysis tools, quality assessment
- **Output**: Returns analysis to main agent

#### **Synthesis Subagent** (New or use existing)
- **Purpose**: Synthesize findings, generate insights
- **Tools**: Perplexity Sonar Deep Research
- **Output**: Returns synthesis to main agent

### **3. Human-in-the-Loop Strategy**

Since you **cannot interrupt subagent spawning**, here's the workaround:

#### **Option A: Conversational Planning (Recommended)**
```python
# In main agent prompt:
"""
PLANNING PHASE (INTERACTIVE):
1. Write user request to request.md immediately
2. Use write_todos to create initial plan
3. Draft literature_review_plan.md with:
   - Research question
   - Inclusion/exclusion criteria
   - Search strategy
   - Analysis approach
4. PRESENT plan to user and ASK: "Does this plan look good? Any changes needed?"
5. WAIT for user response before proceeding
6. If user suggests changes, update plan and ask again
7. Only proceed with execution after user approval
"""
```

**How it works**:
- Agent naturally pauses after asking a question
- User provides feedback
- Agent refines and asks again
- No interrupt config needed - it's conversational

#### **Option B: Interrupt on Expensive Tools**
```python
interrupt_config={
    "scroll_export_works": {  # Large data export
        "allow_ignore": False,
        "allow_respond": True,
        "allow_edit": True,
        "allow_accept": True,
    },
    "sonar_deep_research": {  # Expensive API call
        "allow_ignore": False,
        "allow_respond": True,
        "allow_edit": True,
        "allow_accept": True,
    }
}
```

**But**: Main agent won't call these directly (subagents will), so this doesn't help much.

#### **Option C: Checkpoint-Based Planning (Best for Your Use Case)**
```python
# In main agent prompt:
"""
WORKFLOW WITH USER CHECKPOINTS:

PHASE 1 - PLANNING (Interactive):
1. Write request.md
2. Create initial plan with write_todos
3. Draft literature_review_plan.md
4. ASK USER: "Review the plan in literature_review_plan.md. Reply 'approved' to proceed or suggest changes."
5. WAIT for user response
6. Refine plan based on feedback
7. Repeat until user says "approved"

PHASE 2 - INITIAL SEARCH (Semi-automated):
1. Spawn search subagent to conduct initial search
2. Process results into initial_list.csv
3. ASK USER: "Found X papers. Review initial_list.csv. Reply 'proceed' to continue screening."
4. WAIT for user response

PHASE 3 - SCREENING (Interactive):
1. ASK USER: "What are the inclusion/exclusion criteria?"
2. WAIT for criteria
3. Spawn screening subagent
4. Create refined_list.csv
5. ASK USER: "Screening complete. Review refined_list.csv. Approve to proceed with analysis?"
6. WAIT for approval

PHASE 4 - ANALYSIS (Automated):
1. For each paper in refined_list.csv:
   - Spawn analysis subagent to get full text and analyze
   - Collect analysis results
2. Write all analyses to literature_analysis.md
3. ASK USER: "Analysis complete. Review literature_analysis.md. Approve for final synthesis?"
4. WAIT for approval

PHASE 5 - SYNTHESIS (Automated):
1. Spawn synthesis subagent with literature_analysis.md
2. Receive final literature review
3. Write to literature_review.md
4. PRESENT to user with summary
"""
```

### **4. File Management Strategy**

```python
# Main agent owns ALL file creation:
FILES_TO_CREATE = {
    "request.md": "User's literature review request (created first)",
    "literature_review_plan.md": "Detailed step-by-step plan (refined with user)",
    "initial_list.csv": "Initial search results (wide search)",
    "refined_list.csv": "Screened papers after inclusion/exclusion",
    "literature_analysis.md": "Critical analysis of each paper",
    "literature_review.md": "Final literature review document"
}

# Subagents RETURN data, don't write files
# Main agent writes files based on subagent outputs
```

### **5. Full-Text Analysis Workflow**

For obtaining and analyzing full-text papers:

```python
# In main agent prompt:
"""
FULL-TEXT ANALYSIS PROCESS:
1. Read refined_list.csv to get paper IDs/DOIs
2. For each paper:
   a. Spawn general_subagent with task: "Get full text for DOI: {doi}"
   b. Subagent uses CORE API get_work_by_id or searches for PDF
   c. Subagent returns full text content
   d. Spawn analysis_subagent with: "Critically analyze this paper: {full_text}"
   e. Analysis subagent returns structured analysis
   f. Append analysis to literature_analysis.md
3. After all papers analyzed, literature_analysis.md is complete
"""
```

## 📝 Recommended Prompt Structure

### **Main Agent Prompt** (Concise, Workflow-Focused)

```python
LITERATURE_REVIEW_AGENT_INSTRUCTIONS = """You are a Literature Review Orchestrator. Your role is to plan and coordinate a systematic literature review through human-in-the-loop dialogue and subagent delegation.

REQUIRED FILES (you must create these):
1. request.md - User's literature review request
2. literature_review_plan.md - Detailed review plan (refined with user)
3. initial_list.csv - Initial search results
4. refined_list.csv - Screened papers
5. literature_analysis.md - Critical analysis of each paper
6. literature_review.md - Final literature review

WORKFLOW:
1. CAPTURE REQUEST: Write user's request to request.md immediately
2. PLAN INTERACTIVELY: 
   - Create plan with write_todos
   - Draft literature_review_plan.md
   - Discuss with user, refine until approved
3. INITIAL SEARCH:
   - Spawn subagent to search literature
   - Write results to initial_list.csv
   - Show user, get feedback
4. SCREENING:
   - Get inclusion/exclusion criteria from user
   - Spawn subagent to screen papers
   - Write refined_list.csv
   - Get user approval
5. ANALYSIS:
   - For each paper in refined_list.csv:
     * Spawn subagent to get full text
     * Spawn subagent to analyze paper
     * Collect all analyses
   - Write complete literature_analysis.md
   - Get user approval
6. SYNTHESIS:
   - Spawn synthesis subagent with literature_analysis.md
   - Write final literature_review.md
   - Present to user

TOOLS USAGE:
- Use ONLY built-in tools (write_file, read_file, edit_file, write_todos, ls, task)
- Delegate ALL searches, analyses, and synthesis to subagents via task tool
- You orchestrate; subagents execute

HUMAN INTERACTION:
- Ask questions and WAIT for user responses at each checkpoint
- Present files for review before proceeding
- Refine plans based on user feedback
- Never proceed without user approval at key stages

You have full agentic freedom to plan and execute, but you MUST create all required files and involve the user at key decision points."""
```

### **General Subagent Enhancement**

```python
GENERAL_SUBAGENT_PROMPT = """You are a specialist agent with access to ALL available tools. 

Your job is to:
1. Complete the specific task given to you by the main agent
2. Use any tools needed (search, CORE API, analysis, etc.)
3. Return comprehensive results to the main agent
4. Do NOT write files - return data for main agent to write

Available tool categories:
- Search tools (Perplexity, Tavily, CORE API search)
- Analysis tools (metadata extraction, quality assessment)
- Literature tools (PRISMA, citations, full-text retrieval)

Focus on the specific task, use tools effectively, and return thorough results."""
```

## 🚀 Implementation Plan

### **Step 1: Update Literature Review Agent**

## 🎯 Summary & Answers to Your Questions

### **Key Answers**

#### **1. Is `interrupt_config` at line 131 fixed to planning_coordinator?**

**No, it's NOT working as intended.** The current configuration:
```python
interrupt_config={
    "planning_coordinator": {...}
}
```

**❌ Problem**: `planning_coordinator` is a **subagent name**, not a tool name. The framework only supports interrupting **tool calls**, not subagent spawning. This configuration has no effect.

#### **2. Can the literature review agent use interrupts at any time?**

**No, with limitations**:
- ✅ Can interrupt **specific tool calls** (e.g., `scroll_export_works`, `sonar_deep_research`)
- ❌ **Cannot** interrupt at arbitrary points in the flow
- ❌ **Cannot** interrupt subagent spawning (the `task` tool)
- ❌ **Cannot** interrupt multiple tools in parallel

#### **3. Is there a way to pause the flow for human insight?**

**Yes, but through conversational design, not interrupt_config**:

**Best Approach**: Design the agent prompt to naturally pause and ask questions:
```python
"""
PLANNING PHASE:
1. Write request.md
2. Create plan in literature_review_plan.md
3. ASK USER: "Review the plan. Reply 'approved' to proceed or suggest changes."
4. WAIT for user response
5. Refine based on feedback
6. Repeat until approved
"""
```

This works because:
- Agent asks a question and stops generating
- User responds in next message
- Agent continues based on user input
- No special interrupt configuration needed

#### **4. About the General Subagent**

**Yes, you're correct!** The `general_subagent` in [backend/subagents/general_agent.py](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/subagents/general_agent.py:0:0-0:0) is designed for miscellaneous tasks. 

**Recommendation**: Give it access to ALL tools so the literature review agent can delegate any task:

```python
# In create_general_subagent():
from tools.core_api import *
from tools.literature import *
from tools.search import *

def create_general_subagent():
    return {
        "name": "specialist-agent",
        "description": "General-purpose specialist for any task requiring tools. Delegate specific subtasks here.",
        "prompt": GENERAL_SUBAGENT_PROMPT,
        "tools": [
            # All available tools
            search_works, scroll_export_works, get_work_by_id,
            extract_paper_metadata, quality_assessment,
            perplexity_reasoning_search, sonar_deep_research,
            # ... etc
        ],
        "model": get_default_model(),
    }
```

### **Recommended Implementation**

Would you like me to:

1. **Rewrite [backend/agents/literature_review.py](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/agents/literature_review.py:0:0-0:0)** with:
   - Only built-in tools for the main agent
   - Proper conversational human-in-the-loop design
   - File creation responsibility (all 6 required files)
   - Subagent delegation for all tool usage
   - Remove the non-functional `interrupt_config`

2. **Update [backend/subagents/general_agent.py](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/subagents/general_agent.py:0:0-0:0)** to:
   - Include all available tools
   - Enhanced prompt for flexible task handling

3. **Create a new comprehensive prompt** in [backend/config/prompts.py](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/config/prompts.py:0:0-0:0):
   - `LITERATURE_REVIEW_AGENT_INSTRUCTIONS` with the checkpoint-based workflow
   - Clear file ownership and creation requirements
   - Conversational human-in-the-loop pattern

The agent will have **full agentic freedom** to spawn subagents and plan the review, but will be **prompted to create the 6 required files** and **naturally pause at checkpoints** to get user input through conversational design rather than interrupt configuration.

Shall I proceed with implementing these changes?

ok, lets go with your suggestion '🎯 Recommended Architecture for Literature Review Agent'. 
1. since interrupt doesnt work for subagents, then omit it. 
2. use existing subagents, but refine their prompts if needed, to make it in line with the best practices as displayed in @sample_agent.md . if the required subagent does not exist, then create them.
3. for human in the loop, lets use Option A: Conversational Planning (Recommended). 
4. no need to interrupt for any tools use. 
5. also use Option C: Checkpoint-Based Planning (Best for Your Use Case). please refer to @sample_agent.md and also @prompts.py for best practices in prompting. I want the agent to perform its intended task BUT also to give it agency and freedom to act. 
6. proceed with 4. File Management Strategy




Now let me check what tools are available to give to the general subagent:

I'll proceed with the full implementation now. Let me start by creating the plan and then implementing all the changes:



## Step 1: Update Literature Review Agent Prompt



Now let me create the new comprehensive prompt for the literature review agent:



## Step 2: Update General Subagent with All Tools



Now let me update the GENERAL_SUBAGENT_PROMPT to be more aligned with the sample agent style:



## Step 3: Update Literature Review Agent File



## Step 4: Review and Refine Subagent Prompts

Let me check the existing subagent prompts:



Now let me update the subagent prompts to follow the sample agent pattern (return data, don't write files):



Now let me update the synthesis engine prompt:





Now let me check the work_reviewer prompt and update it:



Perfect! Now let me complete the implementation and create a summary:

# ✅ Implementation Complete!

I've successfully refined the literature review agent following the sample agent best practices. Here's what was implemented:

## 🎯 Changes Made

### **1. Literature Review Agent Prompt** ([config/prompts.py](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/config/prompts.py:0:0-0:0))
✅ **New conversational human-in-the-loop workflow** with 5 phases:
- **Phase 1**: Planning with user approval
- **Phase 2**: Initial search with user review
- **Phase 3**: Screening with interactive criteria setting
- **Phase 4**: Full-text analysis with user checkpoint
- **Phase 5**: Synthesis and final delivery

✅ **Clear file ownership**: Agent creates all 6 required files
- `request.md`, `literature_review_plan.md`, `initial_list.csv`, `refined_list.csv`, `literature_analysis.md`, `literature_review.md`

✅ **Agentic freedom**: Full flexibility to spawn subagents in any order while maintaining required checkpoints

### **2. General Subagent** ([subagents/general_agent.py](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/subagents/general_agent.py:0:0-0:0))
✅ **Added ALL available tools**:
- CORE API tools (9 tools for academic research)
- Literature tools (4 tools for metadata, PRISMA, citations, quality)
- Search tools (5 tools including Perplexity and Tavily)

✅ **Enhanced description**: Now clearly indicates it can handle any task requiring tools

✅ **Updated prompt**: Aligned with sample agent pattern

### **3. Literature Review Agent File** ([agents/literature_review.py](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/agents/literature_review.py:0:0-0:0))
✅ **Removed all external tools**: Main agent now has `tools=[]` (uses ONLY built-in tools)

✅ **Removed `interrupt_config`**: No longer needed with conversational approach

✅ **Simplified subagent list**: 
- `general_subagent` (with ALL tools)
- `literature_screener`
- `content_analyzer`
- `synthesis_engine`
- `work_reviewer`

✅ **Clear documentation**: Architecture and file ownership documented in docstrings

### **4. Subagent Prompts Refined**
✅ **All subagents updated to follow sample agent pattern**:
- **Return data** to main agent (don't write files)
- Focused, concise prompts
- Clear task descriptions
- Final response contains all results

Updated prompts:
- `GENERAL_SUBAGENT_PROMPT`
- `CONTENT_ANALYZER_PROMPT`
- `LITERATURE_SCREENER_PROMPT`
- `SYNTHESIS_ENGINE_PROMPT`
- `WORK_REVIEWER_PROMPT`

## 🏗️ Architecture Summary

```
Literature Review Agent (Orchestrator)
├── Tools: NONE (only built-in: write_file, read_file, edit_file, write_todos, ls, task)
├── Responsibilities: Planning, file creation, user dialogue, orchestration
└── Subagents:
    ├── specialist-agent (general) → ALL tools available
    ├── literature_screener → Screening tasks
    ├── content_analyzer → Paper analysis
    ├── synthesis_engine → Cross-paper synthesis
    └── work_reviewer → Quality assurance
```

## 🎭 How It Works

1. **User starts conversation** → Agent writes `request.md`
2. **Agent creates plan** → Writes `literature_review_plan.md`, asks for approval
3. **User approves** → Agent spawns subagent for search
4. **Subagent returns results** → Agent writes `initial_list.csv`, asks user to review
5. **User proceeds** → Agent spawns screening subagent
6. **Process continues** with checkpoints at each phase
7. **All files created by main agent** based on subagent outputs

## ✨ Key Benefits

- ✅ **Conversational human-in-the-loop** (no interrupt_config needed)
- ✅ **Clear separation of concerns** (orchestrator vs executors)
- ✅ **Maximum flexibility** (general subagent can handle any task)
- ✅ **Proper file ownership** (main agent owns all files)
- ✅ **Follows sample agent best practices** exactly
- ✅ **Agentic freedom** with structured checkpoints

The agent is now ready to conduct systematic literature reviews with proper human collaboration! 🚀