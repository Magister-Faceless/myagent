"""
Models module for managing AI provider configurations and model instances.

This module provides a centralized way to manage different AI model providers,
model configurations, and instantiation of chat models with proper fallbacks.
"""

from enum import Enum, auto
from typing import Dict, Optional, Type, Union, Any
import os
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel


class ModelProvider(str, Enum):
    """Supported AI model providers."""
    OPENROUTER = "openrouter"
    PERPLEXITY = "perplexity"


@dataclass
class ModelConfig:
    """Configuration for an AI model."""
    name: str
    provider: ModelProvider
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    timeout: int = 30
    max_retries: int = 5
    base_url: Optional[str] = None
    api_key_env_var: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = None


class ModelFactory:
    """Factory for creating chat model instances with proper configuration."""
    
    # Default model configurations
    DEFAULT_MODELS = {
        # Primary chat models (with fallback hierarchy) - Using more reliable models
        "primary": ModelConfig(
            name="x-ai/grok-4-fast",
            provider=ModelProvider.OPENROUTER,
            temperature=0.1,
            base_url="https://openrouter.ai/api/v1",
            api_key_env_var="OPENROUTER_API_KEY"
        ),
        "fallback-1": ModelConfig(
            name="anthropic/claude-3.5-sonnet",
            provider=ModelProvider.OPENROUTER,
            temperature=0.1,
            base_url="https://openrouter.ai/api/v1",
            api_key_env_var="OPENROUTER_API_KEY"
        ),
        "fallback-2": ModelConfig(
            name="x-ai/grok-4-fast",
            provider=ModelProvider.OPENROUTER,
            temperature=0.1,
            base_url="https://openrouter.ai/api/v1",
            api_key_env_var="OPENROUTER_API_KEY"
        ),
        
        # Vision models
        "vision-primary": ModelConfig(
            name="google/gemini-2.5-flash-preview-09-2025",
            provider=ModelProvider.OPENROUTER,
            temperature=0.1,
            base_url="https://openrouter.ai/api/v1",
            api_key_env_var="OPENROUTER_API_KEY"
        ),
        "vision-fallback": ModelConfig(
            name="anthropic/claude-3.5-sonnet",
            provider=ModelProvider.OPENROUTER,
            temperature=0.1,
            base_url="https://openrouter.ai/api/v1",
            api_key_env_var="OPENROUTER_API_KEY"
        ),
        
        # Deep research and analysis models
        "deep-research": ModelConfig(
            name="sonar-deep-research",
            provider=ModelProvider.PERPLEXITY,
            temperature=0.1,
            base_url="https://api.perplexity.ai",
            api_key_env_var="PERPLEXITY_API_KEY"
        ),
        
        # Perplexity models for web search and research
        "perplexity-sonar": ModelConfig(
            name="sonar-deep-research",
            provider=ModelProvider.PERPLEXITY,
            temperature=0.1,
            base_url="https://api.perplexity.ai",
            api_key_env_var="PERPLEXITY_API_KEY"
        )
    }
    
    @classmethod
    def get_model(
        cls, 
        model_name: Optional[str] = None,
        provider: Optional[Union[ModelProvider, str]] = None,
        **kwargs
    ) -> BaseChatModel:
        """
        Get a chat model instance with the specified configuration.
        
        Args:
            model_name: Name of the model to use. If None, uses primary model with fallbacks.
            provider: Provider to use. If None, uses OpenRouter.
            **kwargs: Additional parameters to override model config.
            
        Returns:
            Configured chat model instance.
            
        Raises:
            ValueError: If required configuration is missing or invalid.
        """
        # If no model specified, try primary with fallbacks
        if not model_name:
            return cls._get_model_with_fallback()
        
        # Get model config
        if model_name in cls.DEFAULT_MODELS:
            config = cls.DEFAULT_MODELS[model_name].__dict__.copy()
        else:
            # Create a new config with provided parameters
            config = {
                "name": model_name,
                "provider": provider or ModelProvider.OPENROUTER,
                "base_url": "https://openrouter.ai/api/v1",
                "api_key_env_var": "OPENROUTER_API_KEY",
                **kwargs
            }
        
        # Override with any provided kwargs
        config.update(kwargs)
        
        # Handle provider-specific configuration
        provider = ModelProvider(provider) if isinstance(provider, str) else config.get("provider", ModelProvider.OPENROUTER)
        
        if provider == ModelProvider.OPENROUTER:
            return cls._create_openrouter_model(config)
        elif provider == ModelProvider.PERPLEXITY:
            return cls._create_perplexity_model(config)
        else:
            return cls._create_openrouter_model(config)  # Default to OpenRouter
    
    @classmethod
    def _get_model_with_fallback(cls) -> BaseChatModel:
        """Get model with automatic fallback logic."""
        fallback_order = ["primary", "fallback-1", "fallback-2"]
        
        for model_key in fallback_order:
            try:
                config = cls.DEFAULT_MODELS[model_key]
                config_dict = {
                    "name": config.name,
                    "provider": config.provider,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                    "timeout": config.timeout,
                    "max_retries": config.max_retries,
                    "base_url": config.base_url,
                    "api_key_env_var": config.api_key_env_var,
                    "additional_params": config.additional_params or {}
                }
                return cls._create_openrouter_model(config_dict)
            except Exception as e:
                print(f"Failed to create model {model_key}: {e}")
                continue
        
        raise ValueError("All fallback models failed to initialize")
    
    @classmethod
    def _create_openrouter_model(cls, config: Dict[str, Any]) -> ChatOpenAI:
        """Create a model using OpenRouter."""
        api_key = os.getenv(config.get("api_key_env_var", "OPENROUTER_API_KEY"))
        if not api_key:
            raise ValueError(
                "OpenRouter API key not found. Please set the OPENROUTER_API_KEY environment variable."
            )
            
        # Set OpenRouter specific headers
        headers = {
            "HTTP-Referer": "https://github.com/myagents/backend",
            "X-Title": "MyAgents"
        }
        
        additional_params = config.get("additional_params") or {}
        
        return ChatOpenAI(
            model=config["name"],
            temperature=config.get("temperature", 0.1),
            max_tokens=config.get("max_tokens"),
            timeout=config.get("timeout", 30),
            max_retries=config.get("max_retries", 2),
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers=headers,
            **additional_params
        )
    
    @classmethod
    def _create_perplexity_model(cls, config: Dict[str, Any]) -> ChatOpenAI:
        """Create a model using Perplexity API."""
        api_key = os.getenv(config.get("api_key_env_var", "PERPLEXITY_API_KEY"))
        if not api_key:
            raise ValueError(
                "Perplexity API key not found. Please set the PERPLEXITY_API_KEY environment variable."
            )
            
        additional_params = config.get("additional_params") or {}
        
        return ChatOpenAI(
            model=config["name"],
            temperature=config.get("temperature", 0.1),
            max_tokens=config.get("max_tokens"),
            timeout=config.get("timeout", 30),
            max_retries=config.get("max_retries", 2),
            base_url="https://api.perplexity.ai",
            api_key=api_key,
            **additional_params
        )


def get_default_model() -> BaseChatModel:
    """
    Get the default chat model with automatic fallback.
    
    Uses the primary model (google/gemini-2.5-flash-preview-09-2025) with automatic
    fallback to anthropic/claude-3.5-sonnet and then x-ai/grok-4-fast.
    All models use OpenRouter as the provider.
    
    Returns:
        Configured chat model instance.
        
    Raises:
        ValueError: If no valid API key is found or all models fail.
    """
    if not os.getenv("OPENROUTER_API_KEY"):
        raise ValueError(
            "OPENROUTER_API_KEY not found. Please set the OPENROUTER_API_KEY environment variable."
        )
    
    # Build primary model with runtime fallbacks so transient errors (e.g., 429 rate limits)
    # automatically trigger backups without failing the entire run.
    primary_model = ModelFactory.get_model("primary")
    fallback_models = []

    for fallback_key in ["fallback-1", "fallback-2"]:
        try:
            fallback_models.append(ModelFactory.get_model(fallback_key))
        except Exception as exc:  # noqa: BLE001 - log and continue building fallbacks
            print(f"Failed to initialize fallback model '{fallback_key}': {exc}")
            continue

    if fallback_models:
        return primary_model.with_fallbacks(fallback_models)

    return primary_model


def get_vision_model() -> BaseChatModel:
    """Get a vision-capable model."""
    return ModelFactory.get_model("vision-primary")


def get_deep_research_model() -> BaseChatModel:
    """Get a model optimized for deep research and analysis."""
    return ModelFactory.get_model("deep-research")


def get_perplexity_model() -> BaseChatModel:
    """Get a Perplexity model for web search and research."""
    return ModelFactory.get_model("perplexity-sonar")
