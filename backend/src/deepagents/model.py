import sys
import os

# Add the backend directory to the path so we can import from models
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from models import get_default_model as get_configured_model
    
    def get_default_model():
        """Return the configured default model from the models module."""
        return get_configured_model()
        
except ImportError:
    # Fallback to original implementation if models module is not available
    from langchain_openai import ChatOpenAI
    
    def get_default_model():
        """Fallback implementation using OpenRouter with primary model."""
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        
        if openrouter_key:
            api_key = openrouter_key
        elif openai_key and base_url == "https://openrouter.ai/api/v1":
            api_key = openai_key
        else:
            raise ValueError(
                "OPENROUTER_API_KEY not found. Please set the OPENROUTER_API_KEY environment variable."
            )
        
        return ChatOpenAI(
            model="alibaba/tongyi-deepresearch-30b-a3b",
            temperature=0.1,
            max_tokens=None,
            timeout=30,
            max_retries=2,
            base_url=base_url,
            api_key=api_key,
        )
