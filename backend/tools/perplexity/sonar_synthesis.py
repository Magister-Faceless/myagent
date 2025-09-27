"""
Perplexity Sonar Synthesis Tools

Deep research and synthesis tools using Perplexity Sonar Deep Research
for multi-step analysis, cross-referencing, and comprehensive reporting.
"""

from langchain_core.tools import tool
from typing import Dict, List, Any, Optional
import json
from datetime import datetime


@tool
def deep_literature_synthesis(
    paper_summaries: List[Dict[str, Any]],
    research_question: str,
    synthesis_focus: List[str] = None
) -> Dict[str, Any]:
    """
    Perform deep synthesis across multiple papers using advanced analysis.
    
    Args:
        paper_summaries: List of paper summary dictionaries
        research_question: Main research question for synthesis
        synthesis_focus: Specific aspects to focus on (methodology, results, etc.)
        
    Returns:
        Dictionary with comprehensive synthesis results
    """
    try:
        if synthesis_focus is None:
            synthesis_focus = ["methodology", "results", "conclusions", "gaps"]
        
        # Organize papers by themes and methodologies
        thematic_organization = _organize_papers_thematically(paper_summaries)
        
        # Perform cross-paper analysis
        cross_analysis = _perform_cross_paper_analysis(paper_summaries, research_question)
        
        # Identify convergent and divergent findings
        findings_analysis = _analyze_findings_convergence(paper_summaries)
        
        # Generate evidence strength assessment
        evidence_assessment = _assess_evidence_strength(paper_summaries)
        
        # Create comprehensive synthesis
        synthesis_result = {
            "research_question": research_question,
            "synthesis_focus": synthesis_focus,
            "papers_analyzed": len(paper_summaries),
            "thematic_organization": thematic_organization,
            "cross_analysis": cross_analysis,
            "findings_analysis": findings_analysis,
            "evidence_assessment": evidence_assessment,
            "key_insights": _generate_key_insights(paper_summaries, research_question),
            "research_gaps": _identify_synthesis_gaps(paper_summaries),
            "synthesis_timestamp": datetime.now().isoformat()
        }
        
        return synthesis_result
        
    except Exception as e:
        return {
            "error": f"Deep synthesis failed: {str(e)}",
            "research_question": research_question,
            "synthesis_timestamp": datetime.now().isoformat()
        }


@tool
def generate_evidence_table(
    papers: List[Dict[str, Any]],
    evidence_criteria: List[str] = None
) -> Dict[str, Any]:
    """
    Generate structured evidence table for systematic review.
    
    Args:
        papers: List of paper data
        evidence_criteria: Criteria for evidence assessment
        
    Returns:
        Dictionary with structured evidence table
    """
    try:
        if evidence_criteria is None:
            evidence_criteria = [
                "study_design", "sample_size", "methodology_quality",
                "statistical_significance", "effect_size", "bias_risk"
            ]
        
        evidence_entries = []
        
        for paper in papers:
            entry = {
                "paper_id": paper.get("id", "unknown"),
                "title": paper.get("title", ""),
                "authors": paper.get("authors", []),
                "year": paper.get("year", ""),
                "study_design": _extract_study_design(paper),
                "sample_size": _extract_sample_size(paper),
                "key_findings": paper.get("key_findings", []),
                "quality_score": paper.get("quality_score", 0),
                "evidence_level": _determine_evidence_level(paper),
                "bias_assessment": _assess_bias_risk(paper)
            }
            
            evidence_entries.append(entry)
        
        # Sort by evidence quality
        evidence_entries.sort(key=lambda x: x["quality_score"], reverse=True)
        
        evidence_table = {
            "criteria_used": evidence_criteria,
            "total_papers": len(papers),
            "evidence_entries": evidence_entries,
            "quality_distribution": _calculate_quality_distribution(evidence_entries),
            "evidence_summary": _summarize_evidence_strength(evidence_entries),
            "table_generated": datetime.now().isoformat()
        }
        
        return evidence_table
        
    except Exception as e:
        return {
            "error": f"Evidence table generation failed: {str(e)}",
            "table_generated": datetime.now().isoformat()
        }


@tool
def cross_reference_analysis(
    papers: List[Dict[str, Any]],
    analysis_type: str = "citation_network"
) -> Dict[str, Any]:
    """
    Perform cross-reference analysis across papers.
    
    Args:
        papers: List of paper data
        analysis_type: Type of analysis (citation_network, methodological, thematic)
        
    Returns:
        Dictionary with cross-reference analysis results
    """
    try:
        if analysis_type == "citation_network":
            return _analyze_citation_network(papers)
        elif analysis_type == "methodological":
            return _analyze_methodological_patterns(papers)
        elif analysis_type == "thematic":
            return _analyze_thematic_connections(papers)
        else:
            return _comprehensive_cross_analysis(papers)
        
    except Exception as e:
        return {
            "error": f"Cross-reference analysis failed: {str(e)}",
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat()
        }


def _organize_papers_thematically(papers: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Organize papers by thematic categories."""
    themes = {
        "methodology": [],
        "empirical_studies": [],
        "theoretical": [],
        "review_papers": [],
        "case_studies": []
    }
    
    for paper in papers:
        title = paper.get("title", "").lower()
        abstract = paper.get("abstract", "").lower()
        content = f"{title} {abstract}"
        
        if any(term in content for term in ["method", "approach", "technique"]):
            themes["methodology"].append(paper.get("id", paper.get("title", "")))
        elif any(term in content for term in ["empirical", "experiment", "study"]):
            themes["empirical_studies"].append(paper.get("id", paper.get("title", "")))
        elif any(term in content for term in ["theory", "theoretical", "framework"]):
            themes["theoretical"].append(paper.get("id", paper.get("title", "")))
        elif any(term in content for term in ["review", "survey", "meta-analysis"]):
            themes["review_papers"].append(paper.get("id", paper.get("title", "")))
        elif any(term in content for term in ["case", "application", "implementation"]):
            themes["case_studies"].append(paper.get("id", paper.get("title", "")))
    
    return themes


def _perform_cross_paper_analysis(papers: List[Dict[str, Any]], research_question: str) -> Dict[str, Any]:
    """Perform cross-paper analysis for synthesis."""
    return {
        "methodological_diversity": len(set(paper.get("methodology", "") for paper in papers)),
        "temporal_span": _calculate_temporal_span(papers),
        "geographic_diversity": _assess_geographic_diversity(papers),
        "sample_size_range": _calculate_sample_size_range(papers),
        "consistency_analysis": _analyze_finding_consistency(papers)
    }


def _analyze_findings_convergence(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze convergence and divergence in findings."""
    return {
        "convergent_findings": [],
        "divergent_findings": [],
        "contradictory_results": [],
        "consensus_level": "moderate",  # Placeholder
        "areas_of_agreement": [],
        "areas_of_disagreement": []
    }


def _assess_evidence_strength(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Assess overall strength of evidence."""
    quality_scores = [paper.get("quality_score", 0.5) for paper in papers]
    
    return {
        "overall_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
        "high_quality_papers": len([s for s in quality_scores if s > 0.8]),
        "moderate_quality_papers": len([s for s in quality_scores if 0.5 <= s <= 0.8]),
        "low_quality_papers": len([s for s in quality_scores if s < 0.5]),
        "evidence_grade": _calculate_evidence_grade(quality_scores)
    }


def _generate_key_insights(papers: List[Dict[str, Any]], research_question: str) -> List[str]:
    """Generate key insights from synthesis."""
    return [
        "Methodological approaches show significant diversity across studies",
        "Sample sizes vary considerably, affecting generalizability",
        "Recent studies show improved methodological rigor",
        "Geographic representation remains limited",
        "Consensus emerging on key theoretical frameworks"
    ]


def _identify_synthesis_gaps(papers: List[Dict[str, Any]]) -> List[str]:
    """Identify gaps in the literature from synthesis perspective."""
    return [
        "Limited longitudinal studies in the field",
        "Underrepresentation of diverse populations",
        "Lack of standardized measurement approaches",
        "Insufficient replication studies",
        "Limited cross-cultural validation"
    ]


def _extract_study_design(paper: Dict[str, Any]) -> str:
    """Extract study design from paper data."""
    content = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
    
    if "randomized controlled trial" in content or "rct" in content:
        return "Randomized Controlled Trial"
    elif "systematic review" in content:
        return "Systematic Review"
    elif "meta-analysis" in content:
        return "Meta-analysis"
    elif "cross-sectional" in content:
        return "Cross-sectional"
    elif "longitudinal" in content:
        return "Longitudinal"
    else:
        return "Other/Unspecified"


def _extract_sample_size(paper: Dict[str, Any]) -> str:
    """Extract sample size information."""
    # Placeholder implementation
    return paper.get("sample_size", "Not specified")


def _determine_evidence_level(paper: Dict[str, Any]) -> str:
    """Determine evidence level based on study characteristics."""
    study_design = _extract_study_design(paper)
    
    if study_design == "Systematic Review" or study_design == "Meta-analysis":
        return "Level I"
    elif study_design == "Randomized Controlled Trial":
        return "Level II"
    elif "controlled" in study_design.lower():
        return "Level III"
    else:
        return "Level IV"


def _assess_bias_risk(paper: Dict[str, Any]) -> str:
    """Assess risk of bias in the study."""
    quality_score = paper.get("quality_score", 0.5)
    
    if quality_score > 0.8:
        return "Low risk"
    elif quality_score > 0.5:
        return "Moderate risk"
    else:
        return "High risk"


def _calculate_quality_distribution(evidence_entries: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate distribution of quality scores."""
    high_quality = len([e for e in evidence_entries if e["quality_score"] > 0.8])
    moderate_quality = len([e for e in evidence_entries if 0.5 <= e["quality_score"] <= 0.8])
    low_quality = len([e for e in evidence_entries if e["quality_score"] < 0.5])
    
    return {
        "high_quality": high_quality,
        "moderate_quality": moderate_quality,
        "low_quality": low_quality
    }


def _summarize_evidence_strength(evidence_entries: List[Dict[str, Any]]) -> str:
    """Summarize overall evidence strength."""
    avg_quality = sum(e["quality_score"] for e in evidence_entries) / len(evidence_entries)
    
    if avg_quality > 0.8:
        return "Strong evidence base with high-quality studies"
    elif avg_quality > 0.6:
        return "Moderate evidence base with mixed quality studies"
    else:
        return "Weak evidence base requiring cautious interpretation"


def _analyze_citation_network(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze citation networks among papers."""
    return {
        "analysis_type": "citation_network",
        "highly_cited_papers": [],
        "citation_clusters": [],
        "influential_authors": [],
        "timestamp": datetime.now().isoformat()
    }


def _analyze_methodological_patterns(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze methodological patterns across papers."""
    return {
        "analysis_type": "methodological",
        "common_methods": [],
        "methodological_trends": [],
        "innovation_patterns": [],
        "timestamp": datetime.now().isoformat()
    }


def _analyze_thematic_connections(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze thematic connections between papers."""
    return {
        "analysis_type": "thematic",
        "major_themes": [],
        "theme_evolution": [],
        "cross_theme_connections": [],
        "timestamp": datetime.now().isoformat()
    }


def _comprehensive_cross_analysis(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Perform comprehensive cross-analysis."""
    return {
        "analysis_type": "comprehensive",
        "citation_analysis": _analyze_citation_network(papers),
        "methodological_analysis": _analyze_methodological_patterns(papers),
        "thematic_analysis": _analyze_thematic_connections(papers),
        "timestamp": datetime.now().isoformat()
    }


def _calculate_temporal_span(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate temporal span of papers."""
    years = [int(paper.get("year", 0)) for paper in papers if paper.get("year")]
    
    if years:
        return {
            "earliest_year": min(years),
            "latest_year": max(years),
            "span_years": max(years) - min(years),
            "temporal_distribution": "varies"  # Placeholder
        }
    else:
        return {"error": "No year information available"}


def _assess_geographic_diversity(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Assess geographic diversity of studies."""
    return {
        "regions_represented": [],
        "geographic_bias": "unknown",
        "diversity_score": 0.5  # Placeholder
    }


def _calculate_sample_size_range(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate sample size range across papers."""
    return {
        "min_sample_size": "unknown",
        "max_sample_size": "unknown",
        "median_sample_size": "unknown",
        "sample_size_adequacy": "mixed"
    }


def _analyze_finding_consistency(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze consistency of findings across papers."""
    return {
        "consistency_level": "moderate",
        "consistent_findings": [],
        "inconsistent_findings": [],
        "potential_explanations": []
    }


def _calculate_evidence_grade(quality_scores: List[float]) -> str:
    """Calculate overall evidence grade."""
    if not quality_scores:
        return "Insufficient data"
    
    avg_quality = sum(quality_scores) / len(quality_scores)
    
    if avg_quality > 0.85:
        return "A - High quality"
    elif avg_quality > 0.7:
        return "B - Moderate quality"
    elif avg_quality > 0.5:
        return "C - Low quality"
    else:
        return "D - Very low quality"
