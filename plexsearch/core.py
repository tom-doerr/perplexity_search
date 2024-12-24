import os
import json
import signal
import asyncio
import requests
from typing import Optional, Dict, Any, Iterator, List, Union
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from rich.theme import Theme
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import html2text
import ollama
from .prompts import format_prompt

# Load environment variables from .env file
def load_environment():
    """Load environment variables from .env file."""
    # Try to load from current directory
    if Path('.env').exists():
        load_dotenv('.env')
    # Try to load from parent directory (in case we're in a subdirectory)
    elif Path('../.env').exists():
        load_dotenv('../.env')
    
def get_api_key(args, is_openrouter: bool = False) -> Optional[str]:
    """
    Get API key in order of priority:
    1. Command line argument
    2. .env file
    3. System environment variables
    """
    if args and args.api_key:
        return args.api_key
        
    key_name = "OPENROUTER_API_KEY" if is_openrouter else "PERPLEXITY_API_KEY"
    return os.getenv(key_name)

# Custom theme for consistent styling
CUSTOM_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "user": "bold blue",
    "assistant": "bold green",
    "system": "bold yellow",
})

console = Console(theme=CUSTOM_THEME)

def format_message(content: str, role: str = "assistant") -> Panel:
    """Format a message with a panel and appropriate styling."""
    style = Style(color="green" if role == "assistant" else "blue")
    
    if role == "user":
        prefix = "🗣️ You"
        content = Text(content, style=style)
    else:
        prefix = "🤖 Assistant"
        # Process markdown in assistant responses
        content = Markdown(content)
    
    return Panel(
        content,
        title=f"{prefix}",
        title_align="left",
        border_style=style,
        padding=(0, 1)
    )

def display_startup_message():
    """Display a welcome message when starting the tool."""
    welcome_text = (
        "🔍 [bold cyan]Perplexity Search[/]\n"
        "─────────────────────\n"
        "🤖 Powered by AI - Ask me anything!\n"
        "💡 Type 'exit' to quit"
    )
    console.print(welcome_text)
    console.print()

def _handle_stream_response(response) -> Iterator[str]:
    """Handle streaming response from Perplexity API."""
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8').removeprefix('data: '))
                if content := data.get('choices', [{}])[0].get('delta', {}).get('content'):
                    yield content
            except:
                continue

# API Constants
DEFAULT_PERPLEXITY_ENDPOINT = "https://api.perplexity.ai/chat/completions"
DEFAULT_OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

def _build_api_payload(query: str, model: str, stream: bool, result_type: str = "mixed", max_results: int = 5, **optional_params) -> Dict[str, Any]:
    """Build the API request payload.
    
    Args:
        query: The search query
        model: Model to use
        stream: Whether to stream the response
        result_type: Type of results to return ("code", "docs", or "mixed")
        max_results: Maximum number of results to return
        **optional_params: Optional parameters like language, framework, etc.
        
    Returns:
        Dict containing the API request payload
    """
    is_openrouter = model.startswith("perplexity/")
    
    # Get the formatted prompt
    system_prompt = format_prompt(query, result_type, max_results, **optional_params)
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        "stream": stream
    }
    
    if is_openrouter:
        payload.update({
            "http_referer": "https://github.com/tom-doerr/perplexity_search",
            "temperature": 0.7,
            "max_tokens": 1024
        })
    
    return payload

# Enhanced DuckDuckGo search with web content extraction
def perform_duckduckgo_search(query: str, max_results: int = 5, deep_search: bool = False) -> str:
    """
    Perform an enhanced search using DuckDuckGo.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        deep_search: Whether to fetch and parse webpage content
        
    Returns:
        str: Formatted search results
    """
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    
    formatted_results = ["### DuckDuckGo Search Results\n"]
    
    for i, result in enumerate(results, 1):
        formatted_results.append(f"{i}. **{result['title']}**")
        
        if deep_search:
            try:
                # Fetch webpage content
                response = requests.get(result['link'], timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Convert HTML to markdown
                h = html2text.HTML2Text()
                h.ignore_links = False
                content = h.handle(str(soup.find('main')) if soup.find('main') else str(soup.body))
                
                # Add summarized content
                formatted_results.append(f"   Summary: {content[:500]}...")
            except:
                formatted_results.append(f"   {result['body']}")
        else:
            formatted_results.append(f"   {result['body']}")
            
        formatted_results.append(f"   [Link]({result['link']})\n")
    
    return "\n".join(formatted_results)

async def perform_ollama_search(query: str, model: str = "mistral") -> str:
    """
    Perform search using local Ollama model.
    
    Args:
        query: Search query
        model: Ollama model name
        
    Returns:
        str: Model response
    """
    try:
        response = await ollama.chat(
            model=model,
            messages=[{
                'role': 'system',
                'content': 'You are a helpful assistant providing accurate technical information.'
            }, {
                'role': 'user',
                'content': query
            }]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error using Ollama: {str(e)}"

def perform_search(query: str, api_key: Optional[str] = None, model: str = None, stream: bool = False, args = None, 
                  result_type: str = "mixed", max_results: int = 5, **optional_params) -> Iterator[str]:
    """Perform a search using available backends."""
    if model is None:
        model = os.getenv("MODEL", "llama-3.1-sonar-large-128k-online")
    
    # Check if it's an Ollama model
    if model.startswith("ollama:"):
        ollama_model = model.split(":")[1]
        console.print(f"[dim]Using local Ollama model: {ollama_model}[/]")
        result = asyncio.run(perform_ollama_search(query, ollama_model))
        yield result
        return
    
    is_openrouter = model.startswith("perplexity/") or "/" in model
    
    # Get API key with proper priority
    if api_key is None:
        api_key = get_api_key(args, is_openrouter)
        if not api_key:
            # Fallback to DuckDuckGo if no API key
            console.print("[yellow]No API key found, falling back to DuckDuckGo search[/]")
            deep_search = optional_params.get('deep_search', False)
            results = perform_duckduckgo_search(query, max_results, deep_search)
            yield results
            return

    # Show model info
    console.print(f"[dim]Using {model}[/]")
    
    api_endpoint = os.getenv("API_ENDPOINT")
    if not api_endpoint:
        api_endpoint = DEFAULT_OPENROUTER_ENDPOINT if is_openrouter else DEFAULT_PERPLEXITY_ENDPOINT

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    if is_openrouter:
        headers.update({
            "HTTP-Referer": "https://github.com/tom-doerr/perplexity_search",
            "X-Title": "Perplexity Search CLI"
        })
    
    try:
        payload = _build_api_payload(
            query=query, 
            model=model, 
            stream=stream,
            result_type=result_type,
            max_results=max_results,
            **optional_params
        )
        
        response = requests.post(
            api_endpoint,
            headers=headers,
            json=payload,
            stream=stream,
            timeout=30  # Add timeout
        )
        
        if response.status_code != 200:
            error_msg = f"API request failed with status code {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f": {error_details.get('error', {}).get('message', '')}"
            except:
                pass
            console.print(f"[yellow]API Error: {error_msg}, falling back to DuckDuckGo search[/]")
            deep_search = optional_params.get('deep_search', False)
            results = perform_duckduckgo_search(query, max_results, deep_search)
            yield results
            return

        if stream:
            yield from _handle_stream_response(response)
        else:
            yield response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            
    except Exception as e:
        console.print(f"[yellow]Error: {str(e)}, falling back to DuckDuckGo search[/]")
        deep_search = optional_params.get('deep_search', False)
        results = perform_duckduckgo_search(query, max_results, deep_search)
        yield results

def process_query(query: str, args, optional_params: dict = None):
    """Process a single query and display results."""
    try:
        # Print user query
        console.print(format_message(query, role="user"))
        
        accumulated_text = ""
        if args.no_stream:
            # Non-streaming mode
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                progress.add_task(description="[dim]Thinking...[/]", total=None)
                response = list(perform_search(
                    query, 
                    api_key=None, 
                    model=args.model, 
                    stream=False, 
                    args=args,
                    result_type=args.result_type,
                    max_results=args.max_results,
                    **(optional_params or {})
                ))
                accumulated_text = response[0] if response else ""
                
                # Try to parse as JSON
                try:
                    response_json = json.loads(accumulated_text)
                    # Format the response nicely
                    formatted_response = json.dumps(response_json, indent=2)
                    console.print(format_message(formatted_response))
                except json.JSONDecodeError:
                    # If not JSON, display as is
                    console.print(format_message(accumulated_text))
        else:
            # Streaming mode
            with Live(format_message(""), console=console, refresh_per_second=10) as live:
                for chunk in perform_search(
                    query, 
                    api_key=None, 
                    model=args.model, 
                    stream=True, 
                    args=args,
                    result_type=args.result_type,
                    max_results=args.max_results,
                    **(optional_params or {})
                ):
                    accumulated_text += chunk
                    # Try to parse as JSON if complete
                    try:
                        response_json = json.loads(accumulated_text)
                        formatted_response = json.dumps(response_json, indent=2)
                        live.update(format_message(formatted_response))
                    except json.JSONDecodeError:
                        live.update(format_message(accumulated_text))
        
        # Add a newline after response for better readability
        console.print()
            
    except KeyboardInterrupt:
        console.print("\n[yellow]✋ Search interrupted[/]")
        return
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/]")
        return

def main():
    """CLI entry point"""
    # Load environment variables first
    load_environment()
    
    import argparse
    import sys
    
    from plexsearch import __version__
    
    # Display welcome message
    display_startup_message()
    
    parser = argparse.ArgumentParser(description="Perform searches using multiple AI and search backends")
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument("query", nargs="*", help="The search query")
    parser.add_argument("--api-key", help="API key for Perplexity or OpenRouter")
    parser.add_argument("--model", help="Model to use (including Ollama models with 'ollama:' prefix)")
    parser.add_argument("--no-stream", action="store_true", help="Disable streaming output")
    
    # Add new parameters
    parser.add_argument("--result-type", choices=["code", "docs", "mixed"], 
                       default="mixed", help="Type of results to return")
    parser.add_argument("--max-results", type=int, default=5,
                       help="Maximum number of results to return")
    parser.add_argument("--language", help="Programming language to filter results")
    parser.add_argument("--framework", help="Framework to focus results on")
    parser.add_argument("--date-range", help="Date range for results (e.g., '2023-2024')")
    parser.add_argument("--format", help="Output format")
    parser.add_argument("--deep-search", action="store_true",
                       help="Enable deep search for DuckDuckGo (fetches webpage content)")
    
    args = parser.parse_args()
    
    # Collect optional parameters
    optional_params = {}
    if args.language:
        optional_params['language'] = args.language
    if args.framework:
        optional_params['framework'] = args.framework
    if args.date_range:
        optional_params['date_range'] = args.date_range
    if args.format:
        optional_params['format'] = args.format
    if args.deep_search:
        optional_params['deep_search'] = True
    
    # If no query provided, enter interactive mode
    if not args.query:
        while True:
            try:
                query = Prompt.ask("\n[bold blue]Ask[/]")
                if query.lower() in ('exit', 'quit'):
                    console.print("[dim]👋 Goodbye![/]")
                    break
                process_query(query, args, optional_params)
            except (KeyboardInterrupt, EOFError):
                console.print("\n[dim]👋 Goodbye![/]")
                break
    else:
        query = " ".join(args.query)
        process_query(query, args, optional_params)

if __name__ == "__main__":
    main()
