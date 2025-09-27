"""
Generate PRISMA Diagram Tool

Creates PRISMA flow diagrams for systematic literature reviews.
"""

from langchain_core.tools import tool
from typing import Dict, Any, List
import json
from datetime import datetime


@tool
def generate_prisma_diagram(
    identification_count: int,
    screening_count: int, 
    eligibility_count: int,
    included_count: int,
    exclusion_reasons: Dict[str, int],
    output_format: str = "text"
) -> Dict[str, Any]:
    """Generate a PRISMA flow diagram for systematic review.
    
    Args:
        identification_count: Number of records identified through database searching
        screening_count: Number of records after duplicates removed
        eligibility_count: Number of full-text articles assessed for eligibility
        included_count: Number of studies included in qualitative synthesis
        exclusion_reasons: Dictionary mapping exclusion reasons to counts
        output_format: Output format ("text", "markdown", "json")
        
    Returns:
        Dictionary containing the PRISMA diagram data and formatted output
    """
    try:
        # Calculate derived values
        duplicates_removed = identification_count - screening_count
        excluded_after_screening = screening_count - eligibility_count
        excluded_after_eligibility = eligibility_count - included_count
        
        # Create PRISMA data structure
        prisma_data = {
            "identification": {
                "records_identified": identification_count,
                "duplicates_removed": duplicates_removed,
                "records_screened": screening_count
            },
            "screening": {
                "records_screened": screening_count,
                "records_excluded": excluded_after_screening
            },
            "eligibility": {
                "full_text_assessed": eligibility_count,
                "full_text_excluded": excluded_after_eligibility,
                "exclusion_reasons": exclusion_reasons
            },
            "included": {
                "studies_included": included_count
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Generate formatted output based on requested format
        if output_format == "markdown":
            formatted_output = _generate_markdown_prisma(prisma_data)
        elif output_format == "json":
            formatted_output = json.dumps(prisma_data, indent=2)
        else:  # text format
            formatted_output = _generate_text_prisma(prisma_data)
        
        return {
            "status": "success",
            "prisma_data": prisma_data,
            "formatted_output": formatted_output,
            "output_format": output_format,
            "message": f"Successfully generated PRISMA diagram in {output_format} format"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to generate PRISMA diagram"
        }


def _generate_text_prisma(data: Dict[str, Any]) -> str:
    """Generate text-based PRISMA flow diagram."""
    output = []
    output.append("PRISMA FLOW DIAGRAM")
    output.append("=" * 50)
    output.append("")
    
    # Identification
    output.append("IDENTIFICATION:")
    output.append(f"  Records identified: {data['identification']['records_identified']}")
    output.append(f"  Duplicates removed: {data['identification']['duplicates_removed']}")
    output.append(f"  Records for screening: {data['identification']['records_screened']}")
    output.append("")
    
    # Screening
    output.append("SCREENING:")
    output.append(f"  Records screened: {data['screening']['records_screened']}")
    output.append(f"  Records excluded: {data['screening']['records_excluded']}")
    output.append("")
    
    # Eligibility
    output.append("ELIGIBILITY:")
    output.append(f"  Full-text articles assessed: {data['eligibility']['full_text_assessed']}")
    output.append(f"  Full-text articles excluded: {data['eligibility']['full_text_excluded']}")
    
    if data['eligibility']['exclusion_reasons']:
        output.append("  Exclusion reasons:")
        for reason, count in data['eligibility']['exclusion_reasons'].items():
            output.append(f"    - {reason}: {count}")
    output.append("")
    
    # Included
    output.append("INCLUDED:")
    output.append(f"  Studies included in synthesis: {data['included']['studies_included']}")
    
    return "\n".join(output)


def _generate_markdown_prisma(data: Dict[str, Any]) -> str:
    """Generate markdown-based PRISMA flow diagram."""
    output = []
    output.append("# PRISMA Flow Diagram")
    output.append("")
    
    # Identification
    output.append("## Identification")
    output.append(f"- **Records identified**: {data['identification']['records_identified']}")
    output.append(f"- **Duplicates removed**: {data['identification']['duplicates_removed']}")
    output.append(f"- **Records for screening**: {data['identification']['records_screened']}")
    output.append("")
    
    # Screening
    output.append("## Screening")
    output.append(f"- **Records screened**: {data['screening']['records_screened']}")
    output.append(f"- **Records excluded**: {data['screening']['records_excluded']}")
    output.append("")
    
    # Eligibility
    output.append("## Eligibility")
    output.append(f"- **Full-text articles assessed**: {data['eligibility']['full_text_assessed']}")
    output.append(f"- **Full-text articles excluded**: {data['eligibility']['full_text_excluded']}")
    
    if data['eligibility']['exclusion_reasons']:
        output.append("- **Exclusion reasons**:")
        for reason, count in data['eligibility']['exclusion_reasons'].items():
            output.append(f"  - {reason}: {count}")
    output.append("")
    
    # Included
    output.append("## Included")
    output.append(f"- **Studies included in synthesis**: {data['included']['studies_included']}")
    
    return "\n".join(output)
