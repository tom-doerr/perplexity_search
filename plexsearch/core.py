import os
import json
import requests
from typing import Optional, Dict, Any, Iterator
from rich.console import Console
from rich.markdown import Markdown

def perform_search(query: str, api_key: Optional[str] = None, model: str = "llama-3.1-sonar-large-128k-online", stream: bool = False) -> Iterator[str]:
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
        raise Exception(error_msg)

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

def main():
    """CLI entry point"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Perform searches using Perplexity API")
    parser.add_argument("query", nargs="+", help="The search query")
    parser.add_argument("--api-key", help="Perplexity API key")
    parser.add_argument("--model", default="llama-3.1-sonar-large-128k-online",
                       help="Model to use for search")
    parser.add_argument("--no-stream", action="store_true",
                       help="Disable streaming output")
    
    args = parser.parse_args()
    query = " ".join(args.query)
    
    console = Console()
    
    try:
        buffer = []
        for chunk in perform_search(query, api_key=args.api_key, model=args.model, stream=not args.no_stream):
            if args.no_stream:
                buffer.append(chunk)
            else:
                console.print(chunk, end="")
                sys.stdout.flush()
        
        if args.no_stream:
            # Print full response with markdown formatting and bold headings
            content = "".join(buffer)
            # Make headings bold by adding ** around them
            # Add formatting
            lines = content.split("\n")
            for i, line in enumerate(lines):
                # Bold headings with indentation for subheadings
                if line.startswith("## "):
                    lines[i] = "\n**## " + line[3:] + "**"
                elif line.startswith("### "):
                    lines[i] = "\n   **### " + line[4:] + "**"
                # Add bullet points indentation
                elif line.startswith("- "):
                    lines[i] = "   • " + line[2:]
                # Highlight key terms
                elif "`" in line:
                    lines[i] = line.replace("`", "[bold]").replace("`", "[/bold]")
                # Add separator between main sections
                elif line.startswith("# "):
                    lines[i] = "\n─────────────────────────\n**# " + line[2:] + "**\n"
            
            content = "\n".join(lines)
            md = Markdown(content)
            console.print(md)
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
