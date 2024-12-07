import os
import requests

from typing import Optional, Dict, Any

def perform_search(query: str, api_key: Optional[str] = None, model: str = "llama-3.1-sonar-large-128k-online") -> str:
    """
    Perform a search using the Perplexity API.
    
    Args:
        query (str): The search query
        api_key (str, optional): Perplexity API key. Defaults to env var PERPLEXITY_API_KEY
        model (str, optional): Model to use. Defaults to large model.
    
    Returns:
        str: The search response text
    
    Raises:
        Exception: If the API request fails
    """
    if api_key is None:
        api_key = os.environ.get("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError("API key must be provided either directly or via PERPLEXITY_API_KEY environment variable")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "query": query,
        "model": model
    }
    
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers=headers,
        json={
            "model": model,
            "messages": [{"role": "user", "content": query}]
        }
    )
    
    if response.status_code != 200:
        error_msg = f"API request failed with status code {response.status_code}"
        try:
            error_details = response.json()
            error_msg += f": {error_details.get('error', {}).get('message', '')}"
        except:
            pass
        raise Exception(error_msg)
        
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")

def main():
    """CLI entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="Perform searches using Perplexity API")
    parser.add_argument("query", help="The search query")
    parser.add_argument("--api-key", help="Perplexity API key")
    parser.add_argument("--model", default="llama-3.1-sonar-large-128k-online",
                       help="Model to use for search")
    
    args = parser.parse_args()
    result = perform_search(args.query, api_key=args.api_key, model=args.model)
    print(result)

if __name__ == "__main__":
    main()
