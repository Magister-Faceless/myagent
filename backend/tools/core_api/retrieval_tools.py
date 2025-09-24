"""
Retrieval tools for CORE API
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from deepagents.tools import tool
from deepagents.decorators import handle_large_response

from .config import CORE_API_CONFIG, get_api_headers
from .utils import (
    make_api_request, 
    format_authors, 
    clean_text, 
    extract_year,
    validate_doi,
    generate_filename
)

@tool(description="Retrieve a single academic work by ID or DOI from CORE API")
@handle_large_response(max_length=50000)
async def get_work_by_id(
    identifier: str,
    include_full_text: bool = True,
    include_citations: bool = False
) -> Dict[str, Any]:
    """
    Retrieve detailed information for a single work from CORE
    
    Args:
        identifier: CORE ID, DOI, or other supported identifier
        include_full_text: Whether to include full text content
        include_citations: Whether to include citation information
        
    Returns:
        dict: Detailed work information
        
    Note: When include_full_text=True, large responses are automatically
          saved to files due to @handle_large_response decorator.
    """
    try:
        # Clean identifier
        identifier = identifier.strip()
        
        # If it's a DOI, validate it
        if identifier.startswith("10."):
            if not validate_doi(identifier):
                return {
                    "success": False,
                    "error": f"Invalid DOI format: {identifier}",
                    "identifier": identifier
                }
        
        # Prepare request
        url = f"{CORE_API_CONFIG['base_url']}/works/{identifier}"
        headers = get_api_headers()
        
        async with aiohttp.ClientSession() as session:
            response_data = await make_api_request(
                session=session,
                url=url,
                method="GET",
                headers=headers,
                timeout=CORE_API_CONFIG["timeout"]
            )
        
        # Process work data
        work = response_data
        
        # Extract basic information
        processed_work = {
            "core_id": work.get("id"),
            "title": clean_text(work.get("title", ""), 500),
            "authors": format_authors(work.get("authors", [])),
            "year": extract_year(work.get("yearPublished") or work.get("publishedDate")),
            "doi": work.get("identifiers", {}).get("doi"),
            "abstract": clean_text(work.get("abstract", ""), 1000),
            "full_text_available": bool(work.get("fullText")),
            "data_provider": work.get("dataProvider", {}).get("name"),
            "document_type": work.get("documentType"),
            "field_of_study": work.get("fieldOfStudy"),
            "citation_count": work.get("citationCount", 0),
            "download_url": work.get("downloadUrl"),
            "language": work.get("language"),
            "publisher": work.get("publisher"),
            "journal": work.get("journals", [{}])[0].get("title") if work.get("journals") else None,
            "subjects": work.get("subjects", []),
            "keywords": work.get("tags", [])
        }
        
        # Add full text if requested and available
        full_text_content = None
        if include_full_text and work.get("fullText"):
            full_text_content = work["fullText"]
            
            # If full text is very large, save to file
            if len(full_text_content) > 10000:  # 10KB threshold
                filename = generate_filename(
                    prefix="fulltext",
                    query=processed_work["title"][:50],
                    extension="txt"
                )
                
                output_path = Path("output") / filename
                output_path.parent.mkdir(exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {processed_work['title']}\n")
                    f.write(f"Authors: {processed_work['authors']}\n")
                    f.write(f"Year: {processed_work['year']}\n")
                    f.write(f"DOI: {processed_work['doi']}\n\n")
                    f.write("Full Text:\n")
                    f.write(full_text_content)
                
                processed_work["full_text_file"] = str(output_path)
                processed_work["full_text_size"] = len(full_text_content)
            else:
                processed_work["full_text"] = full_text_content
        
        # Add citation information if requested
        if include_citations:
            processed_work["citations"] = work.get("citations", [])
            processed_work["references"] = work.get("references", [])
        
        return {
            "success": True,
            "identifier": identifier,
            "work": processed_work
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "identifier": identifier
        }

@tool(description="Retrieve multiple academic works by their IDs in batch")
@handle_large_response(max_length=50000)
async def batch_get_works_by_ids(
    identifiers: List[str],
    include_full_text: bool = False,
    output_format: str = "json"
) -> Dict[str, Any]:
    """
    Retrieve multiple works by their identifiers in batch
    
    Args:
        identifiers: List of CORE IDs, DOIs, or other identifiers
        include_full_text: Whether to include full text content
        output_format: Output format ('json', 'csv')
        
    Returns:
        dict: Batch retrieval results with file paths
        
    Note: Large responses are automatically saved to files due to
          @handle_large_response decorator.
    """
    try:
        results = []
        errors = []
        
        # Process identifiers in batches to respect rate limits
        batch_size = 10
        
        for i in range(0, len(identifiers), batch_size):
            batch_ids = identifiers[i:i + batch_size]
            
            # Process batch concurrently
            batch_tasks = [
                get_work_by_id(
                    identifier=id_val,
                    include_full_text=include_full_text,
                    include_citations=False
                )
                for id_val in batch_ids
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    errors.append(str(result))
                elif result.get("success"):
                    results.append(result["work"])
                else:
                    errors.append(result.get("error", "Unknown error"))
            
            # Small delay between batches
            if i + batch_size < len(identifiers):
                await asyncio.sleep(0.5)
        
        # Generate output file
        filename = generate_filename(
            prefix="batch_works",
            query=f"{len(identifiers)}_works",
            extension=output_format
        )
        
        output_path = Path("output") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        if output_format == "json":
            await _write_batch_json(output_path, results, errors, identifiers)
        elif output_format == "csv":
            await _write_batch_csv(output_path, results)
        
        return {
            "success": True,
            "total_requested": len(identifiers),
            "total_retrieved": len(results),
            "total_errors": len(errors),
            "output_file": str(output_path),
            "output_format": output_format,
            "errors": errors[:10],  # First 10 errors only
            "summary": {
                "with_full_text": sum(1 for r in results if r.get("full_text_available")),
                "with_doi": sum(1 for r in results if r.get("doi")),
                "unique_years": len(set(r["year"] for r in results if r["year"])),
                "document_types": list(set(r["document_type"] for r in results if r["document_type"]))
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "total_requested": len(identifiers),
            "total_retrieved": 0
        }

async def _write_batch_json(
    file_path: Path, 
    results: List[Dict[str, Any]], 
    errors: List[str],
    identifiers: List[str]
) -> None:
    """Write batch results to JSON file"""
    output_data = {
        "batch_info": {
            "total_requested": len(identifiers),
            "total_retrieved": len(results),
            "total_errors": len(errors),
            "retrieved_at": asyncio.get_event_loop().time()
        },
        "results": results,
        "errors": errors
    }
    
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(output_data, jsonfile, indent=2, ensure_ascii=False)

async def _write_batch_csv(file_path: Path, results: List[Dict[str, Any]]) -> None:
    """Write batch results to CSV file"""
    import csv
    
    if not results:
        return
    
    fieldnames = [
        "core_id", "title", "authors", "year", "doi", "abstract",
        "full_text_available", "data_provider", "document_type",
        "field_of_study", "citation_count", "language", "publisher",
        "journal", "subjects", "keywords"
    ]
    
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            # Flatten complex fields
            row = result.copy()
            row["subjects"] = "; ".join(row.get("subjects", []))
            row["keywords"] = "; ".join(row.get("keywords", []))
            
            # Ensure all fields are present
            row = {field: row.get(field, "") for field in fieldnames}
            writer.writerow(row)
