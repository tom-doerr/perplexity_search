"""Configuration management module."""
import argparse
from typing import Optional, List
from plexsearch import __version__

class Config:
    """Handle application configuration."""
    LLAMA_MODELS = {
        "small": "llama-3.1-sonar-small-128k-online",
        "large": "llama-3.1-sonar-large-128k-online",
        "huge": "llama-3.1-sonar-huge-128k-online"
    }
    
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
    
    @property
    def model(self) -> str:
        if self.args.small:
            return self.LLAMA_MODELS["small"]
        if self.args.huge:
            return self.LLAMA_MODELS["huge"]
        
        return self.LLAMA_MODELS["large"]
    
    @staticmethod
    def _parse_arguments() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Perform searches using Perplexity API")
        parser.add_argument('--version', action='version',
                           version=f'%(prog)s {__version__}')
        parser.add_argument("query", nargs="*", help="The search query")
        parser.add_argument("--api-key", help="Perplexity API key")
        parser.add_argument("--small", action="store_true",
                           help="Use the small model")
        parser.add_argument("--large", action="store_true",
                           help="Use the large model")
        parser.add_argument("--huge", action="store_true", help="Use the huge model")
        parser.add_argument("--no-stream", action="store_true",
                           help="Disable streaming output")
        parser.add_argument("-c", "--citations", action="store_true",
                           help="Show numbered citations")
        parser.add_argument("--log-file", nargs='?', help="Path to log file")
        return parser.parse_args()
