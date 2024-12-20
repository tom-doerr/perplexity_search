"""Configuration management module."""
import argparse
from typing import Optional, List
from plexsearch import __version__

class Config:
    """Handle application configuration."""
    
    DEFAULT_MODEL = "llama-3.1-sonar-large-128k-online"
    DEFAULT_LOG_FILE = "plexsearch_log.json"
    
    def __init__(self):
        self.args = self._parse_arguments()
    
    @property
    def is_interactive(self) -> bool:
        return not self.query
    
    @property
    def query(self) -> Optional[str]:
        return " ".join(self.args.query) if self.args.query else None
    
    @property
    def api_key(self) -> Optional[str]:
        return self.args.api_key
    
    @property
    def model(self) -> str:
        return self.args.model
    
    @property
    def no_stream(self) -> bool:
        return self.args.no_stream
    
    @property
    def show_citations(self) -> bool:
        return self.args.citations
    
    @property
    def log_file(self) -> Optional[str]:
        if self.args.log_file is None:
            return None
        return self.args.log_file if self.args.log_file else Config.DEFAULT_LOG_FILE
    
    @staticmethod
    def _parse_arguments() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Perform searches using Perplexity API")
        parser.add_argument('--version', action='version',
                           version=f'%(prog)s {__version__}')
        parser.add_argument("query", nargs="*", help="The search query")
        parser.add_argument("--api-key", help="Perplexity API key")
        parser.add_argument("--model",
                           default=Config.DEFAULT_MODEL,
                           help="Model to use for search")
        parser.add_argument("--no-stream", action="store_true",
                           help="Disable streaming output")
        parser.add_argument("-c", "--citations", action="store_true",
                           help="Show numbered citations")
        parser.add_argument("--log-file",
                            nargs='?',
                            help="Path to log file")
        return parser.parse_args()
