"""
Export Citations Tool

Exports research paper citations in various academic formats.
"""

from langchain_core.tools import tool
from typing import Dict, Any, List
import json
from datetime import datetime


@tool
def export_citations(
    papers: List[Dict[str, Any]], 
    format_type: str = "bibtex",
    filename: str = None
) -> Dict[str, Any]:
    """Export citations in specified academic format.
    
    Args:
        papers: List of paper metadata dictionaries
        format_type: Citation format ("bibtex", "apa", "mla", "chicago", "endnote")
        filename: Optional filename for export (auto-generated if not provided)
        
    Returns:
        Dictionary containing formatted citations and export information
    """
    try:
        if not papers:
            return {
                "status": "error",
                "message": "No papers provided for citation export"
            }
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"citations_{format_type}_{timestamp}.{_get_file_extension(format_type)}"
        
        # Format citations based on requested format
        if format_type.lower() == "bibtex":
            formatted_citations = _format_bibtex(papers)
        elif format_type.lower() == "apa":
            formatted_citations = _format_apa(papers)
        elif format_type.lower() == "mla":
            formatted_citations = _format_mla(papers)
        elif format_type.lower() == "chicago":
            formatted_citations = _format_chicago(papers)
        elif format_type.lower() == "endnote":
            formatted_citations = _format_endnote(papers)
        else:
            return {
                "status": "error",
                "message": f"Unsupported citation format: {format_type}"
            }
        
        return {
            "status": "success",
            "citations": formatted_citations,
            "format": format_type,
            "filename": filename,
            "paper_count": len(papers),
            "message": f"Successfully exported {len(papers)} citations in {format_type} format"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to export citations in {format_type} format"
        }


def _get_file_extension(format_type: str) -> str:
    """Get appropriate file extension for citation format."""
    extensions = {
        "bibtex": "bib",
        "apa": "txt",
        "mla": "txt", 
        "chicago": "txt",
        "endnote": "enw"
    }
    return extensions.get(format_type.lower(), "txt")


def _format_bibtex(papers: List[Dict[str, Any]]) -> str:
    """Format citations in BibTeX format."""
    citations = []
    
    for i, paper in enumerate(papers):
        # Generate citation key
        first_author = paper.get('authors', ['Unknown'])[0].split(',')[0] if paper.get('authors') else 'Unknown'
        year = paper.get('year', 'Unknown')
        key = f"{first_author.replace(' ', '')}{year}"
        
        # Determine entry type
        entry_type = "article"  # Default to article
        
        citation = f"@{entry_type}{{{key},\n"
        citation += f"  title = {{{paper.get('title', 'Unknown Title')}}},\n"
        
        if paper.get('authors'):
            authors = ' and '.join(paper['authors'])
            citation += f"  author = {{{authors}}},\n"
        
        if paper.get('journal'):
            citation += f"  journal = {{{paper['journal']}}},\n"
        
        if paper.get('year'):
            citation += f"  year = {{{paper['year']}}},\n"
        
        if paper.get('volume'):
            citation += f"  volume = {{{paper['volume']}}},\n"
        
        if paper.get('issue'):
            citation += f"  number = {{{paper['issue']}}},\n"
        
        if paper.get('pages'):
            citation += f"  pages = {{{paper['pages']}}},\n"
        
        if paper.get('doi'):
            citation += f"  doi = {{{paper['doi']}}},\n"
        
        citation += "}\n"
        citations.append(citation)
    
    return "\n".join(citations)


def _format_apa(papers: List[Dict[str, Any]]) -> str:
    """Format citations in APA format."""
    citations = []
    
    for paper in papers:
        citation_parts = []
        
        # Authors
        if paper.get('authors'):
            if len(paper['authors']) == 1:
                citation_parts.append(f"{paper['authors'][0]}")
            elif len(paper['authors']) <= 7:
                authors = ', '.join(paper['authors'][:-1]) + f", & {paper['authors'][-1]}"
                citation_parts.append(authors)
            else:
                authors = ', '.join(paper['authors'][:6]) + ", ... " + paper['authors'][-1]
                citation_parts.append(authors)
        
        # Year
        if paper.get('year'):
            citation_parts.append(f"({paper['year']})")
        
        # Title
        if paper.get('title'):
            citation_parts.append(f"{paper['title']}.")
        
        # Journal info
        if paper.get('journal'):
            journal_part = f"*{paper['journal']}*"
            if paper.get('volume'):
                journal_part += f", *{paper['volume']}*"
                if paper.get('issue'):
                    journal_part += f"({paper['issue']})"
            if paper.get('pages'):
                journal_part += f", {paper['pages']}"
            citation_parts.append(journal_part + ".")
        
        # DOI
        if paper.get('doi'):
            citation_parts.append(f"https://doi.org/{paper['doi']}")
        
        citations.append(' '.join(citation_parts))
    
    return '\n\n'.join(citations)


def _format_mla(papers: List[Dict[str, Any]]) -> str:
    """Format citations in MLA format."""
    citations = []
    
    for paper in papers:
        citation_parts = []
        
        # Author(s)
        if paper.get('authors'):
            if len(paper['authors']) == 1:
                citation_parts.append(f"{paper['authors'][0]}.")
            else:
                first_author = paper['authors'][0]
                citation_parts.append(f"{first_author}, et al.")
        
        # Title
        if paper.get('title'):
            citation_parts.append(f'"{paper["title"]}."')
        
        # Journal
        if paper.get('journal'):
            citation_parts.append(f"*{paper['journal']}*,")
        
        # Volume and issue
        if paper.get('volume'):
            vol_part = f"vol. {paper['volume']}"
            if paper.get('issue'):
                vol_part += f", no. {paper['issue']}"
            citation_parts.append(vol_part + ",")
        
        # Year
        if paper.get('year'):
            citation_parts.append(f"{paper['year']},")
        
        # Pages
        if paper.get('pages'):
            citation_parts.append(f"pp. {paper['pages']}.")
        
        citations.append(' '.join(citation_parts))
    
    return '\n\n'.join(citations)


def _format_chicago(papers: List[Dict[str, Any]]) -> str:
    """Format citations in Chicago format."""
    citations = []
    
    for paper in papers:
        citation_parts = []
        
        # Author(s)
        if paper.get('authors'):
            if len(paper['authors']) == 1:
                citation_parts.append(f"{paper['authors'][0]}.")
            else:
                first_author = paper['authors'][0]
                others = ', '.join(paper['authors'][1:])
                citation_parts.append(f"{first_author}, and {others}.")
        
        # Title
        if paper.get('title'):
            citation_parts.append(f'"{paper["title"]}."')
        
        # Journal
        if paper.get('journal'):
            citation_parts.append(f"*{paper['journal']}*")
        
        # Volume, issue, year
        if paper.get('volume') or paper.get('issue') or paper.get('year'):
            vol_part = ""
            if paper.get('volume'):
                vol_part += f"{paper['volume']}"
            if paper.get('issue'):
                vol_part += f", no. {paper['issue']}"
            if paper.get('year'):
                vol_part += f" ({paper['year']})"
            citation_parts.append(vol_part + ":")
        
        # Pages
        if paper.get('pages'):
            citation_parts.append(f"{paper['pages']}.")
        
        citations.append(' '.join(citation_parts))
    
    return '\n\n'.join(citations)


def _format_endnote(papers: List[Dict[str, Any]]) -> str:
    """Format citations in EndNote format."""
    citations = []
    
    for paper in papers:
        citation = "%0 Journal Article\n"
        
        if paper.get('title'):
            citation += f"%T {paper['title']}\n"
        
        if paper.get('authors'):
            for author in paper['authors']:
                citation += f"%A {author}\n"
        
        if paper.get('journal'):
            citation += f"%J {paper['journal']}\n"
        
        if paper.get('year'):
            citation += f"%D {paper['year']}\n"
        
        if paper.get('volume'):
            citation += f"%V {paper['volume']}\n"
        
        if paper.get('issue'):
            citation += f"%N {paper['issue']}\n"
        
        if paper.get('pages'):
            citation += f"%P {paper['pages']}\n"
        
        if paper.get('doi'):
            citation += f"%R {paper['doi']}\n"
        
        citation += "\n"
        citations.append(citation)
    
    return ''.join(citations)
