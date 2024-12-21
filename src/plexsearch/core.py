#!/usr/bin/env python3

import os
import json
import argparse
import requests
from typing import Dict, List, Optional
from rich.console import Console

LLAMA_MODELS = {
    "small": "llama-3.1-sonar-small-128k-online",
    "large": "llama-3.1-sonar-large-128k-online",
    "huge": "llama-3.1-sonar-huge-128k-online"
}

def create_payload(query: str, 
                  model: str = LLAMA_MODELS["large"],
                  temperature: float = 0.2) -> Dict:
    """Create the payload for the Perplexity API request."""
    return {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a technical assistant focused on providing precise facts, code examples, and numerical data. Format responses with markdown. Include specific numbers, benchmarks, and code snippets where relevant. Avoid conversational language - be direct and technical."
            },
            {
                "role": "user", 
                "content": query
            }
        ],
        "temperature": temperature,
        "top_p": 0.9,
        "search_domain_filter": ["perplexity.ai"],
        "return_images": False,
        "return_related_questions": False,
        "search_recency_filter": "month",
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }

def perform_search(query: str, api_key: Optional[str] = None, model: Optional[str] = None) -> Dict:
    if not api_key:
        api_key = os.getenv('PERPLEXITY_API_KEY')
        if not api_key:
            raise ValueError("No API key provided. Set PERPLEXITY_API_KEY environment variable or pass key directly.")

    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = create_payload(query, model=model)
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    return response.json()

def main():
    parser = argparse.ArgumentParser(description='Search using Perplexity API')
    parser.add_argument('query', nargs='+', help='The search query')
    parser.add_argument('--model', choices=list(LLAMA_MODELS.keys()), default='large',
                      help='Model to use (default: large)')
    parser.add_argument('--api-key', help='Perplexity API key (optional, can use PERPLEXITY_API_KEY env var)')
    args = parser.parse_args()
    console = Console()

    try:
        query: str = ' '.join(args.query)
        model: str = LLAMA_MODELS[args.model]
        result: Dict = perform_search(query, args.api_key, model)
        content: str = result['choices'][0]['message']['content']
        console.print(content)
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()
