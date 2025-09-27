# 🧠🤖 Deep Agents v1.1 – Multi-Agent Platform Guide

Deep Agents v1.1 introduces a full **multi-agent orchestration layer** on top of the classic Deep Agent architecture. You can now register, configure, and run multiple specialized agents side by side (e.g. research, coding, writing) while still taking advantage of recursive planning, subagent delegation, and the LangGraph runtime.

This document explains how to install the package, create agents using both **Dynamic Configuration** and **Hard-Coded File** approaches, register additional agents, wire them into LangGraph, connect the frontend selector, and manage them via the new Agent Registry and REST API.

## 🎯 **Agent Creation Methods Overview**

Deep Agents v1.1 supports **two distinct approaches** for creating specialized agents:

1. **🔄 Dynamic Configuration-Based Agents** - JSON-driven, runtime configurable
2. **📁 Hard-Coded File-Based Agents** - Explicit Python files with full control

Both approaches are valid and can be used simultaneously. Choose based on your needs:

| **Use Dynamic When** | **Use Hard-Coded When** |
|---------------------|------------------------|
| ✅ Rapid agent prototyping | ✅ Maximum control over agent behavior |
| ✅ Runtime configuration changes | ✅ Complex agent-specific initialization |
| ✅ Multi-tenant systems | ✅ Production systems with specific requirements |
| ✅ Non-technical team members need to create agents | ✅ Explicit dependency management |

---

## 📦 Installation

```bash
pip install deepagents
```

All improvements are fully backward compatible with existing single-agent projects. Multi-agent support becomes active when you add extra agent configurations (see the next sections).

---

## 🔄 **Method 1: Dynamic Configuration-Based Agents**

### **How Dynamic Agents Work**

Dynamic agents are created through **JSON configuration** and **factory logic**. The `AgentFactory` reads agent configurations from `agents.json` and dynamically assigns tools, subagents, and prompts based on the `agent_type` field.

### **Step-by-Step: Creating Dynamic Agents**

#### **Step 1: Add Agent Configuration to `agents.json`**

```json
{
  "id": "medical-literature-agent",
  "name": "Medical Literature Review Agent", 
  "description": "Specialized agent for medical literature search, filtering, review, and analysis",
  "agent_type": "medical_research",
  "color": "#DC2626",
  "icon": "🏥",
  "instructions": "You are a medical literature review specialist with expertise in systematic reviews, meta-analyses, and evidence-based medicine.",
  "tools": [],        // Empty = use defaults for agent_type
  "subagents": [],    // Empty = use defaults for agent_type
  "model_config": null,
  "recursion_limit": 100,
  "enabled": true
}
```

#### **Step 2: Add New Agent Type to Enum**

**File: `backend/config/agent_registry.py`**

```python
class AgentType(Enum):
    """Predefined agent types with specific capabilities."""
    GENERAL = "general"
    RESEARCH = "research"
    CODING = "coding"
    CREATIVE = "creative"
    MEDICAL_RESEARCH = "medical_research"  # Add new type
    PYTHON_CODING = "python_coding"        # Add new type
```

#### **Step 3: Add Dynamic Tool Assignment Logic**

**File: `backend/agents/agent_factory.py`**

```python
def _get_default_tools_for_type(self, agent_type: AgentType) -> List[str]:
    """Get default tools for a specific agent type."""
    base_tools = ["get_active_subagents", "get_subagent_summary"]
    
    if agent_type == AgentType.MEDICAL_RESEARCH:
        return base_tools + [
            # Medical literature search tools
            "academic_search",
            "deep_research", 
            "sonar_deep_research",
            # CORE API tools for medical literature
            "search_works",
            "scroll_export_works",
            "get_work_by_id",
            "batch_get_works_by_ids",
            "aggregate_works",
            "time_trend_analysis",
            "search_journals",
            "get_journal_by_id",
            "analyze_top_venues_for_topic"
        ]
    elif agent_type == AgentType.PYTHON_CODING:
        return base_tools + [
            # Python-focused development tools
            "tavily_search",
            "technical_search",
            "perplexity_focused_research"
        ]
    # ... other agent types
```

#### **Step 4: Add Subagent Assignment Logic**

```python
def _get_default_subagents_for_type(self, agent_type: AgentType) -> List[str]:
    """Get default subagents for a specific agent type."""
    base_subagents = ["general_subagent"]
    
    if agent_type == AgentType.MEDICAL_RESEARCH:
        return base_subagents + [
            "reasoning_subagent",
            "deep_research_subagent", 
            "technical_research_subagent"
            # Note: CORE research subagents added automatically
        ]
    elif agent_type == AgentType.PYTHON_CODING:
        return base_subagents + [
            "reasoning_subagent",
            "technical_research_subagent"
        ]
    # ... other agent types
```

#### **Step 5: Add Specialized Prompts**

**File: `backend/config/prompts.py`**

```python
MEDICAL_RESEARCH_INSTRUCTIONS = """You are a specialized medical literature review agent with expertise in evidence-based medicine, systematic reviews, and medical research analysis.

Core Medical Research Capabilities:
- Medical literature search and discovery using CORE API and academic databases
- Systematic literature reviews following PRISMA guidelines
- Meta-analysis data extraction and synthesis
- Medical research quality assessment and bias evaluation
- Evidence grading and clinical significance analysis
- Medical terminology and clinical context understanding

Medical Research Methodology:
1. Systematic search strategy development with medical subject headings (MeSH)
2. Literature screening using inclusion/exclusion criteria
3. Quality assessment using appropriate tools (Cochrane Risk of Bias, Newcastle-Ottawa Scale)
4. Data extraction with focus on clinical outcomes and statistical measures
5. Evidence synthesis with consideration of heterogeneity and clinical relevance
6. GRADE evidence assessment for clinical recommendations

Always prioritize peer-reviewed medical literature, maintain rigorous evidence standards, follow medical research ethics, and provide clinically relevant insights with proper medical terminology and context."""

PYTHON_CODING_INSTRUCTIONS = """You are a specialized Python development assistant with deep expertise in Python programming, best practices, and the Python ecosystem.

Core Python Development Capabilities:
- Python code analysis, review, and optimization
- Debugging and troubleshooting Python applications
- Python library and framework guidance (Django, Flask, FastAPI, etc.)
- Data science and machine learning with Python (pandas, numpy, scikit-learn, etc.)
- Python testing strategies (pytest, unittest, coverage)
- Code quality and maintainability assessment

Always provide Pythonic solutions, follow PEP standards, emphasize readability and maintainability, include proper error handling, and suggest appropriate libraries and tools for the specific use case."""
```

#### **Step 6: Update Factory Instructions Mapping**

**File: `backend/agents/agent_factory.py`**

```python
from config.prompts import (
    MAIN_AGENT_INSTRUCTIONS,
    RESEARCH_AGENT_INSTRUCTIONS,
    CODING_AGENT_INSTRUCTIONS,
    CREATIVE_AGENT_INSTRUCTIONS,
    MEDICAL_RESEARCH_INSTRUCTIONS,
    PYTHON_CODING_INSTRUCTIONS
)

def _get_default_instructions_for_type(self, agent_type: AgentType) -> str:
    """Get default instructions for a specific agent type."""
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

#### **Step 7: Update LangGraph Configuration**

**File: `backend/langgraph.json`**

```json
{
  "dependencies": ["."],
  "graphs": {
    "main-agent": "agents.dynamic_agents:main_agent",
    "research-agent": "agents.dynamic_agents:research_agent",
    "code-assistant": "agents.dynamic_agents:code_assistant", 
    "content-creator": "agents.dynamic_agents:content_creator",
    "medical-literature-agent": "agents.dynamic_agents:medical_literature_agent",
    "python-coding-agent": "agents.dynamic_agents:python_coding_agent"
  },
  "env": ".env"
}
```

#### **Step 8: Update Dynamic Agents Module**

**File: `backend/agents/dynamic_agents.py`**

```python
"""
Dynamic Agents Module - Auto-generated agent instances.
Uses the configuration-based approach for reliable agent creation.
"""

from agents.agent_factory import create_agent_by_id

# Main Agent - General purpose AI agent for complex tasks
main_agent = create_agent_by_id("main-agent")

# Research Agent - Specialized agent for research and data analysis
research_agent = create_agent_by_id("research-agent")

# Code Assistant - Specialized agent for coding and development tasks
code_assistant = create_agent_by_id("code-assistant")

# Content Creator - Agent for writing and content creation tasks
content_creator = create_agent_by_id("content-creator")

# Medical Literature Agent - Specialized agent for medical literature review
medical_literature_agent = create_agent_by_id("medical-literature-agent")

# Python Coding Agent - Specialized Python development assistant
python_coding_agent = create_agent_by_id("python-coding-agent")
```

### **Dynamic Agent Creation Process**

When you call `create_agent_by_id("medical-literature-agent")`:

1. **Factory reads `agents.json`** → finds `agent_type: "medical_research"`
2. **`tools: []` is empty** → calls `_get_default_tools_for_type("medical_research")`
3. **Returns**: `["academic_search", "deep_research", "search_works", ...]`
4. **`subagents: []` is empty** → calls `_get_default_subagents_for_type("medical_research")`
5. **Returns**: `["reasoning_subagent", "deep_research_subagent", ...]`
6. **`instructions: ""` uses** → `_get_default_instructions_for_type("medical_research")`
7. **Returns**: `MEDICAL_RESEARCH_INSTRUCTIONS`
8. **Creates agent** with: `tools + subagents + instructions`

---

## 📁 **Method 2: Hard-Coded File-Based Agents**

### **How Hard-Coded Agents Work**

Hard-coded agents are created through **dedicated Python files** where you explicitly import tools, define subagents, and configure every aspect of the agent. Each agent has its own `.py` file with complete control over its implementation.

### **Step-by-Step: Creating Hard-Coded Agents**

#### **Step 1: Create Agent File**

**File: `backend/agents/medical_research_agent.py`**

```python
"""
Medical Research Agent implementation using the deep agents framework.
Specialized for medical literature review, systematic reviews, and evidence-based medicine.
"""

import os
from typing import Literal, Any
from src.deepagents import create_deep_agent
from src.deepagents.sub_agent import SubAgent

# Import medical research-focused tools
from tools.search.perplexity import perplexity_reasoning_search, perplexity_focused_research
from tools.search.perplexity_strategies import academic_search, technical_search, deep_research
from tools.search.sonar_deep_research import sonar_deep_research

# Import CORE API tools (primary medical research tools)
from tools.core_api import (
    search_works,
    scroll_export_works,
    get_work_by_id,
    batch_get_works_by_ids,
    aggregate_works,
    time_trend_analysis,
    search_journals,
    get_journal_by_id,
    analyze_top_venues_for_topic
)

# Import utility tools
from tools.subagent_tracker import get_active_subagents, get_subagent_summary

# Import medical research-focused subagent creators
from subagents.general_agent import create_general_subagent
from subagents.reasoning_agent import create_reasoning_subagent
from subagents.deep_research_agent import create_deep_research_agent
from subagents.technical_research_agent import create_technical_research_agent
from subagents.core_research_subagents import get_all_core_research_subagents

# Import configuration
from config.prompts import MEDICAL_RESEARCH_INSTRUCTIONS
from config.settings import get_settings

# Import model configuration
from models import get_default_model


def create_medical_research_agent():
    """Create a medical research deep agent with specialized tools and subagents."""
    
    # Get application settings
    settings = get_settings()
    
    # Create medical research-focused subagents
    general_subagent = create_general_subagent()
    reasoning_subagent = create_reasoning_subagent()
    deep_research_subagent = create_deep_research_agent()
    technical_research_subagent = create_technical_research_agent()
    
    # Get all CORE API research subagents (essential for medical research)
    core_research_subagents = get_all_core_research_subagents()
    
    # Get the default model with fallback
    model = get_default_model()
    
    # Create the medical research deep agent with specialized tools
    agent = create_deep_agent(
        tools=[
            # Perplexity medical research tools
            perplexity_reasoning_search,
            perplexity_focused_research,
            # Advanced medical research strategy tools
            academic_search,
            technical_search,
            deep_research,
            # Elite sonar deep research tool
            sonar_deep_research,
            # CORE API tools for medical literature (primary focus)
            search_works,
            scroll_export_works,
            get_work_by_id,
            batch_get_works_by_ids,
            aggregate_works,
            time_trend_analysis,
            search_journals,
            get_journal_by_id,
            analyze_top_venues_for_topic,
            # Utility tools for task and subagent management
            get_active_subagents,
            get_subagent_summary
        ],
        instructions=MEDICAL_RESEARCH_INSTRUCTIONS,
        subagents=[
            general_subagent,
            reasoning_subagent,
            deep_research_subagent,
            technical_research_subagent
        ] + core_research_subagents,  # Add all CORE research subagents
        model=model,
        builtin_tools=None,  # Use all built-in tools
        interrupt_config={
            # Require approval for expensive research operations
            "sonar_deep_research": True,
            "scroll_export_works": True,
        }
    ).with_config({"recursion_limit": settings["recursion_limit"]})
    
    return agent


# Create the agent instance (used by dynamic_agents.py)
agent = create_medical_research_agent()
```

#### **Step 2: Create Python Coding Agent File**

**File: `backend/agents/python_coding_agent.py`**

```python
"""
Python Coding Agent implementation using the deep agents framework.
Specialized for Python development, debugging, and best practices.
"""

import os
from typing import Literal, Any
from src.deepagents import create_deep_agent
from src.deepagents.sub_agent import SubAgent

# Import Python coding-focused tools
from tools.search.tavily_search import tavily_search, tavily_qna_search
from tools.search.perplexity import perplexity_focused_research
from tools.search.perplexity_strategies import technical_search

# Import utility tools
from tools.subagent_tracker import get_active_subagents, get_subagent_summary

# Import coding-focused subagent creators
from subagents.general_agent import create_general_subagent
from subagents.reasoning_agent import create_reasoning_subagent
from subagents.technical_research_agent import create_technical_research_agent

# Import configuration
from config.prompts import PYTHON_CODING_INSTRUCTIONS
from config.settings import get_settings

# Import model configuration
from models import get_default_model


def create_python_coding_agent():
    """Create a Python coding deep agent with specialized tools and subagents."""
    
    # Get application settings
    settings = get_settings()
    
    # Create coding-focused subagents
    general_subagent = create_general_subagent()
    reasoning_subagent = create_reasoning_subagent()
    technical_research_subagent = create_technical_research_agent()
    
    # Get the default model with fallback
    model = get_default_model()
    
    # Create the Python coding deep agent with development-optimized tools
    agent = create_deep_agent(
        tools=[
            # General web search for documentation and solutions
            tavily_search,
            tavily_qna_search,
            # Focused research for technical documentation
            perplexity_focused_research,
            # Technical search for Python-specific queries
            technical_search,
            # Utility tools for task and subagent management
            get_active_subagents,
            get_subagent_summary
        ],
        instructions=PYTHON_CODING_INSTRUCTIONS,
        subagents=[
            general_subagent,
            reasoning_subagent,
            technical_research_subagent
        ],
        model=model,
        builtin_tools=None,  # Use all built-in tools (file operations essential for coding)
        interrupt_config=None  # No interrupts needed for coding tasks
    ).with_config({"recursion_limit": settings["recursion_limit"]})
    
    return agent


# Create the agent instance (used by dynamic_agents.py)
agent = create_python_coding_agent()
```

#### **Step 3: Update Dynamic Agents Module for Hard-Coded**

**File: `backend/agents/dynamic_agents.py`**

```python
"""
Dynamic Agents Module - Specialized agent instances.
This module imports specialized agent implementations for the multi-agent system.
Each agent is optimized for its specific domain with tailored tools and subagents.
"""

# Import specialized agent implementations
from agents.main_agent import create_main_agent
from agents.research_agent import create_research_agent
from agents.code_assistant import create_code_assistant
from agents.content_creator import create_content_creator
from agents.medical_research_agent import create_medical_research_agent
from agents.python_coding_agent import create_python_coding_agent

# Main Agent - General purpose AI agent for complex tasks
main_agent = create_main_agent()

# Research Agent - Specialized agent for research and data analysis
research_agent = create_research_agent()

# Code Assistant - Specialized agent for coding and development tasks
code_assistant = create_code_assistant()

# Content Creator - Agent for writing and content creation tasks
content_creator = create_content_creator()

# Medical Research Agent - Specialized agent for medical literature review
medical_research_agent = create_medical_research_agent()

# Python Coding Agent - Specialized Python development assistant
python_coding_agent = create_python_coding_agent()
```

#### **Step 4: Update LangGraph Configuration**

**File: `backend/langgraph.json`**

```json
{
  "dependencies": ["."],
  "graphs": {
    "main-agent": "agents.dynamic_agents:main_agent",
    "research-agent": "agents.dynamic_agents:research_agent",
    "code-assistant": "agents.dynamic_agents:code_assistant",
    "content-creator": "agents.dynamic_agents:content_creator",
    "medical-research-agent": "agents.dynamic_agents:medical_research_agent",
    "python-coding-agent": "agents.dynamic_agents:python_coding_agent"
  },
  "env": ".env"
}
```

### **Hard-Coded Agent Benefits**

- ✅ **Complete Control**: Fine-tune every aspect of agent behavior
- ✅ **Agent-Specific Logic**: Custom initialization and configuration per agent
- ✅ **Explicit Dependencies**: Clear imports and tool assignments
- ✅ **Type Safety**: Compile-time validation of tool availability
- ✅ **Easier Debugging**: Direct code inspection and debugging
- ✅ **Custom Interrupt Config**: Agent-specific human-in-the-loop settings

---

## ⚙️ Core Concepts (v1.1 Additions)

- **Agent Registry (`backend/config/agent_registry.py`)** – Central source of truth for all agent definitions. Stores metadata (name, description, color, icon), instructions, tool assignments, model overrides, and recursion limits. Reads/writes `backend/config/agents.json`.
- **Agent Factory (`backend/agents/agent_factory.py`)** – Dynamically constructs agents by combining registry settings, tools, and subagents. Automatically discovers available tool and subagent creators from `backend/tools/` and `backend/subagents/`.
- **LangGraph Generator (`backend/utils/langgraph_generator.py`)** – Produces `langgraph.json` and `agents/dynamic_agents.py` from the registry, so every configured agent is available over the LangGraph server.
- **Agent Management API (`backend/agents/api_endpoints.py`)** – FastAPI blueprint providing CRUD endpoints, status checks, and config regeneration for agents.
- **Frontend Multi-Agent UX** – Includes `AgentSelector`, agent-scoped thread management, and per-agent contexts in `frontend/` (see Frontend Integration).

These components unlock editing, creating, or deleting agents without touching core framework code.

---

## 🚀 Quick Start: Spinning Up Multiple Agents

### **Option A: Using Dynamic Configuration Approach**

1. **Install & configure** dependencies (Python + Node) and ensure `backend/.env` / `frontend/.env.local` are set.
2. **Register agents** in `backend/config/agents.json` (see Dynamic Method above).
3. **Update `backend/agents/dynamic_agents.py`** to use `create_agent_by_id()`:
   ```python
   from agents.agent_factory import create_agent_by_id
   
   main_agent = create_agent_by_id("main-agent")
   research_agent = create_agent_by_id("research-agent")
   # ... other agents
   ```
4. **Launch LangGraph server**: `langgraph dev`
5. **Run frontend** (Next.js) – the Agent Selector will list all enabled agents.

### **Option B: Using Hard-Coded File Approach**

1. **Install & configure** dependencies (Python + Node) and ensure `backend/.env` / `frontend/.env.local` are set.
2. **Create agent files** in `backend/agents/` (see Hard-Coded Method above).
3. **Update `backend/agents/dynamic_agents.py`** to import agent creators:
   ```python
   from agents.main_agent import create_main_agent
   from agents.research_agent import create_research_agent
   # ... other agent imports
   
   main_agent = create_main_agent()
   research_agent = create_research_agent()
   # ... other agent instances
   ```
4. **Update `backend/langgraph.json`** with new agent mappings.
5. **Launch LangGraph server**: `langgraph dev`
6. **Run frontend** (Next.js) – the Agent Selector will list all enabled agents.

---

## 🧠 **Deep Agents Core Architecture (From v1.0)**

Deep Agents v1.1 builds upon the proven **Deep Agent architecture** from v1.0. Understanding these core concepts is essential for creating effective agents.

### **What Makes an Agent "Deep"?**

Using an LLM to call tools in a loop is the simplest form of an agent. This architecture, however, can yield agents that are "shallow" and fail to plan and act over longer, more complex tasks. Applications like "Deep Research", "Manus", and "Claude Code" have gotten around this limitation by implementing a combination of four things: a **planning tool**, **sub agents**, access to a **file system**, and a **detailed prompt**.

Deep Agents implements these in a general purpose way so that you can easily create a Deep Agent for your application.

### **Core Deep Agent Components**

#### **1. System Prompt**

Deep Agents comes with a [built-in system prompt](src/deepagents/prompts.py). This is a relatively detailed prompt that is heavily based on and inspired by attempts to replicate Claude Code's system prompt. It was made more general purpose than Claude Code's system prompt.

This contains detailed instructions for how to use the built-in planning tool, file system tools, and sub agents. Note that part of this system prompt can be customized via the `instructions` parameter.

**Without this default system prompt - the agent would not be nearly as successful.** The importance of prompting for creating a "deep" agent cannot be understated.

#### **2. Planning Tool**

Deep Agents comes with a built-in planning tool (`write_todos`). This planning tool is very simple and is based on ClaudeCode's TodoWrite tool. This tool doesn't actually do anything - it is just a way for the agent to come up with a plan, and then have that in the context to help keep it on track.

#### **3. File System Tools**

Deep Agents comes with four built-in file system tools: `ls`, `edit_file`, `read_file`, `write_file`. These do not actually use a file system - rather, they mock out a file system using LangGraph's State object. This means you can easily run many of these agents on the same machine without worrying that they will edit the same underlying files.

Right now the "file system" will only be one level deep (no sub directories).

These files can be passed in (and also retrieved) by using the `files` key in the LangGraph State object.

```python
agent = create_deep_agent(...)

result = agent.invoke({
    "messages": ...,
    # Pass in files to the agent using this key
    # "files": {"foo.txt": "foo", ...}
})

# Access any files afterwards like this
result["files"]
```

#### **4. Sub Agents**

Deep Agents comes with the built-in ability to call sub agents (based on Claude Code). It has access to a `general-purpose` subagent at all times - this is a subagent with the same instructions as the main agent and all the tools that it has access to.

You can also specify custom sub agents with their own instructions and tools.

Sub agents are useful for ["context quarantine"](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#context-quarantine) (to help not pollute the overall context of the main agent) as well as custom instructions.

### **Built-In Tools**

By default, deep agents come with five built-in tools:

- `write_todos`: Tool for writing todos
- `write_file`: Tool for writing to a file in the virtual filesystem
- `read_file`: Tool for reading from a file in the virtual filesystem
- `ls`: Tool for listing files in the virtual filesystem
- `edit_file`: Tool for editing a file in the virtual filesystem

These can be disabled via the `builtin_tools` parameter.

### **Creating Custom Deep Agents**

There are several parameters you can pass to `create_deep_agent` to create your own custom deep agent:

#### **`tools` (Required)**

The first argument to `create_deep_agent` is `tools`. This should be a list of functions or LangChain `@tool` objects. The agent (and any subagents) will have access to these tools.

#### **`instructions` (Required)**

The second argument to `create_deep_agent` is `instructions`. This will serve as part of the prompt of the deep agent. Note that there is a built-in system prompt as well, so this is not the *entire* prompt the agent will see.

#### **`subagents` (Optional)**

A keyword-only argument to `create_deep_agent` is `subagents`. This can be used to specify any custom subagents this deep agent will have access to.

`subagents` should be a list of dictionaries, where each dictionary follows this schema:

```python
class SubAgent(TypedDict):
    name: str
    description: str
    prompt: str
    tools: NotRequired[list[str]]
    model_settings: NotRequired[dict[str, Any]]

class CustomSubAgent(TypedDict):
    name: str
    description: str
    graph: Runnable
```

**SubAgent fields:**
- **name**: This is the name of the subagent, and how the main agent will call the subagent
- **description**: This is the description of the subagent that is shown to the main agent
- **prompt**: This is the prompt used for the subagent
- **tools**: This is the list of tools that the subagent has access to. By default will have access to all tools passed in, as well as all built-in tools.
- **model_settings**: Optional dictionary for per-subagent model configuration (inherits the main model when omitted).

**CustomSubAgent fields:**
- **name**: This is the name of the subagent, and how the main agent will call the subagent
- **description**: This is the description of the subagent that is shown to the main agent  
- **graph**: A pre-built LangGraph graph/agent that will be used as the subagent

#### **Using SubAgent**

```python
research_subagent = {
    "name": "research-agent",
    "description": "Used to research more in depth questions",
    "prompt": sub_research_prompt,
}
subagents = [research_subagent]
agent = create_deep_agent(
    tools,
    prompt,
    subagents=subagents
)
```

#### **Using CustomSubAgent**

For more complex use cases, you can provide your own pre-built LangGraph graph as a subagent:

```python
from langgraph.prebuilt import create_react_agent

# Create a custom agent graph
custom_graph = create_react_agent(
    model=your_model,
    tools=specialized_tools,
    prompt="You are a specialized agent for data analysis..."
)

# Use it as a custom subagent
custom_subagent = {
    "name": "data-analyzer",
    "description": "Specialized agent for complex data analysis tasks",
    "graph": custom_graph
}

subagents = [custom_subagent]
agent = create_deep_agent(
    tools,
    prompt,
    subagents=subagents
)
```

#### **`model` (Optional)**

By default, Deep Agents uses `"claude-sonnet-4-20250514"`. You can customize this by passing any [LangChain model object](https://python.langchain.com/docs/integrations/chat/).

#### **`builtin_tools` (Optional)**

By default, a deep agent will have access to the built-in tools listed above. You can change this by specifying the tools (by name) that the agent should have access to with this parameter.

Example:
```python
# Only give agent access to todo tool, none of the filesystem tools
builtin_tools = ["write_todos"]
agent = create_deep_agent(..., builtin_tools=builtin_tools, ...)
```

#### **Example: Using a Custom Model**

Here's how to use a custom model (like OpenAI's `gpt-oss` model via Ollama):

```python
from deepagents import create_deep_agent
from langchain_core.language_models import init_chat_model

model = init_chat_model(
    model="ollama:gpt-oss:20b",  
)
agent = create_deep_agent(
    tools=tools,
    instructions=instructions,
    model=model,
    ...
)
```

#### **Example: Per-subagent model override**

Use a fast, deterministic model for a critique sub-agent, while keeping a different default model for the main agent and others:

```python
from deepagents import create_deep_agent

critique_sub_agent = {
    "name": "critique-agent",
    "description": "Critique the final report",
    "prompt": "You are a tough editor.",
    "model_settings": {
        "model": "anthropic:claude-3-5-haiku-20241022",
        "temperature": 0,
        "max_tokens": 8192
    }
}

agent = create_deep_agent(
    tools=[internet_search],
    instructions="You are an expert researcher...",
    model="claude-sonnet-4-20250514",  # default for main agent and other sub-agents
    subagents=[critique_sub_agent],
)
```

### **Human-in-the-Loop**

Deep Agents supports human-in-the-loop approval for tool execution. You can configure specific tools to require human approval before execution using the `interrupt_config` parameter, which maps tool names to `HumanInterruptConfig`.

`HumanInterruptConfig` is how you specify what type of human in the loop patterns are supported. It is a dictionary with four specific keys:

- `allow_ignore`: Whether the user can skip the tool call
- `allow_respond`: Whether the user can add a text response
- `allow_edit`: Whether the user can edit the tool arguments
- `allow_accept`: Whether the user can accept the tool call

Currently, Deep Agents does NOT support `allow_ignore`. Currently, Deep Agents only support interrupting one tool at a time. If multiple tools are called in parallel, each requiring interrupts, then the agent will error.

Instead of specifying a `HumanInterruptConfig` for a tool, you can also just set `True`. This will set `allow_ignore`, `allow_respond`, `allow_edit`, and `allow_accept` to be `True`.

In order to use human in the loop, you need to have a checkpointer attached. Note: if you are using LangGraph Platform, this is automatically attached.

Example usage:

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

# Create agent with file operations requiring approval
agent = create_deep_agent(
    tools=[your_tools],
    instructions="Your instructions here",
    interrupt_config={
        # You can specify a dictionary for fine grained control over what interrupt options exist
        "tool_1": {
            "allow_ignore": False,
            "allow_respond": True,
            "allow_edit": True,
            "allow_accept":True,
        },
        # You can specify a boolean for shortcut
        # This is a shortcut for the same functionality as above
        "tool_2": True,
    }
)

checkpointer= InMemorySaver()
agent.checkpointer = checkpointer
```

### **Async Support**

If you are passing async tools to your agent, you will want to use:

```python
from deepagents import async_create_deep_agent
```

### **MCP Integration**

The Deep Agents library can be run with MCP tools. This can be achieved by using the [Langchain MCP Adapter library](https://github.com/langchain-ai/langchain-mcp-adapters).

**NOTE:** You'll want to use `async_create_deep_agent` to use the async version of Deep Agents, since MCP tools are async.

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import async_create_deep_agent

async def main():
    # Collect MCP tools
    mcp_client = MultiServerMCPClient(...)
    mcp_tools = await mcp_client.get_tools()

    # Create agent
    agent = async_create_deep_agent(tools=mcp_tools, ....)

    # Stream the agent
    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": "what is langgraph?"}]},
        stream_mode="values"
    ):
        if "messages" in chunk:
            chunk["messages"][-1].pretty_print()

asyncio.run(main())
```

### **Configurable Agent**

Configurable agents allow you to control the agent via a config passed in.

```python
from deepagents import create_configurable_agent

agent_config = {"instructions": "foo", "subagents": []}

build_agent = create_configurable_agent(
    agent_config['instructions'],
    agent_config['subagents'],
    [],
    agent_config={"recursion_limit": 1000}
)
```

You can now use `build_agent` in your `langgraph.json` and deploy it with `langgraph dev`.

For async tools, you can use `from deepagents import async_create_configurable_agent`.

---

## 🎯 **Choosing Between Dynamic vs Hard-Coded Approaches**

### **Decision Matrix**

| **Criteria** | **Dynamic Configuration** | **Hard-Coded Files** | **Recommendation** |
|--------------|--------------------------|---------------------|-------------------|
| **Development Speed** | ⭐⭐⭐⭐⭐ Fast (JSON only) | ⭐⭐⭐ Moderate (Python files) | Dynamic for rapid prototyping |
| **Control & Flexibility** | ⭐⭐⭐ Limited to factory patterns | ⭐⭐⭐⭐⭐ Complete control | Hard-coded for complex agents |
| **Runtime Changes** | ⭐⭐⭐⭐⭐ Edit JSON, restart | ⭐⭐ Requires code deployment | Dynamic for configurable systems |
| **Debugging** | ⭐⭐ Harder to trace | ⭐⭐⭐⭐⭐ Direct code inspection | Hard-coded for production |
| **Team Collaboration** | ⭐⭐⭐⭐ Non-technical can contribute | ⭐⭐⭐ Requires Python knowledge | Dynamic for mixed teams |
| **Type Safety** | ⭐⭐ Runtime validation only | ⭐⭐⭐⭐⭐ Compile-time validation | Hard-coded for reliability |
| **Maintenance** | ⭐⭐⭐⭐ Centralized logic | ⭐⭐⭐ Distributed across files | Dynamic for consistency |
| **Performance** | ⭐⭐⭐ Factory overhead | ⭐⭐⭐⭐⭐ Direct instantiation | Hard-coded for performance |

### **Use Cases by Approach**

#### **🔄 Choose Dynamic Configuration When:**
- **Rapid Agent Development**: Need to create multiple agents quickly
- **Multi-Tenant Systems**: Different users need different agent configurations
- **A/B Testing**: Want to experiment with different tool combinations
- **Non-Technical Teams**: Content creators or domain experts need to create agents
- **Standardized Patterns**: Agents follow predictable patterns (research, coding, creative)
- **Runtime Flexibility**: Need to modify agent capabilities without redeployment

#### **📁 Choose Hard-Coded Files When:**
- **Production Systems**: Need maximum reliability and performance
- **Complex Agent Logic**: Require custom initialization, validation, or error handling
- **Agent-Specific Features**: Each agent needs unique interrupt configs, model settings, or tool combinations
- **Type Safety Requirements**: Want compile-time validation and IDE support
- **Performance Critical**: Need minimal overhead and direct control
- **Debugging Requirements**: Need clear code paths for troubleshooting

### **Hybrid Approach**

You can also **combine both approaches**:

```python
# In dynamic_agents.py
from agents.agent_factory import create_agent_by_id
from agents.specialized_medical_agent import create_specialized_medical_agent

# Dynamic agents for standard patterns
main_agent = create_agent_by_id("main-agent")
research_agent = create_agent_by_id("research-agent")

# Hard-coded agents for complex specialized logic
specialized_medical_agent = create_specialized_medical_agent()
```

---

## 🧱 Step-by-Step: Adding Another Agent

### **🚨 CRITICAL: File Persistence Requirements**

**ALL agents, subagents, and tools MUST include persistent checkpointer support for file persistence to work correctly.**

#### **For ALL Agent Creation Methods:**

**✅ MANDATORY: Every agent MUST use persistent checkpointer**
```python
from config.checkpointer import get_default_checkpointer

# For create_deep_agent() calls
agent = create_deep_agent(
    tools=tools,
    instructions=instructions,
    subagents=subagents,
    model=model,
    checkpointer=get_default_checkpointer(),  # ← REQUIRED FOR FILE PERSISTENCE
    # ... other parameters
)

# For agent factory (automatic)
agent = create_agent_by_id("agent-id")  # ← Checkpointer added automatically
```

**⚠️ WITHOUT CHECKPOINTER: Files created by agents, subagents, and tools will disappear on server restart!**

**🔧 Why This Is Critical:**
- **Main agents**: Need checkpointer to persist files they create directly
- **Subagents**: Inherit checkpointer from main agent automatically (framework handles this)
- **Tools with large outputs**: Use `@handle_large_response` decorator - files persist via shared state
- **Built-in file tools**: `write_file`, `edit_file`, `read_file`, `ls` all use persistent state

### **For Dynamic Configuration Approach:**

1. **Decide on new capabilities**
   - Add specialized prompts to `backend/config/prompts.py`
   - Create any new tools under `backend/tools/` (decorate with `@tool` and `@handle_large_response` when applicable)
   - Add new subagent creators in `backend/subagents/` if specialization is required

2. **Add agent type to enum**
   - Update `AgentType` enum in `backend/config/agent_registry.py`

3. **Configure factory logic**
   - Add tool assignment logic in `AgentFactory._get_default_tools_for_type()`
   - Add subagent assignment logic in `AgentFactory._get_default_subagents_for_type()`
   - Add instruction mapping in `AgentFactory._get_default_instructions_for_type()`

4. **Register the agent**
   - Add entry to `backend/config/agents.json` with new `agent_type`
   - Set `tools`/`subagents` to empty arrays to use factory defaults

5. **Update runtime configuration**
   - Add agent to `backend/langgraph.json` graphs mapping
   - Add agent instance to `backend/agents/dynamic_agents.py`

6. **Restart services**
   - Restart LangGraph server to pick up new configuration
   - Update frontend agent selector if needed

### **For Hard-Coded File Approach:**

1. **Decide on new capabilities**
   - Add specialized prompts to `backend/config/prompts.py`
   - Create any new tools under `backend/tools/` (decorate with `@tool` and `@handle_large_response` when applicable)
   - Add new subagent creators in `backend/subagents/` if specialization is required

2. **Create agent file**
   - Create new file in `backend/agents/` (e.g., `medical_research_agent.py`)
   - **✅ MANDATORY**: Import checkpointer: `from config.checkpointer import get_default_checkpointer`
   - **✅ MANDATORY**: Add checkpointer to `create_deep_agent()`: `checkpointer=get_default_checkpointer()`
   - Implement `create_[agent_name]_agent()` function
   - Explicitly import and configure all tools, subagents, and settings

3. **Update dynamic agents module**
   - Import agent creator in `backend/agents/dynamic_agents.py`
   - Create agent instance and export it

4. **Update LangGraph configuration**
   - Add agent to `backend/langgraph.json` graphs mapping

5. **Restart services**
   - Restart LangGraph server to pick up new agent
   - Update frontend agent selector if needed

6. **Test the new agent**
   - Verify agent appears in frontend dropdown
   - Test agent functionality and tool access
   - Check subagent spawning and specialized behavior

---

## 📋 **Files Modified Summary**

### **Dynamic Configuration Approach Files:**

| **File** | **Purpose** | **Changes Required** |
|----------|-------------|---------------------|
| `backend/config/agent_registry.py` | Agent type definitions | Add new `AgentType` enum values |
| `backend/config/agents.json` | Agent configurations | Add new agent entries with `agent_type` |
| `backend/config/prompts.py` | Specialized instructions | Add agent-specific instruction prompts |
| `backend/agents/agent_factory.py` | Dynamic assignment logic | Add tool/subagent/instruction mappings |
| `backend/agents/dynamic_agents.py` | Agent instances | Add `create_agent_by_id()` calls |
| `backend/langgraph.json` | LangGraph routing | Add agent ID to graphs mapping |

### **Hard-Coded File Approach Files:**

| **File** | **Purpose** | **Changes Required** |
|----------|-------------|---------------------|
| `backend/config/prompts.py` | Specialized instructions | Add agent-specific instruction prompts |
| `backend/agents/[agent_name].py` | Agent implementation | Create new agent file with explicit configuration |
| `backend/agents/dynamic_agents.py` | Agent instances | Import and instantiate agent creators |
| `backend/langgraph.json` | LangGraph routing | Add agent ID to graphs mapping |

---

## ✅ **Troubleshooting & Tips**

### **File Persistence Issues**

**❌ Problem**: Files disappear after server restart
**✅ Solution**: Ensure checkpointer is configured:
```python
# Check if your agent has checkpointer
from config.checkpointer import get_default_checkpointer
agent = create_deep_agent(..., checkpointer=get_default_checkpointer())
```

**❌ Problem**: Subagent files don't persist
**✅ Solution**: Framework automatically propagates checkpointer to subagents (v1.1+)

**❌ Problem**: Tool outputs don't persist
**✅ Solution**: Use `@handle_large_response` decorator for tools that write files:
```python
from deepagents.decorators import handle_large_response

@tool
@handle_large_response  # Automatically writes large outputs to persistent files
def my_research_tool(query: str) -> str:
    # Tool logic here
    return large_result
```

**❌ Problem**: Database file not created
**✅ Solution**: Run installation script: `python backend/install_persistence.py`

### **Common Issues**

#### **Dynamic Configuration Issues:**
- **Agent not appearing?** Ensure `enabled: true` in `agents.json` and restart server
- **Missing tool errors?** Confirm tool function is imported in `AgentFactory._discover_tools()`
- **Subagent creation failures?** Check subagent creators return proper `SubAgent` objects
- **Wrong tools assigned?** Verify `agent_type` matches factory logic in `_get_default_tools_for_type()`

#### **Hard-Coded File Issues:**
- **Import errors?** Check all tool and subagent imports are correct and available
- **Agent not loading?** Verify agent file is imported in `dynamic_agents.py`
- **Tool registration errors?** Ensure all tools are properly decorated with `@tool`
- **Subagent errors?** Confirm subagent creators are called correctly and return valid objects

#### **General Issues:**
- **Frontend still showing old agents?** Clear browser cache and verify `AVAILABLE_AGENTS` in frontend config
- **LangGraph references stale agents?** Restart LangGraph server after any configuration changes
- **Performance issues?** Consider using hard-coded approach for production systems

### **Best Practices**

#### **For Both Approaches:**
- **Always test agents** before deploying to production
- **Document new tools and subagents** for team reference
- **Use descriptive agent names and IDs** for clarity
- **Follow naming conventions** consistently across the codebase
- **Version control configurations** to track changes

#### **Dynamic Configuration Best Practices:**
- **Keep factory logic simple** and predictable
- **Use consistent agent type naming** (snake_case)
- **Document agent type capabilities** in comments
- **Test factory logic** with different agent type combinations

#### **Hard-Coded File Best Practices:**
- **Follow consistent file structure** across agent files
- **Use descriptive function names** (`create_[domain]_agent`)
- **Include comprehensive docstrings** explaining agent purpose and capabilities
- **Handle errors gracefully** in agent creation functions
- **Use type hints** for better IDE support and debugging

---

## 🔄 **Migration Between Approaches**

### **Dynamic to Hard-Coded Migration:**

1. **Extract agent configuration** from factory logic
2. **Create dedicated agent file** with explicit imports
3. **Copy tool and subagent assignments** from factory methods
4. **Update dynamic_agents.py** to import new agent creator
5. **Test thoroughly** to ensure identical behavior

### **Hard-Coded to Dynamic Migration:**

1. **Add agent type** to `AgentType` enum
2. **Extract tool/subagent lists** from agent file
3. **Add factory logic** for new agent type
4. **Create agents.json entry** with new agent type
5. **Update dynamic_agents.py** to use `create_agent_by_id()`
6. **Remove old agent file** after testing

---

## 🗂️ **Custom Tools & Subagents Catalogue (v1.1)**

### **Available Tools**

- **Perplexity Suite (`backend/tools/search/`):** `perplexity_reasoning_search`, `perplexity_focused_research`, `academic_search`, `technical_search`, `market_research`, `deep_research`, `sonar_deep_research`.
- **Tavily Search (`backend/tools/search/tavily_search.py`):** `tavily_search`, `tavily_qna_search`.
- **CORE API Research (`backend/tools/core_api/`):**
  - Retrieval: `get_work_by_id`, `batch_get_works_by_ids`
  - Search & exports: `search_works`, `scroll_export_works`
  - Analytics: `aggregate_works`, `time_trend_analysis`
  - Journals: `search_journals`, `get_journal_by_id`, `analyze_top_venues_for_topic`
- **Utility:** `get_active_subagents`, `get_subagent_summary` (`backend/tools/subagent_tracker.py`).

### **Available Subagents**

- **General Operations:** `create_general_subagent()` → `specialist-agent`.
- **Perplexity Research Specialists:** `create_reasoning_subagent()`, `create_deep_research_agent()`, `create_market_analysis_agent()`, `create_technical_research_agent()`.
- **CORE Research Pod (`backend/subagents/core_research_subagents.py`):**
  - `literature_screener`
  - `trend_analyzer`
  - `full_text_analyzer`
  - `systematic_review_helper`
  - `meta_analysis_collector`
  - `venue_analyzer`
  - `research_gap_identifier`
  - `citation_network_mapper`

Each subagent declaration includes a focused prompt, tool whitelist, and (when needed) model overrides.

---

## 🛡️ Mandatory Large-Response Handling

Long-running research tools (CORE API exports, Perplexity deep research, etc.) can easily exceed the model context window. **Always decorate any tool that may return large responses** with `@handle_large_response` from `src.deepagents.decorators`.

```python
from src.deepagents import tool
from src.deepagents.decorators import handle_large_response

@tool(description="Retrieve full CORE paper with optional citations")
@handle_large_response(max_length=2000)  # writes large responses to virtual filesystem
async def get_work_by_id(...):
    ...
```

### **When to Apply the Decorator**

- **High-volume outputs**: full-text research papers, multi-document exports, batched CORE API responses, sonar deep research reports.
- **User request**: whenever a user explicitly asks to save full results to disk.
- **Documentation flags**: any API parameter advertising complete datasets, comprehensive reports, `full_text=True`, or similar.

### **Runtime Behavior**

- Results beyond `max_length` (measured in characters, not tokens) are automatically written to the virtual filesystem under `tool_outputs/` directory.
- The tool returns a `Command` object with a `ToolMessage` containing a file reference, keeping the conversation within context limits.
- Files are automatically accessible in the UI through the agent's state management system (`state["files"]`).
- The agent receives a notification message like: `[Large output from tool_name was written to tool_outputs/tool_name_hash_timestamp.ext]`

> **Tip:** Mention the decorator in your tool docstring so future maintainers know large-response safeguarding is in place.

---

## 🏗️ Agent Registry (`backend/config/agent_registry.py`)

The registry loads `agents.json` at startup and exposes helper functions:

- `list_agents(enabled_only=True)` – enumerate available agents.
- `get_agent_config(agent_id)` – fetch configuration by ID.
- `register_agent_config(config)` – add a new agent programmatically.
- `update_agent(agent_id, config)` / `unregister_agent(agent_id)` – modify or remove agents.

### **Agent Configuration Schema**

```python
@dataclass
class AgentConfig:
    id: str
    name: str
    description: str
    agent_type: AgentType  # general | research | coding | creative | ...

    color: str = "#3B82F6"
    icon: str = "🤖"

    instructions: str = ""
    tools: list[str] = field(default_factory=list)
    subagents: list[str] = field(default_factory=list)

    model_config: dict[str, Any] | None = None
    recursion_limit: int = 100
    interrupt_config: dict[str, Any] | None = None
    builtin_tools: list[str] | None = None
    main_agent_tools: list[str] | None = None

    enabled: bool = True
    created_at: str | None = None
    updated_at: str | None = None
```

All configurations are serialized to `backend/config/agents.json`. The generator ensures defaults exist (main, research, coding, creative) if the file is empty.

### **Adding an Agent Manually**

```json
{
  "id": "analysis-agent",
  "name": "Analysis Agent",
  "description": "Handles quantitative analysis and reporting",
  "agent_type": "analysis",
  "color": "#F97316",
  "icon": "📊",
  "instructions": "You are a data analysis specialist...",
  "tools": ["aggregate_works", "time_trend_analysis"],
  "subagents": ["general_subagent", "technical_research_subagent"],
  "model_config": {"model": "claude-sonnet-4-20250514"},
  "recursion_limit": 150,
  "enabled": true
}
```

After editing, run the generator to rebuild LangGraph artifacts.

---

## 🛠️ Agent Factory (`backend/agents/agent_factory.py`)

`AgentFactory` binds registry configs to actual deepagents:

- Discovers tools from `backend/tools/**` and registers them by name (e.g. `tavily_search`, `perplexity_reasoning_search`).
- Discovers subagent creators from `backend/subagents/**` (e.g. `create_general_subagent`, `create_deep_research_agent`).
- Applies default instructions/assignments based on `AgentType` if none provided.
- Calls `deepagents.create_deep_agent()` with the resolved instructions, tools, subagents, models, and builtin tool lists.

Use helper functions:

```python
from agents.agent_factory import create_agent_by_id, create_all_configured_agents

agent = create_agent_by_id("research-agent")
all_agents = create_all_configured_agents()  # returns dict[id -> agent]
```

The generated `agents/dynamic_agents.py` imports these helpers and instantiates configured agents at module import time.

---

## 🌐 Management API (`backend/agents/api_endpoints.py`)

Optional FastAPI blueprint providing:

- `GET /agents` – list all agents (with `enabled` filter).
- `GET /agents/{id}` – retrieve config.
- `POST /agents` – register new agent.
- `PUT /agents/{id}` – update config.
- `DELETE /agents/{id}` – remove agent (except `main-agent`).
- `GET /agents/{id}/status` – validate factory instantiation.
- `GET /tools` – list discovered tools/subagents.
- `POST /regenerate-config` – rerun LangGraph generator.
- `GET /health` – service heartbeat.

Mount it on your FastAPI app or run separately to script agent lifecycle operations.

---

## 💡 Built-In & Custom Models

- Default model per agent is loaded from `models/get_default_model()`.
- Override per agent via `AgentConfig.model_config` (e.g. specify model name, temperature, API key reference).
- Advanced settings like `builtin_tools` or `main_agent_tools` allow fine-grained control over built-ins.

---

## 🖥️ Frontend Integration (Next.js)

Key additions under `frontend/`:

- `src/lib/agents/config.ts` – mirrors available agents with `AVAILABLE_AGENTS` array.
- `src/app/types/types.ts` – defines `Agent` & `AgentContext` interfaces.
- `src/app/components/AgentSelector/` – dropdown to switch agents (color-coded, icon display).
- `src/app/hooks/useChat.ts` – accepts `agent` to open LangGraph streams per agent.
- `src/app/components/ThreadHistorySidebar/ThreadHistorySidebar.tsx` – shows agent-specific threads.
- `src/app/page.tsx` – maintains agent-scoped todos, files, and subagent selections.

This separation ensures each agent has isolated context (thread history, todo state, file saves) while reusing UI components.

---

## 🔄 Migrating from v1.0

1. **Keep existing README (`deepagents.README.md`)** for legacy single-agent reference.
2. **Copy new files** into your project:
   - `config/agent_registry.py`
   - `agents/agent_factory.py`
   - `utils/langgraph_generator.py`
   - `agents/api_endpoints.py` (optional)
   - Updated `config/prompts.py`
   - Frontend changes (if using the provided UI).
3. **Create `config/agents.json`** (auto-populated with defaults on first run).
4. **Run generator** to produce multi-agent LangGraph artifacts.
5. **Update frontend** to use the new selector and agent-aware hooks.

Existing single-agent flows remain unaffected until you add more entries to the registry.

---

## 📚 Additional Resources

- `backend/deepagents.README.md` – original single-agent guide (**DEPRECATED - use this v1.1 guide instead**)
- `backend/config/prompts.py` – concise instructions per agent type
- `backend/tools/` & `backend/subagents/` – extendable toolchains
- `frontend/src/app/components/` – UI components for agent visualization
- [LangGraph Documentation](https://docs.langchain.com/langgraph) – underlying graph runtime

---

## 🗺️ Roadmap Ideas

- CLI for agent registration/updates
- Role-based access or agent-level auth
- Web dashboard for agent configuration
- Telemetry dashboards per agent
- Auto-import tool/subagent docs into README

---

## 📖 **Complete Example: Basic Usage**

Here's a simple example showing how to use Deep Agents v1.1:

```python
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

# Initialize external service
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# Search tool to use for research
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

# Prompt prefix to steer the agent to be an expert researcher
research_instructions = """You are an expert researcher. Your job is to conduct thorough research, and then write a polished report.

You have access to a few tools.

## `internet_search`

Use this to run an internet search for a given query. You can specify the number of results, the topic, and whether raw content should be included.
"""

# Create the agent
agent = create_deep_agent(
    [internet_search],
    research_instructions,
)

# Invoke the agent
result = agent.invoke({"messages": [{"role": "user", "content": "what is langgraph?"}]})
```

The agent created with `create_deep_agent` is just a LangGraph graph - so you can interact with it (streaming, human-in-the-loop, memory, studio) in the same way you would any LangGraph agent.

---

By combining the Agent Registry, Factory, and LangGraph generator, Deep Agents v1.1 becomes a **flexible multi-agent orchestration platform**. You can quickly add specialized agents, equip them with domain-specific tools, and expose them to users through a shared UI—without touching the deep agents core.

Whether you choose the **Dynamic Configuration** approach for rapid development and runtime flexibility, or the **Hard-Coded File** approach for maximum control and production reliability, Deep Agents v1.1 provides the foundation for building sophisticated, specialized AI agent systems.

```json
{
  "id": "analysis-agent",
  "name": "Analysis Agent",
  "description": "Handles quantitative analysis and reporting",
  "agent_type": "analysis",
  "color": "#F97316",
  "icon": "📊",
  "instructions": "You are a data analysis specialist...",
  "tools": ["aggregate_works", "time_trend_analysis"],
  "subagents": ["general_subagent", "technical_research_subagent"],
  "model_config": {"model": "claude-sonnet-4-20250514"},
  "recursion_limit": 150,
  "enabled": true
}
```

After editing, run the generator to rebuild LangGraph artifacts.

---

## 🛠️ Agent Factory (`backend/agents/agent_factory.py`)

`AgentFactory` binds registry configs to actual deepagents:

- Discovers tools from `backend/tools/**` and registers them by name (e.g. `tavily_search`, `perplexity_reasoning_search`).
- Discovers subagent creators from `backend/subagents/**` (e.g. `create_general_subagent`, `create_deep_research_agent`).
- Applies default instructions/assignments based on `AgentType` if none provided.
- Calls `deepagents.create_deep_agent()` with the resolved instructions, tools, subagents, models, and builtin tool lists.

Use helper functions:

```python
from agents.agent_factory import create_agent_by_id, create_all_configured_agents

agent = create_agent_by_id("research-agent")
all_agents = create_all_configured_agents()  # returns dict[id -> agent]
```

The generated `agents/dynamic_agents.py` imports these helpers and instantiates configured agents at module import time.

---

## 🕸️ LangGraph Integration (`backend/utils/langgraph_generator.py`)

The generator outputs:

- `backend/langgraph.json` with `graphs` mapping agent IDs to `agents.dynamic_agents:<agent_variable>`.
- `backend/agents/dynamic_agents.py` containing assignments like `research_agent = create_agent_by_id("research-agent")`.

### CLI Usage

```bash
python -c "from utils.langgraph_generator import generate_langgraph_config; generate_langgraph_config()"
```

- Creates a backup `langgraph.json.backup` if a file already exists.
- Honors `AgentConfig.enabled`: disabled agents are omitted.
- Call after modifying agents to keep LangGraph aligned.

---

## 🌐 Management API (`backend/agents/api_endpoints.py`)

Optional FastAPI blueprint providing:

- `GET /agents` – list all agents (with `enabled` filter).
- `GET /agents/{id}` – retrieve config.
- `POST /agents` – register new agent.
- `PUT /agents/{id}` – update config.
- `DELETE /agents/{id}` – remove agent (except `main-agent`).
- `GET /agents/{id}/status` – validate factory instantiation.
- `GET /tools` – list discovered tools/subagents.
- `POST /regenerate-config` – rerun LangGraph generator.
- `GET /health` – service heartbeat.

Mount it on your FastAPI app or run separately to script agent lifecycle operations.

---

## 🧩 Subagents & Tools

Subagents remain optional but powerful. Configure globally in `backend/subagents/` with creators like `create_deep_research_agent()`. Reference their registry keys in `AgentConfig.subagents`.

Tools live in `backend/tools/` and should be registered with descriptive names. The factory only exposes tools declared in the `tools` list (or defaults per `AgentType`).

> **Tip:** Document new tools/subagents in README sections or internal wikis so team members know which keys to reference when adding agents.

---

## 🗂️ Custom Tools & Subagents Catalogue (v1.1)

### Tools

- **Perplexity Suite (`backend/tools/search/`):** `perplexity_reasoning_search`, `perplexity_focused_research`, `academic_search`, `technical_search`, `market_research`, `deep_research`, `sonar_deep_research`.
- **Tavily Search (`backend/tools/search/tavily_search.py`):** `tavily_search`, `tavily_qna_search`.
- **CORE API Research (`backend/tools/core_api/`):**
  - Retrieval: `get_work_by_id`, `batch_get_works_by_ids`
  - Search & exports: `search_works`, `scroll_export_works`
  - Analytics: `aggregate_works`, `time_trend_analysis`
  - Journals: `search_journals`, `get_journal_by_id`, `analyze_top_venues_for_topic`
- **Utility:** `get_active_subagents`, `get_subagent_summary` (`backend/tools/subagent_tracker.py`).

### Subagents

- **General Operations:** `create_general_subagent()` → `specialist-agent`.
- **Perplexity Research Specialists:** `create_reasoning_subagent()`, `create_deep_research_agent()`, `create_market_analysis_agent()`, `create_technical_research_agent()`.
- **CORE Research Pod (`backend/subagents/core_research_subagents.py`):**
  - `literature_screener`
  - `trend_analyzer`
  - `full_text_analyzer`
  - `systematic_review_helper`
  - `meta_analysis_collector`
  - `venue_analyzer`
  - `research_gap_identifier`
  - `citation_network_mapper`

Each subagent declaration includes a focused prompt, tool whitelist, and (when needed) model overrides.

---

## 🧭 Agents ↔ Subagents ↔ Tools Dictionary

The registry-driven factory allows you to express agent composition as structured dictionaries. Below is the current canonical view (extend as you enable more agents in `config/agents.json`).

```python
AGENT_DIRECTORY = {
    "main-agent": {
        "description": "General purpose orchestrator",
        "subagents": [
            "specialist-agent",
            "perplexity-reasoning-agent",
            "sonar-deep-research",
            "market-analysis",
            "technical-research",
            # CORE pod (spawned dynamically)
            "literature_screener",
            "trend_analyzer",
            "full_text_analyzer",
            "systematic_review_helper",
            "meta_analysis_collector",
            "venue_analyzer",
            "research_gap_identifier",
            "citation_network_mapper",
        ],
        "tools": [
            # Perplexity & Tavily
            "perplexity_reasoning_search",
            "perplexity_focused_research",
            "academic_search",
            "technical_search",
            "market_research",
            "deep_research",
            "sonar_deep_research",
            "tavily_search",
            "tavily_qna_search",
            # CORE API
            "search_works",
            "scroll_export_works",
            "get_work_by_id",
            "batch_get_works_by_ids",
            "aggregate_works",
            "time_trend_analysis",
            "search_journals",
            "get_journal_by_id",
            "analyze_top_venues_for_topic",
            # Utilities
            "get_active_subagents",
            "get_subagent_summary",
            # Built-ins wired automatically by framework (write/read/edit/ls/task/etc.)
        ],
    },
    # Placeholder entries (populate as you enable additional registry agents)
    "research-agent": {
        "description": "Specialized research workflows",
        "subagents": [],
        "tools": [],
    },
    "code-assistant": {
        "description": "Coding-focused assistant",
        "subagents": [],
        "tools": [],
    },
    "content-creator": {
        "description": "Writing and content generation",
        "subagents": [],
        "tools": [],
    },
}
```

> Update this dictionary whenever you register new agents or expand existing ones so future contributors have a single source of truth for orchestration.

---

## 💡 Built-In & Custom Models

- Default model per agent is loaded from `models/get_default_model()`.
- Override per agent via `AgentConfig.model_config` (e.g. specify model name, temperature, API key reference).
- Advanced settings like `builtin_tools` or `main_agent_tools` allow fine-grained control over built-ins.

---

## 🖥️ Frontend Integration (Next.js)

Key additions under `frontend/`:

- `src/lib/agents/config.ts` – mirrors available agents with `AVAILABLE_AGENTS` array.
- `src/app/types/types.ts` – defines `Agent` & `AgentContext` interfaces.
- `src/app/components/AgentSelector/` – dropdown to switch agents (color-coded, icon display).
- `src/app/hooks/useChat.ts` – accepts `agent` to open LangGraph streams per agent.
- `src/app/components/ThreadHistorySidebar/ThreadHistorySidebar.tsx` – shows agent-specific threads.
- `src/app/page.tsx` – maintains agent-scoped todos, files, and subagent selections.

This separation ensures each agent has isolated context (thread history, todo state, file saves) while reusing UI components.

---

## 🔄 Migrating from v1.0

1. **Keep existing README (`deepagents.README.md`)** for legacy single-agent reference.
2. **Copy new files** into your project:
   - `config/agent_registry.py`
   - `agents/agent_factory.py`
   - `utils/langgraph_generator.py`
   - `agents/api_endpoints.py` (optional)
   - Updated `config/prompts.py`
   - Frontend changes (if using the provided UI).
3. **Create `config/agents.json`** (auto-populated with defaults on first run).
4. **Run generator** to produce multi-agent LangGraph artifacts.
5. **Update frontend** to use the new selector and agent-aware hooks.

Existing single-agent flows remain unaffected until you add more entries to the registry.

---

## ✅ Troubleshooting & Tips

- **Agent not appearing?** Ensure `enabled: true` in config and rerun generator.
- **Missing tool errors?** Confirm the tool function is imported inside `AgentFactory._discover_tools()`.
- **Subagent creation failures?** Check that subagent creators return a `SubAgent` object;
  watch console warnings emitted by the factory.
- **Frontend still showing one agent?** Rebuild the app and verify `AVAILABLE_AGENTS` lists every registry agent (IDs must match backend).
- **LangGraph references stale agent list?** Regenerate config after every registry change.

---

## 📚 Additional Resources

- `backend/deepagents.README.md` – original single-agent guide
- `backend/config/prompts.py` – concise instructions per agent type
- `backend/tools/` & `backend/subagents/` – extendable toolchains
- `frontend/src/app/components/` – UI components for agent visualization
- [LangGraph Documentation](https://docs.langchain.com/langgraph) – underlying graph runtime

---

## 🗺️ Roadmap Ideas

- CLI for agent registration/updates
- Role-based access or agent-level auth
- Web dashboard for agent configuration
- Telemetry dashboards per agent
- Auto-import tool/subagent docs into README

---

By combining the Agent Registry, Factory, and LangGraph generator, Deep Agents v1.1 becomes a **flexible multi-agent orchestration platform**. You can quickly add specialized agents, equip them with domain-specific tools, and expose them to users through a shared UI—without touching the deep agents core.
