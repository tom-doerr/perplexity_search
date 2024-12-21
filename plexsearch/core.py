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

def handle_no_stream_search(query: str, args, payload: dict) -> str:    
    """Handle non-streaming search mode."""
    console.print("[cyan]About to clear screen in no_stream mode...[/cyan]")
    clear_new_area()
    spinner_text = "Searching..."
    
    api = PerplexityAPI(args.api_key)
    with Live(Spinner("dots", text=spinner_text), refresh_per_second=10, transient=True):
        response = api.perform_search(query=query,
                                      model=args.model,
                                      stream=False,
                                      show_citations=args.citations,
                                      context=payload.get("messages"))
        content = "".join(response)
    
        console.print(f"Perplexity: {content}")
        return content

def handle_streaming_search(query: str, args, payload: dict) -> str:
    """Handle streaming search mode."""
    accumulated_text = ""
    api = PerplexityAPI(args.api_key)
    with Live("", refresh_per_second=10, transient=False) as live:
        for chunk in api.perform_search(query=query,
                                      model=args.model,
                                      stream=True,
                                      show_citations=args.citations,
                                      context=payload.get("messages")):
            accumulated_text += chunk
            live.update(f"Perplexity: {accumulated_text}")
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

def handle_search(query: str, args, context=None) -> str:
    """Handle a single search query execution."""
    no_stream = args.no_stream or os.environ.get("OR_APP_NAME") == "Aider"
    api = PerplexityAPI(args.api_key)
    
    # Build payload without assistant messages in context
    if context:
        payload = api._build_payload(query=query, model=args.model,
                                   stream=not no_stream, show_citations=args.citations)
        
        messages = []
        messages.append(payload["messages"][0])  # Add the system message
        
        for i in range(0, len(context), 2):
            messages.append(context[i])  # Add user message
            if i + 1 < len(context):
                messages.append(context[i+1])  # Add assistant message
        
        # Ensure the last message is a user message
        messages.append({"role": "user", "content": query})
        payload["messages"] = messages
        console.print(f"[blue]Payload messages in handle_search: {messages}[/blue]")
    else:
        payload = api._build_payload(query=query, model=args.model,
                                   stream=not no_stream, show_citations=args.citations)

    if no_stream:
        return handle_no_stream_search(query, args, payload)
    else:
        return handle_streaming_search(query, args, payload)

def handle_interactive_mode(args, log_file, context=None):
    """Handle interactive mode search session."""
    if context is None:
        context = []
    console.print("[green]Entering interactive mode. Type your queries below. Type 'exit' to quit.[/green]")
    console.print(f"[blue]Initial context: {context}[/blue]")
    
    while True:
        user_input = console.input("\n[cyan]> [/cyan]")
        if user_input.strip() == "":
            console.print("[yellow]Please enter a query or type 'exit' to quit.[/yellow]")
            continue
        if user_input.lower() == "exit":
            console.print("[yellow]Exiting interactive mode.[/yellow]")
            break
        console.print(f"[blue]Context before user input: {context}[/blue]")

        clear_new_area()
        new_user_message = {"role": "user", "content": user_input}
        
        try:
            console.print(f"[blue]Context before handle_search: {context}[/blue]")
            content = handle_search(user_input, args, context)
            new_assistant_message = {"role": "assistant", "content": content}
            log_conversation(log_file, [new_user_message, new_assistant_message])

            context.append(new_user_message)
            context.append(new_assistant_message)
            console.print(f"[blue]Context after handle_search: {context}[/blue]")
        except Exception as e:
            error_msg = f"[red]Error:[/red] {e}"
            print(error_msg, file=sys.stderr)
            console.print(error_msg)

def setup_signal_handler():
    """Set up interrupt signal handler."""
    def handle_interrupt(signum, frame):
        console.print("\n[yellow]Search interrupted by user[/yellow]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_interrupt)

def perform_search(query: str, api_key: Optional[str] = None,
                  model: str = "llama-3.1-sonar-large-128k-online",
                  stream: bool = True,
                  show_citations: bool = False,
                  context: Optional[List[Dict[str, str]]] = None) -> Iterator[str]:
    """
    Perform a search using the Perplexity API.
    
    Args:
        query: The search query string
        api_key: Optional API key (will use env var if not provided)
        model: Model to use for search
        stream: Whether to stream the response
        show_citations: Whether to show citations
        context: Optional conversation context
        
    Returns:
        Iterator yielding response chunks
    """
    api = PerplexityAPI(api_key)
    return api.perform_search(
        query=query,
        model=model,
        stream=stream,
        show_citations=show_citations,
        context=context
    )

def main():
    """CLI entry point"""
    try:
        config = Config()
        setup_signal_handler()
    
        # Check for updates
        checker = UpdateChecker("plexsearch", __version__)
        query = config.query
        
        # Check for updates after getting query but before processing
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

            # Continue with the search after the update
            if query is not None:
                handle_search(query, config.args)
        
        if query is None:
            handle_interactive_mode(config.args, config.log_file)
        else:
            clear_new_area()
            handle_search(query, config.args)
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        print(f"[red]Error:[/red] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
