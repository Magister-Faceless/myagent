"""
Search tools for CORE API
"""

import asyncio
import aiohttp
import csv
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from deepagents.tools import tool
from deepagents.decorators import handle_large_response

from .config import CORE_API_CONFIG, get_api_headers
from .utils import (
    make_api_request, 
    build_query_string, 
    format_authors, 
    clean_text, 
    extract_year,
    generate_filename,
    validate_doi
)

@tool(description="Search CORE API for academic works using advanced query language")
async def search_works(
    query: str,
    limit: int = 100,
    offset: int = 0,
    require_full_text: bool = False,
    date_range: Optional[Dict[str, str]] = None,
    document_types: Optional[List[str]] = None,
    fields_of_study: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Search for academic works in CORE database
    
    Args:
        query: Search query using CORE query language
        limit: Maximum number of results (default: 100, max: 10000)
        offset: Offset for pagination (default: 0)
        require_full_text: Only return works with full text available
        date_range: Dict with 'start_year' and 'end_year' keys
        document_types: List of document types to filter by
        fields_of_study: List of fields of study to filter by
        
    Returns:
        dict: Search results with metadata
        
    Example:
        results = await search_works(
            query="machine learning healthcare",
            limit=50,
            require_full_text=True,
            date_range={"start_year": "2020", "end_year": "2024"}
        )
    """
    try:
        # Validate inputs
        limit = min(limit, CORE_API_CONFIG["max_limit"])
        
        # Build filters
        filters = {}
        if document_types:
            filters["documentType"] = document_types
        if fields_of_study:
            filters["fieldOfStudy"] = fields_of_study
        
        # Build complete query
        complete_query = build_query_string(
            base_query=query,
            filters=filters,
            date_range=date_range,
            require_full_text=require_full_text
        )
        
        # Prepare request
        url = f"{CORE_API_CONFIG['base_url']}/search/works"
        params = {
            "q": complete_query,
            "limit": limit,
            "offset": offset
        }
        
        headers = get_api_headers()
        
        async with aiohttp.ClientSession() as session:
            response_data = await make_api_request(
                session=session,
                url=url,
                method="GET",
                params=params,
                headers=headers,
                timeout=CORE_API_CONFIG["timeout"]
            )
        
        # Process results - handle both list and dict responses
        results = response_data.get("results", [])
        processed_results = []
        
        # Ensure results is a list
        if not isinstance(results, list):
            results = []
        
        for work in results:
            # Ensure work is a dictionary
            if not isinstance(work, dict):
                continue
                
            # Safely extract identifiers
            identifiers = work.get("identifiers", {})
            if isinstance(identifiers, dict):
                doi = identifiers.get("doi")
            else:
                doi = None
            
            # Safely extract data provider
            data_provider = work.get("dataProvider", {})
            if isinstance(data_provider, dict):
                provider_name = data_provider.get("name")
            else:
                provider_name = None
            
            processed_work = {
                "core_id": work.get("id"),
                "title": clean_text(work.get("title", ""), 200),
                "authors": format_authors(work.get("authors", [])),
                "year": extract_year(work.get("yearPublished") or work.get("publishedDate")),
                "doi": doi,
                "abstract": clean_text(work.get("abstract", ""), 300),
                "full_text_available": bool(work.get("fullText")),
                "data_provider": provider_name,
                "document_type": work.get("documentType"),
                "field_of_study": work.get("fieldOfStudy"),
                "citation_count": work.get("citationCount", 0),
                "download_url": work.get("downloadUrl")
            }
            processed_results.append(processed_work)
        
        # Use correct field names from CORE API response format
        total_hits = response_data.get("total_hits", response_data.get("totalHits", len(results)))
        
        return {
            "success": True,
            "query": complete_query,
            "total_hits": total_hits,
            "results_count": len(processed_results),
            "offset": offset,
            "limit": limit,
            "results": processed_results,
            "has_more": total_hits > (offset + len(results))
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "results": []
        }

@tool(description="Export large search results from CORE API to structured files")
@handle_large_response(max_length=50000)
async def scroll_export_works(
    query: str,
    max_results: int = 1000,
    require_full_text: bool = False,
    date_range: Optional[Dict[str, str]] = None,
    document_types: Optional[List[str]] = None,
    output_format: str = "csv"
) -> Dict[str, Any]:
    """
    Export large datasets from CORE API using scroll/pagination
    
    Args:
        query: Search query using CORE query language
        max_results: Maximum number of results to export
        require_full_text: Only return works with full text available
        date_range: Dict with 'start_year' and 'end_year' keys
        document_types: List of document types to filter by
        output_format: Output format ('csv', 'json', 'md')
        
    Returns:
        dict: Export summary with file paths
        
    Note: This function uses @handle_large_response and will automatically
          write results to files when the response exceeds 50K tokens.
    """
    try:
        all_results = []
        offset = 0
        batch_size = min(100, max_results)
        
        # Generate filename
        filename = generate_filename(
            prefix="core_export",
            query=query[:50],
            extension=output_format
        )
        
        while len(all_results) < max_results:
            # Calculate remaining results needed
            remaining = max_results - len(all_results)
            current_limit = min(batch_size, remaining)
            
            # Search batch
            batch_result = await search_works(
                query=query,
                limit=current_limit,
                offset=offset,
                require_full_text=require_full_text,
                date_range=date_range,
                document_types=document_types
            )
            
            if not batch_result["success"]:
                break
            
            batch_results = batch_result["results"]
            if not batch_results:
                break
            
            all_results.extend(batch_results)
            offset += len(batch_results)
            
            # Check if we have all available results
            if not batch_result.get("has_more", False):
                break
            
            # Small delay to respect rate limits
            await asyncio.sleep(0.1)
        
        # Write results to file
        output_path = Path("output") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        if output_format == "csv":
            await _write_csv_file(output_path, all_results)
        elif output_format == "json":
            await _write_json_file(output_path, all_results)
        elif output_format == "md":
            await _write_markdown_file(output_path, all_results, query)
        
        return {
            "success": True,
            "query": query,
            "total_exported": len(all_results),
            "output_file": str(output_path),
            "output_format": output_format,
            "file_size": output_path.stat().st_size if output_path.exists() else 0,
            "summary": {
                "unique_authors": len(set(r["authors"] for r in all_results if r["authors"] != "Unknown")),
                "year_range": _get_year_range(all_results),
                "with_full_text": sum(1 for r in all_results if r["full_text_available"]),
                "with_doi": sum(1 for r in all_results if r["doi"])
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "total_exported": 0
        }

async def _write_csv_file(file_path: Path, results: List[Dict[str, Any]]) -> None:
    """Write results to CSV file"""
    if not results:
        return
    
    fieldnames = [
        "core_id", "title", "authors", "year", "doi", "abstract",
        "full_text_available", "data_provider", "document_type",
        "field_of_study", "citation_count", "download_url"
    ]
    
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            # Ensure all fields are present
            row = {field: result.get(field, "") for field in fieldnames}
            writer.writerow(row)

async def _write_json_file(file_path: Path, results: List[Dict[str, Any]]) -> None:
    """Write results to JSON file"""
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump({
            "exported_at": str(asyncio.get_event_loop().time()),
            "total_results": len(results),
            "results": results
        }, jsonfile, indent=2, ensure_ascii=False)

async def _write_markdown_file(file_path: Path, results: List[Dict[str, Any]], query: str) -> None:
    """Write results to Markdown file"""
    with open(file_path, 'w', encoding='utf-8') as mdfile:
        mdfile.write(f"# CORE API Export Results\n\n")
        mdfile.write(f"**Query:** {query}\n\n")
        mdfile.write(f"**Total Results:** {len(results)}\n\n")
        mdfile.write(f"**Exported:** {asyncio.get_event_loop().time()}\n\n")
        
        mdfile.write("## Results\n\n")
        
        for i, result in enumerate(results, 1):
            mdfile.write(f"### {i}. {result.get('title', 'Untitled')}\n\n")
            mdfile.write(f"**Authors:** {result.get('authors', 'Unknown')}\n\n")
            mdfile.write(f"**Year:** {result.get('year', 'Unknown')}\n\n")
            
            if result.get('doi'):
                mdfile.write(f"**DOI:** {result['doi']}\n\n")
            
            if result.get('abstract'):
                mdfile.write(f"**Abstract:** {result['abstract']}\n\n")
            
            mdfile.write(f"**Full Text Available:** {'Yes' if result.get('full_text_available') else 'No'}\n\n")
            mdfile.write("---\n\n")

def _get_year_range(results: List[Dict[str, Any]]) -> Dict[str, Optional[int]]:
    """Get year range from results"""
    years = [r["year"] for r in results if r["year"]]
    if not years:
        return {"min": None, "max": None}
    
    return {"min": min(years), "max": max(years)}
