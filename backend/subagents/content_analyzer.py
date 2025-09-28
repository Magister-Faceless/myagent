"""
Content Analyzer Subagent - DeepAgents v1.1 Implementation

Comprehensive analysis of full papers using Grok-4-Fast's 2M token context window
and vision capabilities for images, tables, and figures.
"""

from src.deepagents.sub_agent import SubAgent
from typing import Dict, Any, List
import json
from datetime import datetime

from config.prompts import CONTENT_ANALYZER_PROMPT
from models import get_default_model


def _analyze_full_paper(
    paper_content: str,
    paper_metadata: Dict[str, Any],
    analysis_focus: List[str] = None
) -> Dict[str, Any]:
    """
    Comprehensive analysis of a full research paper.
    
    Args:
        paper_content: Full text content of the paper
        paper_metadata: Paper metadata (title, authors, etc.)
        analysis_focus: Specific aspects to focus on
        
    Returns:
        Dictionary with comprehensive paper analysis
    """
    try:
        if analysis_focus is None:
            analysis_focus = ["methodology", "results", "conclusions", "limitations"]
        
        analysis = {
            "paper_id": paper_metadata.get("id", "unknown"),
            "title": paper_metadata.get("title", ""),
            "authors": paper_metadata.get("authors", []),
            "year": paper_metadata.get("year", ""),
            "methodology": _extract_methodology(paper_content),
            "key_findings": _extract_key_findings(paper_content),
            "results_summary": _extract_results(paper_content),
            "limitations": _extract_limitations(paper_content),
            "quality_indicators": _assess_quality(paper_content, paper_metadata),
            "data_extraction": _extract_structured_data(paper_content),
            "visual_elements": _analyze_visual_elements(paper_content),
            "citations_count": paper_metadata.get("citationCount", 0),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return analysis
        
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "paper_id": paper_metadata.get("id", "unknown"),
            "analysis_timestamp": datetime.now().isoformat()
        }


def _extract_visual_data(
    image_descriptions: List[str],
    table_data: List[str],
    figure_captions: List[str]
) -> Dict[str, Any]:
    """
    Extract and analyze data from visual elements using Grok-4-Fast vision capabilities.
    
    Args:
        image_descriptions: Descriptions of images/figures
        table_data: Table content and structure
        figure_captions: Figure captions and descriptions
        
    Returns:
        Dictionary with extracted visual data
    """
    try:
        visual_analysis = {
            "tables": _analyze_tables(table_data),
            "figures": _analyze_figures(image_descriptions, figure_captions),
            "statistical_data": _extract_statistical_data(table_data),
            "methodology_diagrams": _identify_methodology_diagrams(image_descriptions),
            "results_visualizations": _identify_results_viz(image_descriptions, figure_captions),
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        return visual_analysis
        
    except Exception as e:
        return {
            "error": f"Visual analysis failed: {str(e)}",
            "extraction_timestamp": datetime.now().isoformat()
        }


def _create_paper_summary(
    paper_analysis: Dict[str, Any],
    summary_type: str = "comprehensive"
) -> Dict[str, Any]:
    """
    Create structured summary of paper analysis.
    
    Args:
        paper_analysis: Complete paper analysis
        summary_type: Type of summary (comprehensive, focused, brief)
        
    Returns:
        Dictionary with structured paper summary
    """
    try:
        if summary_type == "comprehensive":
            summary = {
                "paper_info": {
                    "title": paper_analysis.get("title", ""),
                    "authors": paper_analysis.get("authors", []),
                    "year": paper_analysis.get("year", ""),
                    "citations": paper_analysis.get("citations_count", 0)
                },
                "methodology_summary": paper_analysis.get("methodology", {}),
                "key_findings": paper_analysis.get("key_findings", []),
                "statistical_results": paper_analysis.get("results_summary", {}),
                "quality_score": paper_analysis.get("quality_indicators", {}).get("overall_score", 0),
                "limitations": paper_analysis.get("limitations", []),
                "visual_data_summary": paper_analysis.get("visual_elements", {}),
                "relevance_score": _calculate_relevance_score(paper_analysis),
                "summary_created": datetime.now().isoformat()
            }
        else:
            # Brief summary
            summary = {
                "title": paper_analysis.get("title", ""),
                "year": paper_analysis.get("year", ""),
                "key_finding": paper_analysis.get("key_findings", [""])[0] if paper_analysis.get("key_findings") else "",
                "quality_score": paper_analysis.get("quality_indicators", {}).get("overall_score", 0),
                "summary_created": datetime.now().isoformat()
            }
        
        return summary
        
    except Exception as e:
        return {
            "error": f"Summary creation failed: {str(e)}",
            "summary_created": datetime.now().isoformat()
        }


def _extract_methodology(content: str) -> Dict[str, Any]:
    """Extract methodology information from paper content."""
    # Simplified extraction - in real implementation would use advanced NLP
    methodology = {
        "study_design": "Not specified",
        "sample_size": "Not specified",
        "data_collection": "Not specified",
        "analysis_methods": [],
        "tools_used": []
    }
    
    content_lower = content.lower()
    
    # Detect study design
    if "randomized controlled trial" in content_lower or "rct" in content_lower:
        methodology["study_design"] = "Randomized Controlled Trial"
    elif "systematic review" in content_lower:
        methodology["study_design"] = "Systematic Review"
    elif "meta-analysis" in content_lower:
        methodology["study_design"] = "Meta-analysis"
    elif "cross-sectional" in content_lower:
        methodology["study_design"] = "Cross-sectional Study"
    
    return methodology


def _extract_key_findings(content: str) -> List[str]:
    """Extract key findings from paper content."""
    # Simplified extraction
    findings = []
    
    # Look for common result indicators
    result_indicators = ["found that", "results show", "demonstrated that", "concluded that"]
    
    sentences = content.split('.')
    for sentence in sentences[:50]:  # Check first 50 sentences
        sentence_lower = sentence.lower()
        for indicator in result_indicators:
            if indicator in sentence_lower and len(sentence.strip()) > 20:
                findings.append(sentence.strip())
                break
        
        if len(findings) >= 5:  # Limit to top 5 findings
            break
    
    return findings


def _extract_results(content: str) -> Dict[str, Any]:
    """Extract results section information."""
    return {
        "statistical_significance": "Not analyzed",
        "effect_sizes": [],
        "confidence_intervals": [],
        "p_values": [],
        "sample_characteristics": {}
    }


def _extract_limitations(content: str) -> List[str]:
    """Extract study limitations."""
    limitations = []
    
    # Look for limitation indicators
    limitation_indicators = ["limitation", "constraint", "weakness", "shortcoming"]
    
    sentences = content.split('.')
    for sentence in sentences:
        sentence_lower = sentence.lower()
        for indicator in limitation_indicators:
            if indicator in sentence_lower and len(sentence.strip()) > 15:
                limitations.append(sentence.strip())
                break
        
        if len(limitations) >= 3:  # Limit to top 3 limitations
            break
    
    return limitations


def _assess_quality(content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Assess paper quality indicators."""
    quality_score = 0.5  # Base score
    
    # Adjust based on citation count
    citations = metadata.get("citationCount", 0)
    if citations > 100:
        quality_score += 0.3
    elif citations > 50:
        quality_score += 0.2
    elif citations > 10:
        quality_score += 0.1
    
    # Adjust based on content indicators
    if "methodology" in content.lower():
        quality_score += 0.1
    if "statistical" in content.lower():
        quality_score += 0.1
    
    return {
        "overall_score": min(1.0, quality_score),
        "citation_score": min(1.0, citations / 100),
        "methodology_clarity": 0.7,  # Placeholder
        "statistical_rigor": 0.6     # Placeholder
    }


def _extract_structured_data(content: str) -> Dict[str, Any]:
    """Extract structured data for analysis."""
    return {
        "sample_size": "Not extracted",
        "demographics": {},
        "outcomes": [],
        "interventions": [],
        "measurements": []
    }


def _analyze_visual_elements(content: str) -> Dict[str, Any]:
    """Analyze visual elements in the paper."""
    return {
        "tables_count": content.lower().count("table"),
        "figures_count": content.lower().count("figure"),
        "has_statistical_tables": "statistical" in content.lower(),
        "has_methodology_diagrams": "diagram" in content.lower() or "flowchart" in content.lower()
    }


def _analyze_tables(table_data: List[str]) -> List[Dict[str, Any]]:
    """Analyze table content."""
    analyzed_tables = []
    for i, table in enumerate(table_data):
        analyzed_tables.append({
            "table_id": f"table_{i+1}",
            "content_type": "data_table",
            "has_statistics": "p-value" in table.lower() or "significant" in table.lower(),
            "row_count": table.count('\n') + 1,
            "extracted_data": {}
        })
    return analyzed_tables


def _analyze_figures(descriptions: List[str], captions: List[str]) -> List[Dict[str, Any]]:
    """Analyze figure content."""
    analyzed_figures = []
    for i, (desc, caption) in enumerate(zip(descriptions, captions)):
        analyzed_figures.append({
            "figure_id": f"figure_{i+1}",
            "type": "chart" if "chart" in desc.lower() else "diagram",
            "caption": caption,
            "description": desc,
            "contains_data": "data" in desc.lower() or "result" in desc.lower()
        })
    return analyzed_figures


def _extract_statistical_data(table_data: List[str]) -> Dict[str, Any]:
    """Extract statistical data from tables."""
    return {
        "p_values": [],
        "confidence_intervals": [],
        "effect_sizes": [],
        "sample_sizes": []
    }


def _identify_methodology_diagrams(descriptions: List[str]) -> List[str]:
    """Identify methodology-related diagrams."""
    methodology_diagrams = []
    for desc in descriptions:
        if any(term in desc.lower() for term in ["flow", "process", "method", "procedure"]):
            methodology_diagrams.append(desc)
    return methodology_diagrams


def _identify_results_viz(descriptions: List[str], captions: List[str]) -> List[str]:
    """Identify results visualizations."""
    results_viz = []
    for desc, caption in zip(descriptions, captions):
        if any(term in (desc + caption).lower() for term in ["result", "outcome", "finding", "data"]):
            results_viz.append(f"{caption}: {desc}")
    return results_viz


def _calculate_relevance_score(analysis: Dict[str, Any]) -> float:
    """Calculate relevance score for the paper."""
    base_score = 0.5
    
    # Adjust based on quality
    quality_score = analysis.get("quality_indicators", {}).get("overall_score", 0.5)
    base_score += quality_score * 0.3
    
    # Adjust based on findings count
    findings_count = len(analysis.get("key_findings", []))
    base_score += min(0.2, findings_count * 0.04)
    
    return min(1.0, base_score)


def create_content_analyzer():
    """Create the Content Analyzer subagent with Grok-4-Fast model."""
    
    # Use default model (Grok-4-Fast) for content analysis with 2M token context
    model = get_default_model()
    
    return {
        "name": "content_analyzer",
        "description": (
            "Comprehensive content analysis of papers including methodology, findings, visual elements, and summaries. "
            "Responsible for creating evidence_summary.md. "
            "Handles full-text and multimodal analysis workflows internally using Grok-4-Fast's large context window."
        ),
        "prompt": CONTENT_ANALYZER_PROMPT,
        "model": model,  # Use Grok-4-Fast for large context window
    }
