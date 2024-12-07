"""Command-line interface for plexsearch."""
import sys
import signal
import argparse
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.markdown import Markdown
from .client import perform_search
from .formatter import format_markdown
from .exceptions import PlexSearchError

def main() -> None:
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Perform searches using Perplexity API")
    try:
        from . import __version__
        version_str = __version__
    except ImportError:
        version_str = "unknown"
    parser.add_argument('--version', action='version', version=f'%(prog)s {version_str}')
    parser.add_argument("query", nargs="+", help="The search query")
    parser.add_argument("--api-key", help="Perplexity API key")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--model", default="llama-3.1-sonar-large-128k-online",
                       help="Model to use for search")
    parser.add_argument("--no-stream", action="store_true",
                       help="Disable streaming output")
    
    args = parser.parse_args()
    query = " ".join(args.query)
    
    console = Console()
    
    def handle_interrupt(signum: int, frame: any) -> None:
        console.print("\n[yellow]Search interrupted by user[/yellow]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_interrupt)
    
    try:
        buffer = []
        accumulated_text = ""
        with Live("", refresh_per_second=10) as live:
            live.update(Spinner("dots", text="Searching..."))
            for chunk in perform_search(query, api_key=args.api_key, 
                                     model=args.model, stream=not args.no_stream):
                if args.no_stream:
                    buffer.append(chunk)
                else:
                    accumulated_text += chunk
                    live.update(accumulated_text)
        
        if args.no_stream:
            content = "".join(buffer)
            formatted_content = format_markdown(content)
            console.print(Markdown(formatted_content))
            
    except PlexSearchError as e:
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}", file=sys.stderr)
        sys.exit(1)
