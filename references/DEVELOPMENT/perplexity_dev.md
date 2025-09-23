# Perplexity AI Integration Framework - DeepAgents Compatible

## Overview
This document outlines the comprehensive integration of Perplexity AI capabilities into the MyAgents system using the DeepAgents framework. The plan extends existing functionality in `backend/tools/search/perplexity.py` while maintaining compatibility with DeepAgents' built-in planning tools (`write_todos`, `task`, filesystem tools) and `BASE_AGENT_PROMPT`.

## DeepAgents Integration Principles
- **Extend, Don't Replace**: Build upon existing `backend/tools/search/perplexity.py` tools
- **Framework Compliance**: All components must work within DeepAgents' `create_deep_agent()` pattern
- **Built-in Tool Usage**: Leverage `write_todos` for planning, `task` for subagent spawning, filesystem tools for persistence
- **Environment Management**: All secrets from `backend/.env`, configuration via `backend/config/settings.py`
- **Prompt Management**: Subagent prompts in `backend/config/prompts.py`, rely on auto-appended `BASE_AGENT_PROMPT`

## Revised Project Structure (DeepAgents Compatible)
```
backend/
├── tools/
│   └── search/
│       ├── perplexity.py              # EXISTING - extend with routing/schema
│       ├── perplexity_client.py       # NEW - centralized client with routing
│       ├── perplexity_strategies.py   # NEW - specialized search strategies
│       └── perplexity_config.py       # NEW - routing policies and budgets
│
├── subagents/
│   ├── deep_research_agent.py         # NEW - long-horizon research
│   ├── market_analysis_agent.py       # NEW - market research specialist
│   └── technical_research_agent.py    # NEW - technical documentation research
│
├── config/
│   ├── prompts.py                     # EXTEND - add subagent prompts
│   └── settings.py                    # EXTEND - add Perplexity config
│
└── agents/
    └── main_agent.py                  # EXTEND - register new subagents
```

## Perplexity Model Routing Policy

### Task-to-Model Routing Matrix
| Task Type | Primary Model | Fallback | Use Case |
|-----------|---------------|----------|----------|
| General Q&A | `sonar_pro` | `sonar` | Balanced cost/latency |
| Multi-step reasoning | `sonar_reasoning` | `sonar_pro` | Chain-of-thought analysis |
| Critical analysis | `sonar_reasoning_pro` | `sonar_reasoning` | High-stakes decisions |
| Deep research | `sonar_deep_research` | `sonar_reasoning_pro` | Multi-source synthesis |

### Filter and Budget Configuration
```python
# In backend/tools/search/perplexity_config.py
ROUTING_CONFIG = {
    "models": {
        "sonar_pro": {"max_tokens": 2000, "max_latency": 3000},
        "sonar_reasoning": {"max_tokens": 4000, "max_latency": 8000},
        "sonar_reasoning_pro": {"max_tokens": 6000, "max_latency": 12000},
        "sonar_deep_research": {"max_tokens": 16000, "max_latency": 45000}
    },
    "filters": {
        "domain_allowlist": ["arxiv.org", "github.com", "docs.python.org"],
        "domain_denylist": ["content-farm.com", "low-quality-aggregator.net"],
        "date_ranges": {"recent": "7d", "current": "30d", "extended": "90d"},
        "source_quality_threshold": 0.7
    },
    "budgets": {
        "normal": {"tokens": 2000, "cost": 0.10, "latency": 3000},
        "pro": {"tokens": 4000, "cost": 0.25, "latency": 8000},
        "deep": {"tokens": 16000, "cost": 1.00, "latency": 45000}
    }
}
```

## Standardized Return Schema

All Perplexity tools must return this consistent structure:

```python
{
    "status": "ok" | "error",
    "query": str,
    "model": str,
    "params": {
        "date_range": str,
        "domains": List[str],
        "depth": int,
        "temperature": float
    },
    "answer": str,  # Concise synthesis for user
    "reasoning_summary": str,  # Brief methodology, not chain-of-thought
    "citations": [
        {
            "title": str,
            "url": str,
            "snippet": str,
            "published_at": str | None,
            "source_type": "primary" | "secondary" | "tertiary",
            "quality_score": float  # 0-1
        }
    ],
    "results": List[dict],  # Raw API results (trimmed)
    "usage": {
        "prompt_tokens": int,
        "completion_tokens": int,
        "total_tokens": int,
        "cost_estimate": float
    },
    "timing": {
        "started_at": str,  # ISO timestamp
        "completed_at": str,
        "latency_ms": int
    },
    "error": str | None,
    "debug": dict  # Internal diagnostics
}
```

## Core Architecture

### 1. Enhanced Tools Layer (`/tools/search/`)

#### 1.1 Perplexity Client Infrastructure
- **`perplexity_client.py`**: Centralized client with authentication, routing, and error handling
- **`perplexity_strategies.py`**: Specialized search patterns (academic, technical, market)
- **`perplexity_config.py`**: Routing policies, budgets, and filter configurations
- **`perplexity.py`** (EXISTING): Extend to use new client and return standardized schema

#### 1.2 Strategy Functions
```python
# In perplexity_strategies.py
def academic_search(query: str, **kwargs) -> dict
def technical_search(query: str, **kwargs) -> dict
def market_research(query: str, **kwargs) -> dict
def deep_research(query: str, **kwargs) -> dict
```

### 2. Specialized Subagents (`/subagents/`)

#### 2.1 Deep Research Agent
- **File**: `backend/subagents/deep_research_agent.py`
- **Name**: `"deep-research"`
- **Description**: "Conducts long-horizon, source-backed web research with citations and synthesis"
- **Tools**: `perplexity_reasoning_search`, `perplexity_focused_research`
- **Prompt**: Focused on multi-source validation and synthesis (stored in `config/prompts.py`)

#### 2.2 Market Analysis Agent
- **File**: `backend/subagents/market_analysis_agent.py`
- **Name**: `"market-analysis"`
- **Description**: "Specialized in market trends, competitive analysis, and business intelligence"
- **Tools**: Perplexity tools + market-specific filters
- **Prompt**: Market research methodology and validation

#### 2.3 Technical Research Agent
- **File**: `backend/subagents/technical_research_agent.py`
- **Name**: `"technical-research"`
- **Description**: "Technical documentation, API research, and developer-focused analysis"
- **Tools**: Perplexity tools with technical domain filters
- **Prompt**: Technical accuracy and code example validation

### 3. DeepAgents Workflow Integration

#### 3.1 Planning Integration
- **Simple Tasks**: Direct tool usage, skip `write_todos`
- **Complex Tasks**: 
  1. Discovery phase (identify subtopics, select models/filters)
  2. Planning with `write_todos` (concrete steps, tool/subagent assignments)
  3. Execution with `task` spawning for parallel research
  4. Synthesis and validation

#### 3.2 Subagent Spawning Pattern
```python
# Main agent spawns parallel research tasks
task_results = await asyncio.gather(
    task("deep-research", "Research AI model performance benchmarks"),
    task("market-analysis", "Analyze AI model market adoption"),
    task("technical-research", "Compare API specifications")
)
# Synthesize results with citations
```

### 4. Credit System Integration

#### 4.1 Usage Tracking
- Map Perplexity model usage to MyAgents credit tiers:
  - **Normal Mode**: sonar_pro (1-2 credits)
  - **Pro Mode**: sonar_reasoning (3-5 credits)  
  - **Deep Mode**: sonar_deep_research (5-10 credits)

#### 4.2 Budget Enforcement
- Pre-flight credit checks before expensive operations
- Graceful degradation (cheaper model) when approaching limits
- Usage reporting in tool return schema

## DeepAgents Framework Compliance

### Environment and Configuration
- **Secrets Management**: All Perplexity API keys in `backend/.env`
- **Configuration**: Routing policies and budgets in `backend/config/settings.py`
- **Prompt Management**: Subagent prompts in `backend/config/prompts.py`
- **Model Selection**: Use `backend/models/` for model configuration

### Tool Requirements
- **Decorator**: All tools use `@tool` decorator with clear docstrings
- **Error Handling**: Return standardized schema even on errors
- **Type Safety**: Explicit parameter types and return annotations
- **Registration**: Register in appropriate `create_*_agent()` functions

### Subagent Requirements
- **Return Format**: Must return `SubAgent` instance from creator function
- **Prompt Focus**: Keep prompts minimal and specialty-focused
- **Tool Selection**: Only include tools needed for the subagent's role
- **Model Override**: Optional model configuration for specialized needs

### Planning and Execution
- **Complexity Assessment**: Use heuristics to determine if `write_todos` needed
- **Task Spawning**: Use `task` tool for parallel, independent research
- **Progress Tracking**: Update todos promptly as steps complete
- **Context Management**: Keep main thread lean, delegate heavy work to subagents

## Development Roadmap (Revised)

### Phase 1: Foundation (Week 1-2)
- [ ] **Extend existing tools**
  - [ ] Update `backend/tools/search/perplexity.py` to return standardized schema
  - [ ] Create `perplexity_client.py` with routing and authentication
  - [ ] Implement `perplexity_config.py` with routing policies
  - [ ] Add Perplexity configuration to `backend/config/settings.py`

- [ ] **Create core subagent**
  - [ ] Implement `deep_research_agent.py` with minimal prompt
  - [ ] Add `DEEP_RESEARCH_PROMPT` to `backend/config/prompts.py`
  - [ ] Register subagent in `backend/agents/main_agent.py`
  - [ ] Test basic functionality with existing tools

### Phase 2: Specialization (Week 3-4)
- [ ] **Add specialized subagents**
  - [ ] Create `market_analysis_agent.py` with market-focused tools
  - [ ] Create `technical_research_agent.py` with technical domain filters
  - [ ] Add corresponding prompts to `config/prompts.py`
  - [ ] Register all subagents in main agent

- [ ] **Implement strategy functions**
  - [ ] Create `perplexity_strategies.py` with specialized search patterns
  - [ ] Implement academic, technical, and market research strategies
  - [ ] Add strategy selection logic to routing system

### Phase 3: Integration and Optimization (Week 5-6)
- [ ] **Credit system integration**
  - [ ] Map Perplexity models to MyAgents credit tiers
  - [ ] Implement budget enforcement and graceful degradation
  - [ ] Add usage tracking to tool return schemas

- [ ] **Performance optimization**
  - [ ] Implement caching for frequent queries
  - [ ] Add rate limiting and circuit breaker patterns
  - [ ] Optimize parallel subagent spawning

- [ ] **Quality assurance**
  - [ ] Add comprehensive error handling and recovery
  - [ ] Implement source quality scoring
  - [ ] Add monitoring and alerting for API usage

### Phase 4: Advanced Features (Week 7-8)
- [ ] **Enhanced capabilities**
  - [ ] Add domain-specific filter presets
  - [ ] Implement citation validation and deduplication
  - [ ] Add result synthesis and summarization tools

- [ ] **Monitoring and analytics**
  - [ ] Track subagent performance and effectiveness
  - [ ] Monitor API costs and usage patterns
  - [ ] Implement quality metrics and scoring

## Implementation Checklist

### For Each New Tool
- [ ] Implements `@tool` decorator with clear docstring
- [ ] Returns standardized schema (status, answer, citations, usage, timing)
- [ ] Handles errors gracefully and returns error in schema
- [ ] Uses environment variables from `backend/.env`
- [ ] Registered in appropriate agent's tools list
- [ ] Includes type hints and parameter documentation

### For Each New Subagent
- [ ] Creator function returns `SubAgent` instance
- [ ] Prompt stored in `backend/config/prompts.py`
- [ ] Prompt is minimal and specialty-focused
- [ ] Tools list includes only necessary tools
- [ ] Registered in `backend/agents/main_agent.py`
- [ ] Optional model override configured if needed

### For Integration
- [ ] Main agent updated with new subagents
- [ ] Configuration added to `backend/config/settings.py`
- [ ] Environment variables documented in `.env.example`
- [ ] No modifications to `backend/src/deepagents/` source files
- [ ] All components work with DeepAgents' built-in planning tools

## Quality Assurance

### Testing Strategy
- **Unit Tests**: Each tool and subagent creator function
- **Integration Tests**: End-to-end workflows with real API calls
- **Performance Tests**: Latency and cost optimization validation
- **Error Handling**: Network failures, API limits, invalid inputs

### Monitoring
- **API Usage**: Track costs, rate limits, and response times
- **Quality Metrics**: Source quality scores and citation accuracy
- **Performance**: Subagent effectiveness and parallel execution efficiency
- **User Experience**: Response quality and relevance scoring

### Security
- **API Key Management**: Secure storage and rotation
- **Input Validation**: Sanitize all user inputs and queries
- **Output Filtering**: Remove sensitive information from responses
- **Rate Limiting**: Prevent abuse and manage costs