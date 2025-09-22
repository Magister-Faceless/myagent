from langchain_openai import ChatOpenAI
import os


def get_default_model():
     """Return the default chat model with sensible provider selection.

     Provider selection rules:
     1) If OPENAI_BASE_URL is explicitly set, use it with OPENAI_API_KEY.
     2) Else, if OPENROUTER_API_KEY is set, use OpenRouter base URL and that key.
     3) Else, if OPENAI_API_KEY is set, use the OpenAI base URL and that key.
     4) Else, raise a clear error instructing how to configure keys.

     Default Model:
     - "alibaba/tongyi-deepresearch-30b-a3b" (available on OpenRouter). If using OpenAI base URL,
       ensure the selected model exists there or override via subagent model config.
     """
     # Explicit override first
     explicit_base_url = os.getenv("OPENAI_BASE_URL")
     openrouter_key = os.getenv("OPENROUTER_API_KEY")
     openai_key = os.getenv("OPENAI_API_KEY")

     if explicit_base_url:
         # Assume the explicit base URL matches the provided OPENAI_API_KEY
         api_key = openai_key
         base_url = explicit_base_url
     elif openrouter_key:
         api_key = openrouter_key
         base_url = "https://openrouter.ai/api/v1"
     elif openai_key:
         api_key = openai_key
         base_url = "https://api.openai.com/v1"
     else:
         raise ValueError(
             "No API key configured. Please set one of: OPENROUTER_API_KEY (preferred), "
             "or OPENAI_API_KEY. Optionally set OPENAI_BASE_URL to override the endpoint."
         )

     return ChatOpenAI(
         model="x-ai/grok-4-fast:free",
         temperature=0,
         max_tokens=None,
         timeout=None,
         max_retries=2,
         base_url=base_url,
         api_key=api_key,
     )
