"""Text formatting utilities."""
from typing import List
from rich.markdown import Markdown

def format_markdown(content: str) -> str:
    """Format markdown content with enhanced styling."""
    lines = content.split("\n")
    formatted_lines: List[str] = []
    
    for line in lines:
        # Bold headings with indentation and decorative elements
        if line.startswith("## "):
            formatted_lines.append("\n[bold cyan]┌──────────────────────┐[/bold cyan]")
            formatted_lines.append("**## " + line[3:] + "**")
            formatted_lines.append("[bold cyan]└──────────────────────┘[/bold cyan]")
        elif line.startswith("### "):
            formatted_lines.append("\n   [cyan]▶[/cyan] **### " + line[4:] + "**")
        # Add bullet points with colored indentation
        elif line.startswith("- "):
            formatted_lines.append("   [cyan]•[/cyan] " + line[2:])
        # Highlight key terms with different style
        elif "`" in line:
            formatted_lines.append(line.replace("`", "[bold magenta]").replace("`", "[/bold magenta]"))
        # Add decorative separator for main sections
        elif line.startswith("# "):
            formatted_lines.append("\n[bold cyan]════════════════════════════════[/bold cyan]")
            formatted_lines.append("**# " + line[2:] + "**")
            formatted_lines.append("[bold cyan]════════════════════════════════[/bold cyan]\n")
        else:
            formatted_lines.append(line)
    
    return "\n".join(formatted_lines)
