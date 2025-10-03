"""
General purpose subagent for specialized tasks with access to ALL tools.
"""

from config.prompts import GENERAL_SUBAGENT_PROMPT
from models import get_default_model


def create_general_subagent():
    """
    Create a general-purpose subagent with access to ALL available tools.
    
    This subagent can handle any task requiring tools, making it extremely
    flexible for the main agent to delegate diverse tasks.
    
    Note: By NOT specifying a "tools" field, this subagent automatically inherits
    ALL tools from the parent agent. This is the default behavior in DeepAgents.
    """
    return {
        "name": "specialist-agent",
        "description": "General-purpose specialist with access to ALL tools. Use for any task requiring searches, retrievals, analyses, or specialized operations. Can handle literature searches, paper retrieval, quality assessments, web searches, and more.",
        "prompt": GENERAL_SUBAGENT_PROMPT,
        # No "tools" field = inherits ALL tools from parent agent automatically
        "model": get_default_model(),
    }
