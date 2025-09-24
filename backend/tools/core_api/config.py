"""
Configuration for CORE API tools
"""

import os
from typing import Dict, Any

# CORE API Configuration
CORE_API_CONFIG = {
    "api_key": os.getenv("CORE_API_KEY"),
    "base_url": os.getenv("CORE_API_BASE_URL", "https://api.core.ac.uk/v3"),
    "rate_limit": int(os.getenv("CORE_API_RATE_LIMIT", "100")),  # requests per minute
    "timeout": int(os.getenv("CORE_API_TIMEOUT", "30")),  # seconds
    "max_retries": 3,
    "backoff_factor": 2,
    "default_limit": 100,
    "max_limit": 10000
}

# Default headers for API requests
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Query templates for different research types
RESEARCH_QUERY_TEMPLATES = {
    "systematic_review": {
        "rct": 'documentType:"research article" AND (title:"randomized controlled trial" OR title:"RCT" OR abstract:"randomized")',
        "cohort": 'documentType:"research article" AND (title:"cohort study" OR abstract:"cohort" OR abstract:"longitudinal")',
        "case_control": 'documentType:"research article" AND (title:"case-control" OR abstract:"case-control" OR abstract:"case control")',
        "meta_analysis": 'documentType:"research article" AND (title:"meta-analysis" OR title:"systematic review" OR abstract:"meta-analysis")'
    },
    "field_filters": {
        "medicine": 'fieldOfStudy:"Medicine" OR fieldOfStudy:"Health Sciences"',
        "computer_science": 'fieldOfStudy:"Computer Science" OR fieldOfStudy:"Engineering"',
        "psychology": 'fieldOfStudy:"Psychology" OR fieldOfStudy:"Social Sciences"',
        "biology": 'fieldOfStudy:"Biology" OR fieldOfStudy:"Life Sciences"'
    }
}

# File output configurations
FILE_OUTPUT_CONFIG = {
    "csv_delimiter": ",",
    "max_file_size_mb": 100,
    "chunk_size": 1000,
    "output_formats": ["csv", "json", "md"]
}

def get_api_headers() -> Dict[str, str]:
    """Get headers for CORE API requests with authentication"""
    headers = DEFAULT_HEADERS.copy()
    if CORE_API_CONFIG["api_key"]:
        headers["Authorization"] = f"Bearer {CORE_API_CONFIG['api_key']}"
    return headers

def validate_config() -> bool:
    """Validate CORE API configuration"""
    if not CORE_API_CONFIG["api_key"]:
        raise ValueError("CORE_API_KEY environment variable is required")
    
    if not CORE_API_CONFIG["base_url"]:
        raise ValueError("CORE_API_BASE_URL is required")
    
    return True
