"""
Planning Coordinator Subagent - DeepAgents v1.1 Implementation

Creates and refines structured research plans for literature reviews.
Requires human approval before execution following the human-in-the-loop workflow.
Uses Grok-4-Fast model for planning and coordination.

The subagent handles all planning logic internally without needing separate tools.
"""

from src.deepagents.sub_agent import SubAgent
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta

# Import prompts
from config.prompts import PLANNING_COORDINATOR_PROMPT
from models import get_default_model


# Helper functions for the subagent (not exposed as tools)
def _create_research_plan(
    research_question: str,
    scope: str = "",
    methodology: str = "systematic_review",
    time_frame: str = "4_weeks"
) -> Dict[str, Any]:
    """
    Create a structured research plan for literature review.
    
    Args:
        research_question: The main research question to investigate
        scope: Scope and boundaries of the review
        methodology: Type of review (systematic_review, scoping_review, narrative_review)
        time_frame: Expected timeframe for completion
        
    Returns:
        Dictionary with detailed research plan
    """
    try:
        # Generate structured research plan
        research_plan = {
            "title": f"Literature Review: {research_question}",
            "research_question": research_question,
            "methodology": methodology,
            "scope": scope,
            "timeline": _generate_timeline(time_frame),
            "search_strategy": _generate_search_strategy(research_question),
            "inclusion_criteria": _generate_inclusion_criteria(research_question, scope),
            "exclusion_criteria": _generate_exclusion_criteria(),
            "quality_assessment": _generate_quality_framework(methodology),
            "data_extraction": _generate_extraction_plan(),
            "synthesis_approach": _generate_synthesis_plan(methodology),
            "deliverables": _generate_deliverables(methodology),
            "resources_needed": _estimate_resources(research_question, methodology),
            "risk_assessment": _assess_risks(research_question, methodology),
            "approval_required": True,
            "status": "draft",
            "created_at": datetime.now().isoformat()
        }
        
        return research_plan
        
    except Exception as e:
        return {
            "error": f"Failed to create research plan: {str(e)}",
            "status": "error",
            "created_at": datetime.now().isoformat()
        }


def _refine_research_plan(
    existing_plan: Dict[str, Any],
    user_feedback: str,
    modifications: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Refine an existing research plan based on user feedback.
    
    Args:
        existing_plan: The current research plan
        user_feedback: User's feedback and requested changes
        modifications: Specific modifications to apply
        
    Returns:
        Dictionary with refined research plan
    """
    try:
        refined_plan = existing_plan.copy()
        
        # Apply modifications based on feedback
        if modifications:
            for key, value in modifications.items():
                if key in refined_plan:
                    refined_plan[key] = value
        
        # Update metadata
        refined_plan["last_modified"] = datetime.now().isoformat()
        refined_plan["revision_notes"] = user_feedback
        refined_plan["status"] = "revised"
        
        # Re-assess timeline and resources if scope changed
        if "scope" in modifications or "methodology" in modifications:
            refined_plan["timeline"] = _generate_timeline(refined_plan.get("time_frame", "4_weeks"))
            refined_plan["resources_needed"] = _estimate_resources(
                refined_plan["research_question"], 
                refined_plan["methodology"]
            )
        
        return refined_plan
        
    except Exception as e:
        return {
            "error": f"Failed to refine research plan: {str(e)}",
            "status": "error",
            "last_modified": datetime.now().isoformat()
        }


def _generate_search_keywords(
    research_question: str,
    domain: str = "",
    include_synonyms: bool = True
) -> Dict[str, Any]:
    """
    Generate comprehensive search keywords and terms for the research question.
    
    Args:
        research_question: The main research question
        domain: Specific domain or field
        include_synonyms: Whether to include synonyms and related terms
        
    Returns:
        Dictionary with organized search terms
    """
    try:
        # Extract key concepts from research question
        key_concepts = _extract_key_concepts(research_question)
        
        search_terms = {
            "primary_terms": key_concepts,
            "synonyms": [],
            "related_terms": [],
            "boolean_combinations": [],
            "mesh_terms": [],
            "field_specific_terms": [],
            "search_strings": []
        }
        
        # Generate synonyms if requested
        if include_synonyms:
            search_terms["synonyms"] = _generate_synonyms(key_concepts)
            search_terms["related_terms"] = _generate_related_terms(key_concepts, domain)
        
        # Create boolean search combinations
        search_terms["boolean_combinations"] = _create_boolean_combinations(
            key_concepts, search_terms["synonyms"]
        )
        
        # Generate complete search strings
        search_terms["search_strings"] = _generate_search_strings(
            search_terms["boolean_combinations"]
        )
        
        return search_terms
        
    except Exception as e:
        return {
            "error": f"Failed to generate search keywords: {str(e)}",
            "primary_terms": [],
            "synonyms": [],
            "related_terms": [],
            "boolean_combinations": [],
            "search_strings": []
        }


def _generate_timeline(time_frame: str) -> Dict[str, Any]:
    """Generate timeline for literature review phases."""
    base_weeks = {
        "2_weeks": 2,
        "4_weeks": 4,
        "6_weeks": 6,
        "8_weeks": 8
    }
    
    weeks = base_weeks.get(time_frame, 4)
    start_date = datetime.now()
    
    phases = {
        "planning": {"duration": "1 week", "percentage": 12.5},
        "search": {"duration": f"{weeks//4 + 1} weeks", "percentage": 25},
        "screening": {"duration": f"{weeks//3} weeks", "percentage": 20},
        "data_extraction": {"duration": f"{weeks//3} weeks", "percentage": 20},
        "analysis": {"duration": f"{weeks//4 + 1} weeks", "percentage": 15},
        "writing": {"duration": "1 week", "percentage": 7.5}
    }
    
    timeline = {}
    current_date = start_date
    
    for phase, details in phases.items():
        phase_weeks = int(details["duration"].split()[0])
        end_date = current_date + timedelta(weeks=phase_weeks)
        
        timeline[phase] = {
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration": details["duration"],
            "percentage": details["percentage"]
        }
        
        current_date = end_date
    
    return timeline


def _generate_search_strategy(research_question: str) -> Dict[str, Any]:
    """Generate comprehensive search strategy."""
    return {
        "databases": [
            "CORE (via API)",
            "PubMed/MEDLINE",
            "Scopus",
            "Web of Science",
            "Google Scholar"
        ],
        "search_approach": "systematic",
        "date_range": "2019-2024",
        "language": "English",
        "document_types": ["journal articles", "conference papers", "reviews"],
        "search_validation": "peer review recommended"
    }


def _generate_inclusion_criteria(research_question: str, scope: str) -> List[str]:
    """Generate inclusion criteria based on research question and scope."""
    base_criteria = [
        "Peer-reviewed publications",
        "Published in English",
        "Published between 2019-2024",
        "Directly addresses the research question"
    ]
    
    # Add scope-specific criteria
    if "recent" in scope.lower():
        base_criteria.append("Published within last 5 years")
    if "empirical" in scope.lower():
        base_criteria.append("Contains empirical data or analysis")
    
    return base_criteria


def _generate_exclusion_criteria() -> List[str]:
    """Generate standard exclusion criteria."""
    return [
        "Non-peer reviewed publications",
        "Gray literature (unless specifically relevant)",
        "Publications not in English",
        "Duplicate publications",
        "Abstracts without full text available",
        "Publications outside date range"
    ]


def _generate_quality_framework(methodology: str) -> Dict[str, Any]:
    """Generate quality assessment framework based on methodology."""
    frameworks = {
        "systematic_review": {
            "tool": "PRISMA 2020",
            "criteria": ["Study design", "Sample size", "Methodology rigor", "Bias assessment"],
            "scoring": "Newcastle-Ottawa Scale or ROB2"
        },
        "scoping_review": {
            "tool": "PRISMA-ScR",
            "criteria": ["Relevance", "Study quality", "Data completeness"],
            "scoring": "Narrative assessment"
        },
        "narrative_review": {
            "tool": "Custom framework",
            "criteria": ["Authority", "Accuracy", "Currency", "Relevance"],
            "scoring": "Qualitative assessment"
        }
    }
    
    return frameworks.get(methodology, frameworks["systematic_review"])


def _generate_extraction_plan() -> Dict[str, Any]:
    """Generate data extraction plan."""
    return {
        "extraction_form": "Structured template",
        "fields": [
            "Citation details",
            "Study design",
            "Sample characteristics",
            "Key findings",
            "Limitations",
            "Quality indicators"
        ],
        "pilot_testing": "Required on 10% of papers",
        "inter_rater_reliability": "Recommended for key decisions"
    }


def _generate_synthesis_plan(methodology: str) -> Dict[str, Any]:
    """Generate synthesis approach based on methodology."""
    approaches = {
        "systematic_review": {
            "type": "Thematic synthesis",
            "methods": ["Meta-analysis (if appropriate)", "Narrative synthesis", "Evidence tables"],
            "tools": ["Perplexity Sonar Deep Research", "Statistical software (if needed)"]
        },
        "scoping_review": {
            "type": "Narrative synthesis",
            "methods": ["Thematic analysis", "Concept mapping", "Gap identification"],
            "tools": ["Qualitative analysis", "Visualization tools"]
        },
        "narrative_review": {
            "type": "Narrative synthesis",
            "methods": ["Thematic organization", "Critical analysis", "Trend identification"],
            "tools": ["Content analysis", "Synthesis writing"]
        }
    }
    
    return approaches.get(methodology, approaches["systematic_review"])


def _generate_deliverables(methodology: str) -> List[str]:
    """Generate expected deliverables."""
    base_deliverables = [
        "Complete literature review document",
        "PRISMA flow diagram",
        "Reference list (BibTeX format)",
        "Data extraction tables",
        "Quality assessment summary"
    ]
    
    if methodology == "systematic_review":
        base_deliverables.extend([
            "Meta-analysis results (if applicable)",
            "Risk of bias assessment"
        ])
    
    return base_deliverables


def _estimate_resources(research_question: str, methodology: str) -> Dict[str, Any]:
    """Estimate required resources."""
    base_resources = {
        "time_estimate": "4-6 weeks",
        "papers_expected": "50-150",
        "tools_needed": ["CORE API", "Grok-4-Fast", "Perplexity Sonar"],
        "expertise_required": "Research methodology, domain knowledge"
    }
    
    # Adjust based on complexity
    if len(research_question.split()) > 10:  # Complex question
        base_resources["time_estimate"] = "6-8 weeks"
        base_resources["papers_expected"] = "100-300"
    
    return base_resources


def _assess_risks(research_question: str, methodology: str) -> List[str]:
    """Assess potential risks and challenges."""
    risks = [
        "Limited availability of relevant literature",
        "Heterogeneity in study designs",
        "Publication bias",
        "Time constraints"
    ]
    
    if "emerging" in research_question.lower():
        risks.append("Rapidly evolving field with limited established literature")
    
    if methodology == "systematic_review":
        risks.append("Complexity of meta-analysis if studies are too heterogeneous")
    
    return risks


def _extract_key_concepts(research_question: str) -> List[str]:
    """Extract key concepts from research question."""
    # Simple keyword extraction (in real implementation, could use NLP)
    stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "what", "how", "why", "when", "where"}
    words = research_question.lower().split()
    key_concepts = [word.strip(".,?!") for word in words if word not in stop_words and len(word) > 3]
    return key_concepts[:5]  # Return top 5 concepts


def _generate_synonyms(key_concepts: List[str]) -> List[str]:
    """Generate synonyms for key concepts."""
    # Simplified synonym generation
    synonym_map = {
        "machine learning": ["artificial intelligence", "AI", "ML", "deep learning"],
        "healthcare": ["medical", "clinical", "health", "medicine"],
        "education": ["learning", "teaching", "academic", "pedagogical"],
        "technology": ["digital", "technological", "tech", "innovation"]
    }
    
    synonyms = []
    for concept in key_concepts:
        if concept in synonym_map:
            synonyms.extend(synonym_map[concept])
    
    return synonyms


def _generate_related_terms(key_concepts: List[str], domain: str) -> List[str]:
    """Generate related terms based on domain."""
    # Domain-specific related terms
    domain_terms = {
        "healthcare": ["patient", "treatment", "diagnosis", "therapy", "clinical"],
        "education": ["student", "curriculum", "assessment", "pedagogy", "learning"],
        "technology": ["software", "algorithm", "system", "platform", "digital"]
    }
    
    return domain_terms.get(domain.lower(), [])


def _create_boolean_combinations(key_concepts: List[str], synonyms: List[str]) -> List[str]:
    """Create boolean search combinations."""
    if not key_concepts:
        return []
    
    combinations = []
    
    # Simple AND combinations
    if len(key_concepts) >= 2:
        combinations.append(f"{key_concepts[0]} AND {key_concepts[1]}")
    
    # OR combinations with synonyms
    if synonyms:
        combinations.append(f"({key_concepts[0]} OR {synonyms[0]})")
    
    return combinations


def _generate_search_strings(boolean_combinations: List[str]) -> List[str]:
    """Generate complete search strings."""
    if not boolean_combinations:
        return []
    
    search_strings = []
    for combo in boolean_combinations:
        # Add field restrictions and filters
        search_strings.append(f'({combo}) AND (title OR abstract)')
        search_strings.append(f'({combo}) AND year:[2019 TO 2024]')
    
    return search_strings


def create_planning_coordinator():
    """Create the Planning Coordinator subagent with Grok-4-Fast model."""
    
    # Use default model (Grok-4-Fast) for planning and coordination
    model = get_default_model()
    
    return {
        "name": "planning_coordinator",
        "description": "Creates and refines structured research plans with human approval workflow. Responsible for creating methodology.md. Handles all planning logic internally including PICO formulation, search strategy, inclusion/exclusion criteria, and timeline development.",
        "prompt": PLANNING_COORDINATOR_PROMPT,
        # No external tools needed - subagent handles planning logic internally
        "model": model
    }
