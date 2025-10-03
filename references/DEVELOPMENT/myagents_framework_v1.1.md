# MyAgents Framework v1.1
## The Ultimate Multi-Agent AI Framework for Complex Task Execution

**Version**: 1.1.0  
**Date**: 2025-10-01  
**Status**: Design & Implementation Plan  
**Purpose**: Create the most effective multi-agent AI framework for building systems that handle complex tasks requiring planning, replanning, documentation, human-in-the-loop refinements, and crucial decisions.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Reference Analysis](#reference-analysis)
3. [Core Architecture](#core-architecture)
4. [Framework Features](#framework-features)
5. [Project Structure](#project-structure)
6. [Implementation Plan](#implementation-plan)
7. [API Design](#api-design)
8. [Migration Guide](#migration-guide)
9. [Roadmap](#roadmap)

---

## 1. Executive Summary

### Vision

MyAgents Framework v1.1 combines the best features from three world-class frameworks:
1. **DeepAgents (New)** - Middleware architecture, automatic summarization, prompt caching
2. **Current MyAgents** - Multi-agent registry, memory system, subagent tracking, QA workflow
3. **Claude Agent SDK** - Permission system, hooks, bidirectional control, MCP integration

### Key Innovations

🎯 **Unified Architecture**: Middleware-based extensibility with backwards compatibility  
🧠 **Intelligent Memory**: Semantic memory with cross-agent collaboration  
🔄 **Adaptive Planning**: Dynamic replanning with human oversight  
📊 **Complete Observability**: Full lifecycle tracking and visualization  
🔐 **Granular Permissions**: Tool-level and subagent-level access control  
🎨 **Developer Experience**: Simple API, rich tooling, comprehensive documentation  

### Target Use Cases

- ✅ **Research & Scientific Publication** - Systematic literature reviews, data analysis, report generation
- ✅ **Long-Form Writing** - Novels, series, technical documentation with consistency tracking
- ✅ **Business Automation** - Process analysis, workflow automation, decision support
- ✅ **Software Development** - Code generation, review, testing, documentation
- ✅ **Data Analysis** - Multi-source data integration, analysis, visualization

---

## 2. Reference Analysis

### 2.1 DeepAgents (New) - Middleware Architecture

**Location**: `references/src/deepagents/`

**Key Features**:
```python
# Middleware-based architecture
middleware = [
    PlanningMiddleware(),           # Auto-adds write_todos + planning prompt
    FilesystemMiddleware(),         # Auto-adds file tools + filesystem prompt
    SubAgentMiddleware(),           # Auto-creates task tool
    SummarizationMiddleware(),      # Auto-summarizes at 120k tokens
    AnthropicPromptCachingMiddleware()  # Caches prompts for 5min
]
```

**Strengths**:
- ✅ Clean separation of concerns
- ✅ Automatic context management (summarization)
- ✅ Cost optimization (prompt caching)
- ✅ Extensible middleware stack
- ✅ Per-subagent middleware customization

**Limitations**:
- ❌ No multi-agent registry
- ❌ No semantic memory system
- ❌ No subagent lifecycle tracking
- ❌ No QA workflow
- ❌ No real file management

**Adoption Strategy**: Use as base framework, add missing features as middleware

---

### 2.2 Current MyAgents - Enhanced Features

**Location**: `backend/`

**Key Features**:

1. **Multi-Agent Registry** (`config/agent_registry.py`)
   ```python
   registry = AgentRegistry.from_file("agents.json")
   agent = registry.create_agent("research-assistant")
   ```

2. **Memory System** (`core/memory/`)
   - Semantic memory with AI-powered search
   - Cross-agent context sharing
   - Thread-based isolation
   - Memory classification (important, decisions, files)

3. **Subagent Tracking** (`tools/subagent_tracker.py`)
   - Lifecycle events (started, active, completed, error)
   - UI visualization support
   - Performance monitoring

4. **QA Review Workflow** (`subagents/qa_reviewer.py`)
   - Mandatory quality assurance
   - Completion verification
   - Gap analysis

5. **Persistent State** (`config/checkpointer.py`)
   - SQLite-based state storage
   - Cross-restart persistence

**Strengths**:
- ✅ Comprehensive feature set
- ✅ Production-ready implementations
- ✅ Addresses real framework gaps
- ✅ Well-tested in practice

**Limitations**:
- ❌ Built on older DeepAgents version
- ❌ Manual tool/prompt assembly
- ❌ No middleware architecture
- ❌ No automatic summarization

**Adoption Strategy**: Port features as middleware and extensions

---

### 2.3 Claude Agent SDK - Permission & Control

**Location**: `references/claude_agent_sdk/`

**Key Features**:

1. **Permission System** (`types.py`)
   ```python
   @dataclass
   class PermissionResultAllow:
       behavior: Literal["allow"] = "allow"
       updated_input: dict[str, Any] | None = None
       updated_permissions: list[PermissionUpdate] | None = None
   
   CanUseTool = Callable[[str, dict, ToolPermissionContext], Awaitable[PermissionResult]]
   ```

2. **Hook System** (`types.py`)
   ```python
   HookEvent = Literal[
       "PreToolUse", "PostToolUse", "UserPromptSubmit",
       "Stop", "SubagentStop", "PreCompact"
   ]
   
   HookCallback = Callable[[input, tool_use_id, HookContext], Awaitable[HookJSONOutput]]
   ```

3. **Bidirectional Control** (`_internal/query.py`)
   - Control request/response routing
   - Async message streaming
   - Initialization handshake

4. **MCP Integration** (`__init__.py`)
   ```python
   @tool("greet", "Greet a user", {"name": str})
   async def greet(args):
       return {"content": [{"type": "text", "text": f"Hello, {args['name']}!"}]}
   
   server = create_sdk_mcp_server("my-server", tools=[greet])
   ```

**Strengths**:
- ✅ Sophisticated permission model
- ✅ Flexible hook system
- ✅ Bidirectional communication
- ✅ MCP server support
- ✅ Production-grade error handling

**Limitations**:
- ❌ Claude-specific (not framework-agnostic)
- ❌ No multi-agent support
- ❌ No planning/replanning
- ❌ No memory system

**Adoption Strategy**: Adapt permission and hook patterns for MyAgents

---

### 2.4 Feature Compatibility Matrix

| Feature | DeepAgents (New) | Current MyAgents | Claude SDK | MyAgents v1.1 |
|---------|------------------|------------------|------------|---------------|
| **Architecture** |
| Middleware System | ✅ | ❌ | ❌ | ✅ |
| Multi-Agent Registry | ❌ | ✅ | ❌ | ✅ |
| Extensible Plugins | ⚠️ | ❌ | ⚠️ | ✅ |
| **Memory & Context** |
| Semantic Memory | ❌ | ✅ | ❌ | ✅ |
| Auto Summarization | ✅ | ❌ | ❌ | ✅ |
| Cross-Agent Context | ❌ | ✅ | ❌ | ✅ |
| Prompt Caching | ✅ | ❌ | ❌ | ✅ |
| **Planning & Execution** |
| Planning Tools | ✅ | ✅ | ❌ | ✅ |
| Dynamic Replanning | ❌ | ⚠️ | ❌ | ✅ |
| QA Workflow | ❌ | ✅ | ❌ | ✅ |
| **Permissions & Control** |
| Tool-Level Permissions | ⚠️ | ✅ | ✅ | ✅ |
| Subagent-Level Permissions | ❌ | ✅ | ❌ | ✅ |
| Permission Updates | ❌ | ❌ | ✅ | ✅ |
| Hook System | ❌ | ❌ | ✅ | ✅ |
| **Observability** |
| Subagent Tracking | ❌ | ✅ | ⚠️ | ✅ |
| Lifecycle Events | ❌ | ✅ | ⚠️ | ✅ |
| Performance Metrics | ❌ | ⚠️ | ❌ | ✅ |
| **File Management** |
| Virtual Files | ✅ | ✅ | ❌ | ✅ |
| Real Files | ❌ | ❌ | ❌ | ✅ |
| File Versioning | ❌ | ✅ | ❌ | ✅ |
| **Integration** |
| MCP Support | ❌ | ❌ | ✅ | ✅ |
| External APIs | ❌ | ✅ | ⚠️ | ✅ |
| Custom Tools | ✅ | ✅ | ✅ | ✅ |

**Legend**: ✅ Full Support | ⚠️ Partial Support | ❌ Not Supported

---

## 3. Core Architecture

### 3.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  (User Agents: Research, Writing, Business, Coding, etc.)  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   MyAgents Framework v1.1                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Agent Registry & Factory                 │  │
│  │  (Multi-agent management, dynamic creation)          │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Middleware Stack                         │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ Planning │ Filesystem │ SubAgent │ Memory     │  │  │
│  │  │ Tracking │ Permissions │ Hooks │ Summarization│  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Core Services                            │  │
│  │  • Memory Manager    • File Manager                  │  │
│  │  • Permission Engine • Hook Engine                   │  │
│  │  • Event Bus         • Metrics Collector             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  DeepAgents Base Framework                   │
│  (Agent creation, tool execution, state management)         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph & LangChain                       │
│  (Graph execution, message handling, checkpointing)         │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Middleware Architecture

**Middleware Pipeline**:
```python
# Request Flow
User Input → Agent → Middleware Stack → Model → Middleware Stack → Response

# Middleware Execution Order
1. PreModelMiddleware (modify request before model)
   - PermissionMiddleware (check permissions)
   - MemoryMiddleware (inject relevant context)
   - PlanningMiddleware (add planning tools/prompts)
   - FilesystemMiddleware (add file tools/prompts)
   - SubAgentMiddleware (add task tool)

2. Model Execution
   - LLM processes request with tools

3. PostModelMiddleware (modify response after model)
   - TrackingMiddleware (emit lifecycle events)
   - HookMiddleware (execute hooks)
   - SummarizationMiddleware (summarize if needed)
   - CachingMiddleware (cache prompts)
```

**Middleware Interface**:
```python
class AgentMiddleware(ABC):
    """Base class for all middleware."""
    
    state_schema: Optional[Type[AgentState]] = None
    tools: list[BaseTool] = []
    
    def modify_model_request(
        self, 
        request: ModelRequest, 
        agent_state: AgentState
    ) -> ModelRequest:
        """Modify request before sending to model."""
        return request
    
    def process_model_response(
        self,
        response: ModelResponse,
        agent_state: AgentState
    ) -> ModelResponse:
        """Process response after model execution."""
        return response
    
    async def on_agent_start(self, agent_state: AgentState) -> None:
        """Called when agent starts."""
        pass
    
    async def on_agent_end(self, agent_state: AgentState) -> None:
        """Called when agent ends."""
        pass
```

---

## 4. Framework Features

### 4.1 Multi-Agent Registry System

**Purpose**: Centralized management of multiple specialized agents

**Implementation**:
```python
# myagents_framework/registry/agent_registry.py

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, List, Any

class AgentType(Enum):
    GENERAL = "general"
    RESEARCH = "research"
    WRITING = "writing"
    CODING = "coding"
    BUSINESS = "business"
    CUSTOM = "custom"

@dataclass
class AgentConfig:
    """Agent configuration."""
    id: str
    name: str
    description: str
    agent_type: AgentType
    
    # Behavior
    instructions: str = ""
    tools: List[str] = field(default_factory=list)
    subagents: List[str] = field(default_factory=list)
    middleware: List[str] = field(default_factory=list)
    
    # Model
    model_config: Optional[Dict[str, Any]] = None
    
    # Features
    enable_memory: bool = True
    enable_tracking: bool = True
    enable_qa_review: bool = False
    enable_real_files: bool = False
    workspace_path: Optional[str] = None
    
    # Permissions
    permission_mode: PermissionMode = "default"
    tool_permissions: Dict[str, PermissionBehavior] = field(default_factory=dict)
    
    # Advanced
    recursion_limit: int = 100
    max_tokens_before_summary: int = 120000
    
    # Metadata
    color: str = "#3B82F6"
    icon: str = "🤖"
    enabled: bool = True

class AgentRegistry:
    """Registry for managing multiple agents."""
    
    def __init__(self, config_path: Optional[str] = None):
        self._agents: Dict[str, AgentConfig] = {}
        self._factories: Dict[str, Callable] = {}
        self._load_configurations(config_path)
    
    def register_agent(self, config: AgentConfig) -> bool:
        """Register a new agent configuration."""
        pass
    
    def create_agent(self, agent_id: str) -> Agent:
        """Create an agent instance from configuration."""
        pass
    
    def list_agents(self, enabled_only: bool = True) -> List[AgentConfig]:
        """List all registered agents."""
        pass
    
    @classmethod
    def from_file(cls, config_path: str) -> "AgentRegistry":
        """Load registry from JSON file."""
        pass
```

**Usage**:
```python
# Define agents in agents.json
{
  "agents": [
    {
      "id": "research-assistant",
      "name": "Research Assistant",
      "type": "research",
      "instructions": "You are a research specialist...",
      "tools": ["academic_search", "web_search"],
      "subagents": ["literature_screener", "synthesis_engine"],
      "enable_memory": true,
      "enable_qa_review": true
    }
  ]
}

# Use in code
registry = AgentRegistry.from_file("agents.json")
agent = registry.create_agent("research-assistant")
```

---

### 4.2 Intelligent Memory System

**Purpose**: Semantic memory with cross-agent collaboration and context continuity

**Architecture**:
```
┌─────────────────────────────────────────────────────────┐
│                   Memory System                          │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐  │
│  │         Memory Manager (Coordinator)              │  │
│  └──────────────────────────────────────────────────┘  │
│           ↓              ↓              ↓               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │   Thread     │ │    Cross     │ │    Search    │  │
│  │   Memory     │ │    Agent     │ │    Engine    │  │
│  │              │ │   Manager    │ │              │  │
│  └──────────────┘ └──────────────┘ └──────────────┘  │
│           ↓              ↓              ↓               │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Storage Layer (SQLite + Vector DB)        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Implementation**:
```python
# myagents_framework/memory/memory_manager.py

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class Memory:
    """Memory entry."""
    id: str
    thread_id: str
    agent_name: str
    content: str
    summary: str
    classification: MemoryClassification
    importance: MemoryImportance
    metadata: Dict[str, Any]
    created_at: datetime
    embedding: Optional[List[float]] = None

class MemoryClassification(Enum):
    DECISION = "decision"
    FILE_OPERATION = "file_operation"
    IMPORTANT_INFO = "important_info"
    CONTEXT = "context"
    GENERAL = "general"

class MemoryImportance(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class MemoryManager:
    """Manages semantic memory for agents."""
    
    def create_memory(
        self,
        thread_id: str,
        agent_name: str,
        content: str,
        classification: MemoryClassification,
        importance: MemoryImportance,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Memory:
        """Create a new memory entry."""
        pass
    
    def search_memories(
        self,
        thread_id: str,
        query: str,
        classification: Optional[MemoryClassification] = None,
        min_importance: Optional[MemoryImportance] = None,
        limit: int = 5
    ) -> List[Memory]:
        """Search memories using semantic search."""
        pass
    
    def get_context_summary(
        self,
        thread_id: str,
        agent_name: str
    ) -> str:
        """Get comprehensive context summary for agent."""
        pass
    
    def share_memory_across_threads(
        self,
        memory_id: str,
        target_thread_ids: List[str]
    ) -> bool:
        """Share important memory across threads."""
        pass
```

**Memory Middleware**:
```python
# myagents_framework/middleware/memory_middleware.py

class MemoryMiddleware(AgentMiddleware):
    """Middleware for automatic memory management."""
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        auto_create_on: List[str] = ["tool_use", "decision", "file_write"]
    ):
        self.memory_manager = memory_manager
        self.auto_create_on = auto_create_on
    
    def modify_model_request(
        self,
        request: ModelRequest,
        agent_state: AgentState
    ) -> ModelRequest:
        """Inject relevant memories into context."""
        # Get relevant memories
        memories = self.memory_manager.search_memories(
            thread_id=agent_state.thread_id,
            query=request.messages[-1].content,
            limit=3
        )
        
        # Inject as system message
        if memories:
            memory_context = self._format_memories(memories)
            request.system_prompt += f"\n\n## Relevant Context:\n{memory_context}"
        
        return request
    
    def process_model_response(
        self,
        response: ModelResponse,
        agent_state: AgentState
    ) -> ModelResponse:
        """Auto-create memories for important events."""
        # Detect important events
        if self._should_create_memory(response):
            self.memory_manager.create_memory(
                thread_id=agent_state.thread_id,
                agent_name=agent_state.agent_name,
                content=self._extract_content(response),
                classification=self._classify_event(response),
                importance=self._assess_importance(response)
            )
        
        return response
```

---

### 4.3 Permission & Hook System

**Purpose**: Granular control over tool execution and agent behavior

**Permission System** (adapted from Claude SDK):
```python
# myagents_framework/permissions/permission_engine.py

from dataclasses import dataclass
from typing import Literal, Optional, Dict, Any, Callable, Awaitable

PermissionMode = Literal["default", "acceptEdits", "plan", "bypassPermissions"]
PermissionBehavior = Literal["allow", "deny", "ask"]

@dataclass
class PermissionContext:
    """Context for permission decisions."""
    tool_name: str
    tool_args: Dict[str, Any]
    agent_name: str
    thread_id: str
    suggestions: List[PermissionUpdate] = field(default_factory=list)

@dataclass
class PermissionResultAllow:
    """Allow permission result."""
    behavior: Literal["allow"] = "allow"
    updated_input: Optional[Dict[str, Any]] = None
    updated_permissions: Optional[List[PermissionUpdate]] = None

@dataclass
class PermissionResultDeny:
    """Deny permission result."""
    behavior: Literal["deny"] = "deny"
    message: str = ""
    interrupt: bool = False

PermissionResult = PermissionResultAllow | PermissionResultDeny

CanUseTool = Callable[
    [str, Dict[str, Any], PermissionContext],
    Awaitable[PermissionResult]
]

class PermissionEngine:
    """Manages tool and subagent permissions."""
    
    def __init__(
        self,
        mode: PermissionMode = "default",
        tool_permissions: Optional[Dict[str, PermissionBehavior]] = None,
        can_use_tool: Optional[CanUseTool] = None
    ):
        self.mode = mode
        self.tool_permissions = tool_permissions or {}
        self.can_use_tool = can_use_tool
    
    async def check_permission(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        context: PermissionContext
    ) -> PermissionResult:
        """Check if tool execution is permitted."""
        # Bypass mode
        if self.mode == "bypassPermissions":
            return PermissionResultAllow()
        
        # Check static permissions
        behavior = self.tool_permissions.get(tool_name, "ask")
        if behavior == "allow":
            return PermissionResultAllow()
        elif behavior == "deny":
            return PermissionResultDeny(message=f"Tool {tool_name} is denied")
        
        # Dynamic permission callback
        if self.can_use_tool:
            return await self.can_use_tool(tool_name, tool_args, context)
        
        # Default: ask user
        return await self._prompt_user(tool_name, tool_args, context)
```

**Hook System** (adapted from Claude SDK):
```python
# myagents_framework/hooks/hook_engine.py

from typing import Literal, Callable, Awaitable, Any, Dict

HookEvent = Literal[
    "PreToolUse",
    "PostToolUse",
    "PreSubagentSpawn",
    "PostSubagentComplete",
    "UserPromptSubmit",
    "PrePlanExecution",
    "PostPlanExecution",
    "PreQAReview",
    "PostQAReview"
]

@dataclass
class HookContext:
    """Context for hook execution."""
    agent_name: str
    thread_id: str
    event_data: Dict[str, Any]

@dataclass
class HookOutput:
    """Output from hook execution."""
    decision: Optional[Literal["block", "continue"]] = None
    system_message: Optional[str] = None
    hook_specific_output: Optional[Any] = None

HookCallback = Callable[
    [Dict[str, Any], str, HookContext],
    Awaitable[HookOutput]
]

class HookEngine:
    """Manages lifecycle hooks."""
    
    def __init__(self):
        self.hooks: Dict[HookEvent, List[HookCallback]] = {}
    
    def register_hook(
        self,
        event: HookEvent,
        callback: HookCallback,
        matcher: Optional[Callable[[Dict[str, Any]], bool]] = None
    ):
        """Register a hook for an event."""
        pass
    
    async def execute_hooks(
        self,
        event: HookEvent,
        event_data: Dict[str, Any],
        context: HookContext
    ) -> List[HookOutput]:
        """Execute all hooks for an event."""
        pass
```

**Permission & Hook Middleware**:
```python
# myagents_framework/middleware/permission_middleware.py

class PermissionMiddleware(AgentMiddleware):
    """Middleware for permission checking."""
    
    def __init__(self, permission_engine: PermissionEngine):
        self.permission_engine = permission_engine
    
    def process_model_response(
        self,
        response: ModelResponse,
        agent_state: AgentState
    ) -> ModelResponse:
        """Check permissions before tool execution."""
        if response.tool_calls:
            for tool_call in response.tool_calls:
                context = PermissionContext(
                    tool_name=tool_call.name,
                    tool_args=tool_call.args,
                    agent_name=agent_state.agent_name,
                    thread_id=agent_state.thread_id
                )
                
                result = await self.permission_engine.check_permission(
                    tool_call.name,
                    tool_call.args,
                    context
                )
                
                if isinstance(result, PermissionResultDeny):
                    # Block tool execution
                    response.tool_calls.remove(tool_call)
                    response.messages.append(
                        SystemMessage(content=result.message)
                    )
        
        return response

class HookMiddleware(AgentMiddleware):
    """Middleware for hook execution."""
    
    def __init__(self, hook_engine: HookEngine):
        self.hook_engine = hook_engine
    
    async def on_tool_use(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        agent_state: AgentState
    ) -> HookOutput:
        """Execute PreToolUse hooks."""
        context = HookContext(
            agent_name=agent_state.agent_name,
            thread_id=agent_state.thread_id,
            event_data={"tool_name": tool_name, "tool_args": tool_args}
        )
        
        outputs = await self.hook_engine.execute_hooks(
            "PreToolUse",
            {"tool_name": tool_name, "tool_args": tool_args},
            context
        )
        
        # Check if any hook blocked execution
        for output in outputs:
            if output.decision == "block":
                return output
        
        return HookOutput(decision="continue")
```

---

### 4.4 Subagent Tracking & Visualization

**Purpose**: Complete observability of subagent lifecycle

**Implementation**:
```python
# myagents_framework/tracking/subagent_tracker.py

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class SubagentStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

@dataclass
class SubagentEvent:
    """Subagent lifecycle event."""
    event_type: Literal["started", "progress", "completed", "error"]
    subagent_id: str
    subagent_type: str
    description: str
    status: SubagentStatus
    timestamp: datetime
    metadata: Dict[str, Any]

class SubagentTracker:
    """Tracks subagent lifecycle."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.active_subagents: Dict[str, SubagentEvent] = {}
    
    def start_subagent(
        self,
        subagent_type: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register a new subagent."""
        subagent_id = self._generate_id()
        event = SubagentEvent(
            event_type="started",
            subagent_id=subagent_id,
            subagent_type=subagent_type,
            description=description,
            status=SubagentStatus.ACTIVE,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.active_subagents[subagent_id] = event
        self.event_bus.emit("subagent_started", event)
        
        return subagent_id
    
    def update_progress(
        self,
        subagent_id: str,
        progress: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update subagent progress."""
        pass
    
    def complete_subagent(
        self,
        subagent_id: str,
        result: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Mark subagent as completed."""
        pass
    
    def error_subagent(
        self,
        subagent_id: str,
        error: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Mark subagent as errored."""
        pass
```

**Tracking Middleware**:
```python
# myagents_framework/middleware/tracking_middleware.py

class TrackingMiddleware(AgentMiddleware):
    """Middleware for subagent tracking."""
    
    def __init__(self, tracker: SubagentTracker):
        self.tracker = tracker
        self.current_subagent_id: Optional[str] = None
    
    async def on_agent_start(self, agent_state: AgentState) -> None:
        """Track agent start."""
        if agent_state.is_subagent:
            self.current_subagent_id = self.tracker.start_subagent(
                subagent_type=agent_state.agent_name,
                description=agent_state.task_description,
                metadata={"thread_id": agent_state.thread_id}
            )
    
    async def on_agent_end(self, agent_state: AgentState) -> None:
        """Track agent completion."""
        if self.current_subagent_id:
            self.tracker.complete_subagent(
                self.current_subagent_id,
                result=agent_state.final_output
            )
```

---

### 4.5 QA Review Workflow

**Purpose**: Mandatory quality assurance before final delivery

**Implementation**:
```python
# myagents_framework/workflows/qa_workflow.py

from dataclasses import dataclass
from typing import Literal, List, Dict, Any

CompletionStatus = Literal["COMPLETE", "PARTIALLY_COMPLETE", "INCOMPLETE"]

@dataclass
class QAReviewResult:
    """QA review result."""
    status: CompletionStatus
    gaps: List[str]
    quality_issues: List[str]
    recommendations: List[str]
    requires_improvement: bool

class QAWorkflow:
    """Manages QA review workflow."""
    
    def __init__(
        self,
        qa_reviewer_config: SubAgent,
        memory_manager: MemoryManager
    ):
        self.qa_reviewer_config = qa_reviewer_config
        self.memory_manager = memory_manager
    
    async def review_completion(
        self,
        thread_id: str,
        agent_name: str,
        user_request: str,
        agent_outputs: List[str],
        files_created: List[str]
    ) -> QAReviewResult:
        """Review task completion."""
        # Get conversation context
        context = self.memory_manager.get_context_summary(
            thread_id, agent_name
        )
        
        # Spawn QA reviewer subagent
        qa_prompt = self._build_qa_prompt(
            user_request, agent_outputs, files_created, context
        )
        
        # Execute QA review
        result = await self._execute_qa_review(qa_prompt)
        
        return result
    
    def _build_qa_prompt(
        self,
        user_request: str,
        agent_outputs: List[str],
        files_created: List[str],
        context: str
    ) -> str:
        """Build QA review prompt."""
        return f"""
        # QA Review Task
        
        ## Original User Request
        {user_request}
        
        ## Agent Outputs
        {chr(10).join(agent_outputs)}
        
        ## Files Created
        {chr(10).join(files_created)}
        
        ## Conversation Context
        {context}
        
        ## Your Task
        Analyze if the user's needs are fully satisfied. Provide:
        1. Completion status (COMPLETE, PARTIALLY_COMPLETE, INCOMPLETE)
        2. List of gaps or missing elements
        3. Quality issues found
        4. Recommendations for improvement
        """
```

**QA Middleware**:
```python
# myagents_framework/middleware/qa_middleware.py

class QAMiddleware(AgentMiddleware):
    """Middleware for automatic QA review."""
    
    def __init__(
        self,
        qa_workflow: QAWorkflow,
        mandatory: bool = True
    ):
        self.qa_workflow = qa_workflow
        self.mandatory = mandatory
    
    async def on_agent_end(self, agent_state: AgentState) -> None:
        """Trigger QA review before final delivery."""
        if not agent_state.is_subagent and self.mandatory:
            # Perform QA review
            result = await self.qa_workflow.review_completion(
                thread_id=agent_state.thread_id,
                agent_name=agent_state.agent_name,
                user_request=agent_state.initial_request,
                agent_outputs=agent_state.outputs,
                files_created=agent_state.files_created
            )
            
            # Handle incomplete work
            if result.requires_improvement:
                # Ask user for approval to improve
                approved = await self._ask_user_approval(result)
                if approved:
                    # Continue execution with improvements
                    agent_state.continue_execution = True
                    agent_state.improvement_plan = result.recommendations
```

---

### 4.6 Real File Management

**Purpose**: Manage actual filesystem files with security

**Implementation**:
```python
# myagents_framework/files/real_file_manager.py

from pathlib import Path
from typing import Optional, List
import os

class RealFileManager:
    """Manages real filesystem files."""
    
    def __init__(
        self,
        workspace_root: Path,
        allowed_extensions: Optional[List[str]] = None,
        max_file_size: int = 10 * 1024 * 1024  # 10MB
    ):
        self.workspace_root = workspace_root
        self.allowed_extensions = allowed_extensions
        self.max_file_size = max_file_size
        
        # Ensure workspace exists
        self.workspace_root.mkdir(parents=True, exist_ok=True)
    
    def write_file(
        self,
        relative_path: str,
        content: str,
        create_dirs: bool = True
    ) -> Path:
        """Write content to a real file."""
        # Security: Validate path is within workspace
        full_path = self._validate_path(relative_path)
        
        # Security: Check file size
        if len(content.encode('utf-8')) > self.max_file_size:
            raise ValueError(f"File size exceeds limit: {self.max_file_size}")
        
        # Security: Check extension
        if self.allowed_extensions:
            if full_path.suffix not in self.allowed_extensions:
                raise ValueError(f"File extension not allowed: {full_path.suffix}")
        
        # Create parent directories
        if create_dirs:
            full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        full_path.write_text(content, encoding='utf-8')
        
        return full_path
    
    def read_file(self, relative_path: str) -> str:
        """Read content from a real file."""
        full_path = self._validate_path(relative_path)
        return full_path.read_text(encoding='utf-8')
    
    def list_files(
        self,
        directory: str = ".",
        pattern: str = "*",
        recursive: bool = False
    ) -> List[Path]:
        """List files in directory."""
        dir_path = self._validate_path(directory)
        
        if recursive:
            return list(dir_path.rglob(pattern))
        else:
            return list(dir_path.glob(pattern))
    
    def _validate_path(self, relative_path: str) -> Path:
        """Validate path is within workspace."""
        full_path = (self.workspace_root / relative_path).resolve()
        
        # Security: Prevent directory traversal
        if not str(full_path).startswith(str(self.workspace_root.resolve())):
            raise ValueError(f"Path outside workspace: {relative_path}")
        
        return full_path
```

**Real File Tools**:
```python
# myagents_framework/tools/real_file_tools.py

from langchain_core.tools import tool

@tool
def write_real_file(
    path: str,
    content: str,
    thread_id: str,
    agent_name: str = "unknown"
) -> str:
    """Write content to a real file on the filesystem."""
    file_manager = get_real_file_manager(thread_id)
    memory_manager = get_memory_manager(thread_id)
    
    # Write to real filesystem
    full_path = file_manager.write_file(path, content)
    
    # Create memory entry
    memory_manager.create_memory(
        thread_id=thread_id,
        agent_name=agent_name,
        content=f"Created real file: {full_path}",
        classification=MemoryClassification.FILE_OPERATION,
        importance=MemoryImportance.MEDIUM,
        metadata={"file_path": str(full_path), "file_size": len(content)}
    )
    
    return f"✅ File written to: {full_path}"

@tool
def read_real_file(
    path: str,
    thread_id: str,
    agent_name: str = "unknown"
) -> str:
    """Read content from a real file on the filesystem."""
    file_manager = get_real_file_manager(thread_id)
    return file_manager.read_file(path)

@tool
def list_real_files(
    directory: str = ".",
    pattern: str = "*",
    recursive: bool = False,
    thread_id: str = None
) -> str:
    """List real files in a directory."""
    file_manager = get_real_file_manager(thread_id)
    files = file_manager.list_files(directory, pattern, recursive)
    
    result = f"📁 **Files in {directory}** ({len(files)} files):\n\n"
    for file_path in files:
        size = file_path.stat().st_size
        size_str = f"{size/1024:.1f} KB" if size > 1024 else f"{size} B"
        result += f"- {file_path.relative_to(file_manager.workspace_root)} ({size_str})\n"
    
    return result
```

---

## 5. Project Structure

### 5.1 Complete Directory Structure

```
MyAgents/
├── MyAgents_Backend/
│   ├── pyproject.toml
│   ├── README.md
│   ├── .gitignore
│   │
│   ├── src/
│   │   └── myagents_framework/
│   │       ├── __init__.py
│   │       ├── version.py
│   │       │
│   │       ├── core/
│   │       │   ├── __init__.py
│   │       │   ├── agent.py              # Base agent class
│   │       │   ├── middleware.py         # Middleware base classes
│   │       │   ├── state.py              # State schemas
│   │       │   └── types.py              # Type definitions
│   │       │
│   │       ├── registry/
│   │       │   ├── __init__.py
│   │       │   ├── agent_registry.py     # Multi-agent registry
│   │       │   ├── agent_factory.py      # Dynamic agent creation
│   │       │   └── config_schema.py      # Configuration schemas
│   │       │
│   │       ├── memory/
│   │       │   ├── __init__.py
│   │       │   ├── memory_manager.py     # Memory coordination
│   │       │   ├── thread_memory.py      # Thread-specific memory
│   │       │   ├── cross_agent_manager.py # Cross-agent context
│   │       │   ├── search_engine.py      # Semantic search
│   │       │   └── storage.py            # Storage backends
│   │       │
│   │       ├── permissions/
│   │       │   ├── __init__.py
│   │       │   ├── permission_engine.py  # Permission management
│   │       │   ├── rules.py              # Permission rules
│   │       │   └── callbacks.py          # Permission callbacks
│   │       │
│   │       ├── hooks/
│   │       │   ├── __init__.py
│   │       │   ├── hook_engine.py        # Hook management
│   │       │   ├── matchers.py           # Hook matchers
│   │       │   └── callbacks.py          # Hook callbacks
│   │       │
│   │       ├── tracking/
│   │       │   ├── __init__.py
│   │       │   ├── subagent_tracker.py   # Subagent lifecycle
│   │       │   ├── event_bus.py          # Event system
│   │       │   └── metrics.py            # Performance metrics
│   │       │
│   │       ├── files/
│   │       │   ├── __init__.py
│   │       │   ├── virtual_file_manager.py  # Virtual files
│   │       │   ├── real_file_manager.py     # Real files
│   │       │   └── file_versioning.py       # Version control
│   │       │
│   │       ├── middleware/
│   │       │   ├── __init__.py
│   │       │   ├── planning_middleware.py
│   │       │   ├── filesystem_middleware.py
│   │       │   ├── subagent_middleware.py
│   │       │   ├── memory_middleware.py
│   │       │   ├── permission_middleware.py
│   │       │   ├── hook_middleware.py
│   │       │   ├── tracking_middleware.py
│   │       │   ├── qa_middleware.py
│   │       │   ├── summarization_middleware.py
│   │       │   └── caching_middleware.py
│   │       │
│   │       ├── tools/
│   │       │   ├── __init__.py
│   │       │   ├── base.py               # Tool base classes
│   │       │   ├── memory_tools.py       # Memory tools
│   │       │   ├── file_tools.py         # File tools
│   │       │   ├── real_file_tools.py    # Real file tools
│   │       │   └── planning_tools.py     # Planning tools
│   │       │
│   │       ├── workflows/
│   │       │   ├── __init__.py
│   │       │   ├── qa_workflow.py        # QA review workflow
│   │       │   ├── planning_workflow.py  # Planning workflow
│   │       │   └── templates.py          # Workflow templates
│   │       │
│   │       ├── integrations/
│   │       │   ├── __init__.py
│   │       │   ├── mcp/                  # MCP integration
│   │       │   │   ├── __init__.py
│   │       │   │   ├── server.py
│   │       │   │   └── client.py
│   │       │   └── external_apis/        # External API wrappers
│   │       │       ├── __init__.py
│   │       │       ├── search.py
│   │       │       └── research.py
│   │       │
│   │       ├── config/
│   │       │   ├── __init__.py
│   │       │   ├── settings.py           # Global settings
│   │       │   ├── prompts.py            # System prompts
│   │       │   └── checkpointer.py       # State persistence
│   │       │
│   │       └── utils/
│   │           ├── __init__.py
│   │           ├── helpers.py
│   │           ├── logging.py
│   │           └── validation.py
│   │
│   ├── Agents/
│   │   ├── __init__.py
│   │   ├── agents.json                   # Agent configurations
│   │   ├── main_agent.py                 # Main agent
│   │   ├── research_agent.py             # Research agent
│   │   ├── writing_agent.py              # Writing agent
│   │   └── ...                           # Other agents
│   │
│   ├── subagents/
│   │   ├── __init__.py
│   │   ├── planning_coordinator.py
│   │   ├── qa_reviewer.py
│   │   ├── literature_screener.py
│   │   └── ...                           # Other subagents
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search/
│   │   │   ├── __init__.py
│   │   │   ├── tavily_search.py
│   │   │   └── academic_search.py
│   │   ├── research/
│   │   │   ├── __init__.py
│   │   │   └── core_api.py
│   │   └── ...                           # Other tool categories
│   │
│   ├── config/
│   │   ├── agents.json                   # Agent registry
│   │   ├── prompts.py                    # Agent prompts
│   │   └── settings.py                   # Application settings
│   │
│   ├── data/
│   │   ├── checkpoints/                  # State persistence
│   │   └── workspaces/                   # User workspaces
│   │
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── e2e/
│
└── MyAgents_Frontend/
    ├── package.json
    ├── next.config.js
    ├── tsconfig.json
    │
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx
    │   │   ├── page.tsx
    │   │   ├── chat/
    │   │   ├── research/
    │   │   └── ...
    │   │
    │   ├── components/
    │   │   ├── ChatInterface/
    │   │   ├── SubAgentPanel/
    │   │   ├── ActiveSubAgentsPanel/
    │   │   └── ...
    │   │
    │   ├── lib/
    │   │   ├── agents/
    │   │   │   └── config.ts
    │   │   └── utils/
    │   │
    │   └── types/
    │       └── types.ts
    │
    └── public/
        └── ...
```

---

## 6. Implementation Plan

### Phase 1: Foundation (Week 1-2)

**Goal**: Set up project structure and core framework

**Tasks**:
1. ✅ Create project structure
   - Initialize `MyAgents/MyAgents_Backend/` with proper structure
   - Set up `pyproject.toml` with dependencies
   - Create `src/myagents_framework/` package

2. ✅ Port DeepAgents (New) as base
   - Copy middleware architecture from `references/src/deepagents/`
   - Adapt to MyAgents structure
   - Add backwards compatibility layer

3. ✅ Implement core middleware
   - `PlanningMiddleware`
   - `FilesystemMiddleware`
   - `SubAgentMiddleware`
   - `SummarizationMiddleware`
   - `CachingMiddleware`

4. ✅ Create agent registry system
   - Port from `backend/config/agent_registry.py`
   - Enhance with middleware support
   - Add JSON configuration loading

**Deliverables**:
- Working base framework with middleware
- Agent registry with dynamic creation
- Basic agent creation working

---

### Phase 2: Memory & Tracking (Week 3-4)

**Goal**: Add intelligent memory and observability

**Tasks**:
1. ✅ Implement memory system
   - Port from `backend/core/memory/`
   - Create `MemoryManager`, `CrossAgentManager`, `SearchEngine`
   - Add `MemoryMiddleware`

2. ✅ Implement subagent tracking
   - Port from `backend/tools/subagent_tracker.py`
   - Create `SubagentTracker` and `EventBus`
   - Add `TrackingMiddleware`

3. ✅ Add metrics collection
   - Create `MetricsCollector`
   - Track performance, costs, latency
   - Add metrics middleware

**Deliverables**:
- Working memory system with semantic search
- Subagent tracking with event emission
- Performance metrics collection

---

### Phase 3: Permissions & Hooks (Week 5-6)

**Goal**: Add permission system and lifecycle hooks

**Tasks**:
1. ✅ Implement permission engine
   - Adapt from Claude SDK
   - Create `PermissionEngine` and `PermissionMiddleware`
   - Add tool-level and subagent-level permissions

2. ✅ Implement hook system
   - Adapt from Claude SDK
   - Create `HookEngine` and `HookMiddleware`
   - Support all hook events

3. ✅ Add human-in-the-loop
   - Enhance existing HITL implementation
   - Integrate with permission system
   - Add UI approval flows

**Deliverables**:
- Working permission system
- Hook system with all events
- Enhanced HITL with permissions

---

### Phase 4: QA & File Management (Week 7-8)

**Goal**: Add QA workflow and real file management

**Tasks**:
1. ✅ Implement QA workflow
   - Port from `backend/subagents/qa_reviewer.py`
   - Create `QAWorkflow` and `QAMiddleware`
   - Add mandatory review option

2. ✅ Implement real file management
   - Create `RealFileManager`
   - Add security (sandboxing, validation)
   - Create real file tools
   - Integrate with memory system

3. ✅ Add file versioning
   - Track file changes
   - Support rollback
   - Show file history

**Deliverables**:
- Working QA workflow
- Real file management with security
- File versioning system

---

### Phase 5: Workflow Templates (Week 9-10)

**Goal**: Create reusable workflow templates

**Tasks**:
1. ✅ Create workflow template system
   - Base `WorkflowTemplate` class
   - Template configuration format

2. ✅ Implement domain templates
   - `ResearchWorkflow`
   - `WritingWorkflow`
   - `BusinessAutomationWorkflow`
   - `CodingWorkflow`

3. ✅ Add template customization
   - Template parameters
   - Dynamic subagent selection
   - Conditional steps

**Deliverables**:
- Workflow template system
- 4+ domain-specific templates
- Template customization API

---

### Phase 6: Frontend Integration (Week 11-12)

**Goal**: Integrate backend with frontend

**Tasks**:
1. ✅ Update frontend for new backend
   - Adapt to new API
   - Add subagent visualization
   - Add permission prompts

2. ✅ Add new UI features
   - File browser (virtual + real)
   - Workspace selector
   - Permission manager
   - Hook configuration

3. ✅ Testing & debugging
   - End-to-end testing
   - Fix integration issues
   - Performance optimization

**Deliverables**:
- Fully integrated frontend
- New UI components
- Working end-to-end system

---

### Phase 7: Documentation & Testing (Week 13-14)

**Goal**: Complete documentation and testing

**Tasks**:
1. ✅ Write comprehensive documentation
   - API documentation
   - Usage guides
   - Best practices
   - Migration guide

2. ✅ Create examples
   - Simple agent example
   - Research workflow example
   - Writing workflow example
   - Custom middleware example

3. ✅ Add tests
   - Unit tests (80%+ coverage)
   - Integration tests
   - E2E tests
   - Performance tests

**Deliverables**:
- Complete documentation
- Example projects
- Comprehensive test suite

---

## 7. API Design

### 7.1 Simple API (For Quick Start)

```python
from myagents_framework import create_agent, AgentConfig

# Simplest usage
agent = create_agent(
    name="My Agent",
    instructions="You are a helpful assistant.",
    tools=["web_search"]
)

# With configuration
config = AgentConfig(
    name="Research Assistant",
    type="research",
    instructions="You are a research specialist...",
    tools=["academic_search", "web_search"],
    enable_memory=True,
    enable_qa_review=True
)
agent = create_agent(config)

# Run agent
result = agent.run("Conduct a literature review on AI safety")
```

### 7.2 Advanced API (For Full Control)

```python
from myagents_framework import (
    AgentBuilder,
    MemoryMiddleware,
    PermissionMiddleware,
    QAMiddleware,
    SubAgent
)

# Create agent with full control
builder = AgentBuilder()

# Configure middleware
builder.add_middleware(MemoryMiddleware(
    auto_create_on=["tool_use", "decision"]
))
builder.add_middleware(PermissionMiddleware(
    mode="plan",
    tool_permissions={"delete_file": "deny"}
))
builder.add_middleware(QAMiddleware(mandatory=True))

# Add tools
builder.add_tools([
    "web_search",
    "academic_search",
    "write_real_file"
])

# Add subagents
builder.add_subagent(SubAgent(
    name="literature_screener",
    description="Screen papers for relevance",
    prompt="You are a literature screening specialist...",
    tools=["academic_search"]
))

# Configure permissions
builder.set_permission_callback(async def can_use_tool(
    tool_name: str,
    tool_args: dict,
    context: PermissionContext
) -> PermissionResult:
    if tool_name == "delete_file":
        # Always ask user
        return await prompt_user(f"Delete {tool_args['path']}?")
    return PermissionResultAllow()
)

# Add hooks
builder.add_hook("PreToolUse", async def on_tool_use(
    input_data: dict,
    tool_use_id: str,
    context: HookContext
) -> HookOutput:
    # Log tool usage
    logger.info(f"Tool used: {input_data['tool_name']}")
    return HookOutput(decision="continue")
)

# Build agent
agent = builder.build()

# Run with streaming
async for event in agent.stream("Your task here"):
    if event.type == "subagent_started":
        print(f"Subagent started: {event.data['name']}")
    elif event.type == "tool_use":
        print(f"Tool used: {event.data['tool_name']}")
    elif event.type == "message":
        print(event.data['content'])
```

### 7.3 Registry API (For Multi-Agent)

```python
from myagents_framework import AgentRegistry

# Load from configuration
registry = AgentRegistry.from_file("agents.json")

# List available agents
agents = registry.list_agents()
for agent_config in agents:
    print(f"{agent_config.name}: {agent_config.description}")

# Create agent by ID
agent = registry.create_agent("research-assistant")

# Create all agents
all_agents = registry.create_all_agents()

# Register new agent
registry.register_agent(AgentConfig(
    id="custom-agent",
    name="Custom Agent",
    type="custom",
    instructions="...",
    tools=["tool1", "tool2"]
))

# Update agent
registry.update_agent("custom-agent", updated_config)
```

### 7.4 Workflow API (For Templates)

```python
from myagents_framework.workflows import (
    ResearchWorkflow,
    WritingWorkflow,
    WorkflowBuilder
)

# Use predefined workflow
workflow = ResearchWorkflow(
    enable_qa_review=True,
    enable_memory=True
)
agent = workflow.create_agent()

# Customize workflow
workflow = ResearchWorkflow()
workflow.add_subagent("custom_analyzer")
workflow.set_hitl_points(["planning_coordinator", "synthesis_engine"])
agent = workflow.create_agent()

# Build custom workflow
builder = WorkflowBuilder()
builder.add_stage("validation", subagent="request_validator")
builder.add_stage("planning", subagent="planning_coordinator", hitl=True)
builder.add_stage("execution", subagents=["screener", "analyzer"])
builder.add_stage("synthesis", subagent="synthesis_engine")
builder.add_stage("qa", subagent="qa_reviewer", mandatory=True)
workflow = builder.build()
agent = workflow.create_agent()
```

---

## 8. Migration Guide

### 8.1 From Current MyAgents

**Minimal Migration** (No code changes):
```python
# Old (current MyAgents)
from src.deepagents import create_deep_agent

agent = create_deep_agent(
    tools=[...],
    instructions="...",
    subagents=[...]
)

# New (MyAgents v1.1) - Same API
from myagents_framework import create_deep_agent

agent = create_deep_agent(
    tools=[...],
    instructions="...",
    subagents=[...]
)
```

**Opt-In Features**:
```python
# Add new features incrementally
from myagents_framework import create_agent, AgentConfig

agent = create_agent(AgentConfig(
    name="My Agent",
    instructions="...",
    tools=[...],
    subagents=[...],
    # New features
    enable_memory=True,
    enable_tracking=True,
    enable_qa_review=True,
    enable_real_files=True,
    workspace_path="/path/to/workspace"
))
```

**Full Migration**:
```python
# Use registry for multi-agent
from myagents_framework import AgentRegistry

registry = AgentRegistry.from_file("agents.json")
agent = registry.create_agent("my-agent")
```

### 8.2 From DeepAgents (Original)

```python
# Old (DeepAgents)
from deepagents import create_deep_agent

agent = create_deep_agent(
    tools=[...],
    instructions="..."
)

# New (MyAgents v1.1) - Enhanced
from myagents_framework import create_agent, AgentConfig

agent = create_agent(AgentConfig(
    name="My Agent",
    instructions="...",
    tools=[...],
    # Automatic enhancements
    enable_memory=True,      # Semantic memory
    enable_tracking=True,    # Subagent tracking
    enable_qa_review=True   # Quality assurance
))
```

---

## 9. Roadmap

### Q1 2025: Foundation
- ✅ Core framework with middleware
- ✅ Multi-agent registry
- ✅ Memory system
- ✅ Subagent tracking

### Q2 2025: Advanced Features
- ✅ Permission & hook system
- ✅ QA workflow
- ✅ Real file management
- ✅ Workflow templates

### Q3 2025: Ecosystem
- 🔄 MCP integration
- 🔄 Plugin marketplace
- 🔄 Template library
- 🔄 Community tools

### Q4 2025: Enterprise
- 🔄 Team collaboration
- 🔄 Access control
- 🔄 Audit logging
- 🔄 Compliance features

---

## 10. Conclusion

MyAgents Framework v1.1 represents the **next generation of multi-agent AI systems**, combining:

✅ **Best-in-class architecture** from DeepAgents middleware  
✅ **Production-tested features** from current MyAgents  
✅ **Sophisticated control** from Claude Agent SDK  
✅ **Novel innovations** for complex task execution  

**Key Differentiators**:
1. **Middleware-based extensibility** - Clean, composable architecture
2. **Intelligent memory** - Semantic context across agents and sessions
3. **Complete observability** - Full lifecycle tracking and visualization
4. **Granular permissions** - Tool and subagent-level access control
5. **Quality assurance** - Built-in QA workflow for high-quality outputs
6. **Real file management** - Secure filesystem operations
7. **Workflow templates** - Reusable patterns for common tasks

**Target Audience**:
- Researchers conducting systematic literature reviews
- Writers creating long-form content (novels, series)
- Business analysts automating workflows
- Developers building AI-powered applications
- Data scientists analyzing complex datasets

**Next Steps**:
1. Review and approve this design
2. Begin Phase 1 implementation
3. Set up development environment
4. Create initial project structure
5. Start porting DeepAgents (New) as base

---

**Ready to build the future of multi-agent AI? Let's get started! 🚀**
