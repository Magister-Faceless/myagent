"""
General purpose subagent for specialized tasks.
"""

from config.prompts import GENERAL_SUBAGENT_PROMPT
from models import get_default_model


def create_general_subagent():
    """Create a general-purpose subagent configuration."""
    return {
        "name": "specialist-agent",
        "description": "Used for specialized tasks that require focused attention. Delegate specific subtasks to this agent when you need deep focus on a particular aspect of the work.",
        "prompt": GENERAL_SUBAGENT_PROMPT,
        "model": get_default_model(),
    }
