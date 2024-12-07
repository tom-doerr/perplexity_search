import os
import json
import signal
import requests
from typing import Optional, Dict, Any, Iterator
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner

def perform_search(query: str, api_key: Optional[str] = None, model: str = "llama-3.1-sonar-large-128k-online", stream: bool = False) -> Iterator[str]:
    """
    Perform a search using the Perplexity API with improved error handling and streaming display.
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
            if isinstance(error_details, dict):
                error_msg += f": {error_details.get('error', {}).get('message', '')}"
            else:
                error_msg += f": {response.text}"
        except:
            if response.text:
                error_msg += f": {response.text}"
        raise Exception(error_msg)

    if stream:
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8').removeprefix('data: '))
                    if content := data.get('choices', [{}])[0].get('delta', {}).get('content'):
                        # Buffer and center headlines in streamed output
                        if content.startswith('# ') or content.startswith('## '):
                            # Start buffering heading
                            heading_buffer = content
                            for line in response.iter_lines():
                                if not line:
                                    break
                                try:
                                    next_data = json.loads(line.decode('utf-8').removeprefix('data: '))
                                    next_content = next_data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                                    if next_content.startswith('\n') or not next_content:
                                        break
                                    heading_buffer += next_content
                                except (json.JSONDecodeError, AttributeError):
                                    break
                            
                            # Now center the complete heading
                            marker = '# ' if heading_buffer.startswith('# ') else '## '
                            text = heading_buffer.lstrip('#').lstrip()
                            terminal_width = os.get_terminal_size().columns
                            padding = (terminal_width - len(text)) // 2
                            content = ' ' * padding + marker + text
                        yield content
                except:
                    continue
    else:
        yield response.json().get("choices", [{}])[0].get("message", {}).get("content", "")

def main():
    """CLI entry point"""
    import argparse
    import sys
    
    from plexsearch import __version__
    parser = argparse.ArgumentParser(description="Perform searches using Perplexity API")
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument("query", nargs="+", help="The search query")
    parser.add_argument("--api-key", help="Perplexity API key")
    parser.add_argument("--model", default="llama-3.1-sonar-large-128k-online",
                       help="Model to use for search")
    parser.add_argument("--no-stream", action="store_true",
                       help="Disable streaming output")
    
    args = parser.parse_args()
    query = " ".join(args.query)
    
    console = Console()
    
    # Set up signal handler for clean ctrl+c
    def handle_interrupt(signum, frame):
        console.print("\n[yellow]Search interrupted by user[/yellow]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_interrupt)
    
    try:
        buffer = []
        accumulated_text = ""
        with Live("", refresh_per_second=10) as live:
            live.update(Spinner("dots", text="Searching..."))
            for chunk in perform_search(query, api_key=args.api_key, model=args.model, stream=not args.no_stream):
                if args.no_stream:
                    buffer.append(chunk)
                else:
                    accumulated_text += chunk
                    live.update(accumulated_text)
        
        if args.no_stream:
            content = "".join(buffer)
            # Make headings bold by adding ** around them
            # Add formatting
            lines = content.split("\n")
            for i, line in enumerate(lines):
                # Bold headings with indentation and decorative elements
                if line.startswith("## "):
                    lines[i] = "\n[bold cyan]┌──────────────────────┐[/bold cyan]\n**## " + line[3:] + "**\n[bold cyan]└──────────────────────┘[/bold cyan]"
                elif line.startswith("### "):
                    lines[i] = "\n   [cyan]▶[/cyan] **### " + line[4:] + "**"
                # Add bullet points with colored indentation
                elif line.startswith("- "):
                    lines[i] = "   [cyan]•[/cyan] " + line[2:]
                # Highlight key terms with different style
                elif "`" in line:
                    lines[i] = line.replace("`", "[bold magenta]").replace("`", "[/bold magenta]")
                # Add decorative separator for main sections
                elif line.startswith("# "):
                    lines[i] = "\n[bold cyan]════════════════════════════════[/bold cyan]\n**# " + line[2:] + "**\n[bold cyan]════════════════════════════════[/bold cyan]\n"
            
            content = "\n".join(lines)
            md = Markdown(content)
            console.print(md)
            
    except Exception as e:
        error_console = Console(stderr=True)
        error_console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
