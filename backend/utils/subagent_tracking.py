"""Utilities for enabling subagent tracking hooks without modifying framework internals."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Callable, Generator, Any

from tools.subagent_tracker import create_enhanced_task_tool


@contextmanager
def enable_subagent_tracking() -> Generator[None, None, None]:
    """Temporarily wrap DeepAgents task tools with the enhanced tracker.

    This context manager monkey patches ``src.deepagents.sub_agent``'s task tool
    factories so that any agent constructed within the context will emit
    lifecycle events for subagents via ``create_enhanced_task_tool``.
    """

    from src.deepagents import sub_agent as deep_sub_agent  # Import inside to avoid cycles

    original_async: Callable[..., Any] = deep_sub_agent._create_task_tool
    original_sync: Callable[..., Any] = deep_sub_agent._create_sync_task_tool

    def _wrap_async(*args: Any, **kwargs: Any):
        original_tool = original_async(*args, **kwargs)
        return create_enhanced_task_tool(original_tool, is_async=True)

    def _wrap_sync(*args: Any, **kwargs: Any):
        original_tool = original_sync(*args, **kwargs)
        return create_enhanced_task_tool(original_tool, is_async=False)

    deep_sub_agent._create_task_tool = _wrap_async
    deep_sub_agent._create_sync_task_tool = _wrap_sync

    try:
        yield
    finally:
        deep_sub_agent._create_task_tool = original_async
        deep_sub_agent._create_sync_task_tool = original_sync
