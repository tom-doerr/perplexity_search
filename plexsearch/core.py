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
    # Print newlines to push content up
    height, _ = get_terminal_size()
    # Add additional newlines to push previous content out of view
    console.print("\n" * (height + 10))

def handle_no_stream_search(query: str, args, context: Optional[List[Dict[str, str]]] = None) -> str:    
    """Handle non-streaming search mode."""
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
        with Live("[cyan]Running search...[/cyan]", refresh_per_second=10, transient=False) as live:
            for chunk in api.perform_search(query=query,
                                          model=args.model,
                                          stream=True,
                                          show_citations=args.citations,
                                          context=context):
                accumulated_text += chunk
                # live.update(f"Perplexity: {accumulated_text}")
                live.update(f"[cyan]Perplexity:[/cyan]\n{accumulated_text}", refresh=True)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise
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

import logging

def handle_search(query: str, args, context: Optional[List[Dict[str, str]]] = None) -> str:
    """Handle a single search query execution."""
    logging.debug(f"Handling search for query: {query}")
    no_stream = args.no_stream or os.environ.get("OR_APP_NAME") == "Aider"
    if context is None:
        context = []
    
    if context is None:
        context = []
        
    if not context or context[0].get('role') != 'system':
        context.insert(0, {
            "role": "system", 
            "content": "You are a technical assistant focused on providing accurate, practical information..."
        })
    # Ensure alternating roles
    for i in range(1, len(context)):
        if i % 2 == 1 and context[i]['role'] != 'user':
            raise ValueError("After the (optional) system message(s), user and assistant roles should be alternating.")
        if i % 2 == 0 and context[i]['role'] != 'assistant':
            raise ValueError("After the (optional) system message(s), user and assistant roles should be alternating.")
    if no_stream:
        logging.debug("Using no-stream search mode.")
        return handle_no_stream_search(query, args, context)
    logging.debug("Using streaming search mode.")
    return handle_streaming_search(query, args, context)

def handle_interactive_mode(args, log_file, context: Optional[List[Dict[str, str]]] = None):
    """Handle interactive mode, with optional markdown file output."""
    logging.debug("Entering interactive mode.")
    if context is None:
        context = []
    console.print("[green]Entering interactive mode. Type 'exit' or press Ctrl-D to exit.[/green]")
    
    while True:

        try:
            user_input = console.input("\n[cyan]> [/cyan]")
            clear_new_area()
            sys.stdout.write("\033[H\033[J")

        except EOFError:
            console.print("\n[yellow]Exiting interactive mode.[/yellow]")
            logging.debug("Exiting interactive mode due to EOFError.")
            break

        if user_input.strip() == "":
            console.print("[yellow]Please enter a query or type 'exit' to quit.[/yellow]")
            continue
        if user_input.lower() == "exit":
            console.print("[yellow]Exiting interactive mode.[/yellow]")
            logging.debug("Exiting interactive mode due to user input 'exit'.")
            break

        
        try:
            content = handle_search(user_input, args, context)
            new_user_message = {"role": "user", "content": user_input}
            new_assistant_message = {"role": "assistant", "content": content}
            if log_file:
                log_conversation(log_file, [new_user_message, new_assistant_message])

            if args.markdown_file:
                _write_to_markdown_file(args.markdown_file, [new_user_message, new_assistant_message])

            context.append(new_user_message)
            context.append(new_assistant_message)
        except Exception as e:
            error_msg = f"[red]Error:[/red] {e}"
            logging.error(f"Error during interactive mode: {e}", exc_info=True)
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
        console.print("\n[yellow]Search interrupted by user. Press Ctrl-D to exit[/yellow]")
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
    logging.debug(f"Performing search with query: {query}, model: {model}, stream: {stream}, citations: {show_citations}")
    api = PerplexityAPI(api_key)
    response = api.perform_search(
        query=query,        
        model=model,        
        stream=stream if stream is not None else True,
        show_citations=show_citations,        
        context=context
    )
    content = "".join(response)
    logging.debug(f"Search completed, response content: {content}")
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
        
        if config.debug:
            os.environ["PLEXSEARCH_DEBUG"] = "1"
            
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
        logging.error(f"Unhandled exception in main: {e}", exc_info=True)
        console.print(f"[red]Error:[/red] {e}")
        print(f"[red]Error:[/red] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
