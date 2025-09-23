from deepagents.prompts import TASK_TOOL_DESCRIPTION
from deepagents.state import DeepAgentState
try:
    from langgraph.prebuilt import create_react_agent
except ImportError:
    # Fallback for newer versions
    from langgraph.graph import StateGraph
    from langgraph.graph.message import add_messages
    from typing import Annotated
    
    def create_react_agent(model, tools, state_modifier=None, **kwargs):
        """Fallback implementation for create_react_agent."""
        # This is a simplified fallback - you may need to adjust based on your needs
        from langgraph.graph import MessagesState, StateGraph
        
        # Create a basic state graph that can handle the expected interface
        graph = StateGraph(MessagesState)
        
        # Add a simple node that uses the model
        def agent_node(state):
            return {"messages": []}
        
        graph.add_node("agent", agent_node)
        graph.set_entry_point("agent")
        graph.set_finish_point("agent")
        
        return graph.compile()
from langchain_core.tools import BaseTool
from typing_extensions import TypedDict
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langchain_core.language_models import LanguageModelLike
from langchain.chat_models import init_chat_model
from typing import Annotated, NotRequired, Any, Union, Optional, Callable
from langgraph.types import Command
from langchain_core.runnables import Runnable

try:
    from langgraph.prebuilt import InjectedState
except ImportError:
    # Fallback for newer versions
    from typing import Any
    InjectedState = Any


class SubAgent(TypedDict):
    name: str
    description: str
    prompt: str
    tools: NotRequired[list[str]]
    # Optional per-subagent model: can be either a model instance OR dict settings
    model: NotRequired[Union[LanguageModelLike, dict[str, Any]]]


class CustomSubAgent(TypedDict):
    name: str
    description: str
    graph: Runnable


def _get_agents(
    tools,
    instructions,
    subagents: list[SubAgent | CustomSubAgent],
    model,
    state_schema,
    post_model_hook: Optional[Callable] = None,
):
    agents = {
        "general-purpose": create_react_agent(
            model,
            prompt=instructions,
            tools=tools,
            checkpointer=False,
            post_model_hook=post_model_hook,
            state_schema=state_schema,
        )
    }
    tools_by_name = {}
    for tool_ in tools:
        if not isinstance(tool_, BaseTool):
            tool_ = tool(tool_)
        tools_by_name[tool_.name] = tool_
    for _agent in subagents:
        if "graph" in _agent:
            agents[_agent["name"]] = _agent["graph"]
            continue
        if "tools" in _agent:
            _tools = [tools_by_name[t] for t in _agent["tools"]]
        else:
            _tools = tools
        # Resolve per-subagent model: can be instance or dict
        if "model" in _agent:
            agent_model = _agent["model"]
            if isinstance(agent_model, dict):
                # Dictionary settings - create model from config
                sub_model = init_chat_model(**agent_model)
            else:
                # Model instance - use directly
                sub_model = agent_model
        else:
            # Fallback to main model
            sub_model = model
        agents[_agent["name"]] = create_react_agent(
            sub_model,
            prompt=_agent["prompt"],
            tools=_tools,
            state_schema=state_schema,
            checkpointer=False,
            post_model_hook=post_model_hook,
        )
    return agents


def _get_subagent_description(subagents: list[SubAgent | CustomSubAgent]):
    return [f"- {_agent['name']}: {_agent['description']}" for _agent in subagents]


def _create_task_tool(
    tools,
    instructions,
    subagents: list[SubAgent | CustomSubAgent],
    model,
    state_schema,
    post_model_hook: Optional[Callable] = None,
):
    agents = _get_agents(
        tools, instructions, subagents, model, state_schema, post_model_hook
    )
    other_agents_string = _get_subagent_description(subagents)

    @tool(
        description=TASK_TOOL_DESCRIPTION.format(other_agents=other_agents_string)
    )
    async def task(
        description: str,
        subagent_type: str,
        state: Annotated[DeepAgentState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        if subagent_type not in agents:
            return f"Error: invoked agent of type {subagent_type}, the only allowed types are {[f'`{k}`' for k in agents]}"
        sub_agent = agents[subagent_type]
        state["messages"] = [{"role": "user", "content": description}]
        result = await sub_agent.ainvoke(state)
        return Command(
            update={
                "files": result.get("files", {}),
                "messages": [
                    ToolMessage(
                        result["messages"][-1].content, tool_call_id=tool_call_id
                    )
                ],
            }
        )

    return task


def _create_sync_task_tool(
    tools,
    instructions,
    subagents: list[SubAgent | CustomSubAgent],
    model,
    state_schema,
    post_model_hook: Optional[Callable] = None,
):
    agents = _get_agents(
        tools, instructions, subagents, model, state_schema, post_model_hook
    )
    other_agents_string = _get_subagent_description(subagents)

    @tool(
        description=TASK_TOOL_DESCRIPTION.format(other_agents=other_agents_string)
    )
    def task(
        description: str,
        subagent_type: str,
        state: Annotated[DeepAgentState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        if subagent_type not in agents:
            return f"Error: invoked agent of type {subagent_type}, the only allowed types are {[f'`{k}`' for k in agents]}"
        sub_agent = agents[subagent_type]
        state["messages"] = [{"role": "user", "content": description}]
        result = sub_agent.invoke(state)
        return Command(
            update={
                "files": result.get("files", {}),
                "messages": [
                    ToolMessage(
                        result["messages"][-1].content, tool_call_id=tool_call_id
                    )
                ],
            }
        )

    return task
