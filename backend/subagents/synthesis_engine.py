"""
Synthesis Engine Subagent - DeepAgents v1.1 Implementation

Advanced evidence synthesis and comprehensive report generation using
Perplexity Sonar Deep Research model for multi-step synthesis and citations.
"""

from src.deepagents.sub_agent import SubAgent
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from collections import defaultdict

# Import prompts
from config.prompts import SYNTHESIS_ENGINE_PROMPT
from models.models import ModelFactory


def _identify_themes(
    extracted_data: List[Dict[str, Any]],
    research_question: str
) -> Dict[str, Any]:
    """Identify themes across multiple research papers.
    
    Args:
        extracted_data: List of extracted data from papers
        research_question: The research question being investigated
        
    Returns:
        Dictionary with identified themes and analysis
    """
    try:
        if not extracted_data:
            return {
                "status": "error",
                "message": "No extracted data provided for theme identification"
            }
        
        # Mock theme identification - in real implementation would use NLP/ML
        themes = []
        
        # Group papers by study design
        design_groups = defaultdict(list)
        for paper in extracted_data:
            design = paper.get('study_design', 'other')
            design_groups[design].append(paper)
        
        # Create themes based on common patterns
        for design, papers in design_groups.items():
            if len(papers) >= 2:  # Only create theme if multiple papers
                theme = {
                    "name": f"Evidence from {design.replace('_', ' ').title()} Studies",
                    "description": f"Findings from {len(papers)} {design.replace('_', ' ')} studies",
                    "supporting_papers": [p.get('paper_id', '') for p in papers],
                    "key_findings": _extract_common_findings(papers),
                    "strength_of_evidence": _assess_theme_strength(papers),
                    "consistency": _assess_theme_consistency(papers),
                    "paper_count": len(papers)
                }
                themes.append(theme)
        
        # Add cross-cutting themes
        if len(extracted_data) >= 3:
            cross_theme = {
                "name": "Cross-Study Patterns",
                "description": "Common patterns identified across different study designs",
                "supporting_papers": [p.get('paper_id', '') for p in extracted_data],
                "key_findings": _identify_cross_cutting_findings(extracted_data),
                "strength_of_evidence": "moderate",
                "consistency": "partially_consistent",
                "paper_count": len(extracted_data)
            }
            themes.append(cross_theme)
        
        return {
            "status": "success",
            "themes": themes,
            "theme_count": len(themes),
            "total_papers_analyzed": len(extracted_data),
            "research_question": research_question
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to identify themes"
        }


def _assess_evidence_strength(
    themes: List[Dict[str, Any]],
    quality_criteria: List[str] = None
) -> Dict[str, Any]:
    """Assess the strength of evidence for identified themes.
    
    Args:
        themes: List of identified themes
        quality_criteria: Criteria for assessing evidence strength
        
    Returns:
        Dictionary with evidence strength assessment
    """
    try:
        if quality_criteria is None:
            quality_criteria = [
                "study_design_quality",
                "sample_size_adequacy", 
                "consistency_across_studies",
                "risk_of_bias"
            ]
        
        assessments = []
        
        for theme in themes:
            paper_count = theme.get('paper_count', 0)
            
            # Mock assessment logic
            if paper_count >= 5:
                strength = "high"
            elif paper_count >= 3:
                strength = "moderate"
            else:
                strength = "low"
            
            # Adjust based on consistency
            consistency = theme.get('consistency', 'unknown')
            if consistency == 'inconsistent':
                strength = _downgrade_strength(strength)
            
            assessment = {
                "theme_name": theme.get('name', 'Unnamed Theme'),
                "strength_of_evidence": strength,
                "supporting_evidence": {
                    "paper_count": paper_count,
                    "consistency": consistency,
                    "quality_factors": quality_criteria
                },
                "confidence_level": _calculate_confidence(paper_count, consistency),
                "recommendations": _get_strength_recommendations(strength)
            }
            assessments.append(assessment)
        
        # Overall synthesis strength
        overall_strength = _calculate_overall_strength(assessments)
        
        return {
            "status": "success",
            "evidence_assessments": assessments,
            "overall_strength": overall_strength,
            "quality_criteria_used": quality_criteria
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to assess evidence strength"
        }


def _identify_research_gaps(
    themes: List[Dict[str, Any]],
    extracted_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Identify gaps in the research literature.
    
    Args:
        themes: List of identified themes
        extracted_data: List of extracted data from papers
        
    Returns:
        Dictionary with identified research gaps
    """
    try:
        gaps = []
        
        # Methodological gaps
        study_designs = [paper.get('study_design', 'other') for paper in extracted_data]
        design_counts = defaultdict(int)
        for design in study_designs:
            design_counts[design] += 1
        
        # Identify missing study designs
        expected_designs = ['randomized_controlled_trial', 'cohort_study', 'systematic_review']
        for design in expected_designs:
            if design_counts[design] < 2:
                gaps.append({
                    "type": "methodological",
                    "description": f"Limited {design.replace('_', ' ')} studies",
                    "significance": "High - affects evidence quality",
                    "priority": "high",
                    "suggested_studies": [f"Well-designed {design.replace('_', ' ')} study"]
                })
        
        # Population gaps
        populations = [paper.get('participants', {}).get('population', 'unspecified') 
                      for paper in extracted_data]
        if populations.count('unspecified') > len(populations) * 0.5:
            gaps.append({
                "type": "population",
                "description": "Limited diversity in study populations",
                "significance": "Medium - affects generalizability",
                "priority": "medium",
                "suggested_studies": ["Studies in diverse populations"]
            })
        
        # Outcome measurement gaps
        outcome_measures = set()
        for paper in extracted_data:
            outcomes = paper.get('outcomes', [])
            for outcome in outcomes:
                outcome_measures.add(outcome.get('name', 'unspecified'))
        
        if len(outcome_measures) < 3:
            gaps.append({
                "type": "outcome_measurement",
                "description": "Limited variety in outcome measures",
                "significance": "Medium - limits comprehensive understanding",
                "priority": "medium",
                "suggested_studies": ["Studies with standardized outcome measures"]
            })
        
        # Temporal gaps
        years = [paper.get('year', 0) for paper in extracted_data if paper.get('year')]
        if years and max(years) - min(years) < 5:
            gaps.append({
                "type": "temporal",
                "description": "Limited temporal coverage of studies",
                "significance": "Medium - may miss temporal trends",
                "priority": "low",
                "suggested_studies": ["Longitudinal studies", "Historical analysis"]
            })
        
        return {
            "status": "success",
            "research_gaps": gaps,
            "gap_count": len(gaps),
            "gap_types": list(set(gap["type"] for gap in gaps))
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to identify research gaps"
        }


def _generate_synthesis_report(
    research_question: str,
    themes: List[Dict[str, Any]],
    evidence_assessments: List[Dict[str, Any]],
    research_gaps: List[Dict[str, Any]],
    format_type: str = "markdown"
) -> Dict[str, Any]:
    """Generate a comprehensive synthesis report.
    
    Args:
        research_question: The research question
        themes: Identified themes
        evidence_assessments: Evidence strength assessments
        research_gaps: Identified research gaps
        format_type: Output format ("markdown", "json", "html")
        
    Returns:
        Dictionary with the generated synthesis report
    """
    try:
        if format_type == "markdown":
            report = _generate_markdown_report(
                research_question, themes, evidence_assessments, research_gaps
            )
        elif format_type == "json":
            report = json.dumps({
                "research_question": research_question,
                "themes": themes,
                "evidence_assessments": evidence_assessments,
                "research_gaps": research_gaps,
                "generated_at": datetime.utcnow().isoformat()
            }, indent=2)
        else:  # html
            report = _generate_html_report(
                research_question, themes, evidence_assessments, research_gaps
            )
        
        return {
            "status": "success",
            "report": report,
            "format": format_type,
            "sections": {
                "themes": len(themes),
                "evidence_assessments": len(evidence_assessments),
                "research_gaps": len(research_gaps)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to generate {format_type} synthesis report"
        }


# Helper functions
def _extract_common_findings(papers: List[Dict[str, Any]]) -> List[str]:
    """Extract common findings across papers."""
    # Mock implementation
    return ["Common finding 1", "Common finding 2"]


def _assess_theme_strength(papers: List[Dict[str, Any]]) -> str:
    """Assess the strength of evidence for a theme."""
    if len(papers) >= 5:
        return "high"
    elif len(papers) >= 3:
        return "moderate"
    else:
        return "low"


def _assess_theme_consistency(papers: List[Dict[str, Any]]) -> str:
    """Assess the consistency of findings across papers."""
    # Mock implementation - would analyze actual findings
    return "partially_consistent"


def _identify_cross_cutting_findings(papers: List[Dict[str, Any]]) -> List[str]:
    """Identify findings that cut across multiple studies."""
    return ["Cross-cutting finding 1", "Cross-cutting finding 2"]


def _downgrade_strength(strength: str) -> str:
    """Downgrade evidence strength due to inconsistency."""
    if strength == "high":
        return "moderate"
    elif strength == "moderate":
        return "low"
    else:
        return "very_low"


def _calculate_confidence(paper_count: int, consistency: str) -> str:
    """Calculate confidence level based on paper count and consistency."""
    if paper_count >= 5 and consistency == "consistent":
        return "high"
    elif paper_count >= 3 and consistency in ["consistent", "partially_consistent"]:
        return "moderate"
    else:
        return "low"


def _get_strength_recommendations(strength: str) -> List[str]:
    """Get recommendations based on evidence strength."""
    recommendations = {
        "high": ["Evidence is robust", "Can inform practice with confidence"],
        "moderate": ["Evidence is promising", "Additional studies would strengthen conclusions"],
        "low": ["Evidence is limited", "More research needed before recommendations"],
        "very_low": ["Evidence is insufficient", "Substantial additional research required"]
    }
    return recommendations.get(strength, ["No specific recommendations"])


def _calculate_overall_strength(assessments: List[Dict[str, Any]]) -> str:
    """Calculate overall strength across all themes."""
    strengths = [a["strength_of_evidence"] for a in assessments]
    if "high" in strengths:
        return "moderate_to_high"
    elif "moderate" in strengths:
        return "moderate"
    else:
        return "low"


def _generate_markdown_report(
    research_question: str,
    themes: List[Dict[str, Any]],
    evidence_assessments: List[Dict[str, Any]],
    research_gaps: List[Dict[str, Any]]
) -> str:
    """Generate markdown synthesis report."""
    report = []
    report.append("# Literature Synthesis Report")
    report.append("")
    report.append(f"**Research Question:** {research_question}")
    report.append("")
    report.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    report.append("")
    
    # Themes section
    report.append("## Key Themes")
    report.append("")
    for i, theme in enumerate(themes, 1):
        report.append(f"### {i}. {theme.get('name', 'Unnamed Theme')}")
        report.append(f"{theme.get('description', 'No description available')}")
        report.append("")
        report.append(f"**Supporting Papers:** {theme.get('paper_count', 0)}")
        report.append(f"**Strength of Evidence:** {theme.get('strength_of_evidence', 'Not assessed')}")
        report.append("")
    
    # Evidence assessment section
    if evidence_assessments:
        report.append("## Evidence Strength Assessment")
        report.append("")
        for assessment in evidence_assessments:
            report.append(f"### {assessment.get('theme_name', 'Unnamed Theme')}")
            report.append(f"**Strength:** {assessment.get('strength_of_evidence', 'Not assessed')}")
            report.append(f"**Confidence:** {assessment.get('confidence_level', 'Not assessed')}")
            report.append("")
    
    # Research gaps section
    if research_gaps:
        report.append("## Research Gaps")
        report.append("")
        for i, gap in enumerate(research_gaps, 1):
            report.append(f"### Gap {i}: {gap.get('description', 'Unspecified gap')}")
            report.append(f"**Type:** {gap.get('type', 'Unspecified')}")
            report.append(f"**Significance:** {gap.get('significance', 'Not specified')}")
            report.append(f"**Priority:** {gap.get('priority', 'Not specified')}")
            report.append("")
    
    return "\n".join(report)


def _generate_html_report(
    research_question: str,
    themes: List[Dict[str, Any]],
    evidence_assessments: List[Dict[str, Any]],
    research_gaps: List[Dict[str, Any]]
) -> str:
    """Generate HTML synthesis report."""
    # Basic HTML structure - would be more sophisticated in real implementation
    html = f"""
    <html>
    <head><title>Literature Synthesis Report</title></head>
    <body>
    <h1>Literature Synthesis Report</h1>
    <p><strong>Research Question:</strong> {research_question}</p>
    <p><strong>Generated:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
    
    <h2>Key Themes</h2>
    {"".join(f"<h3>{theme.get('name', 'Unnamed')}</h3><p>{theme.get('description', '')}</p>" for theme in themes)}
    
    <h2>Research Gaps</h2>
    {"".join(f"<h3>{gap.get('description', 'Unspecified')}</h3><p>Priority: {gap.get('priority', 'Not specified')}</p>" for gap in research_gaps)}
    </body>
    </html>
    """
    return html


def create_synthesis_engine():
    """
    Create synthesis engine subagent with Perplexity Sonar Deep Research model.
    
    Uses specialized model for long-running synthesis, multi-paper analysis,
    and comprehensive report generation with citations.
    """
    
    # Use Perplexity Sonar Deep Research model for synthesis
    sonar_model = ModelFactory.get_model("deep-research")
    
    return {
        "name": "synthesis_engine",
        "description": (
            "Advanced evidence synthesis and reporting using Perplexity Sonar Deep Research. "
            "Responsible for creating final_report.md and bibliography.bib. "
            "Handles theme identification, evidence grading, gap analysis, and report generation internally."
        ),
        "prompt": SYNTHESIS_ENGINE_PROMPT,
        # No external tools needed - subagent manages synthesis workflow internally
        "model": sonar_model,
    }
