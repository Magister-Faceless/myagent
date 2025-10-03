# Complete Agent System Guide - Dynamic vs Hardcoded

## 📊 **Overview: Two Agent Creation Systems**

Your application uses **TWO different approaches** for creating agents:

### **System 1: Dynamic Agents (Agent Factory)**
- Configuration-driven
- Auto-selects tools and subagents based on agent type
- Defined in `config/agents.json`
- Created via `agent_factory.py`

### **System 2: Hardcoded Agents (Direct Files)**
- Code-driven
- Explicitly defines everything
- Defined in individual `.py` files (e.g., `agents/main_agent.py`)
- Full control over implementation

---

## 🔍 **How Dynamic Agents Work**

### **Flow:**
```
Frontend → langgraph.json → dynamic_agents.py → agent_factory.py → agents.json → Agent Created
```

### **Where They Get Their Logic:**

#### **1. Instructions (Prompts)**
Mapped by `agent_type` in `agent_factory.py`:

```python
# agent_factory.py line 260-270
def _get_default_instructions_for_type(self, agent_type: AgentType):
    instructions_map = {
        AgentType.GENERAL: MAIN_AGENT_INSTRUCTIONS,
        AgentType.RESEARCH: RESEARCH_AGENT_INSTRUCTIONS,
        AgentType.CODING: CODING_AGENT_INSTRUCTIONS,
        AgentType.CREATIVE: CREATIVE_AGENT_INSTRUCTIONS,
        AgentType.MEDICAL_RESEARCH: MEDICAL_RESEARCH_INSTRUCTIONS,
        AgentType.PYTHON_CODING: PYTHON_CODING_INSTRUCTIONS,
    }
    return instructions_map.get(agent_type, MAIN_AGENT_INSTRUCTIONS)
```

#### **2. Tools**
Auto-selected by `agent_type` in `agent_factory.py`:

```python
# agent_factory.py line 177-218
def _get_default_tools_for_type(self, agent_type: AgentType):
    base_tools = ["tavily_search", "perplexity_reasoning_search"]
    
    if agent_type == AgentType.RESEARCH:
        return base_tools + [
            "perplexity_focused_research",
            "academic_search",
            "deep_research",
            "sonar_deep_research"
        ]
    elif agent_type == AgentType.MEDICAL_RESEARCH:
        return base_tools + [
            "search_works",
            "scroll_export_works",
            "get_work_by_id",
            # ... CORE API tools
        ]
    # ... etc
```

#### **3. Subagents**
Auto-selected by `agent_type` in `agent_factory.py`:

```python
# agent_factory.py line 220-258
def _get_default_subagents_for_type(self, agent_type: AgentType):
    base_subagents = ["general_subagent"]
    
    if agent_type == AgentType.RESEARCH:
        return base_subagents + [
            "reasoning_subagent",
            "deep_research_subagent",
            "market_analysis_subagent",
            "technical_research_subagent"
        ]
    # ... etc
```

---

## 📋 **Current Agents in Backend**

### **From `langgraph.json`:**

| Agent ID | Type | System | Description |
|----------|------|--------|-------------|
| **main-agent** | Hardcoded | `agents.main_agent:agent` | General purpose with CustomSubAgent pattern |
| **research-agent** | Dynamic | `agents.dynamic_agents:research_agent` | Research specialist (type: `research`) |
| **code-assistant** | Dynamic | `agents.dynamic_agents:code_assistant` | Coding specialist (type: `coding`) |
| **content-creator** | Dynamic | `agents.dynamic_agents:content_creator` | Content creation (type: `creative`) |
| **medical-literature-agent** | Dynamic | `agents.dynamic_agents:medical_literature_agent` | Medical research (type: `medical_research`) |
| **python-coding-agent** | Dynamic | `agents.dynamic_agents:python_coding_agent` | Python specialist (type: `python_coding`) |
| **enhanced-main-agent** | Dynamic | `agents.dynamic_agents:enhanced_main_agent` | Memory-enhanced (type: `enhanced_general`) |
| **literature-review** | Hardcoded | `agents.literature_review:agent` | Literature review with citation verification |

---

## 🎯 **How Each Dynamic Agent Differs**

### **1. research-agent** (type: `research`)
**Tools:**
- Base: tavily_search, perplexity_reasoning_search
- Added: perplexity_focused_research, academic_search, deep_research, sonar_deep_research

**Subagents:**
- general_subagent
- reasoning_subagent
- deep_research_subagent
- market_analysis_subagent
- technical_research_subagent

**Instructions:** `RESEARCH_AGENT_INSTRUCTIONS`

### **2. code-assistant** (type: `coding`)
**Tools:**
- Base: tavily_search, perplexity_reasoning_search
- Added: technical_search, perplexity_focused_research

**Subagents:**
- general_subagent
- reasoning_subagent
- technical_research_subagent

**Instructions:** `CODING_AGENT_INSTRUCTIONS`

### **3. content-creator** (type: `creative`)
**Tools:**
- Base: tavily_search, perplexity_reasoning_search

**Subagents:**
- general_subagent
- reasoning_subagent

**Instructions:** `CREATIVE_AGENT_INSTRUCTIONS`

### **4. medical-literature-agent** (type: `medical_research`)
**Tools:**
- Base: tavily_search, perplexity_reasoning_search
- Added: ALL CORE API tools (search_works, get_work_by_id, etc.)
- Added: ALL literature tools (extract_paper_metadata, quality_assessment, etc.)

**Subagents:**
- general_subagent
- reasoning_subagent
- deep_research_subagent
- technical_research_subagent

**Instructions:** `MEDICAL_RESEARCH_INSTRUCTIONS`

### **5. python-coding-agent** (type: `python_coding`)
**Tools:**
- Base: tavily_search, perplexity_reasoning_search
- Added: technical_search, perplexity_focused_research

**Subagents:**
- general_subagent
- reasoning_subagent
- technical_research_subagent

**Instructions:** `PYTHON_CODING_INSTRUCTIONS`

### **6. enhanced-main-agent** (type: `enhanced_general`)
**Tools:** (Explicitly defined in agents.json)
- enhanced_write_file
- enhanced_read_file
- intelligent_file_search
- get_thread_memory_context
- get_shared_context_summary
- list_thread_files
- update_file_content

**Subagents:** (Explicitly defined in agents.json)
- general_subagent
- reasoning_subagent
- deep_research_subagent
- market_analysis_subagent
- technical_research_subagent

**Instructions:** Auto-selected for `enhanced_general` type

---

## 🔗 **Frontend Connection**

### **Before (Missing Agents):**
```typescript
// frontend/src/lib/agents/config.ts
export const AVAILABLE_AGENTS: Agent[] = [
  { id: "main-agent", ... },
  { id: "research-agent", ... },
  { id: "code-assistant", ... },
  { id: "content-creator", ... },
  { id: "literature-review", ... },
  // ❌ Missing: medical-literature-agent
  // ❌ Missing: python-coding-agent
  // ❌ Missing: enhanced-main-agent
];
```

### **After (All Agents Available):**
```typescript
// frontend/src/lib/agents/config.ts
export const AVAILABLE_AGENTS: Agent[] = [
  { id: "main-agent", name: "Main Agent", ... },
  { id: "research-agent", name: "Research Agent", ... },
  { id: "code-assistant", name: "Code Assistant", ... },
  { id: "content-creator", name: "Content Creator", ... },
  { id: "medical-literature-agent", name: "Medical Literature Agent", ... }, // ✅ Added
  { id: "python-coding-agent", name: "Python Coding Assistant", ... }, // ✅ Added
  { id: "enhanced-main-agent", name: "Enhanced Main Agent", ... }, // ✅ Added
  { id: "literature-review", name: "Literature Review Agent", ... }, // ✅ Fixed
];
```

---

## ✅ **What Was Fixed**

### **1. Literature Review Agent Routing**
**Problem:** Was using dynamic agent (outdated config)
**Solution:** Changed to hardcoded agent

```json
// langgraph.json
"literature-review": "agents.literature_review:agent"  // ✅ Now uses custom implementation
```

### **2. Frontend Agent List**
**Problem:** Missing 3 backend agents
**Solution:** Added all agents to `config.ts`

✅ Added: medical-literature-agent
✅ Added: python-coding-agent  
✅ Added: enhanced-main-agent
✅ Fixed: literature-review (updated description)

---

## 📊 **Comparison Table**

| Feature | Dynamic Agents | Hardcoded Agents |
|---------|---------------|------------------|
| **Configuration** | `agents.json` | Python file (`.py`) |
| **Instructions** | Auto-mapped by type | Explicitly imported |
| **Tools** | Auto-selected by type | Explicitly defined |
| **Subagents** | Auto-selected by type | Explicitly created |
| **Flexibility** | Limited to type logic | Full control |
| **Maintenance** | Update JSON + factory | Update Python file |
| **Best For** | Standard agent types | Custom specialized agents |
| **Examples** | research-agent, code-assistant | main-agent, literature-review |

---

## 🎯 **When to Use Each Approach**

### **Use Dynamic Agents When:**
- ✅ Agent fits a predefined type (research, coding, creative, etc.)
- ✅ Standard tool/subagent combinations work
- ✅ Want easy configuration via JSON
- ✅ Need multiple similar agents with slight variations

### **Use Hardcoded Agents When:**
- ✅ Need custom workflow (like literature review)
- ✅ Require specific tool combinations
- ✅ Need CustomSubAgent pattern
- ✅ Want full control over implementation
- ✅ Complex multi-step processes with specific requirements

---

## 🚀 **Current Status**

### ✅ **Backend:**
- 8 agents defined in `langgraph.json`
- 2 hardcoded (main-agent, literature-review)
- 6 dynamic (research, code, content, medical, python, enhanced)
- All properly configured

### ✅ **Frontend:**
- All 8 agents now available in UI
- Agent selector shows complete list
- Users can switch between all agents
- Literature review agent uses correct implementation

### ✅ **Literature Review Agent:**
- Uses hardcoded implementation
- Has correct prompt with file structures
- Has citation verification subagent
- Follows 8-step workflow
- Creates all 6 required files

---

## 📝 **Summary**

**Dynamic Agents:**
- Get logic from `agent_factory.py` based on `agent_type`
- Instructions mapped from `config/prompts.py`
- Tools auto-selected by type
- Subagents auto-selected by type
- Configured in `agents.json`

**Hardcoded Agents:**
- Get logic from their own `.py` files
- Everything explicitly defined
- Full control over behavior
- Best for specialized workflows

**Frontend:**
- Now shows ALL 8 backend agents
- Agent IDs must match `langgraph.json`
- Configuration in `frontend/src/lib/agents/config.ts`

All agents are now properly connected and available! 🎉
