"""Perplexity API client implementation."""
import json
import requests
from typing import Optional, Iterator
from .exceptions import APIError, ConfigError
from .config import API_URL, get_api_key

def perform_search(query: str, api_key: Optional[str] = None, 
                  model: str = "llama-3.1-sonar-large-128k-online", 
                  stream: bool = False) -> Iterator[str]:
    """
    Perform a search using the Perplexity API.
    
    Args:
        query: The search query
        api_key: Optional API key (defaults to environment variable)
        model: Model to use (defaults to large model)
        stream: Whether to stream the response
    
    Yields:
        Response text chunks if streaming, or complete response
    
    Raises:
        APIError: If the API request fails
        ConfigError: If API key is missing
    """
    api_key = get_api_key(api_key)
    if not api_key:
        raise ConfigError("API key is required")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "model": model,
            "messages": [{"role": "user", "content": query}],
            "stream": stream
        },
        stream=stream
    )
    
    if response.status_code != 200:
        error_msg = f"API request failed with status code {response.status_code}"
        try:
            error_details = response.json()
            error_msg += f": {error_details.get('error', {}).get('message', '')}"
        except:
            pass
        raise APIError(error_msg)

    if stream:
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8').removeprefix('data: '))
                    if content := data.get('choices', [{}])[0].get('delta', {}).get('content'):
                        yield content
                except:
                    continue
    else:
        yield response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
