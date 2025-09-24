"""
Utility functions for CORE API tools
"""

import re
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def validate_doi(doi: str) -> bool:
    """
    Validate DOI format
    
    Args:
        doi: DOI string to validate
        
    Returns:
        bool: True if valid DOI format
    """
    # DOI regex pattern
    doi_pattern = r'^10\.\d{4,}\/[^\s]+$'
    return bool(re.match(doi_pattern, doi.strip()))

def format_authors(authors: List[Dict[str, Any]]) -> str:
    """
    Format author list for display
    
    Args:
        authors: List of author dictionaries
        
    Returns:
        str: Formatted author string
    """
    if not authors:
        return "Unknown"
    
    author_names = []
    for author in authors[:5]:  # Limit to first 5 authors
        if isinstance(author, dict):
            name = author.get('name', '')
        else:
            name = str(author)
        
        if name:
            author_names.append(name)
    
    if len(authors) > 5:
        author_names.append("et al.")
    
    return "; ".join(author_names)

def clean_text(text: str, max_length: int = 300) -> str:
    """
    Clean and truncate text for display
    
    Args:
        text: Text to clean
        max_length: Maximum length
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and newlines
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    # Truncate if too long
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length-3] + "..."
    
    return cleaned

def extract_year(date_str: str) -> Optional[int]:
    """
    Extract year from date string
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        int: Extracted year or None
    """
    if not date_str:
        return None
    
    # Try to extract 4-digit year
    year_match = re.search(r'\b(19|20)\d{2}\b', str(date_str))
    if year_match:
        return int(year_match.group())
    
    return None

async def handle_api_error(response: aiohttp.ClientResponse) -> Dict[str, Any]:
    """
    Handle API error responses
    
    Args:
        response: HTTP response object
        
    Returns:
        dict: Error information
    """
    try:
        error_data = await response.json()
    except:
        error_data = {"message": "Unknown error"}
    
    error_info = {
        "status_code": response.status,
        "error": error_data.get("message", "API request failed"),
        "details": error_data
    }
    
    logger.error(f"CORE API Error: {error_info}")
    return error_info

async def make_api_request(
    session: aiohttp.ClientSession,
    url: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Make API request with error handling and retries
    
    Args:
        session: HTTP session
        url: Request URL
        method: HTTP method
        params: URL parameters
        json_data: JSON payload
        headers: Request headers
        timeout: Request timeout
        
    Returns:
        dict: API response data
    """
    from .config import CORE_API_CONFIG
    
    max_retries = CORE_API_CONFIG["max_retries"]
    backoff_factor = CORE_API_CONFIG["backoff_factor"]
    
    for attempt in range(max_retries):
        try:
            async with session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:  # Rate limit
                    wait_time = (backoff_factor ** attempt) * 60
                    logger.warning(f"Rate limited, waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    error_info = await handle_api_error(response)
                    if attempt == max_retries - 1:
                        raise Exception(f"API request failed: {error_info['error']}")
                    
        except asyncio.TimeoutError:
            if attempt == max_retries - 1:
                raise Exception(f"Request timeout after {timeout}s")
            await asyncio.sleep(backoff_factor ** attempt)
        
        except Exception as e:
            if attempt == max_retries - 1:
                raise Exception(f"Request failed: {str(e)}")
            await asyncio.sleep(backoff_factor ** attempt)
    
    raise Exception("Max retries exceeded")

def build_query_string(
    base_query: str,
    filters: Optional[Dict[str, Any]] = None,
    date_range: Optional[Dict[str, str]] = None,
    require_full_text: bool = False
) -> str:
    """
    Build CORE API query string with filters
    
    Args:
        base_query: Base search query
        filters: Additional filters
        date_range: Date range filter
        require_full_text: Whether to require full text
        
    Returns:
        str: Complete query string
    """
    query_parts = [base_query] if base_query else []
    
    # Add full text requirement
    if require_full_text:
        query_parts.append("_exists_:fullText")
    
    # Add date range
    if date_range:
        start_year = date_range.get("start_year")
        end_year = date_range.get("end_year")
        
        if start_year:
            query_parts.append(f"yearPublished>={start_year}")
        if end_year:
            query_parts.append(f"yearPublished<={end_year}")
    
    # Add other filters
    if filters:
        for field, value in filters.items():
            if value:
                if isinstance(value, list):
                    # Multiple values with OR
                    or_values = " OR ".join([f'{field}:"{v}"' for v in value])
                    query_parts.append(f"({or_values})")
                else:
                    query_parts.append(f'{field}:"{value}"')
    
    return " AND ".join(query_parts)

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def generate_filename(
    prefix: str,
    query: str,
    extension: str = "csv",
    max_length: int = 100
) -> str:
    """
    Generate safe filename for output files
    
    Args:
        prefix: Filename prefix
        query: Search query for filename
        extension: File extension
        max_length: Maximum filename length
        
    Returns:
        str: Safe filename
    """
    # Clean query for filename
    safe_query = re.sub(r'[^\w\s-]', '', query)
    safe_query = re.sub(r'[-\s]+', '_', safe_query)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Build filename
    filename = f"{prefix}_{safe_query}_{timestamp}.{extension}"
    
    # Truncate if too long
    if len(filename) > max_length:
        max_query_len = max_length - len(prefix) - len(timestamp) - len(extension) - 10
        safe_query = safe_query[:max_query_len]
        filename = f"{prefix}_{safe_query}_{timestamp}.{extension}"
    
    return filename
