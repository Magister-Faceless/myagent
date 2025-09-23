---
trigger: always_on
---

DeepAgents Backend Development Rules:

Every time developing the backend and making changes to files or folders in C:\Users\netfl\OneDrive\Desktop\myagents\backend, you must always follow these rules:

- Source of truth
  - Always follow the deepagents guideline in [backend/deepagents.README.md](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/deepagents.README.md:0:0-0:0).
  - Do not modify source files under `backend/src/deepagents/` (framework internals).
  - Keep imports at the top of files and follow the framework’s patterns.

- Project structure and locations
  - Main agent files live in `backend/agents/` (e.g., [backend/agents/main_agent.py](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/agents/main_agent.py:0:0-0:0)).
  - Subagents live in `backend/subagents/` with one creator per subagent (e.g., `create_xyz_subagent()`).
  - Tools live in `backend/tools/` grouped by domain (e.g., `backend/tools/search/...`).
  - Prompts for the main agent and subagents live in [backend/config/prompts.py](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/config/prompts.py:0:0-0:0).
  - Models and model selection belong in `backend/models/`.

- Main agent requirements
  - Construct the main agent with [deepagents.create_deep_agent(...)](cci:1://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/graph.py:129:0-183:5) in [backend/agents/main_agent.py](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/agents/main_agent.py:0:0-0:0).
  - Pass `instructions` from [backend/config/prompts.py](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/config/prompts.py:0:0-0:0) (keep them concise and policy-based).
  - Do not paste or duplicate the framework’s long built-in prompt; the framework appends `BASE_AGENT_PROMPT` automatically.
  - Add external tools explicitly in the `tools=[...]` list.
  - Wire subagents by calling their creators from `backend/subagents/` and passing them in `subagents=[...]`.
  - Respect settings (e.g., recursion limit, model selection) via `backend/config/settings.py`.

- Subagent requirements
  - Each subagent has:
    - A unique `name`, concise `description`, and a focused `prompt` (from [backend/config/prompts.py](cci:7://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/config/prompts.py:0:0-0:0)).
    - An optional `tools` list (only those needed for the subagent’s role).
    - An optional model override (use `backend/models/` or a configuration dict).
  - Keep subagent prompts minimal and specialty-focused; do not duplicate built-in tool usage instructions.
  - Subagents are designed to be spawned via the built-in `task` tool; they automatically inherit `BASE_AGENT_PROMPT`.

- Tools requirements
  - Implement tools in `backend/tools/` with clear names, docstrings, and `@tool` decorators.
  - Make tools pure and safe by default; handle and return errors gracefully.
  - Use explicit, typed parameters and return shapes; document defaults and examples in docstrings.
  - Register tools in the main agent (and in subagents when necessary) in their respective `create_*` functions.
  - Do not reimplement built-in planning/filesystem tools. The framework auto-includes:
    - [write_todos](cci:1://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:21:0-32:5), [ls](cci:1://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:35:0-38:46), [read_file](cci:1://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:41:0-83:34), [write_file](cci:1://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:86:0-102:5), [edit_file](cci:1://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:105:0-153:5), and the `task` subagent spawner.

- Environment and secrets
  - All secrets and configuration must be sourced from `backend/.env` (path: [C:\Users\netfl\OneDrive\Desktop\myagents\backend\.env](cci:7://file:///Users/netfl/OneDrive/Desktop/myagents/backend/.env:0:0-0:0)).
  - Never hardcode secrets or read them from the frontend. Centralize env access through `backend/config/settings.py` or a single config loader.
  - Document required environment variables and failure modes for every new tool/subagent/API.

- Planning and execution policy (adaptive)
  - Simple tasks (1–2 trivial steps): execute directly; skip planning.
  - Complex tasks (3+ steps, multiple tools/subagents, external lookups, or file edits):
    - Discovery first: identify relevant prompts/guidance, tools, and subagents; decide ordering and parallelism.
    - Commit plan using [write_todos](cci:1://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:21:0-32:5) (include concrete steps, tools/subagents per step, mark first step(s) `in_progress`).
    - Execute steps; update todos promptly (complete and advance).
    - Use `task` to spawn subagents in parallel for independent subtasks; keep the main thread lean.

- Built-ins usage and prompt management
  - Rely on `BASE_AGENT_PROMPT` (auto-appended by the framework) for comprehensive instructions on planning, `task`, and filesystem tools.
  - Keep `MAIN_AGENT_INSTRUCTIONS` short, focusing on:
    - Complexity assessment policy.
    - “Discovery → Plan ([write_todos](cci:1://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/tools.py:21:0-32:5)) → Execute” sequence for complex tasks.
    - Tool/subagent effectiveness and parallelization principles.
  - Avoid adding long, redundant guidance to custom prompts; load specialized guidance on-demand (e.g., via a future prompt library tool) to preserve context.

- External APIs and MCP
  - Wrap external APIs and MCP integrations as tools or specialized subagents.
  - Keys and endpoints must come from `backend/.env`.
  - Implement timeouts, retries, rate limiting, and error handling.
  - Provide minimal but clear usage descriptions and examples; register them with the main agent or the relevant subagent only.

- Wiring and integration checks
  - When adding a tool: file under `backend/tools/`, import into the appropriate `create_*` function, ensure env access via config, and docstring coverage.
  - When adding a subagent: create under `backend/subagents/`, return a `SubAgent` instance, keep prompt focused, and wire into the main agent’s `subagents=[...]`.
  - When updating the main agent’s file path or name, update `backend/langgraph.json` to keep frontend-backend linkage intact.
  - For any frontend changes, follow `frontend/ui.README.md` (do not guess).

- Prohibited and gotchas
  - Do not modify `backend/src/deepagents/` internals.
  - Do not duplicate or override built-in planning/filesystem tools or the base prompt.
  - Do not bloat prompts with long operational text—prefer dynamic retrieval, docstrings, and built-in guidance.
  - Keep imports at the top of files; maintain consistent, typed interfaces.

- Pre-merge checklist (quick)
  - New components live in the correct directory (`agents/`, `subagents/`, `tools/`).
  - Tools are decorated, documented, tested, and registered.
  - Subagents return proper `SubAgent` specs, with minimal prompts and optional tools/models.
  - Env vars documented and loaded from `backend/.env`.
  - [create_deep_agent(...)](cci:1://file:///c:/Users/netfl/OneDrive/Desktop/myagents/backend/src/deepagents/graph.py:129:0-183:5) usage confirmed; built-ins leveraged; `MAIN_AGENT_INSTRUCTIONS` stays concise.
  - `langgraph.json` updated if the main agent path changed.
  - No edits to `backend/src/deepagents/`.

