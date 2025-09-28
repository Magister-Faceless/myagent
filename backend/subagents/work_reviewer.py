"""
Work Reviewer Subagent - DeepAgents v1.1 Implementation

Quality assurance subagent responsible for verifying all literature review 
deliverables are complete and meet academic standards. Creates work_review_report.md.
"""

from src.deepagents.sub_agent import SubAgent
from config.prompts import WORK_REVIEWER_PROMPT
from models import get_default_model


def create_work_reviewer():
    """
    Create work reviewer subagent for quality assurance of literature review outputs.
    
    FILE OUTPUT RESPONSIBILITY: Creates work_review_report.md
    
    This subagent verifies that all required deliverables exist and meet quality standards:
    - final_report.md (complete systematic review)
    - prisma_diagram.md (PRISMA flow chart) 
    - bibliography.bib (all citations in BibTeX format)
    - evidence_summary.md (quality assessment summary)
    - methodology.md (reproducible search strategy)
    
    Uses built-in DeepAgents tools: ls, read_file, write_file
    """
    return SubAgent(
        name="work_reviewer",
        description="Quality assurance reviewer for literature review deliverables. Responsible for creating work_review_report.md. Verifies all required files (final_report.md, prisma_diagram.md, bibliography.bib, evidence_summary.md, methodology.md) exist and meet academic standards using ls, read_file, and write_file tools.",
        prompt=WORK_REVIEWER_PROMPT,
        model=get_default_model(),
        tools=[]  # Uses built-in tools: ls, read_file, write_file
    )
