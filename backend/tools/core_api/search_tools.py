"""
Search tools for CORE API
"""

import asyncio
import aiohttp
import csv
import json
from typing import Dict, Any, List, Optional, Annotated
from pathlib import Path

from langchain_core.tools import tool, InjectedToolCallId
from langgraph.types import Command
from langchain_core.messages import ToolMessage
try:
    from langgraph.prebuilt import InjectedState
except ImportError:
    # Fallback for newer versions
    from typing import Any
    InjectedState = Any

from deepagents.state import DeepAgentState
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
async def scroll_export_works(
    query: str,
    max_results: int = 1000,
    require_full_text: bool = False,
    date_range: Optional[Dict[str, str]] = None,
    document_types: Optional[List[str]] = None,
    output_format: str = "csv",
    state: Annotated[DeepAgentState, InjectedState] = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
) -> Command:
    """
    Export large datasets from CORE API using scroll/pagination
    
    Args:
        query: Search query using CORE query language
        max_results: Maximum number of results to export
        require_full_text: Only return works with full text available
        date_range: Dict with 'start_year' and 'end_year' keys
        document_types: List of document types to filter by
        output_format: Output format ('csv', 'json', 'md')
        state: Agent state (injected automatically)
        tool_call_id: Tool call ID (injected automatically)
        
    Returns:
        Command: LangGraph command with file updates and progress messages
    """
    try:
        # Initialize progress tracking
        progress_messages = []
        all_results = []
        offset = 0
        batch_size = min(100, max_results)
        
        # Generate filename
        filename = generate_filename(
            prefix="core_export",
            query=query[:50],
            extension=output_format
        )
        
        # Send initial progress message
        progress_messages.append(
            ToolMessage(
                content=f"🔍 Starting export of up to {max_results} results for query: {query[:100]}...",
                tool_call_id=tool_call_id,
                additional_kwargs={"progress": "started", "filename": filename}
            )
        )
        
        while len(all_results) < max_results:
            # Calculate remaining results needed
            remaining = max_results - len(all_results)
            current_limit = min(batch_size, remaining)
            
            # Send progress update
            if len(all_results) > 0 and len(all_results) % 200 == 0:
                progress_messages.append(
                    ToolMessage(
                        content=f"📊 Progress: Retrieved {len(all_results)} results so far...",
                        tool_call_id=tool_call_id,
                        additional_kwargs={"progress": "ongoing", "count": len(all_results)}
                    )
                )
            
            # Search batch
            batch_result = await search_works(
                query=query,
                limit=current_limit,
                offset=offset,
                require_full_text=require_full_text,
                date_range=date_range,
                document_types=document_types
            )
            
            if not batch_result.get("success", False):
                error_msg = batch_result.get("error", "Unknown search error")
                progress_messages.append(
                    ToolMessage(
                        content=f"❌ Search failed: {error_msg}",
                        tool_call_id=tool_call_id,
                        additional_kwargs={"error": True}
                    )
                )
                break
            
            batch_results = batch_result.get("results", [])
            if not batch_results:
                progress_messages.append(
                    ToolMessage(
                        content=f"✅ No more results available. Retrieved {len(all_results)} total results.",
                        tool_call_id=tool_call_id,
                        additional_kwargs={"progress": "complete_no_more"}
                    )
                )
                break
            
            all_results.extend(batch_results)
            offset += len(batch_results)
            
            # Check if we have all available results
            if not batch_result.get("has_more", False):
                progress_messages.append(
                    ToolMessage(
                        content=f"✅ Retrieved all available results: {len(all_results)} papers",
                        tool_call_id=tool_call_id,
                        additional_kwargs={"progress": "complete_all"}
                    )
                )
                break
            
            # Small delay to respect rate limits
            await asyncio.sleep(0.1)
        
        if not all_results:
            progress_messages.append(
                ToolMessage(
                    content="❌ No results found for the given query and criteria.",
                    tool_call_id=tool_call_id,
                    additional_kwargs={"error": True, "reason": "no_results"}
                )
            )
            return Command(update={"messages": progress_messages})
        
        # Prepare file content
        if output_format == "csv":
            file_content = await _generate_csv_content(all_results)
        elif output_format == "json":
            file_content = await _generate_json_content(all_results)
        elif output_format == "md":
            file_content = await _generate_markdown_content(all_results, query)
        else:
            progress_messages.append(
                ToolMessage(
                    content=f"❌ Unsupported output format: {output_format}",
                    tool_call_id=tool_call_id,
                    additional_kwargs={"error": True, "reason": "invalid_format"}
                )
            )
            return Command(update={"messages": progress_messages})
        
        # Update state with the file
        files = state.get("files", {})
        files[filename] = file_content
        
        # Create summary
        summary = {
            "unique_authors": len(set(r.get("authors", "Unknown") for r in all_results if r.get("authors") != "Unknown")),
            "year_range": _get_year_range(all_results),
            "with_full_text": sum(1 for r in all_results if r.get("full_text_available", False)),
            "with_doi": sum(1 for r in all_results if r.get("doi"))
        }
        
        # Final success message
        success_message = f"✅ Successfully exported {len(all_results)} results to {filename}\n\n📊 Summary:\n" + \
                         f"• Unique authors: {summary['unique_authors']}\n" + \
                         f"• Year range: {summary['year_range']}\n" + \
                         f"• With full text: {summary['with_full_text']}\n" + \
                         f"• With DOI: {summary['with_doi']}\n\n" + \
                         f"📁 File: {filename} ({len(file_content):,} characters)"
        
        progress_messages.append(
            ToolMessage(
                content=success_message,
                tool_call_id=tool_call_id,
                additional_kwargs={
                    "success": True,
                    "filename": filename,
                    "total_exported": len(all_results),
                    "summary": summary
                }
            )
        )
        
        return Command(
            update={
                "files": files,
                "messages": progress_messages
            }
        )
        
    except Exception as e:
        error_message = f"❌ Fatal error during export: {str(e)}"
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=error_message,
                        tool_call_id=tool_call_id,
                        additional_kwargs={
                            "error": True,
                            "exception": str(e),
                            "query": query
                        }
                    )
                ]
            }
        )

async def _generate_csv_content(results: List[Dict[str, Any]]) -> str:
    """Generate CSV content as string"""
    if not results:
        return ""
    
    import io
    
    fieldnames = [
        "core_id", "title", "authors", "year", "doi", "abstract",
        "full_text_available", "data_provider", "document_type",
        "field_of_study", "citation_count", "download_url"
    ]
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for result in results:
        # Ensure all fields are present
        row = {field: result.get(field, "") for field in fieldnames}
        writer.writerow(row)
    
    return output.getvalue()

async def _generate_json_content(results: List[Dict[str, Any]]) -> str:
    """Generate JSON content as string"""
    import datetime
    
    data = {
        "exported_at": datetime.datetime.now().isoformat(),
        "total_results": len(results),
        "results": results
    }
    
    return json.dumps(data, indent=2, ensure_ascii=False)

async def _generate_markdown_content(results: List[Dict[str, Any]], query: str) -> str:
    """Generate Markdown content as string"""
    import datetime
    
    content = f"# CORE API Export Results\n\n"
    content += f"**Query:** {query}\n\n"
    content += f"**Total Results:** {len(results)}\n\n"
    content += f"**Exported:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    content += "---\n\n"
    
    for i, result in enumerate(results, 1):
        content += f"## {i}. {result.get('title', 'Untitled')}\n\n"
        
        if result.get('authors'):
            content += f"**Authors:** {result['authors']}\n\n"
        
        if result.get('year'):
            content += f"**Year:** {result['year']}\n\n"
        
        if result.get('doi'):
            content += f"**DOI:** {result['doi']}\n\n"
        
        if result.get('abstract'):
            abstract = result['abstract'][:500] + "..." if len(result['abstract']) > 500 else result['abstract']
            content += f"**Abstract:** {abstract}\n\n"
        
        if result.get('full_text_available'):
            content += "**Full Text:** Available\n\n"
        
        content += "---\n\n"
    
    return content

def _get_year_range(results: List[Dict[str, Any]]) -> Dict[str, Optional[int]]:
    """Get year range from results"""
    years = [r["year"] for r in results if r["year"]]
    if not years:
        return {"min": None, "max": None}
    
    return {"min": min(years), "max": max(years)}
