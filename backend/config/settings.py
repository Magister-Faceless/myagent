"""
Application settings and configuration.
"""

import os
from typing import Dict, Any


def get_settings() -> Dict[str, Any]:
    """Get application settings from environment variables."""
    return {
        "tavily_api_key": os.environ.get("TAVILY_API_KEY"),
        "perplexity_api_key": os.environ.get("PERPLEXITY_API_KEY"),
        "recursion_limit": 1000,
        "default_max_results": 5,
        "default_temperature": 0.1,
    }


# API URLs
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
