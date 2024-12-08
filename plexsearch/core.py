import os
import json
import signal
import requests
from typing import Optional, Dict, Any, Iterator
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from plexsearch import __version__
from plexsearch.update_checker import UpdateChecker



def _handle_stream_response(response, show_citations: bool = False) -> Iterator[str]:
    """Handle streaming response from Perplexity API.

    Args:
        response: The streaming response from the API
        show_citations: Whether to include citations in the output

    Yields:
        str: Content chunks from the response
    """
    content_buffer = []
    citations = []
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8').removeprefix('data: '))
                if content := (data.get('choices', [{}])[0]
                             .get('delta', {})
                             .get('content')):
                    content_buffer.append(content)
                    yield content
                if 'citations' in data:
                    citations = data['citations']
            except json.JSONDecodeError:
                continue

    # Only yield citations at the end if we have any and citations are enabled
    if citations and show_citations:
        citations_text = "\n\nReferences:\n" + "\n".join(
            f"[{i+1}] {url}" for i, url in enumerate(citations)
        )
        yield citations_text



# API Constants
PERPLEXITY_API_ENDPOINT = "https://api.perplexity.ai/chat/completions"


def _build_api_payload(
    query: str,
    model: str,
    stream: bool,
    show_citations: bool = False
) -> Dict[str, Any]:
    """Build the API request payload.
    
    Args:
        query: The search query
        model: Model to use
        stream: Whether to stream the response
        
    Returns:
        Dict containing the API request payload
    """
    system_message = (
        "You are a technical assistant focused on providing accurate, practical "
        "information. Follow these guidelines:\n"
        "1. Include code examples when relevant to explain concepts\n"
        "2. Include measurements and numbers when relevant\n"
        "3. Keep explanations concise and direct\n"
        "4. Focus on facts, technical details and real-world usage\n"
        "5. Show basic and advanced usage patterns when relevant\n"
        "6. Use tables or lists to organize information when appropriate\n"
        "7. If show_citations is True, add numbered citations at the bottom in "
        "[1], [2] format"
    )
    
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query}
        ],
        "stream": stream
    }

def perform_search(query: str, api_key: Optional[str] = None, model: str = "llama-3.1-sonar-large-128k-online", stream: bool = False, show_citations: bool = False) -> Iterator[str]:
    """
    Perform a search using the Perplexity API.
    
    Args:
        query (str): The search query
        api_key (str, optional): Perplexity API key. Defaults to env var PERPLEXITY_API_KEY
        model (str): Model to use. Defaults to large model.
        stream (bool): Whether to stream the response. Defaults to False.
    
    Returns:
        Iterator[str]: The search response text chunks if streaming, or full response
        
    Raises:
        ValueError: If API key is missing
        Exception: If the API request fails
    """
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
    
    payload = _build_api_payload(query, model, stream, show_citations)
    response = requests.post(
        PERPLEXITY_API_ENDPOINT,
        headers=headers,
        json=payload,
        stream=stream
    )
    
    if response.status_code != 200:
        error_msg = f"API request failed with status code {response.status_code}"
        if response.status_code == 401:
            error_msg = "Authentication failed. Please check your API key."
        elif response.status_code == 429:
            error_msg = "Rate limit exceeded. Please wait before making more requests."
        elif response.status_code == 500:
            error_msg = "Perplexity API server error. Please try again later."
        else:
            try:
                error_details = response.json()
                error_msg += f": {error_details.get('error', {}).get('message', '')}"
            except:
                pass
        raise Exception(error_msg)

    if stream:
        yield from _handle_stream_response(response, show_citations)
    else:
        response_data = response.json()
        content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        citations = response_data.get("citations", [])
        if citations and show_citations:
            content += "\n\nReferences:\n" + "\n".join(f"[{i+1}] {url}" for i, url in enumerate(citations))
        yield content

def main():
    """CLI entry point"""
    import argparse
    import sys
    parser = argparse.ArgumentParser(description="Perform searches using Perplexity API")
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument("query", nargs="+", help="The search query")
    parser.add_argument("--api-key", help="Perplexity API key")
    parser.add_argument("--model", default="llama-3.1-sonar-large-128k-online",
                       help="Model to use for search")
    parser.add_argument("--no-stream", action="store_true",
                       help="Disable streaming output and display the full response when finished")
    parser.add_argument("-c", "--citations", action="store_true",
                       help="Show numbered citations at the bottom of the response")
    
    args = parser.parse_args()
    query = " ".join(args.query)
    
    console = Console()
    
    # Set up signal handler for clean ctrl+c
    def handle_interrupt(signum, frame):
        console.print("\n[yellow]Search interrupted by user[/yellow]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_interrupt)
    
    try:
        # Check for updates
        checker = UpdateChecker("plexsearch", __version__)
        if latest_version := checker.check_and_notify():
            console.print(f"\n[yellow]New version {latest_version} available![/yellow]\n")
            response = input("Would you like to update now? (Y/n): ").strip().lower()
            if not response or response in ['y', 'yes']:
                try:
                    if checker.update_package():
                        console.print("[green]Successfully updated to the new version! The new version will be used on next execution.[/green]")
                    else:
                        console.print("[red]Update failed. Please try updating manually with: pip install --upgrade plexsearch[/red]")
                except Exception as e:
                    console.print(f"[red]Update failed: {str(e)}[/red]")
                console.print() # Add blank line after update messages

        # Disable streaming if --no-stream flag is set or if running in Aider
        no_stream = args.no_stream or os.environ.get("OR_APP_NAME") == "Aider"
        if no_stream:
            # For non-streaming mode, show spinner during search
            console.clear()
            with Live(Spinner("dots", text="Searching..."), refresh_per_second=10, transient=True):
                buffer = []
                for chunk in perform_search(query, api_key=args.api_key, model=args.model, stream=False, show_citations=args.citations):
                    buffer.append(chunk)
            
            # After search completes, just print the plain result
            content = "".join(buffer)
            print(content)
        else:
            # For streaming mode, update content live
            accumulated_text = ""
            console.clear()
            with Live("", refresh_per_second=10, transient=False) as live:
                for chunk in perform_search(query, api_key=args.api_key, model=args.model, stream=True, show_citations=args.citations):
                    accumulated_text += chunk
                    live.update(accumulated_text)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
