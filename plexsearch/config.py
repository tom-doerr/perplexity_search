"""Configuration handling for plexsearch."""
from typing import Optional
import os
from .exceptions import ConfigError


DEFAULT_MODEL = "llama-3.1-sonar-large-128k-online"
API_URL = "https://api.perplexity.ai/chat/completions"


def get_api_key(api_key: Optional[str] = None) -> str:
    """Get API key from argument or environment."""
    if api_key is None:
        api_key = os.environ.get("PERPLEXITY_API_KEY")
        if not api_key:
            raise ConfigError(
                "API key must be provided either directly or via PERPLEXITY_API_KEY environment variable"
            )
    return api_key
