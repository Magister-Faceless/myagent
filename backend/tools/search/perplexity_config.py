"""
Perplexity AI routing policies, budgets, and configuration.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

# Model routing configuration
ROUTING_CONFIG = {
    "models": {
        "sonar": {
            "max_tokens": 1000,
            "max_latency": 2000,
            "cost_per_1k_tokens": 0.005,
            "use_case": "Quick queries and general Q&A"
        },
        "sonar-pro": {
            "max_tokens": 2000,
            "max_latency": 3000,
            "cost_per_1k_tokens": 0.01,
            "use_case": "Balanced cost/latency for general tasks"
        },
        "sonar-reasoning": {
            "max_tokens": 4000,
            "max_latency": 8000,
            "cost_per_1k_tokens": 0.02,
            "use_case": "Chain-of-thought analysis and reasoning"
        },
        "sonar-reasoning-pro": {
            "max_tokens": 6000,
            "max_latency": 12000,
            "cost_per_1k_tokens": 0.04,
            "use_case": "High-stakes decisions and complex analysis"
        },
        "sonar-deep-research": {
            "max_tokens": 16000,
            "max_latency": 45000,
            "cost_per_1k_tokens": 0.08,
            "use_case": "Multi-source synthesis and deep research"
        }
    },
    "filters": {
        "domain_allowlist": [
            "arxiv.org", "github.com", "docs.python.org", "stackoverflow.com",
            "medium.com", "towards-data-science.com", "nature.com", "science.org",
            "ieee.org", "acm.org", "openai.com", "anthropic.com", "google.com",
            "microsoft.com", "aws.amazon.com", "cloud.google.com"
        ],
        "domain_denylist": [
            "content-farm.com", "low-quality-aggregator.net", "clickbait-site.com",
            "spam-domain.org", "fake-news-site.net"
        ],
        "date_ranges": {
            "recent": "7d",
            "current": "30d", 
            "extended": "90d",
            "historical": "365d"
        },
        "source_quality_threshold": 0.7,
        "academic_domains": [
            "arxiv.org", "nature.com", "science.org", "ieee.org", "acm.org",
            "springer.com", "elsevier.com", "wiley.com", "jstor.org"
        ],
        "technical_domains": [
            "github.com", "docs.python.org", "stackoverflow.com", "developer.mozilla.org",
            "kubernetes.io", "docker.com", "tensorflow.org", "pytorch.org"
        ],
        "business_domains": [
            "bloomberg.com", "reuters.com", "wsj.com", "ft.com", "forbes.com",
            "techcrunch.com", "venturebeat.com", "crunchbase.com"
        ]
    },
    "budgets": {
        "normal": {
            "tokens": 2000,
            "cost": 0.10,
            "latency": 3000,
            "model": "sonar-pro"
        },
        "pro": {
            "tokens": 4000,
            "cost": 0.25,
            "latency": 8000,
            "model": "sonar-reasoning"
        },
        "deep": {
            "tokens": 16000,
            "cost": 1.00,
            "latency": 45000,
            "model": "sonar-deep-research"
        }
    }
}

# Task-to-model routing matrix
TASK_ROUTING = {
    "general_qa": {
        "primary": "sonar-pro",
        "fallback": "sonar",
        "description": "General questions and quick information lookup"
    },
    "reasoning": {
        "primary": "sonar-reasoning",
        "fallback": "sonar-pro", 
        "description": "Multi-step reasoning and analysis"
    },
    "critical_analysis": {
        "primary": "sonar-reasoning-pro",
        "fallback": "sonar-reasoning",
        "description": "High-stakes decisions and complex analysis"
    },
    "deep_research": {
        "primary": "sonar-deep-research",
        "fallback": "sonar-reasoning-pro",
        "description": "Multi-source synthesis and comprehensive research"
    },
    "academic_research": {
        "primary": "sonar-deep-research",
        "fallback": "sonar-reasoning-pro",
        "description": "Academic and scientific research"
    },
    "technical_research": {
        "primary": "sonar-reasoning-pro",
        "fallback": "sonar-reasoning",
        "description": "Technical documentation and API research"
    },
    "market_analysis": {
        "primary": "sonar-reasoning-pro",
        "fallback": "sonar-reasoning",
        "description": "Market trends and business intelligence"
    }
}

def get_model_for_task(task_type: str, fallback: bool = False) -> str:
    """Get the appropriate model for a given task type."""
    if task_type not in TASK_ROUTING:
        return "sonar-pro"  # Default model
    
    routing = TASK_ROUTING[task_type]
    return routing["fallback"] if fallback else routing["primary"]

def get_domain_filter_for_strategy(strategy: str) -> List[str]:
    """Get domain filters for specific research strategies."""
    filters = ROUTING_CONFIG["filters"]
    
    if strategy == "academic":
        return filters["academic_domains"]
    elif strategy == "technical":
        return filters["technical_domains"]
    elif strategy == "business" or strategy == "market":
        return filters["business_domains"]
    else:
        return filters["domain_allowlist"]

def calculate_quality_score(domain: str, position: int, total_results: int) -> float:
    """Calculate quality score for a source based on domain and search ranking."""
    base_score = 1.0 - (position / total_results)  # Higher for better ranking
    
    # Domain quality multipliers
    filters = ROUTING_CONFIG["filters"]
    if domain in filters["academic_domains"]:
        return min(1.0, base_score * 1.3)  # Academic sources get boost
    elif domain in filters["technical_domains"]:
        return min(1.0, base_score * 1.2)  # Technical sources get moderate boost
    elif domain in filters["domain_denylist"]:
        return max(0.1, base_score * 0.3)  # Penalize low-quality domains
    else:
        return base_score

def validate_model_config(model: str) -> Dict[str, Any]:
    """Validate and return model configuration."""
    if model not in ROUTING_CONFIG["models"]:
        model = "sonar-pro"  # Default fallback
    
    return ROUTING_CONFIG["models"][model]

def get_budget_config(budget_level: str) -> Dict[str, Any]:
    """Get budget configuration for a given level."""
    if budget_level not in ROUTING_CONFIG["budgets"]:
        budget_level = "normal"  # Default budget
    
    return ROUTING_CONFIG["budgets"][budget_level]

def should_use_domain_filter(query: str, strategy: Optional[str] = None) -> bool:
    """Determine if domain filtering should be applied based on query and strategy."""
    # Keywords that suggest need for high-quality sources
    quality_keywords = [
        "research", "study", "analysis", "academic", "scientific", "technical",
        "documentation", "official", "authoritative", "peer-reviewed"
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in quality_keywords) or strategy is not None

def get_date_filter_for_recency(recency: str) -> Optional[str]:
    """Convert recency string to appropriate date filter."""
    date_ranges = ROUTING_CONFIG["filters"]["date_ranges"]
    
    if recency in date_ranges:
        return date_ranges[recency]
    
    return None

# Export configuration for easy access
__all__ = [
    "ROUTING_CONFIG",
    "TASK_ROUTING", 
    "get_model_for_task",
    "get_domain_filter_for_strategy",
    "calculate_quality_score",
    "validate_model_config",
    "get_budget_config",
    "should_use_domain_filter",
    "get_date_filter_for_recency"
]
