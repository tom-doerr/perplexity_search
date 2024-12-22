import os
import sys
import signal
import json
from typing import Optional, List, Dict, Iterator
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from plexsearch import __version__
from plexsearch.update_checker import UpdateChecker
from plexsearch.api import PerplexityAPI
from plexsearch.config import Config
from plexsearch.context import ConversationContext
    


console = Console()


def get_terminal_size() -> tuple[int, int]:
    """Get the dimensions of the terminal."""
    try:
        import shutil
        height, width = shutil.get_terminal_size()
        return height, width
    except Exception:
        # Fallback to default dimensions if shutil fails
        return 24, 80

def clear_new_area() -> None:
    """Clear screen while preserving scrollback buffer."""
    console.print("[cyan]Clearing screen...[/cyan]")
    # Print newlines to push content up
    height, _ = get_terminal_size()
    console.print("\n" * height)
    # Use Rich's clear which preserves scrollback
    console.clear()

def handle_no_stream_search(query: str, args, context: Optional[List[Dict[str, str]]] = None) -> str:    
    """Handle non-streaming search mode."""
    console.print("[cyan]About to clear screen in no_stream mode...[/cyan]")
    clear_new_area()
    spinner_text = "Searching..."
    
    api = PerplexityAPI(args.api_key)
    try:
        with Live(Spinner("dots", text=spinner_text), refresh_per_second=10, transient=True):
            response = api.perform_search(query=query,
                                        model=args.model,
                                        stream=False,
                                        show_citations=args.citations,
                                        context=context)
            content = "".join(response)
        
        console.print(f"Perplexity: {content}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return ""
    return content

def handle_streaming_search(query: str, args, context: Optional[List[Dict[str, str]]] = None) -> str:
    """Handle streaming search mode."""
    accumulated_text = ""
    api = PerplexityAPI(args.api_key)
    try:
        with Live("", refresh_per_second=10, transient=False) as live:
            for chunk in api.perform_search(query=query,
                                          model=args.model,
                                          stream=True,
                                          show_citations=args.citations,
                                          context=context):
                accumulated_text += chunk
                live.update(f"Perplexity: {accumulated_text}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return ""
    return accumulated_text

def log_conversation(log_file: str, new_messages: List[Dict[str, str]]) -> None:
    """Log only the new messages to the file."""
    try:
        with open(log_file, "a") as f:
            for message in new_messages:
                json.dump(message, f)
                f.write("\n")
    except Exception as e:
        console.print(f"[red]Error writing to log file: {e}[/red]")

def handle_search(query: str, args, context: Optional[List[Dict[str, str]]] = None) -> str:
    """Handle a single search query execution."""
    no_stream = args.no_stream or os.environ.get("OR_APP_NAME") == "Aider"
    
    if context is None:
        context = []
        
    if not context or context[0].get('role') != 'system':
        context.insert(0, {
            "role": "system", 
            "content": "You are a technical assistant focused on providing accurate, practical information..."
        })
    
    try:
        if no_stream:
            return handle_no_stream_search(query, args, context)
        else:
            return handle_streaming_search(query, args, context)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return ""

def handle_interactive_mode(args, log_file, context: Optional[List[Dict[str, str]]] = None):
    """Handle interactive mode, with optional markdown file output."""
    if context is None:
        context = []
    console.print("[green]Entering interactive mode. Type your queries below. Type 'exit' to quit or press Ctrl-D to exit.[/green]")
    
    while True:
        try:
            user_input = console.input("\n[cyan]> [/cyan]")
        except EOFError:
            console.print("\n[yellow]Exiting interactive mode.[/yellow]")
            break

        if user_input.strip() == "":
            console.print("[yellow]Please enter a query or type 'exit' to quit.[/yellow]")
            continue
        if user_input.lower() == "exit":
            console.print("[yellow]Exiting interactive mode.[/yellow]")
            break

        clear_new_area()
        
        try:
            content = handle_search(user_input, args, context)
            new_user_message = {"role": "user", "content": user_input}
            new_assistant_message = {"role": "assistant", "content": content}
            log_conversation(log_file, [new_user_message, new_assistant_message])

            if args.markdown_file:
                _write_to_markdown_file(args.markdown_file, [new_user_message, new_assistant_message])

            context.append(new_user_message)
            context.append(new_assistant_message)
        except Exception as e:
            error_msg = f"[red]Error:[/red] {e}"
            print(error_msg, file=sys.stderr)
            console.print(error_msg)

def _format_message_to_markdown(message: Dict[str, str]) -> str:
    """Format a message to markdown."""
    role = message["role"].capitalize()
    content = message["content"]
    return f"**{role}**: {content}\n\n"


def _write_to_markdown_file(markdown_file: str, new_messages: List[Dict[str, str]]) -> None:
    """Write the conversation to a markdown file."""
    try:
        with open(markdown_file, "a", encoding="utf-8") as f:
            for message in new_messages:
                f.write(_format_message_to_markdown(message))
    except Exception as e:
        console.print(f"[red]Error writing to markdown file: {e}[/red]")

def setup_signal_handler():
    """Set up interrupt signal handler."""
    def handle_interrupt(signum, frame):
        console.print("\n[yellow]Search interrupted by user[/yellow]")
    signal.signal(signal.SIGINT, handle_interrupt)

 
def perform_search(query: str, api_key: Optional[str] = None,
                  model: str = "llama-3.1-sonar-large-128k-online",
                  stream: Optional[bool] = None,
                  show_citations: bool = False,
                  context: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Perform a search using the Perplexity API.
    
    Args:
        query: The search query string
        api_key: Optional API key (will use env var if not provided)
        model: Model to use for search
        stream: Whether to stream the response
        show_citations: Whether to show citations
        context: Optional conversation context
        
    Returns: The response content
    """
    api = PerplexityAPI(api_key)
    response = api.perform_search(
        query=query,        
        model=model,        
        stream=stream if stream is not None else True,
        show_citations=show_citations,        
        context=context
    )
    content = "".join(response)
    return content

def check_for_updates(checker: UpdateChecker) -> None:
    """Check for package updates and handle user interaction."""
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

def main():
    """CLI entry point"""
    try:
        config = Config()
        setup_signal_handler()
    
        # Check for updates
        checker = UpdateChecker("plexsearch", __version__)
        query = config.query
        
        check_for_updates(checker)
        
        if query is not None:
            clear_new_area()
            content = handle_search(query, config.args)
            
            if config.log_file:
                new_messages = [{"role": "user", "content": query}, {"role": "assistant", "content": content}]
                log_conversation(config.log_file, new_messages)
            
            if config.args.markdown_file:
                _write_to_markdown_file(config.args.markdown_file, [{"role": "user", "content": query}, {"role": "assistant", "content": content}])
        else:
            handle_interactive_mode(config.args, config.log_file)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        print(f"[red]Error:[/red] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
