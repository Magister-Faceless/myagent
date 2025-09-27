"""
Checkpointer configuration for persistent state storage.

This module provides utilities for creating and configuring persistent
checkpointers that store LangGraph state (including files and todos)
across server restarts.
"""

import os
from pathlib import Path
from typing import Optional
from langgraph.types import Checkpointer

# Try different import paths for SqliteSaver
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:
    try:
        from langgraph_checkpoint_sqlite import SqliteSaver
    except ImportError:
        try:
            from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver as SqliteSaver
        except ImportError:
            print("❌ Could not import SqliteSaver. Please install: pip install langgraph-checkpoint-sqlite")
            SqliteSaver = None


def get_checkpointer_path() -> str:
    """Get the path for the SQLite checkpointer database.
    
    Returns:
        Path to the SQLite database file for storing checkpoints.
    """
    # Create checkpoints directory if it doesn't exist
    backend_dir = Path(__file__).parent.parent
    checkpoints_dir = backend_dir / "data" / "checkpoints"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    
    # Return path to the SQLite database
    return str(checkpoints_dir / "agent_state.db")


def create_persistent_checkpointer() -> Optional[Checkpointer]:
    """Create a persistent SQLite checkpointer for agent state.
    
    This checkpointer will persist all agent state including:
    - Messages and conversation history
    - Todo lists
    - Files created by the agent
    - Any other state in DeepAgentState
    
    Returns:
        Configured SQLite checkpointer instance, or None if unavailable.
    """
    if SqliteSaver is None:
        print("⚠️  SqliteSaver not available. Files will not persist across restarts.")
        return None
    
    try:
        db_path = get_checkpointer_path()
        
        # Create SQLite checkpointer with connection string
        checkpointer = SqliteSaver.from_conn_string(f"sqlite:///{db_path}")
        
        print(f"✅ Persistent checkpointer configured: {db_path}")
        return checkpointer
    except Exception as e:
        print(f"❌ Failed to create checkpointer: {e}")
        print("⚠️  Files will not persist across restarts.")
        return None


def get_default_checkpointer() -> Optional[Checkpointer]:
    """Get the default checkpointer for agents.
    
    Returns:
        Persistent checkpointer if enabled, None otherwise.
    """
    # Check if persistence is disabled via environment variable
    if os.environ.get("DISABLE_PERSISTENCE", "").lower() in ("true", "1", "yes"):
        print("⚠️  Persistence disabled via DISABLE_PERSISTENCE environment variable")
        return None
    
    try:
        return create_persistent_checkpointer()
    except Exception as e:
        print(f"❌ Failed to create persistent checkpointer: {e}")
        print("⚠️  Falling back to in-memory state (files will not persist)")
        return None


# Export the main function for easy import
__all__ = ["create_persistent_checkpointer", "get_default_checkpointer", "get_checkpointer_path"]
