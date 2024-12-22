"""Module for checking and handling package updates."""
import os
import json
import time
from packaging import version
import warnings
from typing import Optional, Dict, Any
import subprocess

try:
    import feedparser
    HAVE_FEEDPARSER = True
except ImportError:
    HAVE_FEEDPARSER = False
    warnings.warn("feedparser not installed. Version checking disabled. Install with 'pip install feedparser'")


def _parse_version_from_title(title: str) -> str:
    """Helper function to parse version from feed title."""
    if ": " in title:
        return title.split(": ")[1]
    elif " " in title:
        return title.split(" ")[1]
    return title

def get_latest_version(package_name: str) -> str:
    """Get the latest version of a package from PyPI."""
    if not HAVE_FEEDPARSER:
        return "0.0.0"
    
    try:
        rss_url = f"https://pypi.org/rss/project/{package_name}/releases.xml"
        feed = feedparser.parse(rss_url)
        if not feed.entries:
            return "0.0.0"
        title = feed.entries[0].title
        return _parse_version_from_title(title)
    except feedparser.FeedParserError:
        return "0.0.0"
    except Exception as e:
        print(f"Error fetching latest version: {e}")
        return "0.0.0"

def check_for_update(current_version: str, latest_version: str) -> bool:
    """Compare versions to check if an update is available."""
    try:
        return version.parse(latest_version) > version.parse(current_version)
    except version.InvalidVersion:
        return False

class UpdateChecker:
    """Handles checking for package updates."""
    
    def __init__(self, package_name: str, current_version: str):
        """Initialize the update checker."""
        self.package_name = package_name
        self.current_version = current_version
        self.state_dir = os.path.expanduser("~/.config/plexsearch")
        self.state_file = os.path.join(self.state_dir, "update_state.json")
        
    def load_state(self) -> Dict[str, float]:
        """Load the saved state from file."""
        if not os.path.exists(self.state_file):
            if not os.path.exists(self.state_dir):
                os.makedirs(self.state_dir)
            return {"last_check": 0, "last_reminder": 0}
        
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"last_check": 0, "last_reminder": 0}
            
    def save_state(self, state: Dict[str, float]) -> None:
        """Save the state to file."""
        with open(self.state_file, 'w') as f:
            json.dump(state, f)
            
    def check_and_notify(self, interval_hours: int = 24) -> Optional[str]:
        """Check for updates and notify if available."""
        state = self.load_state()
        current_time = time.time()
        
        if current_time - state["last_check"] < interval_hours * 3600:
            return None
        # Ensure the interval condition is met
        if current_time - state["last_reminder"] < interval_hours * 3600:
            return None
            
        state["last_check"] = current_time
        latest_version = get_latest_version(self.package_name)
        
        if check_for_update(self.current_version, latest_version):
            if current_time - state["last_reminder"] < interval_hours * 3600:
                return None
                
            state["last_reminder"] = current_time
            self.save_state(state)
            return latest_version
            
        self.save_state(state)
        return None
        
    def update_package(self) -> bool:
        """Update the package using pip."""
        try:
            from rich.progress import Progress
            with Progress() as progress:
                task = progress.add_task("[cyan]Updating package...", total=100)
                process = subprocess.run(
                    ["pip", "install", "--upgrade", "--no-cache-dir", self.package_name],
                    check=False,
                    capture_output=True,
                    text=True
                )
                progress.update(task, completed=100)
                
                if process.returncode == 0 and "Successfully installed" in process.stdout:
                    return True
                
                output = process.stdout + process.stderr
                print(f"Update failed with output: {output}")
                return False
        except FileNotFoundError:
            print("Error: pip command not found. Ensure pip is installed and in your system's PATH.")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during update: {e}")
            return False
