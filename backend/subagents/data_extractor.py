"""
Data Extractor Subagent - DeepAgents v1.1 Implementation

Handles structured data extraction from research papers following
the deepagents SubAgent pattern.
"""

from src.deepagents.sub_agent import SubAgent
from langchain_core.tools import tool
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

# Import prompts
from config.prompts import DATA_EXTRACTOR_PROMPT


@tool
def extract_study_data(
    papers: List[Dict[str, Any]],
    extraction_fields: List[str] = None
) -> Dict[str, Any]:
    """Extract structured data from research papers.
    
    Args:
        papers: List of papers to extract data from
        extraction_fields: Specific fields to extract (optional)
        
    Returns:
        Dictionary with extracted structured data
    """
    try:
        if extraction_fields is None:
            extraction_fields = [
                "study_design", "sample_size", "interventions", 
                "outcomes", "key_findings", "limitations"
            ]
        
        extracted_data = []
        
        for paper in papers:
            # Mock data extraction - in real implementation would analyze paper content
            study_data = {
                "paper_id": paper.get('id', f"paper_{len(extracted_data)}"),
                "title": paper.get('title', 'Untitled'),
                "authors": paper.get('authors', []),
                "year": paper.get('year', datetime.now().year),
                "journal": paper.get('journal', ''),
                "doi": paper.get('doi'),
                "study_design": _extract_study_design(paper),
                "sample_size": _extract_sample_size(paper),
                "participants": _extract_participant_info(paper),
                "interventions": _extract_interventions(paper),
                "outcomes": _extract_outcomes(paper),
                "key_findings": _extract_key_findings(paper),
                "limitations": _extract_limitations(paper),
                "quality_indicators": _extract_quality_indicators(paper),
                "extracted_at": datetime.utcnow().isoformat()
            }
            
            # Filter by requested fields
            if extraction_fields:
                filtered_data = {k: v for k, v in study_data.items() 
                               if k in extraction_fields or k in ['paper_id', 'title', 'extracted_at']}
                extracted_data.append(filtered_data)
            else:
                extracted_data.append(study_data)
        
        return {
            "status": "success",
            "extracted_data": extracted_data,
            "extraction_summary": {
                "total_papers": len(papers),
                "successfully_extracted": len(extracted_data),
                "fields_extracted": extraction_fields or "all"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to extract study data"
        }


@tool
def create_data_extraction_table(
    extracted_data: List[Dict[str, Any]],
    table_format: str = "markdown"
) -> Dict[str, Any]:
    """Create a structured table from extracted data.
    
    Args:
        extracted_data: List of extracted study data
        table_format: Format for the table ("markdown", "csv", "json")
        
    Returns:
        Dictionary with formatted table
    """
    try:
        if not extracted_data:
            return {
                "status": "error",
                "message": "No extracted data provided"
            }
        
        if table_format == "markdown":
            table = _create_markdown_table(extracted_data)
        elif table_format == "csv":
            table = _create_csv_table(extracted_data)
        else:  # json
            table = json.dumps(extracted_data, indent=2)
        
        return {
            "status": "success",
            "table": table,
            "format": table_format,
            "row_count": len(extracted_data)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to create {table_format} table"
        }


def _extract_study_design(paper: Dict[str, Any]) -> str:
    """Extract study design from paper."""
    # Mock extraction - would analyze paper content
    title = paper.get('title', '').lower()
    abstract = paper.get('abstract', '').lower()
    
    if 'randomized' in title or 'rct' in title:
        return "randomized_controlled_trial"
    elif 'cohort' in title or 'longitudinal' in title:
        return "cohort_study"
    elif 'case-control' in title:
        return "case_control_study"
    elif 'systematic review' in title:
        return "systematic_review"
    elif 'meta-analysis' in title:
        return "meta_analysis"
    else:
        return "other"


def _extract_sample_size(paper: Dict[str, Any]) -> Optional[int]:
    """Extract sample size from paper."""
    # Mock extraction - would parse abstract/methods for sample size
    abstract = paper.get('abstract', '')
    # Simple regex would be used in real implementation
    return 100  # Placeholder


def _extract_participant_info(paper: Dict[str, Any]) -> Dict[str, Any]:
    """Extract participant information."""
    return {
        "sample_size": _extract_sample_size(paper),
        "age_mean": None,  # Would extract from text
        "gender_distribution": None,  # Would extract from text
        "population": "Not specified"  # Would extract from text
    }


def _extract_interventions(paper: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract intervention information."""
    # Mock extraction
    return [{
        "name": "Intervention A",
        "description": "Primary intervention described in study",
        "duration": "Not specified",
        "comparator": "Control group"
    }]


def _extract_outcomes(paper: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract outcome measures."""
    # Mock extraction
    return [{
        "name": "Primary outcome",
        "measure": "Not specified",
        "time_frame": "Not specified",
        "significance": None
    }]


def _extract_key_findings(paper: Dict[str, Any]) -> List[str]:
    """Extract key findings."""
    # Mock extraction
    return ["Key finding 1", "Key finding 2"]


def _extract_limitations(paper: Dict[str, Any]) -> List[str]:
    """Extract study limitations."""
    # Mock extraction
    return ["Limitation 1", "Limitation 2"]


def _extract_quality_indicators(paper: Dict[str, Any]) -> Dict[str, Any]:
    """Extract quality indicators."""
    return {
        "peer_reviewed": True,
        "impact_factor": paper.get('impact_factor'),
        "citation_count": paper.get('citation_count'),
        "funding_disclosed": None
    }


def _create_markdown_table(data: List[Dict[str, Any]]) -> str:
    """Create markdown table from extracted data."""
    if not data:
        return "No data to display"
    
    # Get common fields
    fields = ["title", "year", "study_design", "sample_size", "key_findings"]
    
    # Create header
    header = "| " + " | ".join(fields) + " |"
    separator = "|" + "|".join([" --- " for _ in fields]) + "|"
    
    # Create rows
    rows = []
    for item in data:
        row_data = []
        for field in fields:
            value = item.get(field, "N/A")
            if isinstance(value, list):
                value = "; ".join(str(v) for v in value[:2])  # Limit to first 2 items
            row_data.append(str(value))
        rows.append("| " + " | ".join(row_data) + " |")
    
    return "\n".join([header, separator] + rows)


def _create_csv_table(data: List[Dict[str, Any]]) -> str:
    """Create CSV table from extracted data."""
    if not data:
        return "No data to display"
    
    import csv
    import io
    
    output = io.StringIO()
    
    # Get all unique fields
    all_fields = set()
    for item in data:
        all_fields.update(item.keys())
    
    fieldnames = sorted(list(all_fields))
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    for item in data:
        # Convert lists to strings for CSV
        csv_item = {}
        for key, value in item.items():
            if isinstance(value, list):
                csv_item[key] = "; ".join(str(v) for v in value)
            else:
                csv_item[key] = value
        writer.writerow(csv_item)
    
    return output.getvalue()


def create_data_extractor() -> SubAgent:
    """Create a data extractor subagent following deepagents v1.1 pattern."""
    return SubAgent(
        name="data_extractor",
        description="Extracts structured data from research papers for systematic reviews",
        prompt=DATA_EXTRACTOR_PROMPT,
        tools=[
            extract_study_data,
            create_data_extraction_table,
        ]
    )
