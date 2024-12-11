import os
import sys
import json
import signal
import requests
from typing import Optional, Dict, Any, Iterator, List
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from plexsearch import __version__
from plexsearch.update_checker import UpdateChecker


console = Console()


def get_terminal_size():
    """Get the dimensions of the terminal."""
    try:
        import shutil
        height, width = shutil.get_terminal_size()
        return height, width
    except Exception:
        # Fallback to default dimensions if shutil fails
        return 24, 80

def clear_new_area():
    """Clear screen while preserving scrollback buffer."""
    console.print("[cyan]Clearing screen...[/cyan]")
    # Print newlines to push content up
    height, _ = get_terminal_size()
    console.print("\n" * height)
    # Use Rich's clear which preserves scrollback
    console.clear()

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

def perform_search(query: str, api_key: Optional[str] = None, model: str = "llama-3.1-sonar-large-128k-online", stream: bool = False, show_citations: bool = False, context: Optional[List[Dict[str, str]]] = None) -> Iterator[str]:
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
    if context:
        payload["messages"] = context
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


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Perform searches using Perplexity API")
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument("query", nargs="*", help="The search query")
    parser.add_argument("--api-key", help="Perplexity API key")
    parser.add_argument("--model", default="llama-3.1-sonar-large-128k-online",
                       help="Model to use for search")
    parser.add_argument("--no-stream", action="store_true",
                       help="Disable streaming output")
    parser.add_argument("-c", "--citations", action="store_true",
                       help="Show numbered citations")
    return parser.parse_args()

def handle_no_stream_search(query: str, args, payload: dict) -> str:
    """Handle non-streaming search mode."""
    console.print("[cyan]About to clear screen in no_stream mode...[/cyan]")
    clear_new_area()
    spinner_text = "Searching..."
    buffer = []
    
    with Live(Spinner("dots", text=spinner_text), refresh_per_second=10, transient=True):
        for chunk in perform_search(query=query, api_key=args.api_key,
                                  model=args.model, stream=False,
                                  show_citations=args.citations,
                                  context=payload.get("messages")):
            buffer.append(chunk)
    
    content = "".join(buffer)
    console.print(f"Perplexity: {content}")
    return content

def handle_streaming_search(query: str, args, payload: dict) -> str:
    """Handle streaming search mode."""
    accumulated_text = ""
    with Live("", refresh_per_second=10, transient=False) as live:
        for chunk in perform_search(query=query, api_key=args.api_key,
                                  model=args.model, stream=True,
                                  show_citations=args.citations,
                                  context=payload.get("messages")):
            accumulated_text += chunk
            live.update(f"Perplexity: {accumulated_text}")
    return accumulated_text

def handle_search(query: str, args, context=None) -> str:
    """Handle a single search query execution."""
    no_stream = args.no_stream or os.environ.get("OR_APP_NAME") == "Aider"
    payload = _build_api_payload(query=query, model=args.model,
                               stream=not no_stream, show_citations=args.citations)
    if context:
        payload["messages"] = context

    if no_stream:
        return handle_no_stream_search(query, args, payload)
    else:
        return handle_streaming_search(query, args, payload)

def handle_interactive_mode(args, context=None):
    """Handle interactive mode search session."""
    if context is None:
        context = []
    console.print("[green]Entering interactive mode. Type your queries below. Type 'exit' to quit.[/green]")
    
    while True:
        user_input = input("\n> ")
        if user_input.lower() == "exit":
            console.print("[yellow]Exiting interactive mode.[/yellow]")
            break

        clear_new_area()
        context.append({"role": "user", "content": user_input})
        try:
            content = handle_search(user_input, args, context)
            context.append({"role": "assistant", "content": content})
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            print(f"[red]Error:[/red] {e}", file=sys.stderr)

def setup_signal_handler():
    """Set up interrupt signal handler."""
    def handle_interrupt(signum, frame):
        console.print("\n[yellow]Search interrupted by user[/yellow]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_interrupt)

def main():
    """CLI entry point"""
    try:
        args = parse_arguments()
        setup_signal_handler()
    
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
                console.print()

        query = " ".join(args.query) if args.query else None
        
        if query is None:
            handle_interactive_mode(args)
        else:
            clear_new_area()
            handle_search(query, args)
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        print(f"[red]Error:[/red] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
