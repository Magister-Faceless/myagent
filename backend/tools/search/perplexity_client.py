"""
Centralized Perplexity AI client with routing, authentication, and citation extraction.
"""

import os
import requests
import time
from typing import Dict, List, Any, Optional, Literal
from datetime import datetime
from urllib.parse import urlparse

from .perplexity_config import (
    validate_model_config,
    calculate_quality_score,
    get_model_for_task,
    ROUTING_CONFIG
)

class PerplexityClient:
    """Centralized client for Perplexity AI API with routing and citation extraction."""
    
    def __init__(self):
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.api_key = self._get_api_key()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _get_api_key(self) -> str:
        """Get Perplexity API key from environment variables."""
        api_key = os.environ.get("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable is required")
        return api_key
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            return urlparse(url).netloc.lower()
        except:
            return "unknown"
    
    def _process_citations(self, response_data: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Extract and process citations from Perplexity API response."""
        citations = []
        
        # Try to get citations from different possible locations in the response
        raw_citations = []
        
        # Method 1: Direct citations field
        if "citations" in response_data:
            raw_citations = response_data["citations"]
        
        # Method 2: Citations in message metadata
        elif "choices" in response_data and len(response_data["choices"]) > 0:
            message = response_data["choices"][0]["message"]
            if "citations" in message:
                raw_citations = message["citations"]
        
        # Method 3: Search results (if available)
        if not raw_citations and "search_results" in response_data:
            raw_citations = response_data["search_results"]
        
        # Process citations into standardized format
        for i, citation in enumerate(raw_citations[:10]):  # Limit to 10 citations
            try:
                processed_citation = {
                    "title": citation.get("title", "Untitled Source"),
                    "url": citation.get("url", ""),
                    "snippet": citation.get("snippet", citation.get("text", ""))[:200],  # Limit snippet length
                    "published_at": citation.get("date", citation.get("published_at")),
                    "source_type": self._classify_source_type(citation.get("url", "")),
                    "quality_score": calculate_quality_score(
                        self._extract_domain(citation.get("url", "")), 
                        i, 
                        len(raw_citations)
                    )
                }
                citations.append(processed_citation)
            except Exception as e:
                # Skip malformed citations but log the issue
                continue
        
        return citations
    
    def _classify_source_type(self, url: str) -> str:
        """Classify source type based on domain."""
        domain = self._extract_domain(url)
        
        academic_domains = ROUTING_CONFIG["filters"]["academic_domains"]
        technical_domains = ROUTING_CONFIG["filters"]["technical_domains"]
        
        if any(academic_domain in domain for academic_domain in academic_domains):
            return "primary"
        elif any(tech_domain in domain for tech_domain in technical_domains):
            return "secondary"
        else:
            return "tertiary"
    
    def _build_request_payload(
        self,
        query: str,
        model: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build the request payload for Perplexity API."""
        
        # Validate model configuration
        model_config = validate_model_config(model)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": query})
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.1),
            "max_tokens": kwargs.get("max_tokens", model_config["max_tokens"]),
            "enable_search_classifier": kwargs.get("enable_search_classifier", True),
            "disable_search": kwargs.get("disable_search", False)
        }
        
        # Add search filters
        search_filters = [
            "search_domain_filter", "search_after_date_filter", "search_before_date_filter",
            "last_updated_after_filter", "last_updated_before_filter", "search_recency_filter"
        ]
        
        for filter_name in search_filters:
            if filter_name in kwargs and kwargs[filter_name] is not None:
                payload[filter_name] = kwargs[filter_name]
        
        return payload
    
    def search(
        self,
        query: str,
        model: str = "sonar-pro",
        system_prompt: Optional[str] = None,
        task_type: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform a search using Perplexity AI with standardized response format.
        
        Args:
            query: The search query
            model: Perplexity model to use
            system_prompt: Optional system prompt for the model
            task_type: Task type for automatic model routing
            **kwargs: Additional parameters for the API
        
        Returns:
            Standardized response dictionary with citations
        """
        
        start_time = time.time()
        started_at = datetime.now().isoformat()
        
        # Auto-route model based on task type if provided
        if task_type and not model:
            model = get_model_for_task(task_type)
        
        try:
            payload = self._build_request_payload(query, model, system_prompt, **kwargs)
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            completed_at = datetime.now().isoformat()
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract the main answer
            answer = ""
            reasoning_summary = ""
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                answer = content
                
                # Try to extract reasoning summary from structured content
                if "## " in content or "### " in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if any(keyword in line.lower() for keyword in ["reasoning", "analysis", "methodology"]):
                            # Take next few lines as reasoning summary
                            reasoning_lines = lines[i:i+3]
                            reasoning_summary = ' '.join(reasoning_lines)[:200]
                            break
                
                if not reasoning_summary:
                    reasoning_summary = content[:200] + "..." if len(content) > 200 else content
            
            # Process citations
            citations = self._process_citations(result, query)
            
            # Extract usage information
            usage = result.get("usage", {})
            
            # Build standardized response
            standardized_response = {
                "status": "ok",
                "query": query,
                "model": model,
                "params": {
                    "date_range": kwargs.get("search_recency_filter"),
                    "domains": kwargs.get("search_domain_filter", []),
                    "depth": len(citations),
                    "temperature": kwargs.get("temperature", 0.1)
                },
                "answer": answer,
                "reasoning_summary": reasoning_summary,
                "citations": citations,
                "results": result.get("search_results", [])[:5],  # Limit raw results
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                    "cost_estimate": self._estimate_cost(usage.get("total_tokens", 0), model)
                },
                "timing": {
                    "started_at": started_at,
                    "completed_at": completed_at,
                    "latency_ms": latency_ms
                },
                "error": None,
                "debug": {
                    "model_config": validate_model_config(model),
                    "payload_size": len(str(payload)),
                    "response_size": len(str(result))
                }
            }
            
            return standardized_response
            
        except requests.exceptions.RequestException as e:
            return self._error_response(query, model, f"API request failed: {str(e)}", started_at)
        except Exception as e:
            return self._error_response(query, model, f"Unexpected error: {str(e)}", started_at)
    
    def _estimate_cost(self, total_tokens: int, model: str) -> Optional[float]:
        """Estimate cost based on token usage and model."""
        try:
            model_config = validate_model_config(model)
            cost_per_1k = model_config.get("cost_per_1k_tokens", 0.01)
            return (total_tokens / 1000) * cost_per_1k
        except:
            return None
    
    def _error_response(self, query: str, model: str, error_msg: str, started_at: str) -> Dict[str, Any]:
        """Generate standardized error response."""
        return {
            "status": "error",
            "query": query,
            "model": model,
            "params": {},
            "answer": "",
            "reasoning_summary": "",
            "citations": [],
            "results": [],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "cost_estimate": None
            },
            "timing": {
                "started_at": started_at,
                "completed_at": datetime.now().isoformat(),
                "latency_ms": 0
            },
            "error": error_msg,
            "debug": {}
        }
    
    def chat_completion(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Direct chat completion method for custom requests."""
        try:
            response = requests.post(self.api_url, headers=self.headers, json=request_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Chat completion failed: {str(e)}")
    
    def async_chat_completion(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit async chat completion request."""
        async_url = "https://api.perplexity.ai/async/chat/completions"
        try:
            payload = {"request": request_data}
            response = requests.post(async_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Async chat completion submission failed: {str(e)}")
    
    def poll_async_completion(self, request_id: str, max_wait_time: int = 600) -> Optional[Dict[str, Any]]:
        """Poll for async completion results with timeout."""
        url = f"https://api.perplexity.ai/async/chat/completions/{request_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                status = data.get('status')
                if status == 'COMPLETED':
                    return data
                elif status == 'FAILED':
                    return data
                
                # Wait before next poll
                time.sleep(2)
                
            except Exception as e:
                # Continue polling on temporary errors
                time.sleep(5)
                continue
        
        return None  # Timeout

# Global client instance
_client = None

def get_perplexity_client() -> PerplexityClient:
    """Get singleton Perplexity client instance."""
    global _client
    if _client is None:
        _client = PerplexityClient()
    return _client
