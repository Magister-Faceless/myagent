"""
Literature Screener Subagent - DeepAgents v1.1 Implementation

PRISMA-compliant paper screening with CORE API integration and Grok-4-Fast 
vision capabilities for full-text analysis including images, tables, and figures.
"""

from src.deepagents.sub_agent import SubAgent
from typing import Dict, List, Any
import json
from datetime import datetime

# Import prompts
from config.prompts import LITERATURE_SCREENER_PROMPT
from models import get_default_model


def _screen_papers(
    papers: List[Dict[str, Any]], 
    inclusion_criteria: List[str],
    exclusion_criteria: List[str],
    stage: str = "title_abstract"
) -> Dict[str, Any]:
    """Screen papers based on inclusion/exclusion criteria.
    
    Args:
        papers: List of papers to screen with metadata
        inclusion_criteria: List of inclusion criteria
        exclusion_criteria: List of exclusion criteria  
        stage: Screening stage ('title_abstract' or 'full_text')
        
    Returns:
        Dictionary with screening results and statistics
    """
    try:
        screening_results = []
        
        for paper in papers:
            # Mock screening logic - in real implementation would analyze content
            decision = "include"  # Default decision
            reason = "Meets inclusion criteria"
            
            # Simple mock screening based on year
            if paper.get('year', 0) < 2010:
                decision = "exclude"
                reason = "Publication year too old"
            
            # Check for exclusion keywords in title/abstract
            title = paper.get('title', '').lower()
            abstract = paper.get('abstract', '').lower()
            
            for exclusion in exclusion_criteria:
                if exclusion.lower() in title or exclusion.lower() in abstract:
                    decision = "exclude"
                    reason = f"Contains exclusion term: {exclusion}"
                    break
            
            result = {
                "paper_id": paper.get('id', f"paper_{len(screening_results)}"),
                "title": paper.get('title', 'Untitled'),
                "decision": decision,
                "reason": reason,
                "stage": stage,
                "screened_at": datetime.utcnow().isoformat()
            }
            screening_results.append(result)
        
        # Calculate statistics
        included = sum(1 for r in screening_results if r["decision"] == "include")
        excluded = len(screening_results) - included
        
        return {
            "status": "success",
            "screening_results": screening_results,
            "statistics": {
                "total_papers": len(papers),
                "included": included,
                "excluded": excluded,
                "inclusion_rate": included / len(papers) if papers else 0
            },
            "stage": stage
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to screen papers at {stage} stage"
        }


def _generate_prisma_data(screening_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate PRISMA flow diagram data from screening results.
    
    Args:
        screening_results: List of screening result dictionaries
        
    Returns:
        Dictionary with PRISMA flow data
    """
    try:
        # Count decisions by stage
        title_abstract_results = [r for r in screening_results if r.get('stage') == 'title_abstract']
        full_text_results = [r for r in screening_results if r.get('stage') == 'full_text']
        
        # Calculate counts
        total_identified = len(screening_results)
        included_after_title = sum(1 for r in title_abstract_results if r.get('decision') == 'include')
        included_final = sum(1 for r in full_text_results if r.get('decision') == 'include')
        
        # Group exclusion reasons
        exclusion_reasons = {}
        for result in screening_results:
            if result.get('decision') == 'exclude':
                reason = result.get('reason', 'Unspecified')
                exclusion_reasons[reason] = exclusion_reasons.get(reason, 0) + 1
        
        prisma_data = {
            "identification": {
                "records_identified": total_identified,
                "duplicates_removed": 0,  # Would be calculated separately
                "records_screened": len(title_abstract_results)
            },
            "screening": {
                "records_screened": len(title_abstract_results),
                "records_excluded": len(title_abstract_results) - included_after_title
            },
            "eligibility": {
                "full_text_assessed": len(full_text_results),
                "full_text_excluded": len(full_text_results) - included_final,
                "exclusion_reasons": exclusion_reasons
            },
            "included": {
                "studies_included": included_final
            }
        }
        
        return {
            "status": "success",
            "prisma_data": prisma_data,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to generate PRISMA data"
        }


def create_literature_screener():
    """
    Create literature screener subagent with Grok-4-Fast model.
    
    Uses Grok-4-Fast for PRISMA screening with vision analysis capabilities
    for analyzing images, tables, and figures in papers.
    """
    
    # Use default model (Grok-4-Fast) for screening and vision analysis
    model = get_default_model()
    
    return {
        "name": "literature_screener",
        "description": (
            "PRISMA-compliant screening with Grok-4-Fast vision analysis for images, tables, and figures. "
            "Responsible for creating prisma_diagram.md. "
            "Handles screening workflows internally including PRISMA data generation and statistics."
        ),
        "prompt": LITERATURE_SCREENER_PROMPT,
        # No external tools needed - subagent handles screening logic internally
        "model": model,  # Use Grok-4-Fast for vision capabilities
    }
