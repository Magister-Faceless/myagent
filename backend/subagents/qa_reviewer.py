"""
Enhanced Quality Assurance Reviewer Subagent - DeepAgents v1.1 Implementation

Provides comprehensive completion verification by analyzing user requests,
chat history, and all outputs (responses + files) to ensure user satisfaction
before final delivery.
"""

from src.deepagents.sub_agent import SubAgent

from config.prompts import QA_REVIEWER_PROMPT
from models import get_default_model

# Import memory tools for chat history analysis
from tools.memory_enhanced_tools import (
    get_thread_memory_context,
    get_shared_context_summary,
)


def create_qa_reviewer() -> SubAgent:
    """Create the enhanced quality assurance reviewer subagent.

    The QA reviewer analyzes the user's original request from chat history,
    reviews all outputs (chat responses and files), and determines if the
    user's needs have been fully satisfied. Provides specific recommendations
    for improvement if gaps are identified.
    
    Enhanced capabilities:
    - Chat history analysis to understand user requirements
    - Completion verification against original request
    - Gap analysis and improvement recommendations
    - User satisfaction focus
    """
    return SubAgent(
        name="qa_reviewer",
        description=(
            "Enhanced quality assurance reviewer that analyzes user requests "
            "from chat history, reviews all outputs (responses + files), and "
            "verifies completion before final delivery. Provides specific "
            "recommendations if user needs are not fully satisfied."
        ),
        prompt=QA_REVIEWER_PROMPT,
        model=get_default_model(),
        tools=[
            # Reference tools by name so framework resolves them from main tool list
            "get_thread_memory_context",
            "get_shared_context_summary",
        ],  # Also relies on built-in ls/read_file for file inspection
    )
