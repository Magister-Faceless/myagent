"""
Literature Review Reviewer Subagent - Citation Verification Specialist

This subagent verifies citation accuracy and consistency in the final literature review.
It cross-references citations with the references section and literature_analysis.md.
"""

from config.prompts import LITERATURE_REVIEW_REVIEWER_PROMPT
from models import get_default_model


def create_literature_review_reviewer():
    """
    Create the literature review citation verification subagent.
    
    This subagent:
    - Verifies all citations [N] in literature_review.md
    - Checks References section completeness
    - Cross-references with literature_analysis.md
    - Returns detailed verification report
    
    Tools: ONLY built-in tools (ls, read_file)
    """
    return {
        "name": "literature_review_reviewer",
        "description": "Citation verification specialist. Verifies all [N] citations in literature_review.md match the References section and cross-references with literature_analysis.md. Returns detailed verification report.",
        "prompt": LITERATURE_REVIEW_REVIEWER_PROMPT,
        # No tools specified = inherits built-in tools only (ls, read_file)
        "model": get_default_model(),
    }
