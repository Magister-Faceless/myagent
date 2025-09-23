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
        # Perplexity-specific settings
        "perplexity_default_model": "sonar-pro",
        "perplexity_max_retries": 3,
        "perplexity_timeout": 30,
        "perplexity_enable_caching": True,
        "perplexity_cache_ttl": 3600,  # 1 hour
    }


# API URLs
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

# Perplexity Configuration
PERPLEXITY_CONFIG = {
    "api_url": PERPLEXITY_API_URL,
    "default_model": "sonar-pro",
    "max_retries": 3,
    "timeout": 30,
    "rate_limit": {
        "requests_per_minute": 60,
        "tokens_per_minute": 100000
    },
    "citation_requirements": {
        "always_include": True,
        "max_citations": 10,
        "require_quality_score": True
    }
}
