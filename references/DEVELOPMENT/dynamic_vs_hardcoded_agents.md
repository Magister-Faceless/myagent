# Dynamic Agents vs Hardcoded Agents - Complete Explanation

## 📊 **Two Agent Creation Systems**

Your backend has **TWO different systems** for creating agents:

### **1. Dynamic Agents (Agent Factory System)**

**How it works:**
```
Frontend → langgraph.json → dynamic_agents.py → agent_factory.py → agents.json → CREATE AGENT
```

**Configuration Source:** `config/agents.json`

**Logic Source:**
- **Instructions:** From `config/prompts.py` based on `agent_type`
- **Tools:** Auto-selected based on `agent_type` in `agent_factory.py`
- **Subagents:** Auto-selected based on `agent_type` in `agent_factory.py`

**Example from agents.json:**
```json
{
  "id": "research-agent",
  "agent_type": "research",
  "instructions": "...",
  "tools": [],  // Empty = auto-populated
  "subagents": []  // Empty = auto-populated
}
```

**Agent Factory Logic (agent_factory.py):**
```python
def _get_default_tools_for_type(self, agent_type: AgentType):
    if agent_type == AgentType.RESEARCH:
        return base_tools + [
            "perplexity_reasoning_search",
            "perplexity_focused_research",
            "academic_search",
            "deep_research",
            "sonar_deep_research"
        ]
    elif agent_type == AgentType.MEDICAL_RESEARCH:
        return base_tools + [
            "search_works",
            "scroll_export_works",
            ...
        ]
```

### **2. Hardcoded Agents (Direct File Import)**

**How it works:**
```
Frontend → langgraph.json → specific_agent.py → CREATE AGENT
```

**Configuration Source:** The Python file itself (e.g., `agents/literature_review.py`)

**Logic Source:**
- **Instructions:** Explicitly defined in the file
- **Tools:** Explicitly imported and listed
- **Subagents:** Explicitly created and configured

**Example:**
```python
# agents/literature_review.py
from config.prompts import LITERATURE_REVIEW_AGENT_INSTRUCTIONS

agent = create_deep_agent(
    tools=[],  # Explicitly defined
    subagents=[...],  # Explicitly created
    instructions=LITERATURE_REVIEW_AGENT_INSTRUCTIONS,
    ...
)
```

## 🔍 **Current Agents in langgraph.json**

### **Dynamic Agents (via agent factory):**

1. **research-agent** (`agents.dynamic_agents:research_agent`)
   - Type: `research`
   - Auto-gets: perplexity tools, deep research, academic search
   - Auto-gets: reasoning_subagent, deep_research_subagent, etc.

2. **code-assistant** (`agents.dynamic_agents:code_assistant`)
   - Type: `coding`
   - Auto-gets: coding-focused tools
   - Auto-gets: reasoning_subagent, technical_research_subagent

3. **content-creator** (`agents.dynamic_agents:content_creator`)
   - Type: `creative`
   - Auto-gets: creative tools
   - Auto-gets: reasoning_subagent

4. **medical-literature-agent** (`agents.dynamic_agents:medical_literature_agent`)
   - Type: `medical_research`
   - Auto-gets: CORE API tools, literature tools
   - Auto-gets: reasoning_subagent, deep_research_subagent, technical_research_subagent

5. **python-coding-agent** (`agents.dynamic_agents:python_coding_agent`)
   - Type: `python_coding`
   - Auto-gets: Python-focused tools
   - Auto-gets: reasoning_subagent, technical_research_subagent

6. **enhanced-main-agent** (`agents.dynamic_agents:enhanced_main_agent`)
   - Type: `enhanced_general`
   - Has explicit tools in agents.json (memory tools)
   - Has explicit subagents in agents.json

### **Hardcoded Agents (direct import):**

1. **main-agent** (`agents.main_agent:agent`)
   - Defined in: `agents/main_agent.py`
   - CustomSubAgent pattern
   - Explicit configuration

2. **literature-review** (`agents.literature_review:agent`)
   - Defined in: `agents/literature_review.py`
   - CustomSubAgent pattern
   - Explicit configuration

## 🎯 **Key Differences**

| Aspect | Dynamic Agents | Hardcoded Agents |
|--------|---------------|------------------|
| **Configuration** | `agents.json` | Python file |
| **Tools** | Auto-selected by type | Explicitly defined |
| **Subagents** | Auto-selected by type | Explicitly created |
| **Instructions** | From prompts.py via type mapping | Directly imported |
| **Flexibility** | Limited to predefined types | Full control |
| **Maintenance** | Update JSON + factory logic | Update Python file |
| **Best for** | Standard agent types | Custom specialized agents |

## 📋 **Frontend Connection**

**Current Frontend Config** (`frontend/src/lib/agents/config.ts`):

```typescript
export const AVAILABLE_AGENTS: Agent[] = [
  { id: "main-agent", name: "Main Agent", ... },
  { id: "research-agent", name: "Research Agent", ... },
  { id: "code-assistant", name: "Code Assistant", ... },
  { id: "content-creator", name: "Content Creator", ... },
  { id: "literature-review", name: "Literature Review Agent", ... },
];
```

**Missing from Frontend:**
- ❌ medical-literature-agent
- ❌ python-coding-agent
- ❌ enhanced-main-agent

## ✅ **Recommendations**

### **For Literature Review Agent:**
✅ **Already fixed** - Using hardcoded approach (`agents.literature_review:agent`)
- Full control over prompt, tools, subagents
- CustomSubAgent pattern
- Citation verification

### **For Other Agents:**

**Option 1: Keep Dynamic (Recommended for standard agents)**
- Good for: research-agent, code-assistant, content-creator
- Easy to maintain via agents.json
- Automatic tool/subagent selection

**Option 2: Convert to Hardcoded (For specialized agents)**
- Good for: Agents needing custom logic
- Create dedicated .py files
- Full control over behavior

### **For Frontend:**
**Add missing agents** to make all backend agents available in UI

## 🔧 **How Dynamic Agents Get Their Logic**

1. **Agent Type Mapping** (agent_factory.py):
   ```python
   AgentType.RESEARCH → RESEARCH_AGENT_INSTRUCTIONS
   AgentType.CODING → CODING_AGENT_INSTRUCTIONS
   AgentType.MEDICAL_RESEARCH → MEDICAL_RESEARCH_INSTRUCTIONS
   ```

2. **Tool Selection** (agent_factory.py):
   ```python
   if agent_type == AgentType.RESEARCH:
       return ["perplexity_reasoning_search", "academic_search", ...]
   ```

3. **Subagent Selection** (agent_factory.py):
   ```python
   if agent_type == AgentType.RESEARCH:
       return ["reasoning_subagent", "deep_research_subagent", ...]
   ```

4. **Final Assembly** (agent_factory.py):
   ```python
   agent = create_deep_agent(
       tools=resolved_tools,
       subagents=resolved_subagents,
       instructions=instructions_from_type,
       ...
   )
   ```

## 📝 **Summary**

- **Dynamic Agents:** Configured via JSON, logic auto-selected by type
- **Hardcoded Agents:** Configured in Python files, full explicit control
- **Frontend:** Only shows agents listed in `config.ts`
- **Missing:** 3 backend agents not exposed to frontend
- **Literature Review:** Now using hardcoded approach (correct implementation)
